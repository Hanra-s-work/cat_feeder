#pragma once
#include <ESP8266WebServer.h>
#include "active_components.hpp"
#include "shared_dependencies.hpp"

namespace HttpServer
{
    extern ESP8266WebServer server; // declared in server.cpp
    extern MyUtils::ActiveComponents::Component blinkIntervalComponent;

    void initialize_server();
    void setupServer();
    void handleInfo();
    void handleBlink();
}
