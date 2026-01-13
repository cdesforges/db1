from utime import ticks_ms
from components import Component, Button, Led, Photoresistor
from fileio import read_file
import sys

filename = "sensor_final_4000000.txt"

recording_led = Led(32, blink_dur=1000)
measurement_led = Led(27, perc_brightness=10)
start_button = Button(12, debounce_ms=10)
exit_button = Button(13)
photosensor = Photoresistor(15, measurement_interval=500, filename=filename, debug_enabled=True)

percent_walker = 0

print("Ready to go...\n")

while True:
    execfile("led_on.py")
    curr_time = ticks_ms()

    # start and stop measuring
    if start_button.get_count() % 2 == 1 and not photosensor.is_on() and percent_walker < 100:
        recording_led.turn_on()
        measurement_led.turn_on()
        photosensor.turn_on()
        photosensor.set_measurement_start_time(curr_time)
        photosensor.inc_filename()
        photosensor.connect_file()
    elif start_button.get_count() % 2 == 1 and photosensor.is_on() and percent_walker < 100:
        photosensor._take_measurement(paired_val=measurement_led.get_duty())
        percent_walker += 1
        measurement_led.set_duty(percent_walker)
        if percent_walker >= 100:
            recording_led.turn_off()
            measurement_led.turn_off()
            photosensor.stop_measurements()
            exit_button.set_count(1)
    elif start_button.get_count() % 2 == 0 and photosensor.is_on():
        recording_led.turn_off()
        measurement_led.turn_off()
        photosensor.stop_measurements()


    # exit code
    if exit_button.get_count() > 0:
        read_file(filename)
        
        print("\n\nExited successfully\n\n")
        recording_led.turn_off()
        measurement_led.turn_off()
        for c in Component.registry:
            c.update(curr_time)
        execfile("led_off.py")
        sys.exit(0)

    #update components
    for c in Component.registry:
        c.update(curr_time)