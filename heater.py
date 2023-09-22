import appdaemon.plugins.hass.hassapi as hass

class Heater():
    def __init__(self, api: hass.Hass, id: str):
        self.api = api
        self.id = id
        state = self.api.get_state(self.id)
        self.api.log('Heater with id {0} has state: {1}'.format(self.id, state))
        return

    def turn_on(self):
        if self.is_on():
            self.api.log('Skipped turning on Heater with id {0} because it\'s already on!'.format(self.id))
            return
        self.api.turn_on(self.id)
        self.api.log('Turned on Heater with id {0}'.format(self.id))
        return
    
    def turn_off(self):
        if not self.is_on():
            self.api.log('Skipped turning off Heater with id {0} because it\'s already off!'.format(self.id))
            return
        self.api.turn_off(self.id)
        self.api.log('Turned off Heater with id {0}'.format(self.id))
        return

    def is_on(self):
        state = self.api.get_state(self.id)
        return state != None and state != 'off'
