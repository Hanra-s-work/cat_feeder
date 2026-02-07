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
* FILE: wifi_handler.hpp
* CREATION DATE: 07-02-2026
* LAST Modified: 1:49:8 07-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the module for handling wifi connections.
* // AR
* +==== END CatFeeder =================+
*/
#pragma once
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include "leds.hpp"
#include "colours.hpp"
#include "sentinels.hpp"
#include "active_components.hpp"

namespace Wifi
{
    static constexpr MyUtils::ActiveComponents::Component WIFI_COMPONENT = MyUtils::ActiveComponents::Component::WifiStatus;
    class WifiHandler {
        public:
        WifiHandler(
            const char *ssid, const char *password,
            const LED::Colour &background, LED::ColourPos *animArray
        );
        void init();
        void connect(); // starts Wi-Fi and shows animation
        void showIp(); // print the IP to the serial monitor
        IPAddress getIP() const;
        /**
         * @brief Convert a 32-bit value to a lowercase hex string.
         */
        static inline std::string to_hex(uint32_t value);
        /**
         * @brief Returns the ESP8266 MAC address as a formatted string.
         *
         * Example: "18:FE:34:12:AB:CD"
         */
        static inline String getMacAddress()
        {
            return WiFi.macAddress();
        }
        /**
         * @brief Get the ESP8266 Chip ID.
         *
         * Derived from the base MAC address (lower 24 bits).
         * Not globally unique, but stable per device.
         *
         * @return std::string Hexadecimal string (e.g. "1A2B3C").
         */
        static inline std::string getChipId();

        /**
         * @brief Get the flash chip identifier.
         *
         * Encodes manufacturer and flash characteristics.
         * Not unique on its own.
         *
         * @return std::string Hexadecimal string (e.g. "1640EF").
         */
        static inline std::string getFlashChipId();

        /**
         * @brief Get a composite device fingerprint.
         *
         * Combines ChipID + FlashChipID into a single stable identifier.
         * Suitable for server-side identification during development.
         *
         * @return std::string Fingerprint string.
         *         Example: "esp8266-1a2b3c-1640ef"
         */
        static inline std::string getFingerprint();

        private:

        const char *ssid;
        const char *password;
        const LED::Colour &background;
        LED::ColourPos *wifi_anim;
        size_t wifi_anim_length;
    };
}
