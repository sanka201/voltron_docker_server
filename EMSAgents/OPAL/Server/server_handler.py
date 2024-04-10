import asyncio
from kasa import SmartPlug
from datetime import datetime
import yaml
from kasa import exceptions
from pymongo import errors

class PlugCommandHandler():
    """
    Class to Handle Plug Commands from CLI
    """
    def __init__(self, plug_shared):
        self._plug_shared = plug_shared

    def _get_plug_client(self, ip_addr):
        for client in self._plug_shared.plug_clients:
            if client.get("IP", None) == ip_addr:
                return client.get("Client", None)

    async def parse_command(self, msg):
        command = msg.get("Command", None)
        if command is None:
            return
        return await getattr(self, command)(msg)

    async def list_plugs(self, args):
        device_list = []
        
        for device in self._plug_shared.plug_clients:
            try:
                await device.get("Client").update()
                device_list.append(
                    {
                        "ip_addr": device.get("IP"),
                        "alias": device.get("Client").alias,
                        "on": device.get("Client").is_on
                    }
                )
            except:
                pass

        return {"status": device_list}

    async def add_plug(self, msg):
        ip_addr = msg.get("IP", None)
        if ip_addr:
            plug_client = self._get_plug_client(ip_addr=ip_addr)
            if plug_client is None:
                try:
                    #create object for plug
                    self._plug_shared.plug_clients.append(
                        {
                            "IP": ip_addr,
                            "Alias": None,
                            "Client": SmartPlug(ip_addr),
                            "MacAddress": None,
                            "Active": None,
                            "Connected": None
                        }
                    )
                    client = self._plug_shared.plug_clients[-1]["Client"]
    
                    await client.update()
                    self._plug_shared.plug_clients[-1]["MacAddress"] = client.mac
                    self._plug_shared.plug_clients[-1]["Active"] = client.is_on
                    self._plug_shared.plug_clients[-1]["Alias"] = client.alias
                    plug = self._plug_shared.plug_clients[-1]
                    #insert into database

                    doc = self._plug_shared._mongoDB_access_col.find({"MAC Address": plug['MacAddress']}).limit(1)

                    if len(list(doc)) == 0: #doesnt exist in database
                        #insert
                        self._plug_shared._mongoDB_access_col.insert_one(
                            {
                            "MAC Address": plug["MacAddress"],
                            "Name": plug["Alias"],
                            "Active": plug["Active"],
                            "Entry Time": datetime.utcnow(),
                            "Connected": True,
                            "IP": plug["IP"],
                            "lastPower": 0
                            }
                        )
                    else:
                        #update
                        self._plug_shared._mongoDB_access_col.update_one({"MAC Address": plug['MacAddress']}, 
                            {'$set': 
                                {
                                "MAC Address": plug["MacAddress"],
                                "Name": plug["Alias"],
                                "Active": plug["Active"],
                                "Entry Time": datetime.utcnow(),
                                "Connected": True,
                                "IP": plug["IP"]
                                }
                            }
                        )

                    dict = {'IP': plug["IP"]}
                    with open('config.yml','r') as yamlfile:
                        cur_yaml = yaml.safe_load(yamlfile) 
                        cur_yaml['smartPlugs'].append(dict)
                    if cur_yaml:
                        with open('config.yml','w') as yamlfile:
                            yaml.safe_dump(cur_yaml, yamlfile) 
                    plug_col = self._plug_shared._mongoDB_plugs_db[plug["MacAddress"]]

                    #create task
                    self._plug_shared.plug_connections[ip_addr] = asyncio.create_task(
                        self._plug_shared.query_plug_emeter(plug=plug["Client"], plug_col=plug_col, access_col=self._plug_shared._mongoDB_access_col, ip=plug["IP"])
                    )
                    
                    # connection.cancel
                    # self._plug_shared.plug_connections[ip_addr].pop()
                    return {"status": "Added"}
                except:
                    return {"status": "Error Adding"}
            else:
                return {"status": "Exists Already"}


        

    async def set_alias(self, msg):
        response = {}
        ip_addr = msg.get("IP", None)
        alias_name = msg.get("Action", None)

        if ip_addr and alias_name:
            plug_client = self._get_plug_client(ip_addr=ip_addr)

            await plug_client.set_alias(alias_name)
            await plug_client.update()

            self._plug_shared._mongoDB_access_col.update_one({"MAC Address": plug_client.mac}, 
                    {'$set': 
                        {
                        "Name": plug_client.alias,
                        }
                    }
                )

            response = {"ip_addr": ip_addr, "alias": plug_client.alias}

        return {"status": response}

    async def toggle(self, msg):
        try:
            ip_addr = msg.get("IP", None)
            on = msg.get("Action", None)
            if ip_addr:
                plug_client = self._get_plug_client(ip_addr=ip_addr)
            print(ip_addr, on)
            if on == 1:
                await plug_client.turn_on()
                await plug_client.update()
                # return {"status": {"device_address": ip_addr, "on": True}}
            elif on == 0:
                await plug_client.update()
                self._plug_shared._mongoDB_access_col.update_one({"MAC Address": plug_client.mac}, 
                    {'$set': 
                        {
                        "lastPower": plug_client.emeter_realtime.power,
                        }
                    }
                )
                await plug_client.turn_off()
                await plug_client.update()
                # return {"status": {"device_address": ip_addr, "on": False}}
            elif on == -1:
                await plug_client.turn_off()
                await plug_client.update()
                await asyncio.sleep(2)
                await plug_client.turn_on()
                await plug_client.update()
                # return {"status": {"device_address": ip_addr, "on": True}}
            elif on == -2:
                await plug_client.update()
                if plug_client.is_on:
                    self._plug_shared._mongoDB_access_col.update_one({"MAC Address": plug_client.mac}, 
                        {'$set': 
                            {
                            "lastPower": 100000000000,
                            }
                        }
                    )
                    await plug_client.turn_off()
                    await plug_client.update()
                    # return {"status": {"device_address": ip_addr, "on": False}}
                else:
                    await plug_client.turn_on()
                    await plug_client.update()
                    # return {"status": {"device_address": ip_addr, "on": True}}
            self._plug_shared._mongoDB_access_col.update_one({"MAC Address": plug_client.mac}, 
                        {'$set': 
                            {
                            "Active": plug_client.is_on,
                            }
                        }
                    )
            return {"status": {"device_address": ip_addr, "on": plug_client.is_on}}
        except exceptions.SmartDeviceException:
            return {"status" : "Plug Disconnected"}
        except errors.ExecutionTimeout:
            return {"status": "Database Disconnected"}
        except: 
            return {"status": "Unknown Error"}
        
    async def emeter(self, msg):
        emeter_stats_keys = {0: "current", 1: "today", 2: "month"}

        ip_addr = msg.get("IP", None)
        stats_amount = msg.get("Action", None)

        if ip_addr:
            plug_client = self._get_plug_client(ip_addr=ip_addr)
            await plug_client.update()
            emeter_key = emeter_stats_keys.get(stats_amount, None)
            if emeter_key == "current":
                emeter_stats = {
                    "device_address": ip_addr,
                    "current (A)": plug_client.emeter_realtime.current,
                    "voltage (V)": plug_client.emeter_realtime.voltage,
                    "power (W)": plug_client.emeter_realtime.power,
                    "total power (kWh)": plug_client.emeter_realtime.total
                }
            elif emeter_key == "today":
                emeter_stats = {
                    "device_address": ip_addr,
                    "todays power (kWh)": plug_client.emeter_today,
                }
            elif emeter_key == "month":
                emeter_stats = {
                    "device_address": ip_addr,
                    "this months power (kWh)": self._plug_shared.plug_clients[
                        ip_addr
                    ].emeter_this_month,
                }

            return {"status": emeter_stats}
