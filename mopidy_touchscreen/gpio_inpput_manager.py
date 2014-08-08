import RPi.GPIO as GPIO
import logging

logger = logging.getLogger(__name__)


class GPIOManager():

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
        GPIO.add_event_detect(23, GPIO.RISING, callback=printFunction, bouncetime=300)


def printFunction():
    logger.error("Sakatu da")
