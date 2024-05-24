"""
Agent documentation goes here.
"""

__docformat__ = 'reStructuredText'

import logging
import sys
from volttron.platform.agent import utils
from volttron.platform.vip.agent import Agent, Core, RPC
sys.path.insert(0, '/code/volttron/VLGAgent/vLGAgent/Utility')
sys.path.insert(0, '/code/volttron/VLGAgent/vLGAgent/Core')
sys.path.insert(0, '/code/volttron/VLGAgent/vLGAgent/Interface')
import VLG as VLG
import Interface as Interface
import status as status
import pandas as pd

_log = logging.getLogger(__name__)
utils.setup_logging()
__version__ = "0.1"


def vLGAgent(config_path, **kwargs):
    """
    Parses the Agent configuration and returns an instance of
    the agent created using that configuration.

    :param config_path: Path to a configuration file.
    :type config_path: str
    :returns: Vlgagent
    :rtype: Vlgagent
    """
    try:
        config = utils.load_config(config_path)
    except Exception:
        config = {}

    if not config:
        _log.info("Using Agent defaults for starting configuration.")

    setting1 = int(config.get('setting1', 1))
    setting2 = config.get('setting2', "some/random/topic")
    Loadconfigfile = config.get('Loadconfigfile', "string")

    return Vlgagent(setting1, setting2,Loadconfigfile, **kwargs)


class Vlgagent(Agent):
    """
    Document agent constructor here.
    """

    def __init__(self, setting1=1, setting2="some/random/topic", Loadconfigfile="string",**kwargs):
        super(Vlgagent, self).__init__(**kwargs)
        _log.debug("vip_identity: " + self.core.identity)

        self.setting1 = setting1
        self.setting2 = setting2
        self.csvpath  = Loadconfigfile

        self.default_config = {"setting1": setting1,
                               "setting2": setting2,
                              "Loadconfigfile":Loadconfigfile}

        # Set a default configuration to ensure that self.configure is called immediately to setup
        # the agent.
        self.load_groups_consumption={}
        self.vip.config.set_default("config", self.default_config)
        #self.Loads=status.Status_NIRE_D2D(self.csvpath)
        # Hook self.configure up to changes to the configuration file "config".
        self.vip.config.subscribe(self.configure, actions=["NEW", "UPDATE"], pattern="config")

        

    def configure(self, config_name, action, contents):
        """
        Called after the Agent has connected to the message bus. If a configuration exists at startup
        this will be called before onstart.

        Is called every time the configuration in the store changes.
        """
        config = self.default_config.copy()
        config.update(contents)

        print("Configuring Agent")

        try:
            setting1 = int(config["setting1"])
            setting2 = config["setting2"]
            Loadconfigfile=str(config["Loadconfigfile"])
            
        except ValueError as e:
            _log.error("ERROR PROCESSING CONFIGURATION: {}".format(e))
            return

        self.setting1 = setting1
        self.setting2 = setting2
        self.csvpath  = Loadconfigfile

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
                                  callback=self._handle_publish)

    def _handle_publish(self, peer, sender, bus, topic, headers, message):
        """
        Callback triggered by the subscription setup using the topic from the agent's config file
        """
        #print(message)
       # print(message['GLEAMM']['BuildingP'])
        self.Loads.update_actual_load_consumption(message,topic)
        [Threashold,load_consumption,GAMSHourFlag,timesync]=self.Loads.get_actual_load_consumption()
        self.comms.publish_priority_consumption(load_consumption)

        
    def dowork(self):
        #Threashold={1:2700,2:600,3:1000}
        [Threashold,load_consumption,GAMSHourFlag,timesync]=self.Loads.get_actual_load_consumption()
        self.load_groups_consumption=self.load_groups.load_groups(Threashold,load_consumption)
        self.comms.publish_priority_consumption(load_consumption)
        if GAMSHourFlag==1:
           
            self.comms.send_threshold(self.load_groups_consumption,timesync)
            
        print("I am VLG agent",'##############################',type(self.load_groups_consumption))
        
    
        
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
        #self.vip.pubsub.publish('pubsub', "some/random/topic", message="HI!")
        
        self.Loads=status.Status_GLEAM_D2D(self.csvpath,self.vip)
        self.load_groups=VLG.VLG_GLEAMM()
        self.comms=Interface.Interface_GLEAMM(self.vip)
        [Threashold,load_consumption,GAMSHourFlag,timesync]=self.Loads.get_actual_load_consumption()
        self.load_groups_consumption=self.load_groups.load_groups(Threashold,load_consumption)
        self.comms.publish_priority_consumption(load_consumption)
        self.comms.send_threshold(self.load_groups_consumption,timesync)
        self.core.periodic(10,self.dowork)
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
    utils.vip_main(vLGAgent, 
                   version=__version__)


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
