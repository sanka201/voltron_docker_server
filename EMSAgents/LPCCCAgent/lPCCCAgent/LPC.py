from abc import ABC,abstractmethod
from csv import DictReader, DictWriter
import os
import csv
import collections
from collections import defaultdict
import operator
import numpy as np


class LPC(ABC):
    @abstractmethod
    def read_device_configurations(csv_path):
        pass
    def read_device_status(topic,message):
        pass
    def set_lpc_control_mode(topic,message):
        pass
    def get_total_device_consumption():
        pass
    def lpc_shedding(message):
        pass
    def lpc_directcontrol(message):
        pass
    def lpc_increment(message):
        pass
    def get_lpc_status():
        pass
    def set_priority(priority):
        pass

   
class LPCWemo(LPC):
    def __init__(self,wemo_topic="acquisition/loads/building"):
        self.__topic=wemo_topic
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
    def read_device_configurations(self,csv_path):
        print("###################################__Reading_device_configuration__##########################")
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
                    #This is the topic that use for RPC call
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
                self.set_priority(self.__WeMo_Priority_increment)    
        else:
            # Device hasn't been created, or the path to this device is incorrect
            raise RuntimeError("CSV device at {} does not exist".format(self.csv_path))
    def read_device_status(self,topic,message):
        result=0
        print('*********************************************** Topic *******************************',topic)
        result = topic.find('NIRE_WeMo_cc_1')
        
        if result >=0:
            result=0
            
            result = topic.find('control')
            if result >=0:
                    pass
            else:
                load_tag=topic.split("/all")
       #     index=load_tag[-2]+"_"+load_tag[-3][-1]
                self.__loads_consumption[load_tag[0]]=int((message[0])['power'])/1000
                print(self.__loads_consumption[load_tag[0]],'hah')
                self.__WeMo_Actual_Status[load_tag[0]]=int((message[0])['status'])
                self.__WeMo_Priority_increment[load_tag[0]]=int((message[0])['priority'])
                if self.__loads_max_consumption[load_tag[0]]< self.__loads_consumption[load_tag[0]]:
                    self.__loads_max_consumption[load_tag[0]]=self.__loads_consumption[load_tag[0]]
                self.__total_consumption=sum(self.__loads_consumption.values())
    def set_priority(self,priority):
        for i in priority:
            print("setting priority to cluster controller for ",i,priority[i],i.split("devices/")[1])
            result=self.vip.rpc.call('platform.driver','set_point', i.split("devices/")[1],'priority',priority[i]).get(timeout=20)
    def set_lpc_control_mode(self,topic,message):
        result = str(topic).find('control')
        if result >=0:
            result=topic.find('shedding')
            if result >=0:
                print('Shedding...........................................................')
                self.__control_command=int(message)
                self.__controller_mode_active='Active'
                self.__controller_mode='Shedding'
                self.lpc_shedding(message)
                self.__controller_mode_active='Inactive'
            result=topic.find('directcontrol')
            if result >=0:
                self.__control_command=int(message[1])
                self.__controller_mode_active='Active'
                self.__controller_mode='Direct'
                self.lpc_directcontrol(message)
                self.__controller_mode_active='Inactive'
            result=topic.find('increment')
            if result >=0:
                self.__control_command=int(message)
                self.__controller_mode_active='Active'
                self.__controller_mode='Increment'
                self.lpc_increment(message)
                self.__controller_mode_active='Inactive'
    def get_total_device_consumption(self):
        self.vip.pubsub.publish('pubsub', self.__building_Controller+"/TotalWeMoConsumption", message=self.__total_consumption)
        return self.__total_consumption
    def lpc_shedding(self,message):
        self.__check_shedding_condition()
        self.__sort_WeMo_list()            
        self.__WeMo_Scheduled_Status=self.__schedule_shedding_control_WeMo()
        print(self.__WeMo_Scheduled_Status)
        self.__send_WeMo_schedule()
    def lpc_directcontrol(self,message):
        if message[0]=='all':
           for i in self.__WeMo_Priority_increment:
#                result=agent.vip.rpc.call('platform.driver','set_point','building540/NIRE_WeMo_cc_1/w'+str(i),'priority',i)
              result=self.vip.rpc.call('platform.driver','set_point', i.split("devices/")[1],'status',message[1]).get(timeout=20)
    def lpc_increment(self,message):
        self.__check_shedding_condition()
        self.__sort_WeMo_list()
        self.__WeMo_Scheduled_Status=self.__schedule_increment_control_WeMo()
        print(self.__WeMo_Scheduled_Status)
        self.__send_WeMo_schedule()

    def __check_shedding_condition(self):
        total_consumption=self.__total_consumption
        self.__Power_Consumption_Upper_limit=total_consumption-int(self.__control_command)
        if self.__Power_Consumption_Upper_limit<0:
                    self.__Power_Consumption_Upper_limit=0            
    def get_lpc_status(self):
        return {'Mode':self.__controller_mode,'Command':self.__control_command,'Status':self.__controller_mode_active} 
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

    def __send_WeMo_schedule(self):
        print("sending schedule............")
        if bool(self.__WeMo_Scheduled_Status)==True:
            #for x in self.WeMo_Actual_Status.keys():
                #if x in   self.WeMo_Scheduled_Status:
                 #   pass
                #else :
                  #  self.WeMo_Scheduled_Status[x]=1

            for y in self.__WeMo_Scheduled_Status:            
                WeMo=self.__send_request(y,1)
                if WeMo==0:
                #print('*************************************************************Recieved1*************************************************************')
                    pass
                else :
                #print(y+'*************************************************************Recieved2*************************************************************'+WeMo)
                   self.__WeMo_respond_list[WeMo]=WeMo
                   print("WeMo_respond_list"+str(self.__WeMo_respond_list))
                
            for ybar in self.__WeMo_respond_list:
                # print(ybar+'*************************************************************deleting*************************************************************')
                     print(self.__WeMo_Scheduled_Status)
                     del self.__WeMo_Scheduled_Status[ybar]
            self.__control_command=0
                 
        self.__WeMo_respond_list.clear()

    def __send_request(self,WeMo,CC):
        ## Sending commandes to the wemo cluster controller
        try:
            print("sending requests to cluster controller for ",WeMo,self.__WeMo_Scheduled_Status[WeMo],WeMo.split("devices/")[1])
            result=self.vip.rpc.call('platform.driver','set_point', WeMo.split("devices/")[1],'status',self.__WeMo_Scheduled_Status[WeMo]).get(timeout=20)
            if result['status']==11:
                print('Wemo is not responded')
                return 0
            else:
                #del self.WeMo_Scheduled_Status[WeMo]
                print(self.__WeMo_Scheduled_Status)
                return WeMo
        except:
            print("somthing happend")
            
            return 0
