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
* FILE: ble_handler.hpp
* CREATION DATE: 07-02-2026
* LAST Modified: 22:12:20 11-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the header for the bluetooth module overlay for handling detection of ble devices.
* // AR
* +==== END CatFeeder =================+
*/
#pragma once
#include <string_view>

#include <Arduino.h>
#include <SoftwareSerial.h>

#include "my_overloads.hpp"

#include "ble_enums.hpp"
#include "ble_structs.hpp"
#include "ble_AT_quickies.hpp"

#include "leds.hpp"
#include "pins.hpp"
#include "config.hpp"
#include "colours.hpp"
#include "structs.hpp"
#include "sentinels.hpp"
#include "active_components.hpp"


namespace BluetoothLE
{
    class BLEHandler {
        public:
        BLEHandler(uint32_t baud = 9600);

        // Basic operations
        void init();            // setup pins and serial
        void enable();          // turn on BLE module
        void disable();         // turn off BLE module
        bool isConnected() const;   // read BLE_STATE pin
        void send(const String &data);  // send string over BLE
        String receive();            // read available data

        // AT Command operations
        String sendATCommand(const std::string_view &cmd, uint32_t timeout_ms = 1000);
        ATCommandResult testConnection();  // Send "AT" to test if module responds
        String getModuleName();
        String getModuleAddress();
        String getVersion();
        BLERole getRole();
        bool setRole(BLERole role);

        // Scanning operations
        bool startScan(uint32_t timeout_ms = 5000);  // Start BLE device discovery
        const BLEDevice *getScannedDevices() const;  // Get pointer to device array
        uint8_t getDeviceCount() const;              // Get number of devices found
        uint8_t getOverflowCount() const;            // Get number of devices lost due to overflow
        void clearScannedDevices();                   // Clear the device list
        bool connectToDevice(const String &address); // Connect to a device by MAC address
        bool disconnect();                            // Disconnect from current device

        // Utility functions
        void reset();           // Reset module to factory defaults
        void printStatus();     // Print module status to Serial

        private:
        SoftwareSerial _serial;
        uint32_t _baud;
        MyUtils::ActiveComponents::Component _ble_component = MyUtils::ActiveComponents::Component::Bluetooth;
        uint16_t _led_index = 0;   // for moving dot animation
        BLEDevice _scanned_devices[MAX_BLE_DEVICES];  // Fixed-size array of discovered devices
        uint8_t _device_count = 0;      // Number of devices currently stored
        uint8_t _overflow_count = 0;    // Number of devices lost due to array overflow
        BLERole _current_role = BLERole::Unknown;

        // Helper methods
        String _readResponse(uint32_t timeout_ms);
        BLEDevice _parseDiscoveryLine(const String &line);
        void _flushSerial();
    };
}
