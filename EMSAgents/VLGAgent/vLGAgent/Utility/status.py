import csv
import sys
from csv import DictReader, DictWriter
import os
from json import load
import copy as cp
from abc import ABC,abstractmethod
import pandas as pd

class Status(ABC):
    @abstractmethod
    def read_load_configurations(self):
        pass
    @abstractmethod
    def read_actual_load_consumption(self):
        pass
    @abstractmethod
    def get_actual_load_consumption(self):
        pass
    @abstractmethod
    def update_actual_load_consumption(self,message,topic):
        pass
    
class Status_GLEAM_D2D(Status):
    def __init__(self,CSV_PATH,vip):
        self.__CSV_PATH=CSV_PATH
        self.__loads={}
        self.__priority_consumption={}
        self.read_load_configurations()
        self.__timesync={}
        self.__thresholds={1:20000,2:20000,3:20000}
        self.__GAMSHourFlag=0
        self.__baseline_hour=0
        self.vip=vip
        
    def read_load_configurations(self):
        print("Reading the device")
 
        if os.path.isfile(self.__CSV_PATH):
            self.__loads= pd.read_csv (self.__CSV_PATH)
        else:
            raise RuntimeError("CSV device at {} does not exist".format(self.__CSV_PATH))
        return 0
    def read_actual_load_consumption(self):
        pass
    def get_actual_load_consumption(self):
        return [self.__thresholds,self.__loads,self.__GAMSHourFlag,self.__timesync]
    def update_actual_load_consumption(self,message,topic):
        if topic=='record/GLEAMM':
           self.__timesync['RTAC_Sim_Min']=int(message['GLEAMM']['RTACHREXTRA']['Min'])
           self.__timesync['RTAC_Sim_Hr']=int(message['GLEAMM']['RTACHREXTRA']['Hour'])
           self.vip.pubsub.publish(peer='pubsub',topic= 'devices/campus/building/sync/all', message=[{'Hour':self.__timesync['RTAC_Sim_Hr'],'Minute':self.__timesync['RTAC_Sim_Min']}])
      
            

                  
        if topic =='record/building540':
               self.__thresholds[1]=int(message['building540']['GAMS']['Solar_4'])
               self.__thresholds[2]=int(message['building540']['GAMS']['Solar_5'])
               self.__thresholds[3]=int(message['building540']['GAMS']['Solar_6'])   
               self.__GAMSHourFlag=int(message['building540']['GAMS']['GAMSHourFlag'])
               self.__timesync['GAMS_Hr']=int(message['building540']['GAMS']['Interruptible_24'])
               print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%',self.__timesync)

               print('Threshold',self.__thresholds,'GAMSHourFlag',self.__GAMSHourFlag)
        for ind in self.__loads.index:
            if topic =='record/GLEAMM':
            #    print('ttttttttttttttttttttttttest',(message[self.__loads['Site'][ind]][self.__loads['LoadType'][ind]][self.__loads['LoadID'][ind]]/self.__loads['Devider'][ind])*float(self.__loads['Multiplayer'][ind]))
                try:
                   self.__loads['Consumption'][ind]=(message[self.__loads['Site'][ind]][self.__loads['LoadType'][ind]][self.__loads['LoadID'][ind]]/self.__loads['Devider'][ind])*float(self.__loads['Multiplayer'][ind])
                   self.__loads['ConsumptionAhed'][ind]=(message[self.__loads['Site'][ind]][self.__loads['LoadType'][ind]][self.__loads['LoadID'][ind]]/self.__loads['Devider'][ind])*float(self.__loads['Multiplayer'][ind])
                   self.__loads['BaselineConsumption'][ind]=(message[self.__loads['Site'][ind]][self.__loads['LoadType'][ind]][self.__loads['LoadID'][ind]]/self.__loads['Devider'][ind])*float(self.__loads['Multiplayer'][ind])

            
                except:
                    pass
            elif topic =='record/building540':
                  
            #    print('ttttttttttttttttttttttttest',(message[self.__loads['Site'][ind]][self.__loads['LoadType'][ind]][self.__loads['LoadID'][ind]]/self.__loads['Devider'][ind])*float(self.__loads['Multiplayer'][ind]))
                  try:
                   self.__loads['Consumption'][ind]=(message[self.__loads['Site'][ind]][self.__loads['LoadType'][ind]][self.__loads['LoadID'][ind]]/self.__loads['Devider'][ind])*float(self.__loads['Multiplayer'][ind])
                  except:
                      pass

        for i in self.__loads['Priority'].unique():
                 tempsum=self.__loads.loc[self.__loads['Priority']==i]['Consumption'].sum()
                 print('Consum of the priority groups:',i,' = ',tempsum)
 
            
        
class Status_NIRE_D2D(Status):
    def __init__(self,CSV_PATH):
        self.__CSV_PATH=CSV_PATH
        self.read_load_configurations()
        self.__loads
    def read_load_configurations(self):
        print("Reading the device")
        if os.path.isfile(self.__CSV_PATH):
            self.__loads= pd.read_csv (self.__CSV_PATH)
        else:
            raise RuntimeError("CSV device at {} does not exist".format(self.__CSV_PATH))
        return 0
    def read_actual_load_consumption(self):
        pass
    def get_actual_load_consumption(self):
        return self.__loads
    def update_actual_load_consumption(self,message,topic):
        #print(self.__loads.loc[self.__loads['Priority']==1].index)
      
        for ind in self.__loads.index:
            try:
                self.__loads['Consumption'][ind]=message[self.__loads['Site'][ind]][self.__loads['LoadType'][ind]][self.__loads['LoadID'][ind]]
            except:
                pass
        for i in self.__loads['Priority'].unique():
             tempsum=self.__loads.loc[self.__loads['Priority']==i]['Consumption'].sum()
             print('Consumption of the priority group:$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$',i,)
  