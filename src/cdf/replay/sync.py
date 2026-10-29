"""Two viewers shown side by side (GROUND TRUTH and RECONSTRUCTION), driven from either window.

The two viewers are linked by two UDP ports on this machine: the leader sends on ``PORT`` and listens on
``PORT + 1``, the follower the other way round (``lead_ports`` / ``follow_ports``).  Three messages cross:

* ``clock``: the instant shown on the recording clock (``t_recording``: the clock of the recordings, the
  simulator's in the canonical runs, where every recorder's clock is the simulator's), whether it plays, and its
  speed.  The leader sends one every frame; the follower maps the instant through its own clock
  (``run.replay_time_of``).  When the user plays, pauses, seeks or changes the speed in the follower's window, the
  follower sends its new clock as a numbered command (``n``); the leader applies it and echoes the number of the
  last command it applied, and the follower ignores the leader's older clocks until that echo arrives.
* ``view``: the camera after a user action in either window (C, TAB while following, mouse, free camera): its
  mode, the recorder it follows, the overview angles and zoom, the follow orbit and distance, the free camera
  pose.  The other viewer takes it as it is.
* ``quit``: ESC or a closed window ends both viewers.

Nothing about the recordings crosses: no vehicle position, no event, and no identity but the name of a recorder
both viewers replay (the followed vehicle), so neither viewer reads anything of the other's data and each keeps
its own CARLA server.
"""

from __future__ import annotations

import json
import socket
from typing import Any, Dict, List, Tuple

HOST = "127.0.0.1"
CLOCK, VIEW, QUIT = "clock", "view", "quit"
VIEW_FIELDS = ("camera", "selected", "heading", "elevation", "zoom", "orbit", "distance", "free")


def lead_ports(port: int) -> Tuple[int, int]:
    """(send, listen) of the leading viewer."""
    return int(port), int(port) + 1


def follow_ports(port: int) -> Tuple[int, int]:
    """(send, listen) of the following viewer."""
    return int(port) + 1, int(port)


def encode(t_recording: float, playing: bool, speed: float, n: int = 0) -> bytes:
    """A clock message; ``n``: the follower's command number (sent by the follower) or the last one the leader
    applied (sent by the leader)."""
    return json.dumps({"type": CLOCK, "t_recording": round(float(t_recording), 6), "playing": bool(playing),
                       "speed": float(speed), "n": int(n)}).encode("utf-8")


def encode_view(view: Dict[str, Any]) -> bytes:
    return json.dumps(dict({key: view.get(key) for key in VIEW_FIELDS}, type=VIEW)).encode("utf-8")


def encode_quit() -> bytes:
    return json.dumps({"type": QUIT}).encode("utf-8")


def decode(data: bytes) -> Dict[str, Any]:
    message = json.loads(data.decode("utf-8"))
    kind = message.get("type", CLOCK)
    if kind == CLOCK:
        return {"type": CLOCK, "t_recording": float(message["t_recording"]), "playing": bool(message["playing"]),
                "speed": float(message["speed"]), "n": int(message.get("n", 0))}
    if kind == VIEW:
        view = {key: message.get(key) for key in VIEW_FIELDS}
        view["type"] = VIEW
        return view
    if kind == QUIT:
        return {"type": QUIT}
    raise ValueError("unknown sync message " + repr(kind))


class SyncPeer:
    """One viewer's end of the link: sends to the other viewer's port, receives on its own."""

    def __init__(self, send_port: int, listen_port: int) -> None:
        self.send_port = int(send_port)
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receiver.bind((HOST, int(listen_port)))
        self.receiver.setblocking(False)
        self.port = self.receiver.getsockname()[1]

    def send(self, data: bytes) -> None:
        try:
            self.sender.sendto(data, (HOST, self.send_port))
        except OSError:
            pass  # the other viewer is not there (yet): this one is never disturbed

    def received(self) -> List[Dict[str, Any]]:
        """Every message received since the previous call, oldest first."""
        messages = []
        while True:
            try:
                data = self.receiver.recv(4096)
            except (BlockingIOError, OSError):
                return messages
            try:
                messages.append(decode(data))
            except (ValueError, KeyError, TypeError):
                continue

    def close(self) -> None:
        self.sender.close()
        self.receiver.close()


def apply_sync(clock: Any, run: Any, message: Dict[str, Any]) -> None:
    """Put a PlaybackClock on the other viewer's instant, play state and speed."""
    clock.seek_to(run.replay_time_of(message["t_recording"]))
    if message["speed"] > 0:
        clock.set_speed(message["speed"])
    clock.playing = bool(message["playing"]) and not clock.at_end
