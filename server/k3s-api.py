#!/usr/bin/env python3
"""K3s cluster API server for big-screen dashboard."""
import json
import subprocess
import threading
import time
import re
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

KUBECONFIG = "/home/a/.kube/config"
CACHE_TTL = 5
HISTORY_SIZE = 60
PORT = 8099

_cache = {
    "nodes_raw": None,
    "nodes_ts": 0,
    "top_nodes": None,
    "top_nodes_ts": 0,
    "pods_count": None,
    "pods_count_ts": 0,
}
_history = []
_lock = threading.RLock()


def run_kubectl(args):
    """Run kubectl command and return parsed JSON or raw output."""
    cmd = ["k3s", "kubectl"] + args
    env = {"KUBECONFIG": KUBECONFIG, "PATH": "/usr/local/bin:/usr/bin:/bin"}
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, env=env)
        if result.returncode != 0:
            print(f"[kubectl error] {' '.join(cmd)}: {result.stderr.strip()}")
            return None
        return result.stdout.strip()
    except Exception as e:
        print(f"[kubectl exception] {' '.join(cmd)}: {e}")
        return None


def get_nodes_json():
    now = time.time()
    with _lock:
        cached_raw = _cache["nodes_raw"]
        cached_ts = _cache["nodes_ts"]
    if cached_raw and (now - cached_ts) < CACHE_TTL:
        return json.loads(cached_raw)

    raw = run_kubectl(["get", "nodes", "-o", "json"])
    if raw:
        with _lock:
            _cache["nodes_raw"] = raw
            _cache["nodes_ts"] = now
    return json.loads(raw) if raw else None


def get_top_nodes():
    now = time.time()
    with _lock:
        cached_top = _cache["top_nodes"]
        cached_ts = _cache["top_nodes_ts"]
    if cached_top and (now - cached_ts) < CACHE_TTL:
        return cached_top

    top = parse_top_nodes(run_kubectl(["top", "nodes", "--no-headers"]))
    with _lock:
        _cache["top_nodes"] = top
        _cache["top_nodes_ts"] = now
    return top


def get_running_pod_count():
    now = time.time()
    with _lock:
        cached_count = _cache["pods_count"]
        cached_ts = _cache["pods_count_ts"]
    if cached_count is not None and (now - cached_ts) < CACHE_TTL:
        return cached_count

    raw = run_kubectl([
        "get",
        "pods",
        "--all-namespaces",
        "--field-selector=status.phase!=Succeeded,status.phase!=Failed",
        "--no-headers",
    ])
    count = len([line for line in raw.splitlines() if line.strip()]) if raw else 0
    with _lock:
        _cache["pods_count"] = count
        _cache["pods_count_ts"] = now
    return count


def parse_top_nodes(raw):
    """Parse 'kubectl top nodes --no-headers' output.
    Format: NAME  CPU(cores)  CPU%  MEMORY(bytes)  MEMORY%
    """
    result = {}
    if not raw:
        return result
    for line in raw.strip().split("\n"):
        parts = line.split()
        if len(parts) >= 5:
            name = parts[0]
            cpu_cores = parts[1]  # e.g. "895m"
            cpu_pct = parts[2]    # e.g. "22%"
            mem_bytes = parts[3]  # e.g. "1313Mi"
            mem_pct = parts[4]    # e.g. "37%"
            result[name] = {
                "cpuCores": cpu_cores,
                "cpuPct": cpu_pct,
                "memory": mem_bytes,
                "memoryPct": mem_pct,
            }
    return result


def parse_cpu_to_millicores(cpu_str):
    if cpu_str.endswith("m"):
        return int(cpu_str[:-1])
    if cpu_str.endswith("n"):
        return int(cpu_str[:-1]) // 1000000
    try:
        return int(float(cpu_str) * 1000)
    except ValueError:
        return 0


def parse_memory_to_mib(mem_str):
    mem_str = mem_str.upper()
    if "KI" in mem_str:
        return int(mem_str.replace("KI", "")) // 1024
    if "MI" in mem_str:
        return int(mem_str.replace("MI", ""))
    if "GI" in mem_str:
        return int(float(mem_str.replace("GI", "")) * 1024)
    if "TI" in mem_str:
        return int(float(mem_str.replace("TI", "")) * 1024 * 1024)
    try:
        return int(mem_str) // (1024 * 1024)
    except ValueError:
        return 0


def parse_resource_str(resource_str):
    """Parse k8s resource string like '7726868Ki' to numeric value in base units."""
    s = resource_str.upper()
    if "KI" in s:
        return int(s.replace("KI", "")) * 1024
    if "MI" in s:
        return int(s.replace("MI", "")) * 1024 * 1024
    if "GI" in s:
        return int(float(s.replace("GI", "")) * 1024 * 1024 * 1024)
    try:
        return int(s)
    except ValueError:
        return 0


def collect_history():
    """Collect current cluster metrics and append to history."""
    nodes = get_nodes_json()
    top = get_top_nodes()
    if not nodes or not top:
        return

    total_cpu_cap = 0
    total_mem_cap = 0
    total_cpu_used = 0
    total_mem_used = 0
    ready_count = 0

    for item in nodes.get("items", []):
        name = item["metadata"]["name"]
        caps = item["status"]["capacity"]
        total_cpu_cap += int(caps.get("cpu", "0"))
        total_mem_cap += parse_resource_str(caps.get("memory", "0Ki"))
        for cond in item["status"].get("conditions", []):
            if cond["type"] == "Ready" and cond["status"] == "True":
                ready_count += 1
        if name in top:
            total_cpu_used += parse_cpu_to_millicores(top[name]["cpuCores"])
            total_mem_used += parse_memory_to_mib(top[name]["memory"]) * 1024 * 1024

    cpu_usage = round(total_cpu_used / (total_cpu_cap * 1000) * 100, 1) if total_cpu_cap > 0 else 0
    mem_usage = round(total_mem_used / total_mem_cap * 100, 1) if total_mem_cap > 0 else 0

    entry = {
        "timestamp": int(time.time() * 1000),
        "cpuUsage": cpu_usage,
        "memoryUsage": mem_usage,
        "storageUsage": 10,  # TODO: get actual storage usage from PVC
    }
    with _lock:
        _history.append(entry)
        if len(_history) > HISTORY_SIZE:
            _history.pop(0)


def get_node_count():
    nodes = get_nodes_json()
    if not nodes:
        return 0
    return len(nodes.get("items", []))


def get_pod_count():
    return get_running_pod_count()


class APIHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, msg, code=500):
        self._send_json({"ret": 0, "msg": msg}, code)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        try:
            # /api/k8s/getClusterResource/<clusterName>
            if path.startswith("/api/k8s/getClusterResource/"):
                cluster_name = path.split("/api/k8s/getClusterResource/")[-1]
                self._handle_cluster_resource(cluster_name)

            # /api/k8s/getNodeResource?clusterName=xxx
            elif path == "/api/k8s/getNodeResource":
                cluster_name = params.get("clusterName", ["default"])[0]
                self._handle_node_resource(cluster_name)

            # /api/k8s/getData?clusterName=xxx
            elif path == "/api/k8s/getData":
                cluster_name = params.get("clusterName", ["default"])[0]
                self._handle_get_data(cluster_name)

            # /api/k8s/getClusterInfo/<clusterName>
            elif path.startswith("/api/k8s/getClusterInfo/"):
                cluster_name = path.split("/api/k8s/getClusterInfo/")[-1]
                self._handle_cluster_info(cluster_name)

            # /api/k8s/getPredictClusterInfo/<clusterName>
            elif path.startswith("/api/k8s/getPredictClusterInfo/"):
                cluster_name = path.split("/api/k8s/getPredictClusterInfo/")[-1]
                self._handle_predict_cluster_info(cluster_name)

            # /api/cluster/getClusterBaseInfo/<clusterName>
            elif path.startswith("/api/cluster/getClusterBaseInfo/"):
                cluster_name = path.split("/api/cluster/getClusterBaseInfo/")[-1]
                self._handle_cluster_base_info(cluster_name)

            # /api/cluster/getAllClusterInfo/<cityId>
            elif path.startswith("/api/cluster/getAllClusterInfo/"):
                city_id = path.split("/api/cluster/getAllClusterInfo/")[-1]
                self._handle_all_cluster_info(city_id)

            # /api/dataCenters/getDataCenters
            elif path == "/api/dataCenters/getDataCenters":
                self._handle_data_centers()

            # health check
            elif path == "/api/health":
                self._send_json({"ret": 1, "data": "ok"})

            else:
                self._send_error("Not found", 404)

        except Exception as e:
            print(f"[handler error] {path}: {e}")
            self._send_error(str(e))

    def _handle_cluster_resource(self, cluster_name):
        nodes = get_nodes_json()
        top = get_top_nodes()
        if not nodes:
            return self._send_error("Failed to get nodes")

        total_cpu_cap = 0
        total_mem_cap = 0
        total_cpu_used = 0
        total_mem_used = 0
        node_count = 0

        for item in nodes.get("items", []):
            caps = item["status"]["capacity"]
            node_count += 1
            total_cpu_cap += int(caps.get("cpu", "0"))
            total_mem_cap += parse_resource_str(caps.get("memory", "0Ki"))
            name = item["metadata"]["name"]
            if name in top:
                total_cpu_used += parse_cpu_to_millicores(top[name]["cpuCores"])
                total_mem_used += parse_memory_to_mib(top[name]["memory"]) * 1024 * 1024

        cpu_usage = round(total_cpu_used / (total_cpu_cap * 1000) * 100, 1) if total_cpu_cap > 0 else 0
        mem_usage = round(total_mem_used / total_mem_cap * 100, 1) if total_mem_cap > 0 else 0

        self._send_json({"ret": 1, "data": {
            "cpuUsage": cpu_usage,
            "storageUsage": 10,
            "memoryUsage": mem_usage,
            "nodeCount": node_count,
        }})

    def _handle_node_resource(self, cluster_name):
        nodes = get_nodes_json()
        top = get_top_nodes()
        if not nodes:
            return self._send_error("Failed to get nodes")

        pod_per_node = {}

        raw = run_kubectl([
            "get",
            "pods",
            "--all-namespaces",
            "-o",
            "custom-columns=NODE:.spec.nodeName",
            "--no-headers",
        ])
        if raw:
            for line in raw.splitlines():
                node_name = line.strip()
                if node_name:
                    pod_per_node[node_name] = pod_per_node.get(node_name, 0) + 1

        result = []
        for item in nodes.get("items", []):
            name = item["metadata"]["name"]
            caps = item["status"]["capacity"]
            cpu_cap = caps.get("cpu", "?")
            mem_cap = caps.get("memory", "?")
            t = top.get(name, {})
            cpu_cores = t.get("cpuCores", "0m")
            cpu_pct = t.get("cpuPct", "0%")
            mem_val = t.get("memory", "0Mi")
            mem_pct = t.get("memoryPct", "0%")
            pod_count = pod_per_node.get(name, 0)
            is_ready = "正常"
            for cond in item["status"].get("conditions", []):
                if cond["type"] == "Ready" and cond["status"] != "True":
                    is_ready = "异常"

            result.append({
                "nodeName": name,
                "podCount": pod_count,
                "cpu": f"{cpu_cores} ({cpu_pct}) / {cpu_cap} cores",
                "memory": f"{mem_val} ({mem_pct}) / {mem_cap}",
                "storage": "N/A",
                "nodeStatus": is_ready,
            })

        self._send_json({"ret": 1, "data": result})

    def _handle_get_data(self, cluster_name):
        start = time.time()
        node_count = get_node_count()
        pod_count = get_pod_count()
        elapsed = round((time.time() - start) * 1000)

        self._send_json({"ret": 1, "data": {
            "responseTimeMs": elapsed,
            "podCount": pod_count,
            "nodeCount": node_count,
        }})

    def _handle_cluster_info(self, cluster_name):
        with _lock:
            data = list(_history)
        self._send_json({"ret": 1, "data": data})

    def _handle_predict_cluster_info(self, cluster_name):
        with _lock:
            data = list(_history)
        self._send_json({"ret": 1, "data": data})

    def _handle_cluster_base_info(self, cluster_name):
        self._send_json({"ret": 1, "data": {
            "type": "K3s",
            "ip": "192.168.31.36",
            "port": "6443",
            "createTime": "2025-03-25",
        }})

    def _handle_all_cluster_info(self, city_id):
        self._send_json({"ret": 1, "data": [
            {"name": "k3s-cluster"},
        ]})

    def _handle_data_centers(self):
        self._send_json({"ret": 1, "data": []})

    def do_POST(self):
        self._send_error("Not implemented", 405)

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {self.client_address} {format % args}")


def history_collector():
    while True:
        try:
            collect_history()
        except Exception as e:
            print(f"[collector error] {e}")
        time.sleep(5)


def main():
    print(f"[k3s-api] Starting on port {PORT}...")
    print(f"[k3s-api] KUBECONFIG={KUBECONFIG}")

    t = threading.Thread(target=history_collector, daemon=True)
    t.start()

    server = ThreadingHTTPServer(("0.0.0.0", PORT), APIHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
