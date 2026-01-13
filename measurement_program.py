from utime import ticks_ms
from components import Component, Button, Led, Photoresistor
from fileio import read_file
import sys

filename = "demonstration.txt"

recording_led = Led(14, blink_dur=1000)
measurement_led = Led(27, perc_brightness=100)
safe_to_eject_led = Led(32, perc_brightness=100)
start_button = Button(12, debounce_ms=10)
exit_button = Button(13)
photoresistor = Photoresistor(33, measurement_interval=500, filename=filename)

while True:
    execfile("led_on.py")
    curr_time = ticks_ms()

    # start and stop measuring
    if start_button.get_count() % 2 == 1 and not photoresistor.is_on():
        recording_led.turn_on()
        measurement_led.turn_on()
        photoresistor.start_measurements(curr_time)
    elif start_button.get_count() % 2 == 0 and photoresistor.is_on():
        recording_led.turn_off()
        measurement_led.turn_off()
        photoresistor.stop_measurements()

    # exit code
    if exit_button.get_count() > 0:
        for filename in photoresistor.get_filenames():
            print(f"Measurements in file {filename}:\n")
            read_file(filename)
        
        print("\n\nExited successfully\n\n")
        recording_led.turn_off()
        measurement_led.turn_off()
        safe_to_eject_led.turn_on()
        for c in Component.registry:
            c.update(curr_time)
        execfile("led_off.py")
        sys.exit(0)

    #update components
    for c in Component.registry:
        c.update(curr_time)