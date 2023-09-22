import appdaemon.plugins.hass.hassapi as hass

class Sensor():
    def __init__(self, api: hass.Hass, id: str):
        self.api = api
        self.id = id
        self.value = 0
        self.api.listen_state(self.on_temperature_change, self.id)
        return
    
    def on_temperature_change(self, entity, attribute, old, new, kwargs):
        self.value = new
        self.api.log('Sensor with id {0} has current temperature of {1}'.format(self.id, self.value))
        return

    def get_current_value(self) -> float:
        if self.value != 0:
            return self.value
        return float(self.api.get_state(self.id))
