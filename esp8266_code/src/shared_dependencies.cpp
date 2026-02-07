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
* FILE: shared_dependencies.cpp
* CREATION DATE: 07-02-2026
* LAST Modified: 1:52:52 07-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the base implementation for the shared dependencies.
* // AR
* +==== END CatFeeder =================+
*/
#include "shared_dependencies.hpp"

Motors::Motor *SharedDependencies::leftMotor = nullptr;
Motors::Motor *SharedDependencies::rightMotor = nullptr;
Wifi::WifiHandler *SharedDependencies::wifiHandler = nullptr;
BluetoothLE::BLEHandler *SharedDependencies::bleHandler = nullptr;
