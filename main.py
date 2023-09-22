import appdaemon.plugins.hass.hassapi as hass
import datetime
from zone import Zone
from heat_modes import HeatMode

class VirtualThermostat(hass.Hass):
    def initialize(self):
        self.log('Initializing VirtualThermostat...')
        self.mode = HeatMode(self.args['heat_mode'])
        self.log('Found HeatMode {0}!'.format(self.mode))
        self.interval = self.args['poll_interval_seconds']
        self.log('Found Poll Interval of {0} seconds!'.format(self.interval))
        self.zones = []
        for zone in self.args['zones']:
            name = zone['name']
            sensors = zone['sensors']
            heaters = zone['heaters']
            coolers = zone['coolers']
            target_temp_id = zone['target_temp']
            zone_instance = Zone(self, name, self.mode, sensors, heaters, coolers, target_temp_id)
            self.log('Zone {0} setup is complete.'.format(name))
            self.zones.append(zone_instance)
            zone_instance.setup_zone()
        self.run_every(self.check_all_zones, "now", self.interval)
        self.log('Initialization of the VirtualThermostat is complete!')
        return
    
    def terminate(self):
        self.log('Terminating VirtualThermostat...')
        return

    def check_all_zones(self, cb_args):
        self.log('Checking all zones...')
        for zone in self.zones:
            zone.check_temperature()
        return
