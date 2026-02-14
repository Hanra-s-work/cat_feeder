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
* LAST Modified: 10:11:12 14-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the base implementation for the shared dependencies.
* // AR
* +==== END CatFeeder =================+
*/
#include "shared_dependencies.hpp"
#include "config.hpp"

// Initialize shared instances
static HTTPClient httpClient;
static ESP8266WebServer webServerInstance(SERVER_PORT);

HTTPClient *SharedDependencies::webClient = &httpClient;
ESP8266WebServer *SharedDependencies::webServer = &webServerInstance;
Motors::Motor *SharedDependencies::leftMotor = nullptr;
Motors::Motor *SharedDependencies::rightMotor = nullptr;
Wifi::WifiHandler *SharedDependencies::wifiHandler = nullptr;
BluetoothLE::BLEHandler *SharedDependencies::bleHandler = nullptr;
