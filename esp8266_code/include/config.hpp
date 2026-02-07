/*
* +==== BEGIN CatFeeder =================+
* LOGO:
* ..............(....⁄\
* ...............)..(.')
* ..............(../..)
* ...............\(__)|
* Inspired by Joan Stark
* source https://www.asciiart.eu/
* animals/cats
* /STOP
* PROJECT: CatFeeder
* FILE: config.hpp
* CREATION DATE: 07-02-2026
* LAST Modified: 1:19:39 07-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the file in charge of containing all the configuration required for the program to work properly.
* // AR
* +==== END CatFeeder =================+
*/
#pragma once
#include <Adafruit_NeoPixel.h>

// Max values for various types
#include "sentinels.hpp"

// Pin configuration
#include "pins.hpp"

// Wifi connection
constexpr char SSID[] = "[SSID]";
constexpr char SSID_PASSWORD[] = "[SSID_PASSWORD]";

// Board name
constexpr char BOARD_NAME[] = "[BOARD_NAME]";

// Ntfy server Address
constexpr char NTFY_SERVER[] = "[NTFY_SERVER]";
constexpr char NTFY_TOPIC[] = "[NTFY_TOPIC]";

// Internal server configuration
constexpr int SERVER_PORT = 80;

// Blink interval (ms)
inline unsigned long blinkInterval = 1000;

// Serial communication baud rate
constexpr unsigned long SERIAL_BAUDRATE = 115200;

// connection attempts delay (ms)
constexpr unsigned long WIFI_RETRY_DELAY = 500;

// Led configs
constexpr uint8_t LED_BRIGHTNESS = 100; // 0-255
constexpr uint8_t LED_WHITE_LEVEL = 0;  // 0-255
constexpr uint16_t LED_NUMBER = 30;    // Number of LEDs in the strip
constexpr uint8_t LED_DURATION = 0;   // Duration for color display in setColor functions (0 = infinite)
#ifndef LED_TYPE
#define LED_TYPE NEO_KHZ800 // LED strip type
#endif
#ifndef LED_COLOUR_ORDER
#define LED_COLOUR_ORDER NEO_GRBW // LED strip colour order
#endif

// Led cycle animation
constexpr uint32_t LED_CYCLE_INTERVAL_MS = 100; // Interval between frames in cycle animation
constexpr int16_t LED_CYCLE_STEP = 1; // Step size for cycle animation

// component led info
constexpr int16_t LED_COMPONENT_STEP = 0;
constexpr bool LED_COMPONENT_DISABLE_ON_COMPLETE = false;
constexpr uint32_t LED_COMPONENT_INTERVAL_MS = 500;


// Motor configs
constexpr uint8_t MOTOR_SPEED_DEFAULT = 50; // Default motor speed (0-100)
constexpr unsigned long MOTOR_TURN_DURATION_DEFAULT = 1000; // Default duration for turning (ms)
constexpr float MOTOR_TURN_DEGREES_DEFAULT = 90.0f; // Default degrees to turn

// PDP pseudo-emulation
constexpr uint8_t BOTTOM_STRIP_SIZE = 15;
constexpr uint8_t TOP_STRIP_START = 15;
constexpr uint8_t TOP_STRIP_END = LED_NUMBER - 1; // 29

// Bluethooth Serial
constexpr unsigned long BLUETOOTH_BAUDRATE = 9600;
