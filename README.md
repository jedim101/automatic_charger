# Automatic Car Charging Cable Retration System

## What is it?

The charging cable for my Tesla gets in the way of walking around the garage when it sits on the floor and there's no good place to store it when unplugged. The cable is now held on a cable in the air (~10ft up) to stay out of the way, and automatically lowers and raises with an ESP32 controlling a stepper motor based on the following:

- whether the car charging port is open or closed (detected using a websocket runnning on the ESP32 connected to Tesla Fleet Telemetry)
- whether the garage door is open or closed (detected using a ToF sensor)
- can be manually controlled by a button on the wall

## Hardware & Electronics

coming soon

## Tesla Fleet Telemetry

I set up a partner account with Tesla Developer, got a token and registered a fleet telemetry endpoint. (This is a gross oversimplification and this whole process took ~15 hours, 4 simultaneous authications keys, and 4 different "test" projects through the developer dashboard)

I now have a websocket running on the ESP32 that gets an update about the state of the charge port door every time it changes. Tesla sends the data via the open websocket at api.matthewglasser.org where it uses a Cloudflare tunnel running on a spare computer on my wifi to connect to the ESP32 which then decodes the raw binary and processes it.

## ESP32 Code

coming soon
