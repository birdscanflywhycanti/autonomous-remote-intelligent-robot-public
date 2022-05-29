from math import dist
import RPi.GPIO as GPIO
import time
import logging

class HCSR04():
    def __init__(self, trigger=12, echo=24, echo_timeout_ns=3000000000, logger=None):
        self.trigger = trigger
        self.echo = echo
        self.echo_timeout_ns = echo_timeout_ns

        self.logger = logger

    def setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
        GPIO.output(self.trigger, False)
        time.sleep(0.5)   # settle sensor

    def pulse(self):
        # NOTE: no debugging during pulse below, as messes up timings
        GPIO.output(self.trigger, True) # send pulse for 0.00001 seconds
        time.sleep(0.001)
        GPIO.output(self.trigger, False)

        pulse_sent = time.time_ns()

        pulse_start_ns = time.time_ns() # preset in case of instant exit from while loop
        while GPIO.input(self.echo) == 0:   # wait for response
            pulse_start_ns = time.time_ns()   # record time when response is recieved

            if pulse_start_ns - pulse_sent > self.echo_timeout_ns: # if waited too long, exit
                logging.debug("pulse timeout")
                return -1

        pulse_end_ns = time.time_ns() # preset in case of instant exit from while loop
        while GPIO.input(self.echo) == 1:   # wait for pulse to end
            pulse_end_ns = time.time_ns() # record pulse end time

            if pulse_end_ns - pulse_sent > self.echo_timeout_ns:  # if time between pulse send and pulse end is greater than timeout
                logging.debug("pulse end timeout")
                return -1
        
        # NOTE: debug from here
        #logging.debug(f"pulse start: {pulse_start_ns}")
        #logging.debug(f"pulse end: {pulse_end_ns}")

        pulse_duration = (pulse_end_ns - pulse_start_ns) / 1000000000   # convert from nanoseconds to seconds
        distance = pulse_duration * 17150   # calculate distance using speed of sound (in cm/s)

        if self.logger:
            self.logger.debug(distance)

        return distance

    def cleanup(self):
        GPIO.cleanup()  # reset pins

    def get_distance(self):
        if self.logger:
            self.logger.debug("-----")

        # perform obstacle checks
        total_pulses = 0
        avg_distance = 0
        N = 20

        self.setup()  # setup sensor and settle
        
        for i in range(N):  # attempt N pulses
            distance = self.pulse()
            time.sleep(0.05)  # pause inbetween pulses
            if distance <= 60 and distance > 0:  # if within 0-60cm range
                avg_distance += distance
                total_pulses += 1  # increment successfuly pulses

            #if self.logger:
            #    self.logger.debug(i, distance)

        self.cleanup()  # cleanup sensor

        if total_pulses > 0:
            avg_distance /= total_pulses
            avg_distance = round(avg_distance, 3)
        else:
            avg_distance = -1

        confidence = total_pulses / float(N)
        
        return avg_distance, confidence

if __name__ == "__main__":
    # enable debug logging
    logging.basicConfig(filename="logging_mpu6050", filemode="a", format='%(asctime)s - %(message)s', level=logging.INFO)

    sensor = HCSR04(trigger=12, echo=24, echo_timeout_ns=3000000000)    # 3 second timeout (in nanoseconds)
    try:
        sensor.setup()
        
        while 1:
            distance = sensor.pulse()
            distance = round(distance, 3)

            # logical bounds checking
            if distance > 400 or distance < 0:   # 400cm sensor range, also return error for timeouts
                distance = f"ERROR ({distance})"    # log as sensor error

            logging.info(f"Distance: {distance}cm")
            time.sleep(0.1)
    except KeyboardInterrupt:
        sensor.cleanup()
    
    sensor.cleanup()    # remember to perform manual cleanup