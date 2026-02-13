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
* LAST Modified: 17:36:56 12-02-2026
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

        // Send/receive - buffer versions (no heap allocation)
        void send(const char *data, size_t length);  // send char array over BLE
        size_t receive(char *buffer, size_t buffer_size);  // read into buffer, returns bytes read

        // Send/receive - String versions (for convenience in non-critical paths)
        void send(const String &data);  // send string over BLE
        String receive();            // read available data (allocates)

        // AT Command operations
        // Buffer versions (no heap allocation - for hot path)
        size_t sendATCommand(const std::string_view &cmd, char *response_buffer, size_t buffer_size, uint32_t timeout_ms = 1000);
        ATCommandResult testConnection();  // Send "AT" to test if module responds (uses buffer internally)

        // String versions (for diagnostics/convenience)
        String sendATCommand(const std::string_view &cmd, uint32_t timeout_ms = 1000);
        String getModuleName();
        String getModuleAddress();
        String getVersion();
        BLERole getRole();
        bool setRole(BLERole role);

        // Slave/Peripheral mode configuration
        bool setModuleName(const char *name);                         // Set BLE device name (uses buffer)
        bool setModuleName(const String &name);                       // Set BLE device name (String wrapper)
        bool setupSlaveMode(const char *device_name = nullptr);       // Configure module for peripheral mode
        bool waitForConnection(uint32_t timeout_ms = 0);              // Wait for incoming connection (0 = no timeout)
        bool hasIncomingData();                                        // Check if data is available to read
        void monitorConnection();                                      // Check and log connection state changes

        // Scanning operations
        bool startScan(uint32_t timeout_ms = 5000);  // Start BLE device discovery
        const BLEDevice *getScannedDevices() const;  // Get pointer to device array
        uint8_t getDeviceCount() const;              // Get number of devices found
        uint8_t getOverflowCount() const;            // Get number of devices lost due to overflow
        void clearScannedDevices();                   // Clear the device list
        bool connectToDevice(const char *address);   // Connect by MAC (char array - no allocation)
        bool connectToDevice(const String &address); // Connect by MAC (String - for convenience)
        bool disconnect();                            // Disconnect from current device

        // Utility functions
        void reset();           // Reset module to factory defaults
        void printStatus();     // Print module status to Serial
        void changeBaudRate(uint32_t new_baud); // Change baud rate and reinitialize serial

        // Diagnostic and testing functions
        void testHardware();    // Print hardware diagnostics (pins, baud rate, basic AT test)
        void testBaudRates();   // Test common baud rates to find working one
        void printInitialScan(uint32_t scan_duration_ms = 5000); // Run and print initial scan results
        void printConnectionStatus();  // Print current connection status
        void printPeriodicScan();      // Run periodic scan and print results with device details

        private:
        SoftwareSerial _serial;
        uint32_t _baud;
        MyUtils::ActiveComponents::Component _ble_component = MyUtils::ActiveComponents::Component::Bluetooth;
        uint16_t _led_index = 0;   // for moving dot animation
        BLEDevice _scanned_devices[MAX_BLE_DEVICES];  // Fixed-size array of discovered devices
        uint8_t _device_count = 0;      // Number of devices currently stored
        uint8_t _overflow_count = 0;    // Number of devices lost due to array overflow
        BLERole _current_role = BLERole::Unknown;
        bool _was_connected = false;    // Track previous connection state for change detection

        // Helper methods
        size_t _readResponseToBuffer(char *buffer, size_t buffer_size, uint32_t timeout_ms);
        String _readResponse(uint32_t timeout_ms);  // String version for convenience
        BLEDevice _parseDiscoveryLine(const char *line, size_t length);  // Buffer version
        BLEDevice _parseDiscoveryLine(const String &line);  // String wrapper
        void _flushSerial();
    };
}
