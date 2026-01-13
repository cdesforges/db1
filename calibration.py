from utime import ticks_ms
from components import Component, Button, Led, Photoresistor
from fileio import read_file
import sys

filename = "calibration_data"

recording_led = Led(14, blink_dur=1000)
measurement_led = Led(27, perc_brightness=8.8)
safe_to_eject_led = Led(32, perc_brightness=100)
start_button = Button(12, debounce_ms=10)
exit_button = Button(13)
photoresistor = Photoresistor(15, num_measurements=100, filename=filename)

while True:
    execfile("led_on.py")
    curr_time = ticks_ms()

    # start and stop measuring
    if start_button.get_count() % 2 == 1 and not photoresistor.is_on() and not photoresistor.is_complete():
        recording_led.turn_on()
        measurement_led.turn_on()
        photoresistor.start_measurements(curr_time)

    if start_button.get_count() % 2 == 0 and start_button.get_count() != 0 and photoresistor.is_complete():
        recording_led.turn_off()
        measurement_led.turn_off()
        photoresistor.restart()


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

    print(f"photo_voltage = {photoresistor.get_voltage()}")
    #update components
    for c in Component.registry:
        c.update(curr_time)