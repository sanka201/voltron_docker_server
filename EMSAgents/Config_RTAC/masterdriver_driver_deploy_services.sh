#vctl config store platform.driver devices/OPAL_RT/Building104 /home/pi/Config/Building104.config --json
#vctl config store platform.driver devices/OPAL_RT/Building105 /home/pi/Config/Building105.config --json
#vctl config store platform.driver devices/OPAL_RT/Building106 /home/pi/Config/Building106.config --json
vctl config store platform.driver devices/RTAC ~/Config_RTAC/RTAC.config --json
#vctl config store platform.driver devices/OPAL_RT/Building106 /home/pi/Config/Building106.config --json
vctl config store platform.driver devices/RTACHR ~/Config_RTAC/RTACHR.config --json

#vctl config store platform.driver devices/Building540/Bay_area/solaredge86 /home/pi/Config/solaredge86.config --json
#volttron-ctl config store platform.driver registry_configs/points.csv /home/pi/Config/points.csv --csv
#volttron-ctl config store platform.driver registry_configs/outbackpoints.csv /home/pi/Config/outbackpoints.csv --csv
#volttron-ctl config store platform.driver registry_configs/Building104.csv /home/pi/Config/Building104.csv --csv
#volttron-ctl config store platform.driver registry_configs/Building105.csv /home/pi/Config/Building105.csv --csv
#volttron-ctl config store platform.driver registry_configs/Building106.csv /home/pi/Config/Building106.csv --csv

volttron-ctl config store platform.driver registry_configs/RTAC.csv ~/Config_RTAC/RTAC.csv --csv
volttron-ctl config store platform.driver registry_configs/RTACHR.csv ~/Config_RTAC/RTACHR.csv --csv

