import asyncio
import json
import sys
import yaml
from datetime import datetime
from kasa import exceptions

# from websocket import WebSocketApp #websocket-client libary -wouldnt work
# import websocket
import websockets
import pymongo
from kasa import SmartPlug

from server_handler import PlugCommandHandler
from plug_shared import SharedPlugs
from node_server_handler import NodeCommandHandler


class APServer:
    def __init__(self, config_path=None, ip_addr="127.0.0.1"):
        self._reg_plugs = []

        self._plug_shared = SharedPlugs()

        self._server_connection = {}

        self._node_server_connection = {}

        self._table_client = None

        self._AP_connection_ip = ip_addr

        self._EMS_connection_ip = ip_addr

        self._access_point_name = "NIRE_KASA_CC_1"

        if config_path:
            self.config_path = config_path
        else:
            raise Exception("Config File Not Found.")

        self._load_config()

        self._handler = PlugCommandHandler(self._plug_shared)

        self._node_handler = NodeCommandHandler(self._plug_shared)


    def _load_config(self):
        configFile = {}

        with open(self.config_path, "r", encoding="utf-8") as config:
            configFile = yaml.safe_load(config)
            self._reg_plugs = configFile.get("smartPlugs", None)
            self._AP_connection_ip = configFile.get("APConnectionIP")[0]["IP"]
            self._EMS_connection_ip = configFile.get(
                "EMSConnectionIP", None
            )[0]["IP"]
            
        if self._reg_plugs is None:
            raise Exception("Config File is Empty.")

        if self._EMS_connection_ip is None:
            raise Exception("IP not defined in Config File")

        for plug in self._reg_plugs:
            self._plug_shared.plug_clients.append(
                {
                    "IP": plug.get("IP", None),
                    "Alias": plug.get("Alias", None),
                    "Client": SmartPlug(plug.get("IP", None)),
                    "MacAddress": None,
                    "Active": None,
                    "Connected": None
                }
            )

    def _get_plug_client(self, ip_addr):
        for client in self._plug_shared.plug_clients:
            if client.get("IP", None) == ip_addr:
                return client.get("Client", None)

    def _init_mongodb_client(self):
        # connection parameters
        MONGO_HOST = self._EMS_connection_ip
        MONGO_PORT = "27017"
        MONGO_USER = "admin"
        MONGO_PASS = "dbAdmin$"
        uri = "mongodb://{}:{}@{}:{}/?authSource=admin&authMechanism=DEFAULT".format(MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT)

        #initiate connection
        self._plug_shared._mongoDB_client = pymongo.MongoClient(uri)

        #database references
        self._plug_shared._mongoDB_plugs_db = self._plug_shared._mongoDB_client["Plugs"]
        self._plug_shared._mongoDB_access_db = self._plug_shared._mongoDB_client["AccessPoints"]
        self._plug_shared._mongoDB_access_col = self._plug_shared._mongoDB_access_db[self._access_point_name]
        doc = self._plug_shared._mongoDB_access_col.find({"MAC Address": self._plug_shared._MAC_Address}).limit(1)

        if len(list(doc)) == 0: #doesnt exist in database
            #insert
            self._plug_shared._mongoDB_access_col.insert_one(
                {
                "Access Point": "True",
                "MAC Address": self._plug_shared._MAC_Address,
                "Name": self._access_point_name,
                "ip": self._AP_connection_ip,
                }
            )
        else:
            #update
            self._plug_shared._mongoDB_access_col.update_one({"MAC Address": self._plug_shared._MAC_Address}, 
                {'$set': 
                    {
                    "Access Point": "True",
                    "MAC Address": self._plug_shared._MAC_Address,
                    "Name": self._access_point_name,
                    "ip": self._AP_connection_ip,
                    }
                }
            )

    def _init_tasks(self):
        #create server for cli module
        self._server_connection["ServerSocket"] = asyncio.create_task(
            self._create_server_socket(handler=self._cli_handle, port=5555)
        )
        # self._node_server_connection["ServerSocket"] = asyncio.create_task(
        #         self._create_webserver_server(handler=self._node_handle, port=5556)
        # )

    async def _store_plug_data_tasks(self):
        #iterate over plugs
        for plug in self._plug_shared.plug_clients.copy():
            #get object reference for smartplug object
            client = self._plug_shared._get_plug_client(ip_addr=plug["IP"])
            #call plug update to receive latest data
            await client.update()
            #update object fields based on latest data
            plug["MacAddress"] = client.mac
            plug["Active"] = client.is_on
            plug["Alias"] = client.alias

        #define access collection reference
        access_col = self._plug_shared._mongoDB_access_db[self._access_point_name]

        #iterate over plugs
        for plug in self._plug_shared.plug_clients:
            #get the plugs collection reference in plugs db
            plug_col = self._plug_shared._mongoDB_plugs_db[plug["MacAddress"]]

            #create an index to put a Time to Live on all documents in that collection, set to 1 year
            plug_col.create_index("createdAt", expireAfterSeconds = 31536000)

            #create a task for plug emeter querying and add it to plug_connections dict
            self._plug_shared.plug_connections[plug.get("IP")] = asyncio.create_task(
                self._plug_shared.query_plug_emeter(plug=plug["Client"], plug_col=plug_col, access_col=access_col, ip=plug["IP"])
            )
            
            doc = access_col.find({"MAC Address": plug["MacAddress"]})
            if len(list(doc)) == 0:
                #insert
                access_col.insert_one(
                    {
                    "MAC Address": plug["MacAddress"],
                    "Name": plug["Alias"],
                    "Active": plug["Active"],
                    "Entry Time": datetime.utcnow(),
                    "Connected": True,
                    "IP": plug["IP"]
                    }
                )
            else:
                #update
                access_col.update_one({"MAC Address": plug["MacAddress"]}, 
                    {'$set': 
                        {
                        "MAC Address": plug["MacAddress"],
                        "Name": plug["Alias"],
                        "Active": plug["Active"],
                        "Entry Time": datetime.utcnow(),
                        "Connected": True,
                        "IP": plug["IP"],
                        "lastPower": 0
                        }
                    }
                )

        while True:
            try:
                #run all plug tasks
                tasks = self._plug_shared.plug_connections.values()
                #await all plug tasks completion
                await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
            except Exception:
                pass

    async def _cli_handle(self, reader, writer):
        try:
            data = await reader.read(200)
            message = json.loads(data.decode())

            response = await self._handler.parse_command(message)

            writer.write(json.dumps(response).encode())
            await writer.drain()

            writer.close()
        except:
            print('error')
            pass

    async def _node_handle(self, req):
        data = await req.read(200)
        message = json.loads(data.decode())

        response = await self._node_handler._parse_command(message)
        return response

    async def _create_server_socket(self, handler, port):
        server = await asyncio.start_server(handler, self._AP_connection_ip, port)

        addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
        print(f"Serving on {addrs}")

        async with server:
            await server.serve_forever()
    
    # async def _create_webserver_server(self, handler, port):
        
    #     async with websockets.serve(handler, "", port):
    #         print(f"Websocket Server serving on port: {port}")
    #         await asyncio.Future()  # run forever

    # async def websocketHandler(self, websocket, path):
    #     # Example data = { 
    #       # "PlugIPAddress" : "IP-string",
    #       # "message": "turnOff" OR "turnOn"  
    #     # }
    #     async for message in websocket:
    #         data = json.dumps(message)
    #         # plug = SmartPlug(data["PlugIPAddress"])
    #         plug = self._plug_shared.plug_clients.get([data["PlugIPAddress"], None])
    #         if message == "turnOff":
    #             plug.turn_off()
    #         elif message == "turnOn":
    #             plug.turn_on()
    #         await asyncio.sleep(10)

    async def run(self):
        self._init_mongodb_client()
        self._init_tasks()
        await self._store_plug_data_tasks()
        await self._server_connection["ServerSocket"]
        await self._node_server_connection["ServerSocket"]
        # await self.runWebSocket()

    # async def runWebSocket(self):
    #     # start_server = websockets.serve(self.websocketHandler, "", 8888)
    #     start_server = websockets.serve(self._cli_handle, "", 8888)
    #     async with start_server:
    #         await asyncio.Future()



if __name__ == "__main__":
    ems = APServer(config_path="config.yml", ip_addr="192.168.68.125")
    try:
        asyncio.run(ems.run())
    except KeyboardInterrupt:
        sys.exit(1)
