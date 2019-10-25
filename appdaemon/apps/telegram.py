import appdaemon.plugins.hass.hassapi as hass
import time

class TelegramBotEventListener(hass.Hass):
    "Event listener for Telegram bot events."

    def initialize(self):
        """Listen to Telegram Bot events of interest."""
        self.listen_event(self.receive_telegram_text, 'telegram_text')
        self.listen_event(self.receive_telegram_callback, 'telegram_callback')
        self.listen_event(self.receive_telegram_command, 'telegram_command')

    def receive_telegram_command(self, event_id, payload_event, *args):
        assert event_id == 'telegram_command'
        command = payload_event['command']
        args = payload_event['args']
        user_id = payload_event['user_id']
        #Heaters command
        if command == "/heaters":
            state_winter = self.get_state("input_boolean.winter_mode")
            state_bedroom = self.get_state("input_select.heater_bedroom")
            state_living_room = self.get_state("input_select.heater_living_room")
            state_hall = self.get_state("input_select.heater_hall")
            if state_winter =='on':
                msg = 'Winter mode is on'
                keyboard = [[("Modify the status", "/heaters_modify"),("Reset to default state", "/heaters_reset")]]
            else:
                msg = 'Winter mode is off\n\n*No automation activated\nBe sure to stop heaters afterwards !!\n*'
                keyboard = [[("Modify the status", "/heaters_modify")]]
            msg = msg+'\nHall: '+state_hall+'\nLiving room: '+state_living_room+'\nBedroom: '+state_bedroom
            self.call_service('telegram_bot/send_message',
                              title='*Heaters status*',
                              target=user_id,
                              message=msg,
                              disable_notification=True,
                              inline_keyboard=keyboard)
        #winter command
        if command == "/winter":
            self.command_basic("winter_mode", "input_boolean.winter_mode", user_id)
        #kodi command
        if command == "/kodi":
            self.command_basic("kodi", "media_player.kodi", user_id)
        #filter command
        if command == "/filter":
            self.command_basic("filter", "fan.xiaomi_miio_device", user_id)
        #vacuum command
        if command == "/vacuum":
            component='vacuum'
            entity_id="vacuum.xiaomi_vacuum_cleaner"
            title='*'+component.title()+'*'
            state = self.get_state(entity_id)
            msg = 'Robot '+state
            if state == 'docked':
                keyboard = [[("Start cleaning", "/"+component+"_start")]]
            elif state == 'paused':
                keyboard = [[("Start cleaning", "/"+component+"_start")],[("Stop robot (will return to dock)", "/"+component+"_stop")]]
            else:
                keyboard = [[("Pause robot", "/"+component+"_pause")],[("Stop robot (will return to dock)", "/"+component+"_stop")]]
            self.call_service('telegram_bot/send_message',
                              title=title,
                              target=user_id,
                              message=msg,
                              disable_notification=True,
                              inline_keyboard=keyboard)

    def command_basic(self, component, entity_id, user_id):
        title='*'+component.title()+'*'
        state = self.get_state(entity_id)
        if state == 'on':
            msg = component.replace("_", " ").title()+' is on'
            keyboard = [[("Stop "+component, "/"+component+"_off")]]
        elif state == 'off':
            msg = component.replace("_", " ").title()+' is off'
            keyboard = [[("Start "+component, "/"+component+"_on")]]
        else:
            msg = component.replace("_", " ").title()+' is '+state
            keyboard = [[("Stop "+component, "/"+component+"_off")]]
        self.call_service('telegram_bot/send_message',
                          title=title,
                          target=user_id,
                          message=msg,
                          disable_notification=True,
                          inline_keyboard=keyboard)


    def receive_telegram_text(self, event_id, payload_event, *args):
        """Text repeater."""
        assert event_id == 'telegram_text'
        user_id = payload_event['user_id']
        msg = 'You said: ``` %s ```' % payload_event['text']
        keyboard = [[("Edit message", "/edit_msg"),
                     ("Don't", "/do_nothing")],
                    [("Remove this button", "/remove button")]]
        self.call_service('telegram_bot/send_message',
                          title='*Dumb automation*',
                          target=user_id,
                          message=msg,
                          disable_notification=True,
                          inline_keyboard=keyboard)

    def receive_telegram_callback(self, event_id, payload_event, *args):
        """Event listener for Telegram callback queries."""
        assert event_id == 'telegram_callback'
        data_callback = payload_event['data']
        callback_id = payload_event['id']
        chat_id = payload_event['chat_id']
        user_id = payload_event['user_id']
        msg_id = payload_event['message']['message_id']
        # keyboard = ["Edit message:/edit_msg, Don't:/do_nothing",
        #             "Remove this button:/remove button"]
        keyboard = [[("Edit message", "/edit_msg"),
                     ("Don't", "/do_nothing")],
                    [("Remove this button", "/remove button")]]

        #Modify heater step1
        if data_callback == "/heaters_modify":
            msg = 'Please select a room:'
            keyboard = [[("Living Room", "/heater_room_livingroom"), ("Bedroom", "/heater_room_bedroom"), ("Hall", "/heater_room_hall")],
                        [("All heaters", "/heater_room_all")]]
            self.call_service('telegram_bot/edit_replymarkup',
                              chat_id=chat_id,
                              message_id='last',
                              inline_keyboard=[])
            self.call_service('telegram_bot/send_message',
                              title='*Modifying heater status*',
                              target=user_id,
                              message=msg,
                              disable_notification=True,
                              inline_keyboard=keyboard)

        #Modify heater step2
        if data_callback.startswith("/heater_room"):
            args = data_callback.split("_")
            heater = args[2]
            msg = 'Please select a status:'
            keyboard = [[("Eco", "/heater_status_eco_"+heater), ("Confort", "/heater_status_confort_"+heater), ("Hors Gel", "/heater_status_horsgel_"+heater)],
                        [("Arret", "/heater_status_arret_"+heater)]]
            self.call_service('telegram_bot/edit_message',
                              chat_id=chat_id,
                              message_id=msg_id,
                              title='*Modifying heater status*',
                              message=msg,
                              inline_keyboard=keyboard)

        #Modify heater step3 (final step)
        if data_callback.startswith("/heater_status"):
            args = data_callback.split("_")
            heater = args[3]
            status = args[2]
            if status == 'eco':
                status = 'Eco'
            if status == 'confort':
                status = 'Confort'
            if status == 'arret':
                status = 'Arret'
            if status == 'horsgel':
                status = 'Hors Gel'
            if heater == 'livingroom':
                heater = 'living_room'
            input_select = 'input_select.heater_'+heater
            msg = 'Heater '+heater+' on '+status
            if heater == 'all':
                input_select = 'input_select.all_heaters'
                msg = 'All heaters on '+status
            self.select_option(input_select, status)
            self.call_service('telegram_bot/edit_message',
                              chat_id=chat_id,
                              message_id=msg_id,
                              title='*Modifying heater status*',
                              message=msg,
                              inline_keyboard=[])

        #reset to default state
        if data_callback == '/heaters_reset':
            self.call_service('telegram_bot/edit_message',
                              chat_id=chat_id,
                              message_id='last',
                              title='*Modifying heater status*',
                              message="Reseting ...",
                              inline_keyboard=[])
            self.turn_off("input_boolean.run_heaters_automations")
            time.sleep(1)
            self.turn_on("input_boolean.run_heaters_automations")
            title='*Winter mode reactivated*'
            time.sleep(10)
            state_athome = self.get_state("input_boolean.at_home")
            msg = '\n*Resetting to default state*'
            if state_athome =='on':
                msg = msg+'\nAt home scenario'
            else:
                msg = msg+'\nNot at home scenario'
            state_bedroom = self.get_state("input_select.heater_bedroom")
            state_living_room = self.get_state("input_select.heater_living_room")
            state_hall = self.get_state("input_select.heater_hall")
            msg = msg + '\nHall: '+state_hall+'\nLiving room: '+state_living_room+'\nBedroom: '+state_bedroom
            self.call_service('telegram_bot/edit_message',
                              chat_id=chat_id,
                              message_id='last',
                              title='*Modifying heater status*',
                              message=msg,
                              inline_keyboard=[])

        #Filter
        if data_callback == '/filter_on':
            self.turn_on("fan.xiaomi_miio_device")
            self.call_service('telegram_bot/edit_message',
                              chat_id=chat_id,
                              message_id='last',
                              title="*Filter*",
                              message="Filter is now on",
                              inline_keyboard=[])
        if data_callback == '/filter_off':
            self.turn_off("fan.xiaomi_miio_device")
            self.call_service('telegram_bot/edit_message',
                              chat_id=chat_id,
                              message_id='last',
                              title="*Filter*",
                              message="Filter is now off",
                              inline_keyboard=[])
        #Kodi
        if data_callback == '/kodi_on':
            self.turn_on("media_player.kodi")
            state = self.get_state("media_player.kodi")
            self.call_service('telegram_bot/edit_message',
                              chat_id=chat_id,
                              message_id='last',
                              title="*Kodi*",
                              message="Starting ...",
                              inline_keyboard=[])
            maxLoop = 30
            loop = 0
            while state == "off" and loop < maxLoop:
                time.sleep(2)
                loop=loop+1
                state = self.get_state("media_player.kodi")
            self.call_service('telegram_bot/edit_message',
                              chat_id=chat_id,
                              message_id='last',
                              title="*Kodi*",
                              message="Kodi is now on",
                              inline_keyboard=[])

        if data_callback == '/kodi_off':
            self.turn_off("media_player.kodi")
            state = self.get_state("media_player.kodi")
            self.call_service('telegram_bot/edit_message',
                              chat_id=chat_id,
                              message_id='last',
                              title="*Kodi*",
                              message="Stopping ...",
                              inline_keyboard=[])
            maxLoop = 30
            loop = 0
            while state != "off" and loop < maxLoop:
                time.sleep(2)
                loop=loop+1
                state = self.get_state("media_player.kodi")
            self.call_service('telegram_bot/edit_message',
                              chat_id=chat_id,
                              message_id='last',
                              title="*Kodi*",
                              message="Kodi is now off",
                              inline_keyboard=[])
        #Vacuum
        if data_callback == '/vacuum_start':
            self.call_service('vacuum/start',
                              entity_id='vacuum.vacuum_up')
            self.call_service('telegram_bot/edit_message',
                              chat_id=chat_id,
                              message_id='last',
                              title="*Vacuum*",
                              message="Starting ...",
                              inline_keyboard=[])
            maxLoop = 10
            loop = 0
            state = self.get_state("vacuum.vacuum_up")
            while state != "cleaning" and loop < maxLoop:
                time.sleep(2)
                state = self.get_state("vacuum.vacuum_up")
                loop=loop+1
            self.call_service('telegram_bot/edit_message',
                              chat_id=chat_id,
                              message_id='last',
                              title="*Vacuum*",
                              message="Robot "+state,
                              inline_keyboard=[])
        if data_callback == '/vacuum_stop':
            self.call_service('vacuum/return_to_base',
                              entity_id='vacuum.vacuum_up')
            self.call_service('telegram_bot/edit_message',
                              chat_id=chat_id,
                              message_id='last',
                              title="*Vacuum*",
                              message="Going back to the dock ...",
                              inline_keyboard=[])
            maxLoop = 60
            loop = 0
            state = self.get_state("vacuum.vacuum_up")
            while state != "docked" and loop < maxLoop:
                time.sleep(2)
                state = self.get_state("vacuum.vacuum_up")
                loop=loop+1
            self.call_service('telegram_bot/edit_message',
                              chat_id=chat_id,
                              message_id='last',
                              title="*Vacuum*",
                              message="Robot "+state,
                              inline_keyboard=[])
        if data_callback == '/vacuum_pause':
            self.call_service('vacuum/pause',
                              entity_id='vacuum.vacuum_up')
            self.call_service('telegram_bot/edit_message',
                              chat_id=chat_id,
                              message_id='last',
                              title="*Vacuum*",
                              message="Pausing ...",
                              inline_keyboard=[])
            maxLoop = 10
            loop = 0
            state = self.get_state("vacuum.vacuum_up")
            while state != "paused" and loop < maxLoop:
                time.sleep(2)
                state = self.get_state("vacuum.vacuum_up")
                loop=loop+1
            self.call_service('telegram_bot/edit_message',
                              chat_id=chat_id,
                              message_id='last',
                              title="*Vacuum*",
                              message="Robot "+state,
                              inline_keyboard=[])
        if data_callback == '/vacuum_stop_automation':
            self.turn_off("input_boolean.automation_vacuum")
            self.call_service('telegram_bot/edit_message',
                              chat_id=chat_id,
                              message_id='last',
                              title="*Cleaning appartment*",
                              message="Automation stopped. Robot won't start at 10am",
                              inline_keyboard=[])

        #winter
        if data_callback.startswith('/winter_mode'):
            if data_callback == '/winter_mode_on':
                    self.turn_on("input_boolean.winter_mode")
                    self.call_service('telegram_bot/edit_message',
                                      chat_id=chat_id,
                                      message_id='last',
                                      title="*Winter mode*",
                                      message="Activating ...",
                                      inline_keyboard=[])
                    title='*Winter mode activated*'
                    state_athome = self.get_state("input_boolean.at_home")
                    if state_athome =='on':
                        msg = 'At home scenario\n'
                    else:
                        msg = 'Not at home scenario\n'
            if data_callback == '/winter_mode_off':
                    self.turn_off("input_boolean.winter_mode")
                    self.call_service('telegram_bot/edit_message',
                                      chat_id=chat_id,
                                      message_id='last',
                                      title="*Winter mode*",
                                      message="Desactivating ...",
                                      inline_keyboard=[])
                    title='*Winter mode desactivated*'
                    msg = ''
            time.sleep(10)
            state_bedroom = self.get_state("input_select.heater_bedroom")
            state_living_room = self.get_state("input_select.heater_living_room")
            state_hall = self.get_state("input_select.heater_hall")
            msg = msg + 'Hall: '+state_hall+'\nLiving room: '+state_living_room+'\nBedroom: '+state_bedroom
            self.call_service('telegram_bot/edit_message',
                              chat_id=user_id,
                              message_id='last',
                              title=title,
                              message=msg)

        if data_callback == '/edit_msg':  # Message editor:
            # Answer callback query
            self.call_service('telegram_bot/answer_callback_query',
                              message='Editing the message!',
                              callback_query_id=callback_id,
                              show_alert=True)

            # Edit the message origin of the callback query
            msg_id = payload_event['message']['message_id']
            user = payload_event['from_first']
            title = '*Message edit*'
            msg = 'Callback received from %s. Message id: %s. Data: ``` %s ```'
            self.call_service('telegram_bot/edit_message',
                              chat_id=chat_id,
                              message_id=msg_id,
                              title=title,
                              message=msg % (user, msg_id, data_callback),
                              inline_keyboard=keyboard)

        elif data_callback == '/remove button':  # Keyboard editor:
            # Answer callback query
            self.call_service('telegram_bot/answer_callback_query',
                              message='Callback received for editing the '
                                      'inline keyboard!',
                              callback_query_id=callback_id)

            # Edit the keyboard
            new_keyboard = keyboard[:1]
            self.call_service('telegram_bot/edit_replymarkup',
                              chat_id=chat_id,
                              message_id='last',
                              inline_keyboard=new_keyboard)

        elif data_callback == '/do_nothing':  # Only Answer to callback query
            self.call_service('telegram_bot/answer_callback_query',
                              message='OK, you said no!',
                              callback_query_id=callback_id)
