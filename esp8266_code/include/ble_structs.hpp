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
* LAST Modified: 21:26:25 11-02-2026
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
        String address;      // MAC address (e.g., "001122334455")
        String name;         // Device name (if available)
        int8_t rssi;        // Signal strength in dBm
        bool valid;         // Whether this entry contains valid data

        BLEDevice() : address(""), name(""), rssi(-127), valid(false) {}
        BLEDevice(const String &addr, const String &n, int8_t r)
            : address(addr), name(n), rssi(r), valid(true)
        {
        }
    };
}
