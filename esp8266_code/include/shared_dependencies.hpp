#pragma once
#include "leds.hpp"
#include "motors.hpp"
#include "server.hpp"
#include "ble_handler.hpp"
#include "wifi_handler.hpp"

struct SharedDependencies {
    static Motors::Motor *leftMotor;
    static Motors::Motor *rightMotor;
    static Wifi::WifiHandler *wifiHandler;
    static BluetoothLE::BLEHandler *bleHandler;
};
