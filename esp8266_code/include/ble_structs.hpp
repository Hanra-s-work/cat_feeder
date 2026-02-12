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
* FILE: ble_structs.hpp
* CREATION DATE: 11-02-2026
* LAST Modified: 0:26:45 12-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the file that will contain the structures used by the ble handler.
* // AR
* +==== END CatFeeder =================+
*/
#pragma once
#include <Arduino.h>

namespace BluetoothLE
{
    struct BLEDevice {
        char address[13];    // MAC address (12 hex chars + null terminator)
        char name[32];       // Device name (max 31 chars + null terminator)
        int8_t rssi;         // Signal strength in dBm
        bool valid;          // Whether this entry contains valid data

        BLEDevice() : rssi(-127), valid(false)
        {
            address[0] = '\0';
            name[0] = '\0';
        }

        BLEDevice(const char *addr, const char *n, int8_t r) : rssi(r), valid(true)
        {
            strncpy(address, addr, sizeof(address) - 1);
            address[sizeof(address) - 1] = '\0';
            strncpy(name, n, sizeof(name) - 1);
            name[sizeof(name) - 1] = '\0';
        }
    };
}
