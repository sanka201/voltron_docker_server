import asyncio
import logging
import datetime
import uuid
from kasa import exceptions

class SharedPlugs():
    """
    Class to create clients to plugs.
    """
    def __init__(self):
        self._logger = logging.Logger("PlugConnection")
        self.plug_clients = []
        self.plug_connections = {}
        self._plug_task_time = 2
                
        self._mongoDB_client = None

        self._mongoDB_plugs_db = None

        self._mongoDB_access_db = None

        self._mongoDB_access_col = None

        self._MAC_Address = self._get_MAC_address()


    def _get_MAC_address(self):
        string = (':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
        for ele in range(0,8*6,8)][::-1]))
        return string

    def _get_plug_client(self, ip_addr):
        for client in self.plug_clients:
            if client.get("IP", None) == ip_addr:
                return client.get("Client", None)

    async def query_plug_emeter(self, plug, plug_col, access_col, ip):
        try:
            # plug_client = self._get_plug_client(ip_addr=plug_address)
            try:
                await plug.update()
            except exceptions.SmartDeviceException:
                self._logger.info(f"Failed to connect to {ip}")
                access_col.update_one({"MAC Address": plug.mac},
                    { "$set": 
                        {
                        "Connected": False
                        }
                    }
                )
                # continue trying to connect
                self.plug_connections[ip] = asyncio.create_task(self.query_plug_emeter(plug=plug, plug_col=plug_col, access_col=access_col, ip=ip))
                return
                
            time = datetime.datetime.utcnow()
            plug_col.insert_one( {
                "createdAt": time,
                'current': plug.emeter_realtime.current,
                'voltage': plug.emeter_realtime.voltage,
                'power': plug.emeter_realtime.power,
                'total': plug.emeter_realtime.total,
                'today': plug.emeter_today,
                'this_month': plug.emeter_this_month,
            }
            )
            access_col.update_one({"MAC Address": plug.mac},
                { "$set": 
                    {
                    "Active": plug.is_on,
                    "Entry Time": time
                    }
                }
            )
            await asyncio.sleep(self._plug_task_time)
            self.plug_connections[ip] = asyncio.create_task(self.query_plug_emeter(plug=plug, plug_col=plug_col, access_col=access_col, ip=ip))
        except Exception:
            self._logger.info(f"Failed to connect to {ip}")
            access_col.update_one({"MAC Address": plug.mac},
                { "$set": 
                    {
                    "Connected": False
                    }
                }
            )
            # continue trying to connect
            self.plug_connections[ip] = asyncio.create_task(self.query_plug_emeter(plug=plug, plug_col=plug_col, access_col=access_col, ip=ip))


