import json
import threading
import time

import websocket
from pymitter import EventEmitter
from websocket._exceptions import WebSocketConnectionClosedException


class CloudVariable:
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value


class CloudSession:
    def __init__(self, session, project_id):
        self.emitter = EventEmitter()
        self.session = session
        self.connect(project_id)

    def connect(self, project_id):
        self.project_id = project_id
        self.cloudvariables = []
        self._last = time.time()
        self._ws = websocket.WebSocket(enable_multithread=True)
        self._ws.connect(
            "wss://clouddata.scratch.mit.edu",
            cookie=f"scratchsessionsid={self.session.session_id};",
            origin="https://scratch.mit.edu",
            subprotocols=["binary", "base64"]
        )
        self._ws.send(json.dumps({
            "method": "handshake",
            "user": self.session.username,
            "project_id": str(project_id),
        }) + "\n")
        self.emitter.emit("connected")
        response = self._ws.recv()
        response = json.loads("[" + response.replace("\n", ",\n")[:-2] + "]")
        for variable in response:
            self.cloudvariables.append(
                CloudVariable(variable["name"][2:], variable["value"])
            )
        thread = threading.Thread(target=self._loop)
        thread.start()

    def _get_name(self, name):
        if name.startswith("☁ "):
            return name[2:]
        else:
            return name

    def _send_packet(self, packet):
        self._ws.send(json.dumps(packet) + "\n")

    def set_cloud_variable(self, name, value):
        if time.time() - self._last > 0.1:
            if not str(value).isdigit():
                raise ValueError("Cloud variables can only contain numbers")
            if len(str(value)) > 256:
                raise ValueError("Value length can't be higher than 256")
            try:
                packet = {
                    "method": "set",
                    "name": "☁ " + self._get_name(name),
                    "value": str(value),
                    "user": self.session.username,
                    "project_id": str(self.project_id),
                }
                self._send_packet(packet)
                self._last = time.time()
            except BrokenPipeError or WebSocketConnectionClosedException or ConnectionAbortedError:
                self.connect()
                time.sleep(0.1 - (time.time() - self._last))
                self.set_cloud_variable(name, value)
                return
        else:
            time.sleep(0.1 - (time.time() - self._last))
            self.set_cloud_variable(name, value)

    def _loop(self):
        while True:
            if self._ws.connected:
                response = json.loads(self._ws.recv())
                variable = next((x for x in self.cloudvariables if x.name == response["value"]), None)
                if variable is None:
                    variable = CloudVariable(
                        response["name"][2:],
                        response["value"]
                    )
                    self.cloudvariables.append(variable)
                else:
                    variable.value = response["value"]
                self.emitter.emit("set", variable)
            else:
                self.connect()

    def get_cloud_variable(self, name):
        var = next((x for x in self.cloudvariables if x.name == self._get_name(name)), None)
        if var is None:
            raise Exception("The variable named doesn't' exist")
        else:
            return var
