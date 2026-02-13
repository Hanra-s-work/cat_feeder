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
* LAST Modified: 18:18:16 12-02-2026
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
#include "ble_AT_quickies.hpp"

namespace BluetoothLE
{
    namespace Constants
    {
        // Buffer sizes
        inline constexpr size_t TEST_RESPONSE_BUFFER_SIZE = 32;      // Buffer for AT test command response
        inline constexpr size_t COMMAND_RESPONSE_BUFFER_SIZE = 64;    // Buffer for general command responses
        inline constexpr size_t CONNECT_COMMAND_BUFFER_SIZE = 22;     // "AT+CON" + 12 hex digits + "\r\n" + null

        // BLE address format
        inline constexpr size_t BLE_ADDRESS_LENGTH = 12;              // BLE MAC address length in hex digits

        // Response string prefix lengths
        inline constexpr size_t RESPONSE_PREFIX_NAME_LENGTH = 5;      // Length of "NAME:" prefix
        inline constexpr size_t RESPONSE_PREFIX_ADDR_LENGTH = 5;      // Length of "ADDR:" prefix
        inline constexpr size_t RESPONSE_PREFIX_VERS_LENGTH = 5;      // Length of "VERS:" prefix

        // Timing delays (milliseconds)
        inline constexpr uint32_t POWER_UP_DELAY_MS = 100;            // Module power-up stabilization time
        inline constexpr uint32_t ROLE_CHANGE_DELAY_MS = 500;         // Delay after changing module role (needs time to stabilize)
        inline constexpr uint32_t SERIAL_REINIT_DELAY_MS = 50;        // Delay for serial reinitialization
        inline constexpr uint32_t SERIAL_STABILIZE_DELAY_MS = 50;     // Serial stabilization delay
        inline constexpr uint32_t RESPONSE_TRAILING_DELAY_MS = 50;    // Delay to catch trailing response characters
        inline constexpr uint32_t RESPONSE_POLL_DELAY_MS = 10;        // Polling interval when reading responses

        // Data size limits
        inline constexpr uint8_t MAX_TRANSMISSION_SIZE = 255;         // Maximum size for LED transmission indicator

        // Maximum name length
        inline constexpr size_t MAX_NAME_LENGTH = 20;
        inline constexpr size_t COMMAND_NAME_LENGTH = (sizeof(AT::Set::NAME) - 1) + MAX_NAME_LENGTH + (sizeof(AT::NEWLINE) - 1) + 1; // "AT+NAME" + name + "\r\n" + null
    }
}
