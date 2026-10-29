#!/usr/bin/env python3
"""Start the project's private CARLA 0.9.15 server (port 3000) and keep it alive until Ctrl-C.

    python scripts/start_carla.py            # port 3000, offscreen, Epic quality

Only the engine this script started is stopped on exit; a server already running elsewhere (port 2000) is
never touched."""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cdf.simulation.carla_client import CarlaServer, query_nvidia_gpus


def main() -> int:
    parser = argparse.ArgumentParser(description="Start a local CARLA 0.9.15 server")
    parser.add_argument("--carla-root", default=None)
    parser.add_argument("--port", type=int, default=3000, help="RPC port (project server: 3000)")
    parser.add_argument("--quality", default=CarlaServer.DEFAULT_QUALITY, help="Epic (default) or Low")
    parser.add_argument("--attended", action="store_true", help="show UE4 dialogs (e.g. on a crash)")
    parser.add_argument("--gpu", default="auto", help="auto, adapter index, or none")
    parser.add_argument("--no-offscreen", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    gpu = None if str(args.gpu).lower() in {"none", "null", "off"} else args.gpu
    server = CarlaServer(root=args.carla_root, port=args.port, quality=args.quality,
                         offscreen=not args.no_offscreen, gpu=gpu, unattended=not args.attended)
    client = server.start()
    print("CARLA client/server:", client.get_server_version())
    print("CARLA PID(s):", server._server_pids())
    print("GPU query:", query_nvidia_gpus())
    print("Launch command:", " ".join(server.command()))
    try:
        while server._server_pids() or server.is_running():
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
