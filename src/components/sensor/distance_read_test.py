"""
Purpose of File: Prints out data measured by the Time of Flight sensor to test if it is working.
"""

import time

def print_check(sensor):
    info = sensor.get_info()
    model_info = info["Sensor Info"]
    dist_mode = info["Distance Mode"]
    time = info["Timing Budget"]

    print("VL53L1X Simple Test.")
    print("--------------------")
    print(f"Sensor Information: {model_info}")
    print(f"Distance Mode: {dist_mode}")
    print(f"Timing Budget: {time}")
    print("------------------")

def range_test(sensor, keep_run):
    try:
        sensor.start_ranging()
        time_check = 0
        while keep_run == "True":
            time_check += time.monotonic()
            if sensor.data_ready:
                print(f"Distance: {sensor.distance} cm")
                sensor.clear_interrupt()
            time.sleep(1.0)
            if time_check > 25.00:
                keep_run =="False"
    finally:
        sensor.stop_ranging()



    



