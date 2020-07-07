import appdaemon.plugins.hass.hassapi as hass
import datetime

class VacationVacuum(hass.Hass):

    def initialize(self):
        self.listen_state(self.look_date, 'calendar.vacation', new = 'on')

    def look_date(self, entity, attribute, old, new, kwargs):
        end_time = self.get_state("calendar.vacation", attribute="end_time")
        if end_time is not None:
            vacation_end_time= datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            hour = vacation_end_time.hour

            if hour <= 10:
                day = vacation_end_time - datetime.timedelta(days=1)
            else:
                day = vacation_end_time

            runtime = datetime.time(10, 0, 0)
            event = datetime.datetime.combine(day, runtime)
            self.log("Will run at: {}".format(event))
            self.run_at(self.run_vacuum, event)

    def run_vacuum(self, kwargs):
        self.call_service('vacuum/start', entity_id='vacuum.vacuum_down')
        self.call_service('vacuum/start', entity_id='vacuum.vacuum_up')
