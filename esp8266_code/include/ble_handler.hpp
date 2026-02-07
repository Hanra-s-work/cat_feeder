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
* FILE: ble_handler.hpp
* CREATION DATE: 07-02-2026
* LAST Modified: 1:43:39 07-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the headeer for the bluetooth module overlay for handling detection of ble devices.
* // AR
* +==== END CatFeeder =================+
*/
#pragma once
#include <Arduino.h>
#include <SoftwareSerial.h>
#include "leds.hpp"
#include "colours.hpp"
#include "pins.hpp"
#include "sentinels.hpp"
#include "active_components.hpp"

namespace BluetoothLE
{
    class BLEHandler {
        public:
        BLEHandler(uint32_t baud = 9600);

        void init();            // setup pins and serial
        void enable();          // turn on BLE module
        void disable();         // turn off BLE module
        bool isConnected() const;   // read BLE_STATE pin
        void send(const String &data);  // send string over BLE
        String receive();            // read available data

        private:
        SoftwareSerial _serial;
        uint32_t _baud;
        MyUtils::ActiveComponents::Component _ble_component = MyUtils::ActiveComponents::Component::Bluetooth;
        uint16_t _led_index = 0;   // for moving dot animation
    };
}
