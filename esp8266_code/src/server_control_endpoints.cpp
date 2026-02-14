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
* LAST Modified: 10:11:50 14-02-2026
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


bool HttpServer::ServerEndpoints::Handler::Get::fed(const char *beacon_mac)
{
    char body[256];
    snprintf(body, sizeof(body), "{\"beacon_mac\":\"%s\"}", beacon_mac);
    WiFiClient client;
    char url[256];
    snprintf(url, sizeof(url), "%s%s", CONTROL_SERVER, HttpServer::ServerEndpoints::Url::Get::FED.data());
    SharedDependencies::webClient->begin(client, url);
    SharedDependencies::webClient->addHeader("Content-Type", "application/json");
    int httpCode = SharedDependencies::webClient->sendRequest("GET", body);
    SharedDependencies::webClient->end();
    if (httpCode == 200) {
        Serial << "GET fed successful for beacon: " << beacon_mac << endl;
        return true; // Assuming 200 means fed/allowed
    } else {
        Serial << "GET fed failed for beacon: " << beacon_mac << " code: " << httpCode << endl;
        return false;
    }
}

bool HttpServer::ServerEndpoints::Handler::Post::fed(const char *beacon_mac)
{
    getCachedMac();
    char body[256];
    snprintf(body, sizeof(body), "{\"beacon_mac\":\"%s\",\"feeder_mac\":\"%s\"}", beacon_mac, mac_buffer);
    WiFiClient client;
    char url[256];
    snprintf(url, sizeof(url), "%s%s", CONTROL_SERVER, HttpServer::ServerEndpoints::Url::Post::FED.data());
    SharedDependencies::webClient->begin(client, url);
    SharedDependencies::webClient->addHeader("Content-Type", "application/json");
    int httpCode = SharedDependencies::webClient->POST(body);
    SharedDependencies::webClient->end();
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
    if (httpCode == 200) {
        Serial << "POST location successful for beacon: " << beacon_mac << endl;
        return true;
    } else {
        Serial << "POST location failed for beacon: " << beacon_mac << " code: " << httpCode << endl;
        return false;
    }
}

bool HttpServer::ServerEndpoints::Handler::Post::visits(const char *beacon_mac)
{
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
    if (httpCode == 200) {
        Serial << "PUT ip successful" << endl;
        return true;
    } else {
        Serial << "PUT ip failed code: " << httpCode << endl;
        return false;
    }
}
