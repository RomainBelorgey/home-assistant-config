import appdaemon.plugins.hass.hassapi as hass
import datetime
import time

class WasherSensor(hass.Hass):

    timestamp_change = time.time()
    new_state = ''

    def initialize(self):
        global timestamp_change
        timestamp_change = time.time()
        global new_state
        self.listen_state(self.change_sensor, 'switch.switch_washer', attribute = 'current_power_w')
        new_state = self.get_state("sensor.washer")

    def change_sensor(self, entity, attribute, old, new, kwargs):
        global timestamp_change
        global new_state
        current_state = self.get_state("sensor.washer")

        if new == None:
            new_state2 = 'off'
        elif new < 0.6:
            new_state2 = 'off'
        elif new < 2:
            new_state2 = 'on'
        elif new < 6:
            new_state2 = 'prog'
        elif new >= 6:
            new_state2 = 'wash'
        else:
            new_state2 = 'unknown'
        if new_state != new_state2:
            new_state = new_state2
            self.log(new_state)
            timestamp_change = time.time()
            self.log("Change time")
        if new_state != current_state:
            if (time.time() - timestamp_change) > 90:
                self.log("Change state")
                status = self.set_state("sensor.washer", state = new_state)
