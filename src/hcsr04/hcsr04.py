import RPi.GPIO as GPIO
import time
import logging

class HCSR04:
    def __init__(self, trigger=24, echo=12):
        self.trigger = trigger
        self.echo = echo

        GPIO.setmode(GPIO.BCM)
        logging.debug("setmode")

    def pulse(self):
        GPIO.setup(self.trigger, GPIO.OUT)
        logging.debug("setup trigger")
        GPIO.setup(self.echo, GPIO.IN)
        logging.debug("setup echo")
        GPIO.output(self.trigger, False)
        logging.debug("set trigger to False")
        time.sleep(2)   # settle sensor
        logging.debug("settled sensor")

        logging.debug("pulsing")

        # NOTE: no debugging during pulse below, as messes up timings
        GPIO.output(self.trigger, True) # send pulse for 0.00001 seconds
        time.sleep(0.001)
        GPIO.output(self.trigger, False)

        pulse_start_ns = time.time_ns() # preset in case of instant exit from while loop
        while GPIO.input(self.echo) == 0:   # wait for response
            pulse_start_ns = time.time_ns()   # record time when response is recieved

        pulse_end_ns = time.time_ns() # preset in case of instant exit from while loop
        while GPIO.input(self.echo) == 1:   # wait for pulse to end
            pulse_end_ns = time.time_ns() # record pulse end time
        
        # NOTE: debug from here
        logging.debug(f"pulse start: {pulse_start_ns}")
        logging.debug(f"pulse end: {pulse_end_ns}")

        pulse_duration = (pulse_end_ns - pulse_start_ns) / 1000000000   # convert from ns to s
        logging.debug(f"pulse duration: {pulse_duration}")
        distance = pulse_duration * 17150   # calculate distance using speed of sound (in cm/s)

        self.cleanup()

        return distance

    def cleanup(self):
        GPIO.cleanup()  # reset pins
        logging.debug("cleaned up pins")

if __name__ == "__main__":
    # enable debug logging
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)

    sensor = HCSR04()
    try:
        while 1:
            distance = sensor.pulse()
            logging.info(f"Distance: {round(distance, 3)}cm")
            time.sleep(0.1)
    except KeyboardInterrupt:
        sensor.cleanup()