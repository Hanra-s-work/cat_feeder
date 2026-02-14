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
* LAST Modified: 8:35:18 14-02-2026
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
inline constexpr char SSID[] = "[SSID]";
inline constexpr char SSID_PASSWORD[] = "[SSID_PASSWORD]";

// Board name
inline constexpr char BOARD_NAME[] = "[BOARD_NAME]";

// Ntfy server Address
inline constexpr char NTFY_SERVER[] = "[NTFY_SERVER]";
inline constexpr char NTFY_TOPIC[] = "[NTFY_TOPIC]";

// Control server
inline constexpr char CONTROL_SERVER[] = "[CONTROL_SERVER]";

// Internal server configuration
inline constexpr int SERVER_PORT = 80;

// Blink interval (ms)
inline unsigned long blinkInterval = 1000;

// Serial communication baud rate
inline constexpr unsigned long SERIAL_BAUDRATE = 115200;

// connection attempts delay (ms)
inline constexpr unsigned long WIFI_RETRY_DELAY = 500;

// Led configs
inline constexpr uint8_t LED_BRIGHTNESS = 100; // 0-255
inline constexpr uint8_t LED_WHITE_LEVEL = 0;  // 0-255
inline constexpr uint16_t LED_NUMBER = 30;    // Number of LEDs in the strip
inline constexpr uint8_t LED_DURATION = 0;   // Duration for color display in setColor functions (0 = infinite)
#ifndef LED_TYPE
#define LED_TYPE NEO_KHZ800 // LED strip type
#endif
#ifndef LED_COLOUR_ORDER
#define LED_COLOUR_ORDER NEO_GRBW // LED strip colour order
#endif

// Led cycle animation
inline constexpr uint32_t LED_CYCLE_INTERVAL_MS = 100; // Interval between frames in cycle animation
inline constexpr int16_t LED_CYCLE_STEP = 1; // Step size for cycle animation

// component led info
inline constexpr int16_t LED_COMPONENT_STEP = 0;
inline constexpr bool LED_COMPONENT_DISABLE_ON_COMPLETE = false;
inline constexpr uint32_t LED_COMPONENT_INTERVAL_MS = 500;


// Motor configs
inline constexpr uint8_t MOTOR_SPEED_DEFAULT = 50; // Default motor speed (0-100)
inline constexpr unsigned long MOTOR_TURN_DURATION_DEFAULT = 1000; // Default duration for turning (ms)
inline constexpr float MOTOR_TURN_DEGREES_DEFAULT = 90.0f; // Default degrees to turn

// PDP pseudo-emulation
inline constexpr uint8_t BOTTOM_STRIP_SIZE = 15;
inline constexpr uint8_t TOP_STRIP_START = 15;
inline constexpr uint8_t TOP_STRIP_END = LED_NUMBER - 1; // 29

// Bluethooth Serial
inline constexpr uint16_t MAX_BLE_DEVICES = 32;
inline constexpr unsigned long BLUETOOTH_BAUDRATE = 9600;
inline constexpr unsigned long BLE_SCAN_INTERVAL = 30000; // Scan every 30 seconds
inline constexpr unsigned long BLE_PERIODIC_SCAN_DURATION = 3000; // Scan for 3 seconds
inline constexpr unsigned long BLE_STATUS_CHECK_INTERVAL = 10000; // Check BLE connectivity every 10 seconds

// Led render timing
inline constexpr unsigned long LED_RENDER_INTERVAL = 100; // Render LEDs every 100ms

// Server update settings
inline constexpr unsigned long SIGNS_OF_LIFE = 1800000; // update ip to server every 30 minutes
