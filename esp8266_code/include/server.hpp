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
* FILE: server.hpp
* CREATION DATE: 07-02-2026
* LAST Modified: 10:11:15 14-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: The is the code used for the server overlay.
* // AR
* +==== END CatFeeder =================+
*/
#pragma once
#include <ESP8266WebServer.h>
#include "active_components.hpp"
#include "shared_dependencies.hpp"

namespace HttpServer
{
    extern ESP8266WebServer *server; // now a pointer to shared instance
    extern MyUtils::ActiveComponents::Component blinkIntervalComponent;

    void initialize_server();
    void setupServer();
    void handleInfo();
    void handleBlink();
}
