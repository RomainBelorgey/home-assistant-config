import appdaemon.plugins.hass.hassapi as hass

class Heaters(hass.Hass):

    def initialize(self):
        #switchs
        self.listen_state(self.set_fil_pilote, 'switch.fil_pilote_living_room_1', duration = 5)
        self.listen_state(self.set_fil_pilote, 'switch.fil_pilote_living_room_2', duration = 5)
        self.listen_state(self.set_fil_pilote, 'switch.fil_pilote_kitchen_1', duration = 5)
        self.listen_state(self.set_fil_pilote, 'switch.fil_pilote_kitchen_2', duration = 5)
        self.listen_state(self.set_fil_pilote, 'switch.fil_pilote_office_1', duration = 5)
        self.listen_state(self.set_fil_pilote, 'switch.fil_pilote_office_2', duration = 5)
        self.listen_state(self.set_fil_pilote, 'switch.fil_pilote_bedroom_1', duration = 5)
        self.listen_state(self.set_fil_pilote, 'switch.fil_pilote_bedroom_2', duration = 5)

        #Input select
        self.listen_state(self.set_switchs, 'input_select.heater_living_room', duration = 2)
        self.listen_state(self.set_switchs, 'input_select.heater_kitchen', duration = 2)
        self.listen_state(self.set_switchs, 'input_select.heater_office', duration = 2)
        self.listen_state(self.set_switchs, 'input_select.heater_bedroom', duration = 2)

    def set_fil_pilote(self, entity, attribute, old, new, kwars):
        part = entity.split('_')
        room = part[2]
        if room == 'living':
            room = 'living_room'
        #Get states
        state1 = self.get_state("switch.fil_pilote_"+room+"_1")
        state2 = self.get_state("switch.fil_pilote_"+room+"_2")
        if state1 == "on" and state2 == "off":
            state_input = "Arret"
        elif state1 == "on" and state2 == "on":
            state_input = "Eco"
        elif state1 == "off" and state2 == "off":
            state_input = "Confort"
        elif state1 == "off" and state2 == "on":
            state_input = "Hors Gel"
        self.set_state("input_select.heater_"+room, state = state_input)
        self.log("Change input select "+room+" to "+state_input)

    def set_switchs(self, entity, attribute, old, new, kwars):
        part = entity.split('_')
        room = part[2]
        if room == 'living':
            room = 'living_room'
        #Set switchs
        if new == "Arret":
            self.turn_on("switch.fil_pilote_"+room+"_1")
            self.turn_off("switch.fil_pilote_"+room+"_2")
        elif new == "Eco":
            self.turn_on("switch.fil_pilote_"+room+"_1")
            self.turn_on("switch.fil_pilote_"+room+"_2")
        elif new == "Confort":
            self.turn_off("switch.fil_pilote_"+room+"_1")
            self.turn_off("switch.fil_pilote_"+room+"_2")
        elif new == "Hors Gel":
            self.turn_off("switch.fil_pilote_"+room+"_1")
            self.turn_on("switch.fil_pilote_"+room+"_2")
        self.log("Change switchs for "+room)