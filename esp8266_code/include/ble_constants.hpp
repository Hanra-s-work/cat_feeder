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
* FILE: ble_constants.hpp
* CREATION DATE: 12-02-2026
* LAST Modified: 2:23:54 12-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: BLE-related constants to avoid magic numbers in the code.
* // AR
* +==== END CatFeeder =================+
*/
#pragma once
#include <cstdint>

namespace BluetoothLE
{
    namespace Constants
    {
        // Buffer sizes
        constexpr size_t TEST_RESPONSE_BUFFER_SIZE = 32;      // Buffer for AT test command response
        constexpr size_t COMMAND_RESPONSE_BUFFER_SIZE = 64;    // Buffer for general command responses
        constexpr size_t CONNECT_COMMAND_BUFFER_SIZE = 22;     // "AT+CON" + 12 hex digits + "\r\n" + null

        // BLE address format
        constexpr size_t BLE_ADDRESS_LENGTH = 12;              // BLE MAC address length in hex digits

        // Response string prefix lengths
        constexpr size_t RESPONSE_PREFIX_NAME_LENGTH = 5;      // Length of "NAME:" prefix
        constexpr size_t RESPONSE_PREFIX_ADDR_LENGTH = 5;      // Length of "ADDR:" prefix
        constexpr size_t RESPONSE_PREFIX_VERS_LENGTH = 5;      // Length of "VERS:" prefix

        // Timing delays (milliseconds)
        constexpr uint32_t POWER_UP_DELAY_MS = 100;            // Module power-up stabilization time
        constexpr uint32_t ROLE_CHANGE_DELAY_MS = 500;         // Delay after changing module role (needs time to stabilize)
        constexpr uint32_t SERIAL_REINIT_DELAY_MS = 50;        // Delay for serial reinitialization
        constexpr uint32_t SERIAL_STABILIZE_DELAY_MS = 50;     // Serial stabilization delay
        constexpr uint32_t RESPONSE_TRAILING_DELAY_MS = 50;    // Delay to catch trailing response characters
        constexpr uint32_t RESPONSE_POLL_DELAY_MS = 10;        // Polling interval when reading responses

        // Data size limits
        constexpr uint8_t MAX_TRANSMISSION_SIZE = 255;         // Maximum size for LED transmission indicator
    }
}
