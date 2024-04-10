import asyncio
from kasa import SmartPlug
# add plugs
# delete/stop plug processes


class NodeCommandHandler():
    """
    Class to Handle Plug Commands from Node
    """
    def __init__(self, plug_shared):
        self._plug_shared = plug_shared

    def _get_plug_client(self, ip_addr):
        for client in self._plug_shared.plug_clients:
            if client.get("IP", None) == ip_addr:
                return client.get("Client", None)

    async def _parse_command(self, msg):
        command = msg.get("Command", None)
        if command is None:
            return
        return await getattr(self, command)(msg)


    async def add_plug(self,msg):
        ip_addr = msg.get("IP", None)
        if ip_addr not in self._plug_shared._plug_connections["IP"]:
                self._plug_shared._plug_clients.append(
                        {
                            "IP": ip_addr,
                            "Client": SmartPlug(ip_addr),
                        }
                )
                try: 
                    self._plug_shared._plug_clients[-1]["Client"].update()
                    self._plug_shared_plug_clients[-1]["Alias"] = self._plug_shared._plug_clients[-1]["Client"].alias
                    self._plug_connections[ip_addr] = asyncio.create_task(self._plug_shared._query_plug_emeter(ip_addr))
                    #add to config file
                    #return connected status
                except:
                    del self._plug_shared._plug_clients[-1]
                    #return failed status


    async def delete_plug(self,msg):
        ip_addr = msg.get("IP", None)
        for client in self._plug_shared._plug_clients:
            if client.get("IP", None) == ip_addr:
                del client
                break
        if self._plug_shared._plug_connections.hasKey(ip_addr):
            self._plug_shared._plug_connections["IP"].cancel()
            del self._plug_shared._plug_connections["IP"]

            

            
