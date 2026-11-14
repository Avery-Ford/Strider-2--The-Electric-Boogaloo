""" 
Main Time of Flight Sensor file. 
"""

import time

MINIMUM_DISTANCE = 40

sensor = DistanceSensor(1, 100)

#TODO: Connect this file to the main file so it can actually move

def walk_forward():
    print("forward")

def turn_left():
    print("turning left")

def turn_right():
    print("turning right")

def stop():
    print("stopping")


def distance_decisions():
    try:
        while True:
            dist = sensor.read_dist()
            if dist is not None and dist < MINIMUM_DISTANCE:
                stop()
                turn_left()
            else:
                walk_forward()
            time.sleep(1.0)
    finally:
        stop()
        sensor.end()



def main():
    distance_read_test.print_check(sensor)
    keep_run = input("Start test?(True/False)")
    distance_read_test.range_test(keep_run)
    distance_calculations()




