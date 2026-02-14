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
* FILE: server_control_endpoints.cpp
* CREATION DATE: 14-02-2026
* LAST Modified: 12:30:12 14-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: Implementation of server control endpoints for communicating with the central server.
* // AR
* +==== END CatFeeder =================+
*/
#include <ESP8266WiFi.h>
#include <cstring>
#include <ArduinoJson.h>
#include "config.hpp"
#include "my_overloads.hpp"
#include "shared_dependencies.hpp"
#include "server_control_endpoints.hpp"

// Cache for MAC address to reduce memory fragmentation
static char mac_buffer[18] = { 0 };

// Cache for IP address
static char ip_buffer[16] = { 0 };

// Helper to get cached MAC
const char *getCachedMac()
{
    if (mac_buffer[0] == '\0') {
        String macStr = SharedDependencies::wifiHandler->getMacAddress();
        strcpy(mac_buffer, macStr.c_str());
    }
    return mac_buffer;
}

// Helper to get cached IP
const char *getCachedIp()
{
    if (ip_buffer[0] == '\0') {
        IPAddress ip = SharedDependencies::wifiHandler->getIP();
        sprintf(ip_buffer, "%d.%d.%d.%d", ip[0], ip[1], ip[2], ip[3]);
    }
    return ip_buffer;
}


bool HttpServer::ServerEndpoints::Handler::Get::fed(const char *beacon_mac, long long int *can_distribute)
{
    MyUtils::ActiveComponents::Panel::activity(blinkIntervalComponent, true);
    char body[256];
    snprintf(body, sizeof(body), "{\"beacon_mac\":\"%s\"}", beacon_mac);
    WiFiClient client;
    char url[256];
    snprintf(url, sizeof(url), "%s%s", CONTROL_SERVER, HttpServer::ServerEndpoints::Url::Get::FED.data());
    SharedDependencies::webClient->begin(client, url);
    SharedDependencies::webClient->addHeader("Content-Type", "application/json");
    int httpCode = SharedDependencies::webClient->sendRequest("GET", body);
    if (httpCode == 200) {
        String response = SharedDependencies::webClient->getString();
        StaticJsonDocument<256> doc;
        DeserializationError err = deserializeJson(doc, response);
        SharedDependencies::webClient->end();
        if (err) {
            Serial << "JSON parse error for beacon: " << beacon_mac << endl;
            return false;
        }
        long long int food_eaten = doc["food_eaten"];
        long long int food_max = doc["food_max"];
        bool can_distribute_check = doc["can_distribute"];
        *can_distribute = food_max - food_eaten;
        MyUtils::ActiveComponents::Panel::activity(blinkIntervalComponent, false);
        if (food_eaten < food_max && can_distribute_check) {
            Serial << "Can feed beacon: " << beacon_mac << " (eaten " << food_eaten << " < max " << food_max << "), can_distribute " << can_distribute_check << endl;
            return true;
        } else {
            Serial << "Cannot feed beacon: " << beacon_mac << " (eaten " << food_eaten << " >= max " << food_max << "), can_distribute " << can_distribute_check << endl;
            *can_distribute = -1;
            return false;
        }
    } else {
        SharedDependencies::webClient->end();
        MyUtils::ActiveComponents::Panel::activity(blinkIntervalComponent, false);
        Serial << "GET fed failed for beacon: " << beacon_mac << " code: " << httpCode << endl;
        *can_distribute = -1;
        return false;
    }
}

bool HttpServer::ServerEndpoints::Handler::Post::fed(const char *beacon_mac, const unsigned long food_amount)
{
    MyUtils::ActiveComponents::Panel::activity(blinkIntervalComponent, true);
    getCachedMac();
    char body[256];
    snprintf(body, sizeof(body), "{\"beacon_mac\":\"%s\",\"feeder_mac\":\"%s\",\"amount\":%lu}", beacon_mac, mac_buffer, food_amount);
    WiFiClient client;
    char url[256];
    snprintf(url, sizeof(url), "%s%s", CONTROL_SERVER, HttpServer::ServerEndpoints::Url::Post::FED.data());
    SharedDependencies::webClient->begin(client, url);
    SharedDependencies::webClient->addHeader("Content-Type", "application/json");
    int httpCode = SharedDependencies::webClient->POST(body);
    SharedDependencies::webClient->end();
    MyUtils::ActiveComponents::Panel::activity(blinkIntervalComponent, false);
    if (httpCode == 200) {
        Serial << "POST fed successful for beacon: " << beacon_mac << endl;
        return true;
    } else {
        Serial << "POST fed failed for beacon: " << beacon_mac << " code: " << httpCode << endl;
        return false;
    }
}

bool HttpServer::ServerEndpoints::Handler::Post::location(const char *beacon_mac)
{
    MyUtils::ActiveComponents::Panel::activity(blinkIntervalComponent, true);
    getCachedMac();
    char body[256];
    snprintf(body, sizeof(body), "{\"beacon_mac\":\"%s\",\"feeder_mac\":\"%s\"}", beacon_mac, mac_buffer);
    WiFiClient client;
    char url[256];
    snprintf(url, sizeof(url), "%s%s", CONTROL_SERVER, HttpServer::ServerEndpoints::Url::Post::LOCATION.data());
    SharedDependencies::webClient->begin(client, url);
    SharedDependencies::webClient->addHeader("Content-Type", "application/json");
    int httpCode = SharedDependencies::webClient->POST(body);
    SharedDependencies::webClient->end();
    MyUtils::ActiveComponents::Panel::activity(blinkIntervalComponent, false);
    if (httpCode == 200) {
        Serial << "POST location successful for beacon: " << beacon_mac << endl;
        return true;
    } else {
        Serial << "POST location failed for beacon: " << beacon_mac << " code: " << httpCode << endl;
        return false;
    }
}

bool HttpServer::ServerEndpoints::Handler::Post::
visits(const char *beacon_mac)
{
    MyUtils::ActiveComponents::Panel::activity(blinkIntervalComponent, true);
    getCachedMac();
    char body[256];
    snprintf(body, sizeof(body), "{\"beacon_mac\":\"%s\",\"feeder_mac\":\"%s\"}", beacon_mac, mac_buffer);
    WiFiClient client;
    char url[256];
    snprintf(url, sizeof(url), "%s%s", CONTROL_SERVER, HttpServer::ServerEndpoints::Url::Post::VISITS.data());
    SharedDependencies::webClient->begin(client, url);
    SharedDependencies::webClient->addHeader("Content-Type", "application/json");
    int httpCode = SharedDependencies::webClient->POST(body);
    SharedDependencies::webClient->end();
    MyUtils::ActiveComponents::Panel::activity(blinkIntervalComponent, false);
    if (httpCode == 200) {
        Serial << "POST visits successful for beacon: " << beacon_mac << endl;
        return true;
    } else {
        Serial << "POST visits failed for beacon: " << beacon_mac << " code: " << httpCode << endl;
        return false;
    }
}
bool HttpServer::ServerEndpoints::Handler::Put::ip()
{
    MyUtils::ActiveComponents::Panel::activity(blinkIntervalComponent, true);
    getCachedMac();
    getCachedIp();
    char body[256];
    snprintf(body, sizeof(body), "{\"mac\":\"%s\",\"ip\":\"%s\"}", mac_buffer, ip_buffer);
    WiFiClient client;
    char url[256];
    snprintf(url, sizeof(url), "%s%s", CONTROL_SERVER, HttpServer::ServerEndpoints::Url::Put::IP.data());
    SharedDependencies::webClient->begin(client, url);
    SharedDependencies::webClient->addHeader("Content-Type", "application/json");
    int httpCode = SharedDependencies::webClient->PUT(body);
    SharedDependencies::webClient->end();
    MyUtils::ActiveComponents::Panel::activity(blinkIntervalComponent, false);
    if (httpCode == 200) {
        Serial << "PUT ip successful" << endl;
        return true;
    } else {
        Serial << "PUT ip failed code: " << httpCode << endl;
        return false;
    }
}
