import appdaemon.plugins.hass.hassapi as hass

class Cooler():
    def __init__(self, api: hass.Hass, id: str):
        self.api = api
        self.id = id
        return

    def turn_on(self):
        if self.is_on():
            self.api.log('Skipped turning on Cooler with id {0} because it\'s already on!'.format(self.id))
            return
        self.api.turn_on(self.id)
        self.api.log('Turned on Cooler with id {0}'.format(self.id))
        return
    
    def turn_off(self):
        if not self.is_on():
            self.api.log('Skipped turning off Cooler with id {0} because it\'s already off!'.format(self.id))
            return
        self.api.turn_off(self.id)
        self.api.log('Turned off Cooler with id {0}'.format(self.id))
        return
        

    def is_on(self):
        state = self.api.get_state(self.id)
        return state != None and state != 'off'
