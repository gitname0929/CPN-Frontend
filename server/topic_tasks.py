#!/usr/bin/env python3
"""Topic benchmark task runner with streaming logs and result parsing."""

from __future__ import annotations

import json
import os
import queue
import shlex
import subprocess
import tempfile
import threading
import time
import uuid
import csv
from collections import deque
from pathlib import Path
from typing import Any

try:
    from openpyxl import load_workbook as _load_workbook
except ImportError:  # pragma: no cover
    _load_workbook = None


def _get_load_workbook():
    if _load_workbook is not None:
        return _load_workbook
    try:
        from openpyxl import load_workbook
        return load_workbook
    except ImportError as exc:
        raise RuntimeError("openpyxl is required to parse benchmark results") from exc

FEITENG_SCRIPT = "/home/a/709Docker/kubernetes_py_ctl_2/run.sh"
FEITENG_WORKDIR = "/home/a/709Docker/kubernetes_py_ctl_2"
ASCEND_HOST = "root@192.168.31.179"
ASCEND_SCRIPT = "/root/709Docker/kubernetes_py_ctl_2/run.sh"
ASCEND_WORKDIR = "/root/709Docker/kubernetes_py_ctl_2"
ASCEND_SSH_PASSWORD = os.environ.get("ASCEND_SSH_PASSWORD", "Mind@123")
PROJECT2_RELEASE_DIR = "/home/a/709Docker/PyTaskPredict-release"
PROJECT2_SCRIPT = f"{PROJECT2_RELEASE_DIR}/run_project2.sh"
PROJECT2_RESULTS_DIR = f"{PROJECT2_RELEASE_DIR}/results"
PROJECT3_WORKDIR = os.environ.get("PROJECT3_WORKDIR", "/home/a/709Docker/kt3_resource")
PROJECT3_ASCEND_SERVER_HOST = os.environ.get("PROJECT3_ASCEND_SERVER_HOST", "root@192.168.31.154")
PROJECT3_ASCEND_CLIENT_HOST = os.environ.get("PROJECT3_ASCEND_CLIENT_HOST", "root@192.168.31.247")
PROJECT3_ASCEND_SERVER_IP = os.environ.get("PROJECT3_ASCEND_SERVER_IP", "192.168.31.154")
PROJECT3_ASCEND_CLIENT_IP = os.environ.get("PROJECT3_ASCEND_CLIENT_IP", "192.168.31.247")
PROJECT3_FEITENG_CLIENT_IP = os.environ.get("PROJECT3_FEITENG_CLIENT_IP", "当前机器")
PROJECT3_SSH_PASSWORD = os.environ.get("PROJECT3_SSH_PASSWORD", ASCEND_SSH_PASSWORD)
PROJECT3_FEITENG_SSH_PASSWORD = os.environ.get("PROJECT3_FEITENG_SSH_PASSWORD", "Sancog123")
PROJECT3_SERVER_SCRIPT = "server_cpu_extreme_compute_torch_shared.py"
PROJECT3_CLIENT_SCRIPT = "client_ascend_fix_patched.py"
PROJECT3_ASCEND_PYTHON = os.environ.get("PROJECT3_ASCEND_PYTHON", "/usr/local/miniconda3/bin/python")
PROJECT3_ASCEND_ENV = os.environ.get("PROJECT3_ASCEND_ENV", "/usr/local/Ascend/ascend-toolkit/set_env.sh")
PROJECT3_TAIL_BACKEND = os.environ.get("PROJECT3_TAIL_BACKEND", "cpu")
PROJECT3_FEITENG_PYTHON = os.environ.get("PROJECT3_FEITENG_PYTHON", "python3")
PROJECT3_DEFAULT_PORT = int(os.environ.get("PROJECT3_PORT", "9999"))
PROJECT3_SERVER_READY_TIMEOUT = int(os.environ.get("PROJECT3_SERVER_READY_TIMEOUT", "600"))
PROJECT3_EXCLUDE_FIRST = int(os.environ.get("PROJECT3_EXCLUDE_FIRST", "5"))
PROJECT3_DEFAULT_TASKS = int(os.environ.get("PROJECT3_DEFAULT_TASKS", "100"))
PROJECT3_MODEL_ALIASES = {
    "deit_tiny_patch_16_224": "deit_tiny_patch16_224",
    "yolo5s": "yolov5",
    "yolov5s": "yolov5",
    "yolov5": "yolov5",
    "yolo8": "yolov8",
    "yolov8n": "yolov8",
    "yolov8": "yolov8",
    "vgg11_static": "vgg11",
}
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROJECT3_REGISTRY_PATH = Path(os.environ.get("PROJECT3_REGISTRY", str(PROJECT_ROOT / "model_registry_1v1.json")))
PROJECT3_MEMORY_CSV = {
    "ascend_ascend": PROJECT_ROOT / "public" / "data" / "topic3" / "图1.2：昇腾1：1内存图.csv",
    "ascend_feiteng": PROJECT_ROOT / "public" / "data" / "topic3" / "图2.2：飞腾1：1内存图.csv",
    "ascend_mixed": PROJECT_ROOT / "public" / "data" / "topic3" / "图2.2：飞腾1：1内存图.csv",
}
PROJECT3_MEMORY_MODEL_ALIASES = {
    "deit_tiny_patch16_224": "deit_tiny_patch_16_224",
    "yolov5": "yolov5s",
    "yolov8": "yolov8n",
    "vgg11": "vgg11_static",
}
PROJECT3_REGISTRY_MODEL_ALIASES = {
    "yolov5": "yolo5",
    "yolov8": "yolo8",
}
SSH_BASE_OPTS = [
    "-o",
    "StrictHostKeyChecking=no",
    "-o",
    "UserKnownHostsFile=/dev/null",
    "-o",
    "ConnectTimeout=15",
    "-o",
    "PreferredAuthentications=password",
    "-o",
    "PubkeyAuthentication=no",
]

TASK_RETENTION_SEC = 3600
_tasks: dict[str, dict[str, Any]] = {}
_lock = threading.RLock()


def _now_ms() -> int:
    return int(time.time() * 1000)


def _cleanup_old_tasks() -> None:
    cutoff = time.time() - TASK_RETENTION_SEC
    with _lock:
        stale = [task_id for task_id, task in _tasks.items() if task["created_at"] < cutoff]
        for task_id in stale:
            _tasks.pop(task_id, None)


def _format_number(value: Any) -> Any:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return value
    rounded = round(number, 2)
    return int(rounded) if rounded == int(rounded) else rounded


def _normalize_models(models: list[str]) -> str:
    cleaned = [item.strip() for item in models if item and item.strip()]
    if not cleaned or cleaned == ["all"]:
        return ""
    return ",".join(cleaned)


def _has_sshpass() -> bool:
    return subprocess.run(
        ["which", "sshpass"],
        capture_output=True,
        text=True,
        check=False,
    ).returncode == 0


def _build_ssh_command(remote_cmd: str) -> list[str]:
    ssh_cmd = ["ssh", *SSH_BASE_OPTS, ASCEND_HOST, remote_cmd]
    if not _has_sshpass():
        return ssh_cmd
    return ["sshpass", "-p", ASCEND_SSH_PASSWORD, *ssh_cmd]


def _build_scp_command(remote_path: str, local_path: str) -> list[str]:
    scp_cmd = ["scp", *SSH_BASE_OPTS, f"{ASCEND_HOST}:{remote_path}", local_path]
    if not _has_sshpass():
        return scp_cmd
    return ["sshpass", "-p", ASCEND_SSH_PASSWORD, *scp_cmd]


def _build_ssh_command_for(host: str, remote_cmd: str, password: str | None = None) -> list[str]:
    ssh_cmd = ["ssh", *SSH_BASE_OPTS, host, f"bash -lc {shlex.quote(remote_cmd)}"]
    if not _has_sshpass():
        return ssh_cmd
    return ["sshpass", "-p", password or ASCEND_SSH_PASSWORD, *ssh_cmd]


def _build_run_command(platform: str, rounds: int, models: list[str]) -> tuple[list[str], Path, str | None]:
    models_arg = _normalize_models(models)
    output_name = f"all_models_state_benchmark_round{rounds}.xlsx"

    if platform == "feiteng":
        cmd = ["bash", FEITENG_SCRIPT, "--rounds", str(rounds)]
        if models_arg:
            cmd.extend(["--models", models_arg])
        return cmd, Path(FEITENG_WORKDIR) / output_name, FEITENG_WORKDIR

    if platform == "ascend":
        remote_cmd = (
            f"cd {shlex.quote(ASCEND_WORKDIR)} && "
            f"bash {shlex.quote(ASCEND_SCRIPT)} --rounds {int(rounds)}"
        )
        if models_arg:
            remote_cmd += f" --models {shlex.quote(models_arg)}"
        cmd = _build_ssh_command(remote_cmd)
        remote_output = f"{ASCEND_WORKDIR}/{output_name}"
        return cmd, Path(remote_output), None

    raise ValueError(f"Unsupported platform: {platform}")


def _build_project2_run_command(board: str, dataset_group: str, load_level: str) -> tuple[list[str], Path, str | None]:
    output_name = f"{board}_{dataset_group}_{load_level}.csv"
    cmd = [
        "bash",
        PROJECT2_SCRIPT,
        "--board",
        board,
        "--dataset_group",
        dataset_group,
        "--load_level",
        load_level,
    ]
    return cmd, Path(PROJECT2_RESULTS_DIR) / output_name, PROJECT2_RELEASE_DIR


def _append_log(task: dict[str, Any], message: str, log_type: str = "stdout") -> None:
    entry = {"time": _now_ms(), "message": message.rstrip("\n"), "type": log_type}
    task["logs"].append(entry)
    for subscriber in list(task["subscribers"]):
        try:
            subscriber.put_nowait(entry)
        except queue.Full:
            pass


def _parse_summary_xlsx(xlsx_path: Path) -> list[dict[str, Any]]:
    load_workbook = _get_load_workbook()

    workbook = load_workbook(xlsx_path, read_only=True, data_only=True)
    sheet = workbook["summary"]
    rows = list(sheet.iter_rows(values_only=True))
    workbook.close()
    if len(rows) < 2:
        return []

    headers = [str(item).strip() if item is not None else "" for item in rows[0]]
    header_index = {name: idx for idx, name in enumerate(headers)}
    required = ["model", "avg_cold_start_sec", "avg_warm_start_sec", "theta_percent"]
    for name in required:
        if name not in header_index:
            raise RuntimeError(f"Missing column in summary sheet: {name}")

    parsed: list[dict[str, Any]] = []
    for row in rows[1:]:
        if not row or row[header_index["model"]] in (None, ""):
            continue
        parsed.append(
            {
                "model": row[header_index["model"]],
                "avgColdToHot": _format_number(row[header_index["avg_cold_start_sec"]]),
                "avgWarmToHot": _format_number(row[header_index["avg_warm_start_sec"]]),
                "improvementRatio": _format_number(row[header_index["theta_percent"]]),
            }
        )
    return parsed


def _parse_csv_rows(csv_path: Path) -> list[dict[str, Any]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file_obj:
        reader = csv.DictReader(file_obj)
        rows: list[dict[str, Any]] = []
        for row in reader:
            parsed = {}
            for key, value in row.items():
                if key is None:
                    continue
                parsed[key] = _format_number(value) if value not in (None, "") else value
            if any(value not in (None, "") for value in parsed.values()):
                rows.append(parsed)
        return rows


def _project3_model_name(model: str) -> str:
    cleaned = (model or "resnet50").strip()
    return PROJECT3_MODEL_ALIASES.get(cleaned, cleaned)


def _project3_pth_path(model: str) -> str:
    return f"{PROJECT3_WORKDIR}/models/backbone_{model}_pretrained.pth"


def _project3_cut_json_path(model: str, scenario: str) -> str:
    if scenario == "ascend_feiteng":
        path = Path(PROJECT3_WORKDIR) / "cut_json_fvs" / f"cut_f_s_{model}.json"
        if model == "lightvgg11" and not path.exists():
            path = Path(PROJECT3_WORKDIR) / "cut_json_fvs" / "cut_f_s_lightvg11.json"
        return str(path)
    if scenario == "ascend_mixed":
        return f"{PROJECT3_WORKDIR}/cut_json_2v1_fsVs/cut_double_s_{model}.json"
    return f"{PROJECT3_WORKDIR}/cut_json_svs/cut_{model}.json"


def _project3_client_profile(scenario: str) -> str:
    if scenario == "ascend_feiteng":
        return "ft"
    if scenario == "ascend_mixed":
        return "mixed"
    return "ascend"


def _project3_scenario_label(scenario: str) -> str:
    labels = {
        "ascend_ascend": "昇腾 server / 昇腾 client",
        "ascend_feiteng": "昇腾 server / 飞腾 client",
        "ascend_mixed": "昇腾 server / 飞腾 client + 昇腾 client",
    }
    return labels.get(scenario, scenario)


def _load_project3_registry() -> dict[str, Any]:
    if not PROJECT3_REGISTRY_PATH.exists():
        return {}
    with PROJECT3_REGISTRY_PATH.open("r", encoding="utf-8") as file_obj:
        data = json.load(file_obj)
    return data if isinstance(data, dict) else {}


def _project3_registry_key(model: str) -> str:
    return PROJECT3_REGISTRY_MODEL_ALIASES.get(model, model)


def _project3_model_config(model: str, scenario: str) -> dict[str, Any]:
    registry = _load_project3_registry()
    registry_key = _project3_registry_key(model)
    item = registry.get(registry_key) if registry else None
    client_profile = _project3_client_profile(scenario)
    if scenario in ("ascend_feiteng", "ascend_ascend", "ascend_mixed") and isinstance(item, dict):
        if item.get("enabled") is False:
            reason = item.get("disabled_reason") or "disabled in registry"
            raise RuntimeError(f"model {registry_key} is disabled: {reason}")
        clients = item.get("clients") or {}
        profile = clients.get(client_profile) or {}
        if isinstance(profile, dict):
            pth = item.get("pth") or _project3_pth_path(model)
            cut_json = profile.get("cut_json") or _project3_cut_json_path(model, scenario)
            arch = item.get("arch") or model
            device_keys = profile.get("device_keys") or [profile.get("device_key") or "device_0"]
            device_keys = [str(key) for key in device_keys if key]
            device_key = device_keys[0] if device_keys else "device_0"
            client_specs = profile.get("clients") or [{"type": client_profile, "device_key": device_key}]
            if not Path(str(pth)).exists():
                raise RuntimeError(f"pth file not found for {registry_key}: {pth}")
            if not Path(str(cut_json)).exists():
                raise RuntimeError(f"cut_json not found for {registry_key}/{client_profile}: {cut_json}")
            # Do not use registry num_classes blindly: current baseline files are ImageNet-1000
            # for several models while the 1v1 registry may contain 100-class experiment values.
            return {
                "registryKey": registry_key,
                "pth": str(pth),
                "cutJson": str(cut_json),
                "arch": str(arch),
                "deviceKey": str(device_key),
                "deviceKeys": device_keys or [str(device_key)],
                "clients": client_specs,
                "runtimeDir": f"{PROJECT3_WORKDIR}/runtime_split_cache_1v1_{client_profile}_{registry_key}",
            }
    return {
        "registryKey": registry_key,
        "pth": _project3_pth_path(model),
        "cutJson": _project3_cut_json_path(model, scenario),
        "arch": model,
        "deviceKey": "device_0",
        "deviceKeys": ["device_0"],
        "clients": [{"type": client_profile, "device_key": "device_0"}],
        "runtimeDir": f"{PROJECT3_WORKDIR}/runtime_split_cache_1v1_{client_profile}_{registry_key}",
    }


def _project3_baseline_path(model: str, scenario: str) -> Path:
    baseline_dir = "baseline_f" if scenario == "ascend_feiteng" else "baseline_s"
    candidates = [
        Path(PROJECT3_WORKDIR) / baseline_dir / f"baseline_{model}_1cpu_2g_onnx.json",
    ]
    if model == "yolov5":
        candidates.append(Path(PROJECT3_WORKDIR) / baseline_dir / "baseline_yolo5_1cpu_2g_onnx.json")
    if model == "yolov8":
        candidates.append(Path(PROJECT3_WORKDIR) / baseline_dir / "baseline_yolo8_1cpu_2g_onnx.json")
    if model == "mobilevgg":
        candidates.append(Path(PROJECT3_WORKDIR) / baseline_dir / "baseline_mobilevgg_fp32_1cpu_2g_onnx.json")
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


def _json_get_path(data: Any, path: list[Any]) -> Any:
    cur = data
    for key in path:
        if isinstance(key, int):
            if not isinstance(cur, list) or len(cur) <= key:
                return None
            cur = cur[key]
            continue
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur


def _parse_project3_baseline(model: str, scenario: str) -> dict[str, Any]:
    if scenario == "ascend_mixed":
        ascend_baseline = _parse_project3_baseline(model, "ascend_ascend")
        feiteng_baseline = _parse_project3_baseline(model, "ascend_feiteng")

        def _avg(left, right):
            try:
                values = [float(item) for item in (left, right) if item is not None]
            except (TypeError, ValueError):
                return None
            return _format_number(sum(values) / len(values)) if values else None

        return {
            "latencyMs": _avg(ascend_baseline.get("latencyMs"), feiteng_baseline.get("latencyMs")),
            "memoryMb": _avg(ascend_baseline.get("memoryMb"), feiteng_baseline.get("memoryMb")),
            "source": f"{ascend_baseline.get('source')} + {feiteng_baseline.get('source')}",
        }

    path = _project3_baseline_path(model, scenario)
    if not path.exists():
        return {"latencyMs": None, "memoryMb": None, "source": str(path)}
    with path.open("r", encoding="utf-8") as file_obj:
        data = json.load(file_obj)
    latency = _json_get_path(data, ["results", 0, "avg_ms_median"])
    if latency is None:
        latency = _json_get_path(data, ["results", 0, "benchmark", "avg_ms_summary", "median"])
    memory = _json_get_path(data, ["results", 0, "benchmark", "mem", "mean"])
    return {
        "latencyMs": _format_number(latency),
        "memoryMb": _format_number(memory),
        "source": str(path),
    }


def _project3_memory_model_name(model: str) -> str:
    return PROJECT3_MEMORY_MODEL_ALIASES.get(model, model)


def _parse_project3_memory_metrics(model: str, scenario: str) -> dict[str, Any]:
    csv_path = PROJECT3_MEMORY_CSV.get(scenario)
    if not csv_path or not csv_path.exists():
        return {"baselineMemoryMb": None, "methodMemoryMb": None, "source": str(csv_path) if csv_path else ""}

    target_model = _project3_memory_model_name(model)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file_obj:
        reader = csv.reader(file_obj)
        rows = list(reader)

    if len(rows) < 5:
        return {"baselineMemoryMb": None, "methodMemoryMb": None, "source": str(csv_path)}

    header = [item.strip() for item in rows[3]]
    full_idx = header.index("完整模型内存占用") if "完整模型内存占用" in header else 1
    head_idx = header.index("head模型内存占用") if "head模型内存占用" in header else 2
    for row in rows[4:]:
        if not row:
            continue
        if row[0].strip() != target_model:
            continue
        return {
            "baselineMemoryMb": _format_number(row[full_idx] if len(row) > full_idx else None),
            "methodMemoryMb": _format_number(row[head_idx] if len(row) > head_idx else None),
            "source": str(csv_path),
        }

    return {"baselineMemoryMb": None, "methodMemoryMb": None, "source": str(csv_path)}


def _extract_metric(text: str, name: str) -> Any:
    import re

    pattern = re.compile(rf"{re.escape(name)}=([-+]?\d+(?:\.\d+)?|nan|null|None)")
    matches = pattern.findall(text or "")
    for raw in reversed(matches):
        if raw in ("nan", "null", "None"):
            continue
        try:
            return _format_number(float(raw))
        except ValueError:
            continue
    return None


def _terminate_process(process: subprocess.Popen | None) -> None:
    if not process or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()


def _wait_for_project3_server_port(
    task: dict[str, Any],
    port: int,
    server_process: subprocess.Popen | None = None,
    timeout_sec: int | None = None,
) -> bool:
    timeout_sec = timeout_sec or PROJECT3_SERVER_READY_TIMEOUT
    deadline = time.time() + timeout_sec
    remote_cmd = f"ss -lnt | grep -q ':{int(port)} '"
    cmd = _build_ssh_command_for(PROJECT3_ASCEND_SERVER_HOST, remote_cmd, PROJECT3_SSH_PASSWORD)
    next_log_at = time.time()
    while time.time() < deadline:
        if server_process is not None and server_process.poll() is not None:
            return False
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if completed.returncode == 0:
            return True
        if time.time() >= next_log_at:
            remaining = max(0, int(deadline - time.time()))
            _append_log(
                task,
                f"server 仍在启动，继续等待端口 {port}，剩余 {remaining}s；首次运行可能正在 ATC 编译 OM 产物",
                "info",
            )
            next_log_at = time.time() + 10
        time.sleep(2)
    return False


def _cleanup_project3_server_port(port: int) -> None:
    remote_cmd = (
        "pkill -TERM -f server_cpu_extreme_compute_torch_shared.py || true; "
        "sleep 1; "
        "pkill -KILL -f server_cpu_extreme_compute_torch_shared.py || true; "
        "pkill -TERM -f 'Ascend/.*/bin/atc' || true; "
        "pkill -TERM -f 'Ascend/.*/bin/atc.bin' || true; "
        "pkill -TERM -f ' ccec ' || true; "
        "pid=$(ss -lntp | sed -n "
        + shlex.quote(f"s/.*:{int(port)}.*pid=\\([0-9]*\\).*/\\1/p")
        + " | head -n1); "
        "if test -n \"$pid\"; then kill \"$pid\" || true; fi"
    )
    subprocess.run(
        _build_ssh_command_for(PROJECT3_ASCEND_SERVER_HOST, remote_cmd, PROJECT3_SSH_PASSWORD),
        capture_output=True,
        text=True,
        timeout=30,
    )


def _start_logged_process(
    task: dict[str, Any],
    label: str,
    cmd: list[str],
    workdir: str | None = None,
) -> tuple[subprocess.Popen, list[str]]:
    _append_log(task, f"{label} 命令: {' '.join(shlex.quote(part) for part in cmd)}", "info")
    process = subprocess.Popen(
        cmd,
        cwd=workdir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )
    lines: list[str] = []

    def _reader() -> None:
        assert process.stdout is not None
        for line in iter(process.stdout.readline, ""):
            clean = line.rstrip("\n")
            lines.append(clean)
            _append_log(task, f"[{label}] {clean}", "stdout")

    threading.Thread(target=_reader, daemon=True).start()
    return process, lines


def _project3_server_command(model: str, scenario: str, tasks: int, port: int) -> list[str]:
    config = _project3_model_config(model, scenario)
    device_key = config["deviceKey"]
    device_keys = config.get("deviceKeys") or [device_key]
    clients = config.get("clients") or []
    total_tasks = int(tasks) + PROJECT3_EXCLUDE_FIRST
    env_prefix = f"source {shlex.quote(PROJECT3_ASCEND_ENV)} && " if PROJECT3_ASCEND_ENV else ""
    command = (
        f"cd {shlex.quote(PROJECT3_WORKDIR)} && "
        f"{env_prefix}"
        f"{shlex.quote(PROJECT3_ASCEND_PYTHON)} -u {shlex.quote(PROJECT3_SERVER_SCRIPT)} "
        f"--host 0.0.0.0 --port {int(port)} "
        f"--pth {shlex.quote(config['pth'])} "
        f"--cut-json {shlex.quote(config['cutJson'])} "
        f"--arch {shlex.quote(config['arch'])} "
        f"--device-key {shlex.quote(device_key)} --device-keys {shlex.quote(','.join(device_keys))} "
        f"--tail-backend {shlex.quote(PROJECT3_TAIL_BACKEND)} --device-id 0 "
        f"--expect-clients {max(1, len(clients))} --tasks-per-client {total_tasks} "
        f"--exclude-first {PROJECT3_EXCLUDE_FIRST} --require-hello "
        f"--runtime-dir {shlex.quote(config['runtimeDir'])} "
        f"--log-every 10 --print-avg-every 50"
    )
    return _build_ssh_command_for(PROJECT3_ASCEND_SERVER_HOST, command, PROJECT3_SSH_PASSWORD)


def _project3_client_command_for(
    client_type: str,
    device_key: str,
    tasks: int,
    port: int,
) -> tuple[list[str], str | None]:
    command = [
        PROJECT3_ASCEND_PYTHON if client_type == "ascend" else PROJECT3_FEITENG_PYTHON,
        "-u",
        PROJECT3_CLIENT_SCRIPT,
        "--server-ip",
        PROJECT3_ASCEND_SERVER_IP,
        "--port",
        str(port),
        "--workdir",
        "./model_cache",
        "--device-key",
        device_key,
        "--num-tasks",
        str(tasks),
        "--exclude-first",
        str(PROJECT3_EXCLUDE_FIRST),
    ]
    if client_type == "ascend":
        env_prefix = f"source {shlex.quote(PROJECT3_ASCEND_ENV)} && " if PROJECT3_ASCEND_ENV else ""
        remote = f"cd {shlex.quote(PROJECT3_WORKDIR)} && {env_prefix}{' '.join(shlex.quote(part) for part in command)}"
        return _build_ssh_command_for(PROJECT3_ASCEND_CLIENT_HOST, remote, PROJECT3_SSH_PASSWORD), None
    command.append("--force-cpu")
    return command, PROJECT3_WORKDIR


def _project3_client_commands(scenario: str, model: str, tasks: int, port: int) -> list[tuple[str, list[str], str | None]]:
    config = _project3_model_config(model, scenario)
    clients = config.get("clients") or []
    commands: list[tuple[str, list[str], str | None]] = []
    for index, client in enumerate(clients, start=1):
        client_type = str(client.get("type") or _project3_client_profile(scenario))
        device_key = str(client.get("device_key") or config["deviceKey"])
        cmd, workdir = _project3_client_command_for(client_type, device_key, tasks, port)
        commands.append((f"client{index}:{client_type}:{device_key}", cmd, workdir))
    if commands:
        return commands
    client_type = "ascend" if scenario == "ascend_ascend" else "ft"
    cmd, workdir = _project3_client_command_for(client_type, config["deviceKey"], tasks, port)
    return [(f"client1:{client_type}:{config['deviceKey']}", cmd, workdir)]


def _project3_improvement(baseline_value: Any, ours_value: Any) -> Any:
    try:
        baseline_num = float(baseline_value)
        ours_num = float(ours_value)
    except (TypeError, ValueError):
        return None
    if baseline_num <= 0:
        return None
    return _format_number((baseline_num - ours_num) / baseline_num * 100)


def _project3_tail_memory(memory_metrics: dict[str, Any], baseline: dict[str, Any]) -> Any:
    baseline_memory = memory_metrics.get("baselineMemoryMb") or baseline.get("memoryMb")
    head_memory = memory_metrics.get("methodMemoryMb")
    try:
        return max(0.0, float(baseline_memory) - float(head_memory))
    except (TypeError, ValueError):
        return None


def _project3_mixed_memory_saving(model: str) -> dict[str, Any]:
    ascend_baseline = _parse_project3_baseline(model, "ascend_ascend")
    feiteng_baseline = _parse_project3_baseline(model, "ascend_feiteng")
    ascend_memory = _parse_project3_memory_metrics(model, "ascend_ascend")
    feiteng_memory = _parse_project3_memory_metrics(model, "ascend_feiteng")
    ascend_full = ascend_memory.get("baselineMemoryMb") or ascend_baseline.get("memoryMb")
    feiteng_full = feiteng_memory.get("baselineMemoryMb") or feiteng_baseline.get("memoryMb")
    ascend_head = ascend_memory.get("methodMemoryMb")
    feiteng_head = feiteng_memory.get("methodMemoryMb")
    ascend_tail = _project3_tail_memory(ascend_memory, ascend_baseline)
    feiteng_tail = _project3_tail_memory(feiteng_memory, feiteng_baseline)
    if any(item is None for item in (ascend_full, feiteng_full, ascend_head, feiteng_head, ascend_tail, feiteng_tail)):
        return {"savedMb": None, "savedRatio": None}
    try:
        baseline_total = float(ascend_full) + float(feiteng_full)
        ours_total = float(ascend_head) + float(feiteng_head) + max(float(ascend_tail), float(feiteng_tail))
    except (TypeError, ValueError):
        return {"savedMb": None, "savedRatio": None}
    saved = baseline_total - ours_total
    return {
        "savedMb": _format_number(saved),
        "savedRatio": _format_number(saved / baseline_total * 100) if baseline_total > 0 else None,
    }


def _project3_result_row(
    scenario: str,
    scenario_label: str,
    model: str,
    baseline: dict[str, Any],
    memory_metrics: dict[str, Any],
    latency=None,
    client_latencies: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if scenario == "ascend_mixed":
        ascend_baseline = _parse_project3_baseline(model, "ascend_ascend")
        feiteng_baseline = _parse_project3_baseline(model, "ascend_feiteng")
        client_latencies = client_latencies or {}
        feiteng_latency = client_latencies.get("ft")
        ascend_latency = client_latencies.get("ascend")
        memory_saving = _project3_mixed_memory_saving(model)
        return {
            "场景": scenario_label,
            "模型": model,
            "飞腾Baseline端到端时延(ms)": feiteng_baseline.get("latencyMs"),
            "飞腾Ours端到端时延(ms)": feiteng_latency,
            "飞腾完成时间性能提升比(%)": _project3_improvement(feiteng_baseline.get("latencyMs"), feiteng_latency),
            "昇腾Baseline端到端时延(ms)": ascend_baseline.get("latencyMs"),
            "昇腾Ours端到端时延(ms)": ascend_latency,
            "昇腾完成时间性能提升比(%)": _project3_improvement(ascend_baseline.get("latencyMs"), ascend_latency),
            "共享切分内存节省(MB)": memory_saving.get("savedMb"),
            "共享切分内存节省比(%)": memory_saving.get("savedRatio"),
        }

    baseline_latency = baseline["latencyMs"]
    return {
        "场景": scenario_label,
        "模型": model,
        "Baseline端到端时延(ms)": baseline_latency,
        "Ours端到端时延(ms)": latency,
        "完成时间性能提升比(%)": _project3_improvement(baseline_latency, latency),
    }


def _run_project3_model(
    task: dict[str, Any],
    scenario: str,
    model: str,
    tasks: int,
    port: int,
) -> dict[str, Any]:
    scenario_label = _project3_scenario_label(scenario)
    baseline = _parse_project3_baseline(model, scenario)
    memory_metrics = _parse_project3_memory_metrics(model, scenario)
    server_process: subprocess.Popen | None = None
    client_processes: list[subprocess.Popen] = []
    client_outputs: list[tuple[str, list[str]]] = []
    server_lines: list[str] = []

    try:
        _append_log(
            task,
            f"开始执行模型 ({scenario_label} / {model} / 统计 {tasks} 次 / 预热 {PROJECT3_EXCLUDE_FIRST} 次)",
            "info",
        )
        _append_log(task, f"Baseline 数据: {baseline['source']}", "info")
        _append_log(task, f"内存数据: {memory_metrics['source']}", "info")
        model_config = _project3_model_config(model, scenario)
        _append_log(
            task,
            "1v1 配置: "
            f"registry={model_config['registryKey']} arch={model_config['arch']} "
            f"device_keys={','.join(model_config.get('deviceKeys') or [model_config['deviceKey']])} "
            f"clients={model_config.get('clients')} tail_backend={PROJECT3_TAIL_BACKEND} "
            f"cut_json={model_config['cutJson']} runtime_dir={model_config['runtimeDir']}",
            "info",
        )
        _cleanup_project3_server_port(port)
        server_cmd = _project3_server_command(model, scenario, tasks, port)
        server_process, server_lines = _start_logged_process(task, f"server:{model}", server_cmd)
        task["process"] = server_process

        _append_log(task, f"等待 server 端口就绪: {PROJECT3_ASCEND_SERVER_IP}:{port}", "info")
        if not _wait_for_project3_server_port(task, port, server_process):
            if server_process.poll() is not None:
                raise RuntimeError(f"server 启动失败，退出码 {server_process.returncode}")
            raise RuntimeError(f"server 端口未就绪: {PROJECT3_ASCEND_SERVER_IP}:{port}")
        _append_log(task, "server 端口已就绪", "success")

        for label, client_cmd, client_workdir in _project3_client_commands(scenario, model, tasks, port):
            client_process, client_lines = _start_logged_process(task, f"{label}:{model}", client_cmd, client_workdir)
            client_processes.append(client_process)
            client_outputs.append((label, client_lines))
        if client_processes:
            task["process"] = client_processes[-1]

        failed_clients = []
        for index, process in enumerate(client_processes):
            client_code = process.wait()
            if client_code != 0:
                failed_clients.append(f"{client_outputs[index][0]}={client_code}")
        if failed_clients:
            raise RuntimeError(f"client 脚本退出码: {', '.join(failed_clients)}")

        try:
            server_process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            _terminate_process(server_process)
        server_code = server_process.poll()
        if server_code not in (0, None):
            _append_log(task, f"server 脚本退出码 {server_code}", "error")

        latencies = []
        client_latencies: dict[str, Any] = {}
        for _label, lines in client_outputs:
            client_text = "\n".join(lines)
            latency_item = _extract_metric(client_text, "avg_e2e_ms")
            if latency_item is None:
                latency_item = _extract_metric(client_text, "e2e_ms")
            if latency_item is not None:
                try:
                    latencies.append(float(latency_item))
                    parts = _label.split(":")
                    if len(parts) >= 2:
                        client_latencies[parts[1]] = _format_number(float(latency_item))
                except (TypeError, ValueError):
                    pass
        latency = _format_number(sum(latencies) / len(latencies)) if latencies else None
        return _project3_result_row(scenario, scenario_label, model, baseline, memory_metrics, latency, client_latencies)
    except Exception as exc:
        for process in client_processes:
            _terminate_process(process)
        _terminate_process(server_process)
        row = _project3_result_row(scenario, scenario_label, model, baseline, memory_metrics)
        row["错误"] = str(exc)
        _append_log(task, f"模型 {model} 执行失败: {exc}", "error")
        return row


def _run_project3_task(task_id: str) -> None:
    with _lock:
        task = _tasks.get(task_id)
    if not task:
        return

    payload = task["payload"]
    scenario = payload["scenario"]
    raw_models = payload.get("models") or [payload.get("model") or "resnet50"]
    models = [_project3_model_name(item) for item in raw_models if item]
    if not models:
        models = ["resnet50"]
    tasks = int(payload.get("numTasks") or PROJECT3_DEFAULT_TASKS)
    port = int(payload.get("port") or PROJECT3_DEFAULT_PORT)
    scenario_label = _project3_scenario_label(scenario)
    _append_log(task, f"开始执行课题三 ({scenario_label} / {len(models)} 个模型 / {tasks} 次)", "info")
    rows = []
    for index, model in enumerate(models, start=1):
        _append_log(task, f"[{index}/{len(models)}] 准备执行模型: {model}", "info")
        rows.append(_run_project3_model(task, scenario, model, tasks, port))

    has_error = any(row.get("错误") for row in rows)
    with _lock:
        current = _tasks.get(task_id)
        if not current:
            return
        current["result_rows"] = rows
        current["status"] = "failed" if has_error else "completed"
        current["error"] = "部分模型执行失败" if has_error else None
        current["process"] = None
        _append_log(current, f"执行完成，共 {len(rows)} 条结果", "success" if not has_error else "error")


def _fetch_remote_xlsx(remote_path: str) -> Path:
    temp_file = Path(tempfile.mkstemp(prefix="topic1_result_", suffix=".xlsx")[1])
    cmd = _build_scp_command(remote_path, str(temp_file))
    completed = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if completed.returncode != 0:
        temp_file.unlink(missing_ok=True)
        raise RuntimeError(completed.stderr.strip() or "Failed to download remote result file")
    return temp_file


def _resolve_result_rows(task: dict[str, Any]) -> list[dict[str, Any]]:
    payload = task["payload"]
    if payload.get("topicId") == 2:
        _, output_path, _ = _build_project2_run_command(
            payload["board"],
            payload["dataset_group"],
            payload["load_level"],
        )
        if not output_path.exists():
            raise RuntimeError(f"Result file not found: {output_path}")
        return _parse_csv_rows(output_path)

    _, output_path, workdir = _build_run_command(
        payload["platform"],
        payload["rounds"],
        payload["models"],
    )

    local_path = output_path
    temp_path: Path | None = None
    try:
        if payload["platform"] == "ascend":
            temp_path = _fetch_remote_xlsx(str(output_path))
            local_path = temp_path
        elif not local_path.exists():
            raise RuntimeError(f"Result file not found: {local_path}")

        return _parse_summary_xlsx(local_path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def _run_process(task_id: str) -> None:
    with _lock:
        task = _tasks.get(task_id)
    if not task:
        return

    payload = task["payload"]
    topic_id = payload.get("topicId", 1)
    try:
        if topic_id == 2:
            cmd, output_path, workdir = _build_project2_run_command(
                payload["board"],
                payload["dataset_group"],
                payload["load_level"],
            )
        else:
            cmd, output_path, workdir = _build_run_command(
                payload["platform"],
                payload["rounds"],
                payload["models"],
            )
    except Exception as exc:
        with _lock:
            task = _tasks.get(task_id)
            if task:
                task["status"] = "failed"
                task["error"] = str(exc)
                _append_log(task, str(exc), "error")
        return

    if topic_id == 2:
        board_label = "昇腾" if payload["board"] == "st" else "飞腾"
        _append_log(
            task,
            f"开始执行课题二 ({board_label} / {payload['dataset_group']} / {payload['load_level']})",
            "info",
        )
    else:
        platform_label = "飞腾" if payload["platform"] == "feiteng" else "昇腾"
        _append_log(task, f"开始执行课题一 ({platform_label})", "info")
    _append_log(task, f"命令: {' '.join(shlex.quote(part) for part in cmd)}", "info")
    _append_log(task, f"结果文件: {output_path}", "info")

    if topic_id == 2:
        Path(PROJECT2_RESULTS_DIR).mkdir(parents=True, exist_ok=True)

    try:
        process = subprocess.Popen(
            cmd,
            cwd=workdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
    except Exception as exc:
        with _lock:
            task = _tasks.get(task_id)
            if task:
                task["status"] = "failed"
                task["error"] = str(exc)
                _append_log(task, f"启动失败: {exc}", "error")
        return

    with _lock:
        task = _tasks.get(task_id)
        if task:
            task["process"] = process

    assert process.stdout is not None
    for line in iter(process.stdout.readline, ""):
        if not line:
            break
        with _lock:
            current = _tasks.get(task_id)
            if not current:
                process.kill()
                return
            _append_log(current, line.rstrip("\n"), "stdout")

    return_code = process.wait()
    with _lock:
        task = _tasks.get(task_id)
        if not task:
            return

        if return_code != 0:
            task["status"] = "failed"
            task["error"] = f"脚本退出码 {return_code}"
            _append_log(task, task["error"], "error")
            return

        try:
            task["result_rows"] = _resolve_result_rows(task)
            task["status"] = "completed"
            _append_log(task, f"执行完成，共 {len(task['result_rows'])} 条结果", "success")
        except Exception as exc:
            task["status"] = "failed"
            task["error"] = str(exc)
            _append_log(task, f"结果解析失败: {exc}", "error")


def start_task(payload: dict[str, Any]) -> str:
    _cleanup_old_tasks()
    task_id = uuid.uuid4().hex
    task = {
        "id": task_id,
        "status": "running",
        "created_at": time.time(),
        "payload": payload,
        "logs": deque(maxlen=5000),
        "subscribers": [],
        "result_rows": [],
        "error": None,
        "process": None,
    }
    with _lock:
        _tasks[task_id] = task

    target = _run_project3_task if payload.get("topicId") == 3 else _run_process
    thread = threading.Thread(target=target, args=(task_id,), daemon=True)
    thread.start()
    return task_id


def get_task(task_id: str) -> dict[str, Any] | None:
    with _lock:
        task = _tasks.get(task_id)
        if not task:
            return None
        return {
            "taskId": task_id,
            "status": task["status"],
            "error": task["error"],
            "rows": list(task["result_rows"]),
            "logCount": len(task["logs"]),
        }


def subscribe_logs(task_id: str) -> tuple[queue.Queue, dict[str, Any] | None]:
    subscriber: queue.Queue = queue.Queue(maxsize=1000)
    with _lock:
        task = _tasks.get(task_id)
        if not task:
            return subscriber, None
        task["subscribers"].append(subscriber)
        snapshot = list(task["logs"])
        current = {
            "status": task["status"],
            "error": task["error"],
            "rows": list(task["result_rows"]),
        }
    for entry in snapshot:
        subscriber.put(entry)
    return subscriber, current


def unsubscribe_logs(task_id: str, subscriber: queue.Queue) -> None:
    with _lock:
        task = _tasks.get(task_id)
        if not task:
            return
        if subscriber in task["subscribers"]:
            task["subscribers"].remove(subscriber)


def cancel_task(task_id: str) -> bool:
    with _lock:
        task = _tasks.get(task_id)
        if not task:
            return False
        process = task.get("process")
        payload = task.get("payload") or {}
        if process and process.poll() is None:
            process.kill()
        if payload.get("topicId") == 3:
            try:
                _cleanup_project3_server_port(int(payload.get("port") or PROJECT3_DEFAULT_PORT))
            except Exception:
                pass
        if task["status"] == "running":
            task["status"] = "failed"
            task["error"] = "任务已取消"
            _append_log(task, "任务已取消", "error")
        return True
