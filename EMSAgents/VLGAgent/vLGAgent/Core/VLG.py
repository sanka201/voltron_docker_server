import csv
import sys
from csv import DictReader, DictWriter
import os
from json import load
import copy as cp
from abc import ABC,abstractmethod
import pandas as pd

class VLG(ABC):
    @abstractmethod
    def load_groups(self):
        pass
    

class VLG_GLEAMM(VLG):
      def __init__(self):
        self.__loads={}
        self.__threshold={}
        self.__priority_consumption={}
      def load_groups(self,threshold,loads):
        self.__loads=loads
        self.__threshold=threshold
        consump={}
        for j in self.__loads['Controller'].unique():
            consump[j]=0
        for i in self.__loads['Priority'].unique():
            self.__priority_consumption[i]=self.__loads.loc[(self.__loads['Priority']==i) ]['Consumption'].sum()
            print("priority group consumption",self.__priority_consumption,"Threshold",self.__threshold)
            err=self.__priority_consumption[i]-self.__threshold[i]
            if err >0:
                
                for j in self.__loads.loc[self.__loads['Priority']==i]['Controller'].unique():
                      tempsum=self.__loads.loc[(self.__loads['Priority']==i) & (self.__loads['Controller']==j)]['Consumption'].sum()
                      calc=err-tempsum
                      if calc>=0:
                         consump[j]=-tempsum+consump[j]
                         err=calc
                      else:
                        consump[j]=-abs(err)+consump[j]
                        print("Break Priority ",i,":","Controller",j,":",tempsum,err,consump)
                        break
                      print("Priority ",i,":","Controller",j,":",tempsum,err)
                
            else:
                    print("Incrementing has initialized",err)
                    for j in self.__loads.loc[self.__loads['Priority']==i]['Controller'].unique():
                      tempsum=self.__loads.loc[(self.__loads['Priority']==i) & (self.__loads['Controller']==j)]['Consumption'].sum()
                      controlmax=self.__loads.loc[(self.__loads['Priority']==i) & (self.__loads['Controller']==j)]['Controller_Max'].sum()
                      print("Control_Max.....",controlmax)
                      calc=abs(err)-(controlmax-tempsum)
                      if calc>=0:
                         consump[j]=controlmax-tempsum+consump[j]
                         err=calc
                      else:
                        consump[j]=abs(err)+consump[j]
                        print("Break Priority ",i,":","Controller",j,":",tempsum,err,consump)
                        break
                      print("Priority ",i,":","Controller",j,":",tempsum,err)
            
 
        command={}
        for j in self.__loads['Controller'].unique():
                command[j]=0
                tempsum=self.__loads.loc[self.__loads['Controller']==j]['Consumption'].sum()
                print("Now temp sum",tempsum)
                if consump[j]==0:
                    consump[j]=0
                consump[j]=consump[j]+tempsum
                #command[j]=consump[j]+tempsum
        print("current consumption",consump)
        return consump

 
   