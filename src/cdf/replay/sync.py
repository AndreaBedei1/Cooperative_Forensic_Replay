
from __future__ import annotations

import json
import socket
from typing import Any, Dict, List, Tuple

HOST = "127.0.0.1"
CLOCK, VIEW, QUIT = "clock", "view", "quit"
VIEW_FIELDS = ("camera", "selected", "heading", "elevation", "zoom", "orbit", "distance", "free")


def lead_ports(port: int) -> Tuple[int, int]:
    return int(port), int(port) + 1


def follow_ports(port: int) -> Tuple[int, int]:
    return int(port) + 1, int(port)


def encode(t_recording: float, playing: bool, speed: float, n: int = 0) -> bytes:
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
            pass

    def received(self) -> List[Dict[str, Any]]:
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
    clock.seek_to(run.replay_time_of(message["t_recording"]))
    if message["speed"] > 0:
        clock.set_speed(message["speed"])
    clock.playing = bool(message["playing"]) and not clock.at_end
