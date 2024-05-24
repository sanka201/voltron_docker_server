import csv
import sys
import time
from csv import DictReader, DictWriter
import os
from json import load
import copy as cp
from abc import ABC,abstractmethod
import pandas as pd
from volttron.platform.agent import utils
from volttron.platform.vip.agent import Agent, Core, RPC
class Interface(ABC):
    @abstractmethod
    def send_threshold(self,threshold):
        pass
    def publish_priority_consumption(self,threshold):
        pass



class Interface_GLEAMM(Interface):
        def __init__(self,vip):
            self.vip=vip
        def send_threshold(self,threshold,timesync):
            
            self.vip.pubsub.publish(peer='pubsub',topic= 'GAMS/control/hourflag',message=0)
            print("recive &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&TT",threshold)
            time.sleep(1)

            for j in threshold:
                if j=='NIRE_WeMo_cc_1':
                    self.__NIRE_WeMo_cc_1(threshold[j])
                elif j=='NIRE_WeMo_cc_4':
                    self.__NIRE_WeMo_cc_4(threshold[j])
                elif j=='NIRE_AlLPHA_cc_1':
                    self.__NIRE_ALPHA_cc_1(threshold[j])
                elif j=='NIRE_ALPHA_cc_2':
                    self.__NIRE_ALPHA_cc_2(threshold[j])
                elif j=='BuildingI':
                    self.__Building_I(threshold[j],timesync)
                elif j=='BuildingP':
                    self.__Building_P(threshold[j],timesync)
                elif j=='BuildingC':
                    self.__Building_C(threshold[j],timesync)
                else:
                    pass
                "Threashhold"
                    
        def __NIRE_WeMo_cc_1(self,threshold):
            print("NIRE_WeMo_cc_1",threshold)
            self.vip.pubsub.publish(peer='pubsub',topic= 'Building540/HMIcontrol/ClusterControl/Threshold/cc1', message=int(threshold))
        def __NIRE_WeMo_cc_4(self,threshold):
            print("NIRE_WeMo_cc_4",threshold)
        def __NIRE_ALPHA_cc_1(self,threshold):
            print("NIRE_Alpha_cc_1",threshold)
            self.vip.pubsub.publish(peer='pubsub',topic= 'Building540/HMIcontrol/ClusterControl/Threshold/a1', message=int(threshold))
        def __NIRE_ALPHA_cc_2(self,threshold):
            print("NIRE_Alpha_cc_2",threshold)
            self.vip.pubsub.publish(peer='pubsub',topic= 'Building540/HMIcontrol/ClusterControl/Threshold/a2',message=int(threshold))
        def __Building_I(self,threshold,timesync):
            print("BuildingI",threshold)
            self.vip.pubsub.publish(peer='pubsub',topic= 'GLEAMM/HMIcontrol/Threshold/buildingI',message={"Threashhold":int(threshold)/1000,"Hour":int(timesync['GAMS_Hr'])})
        def __Building_P(self,threshold,timesync):
            print("BuildingP",threshold)
            self.vip.pubsub.publish(peer='pubsub',topic= 'GLEAMM/HMIcontrol/Threshold/buildingP',message={"Threashhold":int(threshold)/1000,"Hour":int(timesync['GAMS_Hr'])})
        def __Building_C(self,threshold,timesync):
           
            self.vip.pubsub.publish(peer='pubsub',topic= 'GLEAMM/HMIcontrol/Threshold/buildingC',message={"Threashhold":int(threshold)/1000,"Hour":int(timesync['GAMS_Hr'])})
            print("BuildingC*********************************************************************",threshold)
        def publish_priority_consumption(self,loads):
            for i in loads['Priority'].unique():
              tempsum=int(loads.loc[loads['Priority']==i]['Consumption'].sum())
              self.vip.pubsub.publish(peer='pubsub',topic= 'GAMS/control/consumption/prioritygroup/'+str(i), message=tempsum)
              time.sleep(1)

        


 