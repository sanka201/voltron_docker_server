from datetime import datetime
import os
import sys
import time
import random


import gevent
import logging
from gevent.core import callback
from gevent import Timeout


from volttron.platform.messaging import headers as headers_mod
from volttron.platform.vip.agent import Agent, PubSub, Core
from volttron.platform.agent import utils

# Log warnings and errors to make the node red log less chatty
utils.setup_logging(level=logging.WARNING)
_log = logging.getLogger(__name__)

# These are the options that can be set from the settings module.
from Django_setting import agent_kwargs

''' takes two arguments.  Firist is topic to publish under.  Second is message. '''
if  __name__ == '__main__':
    try:
        # If stdout is a pipe, re-open it line buffered
        if utils.isapipe(sys.stdout):
            # Hold a reference to the previous file object so it doesn't
            # get garbage collected and close the underlying descriptor.
            stdout = sys.stdout
            sys.stdout = os.fdopen(stdout.fileno(), 'w', 1)

        agent = Agent(identity='DjangoPublisher', **agent_kwargs)
        now = utils.format_timestamp(datetime.utcnow())
        utcnow = utils.get_aware_utc_now()
        header = {
        #    headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            "Date": utils.format_timestamp(utcnow),
            "TimeStamp":utils.format_timestamp(utcnow)
        }
        Message= [{"P": random.randint(0,100),"Q":random.randint(0,100),"R":random.randint(0,100)},{"P":{'units': 'F', 'tz': 'UTC', 'type': 'float'},"Q":{'units': 'F', 'tz': 'UTC', 'type': 'float'},"R":{'units': 'F', 'tz': 'UTC', 'type': 'float'}}]
        
        event = gevent.event.Event()
        task = gevent.spawn(agent.core.run, event)
        with gevent.Timeout(10):
            event.wait()

        try:
#	   topics=['devices/control/BEMS_1/plc/sheddin']
#	   for x in range(1, 19):
#         	Message= [{"P": random.randint(0,100),"Q":random.randint(0,100),"R":random.randint(0,100)},{"P":{'units': 'F', 'tz': 'UTC', 'type': 'float'},"Q":{'units': 'F', 'tz': 'UTC', 'type': 'float'},"R":{'units': 'F', 'tz': 'UTC', 'type': 'float'}}]
	#	topics='devices/control/BEMS_'+str(x)+'/plc/sheddin'
#                topics='dataconcentrator/devices/Monitor/Campus1/Benshee1/BEMS_'+str(x)
#
#		result = agent.vip.pubsub.publish(peer='pubsub',topic=topics,headers=header, message=Message)
#		time.sleep(.5)
#                topics='control/plc/shedding'
#		result = agent.vip.pubsub.publish(peer='pubsub',topic=topics,headers=header, message=1000)
#		print('turning on building',x,'with the topic : ',topics)
           time.sleep(2)
##           topics='control/plc/shedding'
           Message= {"Threashhold": 7500,"Q":random.randint(0,100)},
#           topics='devices/control/BEMS_1/plc/shedding'

           topics='control/plc/increment'
#	   topics='devices/Centralcontrol/Control/PeakShaver/'
#           result = agent.vip.pubsub.publish(peer='pubsub',topic=topics,headers=header, message=0)
 
          # for x in range(1, 19):
         #       topics='dataconcentrator/devices/Monitor/Campus1/Benshee1/BEMS_'+str(x)
         #       result = agent.vip.pubsub.publish(peer='pubsub',topic=topics,headers=header, message=Message)
         #       time.sleep(1)
         #       result = agent.vip.pubsub.publish(peer='pubsub',topic=topics,headers=header, message=Message)
         #       print('turning off building',x,'with the topic : ',topics)
         #       time.sleep(2)
           print("enter the message")
# 	   Message=list(input())
           val= input()
#	   Message=1000
#           Message= {"Threashhold":int(Message) ,"Q":random.randint(0,100)}
#           result = agent.vip.pubsub.publish(peer='pubsub',topic= 'devices/loadshedule/current',headers=header, message=int(Message))
# 	   result = agent.vip.pubsub.publish(peer='pubsub',topic= 'dataconcentrator/devices/Campus1/Benshee1/BEMS_1/',headers=header, message=0)
#           result = agent.vip.pubsub.publish(peer='pubsub',topic= 'control/plc/increment',headers=header, message=Message)
          # result = agent.vip.pubsub.publish(peer='pubsub',topic= 'control/plc/NIRE_ALPHA_cc_1/increment',headers=header, message=Message)
#           result = agent.vip.pubsub.publish(peer='pubsub',topic= 'control/plc/NIRE_ALPHA_cc_1/directcontrol',headers=header, message=[0,Message])
           result = agent.vip.pubsub.publish(peer='pubsub',topic= 'control/plc/NIRE_ALPHA_cc_1/PeakShaver',headers=header, message=[{"Threashhold":int(val)}])
#           result = agent.vip.pubsub.publish(peer='pubsub',topic= 'devices/Centralcontrol/Control/PriorityControl',headers=header, message=Message)
#           result=agent.vip.rpc.call('platform.driver','set_point', 'building540/NIRE_ALPHA_cc_1/w3' ,'status',Message)
#           result=agent.vip.rpc.call('platform.driver','set_point', 'building540/NIRE_ALPHA_cc_1/w2' ,'status',Message)
#           result=agent.vip.rpc.call('platform.driver','set_point', 'building540/NIRE_ALPHA_cc_1/w4' ,'status',Message)
#           result=agent.vip.rpc.call('platform.driver','set_point', 'building540/NIRE_ALPHA_cc_1/w6' ,'status',Message)
#           result=agent.vip.rpc.call('platform.driver','set_point', 'building540/NIRE_ALPHA_cc_1/w14' ,'status',Message)
#           result=agent.vip.rpc.call('platform.driver','set_point', 'building540/NIRE_ALPHA_cc_1/w19' ,'status',Message)

#	   result=agent.vip.rpc.call('LoadProrityAgentagent-0.1_1','load_consumption').get(timeout=20)
#	    result=agent.vip.rpc.call('platform.driver','get_point', 'devices/campus/building/fake' ,'EKG',external_platform='volttron')
#	    result=agent.vip.rpc.call('bEMSminitoragent-0.1_1','set_BEMS','platform.driver', 'devices/campus/building/fake' ,'EKG',1,'BEMS_1',external_platform='ESTCP_DATACONCENTRATOR_1')
	   # result=agent.vip.rpc.call('platform.driver','scrape_all','acquisition/loads/building2/Wp-59-L',external_platform='Wemo_cc_2')
           print("dooooo",result)
        finally:
            task.kill()
    except KeyboardInterrupt:
        pass
#set_BEMS(self,agent,topic,pointname,message,BEMS,kwarg1=None, kwarg2=None):
