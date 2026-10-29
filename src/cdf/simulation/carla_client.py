"""Connection and process management for the CARLA simulator.

This module exists because a bare ``carla.Client`` is not robust enough for
repeatable scenario acquisition. Three failure modes are handled explicitly:

1. ``client.load_world(X)`` while the server is **already running map X** crashes
   the server. :func:`ensure_map` therefore switches maps only when the requested
   map differs from the current one.
2. A map switch returns before the new world is actually serviceable, so the next
   call times out. :func:`ensure_map` polls the new world until it answers
   consistently.
3. Loading a heavy map can kill the server outright. :class:`CarlaServer` can
   therefore start, stop and restart the simulator process, and
   :func:`connect_with_retry` transparently waits for a server that is still
   booting.

Passing the map on the command line was also tested and is *not* honoured by the
packaged 0.9.15 build (it boots the default map regardless), so map selection
always goes through :func:`ensure_map`.
"""

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
    """Raised when no usable CARLA server or Python API can be reached."""


def query_nvidia_gpus() -> List[Dict[str, Any]]:
    """Return free memory/utilisation for NVIDIA adapters, if nvidia-smi exists."""
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
    """Resolve ``auto`` to the most free, least utilised adapter."""
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
    """Import the ``carla`` module, with an actionable error when it is missing.

    Imported lazily so that the rest of the package (and the entire test-suite)
    works on a machine without the simulator.
    """
    try:
        import carla  # type: ignore

        return carla
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise CarlaUnavailable(
            "the CARLA Python API is not importable. Install the wheel shipped "
            "with your simulator, e.g.\n"
            "  pip install <CARLA>/PythonAPI/carla/dist/carla-0.9.15-cp38-cp38-win_amd64.whl\n"
            "See README.md (Installation). Original error: {0}".format(exc)
        )


def map_basename(name: str) -> str:
    """Reduce ``"Carla/Maps/Town05"`` (or a ``/Game/...`` path) to ``"Town05"``."""
    return str(name).replace("\\", "/").rstrip("/").split("/")[-1]


# ---------------------------------------------------------------------------
# Locating the simulator
# ---------------------------------------------------------------------------

#: Paths probed for a packaged CARLA installation when none is configured.
from ..common.installation import _DEFAULT_ROOT_CANDIDATES, _server_executable, find_carla_root  # noqa: E402,F401


DEFAULT_PORT = 3000


def connect_with_retry(
    host: str = "127.0.0.1",
    port: int = DEFAULT_PORT,
    timeout_s: float = 60.0,
    attempts: int = 40,
    retry_delay_s: float = 3.0,
    probe_timeout_s: float = 10.0,
) -> Any:
    """Connect to a CARLA server, tolerating one that is still booting.

    A short per-probe timeout is used while waiting and the caller's real timeout
    is applied once the handshake succeeds, so a cold start does not block for
    the full ``timeout_s`` on every attempt.

    The handshake alone is not readiness. ``get_server_version`` answers while
    the engine is still bringing a map up, and the caller's first ``get_map``
    then blocks for the full sixty seconds and raises -- which on the collection
    looked like a scenario that hung, retried three times and stalled the whole
    run. So the probe asks for the world as well, and a server that cannot yet
    produce one is treated as still booting rather than as connected.
    """
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
            # Readiness, not just reachability: ask for the world.
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
        except BaseException as exc:  # noqa: BLE001 - re-raised below with context
            last_error = exc
            time.sleep(float(retry_delay_s))
    raise CarlaUnavailable(
        "could not reach a CARLA server at {0}:{1} after {2} attempts. "
        "Start one with scripts/check_environment.py --start-server, or launch "
        "CarlaUE4 manually. Last error: {3}".format(host, port, attempts, last_error)
    )


def ensure_map(client: Any, target_map: str, settle_timeout_s: float = 60.0) -> Any:
    """Return a world running ``target_map``, switching maps only if necessary.

    Reloading the map the server already runs crashes the 0.9.15 build, so the
    current map is checked first. After a genuine switch the new world is polled
    until it reports the expected map *and* answers a settings query, because the
    call returns before the world is serviceable.
    """
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
            # The world is mid-swap; keep polling until the deadline.
            pass
        time.sleep(1.0)
    raise CarlaUnavailable(
        "map switch to {0!r} did not settle within {1}s; the server may have "
        "crashed. Restart it and retry.".format(target, settle_timeout_s)
    )


# ---------------------------------------------------------------------------
# Server process management
# ---------------------------------------------------------------------------


class CarlaServer:
    """Optional supervisor for a locally installed CARLA simulator process.

    The scenario runner can use this to bring a server up when none is
    running, and to restart one that died mid-suite. It never touches a server it
    did not start unless :meth:`kill_existing` is called explicitly.
    """

    #: ``Low`` is not the default: in CARLA 0.9.15 on this setup it makes the
    #: engine crash deterministically in some scenarios (a camera scene capture
    #: renders a vehicle skeletal mesh whose mesh object was already freed:
    #: EXCEPTION_ACCESS_VIOLATION in FSkeletalMeshSceneProxy::
    #: GetMeshElementsConditionallySelectable).  The same runs complete under
    #: ``Epic``, with bit-identical vehicle physics.
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
        # -unattended: an engine crash exits instead of waiting behind a modal
        # "Fatal error" dialog, so a supervisor can restart it.
        self.unattended = bool(unattended)
        self.extra_args = list(extra_args or [])
        self.gpu = gpu
        self.selected_gpu_index: Optional[int] = None
        self.selected_gpu: Optional[Dict[str, Any]] = None
        self._gpu_resolved = False
        self._process: Optional[subprocess.Popen] = None
        self._pre_existing_pids: set = set()
        self._owned_pids: set = set()
        #: Whether the most recent :meth:`restart` actually produced a fresh
        #: engine. ``None`` until one has been attempted.
        self.last_restart_verified: Optional[bool] = None

    @property
    def available(self) -> bool:
        """Whether a simulator executable was found on this machine."""
        return self.root is not None and _server_executable(self.root) is not None

    @property
    def executable(self) -> Optional[Path]:
        return _server_executable(self.root) if self.root else None

    def command(self) -> List[str]:
        """The exact command line used to launch the server."""
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

    #: Image names the packaged Windows build actually runs under. ``CarlaUE4.exe``
    #: is a thin launcher: it spawns ``CarlaUE4-Win64-Shipping.exe`` and exits, so
    #: terminating the handle returned by ``Popen`` does **not** stop the server.
    _SERVER_IMAGE_NAMES: Sequence[str] = (
        "CarlaUE4-Win64-Shipping.exe",
        "CarlaUE4-Linux-Shipping",
    )

    def _server_pids(self) -> List[int]:
        """PIDs of running simulator *engine* processes, launcher excluded."""
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
        """Launch the simulator and return a connected client.

        The engine PIDs present beforehand are recorded so that :meth:`stop` can
        kill exactly the engine this call started, and leave alone one a user
        happens to be running.
        """
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
        """Whether a server we started is still alive."""
        return self._process is not None and self._process.poll() is None

    def stop(self, grace_s: float = 10.0) -> None:
        """Terminate the simulator this session started.

        Killing the launcher is not enough. ``CarlaUE4.exe`` spawns
        ``CarlaUE4-Win64-Shipping.exe`` and exits, so terminating the ``Popen``
        handle leaves a ~2.5 GB engine process alive and still holding the RPC
        port. A collection that restarts the simulator between runs then leaks one
        engine per restart -- and, far worse, every later "fresh" server fails to
        bind the port and the client silently reconnects to the FIRST one, so the
        runs meant to be independent all share accumulated state.

        The engine processes this session started are therefore killed by pid.
        Engines that were already running when :meth:`start` was called are left
        alone.
        """
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

        # `/T` is deliberately NOT used. It walks the process tree by parent pid,
        # and the engine's recorded parent is the launcher, which exited long ago
        # and whose pid Windows is free to hand to an unrelated process -- so a
        # tree kill can reach processes that have nothing to do with the
        # simulator. The engine is killed by its own pid instead, and the kill is
        # then verified rather than assumed.
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
            # Give the OS a moment to release the RPC port, or the next start
            # races the teardown and binds nothing. A pid that is still listed
            # after the wait is reported: a surviving engine is the failure mode
            # this whole method exists to prevent, so it must never be silent.
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

    #: A freshly booted engine has been ticking for at most a few seconds. Well
    #: above that and the client is talking to something older.
    FRESH_ENGINE_MAX_ELAPSED_S = 120.0

    def restart(self, wait_s: float = 180.0) -> Any:
        """Stop (if we own the process) and start again; returns a new client.

        :meth:`stop` deliberately leaves engines that were already running when
        this session started -- killing a server somebody else is using would be
        indefensible. But that creates the failure this method must not hide: a
        pre-existing engine still holding the RPC port means the new engine
        cannot bind it, and the client reconnects to the *old* one. Every
        subsequent "fresh" run then shares accumulated state, silently, while
        every log line says the restart succeeded.

        So the restart is verified rather than assumed. A genuinely fresh engine
        has been ticking for seconds; one that has served a collection has not.
        """
        self.stop()
        time.sleep(3.0)
        client = self.start(wait_s=wait_s)
        self.last_restart_verified = self._verify_fresh(client)
        return client

    def _verify_fresh(self, client: Any) -> bool:
        """Whether the client is talking to an engine this restart started."""
        try:
            elapsed = float(client.get_world().get_snapshot().timestamp.elapsed_seconds)
        except Exception:  # noqa: BLE001 - a probe must never break the run
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
    """Guarantees a live CARLA server running a requested map.

    Map switching on the tested 0.9.15 build is only dependable **once per server
    process**: a freshly booted server switches to any map in a few seconds, but a
    second switch (or a reload of the current map) hangs or kills the simulator.
    Both failure modes were reproduced repeatedly on the reference machine.

    This class therefore tracks whether the current process has already performed
    a switch. The first switch is done in place; any later map change restarts the
    simulator process and switches again from the freshly booted default map. A
    suite that runs nine scenarios on one map and one on another consequently
    pays the restart cost exactly once.
    """

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

    # -- connection -------------------------------------------------------

    def client(self) -> Any:
        """A connected client, starting the simulator if permitted."""
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
        """Return a world running ``map_name``, restarting the server if needed."""
        target = map_basename(map_name)
        client = self.client()
        current = map_basename(client.get_world().get_map().name)

        if current == target:
            return client.get_world()

        if self._switched:
            # This process has already spent its one dependable map switch.
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
            # The switch-budget bookkeeping only knows about switches THIS session
            # performed. A server left on some other map by an earlier process
            # has already spent its budget, and we cannot tell from the outside.
            # So a failed switch falls back to the same remedy as a known-spent
            # budget: restart the process and switch from the boot map.
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
        """Drop the client bound to the current server and collect it.

        Dropping the last reference and forcing a collection lets the CARLA
        client release its background streaming resources before a restart.
        """
        if self._client is None:
            return
        self._client = None
        gc.collect()

    def fresh_world_for_map(self, map_name: str) -> Any:
        """Restart the simulator, then return a world running ``map_name``.
        """
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
        """Stop a server this session started."""
        self.release_client()
        self.server.stop()

    def __enter__(self) -> "SimulatorSession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        # Only a server we started ourselves is stopped; an externally managed
        # simulator is left exactly as we found it.
        self.close()


def session_from_config(cfg: Config, autostart: bool = True) -> SimulatorSession:
    """Build a :class:`SimulatorSession` from the ``simulation`` config section."""
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
    """Connect using the ``simulation`` section of a resolved configuration."""
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
