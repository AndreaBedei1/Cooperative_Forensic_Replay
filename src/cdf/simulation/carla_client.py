
from __future__ import annotations

import gc
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

from ..common.config import Config

LOGGER = logging.getLogger(__name__)

__all__ = [
    "CarlaUnavailable",
    "CarlaServer",
    "SimulatorSession",
    "session_from_config",
    "connect_with_retry",
    "ensure_map",
    "find_carla_root",
    "map_basename",
    "import_carla",
    "query_nvidia_gpus",
    "select_gpu",
]


class CarlaUnavailable(RuntimeError):
    pass


def query_nvidia_gpus() -> List[Dict[str, Any]]:
    command = ["nvidia-smi", "--query-gpu=index,name,memory.total,memory.used,memory.free,utilization.gpu",
               "--format=csv,noheader,nounits"]
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, text=True)
    except (OSError, subprocess.CalledProcessError):
        LOGGER.warning("nvidia-smi unavailable; CARLA GPU selection will use its default adapter")
        return []
    result: List[Dict[str, Any]] = []
    for line in output.splitlines():
        fields = [part.strip() for part in line.split(",")]
        if len(fields) != 6:
            continue
        try:
            result.append({"index": int(fields[0]), "name": fields[1],
                           "memory_total_mib": int(float(fields[2])), "memory_used_mib": int(float(fields[3])),
                           "memory_free_mib": int(float(fields[4])), "utilization_pct": float(fields[5])})
        except ValueError:
            LOGGER.warning("could not parse nvidia-smi row: %s", line)
    return result


def select_gpu(config: Union[str, int, None] = "auto", gpus: Optional[List[Dict[str, Any]]] = None) -> Optional[int]:
    if config is None or str(config).strip().lower() in {"", "none", "null", "off"}:
        return None
    if isinstance(config, int) or str(config).strip().lstrip("-").isdigit():
        return int(config)
    if str(config).strip().lower() != "auto":
        raise ValueError("simulation.gpu must be auto, an integer adapter index, or null")
    candidates = query_nvidia_gpus() if gpus is None else list(gpus)
    if not candidates:
        return None
    chosen = max(candidates, key=lambda gpu: (gpu.get("memory_free_mib", -1),
                                               -gpu.get("utilization_pct", 100000),
                                               -gpu.get("index", 0)))
    return int(chosen["index"])


def import_carla() -> Any:
    try:
        import carla

        return carla
    except ImportError as exc:
        raise CarlaUnavailable(
            "the CARLA Python API is not importable. Install the wheel shipped "
            "with your simulator, e.g.\n"
            "  pip install <CARLA>/PythonAPI/carla/dist/carla-0.9.15-cp38-cp38-win_amd64.whl\n"
            "See README.md (Installation). Original error: {0}".format(exc)
        )


def map_basename(name: str) -> str:
    return str(name).replace("\\", "/").rstrip("/").split("/")[-1]



from ..common.installation import _DEFAULT_ROOT_CANDIDATES, _server_executable, find_carla_root


DEFAULT_PORT = 3000


def connect_with_retry(
    host: str = "127.0.0.1",
    port: int = DEFAULT_PORT,
    timeout_s: float = 60.0,
    attempts: int = 40,
    retry_delay_s: float = 3.0,
    probe_timeout_s: float = 10.0,
) -> Any:
    carla = import_carla()
    last_error: Optional[BaseException] = None
    for attempt in range(int(attempts)):
        try:
            client = carla.Client(host, int(port))
            client.set_timeout(float(probe_timeout_s))
            server_version = client.get_server_version()
            client_version = client.get_client_version()
            if map_basename(server_version) != map_basename(client_version):
                LOGGER.warning(
                    "CARLA version mismatch: server %s, client %s",
                    server_version,
                    client_version,
                )
            client.get_world().get_map().name
            client.set_timeout(float(timeout_s))
            LOGGER.info(
                "connected to CARLA %s at %s:%d after %d attempt(s)",
                server_version,
                host,
                port,
                attempt + 1,
            )
            return client
        except BaseException as exc:
            last_error = exc
            time.sleep(float(retry_delay_s))
    raise CarlaUnavailable(
        "could not reach a CARLA server at {0}:{1} after {2} attempts. "
        "Start one with scripts/check_environment.py --start-server, or launch "
        "CarlaUE4 manually. Last error: {3}".format(host, port, attempts, last_error)
    )


def ensure_map(client: Any, target_map: str, settle_timeout_s: float = 60.0) -> Any:
    target = map_basename(target_map)
    world = client.get_world()
    current = map_basename(world.get_map().name)
    if current == target:
        LOGGER.info("CARLA already running %s; not reloading", target)
        return world

    LOGGER.info("switching CARLA map %s -> %s", current, target)
    previous_timeout = 120.0
    client.set_timeout(max(previous_timeout, float(settle_timeout_s) * 4.0))
    world = client.load_world(target)

    deadline = time.time() + float(settle_timeout_s)
    while time.time() < deadline:
        try:
            if map_basename(world.get_map().name) == target:
                world.get_settings()
                LOGGER.info("map %s settled", target)
                return world
        except RuntimeError:
            pass
        time.sleep(1.0)
    raise CarlaUnavailable(
        "map switch to {0!r} did not settle within {1}s; the server may have "
        "crashed. Restart it and retry.".format(target, settle_timeout_s)
    )




class CarlaServer:

    DEFAULT_QUALITY = "Epic"

    def __init__(
        self,
        root: Optional[str] = None,
        port: int = DEFAULT_PORT,
        quality: str = DEFAULT_QUALITY,
        offscreen: bool = True,
        extra_args: Optional[Sequence[str]] = None,
        gpu: Union[str, int, None] = "auto",
        unattended: bool = True,
    ) -> None:
        self.root = find_carla_root(root)
        self.port = int(port)
        self.quality = quality
        self.offscreen = bool(offscreen)
        self.unattended = bool(unattended)
        self.extra_args = list(extra_args or [])
        self.gpu = gpu
        self.selected_gpu_index: Optional[int] = None
        self.selected_gpu: Optional[Dict[str, Any]] = None
        self._gpu_resolved = False
        self._process: Optional[subprocess.Popen] = None
        self._pre_existing_pids: set = set()
        self._owned_pids: set = set()
        self.last_restart_verified: Optional[bool] = None

    @property
    def available(self) -> bool:
        return self.root is not None and _server_executable(self.root) is not None

    @property
    def executable(self) -> Optional[Path]:
        return _server_executable(self.root) if self.root else None

    def command(self) -> List[str]:
        exe = self.executable
        if exe is None:
            raise CarlaUnavailable(
                "no CARLA executable found. Set $CARLA_ROOT or "
                "simulation.carla_root in the configuration."
            )
        args = [
            str(exe),
            "-carla-server",
            "-quality-level={0}".format(self.quality),
            "-carla-rpc-port={0}".format(self.port),
            "-nosound",
        ]
        if self.offscreen:
            args.append("-RenderOffScreen")
        if self.unattended:
            args.append("-unattended")
        if not self._gpu_resolved:
            self.selected_gpu_index = select_gpu(self.gpu)
            if self.selected_gpu_index is not None:
                self.selected_gpu = next((g for g in query_nvidia_gpus() if g["index"] == self.selected_gpu_index), None)
                LOGGER.info("CARLA GPU adapter %s selected (%s)", self.selected_gpu_index,
                            self.selected_gpu or "explicit adapter request")
            elif str(self.gpu).lower() == "auto":
                LOGGER.warning("no NVIDIA adapter selected for CARLA; using Unreal default")
            self._gpu_resolved = True
        if self.selected_gpu_index is not None:
            args.append("-ini:[/Script/Engine.RendererSettings]:r.GraphicsAdapter={0}".format(self.selected_gpu_index))
        args.extend(self.extra_args)
        return args

    _SERVER_IMAGE_NAMES: Sequence[str] = (
        "CarlaUE4-Win64-Shipping.exe",
        "CarlaUE4-Linux-Shipping",
    )

    def _server_pids(self) -> List[int]:
        pids: List[int] = []
        for name in self._SERVER_IMAGE_NAMES:
            try:
                out = subprocess.check_output(
                    ["tasklist", "/FI", "IMAGENAME eq {0}".format(name), "/FO", "CSV", "/NH"],
                    stderr=subprocess.DEVNULL,
                )
            except (OSError, subprocess.CalledProcessError):
                continue
            for line in out.decode("utf-8", "replace").splitlines():
                parts = [p.strip('" ') for p in line.split('","')]
                if len(parts) >= 2 and parts[0].lower() == name.lower():
                    try:
                        pids.append(int(parts[1]))
                    except ValueError:
                        continue
        return pids

    def start(self, wait_s: float = 180.0) -> Any:
        if not self.available:
            raise CarlaUnavailable("cannot start CARLA: no installation found")
        cmd = self.command()
        LOGGER.info("starting CARLA: %s", " ".join(cmd))
        self._pre_existing_pids = set(self._server_pids())
        self._process = subprocess.Popen(
            cmd,
            cwd=str(self.root),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        client = connect_with_retry(
            port=self.port, attempts=int(wait_s // 3) + 1, retry_delay_s=3.0
        )
        self._owned_pids = set(self._server_pids()) - self._pre_existing_pids
        LOGGER.debug("simulator engine pids owned by this session: %s", sorted(self._owned_pids))
        return client

    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def stop(self, grace_s: float = 10.0) -> None:
        pids = sorted(getattr(self, "_owned_pids", set()))
        if self._process is not None and self._process.poll() is None:
            LOGGER.info("stopping CARLA launcher (pid %s)", self._process.pid)
            self._process.terminate()
            deadline = time.time() + float(grace_s)
            while time.time() < deadline and self._process.poll() is None:
                time.sleep(0.5)
            if self._process.poll() is None:
                self._process.kill()
        self._process = None

        for pid in pids:
            try:
                subprocess.call(
                    ["taskkill", "/F", "/PID", str(pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except OSError as exc:
                LOGGER.warning("could not kill simulator engine pid %s: %s", pid, exc)
        if pids:
            deadline = time.time() + float(grace_s)
            alive = set(pids)
            while time.time() < deadline and alive:
                time.sleep(0.5)
                alive = set(pids) & set(self._server_pids())
            if alive:
                LOGGER.error(
                    "simulator engine pid(s) %s survived the kill; the next run "
                    "would share its state", sorted(alive)
                )
            else:
                LOGGER.info("stopped simulator engine pid(s) %s", pids)
            time.sleep(3.0)
        self._owned_pids = set()

    FRESH_ENGINE_MAX_ELAPSED_S = 120.0

    def restart(self, wait_s: float = 180.0) -> Any:
        self.stop()
        time.sleep(3.0)
        client = self.start(wait_s=wait_s)
        self.last_restart_verified = self._verify_fresh(client)
        return client

    def _verify_fresh(self, client: Any) -> bool:
        try:
            elapsed = float(client.get_world().get_snapshot().timestamp.elapsed_seconds)
        except Exception:
            LOGGER.debug("could not read the world clock to verify the restart")
            return False
        if elapsed <= self.FRESH_ENGINE_MAX_ELAPSED_S:
            return True
        LOGGER.warning(
            "restart did not take effect: the connected engine has been running "
            "for %.0f s, so a pre-existing server is still holding port %d and "
            "this run shares its accumulated state. Stop that server before "
            "running a comparison that depends on independent runs.",
            elapsed, self.port,
        )
        return False

    def __enter__(self) -> "CarlaServer":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop()


class SimulatorSession:

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = DEFAULT_PORT,
        timeout_s: float = 60.0,
        carla_root: Optional[str] = None,
        autostart: bool = True,
        settle_timeout_s: float = 90.0,
        gpu: Union[str, int, None] = "auto",
        quality: str = CarlaServer.DEFAULT_QUALITY,
        unattended: bool = True,
    ) -> None:
        self.host = host
        self.port = int(port)
        self.timeout_s = float(timeout_s)
        self.autostart = bool(autostart)
        self.settle_timeout_s = float(settle_timeout_s)
        self.server = CarlaServer(root=carla_root, port=self.port, gpu=gpu, quality=quality, unattended=unattended)
        self._client: Optional[Any] = None
        self._switched = False
        self.restarts = 0


    def client(self) -> Any:
        if self._client is not None:
            try:
                self._client.get_server_version()
                return self._client
            except RuntimeError:
                LOGGER.warning("lost the CARLA connection; reconnecting")
                self._client = None
        try:
            self._client = connect_with_retry(
                host=self.host, port=self.port, timeout_s=self.timeout_s, attempts=4
            )
        except CarlaUnavailable:
            if not (self.autostart and self.server.available):
                raise
            LOGGER.info("no server reachable; starting one")
            self._client = self.server.start()
            self._switched = False
        return self._client

    def current_map(self) -> str:
        return map_basename(self.client().get_world().get_map().name)

    def world_for_map(self, map_name: str) -> Any:
        target = map_basename(map_name)
        client = self.client()
        current = map_basename(client.get_world().get_map().name)

        if current == target:
            return client.get_world()

        if self._switched:
            LOGGER.info(
                "restarting CARLA to reach %s (this process already switched to %s)",
                target,
                current,
            )
            if not self.server.available:
                raise CarlaUnavailable(
                    "a second map switch ({0} -> {1}) is needed but no local CARLA "
                    "installation was found to restart. Restart the simulator "
                    "manually and rerun.".format(current, target)
                )
            self._client = self.server.restart()
            self.restarts += 1
            self._switched = False
            client = self._client

        try:
            world = ensure_map(client, target, settle_timeout_s=self.settle_timeout_s)
        except CarlaUnavailable:
            if not self.server.available:
                raise
            LOGGER.warning(
                "map switch to %s failed; restarting the simulator and retrying", target
            )
            self.release_client()
            self._client = self.server.restart()
            self.restarts += 1
            world = ensure_map(
                self._client, target, settle_timeout_s=self.settle_timeout_s
            )
        self._switched = True
        return world

    def release_client(self) -> None:
        if self._client is None:
            return
        self._client = None
        gc.collect()

    def fresh_world_for_map(self, map_name: str) -> Any:
        if not self.server.available:
            LOGGER.warning(
                "no local CARLA installation to restart; falling back to the "
                "current server, so runs will NOT be independently reproducible"
            )
            return self.world_for_map(map_name)
        self.release_client()
        self._client = self.server.restart()
        self.restarts += 1
        self._switched = False
        return self.world_for_map(map_name)

    def close(self) -> None:
        self.release_client()
        self.server.stop()

    def __enter__(self) -> "SimulatorSession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def session_from_config(cfg: Config, autostart: bool = True) -> SimulatorSession:
    return SimulatorSession(
        host=cfg.get("simulation.host", "127.0.0.1"),
        port=int(cfg.get("simulation.port", DEFAULT_PORT)),
        timeout_s=float(cfg.get("simulation.timeout_s", 60.0)),
        carla_root=cfg.get("simulation.carla_root"),
        autostart=autostart,
        settle_timeout_s=float(cfg.get("simulation.map_switch_settle_s", 90.0)),
        gpu=cfg.get("simulation.gpu", "auto"),
        quality=str(cfg.get("simulation.quality_level", CarlaServer.DEFAULT_QUALITY)),
        unattended=bool(cfg.get("simulation.unattended", True)),
    )


def client_from_config(cfg: Config, autostart: bool = False) -> Any:
    host = cfg.get("simulation.host", "127.0.0.1")
    port = int(cfg.get("simulation.port", DEFAULT_PORT))
    timeout_s = float(cfg.get("simulation.timeout_s", 60.0))
    try:
        return connect_with_retry(host=host, port=port, timeout_s=timeout_s, attempts=5)
    except CarlaUnavailable:
        if not autostart:
            raise
        server = CarlaServer(root=cfg.get("simulation.carla_root"), port=port,
                             gpu=cfg.get("simulation.gpu", "auto"),
                             quality=str(cfg.get("simulation.quality_level", CarlaServer.DEFAULT_QUALITY)),
                             unattended=bool(cfg.get("simulation.unattended", True)))
        return server.start()
