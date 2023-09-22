import appdaemon.plugins.hass.hassapi as hass
from heat_modes import HeatMode
from sensor import Sensor
from heater import Heater
from cooler import Cooler

class Zone():
    def __init__(self, api: hass.Hass, name: str, mode: HeatMode, sensors, heaters, coolers, target_temp_id):
        self.api = api
        self.name = name
        self.mode = mode
        self.sensor_ids = sensors
        self.heater_ids = heaters
        self.cooler_ids = coolers
        self.target_temp_id = target_temp_id

        self.sensors = []
        self.heaters = []
        self.coolers = []
        self.target_temp_sensor = None
        return

    def setup_zone(self):
        self.setup_sensors()
        self.setup_heaters()
        self.setup_coolers()
        self.setup_target_temp()
        return

    def setup_sensors(self):
        for id in self.sensor_ids:
            instance = Sensor(self.api, id)
            self.sensors.append(instance)
            self.api.log('Zone {0} sensor id {1}'.format(self.name, id))
        return

    def setup_heaters(self):
        for id in self.heater_ids:
            instance = Heater(self.api, id)
            self.heaters.append(instance)
            self.api.log('Zone {0} heater id {1}'.format(self.name, id))
        return
    
    def setup_coolers(self):
        for id in self.cooler_ids:
            instance = Cooler(self.api, id)
            self.coolers.append(instance)
            self.api.log('Zone {0} cooler id {1}'.format(self.name, id))
        return

    def setup_target_temp(self):
        self.target_temp_sensor = Sensor(self.api, self.target_temp_id)
        return

    def check_temperature(self):
        self.api.log('Checking temperature of {0}'.format(self.name))
        target_temp = float(self.target_temp_sensor.get_current_temp())
        sum = 0
        for sensor in self.sensors:
            sum += sensor.get_current_temp()
        average = sum / len(self.sensors)
        self.api.log('Zone {0} has average temp of {1} where target temp is {2}.'.format(self.name, average, target_temp))
        if average < target_temp:
            # turn on the heat, or turn the AC off if the current heat mode allows for it
            if self.mode == HeatMode.HEAT or self.mode == HeatMode.HEATCOOL:
                self.toggle_heaters(True)
            if self.mode == HeatMode.COOL or self.mode == HeatMode.HEATCOOL:
                self.toggle_coolers(False)
        if average > target_temp:
            # turn on the AC, or turn off the heat if the current heat mode allows for it
            if self.mode == HeatMode.HEAT or self.mode == HeatMode.HEATCOOL:
                self.toggle_heaters(False)
            if self.mode == HeatMode.COOL or self.mode == HeatMode.HEATCOOL:
                self.toggle_coolers(True)
        return

    def toggle_heaters(self, enabled: bool):
        self.api.log('Zone {0} is {1} the target temperature. Turning {2} all heaters in this zone.'.format(self.name, 'below' if enabled else 'above', 'on' if enabled else 'off'))
        for heater in self.heaters:
            if enabled:
                heater.turn_on()
                continue
            heater.turn_off()
        return

    def toggle_coolers(self, enabled: bool):
        self.api.log('Zone {0} is {1} the target temperature. Turning {2} all coolers in this zone.'.format(self.name, 'above' if enabled else 'below', 'off' if enabled else 'on'))
        for cooler in self.coolers:
            if enabled:
                cooler.turn_on()
                continue
            cooler.turn_off()
        return
