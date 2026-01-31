#pragma once
#include <Arduino.h>
#include <esp8266_peri.h>

namespace Pins
{
    constexpr uint8_t LED_PIN = 2;   // onboard LED = D2, GPIO2
    constexpr uint8_t LED_STRIP_PIN = 5;   // D1 = GPIO5
    constexpr uint8_t MOTOR1_PIN = 14;  // D5 = GPIO14
    constexpr uint8_t MOTOR2_PIN = 16;   // Servo 2 (D0, GPIO16) -> software PWM
    constexpr uint8_t BLE_RXD_PIN = 13;  // D7 = GPIO13
    constexpr uint8_t BLE_TXD_PIN = 12;  // D6 = GPIO12
    constexpr uint8_t BLE_EN_PIN = 4;   // D2 = GPIO4
    constexpr uint8_t BLE_STATE_PIN = A0;  // ADC0

    static inline void init()
    {
        // Set pin modes if necessary
        pinMode(LED_PIN, OUTPUT);
        digitalWrite(LED_PIN, HIGH); // LED off (active LOW)
        pinMode(LED_STRIP_PIN, OUTPUT);
        pinMode(MOTOR1_PIN, OUTPUT);
        pinMode(MOTOR2_PIN, OUTPUT);
        pinMode(BLE_EN_PIN, OUTPUT);
        digitalWrite(BLE_EN_PIN, LOW);   // default off
        pinMode(BLE_STATE_PIN, INPUT);
    }
} // namespace Pins

