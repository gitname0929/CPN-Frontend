#!/usr/bin/env python3
"""K3s cluster API server for big-screen dashboard."""
import json
import queue
import shlex
import subprocess
import threading
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from topic_tasks import (
    ASCEND_HOST,
    ASCEND_SCRIPT,
    ASCEND_SSH_PASSWORD,
    TOPIC1_ROUNDS,
    PROJECT3_ASCEND_CLIENT1_HOST,
    PROJECT3_CLIENT_SCRIPT,
    PROJECT3_SSH_PASSWORD,
    PROJECT3_WORKDIR,
    PROJECT4_ASCEND_HOST,
    PROJECT4_ASCEND_WORKDIR,
    PROJECT4_SSH_PASSWORD,
    PROJECT3_SCENARIO,
    PROJECT3_SCENARIOS,
    _build_ssh_command_for,
    cancel_task,
    get_task,
    start_task,
    subscribe_logs,
    unsubscribe_logs,
)

KUBECONFIG = "/home/a/.kube/config"
CACHE_TTL = 8
NODE_RESOURCE_TTL = 10
K3S_API_SERVER = "https://127.0.0.1:6443"
HISTORY_SIZE = 60
PORT = 8099
MODEL_DEPLOYMENTS = [
    "resnet18-deploy",
    "resnet50-deploy",
    "resnet101-deploy",
    "mobilevgg-deploy",
    "lightvgg11-deploy",
    "levit128-deploy",
    "deit-tiny-patch16-224-deploy",
    "mobilenetv2-deploy",
    "mobilenetv3-deploy",
    "yolov8n-deploy",
    "yolov5s-deploy",
    "hetero-task-deploy",
]

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


def cleanup_ascend_179_environment():
    """Best-effort cleanup for known task processes on 192.168.31.179."""
    targets = [
        shlex.quote(str(ASCEND_SCRIPT)),
        shlex.quote(f"{PROJECT3_WORKDIR}/{PROJECT3_CLIENT_SCRIPT}"),
        shlex.quote(f"{PROJECT4_ASCEND_WORKDIR}/orchestrator/our_scheduler_api.py"),
    ]
    remote_cmd = "\n".join(f"pkill -TERM -f {target} || true" for target in targets)
    host = PROJECT4_ASCEND_HOST or PROJECT3_ASCEND_CLIENT1_HOST or ASCEND_HOST
    password = PROJECT4_SSH_PASSWORD or PROJECT3_SSH_PASSWORD or ASCEND_SSH_PASSWORD
    try:
        completed = subprocess.run(
            _build_ssh_command_for(host, remote_cmd, password),
            capture_output=True,
            text=True,
            timeout=15,
        )
    except Exception as exc:
        return {"host": host, "cleaned": False, "error": str(exc)}
    output = (completed.stderr or completed.stdout or "").strip()
    return {
        "host": host,
        "cleaned": completed.returncode == 0,
        "error": output if completed.returncode != 0 else "",
    }


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

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def _send_error(self, msg, code=500):
        self._send_json({"ret": 0, "msg": msg}, code)

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

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

            # /api/tasks/{taskId}/stream
            elif path.startswith("/api/tasks/") and path.endswith("/stream"):
                task_id = path[len("/api/tasks/") : -len("/stream")].strip("/")
                self._handle_task_stream(task_id)

            # /api/tasks/{taskId}/result
            elif path.startswith("/api/tasks/") and path.endswith("/result"):
                task_id = path[len("/api/tasks/") : -len("/result")].strip("/")
                self._handle_task_result(task_id)

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

    def _handle_cleanup_pods(self):
        results = []
        failures = []
        for deployment in MODEL_DEPLOYMENTS:
            raw = run_kubectl(["scale", "deploy", deployment, "--replicas=0", "-n", "default"])
            ok = raw is not None
            results.append({"deployment": deployment, "scaled": ok})
            if not ok:
                failures.append(deployment)

        with _lock:
            _cache["pods_count"] = None
            _cache["pods_count_ts"] = 0
            _cache["pod_per_node"] = None
            _cache["pod_per_node_ts"] = 0

        remote_cleanup = cleanup_ascend_179_environment()
        if failures:
            return self._send_json(
                {
                    "ret": 0,
                    "msg": "部分 Deployment 缩容失败",
                    "data": {"failures": failures, "results": results, "remoteCleanup": remote_cleanup},
                },
                500,
            )
        self._send_json({"ret": 1, "data": {"results": results, "remoteCleanup": remote_cleanup}})

    def _handle_task_stream(self, task_id):
        subscriber, current = subscribe_logs(task_id)
        if current is None:
            return self._send_error("Task not found", 404)

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self._send_cors_headers()
        self.end_headers()

        try:
            while True:
                try:
                    entry = subscriber.get(timeout=15)
                    payload = json.dumps(
                        {"message": entry["message"], "type": entry["type"]},
                        ensure_ascii=False,
                    )
                    self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
                    self.wfile.flush()
                except queue.Empty:
                    task = get_task(task_id)
                    if not task or task["status"] != "running":
                        break
                    self.wfile.write(b": heartbeat\n\n")
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            unsubscribe_logs(task_id, subscriber)

    def _handle_task_result(self, task_id):
        task = get_task(task_id)
        if not task:
            return self._send_error("Task not found", 404)
        self._send_json(
            {
                "ret": 1,
                "data": {
                    "taskId": task["taskId"],
                    "status": task["status"],
                    "error": task["error"],
                    "rows": task["rows"],
                },
            }
        )

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        normalized_path = path.rstrip("/") or "/"
        try:
            if normalized_path == "/api/tasks/run":
                self._handle_task_run()
            elif normalized_path in ("/api/k8s/cleanupPods", "/k8s/cleanupPods", "/api/cleanupPods"):
                self._handle_cleanup_pods()
            else:
                self._send_error("Not implemented", 405)
        except Exception as e:
            print(f"[handler error] {path}: {e}")
            self._send_error(str(e))

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if path.startswith("/api/tasks/"):
                task_id = path[len("/api/tasks/") :].strip("/")
                if not task_id or "/" in task_id:
                    return self._send_error("Invalid task id", 400)
                cancelled = cancel_task(task_id)
                if not cancelled:
                    return self._send_error("Task not found", 404)
                self._send_json({"ret": 1, "data": {"taskId": task_id, "cancelled": True}})
            else:
                self._send_error("Not found", 404)
        except Exception as e:
            print(f"[handler error] {path}: {e}")
            self._send_error(str(e))

    def _handle_task_run(self):
        payload = self._read_json_body()
        try:
            topic_id = int(payload.get("topicId"))
        except (TypeError, ValueError):
            return self._send_error("请选择课题", 400)
        if topic_id not in (1, 2, 3, 4):
            return self._send_error("该课题运行配置暂未开放", 400)

        if topic_id == 3:
            scenario = payload.get("scenario") or PROJECT3_SCENARIO
            models = payload.get("models") or []
            if not models and payload.get("model"):
                models = [payload.get("model")]
            num_tasks = payload.get("numTasks") or 100
            port = payload.get("port") or 9999

            if scenario not in PROJECT3_SCENARIOS:
                return self._send_error("请选择运行场景", 400)
            if not isinstance(models, list) or not models:
                return self._send_error("请选择运行模型", 400)
            try:
                num_tasks = int(num_tasks)
            except (TypeError, ValueError):
                return self._send_error("请求次数无效", 400)
            if num_tasks < 1:
                return self._send_error("统计请求次数至少为 1", 400)
            try:
                port = int(port)
            except (TypeError, ValueError):
                return self._send_error("端口无效", 400)

            task_id = start_task(
                {
                    "topicId": topic_id,
                    "scenario": scenario,
                    "models": models,
                    "numTasks": num_tasks,
                    "port": port,
                }
            )
            return self._send_json({"ret": 1, "data": {"taskId": task_id}})

        if topic_id == 2:
            board = payload.get("board")
            dataset_group = payload.get("dataset_group")
            load_level = payload.get("load_level")

            if board not in ("st", "ft"):
                return self._send_error("请选择板子类型", 400)
            if dataset_group not in ("google", "huawei"):
                return self._send_error("请选择数据集分组", 400)
            if load_level not in ("L", "H"):
                return self._send_error("请选择负载等级", 400)

            task_id = start_task(
                {
                    "topicId": topic_id,
                    "board": board,
                    "dataset_group": dataset_group,
                    "load_level": load_level,
                }
            )
            return self._send_json({"ret": 1, "data": {"taskId": task_id}})

        if topic_id == 4:
            device = payload.get("device")
            rounds = payload.get("rounds") or 300

            if device not in ("feiteng", "ascend"):
                return self._send_error("请选择执行设备", 400)
            try:
                rounds = int(rounds)
            except (TypeError, ValueError):
                return self._send_error("总轮数无效", 400)
            if rounds < 1:
                return self._send_error("总轮数至少为 1", 400)

            task_id = start_task(
                {
                    "topicId": topic_id,
                    "device": device,
                    "rounds": rounds,
                }
            )
            return self._send_json({"ret": 1, "data": {"taskId": task_id}})

        platform = payload.get("platform")
        models = payload.get("models") or []

        if platform not in ("feiteng", "ascend"):
            return self._send_error("请选择硬件平台", 400)
        if not models:
            return self._send_error("请至少选择一个模型", 400)

        task_id = start_task(
            {
                "topicId": topic_id,
                "platform": platform,
                "models": models,
                "rounds": TOPIC1_ROUNDS,
            }
        )
        self._send_json({"ret": 1, "data": {"taskId": task_id}})

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
