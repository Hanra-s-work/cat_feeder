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
* FILE: ble_enums.hpp
* CREATION DATE: 11-02-2026
* LAST Modified: 20:30:4 11-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: These are the enums used by the BLE handler.
* // AR
* +==== END CatFeeder =================+
*/
#pragma once

namespace BluetoothLE
{
    enum class BLERole {
        Unknown = -1,
        Slave = 0,      // Peripheral mode (default)
        Master = 1      // Central mode (required for scanning)
    };

    enum class ATCommandResult {
        OK,
        ERROR,
        TIMEOUT,
        UNKNOWN
    };

}
