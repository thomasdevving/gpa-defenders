"""GPA Defenders - Relay server voor online multiplayer.

Start de server los met:
    python -m src.network.server

Of vanuit de game als host via GameServer().start().
"""

import json
import socket
import threading

HOST = "0.0.0.0"
PORT = 5555
MAX_PLAYERS = 2


class GameServer:
    """Lichtgewicht relay-server: stuurt berichten door tussen twee spelers."""

    def __init__(self, port: int = PORT):
        self.port = port
        self._sock: socket.socket | None = None
        self._clients: dict[socket.socket, int] = {}   # conn → player_id
        self._lock = threading.Lock()
        self.running = False

    # ── Publieke API ──────────────────────────────────────────────────────────

    def start(self) -> None:
        """Start de server in een achtergrond-thread."""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((HOST, self.port))
        self._sock.listen(MAX_PLAYERS)
        self.running = True
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def stop(self) -> None:
        self.running = False
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass

    # ── Interne logica ────────────────────────────────────────────────────────

    def _accept_loop(self) -> None:
        next_id = 1
        while self.running:
            try:
                conn, addr = self._sock.accept()
            except OSError:
                break

            with self._lock:
                if len(self._clients) >= MAX_PLAYERS:
                    conn.close()
                    continue
                player_id = next_id
                next_id += 1
                self._clients[conn] = player_id

            self._send(conn, {"type": "CONNECTED", "player_id": player_id})

            with self._lock:
                start_game = len(self._clients) == MAX_PLAYERS
            if start_game:
                self._broadcast({"type": "GAME_START"})

            threading.Thread(target=self._client_loop,
                             args=(conn,), daemon=True).start()

    def _client_loop(self, conn: socket.socket) -> None:
        buf = b""
        while self.running:
            try:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    msg = json.loads(line)
                    self._broadcast(msg, exclude=conn)
            except (OSError, json.JSONDecodeError):
                break

        with self._lock:
            pid = self._clients.pop(conn, None)
        try:
            conn.close()
        except OSError:
            pass
        if pid:
            self._broadcast({"type": "PLAYER_LEFT", "player_id": pid})

    def _send(self, conn: socket.socket, msg: dict) -> None:
        try:
            conn.sendall(json.dumps(msg).encode() + b"\n")
        except OSError:
            pass

    def _broadcast(self, msg: dict, exclude: socket.socket | None = None) -> None:
        with self._lock:
            targets = list(self._clients.keys())
        for conn in targets:
            if conn is not exclude:
                self._send(conn, msg)


def get_local_ip() -> str:
    """Geeft het lokale IP-adres dat bereikbaar is op het netwerk."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


if __name__ == "__main__":
    server = GameServer()
    server.start()
    print(f"[Server] Gestart op {get_local_ip()}:{PORT}")
    print("[Server] Wacht op spelers... (Ctrl+C om te stoppen)")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        server.stop()
        print("[Server] Gestopt.")
