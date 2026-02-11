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
* FILE: server.cpp
* CREATION DATE: 07-02-2026
* LAST Modified: 23:32:12 11-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the implementation of the endpoints for the http server.
* // AR
* +==== END CatFeeder =================+
*/
#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include "server.hpp"
#include "config.hpp"
#include "ble_handler.hpp"
#include "my_overloads.hpp"

namespace HttpServer
{
    ESP8266WebServer server(SERVER_PORT);
    MyUtils::ActiveComponents::Component blinkIntervalComponent = MyUtils::ActiveComponents::Component::Server;

    // ---------- Handlers ----------

    void handleInfo()
    {
        MyUtils::ActiveComponents::Panel::activity(blinkIntervalComponent, true);
        StaticJsonDocument<256> doc;

        doc["chip"] = "ESP8266";
        doc["chip_id"] = ESP.getChipId();
        doc["flash_size"] = ESP.getFlashChipSize();
        doc["flash_speed"] = ESP.getFlashChipSpeed();
        doc["cpu_freq_mhz"] = ESP.getCpuFreqMHz();
        doc["heap_free"] = ESP.getFreeHeap();
        doc["sdk_version"] = ESP.getSdkVersion();
        doc["ip"] = WiFi.localIP().toString();

        String response;
        serializeJson(doc, response);

        Serial << "Info requested: '" << response << "'" << endl;
        MyUtils::ActiveComponents::Panel::data_transmission(blinkIntervalComponent, 5);
        MyUtils::ActiveComponents::Panel::activity(blinkIntervalComponent, false);
        server.send(200, "application/json", response);
    }

    void handleBlink()
    {
        MyUtils::ActiveComponents::Panel::activity(blinkIntervalComponent, true);
        if (!server.hasArg("plain")) {
            MyUtils::ActiveComponents::Panel::activity(blinkIntervalComponent, false);
            server.send(400, "text/plain", "Missing body");
            return;
        }

        StaticJsonDocument<128> doc;
        DeserializationError err = deserializeJson(doc, server.arg("plain"));

        if (err || !doc["interval"].is<unsigned long>()) {
            Serial << "Failed to parse JSON or missing 'interval'" << endl;
            MyUtils::ActiveComponents::Panel::activity(blinkIntervalComponent, false);
            server.send(400, "text/plain", "Invalid JSON");
            return;
        }

        blinkInterval = doc["interval"];
        Serial << "Blink interval updated to " << blinkInterval << endl;
        MyUtils::ActiveComponents::Panel::activity(blinkIntervalComponent, false);
        server.send(200, "text/plain", "Blink interval updated");
    }

    void getBluetoothStatus()
    {
        MyUtils::ActiveComponents::Panel::activity(blinkIntervalComponent, true);
        StaticJsonDocument<256> doc;
        doc["bluetooth_connected"] = SharedDependencies::bleHandler->isConnected();
        String response;
        serializeJson(doc, response);
        Serial << "Bluetooth status requested: '" << response << "'" << endl;
        MyUtils::ActiveComponents::Panel::data_transmission(blinkIntervalComponent, 3);
        MyUtils::ActiveComponents::Panel::activity(blinkIntervalComponent, false);
        server.send(200, "application/json", response);
    }

    void setupServer()
    {
        server.on("/info", HTTP_GET, handleInfo);
        server.on("/blink", HTTP_POST, handleBlink);
        server.on("/bluetooth_status", HTTP_GET, getBluetoothStatus);
        server.begin();
    }

    void initialize_server()
    {
        setupServer();
        MyUtils::ActiveComponents::Panel::enable(blinkIntervalComponent);
    }
}
