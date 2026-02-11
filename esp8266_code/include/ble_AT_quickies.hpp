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
* FILE: ble_AT_quickies.hpp
* CREATION DATE: 11-02-2026
* LAST Modified: 21:37:30 11-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is a set of AT commands that the program could be susceptible to use and are thus made quickly accessible.
* // AR
* +==== END CatFeeder =================+
*/
#pragma once
#include <string_view>

namespace BluetoothLE
{
    namespace AT
    {

        namespace Query
        {
            inline constexpr std::string_view NAME = "AT+NAME?";
            inline constexpr std::string_view ROLE = "AT+ROLE?";
        }

        namespace Set
        {
            inline constexpr std::string_view ROLE_MASTER = "AT+ROLE1";
            inline constexpr std::string_view ROLE_SLAVE = "AT+ROLE0";
        }

        namespace Action
        {
            inline constexpr std::string_view RESET = "AT+RESET";
            inline constexpr std::string_view SLEEP = "AT+SLEEP";
        }

        inline constexpr std::string_view TEST = "AT";
        inline constexpr std::string_view NAME_GET = "AT+NAME?";
        inline constexpr std::string_view NAME_SET = "AT+NAME";      // append new name
        inline constexpr std::string_view ADDR_GET = "AT+ADDR?";
        inline constexpr std::string_view VERSION_GET = "AT+VERS?";
        inline constexpr std::string_view BAUD_GET = "AT+BAUD?";

        inline constexpr std::string_view ROLE_GET = "AT+ROLE?";
        inline constexpr std::string_view ROLE_SLAVE = "AT+ROLE0";
        inline constexpr std::string_view ROLE_MASTER = "AT+ROLE1";

        inline constexpr std::string_view DISCOVER = "AT+DISC?";
        inline constexpr std::string_view CONNECT = "AT+CON";       // append MAC

        inline constexpr std::string_view RESET = "AT+RESET";
        inline constexpr std::string_view SLEEP = "AT+SLEEP";

        inline constexpr std::string_view PASS_GET = "AT+PASS?";
        inline constexpr std::string_view PASS_SET = "AT+PASS";      // append PIN
        inline constexpr std::string_view TYPE_GET = "AT+TYPE?";

    }
}

/*
 * USEFUL AT COMMANDS FOR AT-09 MODULE:
 *
 * Testing & Info:
 *   AT              - Test connection (returns OK)
 *   AT+NAME?        - Get module name
 *   AT+NAMENewName  - Set module name
 *   AT+ADDR?        - Get MAC address
 *   AT+VERS?        - Get firmware version
 *   AT+BAUD?        - Get baud rate
 *
 * Role Management:
 *   AT+ROLE?        - Get role (0=Slave/Peripheral, 1=Master/Central)
 *   AT+ROLE0        - Set to Slave mode (default)
 *   AT+ROLE1        - Set to Master mode (required for scanning)
 *
 * Scanning & Connection (Master mode only):
 *   AT+DISC?        - Start device discovery
 *   AT+CONxxxxxxxxxxxx - Connect to device by MAC (12 hex digits)
 *   AT              - Disconnect from current device
 *
 * Power & Reset:
 *   AT+RESET        - Reset module
 *   AT+SLEEP        - Enter sleep mode
 *
 * Pin & Security:
 *   AT+PASS?        - Get pairing PIN
 *   AT+PASS123456   - Set pairing PIN
 *   AT+TYPE?        - Get pairing mode
 *
 * NOTES:
 * - All commands are case-sensitive
 * - Commands do not end with CR/LF (just send the command string)
 * - Responses typically start with OK+ or ERROR
 * - Some commands require module reset to take effect
 * - Master mode is required for scanning and connecting to other devices
 * - Slave mode is for being discovered and connected to (default)
 */
