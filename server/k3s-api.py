#!/usr/bin/env python3
"""K3s cluster API server for big-screen dashboard."""
import json
import subprocess
import threading
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

KUBECONFIG = "/home/a/.kube/config"
CACHE_TTL = 8
NODE_RESOURCE_TTL = 10
K3S_API_SERVER = "https://127.0.0.1:6443"
HISTORY_SIZE = 60
PORT = 8099

_cache = {
    "nodes_raw": None,
    "nodes_ts": 0,
    "top_nodes": None,
    "top_nodes_ts": 0,
    "pods_count": None,
    "pods_count_ts": 0,
    "pod_per_node": None,
    "pod_per_node_ts": 0,
    "node_resource": None,
    "node_resource_ts": 0,
    "node_fs_stats": None,
    "node_fs_stats_ts": 0,
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


def format_bytes_short(num_bytes):
    """Format byte count to human-readable string."""
    if num_bytes <= 0:
        return "0"
    units = ["B", "Ki", "Mi", "Gi", "Ti"]
    value = float(num_bytes)
    unit_idx = 0
    while value >= 1024 and unit_idx < len(units) - 1:
        value /= 1024
        unit_idx += 1
    if unit_idx == 0:
        return f"{int(value)}{units[unit_idx]}"
    return f"{value:.2f}{units[unit_idx]}"


def format_cpu_short(millicores, cores_total):
    """Format CPU used/total for display."""
    if millicores >= 1000:
        used = f"{millicores / 1000:.2f}"
    else:
        used = f"{millicores}m"
    return f"{used} / {cores_total} 核"


def fetch_node_fs_stats(node_name):
    """Read node root filesystem used/available from kubelet stats summary."""
    raw = run_kubectl(["get", "--raw", f"/api/v1/nodes/{node_name}/proxy/stats/summary"])
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    fs = data.get("node", {}).get("fs") or {}
    used = int(fs.get("usedBytes") or 0)
    available = int(fs.get("availableBytes") or 0)
    capacity = int(fs.get("capacityBytes") or 0)
    if used == 0 and available == 0 and capacity == 0:
        return None
    return {"used": used, "available": available, "capacity": capacity}


def refresh_node_fs_stats(node_names):
    """Fetch filesystem stats for all nodes (kubelet summary API)."""
    stats = {}
    if not node_names:
        with _lock:
            _cache["node_fs_stats"] = stats
            _cache["node_fs_stats_ts"] = time.time()
        return stats

    workers = min(8, len(node_names))

    def _fetch_one(name):
        return name, fetch_node_fs_stats(name)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_fetch_one, name) for name in node_names]
        for fut in as_completed(futures):
            name, item = fut.result()
            if item:
                stats[name] = item
    with _lock:
        _cache["node_fs_stats"] = stats
        _cache["node_fs_stats_ts"] = time.time()
    return stats


def get_node_fs_stats_map(node_names):
    """Return cached per-node fs stats, refreshing when stale."""
    now = time.time()
    with _lock:
        cached = _cache["node_fs_stats"]
        cached_ts = _cache["node_fs_stats_ts"]
    if cached is not None and (now - cached_ts) < NODE_RESOURCE_TTL:
        return cached
    return refresh_node_fs_stats(node_names)


def aggregate_cluster_resources(nodes, top, fs_stats):
    """Cluster totals = sum of per-node used / sum of per-node capacity (CPU, mem, disk)."""
    total_cpu_cap = 0
    total_mem_cap = 0
    total_cpu_used = 0
    total_mem_used = 0
    total_storage_used = 0
    total_storage_capacity = 0
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
        fs = (fs_stats or {}).get(name) or {}
        used = int(fs.get("used") or 0)
        available = int(fs.get("available") or 0)
        capacity = int(fs.get("capacity") or 0) or (used + available)
        total_storage_used += used
        total_storage_capacity += capacity

    storage_total_bytes = total_storage_capacity
    cpu_usage = round(total_cpu_used / (total_cpu_cap * 1000) * 100, 1) if total_cpu_cap > 0 else 0
    mem_usage = round(total_mem_used / total_mem_cap * 100, 1) if total_mem_cap > 0 else 0
    storage_usage = (
        round(total_storage_used / storage_total_bytes * 100, 1)
        if storage_total_bytes > 0
        else 0
    )

    return {
        "node_count": node_count,
        "cpu_usage": cpu_usage,
        "mem_usage": mem_usage,
        "storage_usage": storage_usage,
        "cpu_used": format_cpu_short(total_cpu_used, total_cpu_cap),
        "cpu_total": f"{total_cpu_cap} 核",
        "memory_used": format_bytes_short(total_mem_used),
        "memory_total": format_bytes_short(total_mem_cap),
        "storage_used": format_bytes_short(total_storage_used),
        "storage_total": format_bytes_short(total_storage_capacity),
    }


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

    node_names = [item["metadata"]["name"] for item in nodes.get("items", [])]
    fs_stats = get_node_fs_stats_map(node_names)
    stats = aggregate_cluster_resources(nodes, top, fs_stats)

    entry = {
        "timestamp": int(time.time() * 1000),
        "cpuUsage": stats["cpu_usage"],
        "memoryUsage": stats["mem_usage"],
        "storageUsage": stats["storage_usage"],
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


def refresh_pod_per_node():
    """Background-thread-safe: recompute pod count per node."""
    raw = run_kubectl([
        "get", "pods", "--all-namespaces",
        "--field-selector=status.phase!=Succeeded,status.phase!=Failed",
        "-o", "custom-columns=NODE:.spec.nodeName",
        "--no-headers",
    ])
    mapping = {}
    if raw:
        for line in raw.splitlines():
            node_name = line.strip()
            if node_name:
                mapping[node_name] = mapping.get(node_name, 0) + 1
    with _lock:
        _cache["pod_per_node"] = mapping
        _cache["pod_per_node_ts"] = time.time()


def refresh_nodes():
    raw = run_kubectl(["get", "nodes", "-o", "json"])
    if raw:
        with _lock:
            _cache["nodes_raw"] = raw
            _cache["nodes_ts"] = time.time()


def refresh_top_nodes():
    top = parse_top_nodes(run_kubectl(["top", "nodes", "--no-headers"]))
    with _lock:
        _cache["top_nodes"] = top
        _cache["top_nodes_ts"] = time.time()


def get_pod_per_node():
    """Return last-known pod-per-node mapping refreshed by collector."""
    with _lock:
        return dict(_cache["pod_per_node"]) if _cache["pod_per_node"] is not None else {}


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

        node_names = [item["metadata"]["name"] for item in nodes.get("items", [])]
        fs_stats = get_node_fs_stats_map(node_names)
        stats = aggregate_cluster_resources(nodes, top, fs_stats)

        self._send_json({"ret": 1, "data": {
            "cpuUsage": stats["cpu_usage"],
            "storageUsage": stats["storage_usage"],
            "memoryUsage": stats["mem_usage"],
            "nodeCount": stats["node_count"],
            "cpuUsed": stats["cpu_used"],
            "cpuTotal": stats["cpu_total"],
            "memoryUsed": stats["memory_used"],
            "memoryTotal": stats["memory_total"],
            "storageUsed": stats["storage_used"],
            "storageTotal": stats["storage_total"],
            "ts": int(time.time()),
        }})

    def _handle_node_resource(self, cluster_name):
        nodes = get_nodes_json()
        top = get_top_nodes()
        if not nodes:
            return self._send_error("Failed to get nodes")

        pod_per_node = get_pod_per_node()
        node_names = [item["metadata"]["name"] for item in nodes.get("items", [])]
        fs_stats = get_node_fs_stats_map(node_names)

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

            fs = fs_stats.get(name) or {}
            storage_used_bytes = int(fs.get("used") or 0)
            storage_available_bytes = int(fs.get("available") or 0)
            if storage_used_bytes > 0 or storage_available_bytes > 0:
                storage_total_bytes = storage_used_bytes + storage_available_bytes
                storage_pct = (
                    round(storage_used_bytes / storage_total_bytes * 100, 1)
                    if storage_total_bytes > 0
                    else 0
                )
                storage_display = (
                    f"{format_bytes_short(storage_used_bytes)} ({storage_pct}%) "
                    f"/ {format_bytes_short(storage_available_bytes)}"
                )
            else:
                storage_display = "获取失败"

            result.append({
                "nodeName": name,
                "podCount": pod_count,
                "cpu": f"{cpu_cores} ({cpu_pct}) / {cpu_cap} 核",
                "memory": f"{mem_val} ({mem_pct}) / {mem_cap}",
                "storage": storage_display,
                "nodeStatus": is_ready,
            })

        self._send_json({"ret": 1, "data": result, "ts": int(time.time())})

    def _handle_get_data(self, cluster_name):
        self._send_json({"ret": 1, "data": {
            "podCount": get_pod_count(),
            "nodeCount": get_node_count(),
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
    """Periodically refresh caches so API handlers always read from memory."""
    while True:
        try:
            nodes = get_nodes_json()
            if nodes:
                node_names = [
                    item["metadata"]["name"] for item in nodes.get("items", [])
                ]
                refresh_node_fs_stats(node_names)
            collect_history()
            refresh_nodes()
            refresh_top_nodes()
        except Exception as e:
            print(f"[collector error] {e}")
        time.sleep(5)


def pod_collector():
    """Refresh heavy pod-per-node mapping less frequently."""
    while True:
        try:
            refresh_pod_per_node()
        except Exception as e:
            print(f"[pod-collector error] {e}")
        time.sleep(15)


def main():
    print(f"[k3s-api] Starting on port {PORT}...")
    print(f"[k3s-api] KUBECONFIG={KUBECONFIG}")

    t = threading.Thread(target=history_collector, daemon=True)
    t.start()
    t2 = threading.Thread(target=pod_collector, daemon=True)
    t2.start()

    server = ThreadingHTTPServer(("0.0.0.0", PORT), APIHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
