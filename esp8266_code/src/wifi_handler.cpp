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
* FILE: wifi_handler.cpp
* CREATION DATE: 07-02-2026
* LAST Modified: 23:44:38 11-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the implementation for the wifi handler.
* // AR
* +==== END CatFeeder =================+
*/
#include "wifi_handler.hpp"
#include <ESP8266WiFi.h>
#include <sstream>
#include <iomanip>
#include "sentinels.hpp"


Wifi::WifiHandler::WifiHandler(const char *ssid_, const char *password_, const LED::Colour &background_, LED::ColourPos *animArray_)
    : ssid(ssid_), password(password_), background(background_), wifi_anim(animArray_), wifi_anim_length(LED::led_colourpos_length(animArray_))
{
    if (wifi_anim) {
        wifi_anim[0].pos = 0;
    }
}

void Wifi::WifiHandler::init()
{
    Serial << "Connecting to WiFi..." << endl;
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
}

void Wifi::WifiHandler::connect()
{
    uint16_t connect_attempts = 0;
    Serial.print("Checking status: ");
    while (WiFi.status() != WL_CONNECTED) {
        delay(WIFI_RETRY_DELAY);
        Serial.print(".");
        connect_attempts++;
        LED::led_fancy(wifi_anim, wifi_anim_length, background, 100);
        wifi_anim[0].pos = (wifi_anim[0].pos + 1);
        if (connect_attempts >= LED_NUMBER) {
            connect_attempts = 0;
            wifi_anim[0].pos = 0;
        }
    }
    Serial << "\nWiFi connected" << endl;
    LED::led_set_colour(wifi_anim->colour, LED_DURATION, -1);
    MyUtils::ActiveComponents::Panel::enable(WIFI_COMPONENT);
}

void Wifi::WifiHandler::showIp()
{
    IPAddress ip = getIP();
    Serial << "Device IP Address: " << ip.v4() << endl;
    LED::led_set_colour(wifi_anim->colour, LED_DURATION, -1);
}

IPAddress Wifi::WifiHandler::getIP() const
{
    return WiFi.localIP();
}


std::string Wifi::WifiHandler::to_hex(uint32_t value)
{
    MyUtils::ActiveComponents::Panel::activity(Wifi::WIFI_COMPONENT, true);
    std::ostringstream oss;
    oss << std::hex << std::nouppercase << value;
    MyUtils::ActiveComponents::Panel::activity(Wifi::WIFI_COMPONENT, false);
    return oss.str();
}

std::string Wifi::WifiHandler::getChipId()
{
    // ESP8266: lower 24 bits of base MAC
    uint32_t chipId = ESP.getChipId();
    return to_hex(chipId);
}

std::string Wifi::WifiHandler::getFlashChipId()
{
    uint32_t flashId = ESP.getFlashChipId();
    return to_hex(flashId);
}

std::string Wifi::WifiHandler::getFingerprint()
{
    MyUtils::ActiveComponents::Panel::activity(WIFI_COMPONENT, true);
    std::ostringstream oss;

    oss << "esp8266-"
        << getChipId()
        << "-"
        << getFlashChipId();
    MyUtils::ActiveComponents::Panel::activity(WIFI_COMPONENT, false);
    return oss.str();
}
