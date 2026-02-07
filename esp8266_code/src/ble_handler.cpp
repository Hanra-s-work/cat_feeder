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
* FILE: ble_handler.cpp
* CREATION DATE: 07-02-2026
* LAST Modified: 1:49:58 07-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the implementation for the ble library.
* // AR
* +==== END CatFeeder =================+
*/
#include "ble_handler.hpp"

BluetoothLE::BLEHandler::BLEHandler(uint32_t baud)
    : _serial(Pins::BLE_RXD_PIN, Pins::BLE_TXD_PIN), _baud(baud)
{
}

void BluetoothLE::BLEHandler::init()
{
    pinMode(Pins::BLE_EN_PIN, OUTPUT);
    digitalWrite(Pins::BLE_EN_PIN, LOW);  // default off
    pinMode(Pins::BLE_STATE_PIN, INPUT);

    _serial.begin(_baud);
    MyUtils::ActiveComponents::Panel::enable(_ble_component);
}

void BluetoothLE::BLEHandler::enable()
{
    digitalWrite(Pins::BLE_EN_PIN, HIGH);
    delay(50);  // let the module power up
    MyUtils::ActiveComponents::Panel::enable(_ble_component);
}

void BluetoothLE::BLEHandler::disable()
{
    digitalWrite(Pins::BLE_EN_PIN, LOW);
    MyUtils::ActiveComponents::Panel::disable(_ble_component);
}

bool BluetoothLE::BLEHandler::isConnected() const
{
    const bool status = digitalRead(Pins::BLE_STATE_PIN) == HIGH;
    MyUtils::ActiveComponents::Panel::activity(_ble_component, status);
    return status;
}

void BluetoothLE::BLEHandler::send(const String &data)
{
    MyUtils::ActiveComponents::Panel::activity(_ble_component, true);
    _serial.print(data);

    // flash a dot to indicate sending
    const unsigned int size_raw = data.length();
    uint8_t size;
    if (size_raw == 0) {
        size = 1;
    } else if (size_raw > 255) {
        size = 255;
    } else {
        size = static_cast<uint8_t>(size_raw);
    }
    MyUtils::ActiveComponents::Panel::data_transmission(_ble_component, size);
    MyUtils::ActiveComponents::Panel::activity(_ble_component, false);

}

String BluetoothLE::BLEHandler::receive()
{
    MyUtils::ActiveComponents::Panel::activity(_ble_component, true);
    String received;
    while (_serial.available()) {
        char c = _serial.read();
        received += c;
        MyUtils::ActiveComponents::Panel::data_transmission(_ble_component, 1);
    }
    MyUtils::ActiveComponents::Panel::activity(_ble_component, false);
    return received;
}
