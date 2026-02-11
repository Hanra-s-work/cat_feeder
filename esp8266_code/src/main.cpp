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
* FILE: main.cpp
* CREATION DATE: 07-02-2026
* LAST Modified: 23:5:55 11-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the main file of the program, where the setup and loop occurs.
* // AR
* +==== END CatFeeder =================+
*/
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include "my_overloads.hpp"
#include "ntfy.hpp"
#include "leds.hpp"
#include "config.hpp"
#include "server.hpp"
#include "motors.hpp"
#include "my_utils.hpp"
#include "ble_handler.hpp"
#include "wifi_handler.hpp"
#include "shared_dependencies.hpp"

bool led_state = false;
unsigned long last_toggle = 0;
static unsigned long long iteration = 0;
static unsigned long last_ble_scan = 0;
bool led_cleared = false;

static LED::ColourPos loop_progress[] = {
    { 0, LED::led_get_colour_from_pointer(&LED::Colours::Yellow) },                 // moving dot
    { UINT16_MAX_VALUE, {} }    // sentinel
};

void initial_ble_scan()
{
    const bool scan_response = SharedDependencies::bleHandler->startScan(5000);
    if (scan_response) {  // 5 second scan
        const uint8_t deviceCount = SharedDependencies::bleHandler->getDeviceCount();
        const uint8_t overflow = SharedDependencies::bleHandler->getOverflowCount();
        const BluetoothLE::BLEDevice *devices = SharedDependencies::bleHandler->getScannedDevices();

        Serial << "Found " << deviceCount << " BLE devices:" << endl;
        for (uint8_t i = 0; i < deviceCount; i++) {
            Serial << " - " << devices[i].address;
            if (devices[i].name.length() > 0) {
                Serial << "(" << devices[i].name << ")";
            }
            Serial << " RSSI: " << devices[i].rssi << " dBm" << endl;
        }

        if (overflow > 0) {
            Serial << "WARNING: " << overflow << " devices were not captured (buffer full)" << endl;
        }
    } else {
        Serial << "No devices found or scan failed" << endl;
    }
}


void setup()
{
    // Set up the pins to prevent accidental floating/flashing states
    // ─────────────── Pins & Serial ───────────────
    Pins::init();

    Serial.begin(SERIAL_BAUDRATE);
    Serial << "Starting up..." << endl;
    delay(100);

    // ─────────────── LED Initialization ───────────────
    Serial << "Initializing LEDs..." << endl;
    LED::led_init();
    LED::Nodes::set_pos_step(loop_progress[0], 0);
    // Set up the cycle led animation
    Serial << "Setting up LED cycle animation..." << endl;
    MyUtils::ActiveComponents::initialise_active_components();
    Serial << "LED cycle animation set up complete" << endl;
    Serial << "LEDs initialized" << endl;

    // ─────────────── WiFi ───────────────
    Serial << "Initializing WiFi..." << endl;
    LED::ColourPos wifi_anim[] = {
        {0, LED::green_colour},
        {UINT16_MAX_VALUE, {}}
    };
    LED::Nodes::set_pos_step(wifi_anim[0], 0);

    static Wifi::WifiHandler wifiHandler(SSID, SSID_PASSWORD, LED::dark_blue, wifi_anim);
    Serial << "Sharing WiFi handler pointer..." << endl;
    SharedDependencies::wifiHandler = &wifiHandler;
    Serial << "WiFi handler pointer shared" << endl;
    Serial << "Setting up WiFi handler..." << endl;
    wifiHandler.init();
    Serial << "Connecting to WiFi..." << endl;
    wifiHandler.connect();
    Serial << "WiFi initialized" << endl;


    Serial << "Unveiling IP..." << endl;
    LED::led_set_colour(LED::red_colour, LED_DURATION, -1);
    send_ip_to_ntfy();
    LED::led_set_colour(LED::yellow_colour, LED_DURATION, -1);
    Serial << "\nConnected!" << endl;
    wifiHandler.showIp();

    // ─────────────── Motors ───────────────
    Serial << "Initializing motors..." << endl;
    Serial << "Declaring left motor..." << endl;
    static Motors::Motor kibble_tray(Pins::MOTOR1_PIN, loop_progress, MOTOR_SPEED_DEFAULT, LED::dark_blue, LED::red_colour, MyUtils::ActiveComponents::Component::MotorLeft);
    Serial << "Left motor declared" << endl;
    Serial << "Sharing left motor pointer..." << endl;
    SharedDependencies::leftMotor = &kibble_tray;
    Serial << "Left motor pointer shared" << endl;
    Serial << "Initialising left motor..." << endl;
    kibble_tray.init();
    Serial << "Running test turn on left motor..." << endl;
    kibble_tray.calibrate();
    Serial << "Left motor initialized" << endl;

    Serial << "Initializing right motor..." << endl;
    static Motors::Motor food_trap(Pins::MOTOR2_PIN, loop_progress, MOTOR_SPEED_DEFAULT, LED::dark_blue, LED::red_colour, MyUtils::ActiveComponents::Component::MotorRight);
    Serial << "Rigth motor declared" << endl;
    Serial << "Sharing left motor pointer..." << endl;
    SharedDependencies::rightMotor = &food_trap;
    Serial << "Left motor pointer shared" << endl;
    Serial << "Initialising right motor..." << endl;
    food_trap.init();
    Serial << "Right motor initialized" << endl;
    Serial << "Running test turn on right motor..." << endl;
    food_trap.calibrate();
    Serial << "Right motor initialized" << endl;

    // ─────────────── HTTP Server ───────────────
    Serial << "Starting HTTP server..." << endl;
    HttpServer::initialize_server();
    Serial << "HTTP server started" << endl;
    LED::led_set_colour(LED::blue_colour, LED_DURATION, -1);

    // ─────────────── Bluetooth ───────────────
    Serial << "Setting up bluetooth..." << endl;
    BluetoothLE::BLEHandler bleHandler(BLUETOOTH_BAUDRATE);
    Serial << "Sharing bluetooth handler pointer..." << endl;
    SharedDependencies::bleHandler = &bleHandler;
    Serial << "Bluetooth handler pointer shared" << endl;
    Serial << "Initializing bluetooth..." << endl;
    bleHandler.init();
    Serial << "Enabling bluetooth..." << endl;
    bleHandler.enable();
    Serial << "Ble module information..." << endl;
    bleHandler.printStatus();
    Serial << "Running initial scan..." << endl;
    initial_ble_scan();
    Serial << "Serial BT started" << endl;

    // Final render to clear all setup artifacts
    Serial << "Clearing setup artifacts..." << endl;
    MyUtils::ActiveComponents::Panel::render();
    Serial << "Setup complete - entering main loop" << endl;
}

void onboard_blinker()
{
    uint32_t now = millis();
    if (now - last_toggle >= blinkInterval) {
        last_toggle = now;
        led_state = !led_state;
        digitalWrite(Pins::LED_PIN, led_state ? LOW : HIGH);
    }
}

void increment_iteration()
{
    if (iteration + 1 == UINT32_MAX_VALUE) {
        Serial << "Iteration counter overflow imminent, resetting to 0" << endl;
        iteration = 0;
    } else {
        iteration++;
    }
}

void display_ble_connection_status()
{
    Serial << "Checking BLE connection status" << endl;
    const BluetoothLE::ATCommandResult ble_status = SharedDependencies::bleHandler->testConnection();
    Serial << "Connection status: ";
    if (ble_status == BluetoothLE::ATCommandResult::OK) {
        Serial << "[OK]" << endl;
    } else if (ble_status == BluetoothLE::ATCommandResult::TIMEOUT) {
        Serial << "[TIMEOUT]" << endl;
    } else if (ble_status == BluetoothLE::ATCommandResult::ERROR) {
        Serial << "[ERROR]" << endl;
    } else if (ble_status == BluetoothLE::ATCommandResult::UNKNOWN) {
        Serial << "[UNKNOWN]" << endl;
    } else {
        Serial << "[UKNOWN TYPE]" << endl;
    }
}

bool refresh_ble_scan()
{
    if (millis() - last_ble_scan > BLE_SCAN_INTERVAL) {
        last_ble_scan = millis();
        Serial << "\n--- Periodic BLE Scan ---" << endl;
        SharedDependencies::bleHandler->startScan(BLE_PERIODIC_SCAN_DURATION);

        uint8_t count = SharedDependencies::bleHandler->getDeviceCount();
        uint8_t overflow = SharedDependencies::bleHandler->getOverflowCount();
        Serial << "Detected " << count << " nearby devices" << endl;
        if (overflow > 0) {
            Serial << "Lost " << overflow << " devices (increase MAX_BLE_DEVICES if needed)" << endl;
        }
    } else {
        return false;
    }

    // Check for BLE connection status
    const bool ble_status = SharedDependencies::bleHandler->isConnected();
    if (ble_status) {
        String received = SharedDependencies::bleHandler->receive();
        if (received.length() > 0) {
            Serial << "Received over Bluetooth: " << received << endl;

            // Example: respond to commands
            if (received.indexOf("SCAN") >= 0) {
                Serial << "Command received: Starting scan..." << endl;
                SharedDependencies::bleHandler->startScan(5000);

                // Send results back via BLE
                uint8_t count = SharedDependencies::bleHandler->getDeviceCount();
                const BluetoothLE::BLEDevice *devices = SharedDependencies::bleHandler->getScannedDevices();

                Serial << "Found " << count << " devices" << endl;
                for (uint8_t i = 0; i < count; i++) {
                    Serial << devices[i].address << endl;
                }

                uint8_t overflow = SharedDependencies::bleHandler->getOverflowCount();
                if (overflow > 0) {
                    Serial << "Lost: " << overflow << endl;
                }
            } else if (received.indexOf("STATUS") >= 0) {
                SharedDependencies::bleHandler->printStatus();
            } else if (received.indexOf("CONNECT:") >= 0) {
                // Extract MAC address (e.g., "CONNECT:001122334455")
                String address = received.substring(8);
                address.trim();
                if (SharedDependencies::bleHandler->connectToDevice(address)) {
                    SharedDependencies::bleHandler->send("Connected to " + address);
                } else {
                    SharedDependencies::bleHandler->send("Connection failed");
                }
            }
        }
    }
    return true;
}

void loop()
{
    if (iteration % 1000 == 0) {
        // Serial << "In main loop, iteration: " << iteration << endl;
        MyUtils::ActiveComponents::Panel::tick();
        MyUtils::ActiveComponents::Panel::render();
        display_ble_connection_status();
        bool refreshed = refresh_ble_scan();
        if (refreshed) {
            Serial << "BLE Scan refreshed" << endl;
        } else {
            Serial << "BLE Scan not refreshed" << endl;
        }
        // MyUtils::ActiveComponents::Panel::debug_print_commands();
        // if (!led_cleared) {
        //     LED::led_clear();
        //     led_cleared = true;
        // }
        onboard_blinker();
    }
    // LED::led_set_led_position(5, LED::green_colour, LED_DURATION, true);
    // LED::led_set_led_position(10, LED::led_get_colour_from_pointer(&LED::Colours::Aqua), LED_DURATION, true);
    // LED::led_set_colour(LED::blue_colour, LED_DURATION, 15, LED::black_colour);
    // LED::led_set_colour(LED::led_get_colour_from_pointer(&LED::Colours::Magenta), LED_DURATION, 20, LED::led_get_colour_from_pointer(&LED::Colours::Black));
    HttpServer::server.handleClient();
    // quick repro in loop()
    increment_iteration();
}
