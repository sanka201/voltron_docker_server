from typing import Protocol
from messages import MessageType
from messages  import Message
from diagonstic import DiagnosticsSource
from devices import WeMoPlugDevice
from csv import DictReader, DictWriter
import os
import csv
import collections
from collections import defaultdict
import operator
import numpy as np
class LPCmodule(Protocol):

    def set_lpc_control_mode(self,topic:str,message:dict)->Message:
        ...
    def read_device_configurations(self,csv_path)->Message:
        ...
    def read_device_status(self,topic,message):
        ...
    def set_priority(self,priority):
        ...
    def lpc_shedding(self,message)->Message:
        ...
    def lpc_increment(self,message)->Message:
        ...
    def get_total_device_consumption():  
        ...

class LPCWeMo(LPCmodule):
    def __init__(self,VIP):
        self.vip=VIP
        self.__WeMo_Actual_Status={}
        self.__WeMo_Priorities=defaultdict(list)
        self.__WeMo_Power_Consumption_Sql={}
        self.__WeMo_Topics={}
        self.__WeMo_Consumption={}
        self.__WeMo_cc={}
        self.__WeMo_Priority_increment={}
        self.__loads_consumption={}
        self.__loads_max_consumption={}
        self.__buildings={}
        self.__WeMo_respond_list={}
        self.__total_consumption=0
        self.__control_command=0
        self.__Power_Consumption_Upper_limit=1000000
        self.__controller_mode='None'
        self.__controller_mode_active='Inactive'
        self.__building_Controller=""

    def set_lpc_control_mode(self,topic,message)->Message:
       
        if str(topic).find('control') >=0:
            print("Control mode ##############################",topic,message)
            if topic.find('shedding') >=0:
                self.__control_command=int(message)
                self.__controller_mode_active='Active'
                self.__controller_mode='Shedding'
                devicemessage=self.lpc_shedding(message)
                self.__controller_mode_active='Inactive'
            elif topic.find('directcontrol') >=0:
                print("Direct control ##############")
                self.__control_command=int(message[1])
                self.__controller_mode_active='Active'
                self.__controller_mode='Direct'
                devicemessage=self.lpc_directcontrol(message)
                self.__controller_mode_active='Inactive'
            elif topic.find('increment') >=0:
                self.__control_command=int(message)
                self.__controller_mode_active='Active'
                self.__controller_mode='Increment'
                devicemessage=self.lpc_increment(message)
                self.__controller_mode_active='Inactive'
            
            elif topic.find('setpriority') >=0:
                self.__control_command=int(message)
                self.__controller_mode_active='Active'
                self.__controller_mode='setpriority'
                devicemessage=self.set_priority(message)
                self.__controller_mode_active='Inactive'
            else:
                devicemessage=Message('WeMo',MessageType.WRITE,None,{})
        else:
            devicemessage=Message('WeMo',MessageType.WRITE,None,{})

        
        return devicemessage
        
    def read_device_configurations(self,csv_path)->Message:
       devicemessage=Message('WeMo',MessageType.WRITE,None,{})
       if os.path.isfile(csv_path):
              with open(csv_path, "r") as csv_device:
                reader = DictReader(csv_device)         
         #iterate over the line of the csv
                noofbuilding={}
                for point in reader:
                    Name = point.get("Name")
                    Priority = point.get("Priority")
                    Topic = point.get("Topic")
                    Cluster_Controller = point.get("cc")
                    self.__building_Controller=Cluster_Controller
                    Consumption = point.get("Consumption")
                    if Name=='\t\t\t':
                         pass
                    else:
                        Name=Name+"_"+Cluster_Controller
                        self.__WeMo_Actual_Status[Topic]=0
                        self.__WeMo_Priorities[int(Priority)].append([Topic,int(Consumption)])
                       # self.__WeMo_Topics[Name]=self.__topic+Cluster_Controller+"/"+Name
                        self.__WeMo_Consumption[Topic]=Consumption
                        #self.__WeMo_cc[Name]=Cluster_Controller
                        self.__WeMo_Power_Consumption_Sql[Topic]=0
                        self.__loads_max_consumption[Topic]=0
                        self.__loads_consumption[Topic]=0
                        self.__WeMo_Priority_increment[Topic]=int(Priority)
                        #self.__buildings[Building]=0 
#                        self.set_lpc_control_mode('control/setpriority',self.__WeMo_Priority_increment)
                print("REEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
                #print(self.__WeMo_Priority_increment)
                devicemessage=Message('WeMo',MessageType.WRITE,'priority',self.set_priority(self.__WeMo_Priority_increment))
       else:
            # Device hasn't been created, or the path to this device is incorrect
            raise RuntimeError("CSV device at {} does not exist".format(self.csv_path))
       return devicemessage
    def read_device_status(self,topic,message):
        result=0
        print('*********************************************** Topic *******************************',topic)
        result = topic.find('NIRE_WeMo_cc_1')
        
        if result >=0:
            result=0
            
            result = topic.find('control')
            if result >=0:
                    pass
            elif topic.find('devices/building540/NIRE_WeMo_cc_1')>=0:
                load_tag=topic.split("/all")
       #     index=load_tag[-2]+"_"+load_tag[-3][-1]
#                print(self.__loads_consumption)
                self.__loads_consumption[load_tag[0]]=int((message[0])['power']/1000)
                print(self.__loads_consumption[load_tag[0]],'hah')
                self.__WeMo_Actual_Status[load_tag[0]]=int((message[0])['status'])
                self.__WeMo_Priority_increment[load_tag[0]]=int((message[0])['priority'])
                if self.__loads_max_consumption[load_tag[0]]< self.__loads_consumption[load_tag[0]]:
                    self.__loads_max_consumption[load_tag[0]]=self.__loads_consumption[load_tag[0]]
                self.__total_consumption=sum(self.__loads_consumption.values())
 #               print(self.__loads_consumption)
    def set_priority(self,priority):
        topic=[]
        message=[]
        for i in priority:
            print("setting priority to cluster controller for ",i,priority[i],i.split("devices/")[1])
            topic.append( i.split("devices/")[1])
            message.append(priority[i])
           # result=self.vip.rpc.call('platform.driver','set_point', i.split("devices/")[1],'priority',priority[i]).get(timeout=20)
        return {'topic':topic,'message':message}
    
    def lpc_shedding(self,message)->Message:
        self.__check_shedding_condition()
        self.__sort_WeMo_list()            
        self.__WeMo_Scheduled_Status=self.__schedule_shedding_control_WeMo()
        data=self.__send_WeMo_schedule()
        return Message('WeMo',MessageType.WRITE,'status',data)
    def lpc_increment(self,message)->Message:
        self.__check_shedding_condition()
        self.__sort_WeMo_list()
        self.__WeMo_Scheduled_Status=self.__schedule_increment_control_WeMo()
        data=self.__send_WeMo_schedule()
        return Message('WeMo',MessageType.WRITE,'status',data)
    def lpc_directcontrol(self,message):
        if message[0]=='all':
           topic=[]
           tempmessage=[]
           for i in self.__WeMo_Priority_increment:
                 print("Direct control ##############")
                 topic.append(i.split("devices/")[1])
                 tempmessage.append(message[1])
           return Message('WeMo',MessageType.WRITE,'status',{'topic':topic,'message':tempmessage})


    def __check_shedding_condition(self):
        total_consumption=self.__total_consumption
        self.__Power_Consumption_Upper_limit=total_consumption-int(self.__control_command)
        if self.__Power_Consumption_Upper_limit<0:
                    self.__Power_Consumption_Upper_limit=0 
        print("cheked",self.__Power_Consumption_Upper_limit)    

    def __sort_WeMo_list(self):
        sorted_x= sorted(self.__WeMo_Priorities.items(), key=operator.itemgetter(0),reverse=False) # Sort ascending order (The lowest priority is first)
        self.__WeMo_Priorities = collections.OrderedDict(sorted_x)

    def __schedule_shedding_control_WeMo(self):
        Temp_WeMo_Schedule={}
        Temp_WeMos=defaultdict(list)
        for x in self.__WeMo_Actual_Status:
              Temp_WeMos[int(self.__WeMo_Priority_increment[x])].append([x,int(self.__loads_consumption[x])])
        consumption=self.__total_consumption
        while bool(Temp_WeMos)==True:
            print(Temp_WeMos[min(Temp_WeMos.keys())])
            for y in Temp_WeMos[min(Temp_WeMos.keys())]:
                consumption=consumption-y[1]
                Temp_WeMo_Schedule[y[0]]=0
                if consumption <= self.__Power_Consumption_Upper_limit:
                    break;
            if consumption <= self.__Power_Consumption_Upper_limit:
                break;
            del Temp_WeMos[min(Temp_WeMos.keys())]
        return Temp_WeMo_Schedule
    def __schedule_increment_control_WeMo(self):
        print('********************Increment control initialized****************************')
        Temp_WeMo_Schedule={}
        Temp_Off_WeMos=defaultdict(list)
        for x in self.__WeMo_Actual_Status:
              if self.__WeMo_Actual_Status[x]==0:
                  Temp_Off_WeMos[int(self.__WeMo_Priority_increment[x])].append([x,int(self.__loads_max_consumption[x])])
              else:
                  pass
         #if bool(Temp_Off_WeMos[x])==True:
        consumption=0
        while bool(Temp_Off_WeMos)==True:
            for y in Temp_Off_WeMos[max(Temp_Off_WeMos.keys())]:
                consumption=y[1]+consumption

                if consumption >= self.__control_command:
                    break;
                Temp_WeMo_Schedule[y[0]]=1
            if consumption >= self.__control_command:
                break;

            del Temp_Off_WeMos[max(Temp_Off_WeMos.keys())]
        print('consumption',consumption,self.__loads_max_consumption)
        print('off_wemos',Temp_Off_WeMos)
        return Temp_WeMo_Schedule


    def __send_WeMo_schedule(self)->dict:
        print("sending schedule............")
        topic=[]
        message=[]
        for y in self.__WeMo_Scheduled_Status:            
            topic.append(y.split("devices/")[1])
            message.append(self.__WeMo_Scheduled_Status[y])
        return {'topic':topic,'message':message}
    def get_total_device_consumption(self):
        self.vip.pubsub.publish('pubsub', self.__building_Controller+"/TotalWeMoConsumption", message=self.__total_consumption)
        return self.__total_consumption
                
