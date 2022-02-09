import asyncio
import sys
import signal
import threading

import RPi.GPIO as GPIO
import time
import os

from azure.iot.device.aio import IoTHubModuleClient
from azure.iot.device import Message, MethodResponse

# Event indicating client stop
stop_event = threading.Event()

pin = int(os.getenv('GPIO', 18))

#create and configure servo
GPIO.setwarnings(False)
# Set the layout for the pin declaration
GPIO.setmode(GPIO.BCM)
# The Raspberry Pi pin (GPIO 18) connect to servo signal line(yellow wire)
# Pin 11 send PWM signal to control servo motion
GPIO.setup(pin, GPIO.OUT)

# Now we will start with a PWM signal at 50Hz at pin 18. 
# 50Hz should work for many servos very will. If not you can play with the frequency if you like.
servo = GPIO.PWM(pin, 50)
# This command sets the midle position of the servo
servo.start(0)

servo.ChangeDutyCycle(7.5)
time.sleep(1)
servo.ChangeDutyCycle(0)

print("Servo started!")

def create_client():
    client = IoTHubModuleClient.create_from_edge_environment()

    # Define a method request handler
    async def method_request_handler(method_request):

        if method_request.name == "open":

            print("Received OPEN command!")

            servo.ChangeDutyCycle(2.5)
            time.sleep(1)
            servo.ChangeDutyCycle(0)

            response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
            response_status = 200

        elif method_request.name == "reset":

            print("Received RESET command!")

            servo.ChangeDutyCycle(7.5)
            time.sleep(1)
            servo.ChangeDutyCycle(0)
            
            response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
            response_status = 200

        elif method_request.name == "close":

            print("Received CLOSE command!")

            servo.ChangeDutyCycle(12.5)
            time.sleep(1)
            servo.ChangeDutyCycle(0)
            
            response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
            response_status = 200

        else:

            response_payload = {"Response": "Direct method {} not defined".format(method_request.name)}
            response_status = 404

        method_response = MethodResponse.create_from_method_request(method_request, response_status, response_payload)
        await client.send_method_response(method_response)

    try:
        # Set handler on the client
        client.on_method_request_received  = method_request_handler

    except:
        # Cleanup if failure occurs
        client.shutdown()
        raise

    return client


async def run_sample(client):
    # Customize this coroutine to do whatever tasks the module initiates
    # e.g. sending messages
    while True:
        await asyncio.sleep(1000)


def main():
    if not sys.version >= "3.5.3":
        raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
    print ( "IoT Hub Client for Python" )


    # NOTE: Client is implicitly connected due to the handler being set on it
    client = create_client()

    # Define a handler to cleanup when module is is terminated by Edge
    def module_termination_handler(signal, frame):
        print ("IoTHubClient sample stopped by Edge")
        stop_event.set()

    # Set the Edge termination handler
    signal.signal(signal.SIGTERM, module_termination_handler)

    # Run the sample
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_sample(client))
    except Exception as e:
        print("Unexpected error %s " % e)
        raise
    finally:
        print("Shutting down IoT Hub Client...")
        servo.stop()
        GPIO.cleanup()
        loop.run_until_complete(client.shutdown())
        loop.close()


if __name__ == "__main__":
    main()
