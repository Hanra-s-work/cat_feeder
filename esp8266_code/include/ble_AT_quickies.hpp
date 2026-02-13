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
* LAST Modified: 18:3:44 12-02-2026
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

// Macro for line endings
#ifndef AT_NEWLINE
#define AT_NEWLINE "\r\n"
#endif

namespace BluetoothLE
{
    namespace AT
    {
        // Core constants
        inline constexpr std::string_view NEWLINE = AT_NEWLINE;
        inline constexpr std::string_view TEST = "AT" AT_NEWLINE;

        // Query namespace (all GET operations)
        namespace Query
        {
            inline constexpr std::string_view NAME = "AT+NAME?" AT_NEWLINE;
            inline constexpr std::string_view ADDR = "AT+ADDR?" AT_NEWLINE;
            inline constexpr std::string_view VERSION = "AT+VERS?" AT_NEWLINE;
            inline constexpr std::string_view BAUD = "AT+BAUD?" AT_NEWLINE;
            inline constexpr std::string_view ROLE = "AT+ROLE?" AT_NEWLINE;
            inline constexpr std::string_view PASS = "AT+PASS?" AT_NEWLINE;
            inline constexpr std::string_view TYPE = "AT+TYPE?" AT_NEWLINE;
        }

        // Set namespace (all configuration operations)
        namespace Set
        {
            inline constexpr std::string_view NAME = "AT+NAME";      // append new name + AT_NEWLINE
            inline constexpr std::string_view PASS = "AT+PASS";      // append PIN + AT_NEWLINE
            inline constexpr std::string_view ROLE_SLAVE = "AT+ROLE0" AT_NEWLINE;
            inline constexpr std::string_view ROLE_MASTER = "AT+ROLE1" AT_NEWLINE;
        }

        // Action namespace (operations that perform actions)
        namespace Action
        {
            inline constexpr std::string_view RESET = "AT+RESET" AT_NEWLINE;
            inline constexpr std::string_view SLEEP = "AT+SLEEP" AT_NEWLINE;
            inline constexpr std::string_view DISCOVER = "AT+DISC?" AT_NEWLINE;
            inline constexpr std::string_view DISCOVER_ALT = "AT+DISC" AT_NEWLINE;  // Alternative without '?'
            inline constexpr std::string_view CONNECT = "AT+CON";    // append MAC + AT_NEWLINE
        }

        // Expected responses (for string comparison without heap allocation)
        namespace Responses
        {
            namespace Ok
            {
                inline constexpr std::string_view OK = "OK";
                inline constexpr std::string_view CONN = "OK+CONN";
                inline constexpr std::string_view LOST = "OK+LOST";
                inline constexpr std::string_view DISC = "OK+DISC:";
                inline constexpr std::string_view DIS = "OK+DIS";     // Covers OK+DIS0, OK+DISA, etc.
                inline constexpr std::string_view DISCS = "OK+DISCS";
                inline constexpr std::string_view NAME = "OK+NAME:";
                inline constexpr std::string_view ADDR = "OK+ADDR:";
                inline constexpr std::string_view VERS = "OK+VERS:";
                inline constexpr std::string_view ROLE = "OK+Get:";   // Response to role query (generic)

                namespace Role
                {
                    inline constexpr std::string_view SLAVE = "OK+Get:0";   // Role 0 = Slave/Peripheral
                    inline constexpr std::string_view MASTER = "OK+Get:1";  // Role 1 = Master/Central
                    // Alternative formats (some firmware versions, no "OK" prefix)
                    inline constexpr std::string_view ALT_SLAVE = "+Get:0";
                    inline constexpr std::string_view ALT_MASTER = "+Get:1";
                    inline constexpr std::string_view SET_SLAVE = "+ROLE=0";  // Response to AT+ROLE0
                    inline constexpr std::string_view SET_MASTER = "+ROLE=1"; // Response to AT+ROLE1
                }
            }
            namespace Error
            {
                inline constexpr std::string_view ERROR = "ERROR";
            }
        }

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
