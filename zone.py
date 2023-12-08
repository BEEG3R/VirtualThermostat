import appdaemon.plugins.hass.hassapi as hass
from heat_modes import HeatMode
from sensor import Sensor
from heater import Heater
from cooler import Cooler

class Zone():
    def __init__(self, api: hass.Hass, name: str, heat_mode_sensor: Sensor, sensors, heaters, coolers, target_temp_id: str):
        self.api = api
        self.name = name
        self.heat_mode_sensor = heat_mode_sensor
        self.sensor_ids = sensors
        self.heater_ids = heaters
        self.cooler_ids = coolers
        self.target_temp_id = target_temp_id

        self.sensors = []
        self.heaters = []
        self.coolers = []
        # treat the target temperature as a sensor, so that we get real-time updates
        # when it's value changes, but can also read it's value at any time.
        self.target_temp_sensor = None
        return

    def setup_zone(self):
        self.api.log('Zone {0} setup starting...'.format(self.name))
        self.setup_sensors()
        self.setup_heaters()
        self.setup_coolers()
        self.setup_target_temp()
        self.api.log('Zone {0} setup is complete.'.format(self.name))
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

    def get_current_heat_mode(self) -> HeatMode:
        current_value = self.heat_mode_sensor.get_current_value()
        return HeatMode(current_value)

    def check_temperature(self):
        '''
        Main logic loop to determine if a heater or cooler needs to be turned on.
        This averages the temperature of all temp sensors in the zone, compares that
        average to the target temperature specified in Home Assistant, and based on the
        heating mode, toggles a heater or cooler to bring the sensor readings up to 
        (or down to) the target temperature.
        '''
        mode = self.get_current_heat_mode()
        if not self.should_continue_temp_check(mode):
            self.api.log('Current Heat Mode is {0}. Skipping {1} temperature check.'.format(mode, self.name))
            return
        target_temp = float(self.target_temp_sensor.get_current_value())
        sum = 0
        sensor_count = 0
        for sensor in self.sensors:
            try:
                sum += float(sensor.get_current_value())
                sensor_count += 1 
            except:
                self.api.log('Could not read current value from sensor {0}'.format(sensor.id))
        average = sum / max(sensor_count, 1)
        self.api.log('{0} has an average temp of {1} where target temp is {2}.'.format(self.name, average, target_temp))
        if average < target_temp:
            # turn on the heat, or turn the AC off if the current heat mode allows for it
            if mode == HeatMode.HEAT or mode == HeatMode.HEATCOOL:
                self.toggle_heaters(True)
            if mode == HeatMode.COOL or mode == HeatMode.HEATCOOL:
                self.toggle_coolers(False)
        if average > target_temp:
            # turn on the AC, or turn off the heat if the current heat mode allows for it
            if mode == HeatMode.HEAT or mode == HeatMode.HEATCOOL:
                self.toggle_heaters(False)
            if mode == HeatMode.COOL or mode == HeatMode.HEATCOOL:
                self.toggle_coolers(True)
        return

    def toggle_heaters(self, enabled: bool):
        self.api.log('{0} is {1} the target temperature. Turning {2} all heaters in this zone.'.format(self.name, 'below' if enabled else 'above', 'on' if enabled else 'off'))
        for heater in self.heaters:
            if enabled:
                heater.turn_on()
                continue
            heater.turn_off()
        return

    def toggle_coolers(self, enabled: bool):
        self.api.log('{0} is {1} the target temperature. Turning {2} all coolers in this zone.'.format(self.name, 'above' if enabled else 'below', 'on' if enabled else 'off'))
        for cooler in self.coolers:
            if enabled:
                cooler.turn_on()
                continue
            cooler.turn_off()
        return

    def should_continue_temp_check(self, current_heat_mode: HeatMode) -> bool:
        if current_heat_mode == HeatMode.OFF:
            self.toggle_heaters(False)
            self.toggle_coolers(False)
            return False
        if current_heat_mode == HeatMode.HEAT:
            self.toggle_coolers(False)
        if current_heat_mode == HeatMode.COOL:
            self.toggle_heaters(False)
        return True
