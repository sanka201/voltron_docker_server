
vctl stop --tag MasterDriver

vctl remove --tag MasterDriver

python scripts/install-agent.py -s services/core/PlatformDriverAgent -c services/core/PlatformDriverAgent/platform-driver.agent -t MasterDriver
vctl config store platform.driver registry_configs/csv_reg.csv ~/volttron/Config2/csv_reg.csv --csv 

#vctl config delete platform.driver devices/wemo/w1
#vctl config delete platform.driver devices/wemo/w2
#vctl config delete platform.driver devices/wemo/w3
#vctl config delete platform.driver devices/wemo/w4
#vctl config delete platform.driver devices/wemo/w5
#vctl config delete platform.driver devices/wemo/w6
#vctl config delete platform.driver devices/wemo/w7
#vctl config delete platform.driver devices/wemo/w8
#vctl config delete platform.driver devices/wemo/w9
#vctl config delete platform.driver devices/wemo/w10
#vctl config delete platform.driver  devices/building540/NIRE_WeMo_cc_1/w16
#vctl config delete platform.driver  devices/building540/NIRE_WeMo_cc_1/w17
#vctl config delete platform.driver  devices/building540/NIRE_WeMo_cc_1/w18
#vctl config delete platform.driver  devices/building540/NIRE_WeMo_cc_1/w19
#vctl config delete platform.driver  devices/building540/NIRE_WeMo_cc_1/w20 
#vctl config delete platform.driver  devices/building540/NIRE_WeMo_cc_1/w21
#vctl config delete platform.driver  devices/building540/NIRE_WeMo_cc_1/w22
#vctl config delete platform.driver  devices/building540/NIRE_WeMo_cc_1/w23
#vctl config delete platform.driver  devices/building540/NIRE_WeMo_cc_1/w24
#vctl config delete platform.driver  devices/building540/NIRE_WeMo_cc_1/w25
#vctl config delete platform.driver  devices/building540/NIRE_WeMo_cc_1/w26
#vctl config delete platform.driver  devices/building540/NIRE_WeMo_cc_1/w27
#vctl config delete platform.driver  devices/building540/NIRE_WeMo_cc_1/w28
#vctl config delete platform.driver  devices/building540/NIRE_WeMo_cc_1/w29		
for i in {1..29}
do
    vctl config delete platform.driver devices/building540/NIRE_WeMo_cc_1/w$i
done

vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w1 ~/volttron/Config2/wemo_driver26.config
vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w2 ~/volttron/Config2/wemo_driver33.config
vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w3 ~/volttron/Config2/wemo_driver12.config
vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w4 ~/volttron/Config2/wemo_driver32.config
vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w5 ~/volttron/Config2/wemo_driver20.config
vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w6 ~/volttron/Config2/wemo_driver30.config
vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w7 ~/volttron/Config2/wemo_driver24.config
vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w8 ~/volttron/Config2/wemo_driver43.config
vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w9 ~/volttron/Config2/wemo_driver11.config
vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w10 ~/volttron/Config2/wemo_driver29.config
vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w11 ~/volttron/Config2/wemo_driver18.config
vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w12 ~/volttron/Config2/wemo_driver10.config
vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w13 ~/volttron/Config2/wemo_driver50.config
vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w14 ~/volttron/Config2/wemo_driver25.config
vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w15 ~/volttron/Config2/wemo_driver42.config
vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w16 ~/volttron/Config2/wemo_driver19.config
vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w17 ~/volttron/Config2/wemo_driver37.config
#vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w18 ~/volttron/Config2/wemo_driver18.config
#vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w19 ~/volttron/Config2/wemo_driver19.config
#vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w20 ~/volttron/Config2/wemo_driver15.config
#vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w21 ~/volttron/Config2/wemo_driver43.config
#vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w22 ~/volttron/Config2/wemo_driver16.config
#vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w23 ~/volttron/Config2/wemo_driver28.config
#vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w24 ~/volttron/Config2/wemo_driver30.config
#vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w25 ~/volttron/Config2/wemo_driver31.config
#vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w26 ~/volttron/Config2/wemo_driver34.config
#vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w27 ~/volttron/Config2/wemo_driver38.config
#vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w28 ~/volttron/Config2/wemo_driver44.config
#vctl config store platform.driver devices/building540/NIRE_WeMo_cc_1/w29 ~/volttron/Config2/wemo_driver48.config


vctl start --tag MasterDriver
