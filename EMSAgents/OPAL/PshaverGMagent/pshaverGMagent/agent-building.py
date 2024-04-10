"""
Agent documentation goes here.
"""

__docformat__ = 'reStructuredText'

import datetime
from datetime import datetime
import time
import logging
import sys
from volttron.platform.agent import utils
from volttron.platform.vip.agent import Agent, Core, RPC

_log = logging.getLogger(__name__)
utils.setup_logging()
__version__ = "0.1"


def pshaverGMagent(config_path, **kwargs):
    """
    Parses the Agent configuration and returns an instance of
    the agent created using that configuration.

    :param config_path: Path to a configuration file.
    :type config_path: str
    :returns: Pshavergmagent
    :rtype: Pshavergmagent
    """
    try:
        config = utils.load_config(config_path)
    except Exception:
        config = {}

    if not config:
        _log.info("Using Agent defaults for starting configuration.")

    setting1 = config.get('setting1', 1)
    setting2 = config.get('setting2', "some/random/topic")

    return Pshavergmagent(setting1, setting2, **kwargs)


class Pshavergmagent(Agent):
    """
    Document agent constructor here.
    """

    def __init__(self, setting1=1, setting2="some/random/topic", **kwargs):
        super(Pshavergmagent, self).__init__(**kwargs)
        _log.debug("vip_identity: " + self.core.identity)
        self.BEMStag=0
        self.setting1 = setting1
        self.setting2 = setting2
        self.BEMStag = setting1

        self.default_config = {"setting1": setting1,
                               "setting2": setting2}

        self.Peakshaverthreashhold=10
        self.total_consumption=0
        self.total_uncontrolable=0
        self.simhour=0
        self.Threshour=0
        self.simminute=0

        # Set a default configuration to ensure that self.configure is called immediately to setup
        # the agent.
        self.vip.config.set_default("config", self.default_config)
        # Hook self.configure up to changes to the configuration file "config".
        self.vip.config.subscribe(self.configure, actions=["NEW", "UPDATE"], pattern="config")
        self.core.periodic(15,self.PeakShaver)

    def configure(self, config_name, action, contents):
        """
        Called after the Agent has connected to the message bus. If a configuration exists at startup
        this will be called before onstart.

        Is called every time the configuration in the store changes.
        """
        config = self.default_config.copy()
        config.update(contents)

        _log.debug("Configuring Agent")

        try:
            setting1 = (config["setting1"])
            setting2 = str(config["setting2"])
        except ValueError as e:
            _log.error("ERROR PROCESSING CONFIGURATION: {}".format(e))
            return
        for x in self.setting2:
            self._create_subscriptions(str(x))
            print(str(x))
            

    def _create_subscriptions(self, topic):
        """
        Unsubscribe from all pub/sub topics and create a subscription to a topic in the configuration which triggers
        the _handle_publish callback
        """
        self.vip.pubsub.unsubscribe("pubsub", None, None)

        self.vip.pubsub.subscribe(peer='pubsub',
                                  prefix=topic,
                                  callback=self._handle_publish,all_platforms=True)

    def _handle_publish(self, peer, sender, bus, topic, headers, message):
        """
        Callback triggered by the subscription setup using the topic from the agent's config file
        """
        print("Peak_shaver",topic)
        temptopic1='Microgrid/GLEAMM/BuildingP/LPC/all'
        if topic == temptopic1:
            tag='controllable'
            self.total_consumption=message[tag]
            self.total_uncontrolable=message['Main_P'] - message[tag]
            print("total consumption............",self.total_consumption)
        temptopic2='control/BuildingP/PeakShaver'
        print("Peak_shaver",topic)
        if topic == 'devices/Microgrid/GLEAMM/RTACHREXTRA/all':
             self.simhour=message[0]['Simhour']
             self.simminute=message[0]["Min"]
             print('SIMHour.................................', self.simhour)
        if topic == temptopic2:
            print("***********************got it******************Pshaver",message)
            self.Peakshaverthreashhold=message[0]["Threashhold"]  #-self.total_uncontrolable
            self.Threshour=message[0]["Hour"]
            print("***********************got it******************",self.Peakshaverthreashhold)
            self.PeakShaver()
    
    def PeakShaver(self):
        now = utils.format_timestamp(datetime.utcnow())
        utcnow = utils.get_aware_utc_now()
 
        header = {
        #    headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            "Date": utils.format_timestamp(utcnow),
            "TimeStamp":utils.format_timestamp(utcnow)
        }
        ##        
        shedding=self.total_consumption-self.Peakshaverthreashhold
        print("nothing to shed*************************",shedding)
       # if self.Peakshaverthreashhold >=0 :
        #   result=self.vip.rpc.call('platform.driver','set_point', 'Microgrid/GLEAMM/L4','CMDCBRK',0).get(timeout=20)

        if shedding >0.5 and self.Peakshaverthreashhold>=0 and (self.Threshour==self.simhour):
           #result=self.vip.rpc.call('platform.driver','set_point', 'Microgrid/GLEAMM/BuildingI','CMDIBRK',1).get(timeout=20)
           topics='control/plc/BuildingP/shedding'
           result = self.vip.pubsub.publish(peer='pubsub',topic=topics,message=shedding)
           print("PShaver_Start shedding*************************",shedding,self.Peakshaverthreashhold)
           #topics = "devices/Centralcontrol/Control/Peakshaver/all"
          # Message={"shedding":shedding ,"increment":0}
           #result = self.vip.pubsub.publish(peer='pubsub',topic=topics, headers=header,message= Message)

        if shedding <0 and self.Peakshaverthreashhold>=0 and  (self.Threshour==self.simhour):
           #result=self.vip.rpc.call('platform.driver','set_point', 'Microgrid/GLEAMM/BuildingI','CMDIBRK',1).get(timeout=20)
           topics='control/plc/BuildingP/increment'
           result = self.vip.pubsub.publish(peer='pubsub',topic=topics,message=abs(shedding))
           print("PShaver_Start increment*************************",abs(shedding),self.Peakshaverthreashhold)
           # uncoment above 2 lines for incremental control
          ## topics = "devices/Centralcontrol/Control/Peakshaver/all"
           #Message={"building_status":0 ,"Shedding_Threashold":abs(shedding)}
           #result = self.vip.pubsub.publish(peer='pubsub',topic=topics, headers=header,message= Message)


        if self.Peakshaverthreashhold < 0  and  (self.Threshour==self.simhour) :
            pass
           #result=self.vip.rpc.call('platform.driver','set_point', 'Microgrid/GLEAMM/BuildingI','CMDIBRK',0).get(timeout=20)
           #result=self.vip.rpc.call('platform.driver','set_multiple_points', 'Microgrid/GLEAMM/BuildingI',[('CMDIT1',0),('CMDIT2',0),('CMDIT3',0),('CMDIT4',0),('CMDIT5',0),('CMDIT6',0),('CMDIT7',0),('CMDIT8',0),('CMDIT9',0),('CMDIT10',0)]).get(timeout=20)  
           ##topics='control/plc/BEMS'+str(self.BEMStag)+'/increment'
           ##result = self.vip.pubsub.publish(peer='pubsub',topic=topics,message=abs(shedding))
           ##print("PShaver_Start increment*************************",abs(shedding),self.Peakshaverthreashhold)
           ## uncoment above 2 lines for incremental control
           #topics = "devices/Centralcontrol/Control/Peakshaver/all"
           #Message={"building_status":0 ,"Shedding_Threashold":abs(shedding)}
           #result = self.vip.pubsub.publish(peer='pubsub',topic=topics, headers=header,message= Message)          



        else:
            print("nothing to shed*************************",shedding,self.Peakshaverthreashhold,"Thresh_hour:", self.Threshour,"RTAC_hour", self.simhour)
       # temptopic2="dataconcentrator/devices/control/BEMS"+str(self.BEMStag)+"/PeakShaver"
       # print( temptopic2)



    @Core.receiver("onstart")
    def onstart(self, sender, **kwargs):
        """
        This is method is called once the Agent has successfully connected to the platform.
        This is a good place to setup subscriptions if they are not dynamic or
        do any other startup activities that require a connection to the message bus.
        Called after any configurations methods that are called at startup.

        Usually not needed if using the configuration store.
        """
        # Example publish to pubsub
        self.vip.pubsub.publish('pubsub', "some/random/topic", message="HI!")

        # Example RPC call
        # self.vip.rpc.call("some_agent", "some_method", arg1, arg2)
        pass

    @Core.receiver("onstop")
    def onstop(self, sender, **kwargs):
        """
        This method is called when the Agent is about to shutdown, but before it disconnects from
        the message bus.
        """
        pass

    @RPC.export
    def rpc_method(self, arg1, arg2, kwarg1=None, kwarg2=None):
        """
        RPC method

        May be called from another agent via self.core.rpc.call
        """
        return self.setting1 + arg1 - arg2


def main():
    """Main method called to start the agent."""
    utils.vip_main(pshaverGMagent, 
                   version=__version__)


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
