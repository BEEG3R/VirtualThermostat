import appdaemon.plugins.hass.hassapi as hass

class Sensor():
    def __init__(self, api: hass.Hass, id: str):
        self.api = api
        self.id = id
        self.current_temp = 0
        self.api.listen_state(self.on_temperature_change, self.id)
        return
    
    def on_temperature_change(self, entity, attribute, old, new, kwargs):
        self.current_temp = new
        self.api.log('Sensor with id {0} has current temperature of {1}'.format(self.id, self.current_temp))
        return

    def get_current_temp(self) -> float:
        if self.current_temp != 0:
            return self.current_temp
        return float(self.api.get_state(self.id))
