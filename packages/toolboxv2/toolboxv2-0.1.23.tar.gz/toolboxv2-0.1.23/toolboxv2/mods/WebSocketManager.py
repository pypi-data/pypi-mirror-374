import asyncio
import json
import logging
import math
import os.path
import queue
import threading
import time

import websockets
from fastapi import HTTPException, WebSocket
from websockets import serve
from websockets.sync.client import connect

from toolboxv2 import FileHandler, MainTool, Result, Style, get_app
from toolboxv2.utils.system.types import ApiOb


async def valid_id(ws_id, id_v, websocket=None):
    if ws_id is None or id_v is None:
        raise HTTPException(status_code=403, detail="Access forbidden invalid id")
    if not ws_id.startswith(id_v):
        if websocket is not None:
            await websocket.close()
        raise HTTPException(status_code=403, detail="Access forbidden invalid id")

    return ws_id


class Tools(MainTool, FileHandler):

    def __init__(self, app=None):
        self.version = "0.0.3"
        self.name = "WebSocketManager"
        self.logger: logging.Logger or None = app.logger if app else None
        if app is None:
            app = get_app()

        self.color = "BLUE"
        self.active_connections: dict = {}
        self.active_connections_client: dict = {}
        self.app_id = get_app().id
        self.keys = {
            "tools": "v-tools~~~"
        }
        self.tools = {
            "all": [["Version", "Shows current Version"],
                    ["connect", "connect to a socket async (Server side)"],
                    ["disconnect", "disconnect a socket async (Server side)"],
                    ["send_message", "send_message to a socket group"],
                    ["list", "list all instances"],
                    ["srqw", "Gent an WebSocket with url and ws_id", math.inf, 'srqw_wrapper'],
                    ["construct_render", "construct_render"],
                    ],
            "name": "WebSocketManager",
            "Version": self.show_version,
            "connect": self.connect,
            "get_pools_manager": self.get_pools_manager,
            "disconnect": self.disconnect,
            "send_message": self.send_message,
            "list": self.list_instances,
            "get": self.get_instances,
            "srqw": self.srqw_wrapper,
            "construct_render": self.construct_render,
        }

        self.validated_instances = {

        }
        self.server_actions = {}
        self._get_pools_manager = None
        FileHandler.__init__(self, "WebSocketManager.config", app.id if app else __name__, keys=self.keys, defaults={})
        MainTool.__init__(self, load=self.on_start, v=self.version, tool=self.tools,
                          name=self.name, logs=self.logger, color=self.color, on_exit=self.on_exit)

    def on_start(self):
        self.logger.info("Starting WebSocketManager")
        self.load_file_handler()
        pass

    def on_exit(self):
        self.logger.info("Closing WebSocketManager")
        self.save_file_handler()
        for key in list(self.active_connections_client.keys()):
            self.close_websocket(key)

    def vtID(self, uid):
        vt_id = uid + 'VTInstance'
        # app . key generator
        # app . hash pepper and Salting
        # app . key generator
        self.print(f"APP:{self.app.id} generated from VTInstance:")
        return vt_id

    def show_version(self):
        self.print("Version: ", self.version)
        return self.version

    def get_instances(self, name):
        if name not in self.active_connections:
            self.print(Style.RED("Pleas Create an instance before calling it!"))
            return None
        return self.active_connections[name]

    def list_instances(self):
        for name, instance in self.active_connections.items():
            self.print(f"{name}: {instance.name}")

    def srqw_wrapper(self, url, websocket_id):

        s, r = self.get_sender_receiver_que_ws(url, websocket_id)

        return s, r

    def get_sender_receiver_que_ws(self, url, websocket_id):

        if not (url and websocket_id):
            return "Invalid Inputs", None

        self.print(Style.WHITE("Starting WebSocket Builder"))

        send_queue = queue.Queue()
        recv_queue = queue.Queue()
        loop = asyncio.new_event_loop()

        async def send(ws):
            t0 = time.perf_counter()
            running = True
            while running:
                msg = await loop.run_in_executor(None, send_queue.get)
                msg_json = msg
                if isinstance(msg, dict):
                    msg_json = json.dumps(msg)
                if isinstance(msg, list):
                    msg_json = str(msg)
                self.print(Style.GREY("Sending Data"))
                if msg_json == "exit":
                    running = False
                await ws.send(msg_json)
                self.print(Style.GREY("-- Sendet --"))

                self.print(f"S Parsed Time ; {t0 - time.perf_counter()}")
                if t0 - time.perf_counter() > (60 * 60) * 1:
                    ws.close()

            print("SENDER received exit stop running")

        async def receive(ws):
            t0 = time.perf_counter()
            running = True
            while running:
                msg_json = await ws.recv()
                self.print(Style.GREY("-- received --"))
                print(msg_json)
                if msg_json == "exit":
                    running = False
                msg = json.loads(msg_json)
                recv_queue.put(msg)

                self.print(f"R Parsed Time ; {t0 - time.perf_counter()}")
                if t0 - time.perf_counter() > (60 * 60) * 1:
                    ws.close()

            print("receiver received exit call")

        async def websocket_handler():

            with self.create_websocket(websocket_id, url) as websocket:
                send_task = asyncio.create_task(send(websocket))
                recv_task = asyncio.create_task(receive(websocket))
                try:
                    await asyncio.gather(send_task, recv_task)
                except Exception as e:
                    self.logger.error(f"Error in Client WS : {e}")
                except websockets.exceptions.ConnectionClosedOK:
                    return True
                finally:
                    self.close_websocket(websocket_id)

            return True

        def websocket_thread():
            asyncio.set_event_loop(loop)
            # websocket_handler()
            # loop.run_forever()
            # loop.run_in_executor(None, websocket_handler)
            loop.run_until_complete(websocket_handler())

        ws_thread = threading.Thread(target=websocket_thread, daemon=True)
        ws_thread.start()

        return send_queue, recv_queue

    def create_websocket(self, websocket_id: str, url: str = 'wss://0.0.0.0:5000/ws'):  # wss:
        if websocket_id is None:
            return
        uri = f"{url}/{websocket_id}"
        self.logger.info(f"Crating websocket to {url}")
        websocket = connect(uri)
        if websocket:
            self.print(f"Connection to {url} established")
            self.active_connections_client[websocket_id] = websocket
        return websocket

    def close_websocket(self, websocket_id):
        self.print("close_websocket called")
        if websocket_id not in self.active_connections_client:
            self.print("websocket not found")
        self.active_connections_client[websocket_id].close()
        del self.active_connections_client[websocket_id]

    async def connect(self, websocket: WebSocket, websocket_id):
        if websocket is None or websocket_id is None:
            return "websocket not set"
        websocket_id_sto = await valid_id(websocket_id, self.app_id, websocket)

        data = self.app.run_any("cloudM", "validate_ws_id", [websocket_id])
        valid, key = False, ''
        if isinstance(data, list | tuple):
            if len(data) == 2:
                valid, key = data
            else:
                self.logger.error(f"list error connect {data}")
                return False
        else:
            self.logger.error(f"isinstance error connect {data}, {type(data)}")
            return False

        if valid:
            self.validated_instances[websocket_id_sto] = key

        if websocket_id_sto in self.active_connections:
            print(f"Active connection - added nums {len(self.active_connections[websocket_id_sto])}")
            await self.send_message(json.dumps({"res": f"New connection : {websocket_id}"}), websocket, websocket_id)
            self.active_connections[websocket_id_sto].append(websocket)
        else:
            self.active_connections[websocket_id_sto] = [websocket]
        await websocket.accept()
        return True

    async def disconnect(self, websocket: WebSocket, websocket_id):
        if websocket is None or websocket_id is None:
            return "websocket not set"
        websocket_id_sto = await valid_id(websocket_id, self.app_id)
        await self.send_message(json.dumps({"res": f"Closing connection : {websocket_id}"}), websocket, websocket_id)
        self.active_connections[websocket_id_sto].remove(websocket)
        if len(self.active_connections[websocket_id_sto]) == 0:
            del self.active_connections[websocket_id_sto]
        await websocket.close()

    async def send_message(self, message: str, websocket: WebSocket or None, websocket_id):
        if websocket is None or websocket_id is None:
            return "websocket not set"
        websocket_id_sto = await valid_id(websocket_id, self.app_id)
        for connection in self.active_connections[websocket_id_sto]:
            if connection != websocket:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    self.logger.error(f"{Style.YELLOW('Error')} Connection in {websocket_id} lost to {connection}")
                    self.logger.error(str(e))
                    self.print(f"{Style.YELLOW('Error')} Connection in {websocket_id} lost to {connection}")
                    self.active_connections[websocket_id_sto].remove(connection)

    def add_server_action(self, action_name, function=None):

        if function is None:
            def function(x):
                return str(x)

        if action_name in self.server_actions:
            return f"Server Action {action_name} already exists"

        self.server_actions[action_name] = function

    async def manage_data_flow(self, websocket, websocket_id, data):
        self.logger.info(f"Managing data flow: data {data}")
        if websocket is None or websocket_id is None:
            return "websocket not set"
        websocket_id_sto = await valid_id(websocket_id, self.app_id)

        if websocket_id_sto not in self.active_connections:
            return '{"res": "No websocket connection pleas Log in"}'

        if websocket_id_sto not in self.validated_instances:
            content = self.construct_render(content="""<p id="infoText" color: style="color:var(--error-color);">Pleas Log in
            </p>
            """, element_id="infoText")
            return content

        si_id = self.validated_instances[websocket_id_sto]

        data_type = "Noice"
        try:
            data = json.loads(data)
            data_type = "dict"
        except ValueError as e:
            self.logger.error(Style.YELLOW(f"ValueError json.loads data : {e}"))
            if websocket_id_sto in data:
                data_type = "str"

        self.logger.info(f"type: {data_type}:{type(data)}")

        if data_type == "Noice":
            return

        if data_type == "dict" and isinstance(data, dict):
            keys = list(data.keys())
            if "ServerAction" in keys:
                action = data["ServerAction"]

                if action == "logOut":
                    user_instance = self.app.run_any("cloudM", "wsGetI", [si_id])
                    if user_instance is None or not user_instance:
                        return '{"res": "No User Instance Found"}'

                    if data['data']['token'] == "**SelfAuth**":
                        data['data']['token'] = user_instance['token']

                    api_data = ApiOb()
                    api_data.data = data['data']['data']
                    api_data.token = data['data']['token']
                    command = [api_data, data['command'].split('|')]

                    self.app.run_any("cloudM", "api_log_out_user", command)
                    websocket_id_sto = await valid_id(websocket_id, self.app_id)
                    for websocket_ in self.active_connections[websocket_id_sto]:
                        if websocket == websocket_:
                            continue
                        await self.disconnect(websocket_, websocket_id)

                    if len(self.active_connections[websocket_id_sto]) > 1:
                        await self.send_message(json.dumps({'exit': 'exit'}), websocket, websocket_id)

                    home_content = self.construct_render(content="",
                                                         element_id="main",

                                                         externals=["/web/scripts/go_home.js"])

                    await websocket.send_text(home_content)
                elif action == "getModListAll":
                    return json.dumps({'modlistA': self.app.get_all_mods()})
                elif action == "getModListInstalled":
                    user_instance = self.app.run_any("cloudM", "wsGetI", [si_id])
                    if user_instance is None or not user_instance:
                        self.logger.info("No valid user instance")
                        return '{"res": "No Mods Installed"}'

                    return json.dumps({'modlistI': user_instance['save']['mods']})
                elif action == "getModData":
                    mod_name = data["mod-name"]
                    try:
                        mod = self.app.get_mod(mod_name)
                        return {"settings": {'mod-description': mod.description}}
                    except ValueError:
                        content = self.construct_render(
                            content=f"""<p id="infoText" color: style="color:var(--error-color);">Mod {mod_name} not found
                        </p>
                        """, element_id="infoText")
                        return content
                elif action == "installMod":
                    user_instance = self.app.run_any("cloudM", "wsGetI", [si_id])
                    if user_instance is None or not user_instance:
                        self.logger.info("No valid user instance")
                        return '{"res": "No User Instance Found Pleas Log in"}'

                    if data["name"] not in user_instance['save']['mods']:
                        self.logger.info(f"Appending mod {data['name']}")
                        user_instance['save']['mods'].append(data["name"])

                    self.app.new_ac_mod("cloudM")
                    self.app.AC_MOD.hydrate_instance(user_instance)
                    self.print("Sending webInstaller")
                    installer_content = user_instance['live'][data["name"]].webInstall(user_instance,
                                                                                       self.construct_render)
                    self.app.new_ac_mod("cloudM")
                    self.app.AC_MOD.save_user_instances(user_instance)
                    await websocket.send_text(installer_content)
                elif action == "addConfig":
                    user_instance = self.app.run_any("cloudM", "wsGetI", [si_id])
                    if data["name"] in user_instance['live']:
                        user_instance['live'][data["name"]].add_str_to_config([data["key"], data["value"]])
                    else:
                        await websocket.send_text('{"res": "Mod nod installed or available"}')
                elif action == "runMod":
                    user_instance = self.app.run_any("cloudM", "wsGetI", [si_id])

                    self.print(f"{user_instance}, {data}")
                    if user_instance is None or not user_instance:
                        return '{"res": "No User Instance Found pleas log in"}'

                    if data['data']['token'] == "**SelfAuth**":
                        data['data']['token'] = user_instance['token']

                    api_data = ApiOb()
                    api_data.data = data['data']['data']
                    api_data.token = data['data']['token']
                    command = [api_data, data['command'].split('|')]

                    token_data = self.app.run_any('cloudM', "validate_jwt", command)

                    if not isinstance(token_data, dict):
                        return json.dumps({'res': 'u ar using an invalid token pleas log in again'})

                    if token_data["uid"] != user_instance['save']['uid']:
                        self.logger.critical(
                            f"{Style.RED(f'''User {user_instance['save']['username']} {Style.CYAN('Accessed')} : {Style.Bold(token_data['username'])} token both log aut.''')}")
                        self.app.run_any('cloudM', "close_user_instance", token_data["uid"])
                        self.app.run_any('cloudM', "close_user_instance", user_instance['save']['uid'])
                        return json.dumps({'res': "The server registered: you are"
                                                  " trying to register with an not fitting token "})

                    if data['name'] not in user_instance['save']['mods']:
                        user_instance['save']['mods'].append(data['name'])

                    if data['name'] not in user_instance['live']:
                        self.logger.info(f"'Crating live module:{data['name']}'")
                        self.app.new_ac_mod("cloudM")
                        self.app.AC_MOD.hydrate_instance(user_instance)
                        self.app.new_ac_mod("cloudM")
                        self.app.AC_MOD.save_user_instances(user_instance)

                    try:
                        self.app.new_ac_mod("VirtualizationTool")
                        if self.app.run_function('set-ac', user_instance['live']['v-' + data['name']]):
                            res = self.app.run_function('api_' + data['function'], command)
                        else:
                            res = "Mod Not Found 404"
                    except Exception as e:
                        res = "Mod Error " + str(e)

                    if type(res) == str:
                        if (res.startswith('{') or res.startswith('[')) or res.startswith('"[') or res.startswith('"{') \
                            or res.startswith('\"[') or res.startswith('\"{') or res.startswith(
                            'b"[') or res.startswith('b"{'): \
                            res = eval(res)
                    if not isinstance(res, dict):
                        res = {"res": res, data['name']: True}
                    await websocket.send_text(json.dumps(res))
                else:
                    function_action = self.server_actions.get(action)

                    if function_action is None:
                        return json.dumps(Result.default_internal_error(f"ServerAction {action} is not available"))

                    res = function_action(data)

                    if not isinstance(res, str):
                        res = str(res)
                    await websocket.send_text(res)
                    return res
            if "ValidateSelf" in keys:
                user_instance = self.app.run_any("cloudM", "wsGetI", [si_id])
                if user_instance is None or not user_instance:
                    self.logger.info("No valid user instance")
                    return json.dumps({"res": "No User Instance Found Pleas Log in", "valid": False})
                return json.dumps({"res": "User Instance is valid", "valid": True})
            if "ChairData" in keys:
                user_instance = self.app.run_any("cloudM", "wsGetI", [si_id])
                if user_instance is None or not user_instance:
                    self.logger.info("No valid user instance")
                    return json.dumps({"res": "No User Instance Found Pleas Log in", "valid": False})
                if len(self.active_connections[websocket_id_sto]) < 1:
                    return json.dumps({"res": "No other connections found", "valid": True})
                await self.send_message(json.dumps(data['data']), websocket, websocket_id)
                return json.dumps({"res": "Data Send", "valid": True})

        if data_type == "str":
            await self.send_message(data, websocket, websocket_id)

    async def start_server(self, host="localhost", port=8765, non_block=False):
        async def handle_websocket(websocket):
            websocket_id = await websocket.recv()
            self.active_connections[websocket_id] = websocket
            async for message in websocket:
                response = await self.manage_data_flow(websocket, websocket_id, message)
                if response:
                    await websocket.send(response)
        async with serve(handle_websocket, host, port):
            self.print(f"{self.name} Service Online.")
            if non_block:
                return
            await asyncio.Future()  # Run forever

    def construct_render(self, content: str, element_id: str, externals: list[str] or None = None,
                         placeholder_content: str or None = None, from_file=False, to_str=True):

        if externals is None:
            externals = []
        if element_id is None:
            element_id = ""

        if placeholder_content is None:
            placeholder_content = "<h1>Loading...</h1>"

        if from_file:
            if os.path.exists(content):
                with open(content) as f:
                    self.logger.info(f"File read from {content}")
                    content = f.read()
            else:
                self.print(f"{Style.RED('Could not find file ')}to create renderer {from_file}")

        render_data = {
            "render": {
                "content": content,
                "place": '#' + element_id,
                "id": element_id,
                "externals": externals,
                "placeholderContent": placeholder_content
            }
        }

        self.logger.info(f"render content :  {render_data}")

        if to_str:
            return json.dumps(render_data)
        return render_data

    def get_pools_manager(self):
        if self._get_pools_manager is None:
            self._get_pools_manager = WebSocketPoolManager()
        return self._get_pools_manager

from collections.abc import Callable
from typing import Any


class WebSocketPoolManager:
    def __init__(self):
        self.pools: dict[str, dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)

    async def create_pool(self, pool_id: str) -> None:
        """Create a new WebSocket pool."""
        if pool_id not in self.pools:
            self.pools[pool_id] = {
                'connections': {},
                'actions': {},
                'global_actions': {}
            }
            self.logger.info(f"Created new pool: {pool_id}")
        else:
            self.logger.warning(f"Pool {pool_id} already exists")

    async def add_connection(self, pool_id: str, connection_id: str, websocket) -> None:
        """Add a WebSocket connection to a pool."""
        if pool_id not in self.pools:
            await self.create_pool(pool_id)

        self.pools[pool_id]['connections'][connection_id] = websocket
        self.logger.info(f"Added connection {connection_id} to pool {pool_id}")

    async def remove_connection(self, pool_id: str, connection_id: str) -> None:
        """Remove a WebSocket connection from a pool."""
        if pool_id in self.pools and connection_id in self.pools[pool_id]['connections']:
            del self.pools[pool_id]['connections'][connection_id]
            self.logger.info(f"Removed connection {connection_id} from pool {pool_id}")
        else:
            self.logger.warning(f"Connection {connection_id} not found in pool {pool_id}")

    def register_action(self, pool_id: str, action_name: str, handler: Callable,
                        connection_ids: list[str] = None) -> None:
        """Register an action for specific connections or the entire pool."""
        if pool_id not in self.pools:
            self.logger.error(f"Pool {pool_id} does not exist")
            return

        if connection_ids is None:
            self.pools[pool_id]['global_actions'][action_name] = handler
            self.logger.info(f"Registered global action {action_name} for pool {pool_id}")
        else:
            for conn_id in connection_ids:
                if conn_id not in self.pools[pool_id]['actions']:
                    self.pools[pool_id]['actions'][conn_id] = {}
                self.pools[pool_id]['actions'][conn_id][action_name] = handler
            self.logger.info(f"Registered action {action_name} for connections {connection_ids} in pool {pool_id}")

    async def handle_message(self, pool_id: str, connection_id: str, message: str) -> None:
        """Handle incoming messages and route them to the appropriate action handler."""
        if pool_id not in self.pools or connection_id not in self.pools[pool_id]['connections']:
            self.logger.error(f"Invalid pool_id or connection_id: {pool_id}, {connection_id}")
            return

        try:
            data = json.loads(message)
            action = data.get('action')

            if action:
                if action in self.pools[pool_id]['global_actions']:
                    await self.pools[pool_id]['global_actions'][action](pool_id, connection_id, data)
                elif connection_id in self.pools[pool_id]['actions'] and action in self.pools[pool_id]['actions'][
                    connection_id]:
                    await self.pools[pool_id]['actions'][connection_id][action](pool_id, connection_id, data)
                else:
                    self.logger.warning(f"No handler found for action {action} in pool {pool_id}")
            else:
                self.logger.warning(f"No action specified in message from {connection_id} in pool {pool_id}")
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON received from {connection_id} in pool {pool_id}")

    async def broadcast(self, pool_id: str, message: str, exclude_connection_id: str = None) -> None:
        """Broadcast a message to all connections in a pool, optionally excluding one connection."""
        if pool_id not in self.pools:
            self.logger.error(f"Pool {pool_id} does not exist")
            return

        for conn_id, websocket in self.pools[pool_id]['connections'].items():
            if conn_id != exclude_connection_id:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    self.logger.error(f"Error sending message to {conn_id} in pool {pool_id}: {str(e)}")

    async def send_to_connection(self, pool_id: str, connection_id: str, message: str) -> None:
        """Send a message to a specific connection in a pool."""
        if pool_id in self.pools and connection_id in self.pools[pool_id]['connections']:
            try:
                await self.pools[pool_id]['connections'][connection_id].send_text(message)
            except Exception as e:
                self.logger.error(f"Error sending message to {connection_id} in pool {pool_id}: {str(e)}")
        else:
            self.logger.error(f"Connection {connection_id} not found in pool {pool_id}")

    def get_pool_connections(self, pool_id: str) -> list[str]:
        """Get a list of all connection IDs in a pool."""
        if pool_id in self.pools:
            return list(self.pools[pool_id]['connections'].keys())
        else:
            self.logger.error(f"Pool {pool_id} does not exist")
            return []

    def get_all_pools(self) -> list[str]:
        """Get a list of all pool IDs."""
        return list(self.pools.keys())

    async def close_pool(self, pool_id: str) -> None:
        """Close all connections in a pool and remove the pool."""
        if pool_id in self.pools:
            for websocket in self.pools[pool_id]['connections'].values():
                await websocket.close()
            del self.pools[pool_id]
            self.logger.info(f"Closed and removed pool {pool_id}")
        else:
            self.logger.warning(f"Pool {pool_id} does not exist")

    async def close_all_pools(self) -> None:
        """Close all connections in all pools and remove all pools."""
        for pool_id in list(self.pools.keys()):
            await self.close_pool(pool_id)
        self.logger.info("Closed all pools")
