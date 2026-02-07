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
* FILE: shared_dependencies.hpp
* CREATION DATE: 07-02-2026
* LAST Modified: 1:48:28 07-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the code used for tracking shared dependencies that should be available througout the program.
* // AR
* +==== END CatFeeder =================+
*/
#pragma once
#include "leds.hpp"
#include "motors.hpp"
#include "server.hpp"
#include "ble_handler.hpp"
#include "wifi_handler.hpp"

struct SharedDependencies {
    static Motors::Motor *leftMotor;
    static Motors::Motor *rightMotor;
    static Wifi::WifiHandler *wifiHandler;
    static BluetoothLE::BLEHandler *bleHandler;
};
