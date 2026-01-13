from machine import Pin, PWM, ADC
from utime import ticks_diff

########################################################################################################
# Parent class for components
# Also operated as a built in static registry, all child class instatiations have references saved here
class Component:
    registry = []

    def __init__(self, pin_num = None, pin=None, debug_enabled=False, on=False):
        Component.registry.append(self)                                 # add child to registry
        self.pin_num = pin_num
        self.pin = pin                                                  # takes a pin object
        self.debug_enabled = debug_enabled                              # for debug text
        self.on = on                                              # on/off toggle for each component
        self.last_time = None                                           # time since last update

    def update(self, curr_time):
        raise NotImplementedError                                       # must be implemented in the child!

    def turn_on(self):
        self.on = True
        if self.debug_enabled:
            print(f"Component at pin number {self.pin_num} is now on!")

    def turn_off(self):
        self.on = False
        if self.debug_enabled:
            print(f"Component at pin number {self.pin_num} is now off!")

    def is_on(self):
        return self.on

    def set_debug(self, enabled):
        self.debug_enabled = enabled

#############################################################################################
# Button class inheriting component class
# defaults to on position
class Button(Component):
    def __init__(self, pin_num, debounce_ms=10, debug_enabled=False):
        super().__init__(pin_num, Pin(pin_num, Pin.IN, Pin.PULL_DOWN), debug_enabled, True)
        self.armed = False
        self.count = 0
        self.debounce_ms = 10
        self.low_since = None

    def _check_for_press(self, curr_time):
        if not self.on:
            return

        button_value = self.pin.value()

        if button_value == 1 and self.armed:
            if ticks_diff(curr_time, self.last_time) >= self.debounce_ms:
                self.armed = False
                self.count += 1
                if self.debug_enabled:
                    print("Button pressed, count: {self.count}\n")
                    
                self.last_time = curr_time

        if button_value == 0:
            if self.low_since is None:          # tracks if the button val has been low (0) for a while
                self.low_since = curr_time      # prevents the random 10101 switching that happens at each press from triggering reset
            elif ticks_diff(curr_time, self.low_since) >= self.debounce_ms:
                self.armed = True
        else:
            self.low_since = None

    def get_count(self):
        return self.count

    def set_count(self, count):
        self.count = count

    def value(self):
        return self.pin.value()
    
    def update(self, curr_time):
        if self.last_time is None:
            self.last_time = curr_time

        self._check_for_press(curr_time)

#########################################################################################
# Led class inheriting Component
# If blink_dur is None it's set to emit light constatntly if on
class Led(Component):
    def __init__(self, pin_num, blink_dur=None, perc_brightness=100, on=False, debug_enabled=False):
        super().__init__(pin_num, Pin(pin_num, Pin.OUT, pull=None), debug_enabled, on)
        if blink_dur is not None:
            self.duty = self.perc_to_duty(50)
            self.pwm = PWM(self.pin, freq=int(1000/blink_dur), duty=0)
        else:
            self.duty = self.perc_to_duty(perc_brightness)
            self.pwm = PWM(self.pin, freq=100000, duty=0)
        self.emitting = False
        self.blink_dur = blink_dur # in hertz (if >1000 then looks like always on)
    
    def set_duty(self, perc_brightness):
        self.duty = self.perc_to_duty(perc_brightness)

    def perc_to_duty(self, perc):
        return int((perc / 100.0) * 1023.0)

    def get_duty(self):
        return self.duty

    def update(self, curr_time):
        if self.last_time is None:
            self.last_time = curr_time

        if self.on:
            self.pwm.duty(self.duty)
        else:
            self.pwm.duty(0)


##########################################################################################
# Photoresistor class inheriting Component class
# also contains file io functionality
class Photoresistor(Component):
    def __init__(self, pin_num, debug_enabled=False, measurement_interval=500, filename=None, on=False, measurement_duration=None, num_measurements=None):
        super().__init__(pin_num, Pin(pin_num), debug_enabled, on)
        self.sensor = ADC(self.pin)
        self.sensor.atten(ADC.ATTN_11DB)
        self.f_out = None
        self.filenames = None
        if filename is not None:
            self.base_name = filename
            self.filenames = [self.add_txt(filename)]
        self.filename_counter = 0
        self.save_filename = filename
        self.measurement_interval = measurement_interval # in ms
        self.measurement_start_time = None
        self.measurement_duration = measurement_duration

        self.total_measurements = num_measurements
        self.num_measurements = num_measurements
        if num_measurements is not None:
            self.measurement_interval = 0

        self.measurement_complete = False

    def add_txt(self, filename):
        return filename + ".txt"
    
    def get_voltage(self):
        return self.sensor.read_uv() * 10**(-6)

    def _take_measurement(self, curr_time=None, paired_val=None):
        measurement = self.sensor.read_uv() * 10**(-6)

        if curr_time is not None:
            if self.debug_enabled:
                print(f"Took measurement: {measurement} at time: {curr_time}")
            self._save_measurement(measurement, curr_time=curr_time)
        elif paired_val is not None:
            if self.debug_enabled:
                print(f"Took measurement: {measurement} with paired value: {paired_val}")
            self._save_measurement(measurement, paired_val=paired_val)

        if self.num_measurements is not None:
            print(f"Took measurement! Remaining: {self.num_measurements}")
            self.num_measurements -= 1


    def _save_measurement(self, measurement, curr_time=None, paired_val=None):
        if curr_time is not None:
            time_since_start = ticks_diff(curr_time, self.measurement_start_time)
            if self.f_out is not None:
                self.f_out.write(f"{measurement}, {time_since_start}\n")
                if self.debug_enabled:
                    print(f"Saved measurement: {measurement}, {curr_time} in file {self.save_filename}\n")
        elif paired_val is not None:
            if self.f_out is not None:
                self.f_out.write(f"{measurement}, {paired_val}\n")
                if self.debug_enabled:
                    print(f"Saved measurement: {measurement}, {paired_val} in file {self.save_filename}\n")
    
    def get_measurement(self):
        return self.measurement
    
    def is_complete(self):
        return self.measurement_complete

    def set_measurement_start_time(self, val):
        self.measurement_start_time = val

    def connect_file(self):
        if self.filenames:
            filename = self.filenames[self.filename_counter]
            print(f"Connected to file: {filename}")
            self.f_out = open(filename, "w")
        else:
            print(f"Tried to write to file without a valid filename!\n")
            exit(1)

    def inc_filename(self):
        if self.filename_counter:           # roll counter forward if not first measurement
            self.update_filenames()

    def start_measurements(self, curr_time):
        self.turn_on()
        self.set_measurement_start_time(curr_time)
        self.inc_filename()
        self.connect_file()
        if self.measurement_duration is not None:
            self.measurement_complete = False

    def stop_measurements(self):
        if self.on:
            self.turn_off()
            self.f_out.close()
            self.filename_counter += 1
            self.measurement_complete = True

    def update_filenames(self):
        self.save_filename = self.add_txt(self.base_name + (f"_{self.filename_counter}"))
        self.filenames.append(self.save_filename)

    def get_filenames(self):
        return self.filenames
    
    def check_stop(self, curr_time):
        if self.measurement_duration is not None and ticks_diff(curr_time, self.measurement_start_time) >= self.measurement_duration:
            self.stop_measurements()

        if self.num_measurements is not None and self.num_measurements <= 0:
            self.stop_measurements()

    def restart(self):
        self.measurement_complete = False
        self.num_measurements = self.total_measurements


    def update(self, curr_time):
        if self.last_time is None:
            self.last_time = curr_time

        self.check_stop(curr_time)

        if self.on:
            if ticks_diff(curr_time, self.last_time) > self.measurement_interval:
                self._take_measurement(curr_time)
                self.last_time = curr_time