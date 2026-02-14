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
* LAST Modified: 12:44:18 14-02-2026
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
#include "server_control_endpoints.hpp"

bool led_state = false;
bool led_cleared = false;
unsigned long last_toggle = 0;
static unsigned long long iteration = 0;
static unsigned long last_ble_scan = 0;
static unsigned long last_sign_of_life = 0;
static unsigned long last_ble_status_check = 0;

static LED::ColourPos loop_progress[] = {
    { 0, LED::led_get_colour_from_pointer(&LED::Colours::Yellow) },                 // moving dot
    { UINT16_MAX_VALUE, {} }    // sentinel
};

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
    Serial << "Sharing right motor pointer..." << endl;
    SharedDependencies::rightMotor = &food_trap;
    Serial << "Right motor pointer shared" << endl;
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
    static BluetoothLE::BLEHandler bleHandler(BLUETOOTH_BAUDRATE);
    Serial << "Sharing bluetooth handler pointer..." << endl;
    SharedDependencies::bleHandler = &bleHandler;
    Serial << "Bluetooth handler pointer shared" << endl;
    Serial << "Initializing bluetooth..." << endl;
    bleHandler.init();
    Serial << "Enabling bluetooth..." << endl;
    bleHandler.enable();
    Serial << "Granting additional wait time for first boot..." << endl;
    delay(200);  // AT-09 needs ~200-300ms after power-on (enable() already has 100ms)
    // Hardware diagnostics
    Serial << "Testing Hardware..." << endl;
    bleHandler.testHardware();

    // Debug: Uncomment to test different baud rates
    // bleHandler.testBaudRates();

    Serial << "Ble module information..." << endl;
    bleHandler.printStatus();

    // Setup as discoverable peripheral (slave mode)
    Serial << "Configuring as discoverable BLE peripheral..." << endl;
    if (bleHandler.setupSlaveMode(BOARD_NAME)) {
        Serial << "Device is now discoverable as: " << BOARD_NAME << endl;
    } else {
        Serial << "Warning: Slave mode setup failed, device may not be discoverable" << endl;
    }

    Serial << "Serial BT started" << endl;

    // Give a sign of life to the control server
    Serial << "Giving a sign of life to the server" << endl;
    bool broadcast_status = HttpServer::ServerEndpoints::Handler::Put::ip();
    if (broadcast_status) {
        Serial << "Sign of life provided successfully" << endl;
    } else {
        Serial << "Failed to provide a sign of life to the server, is it down?" << endl;
    }

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

void refresh_ble_scan()
{
    if (millis() - last_ble_scan > BLE_SCAN_INTERVAL) {
        last_ble_scan = millis();
        SharedDependencies::bleHandler->printPeriodicScan();

        // Check for BLE connection and handle incoming data
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
    }
}

// Handle incoming BLE data from connected devices
void handle_ble_data()
{
    // Only check if connected
    if (!SharedDependencies::bleHandler->isConnected()) {
        return;
    }

    // Check if data is available (non-blocking)
    if (!SharedDependencies::bleHandler->hasIncomingData()) {
        return;
    }

    // Option 1: Receive as String (easier but allocates memory)
    String received = SharedDependencies::bleHandler->receive();

    // Option 2: Receive into buffer (more efficient, no heap allocation)
    // char buffer[128];
    // size_t bytes_read = SharedDependencies::bleHandler->receive(buffer, sizeof(buffer));
    // if (bytes_read > 0) { /* process buffer */ }

    if (received.length() > 0) {
        Serial << "[BLE Data] Received: " << received << endl;

        // Example: Echo back to the sender
        SharedDependencies::bleHandler->send("Echo: " + received);

        // Example: Handle specific commands
        if (received.indexOf("STATUS") >= 0) {
            SharedDependencies::bleHandler->send("Device: " + String(BOARD_NAME) + ", Ready!");
        } else if (received.indexOf("FEED") >= 0) {
            Serial << "[Command] Feed command received!" << endl;
            SharedDependencies::bleHandler->send("Feeding cat...");
            // TODO: Add your motor control code here
        } else if (received.indexOf("HELLO") >= 0) {
            SharedDependencies::bleHandler->send("Hello from " + String(BOARD_NAME) + "!");
        }
    }
}

void handle_beacons()
{
    Serial << endl << "Scanning to obtain incoming data for " << BLE_PERIODIC_SCAN_DURATION << " ms" << endl;
    bool scan_status = SharedDependencies::bleHandler->startScan(BLE_PERIODIC_SCAN_DURATION);
    if (!scan_status) {
        Serial << "Scan failed or no devices present" << endl;
        return;
    }
    uint8_t device_id = 0;
    uint8_t valid_devices = 0;
    const BluetoothLE::BLEDevice *devices = SharedDependencies::bleHandler->getScannedDevices();
    uint8_t count = SharedDependencies::bleHandler->getDeviceCount();
    for (uint8_t i = 0; i < count; i++) {
        Serial << "Device " << i << ": " << devices[i].address << endl;
        if (devices[i].rssi < BLE_MIN_VALID_RSSI_VALUE) {
            Serial << "The device is to far from the feeder, ignoring" << endl;
            continue;
        }
        Serial << "Sending the server the presence of the beacon" << endl;
        bool status = HttpServer::ServerEndpoints::Handler::Post::visits(devices[i].address);
        if (status) {
            if (valid_devices == 0) {
                device_id = i;
            }
            valid_devices++;
            Serial << "Server presence of beacon updated" << endl;
        } else {
            Serial << "Server presence of beacon failed to update" << endl;
        }
    }
    if (valid_devices == 0) {
        Serial << "No known device is near the feeder, skipping feed check." << endl;
        return;
    }
    if (valid_devices > 1) {
        Serial << "More than once device is available, using the first seen device to know if feeding is possible." << endl;
    }
    long long int distributable_amount = -1;
    bool can_feed = HttpServer::ServerEndpoints::Handler::Get::fed(devices[device_id].address, &distributable_amount);
    if (!can_feed) {
        Serial << "The device is not allowed to feed, ending check." << endl;
        return;
    }
    if (distributable_amount <= 0) {
        Serial << "The device is not allowed food, can distribute is below or equal to 0, distributable_amount value " << distributable_amount << endl;
        return;
    }
    if (distributable_amount > MAX_FEEDING_SINGLE_PORTION) {
        Serial << "Can distribute more than the single portion, clamping to single portion so other portions can still be given during the day." << endl;
        distributable_amount = MAX_FEEDING_SINGLE_PORTION;
    }
    bool feed_update = HttpServer::ServerEndpoints::Handler::Post::fed(devices[device_id].address, distributable_amount);
    if (feed_update) {
        Serial << "Server feeding update successfully sent, distributing." << endl;
    } else {
        Serial << "Failed to send the server update about feeding, skipping distribution." << endl;
        return;
    }
    Serial << "Dispensing food" << endl;
    Serial << "Closing tray" << endl;
    SharedDependencies::leftMotor->turn_right_degrees(90);
    Serial << "Opening food trap" << endl;
    SharedDependencies::rightMotor->turn_left_degrees(90);
    unsigned long now_start = millis();
    unsigned long current = (millis() - now_start);
    while (current <= distributable_amount) {
        current = (millis() - now_start);
        if (current % 10 == 0) {
            Serial << "Dispensing food to tray" << endl;
        }
    }
    Serial << "Food dispensed to tray, closing trap" << endl;
    SharedDependencies::rightMotor->turn_right_degrees(90);
    Serial << "Trap closed, opening tray" << endl;
    SharedDependencies::leftMotor->turn_left_degrees(90);
    Serial << "Tray opened, Bon appetit" << endl;
}

void loop()
{
    unsigned long now = millis();
    static unsigned long last_led_render = 0;

    // Monitor BLE connection status (detects connect/disconnect events)
    SharedDependencies::bleHandler->monitorConnection();

    // Handle incoming BLE data from connected devices (non-AT commands)
    // handle_ble_data();

    // LED updates every 100ms
    if (now - last_led_render >= LED_RENDER_INTERVAL) {
        last_led_render = now;
        MyUtils::ActiveComponents::Panel::tick();
        MyUtils::ActiveComponents::Panel::render();
    }

    if (now - last_ble_status_check >= BLE_STATUS_CHECK_INTERVAL) {
        if (!SharedDependencies::bleHandler->isConnected()) {
            Serial << ".";
            if (SharedDependencies::bleHandler->hasIncomingData()) {
                handle_beacons();
            }
        } else {
            Serial << "A device is connected to the BLE module" << endl;
        }
    }

    // BLE connectivity status check every 10 seconds
    // if (now - last_ble_status_check >= BLE_STATUS_CHECK_INTERVAL) {
    //     last_ble_status_check = now;
    //     Serial << "\n--- BLE Connectivity Check ---" << endl;
    //     SharedDependencies::bleHandler->printConnectionStatus();
    // }

        // BLE periodic scanning (handled by refresh_ble_scan with BLE_SCAN_INTERVAL)
        // refresh_ble_scan();

    // Inform server
    if (now - last_sign_of_life >= SIGNS_OF_LIFE_INTERVAL) {
        last_sign_of_life = now;
        bool broadcast_status = HttpServer::ServerEndpoints::Handler::Put::ip();
        if (broadcast_status) {
            Serial << "Sign of life provided successfully" << endl;
        } else {
            Serial << "Failed to provide a sign of life to the server, is it down?" << endl;
        }
    }

    // Onboard LED blinker
    onboard_blinker();
    // LED::led_set_led_position(5, LED::green_colour, LED_DURATION, true);
    // LED::led_set_led_position(10, LED::led_get_colour_from_pointer(&LED::Colours::Aqua), LED_DURATION, true);
    // LED::led_set_colour(LED::blue_colour, LED_DURATION, 15, LED::black_colour);
    // LED::led_set_colour(LED::led_get_colour_from_pointer(&LED::Colours::Magenta), LED_DURATION, 20, LED::led_get_colour_from_pointer(&LED::Colours::Black));
    SharedDependencies::webServer->handleClient();
    // quick repro in loop()
    increment_iteration();
}
