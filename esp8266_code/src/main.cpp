#include <Arduino.h>
#include <ESP8266WiFi.h>
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
bool led_cleared = false;

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
    Serial.println("Starting up...");
    delay(100);

    // ─────────────── LED Initialization ───────────────
    Serial.println("Initializing LEDs...");
    LED::led_init();
    LED::Nodes::set_pos_step(loop_progress[0], 0);
    // Set up the cycle led animation
    Serial.println("Setting up LED cycle animation...");
    MyUtils::ActiveComponents::initialise_active_components();
    Serial.println("LED cycle animation set up complete");
    Serial.println("LEDs initialized");

    // ─────────────── WiFi ───────────────
    Serial.println("Initializing WiFi...");
    LED::ColourPos wifi_anim[] = {
        {0, LED::green_colour},
        {UINT16_MAX_VALUE, {}}
    };
    LED::Nodes::set_pos_step(wifi_anim[0], 0);

    static Wifi::WifiHandler wifiHandler(SSID, SSID_PASSWORD, LED::dark_blue, wifi_anim);
    Serial.println("Sharing WiFi handler pointer...");
    SharedDependencies::wifiHandler = &wifiHandler;
    Serial.println("WiFi handler pointer shared");
    Serial.println("Setting up WiFi handler...");
    wifiHandler.init();
    Serial.println("Connecting to WiFi...");
    wifiHandler.connect();
    Serial.println("WiFi initialized");


    Serial.println("Unveiling IP...");
    LED::led_set_colour(LED::red_colour, LED_DURATION, -1);
    send_ip_to_ntfy();
    LED::led_set_colour(LED::yellow_colour, LED_DURATION, -1);
    Serial.println("\nConnected!");
    wifiHandler.showIp();

    // ─────────────── Motors ───────────────
    Serial.println("Initializing motors...");
    Serial.println("Declaring left motor...");
    static Motors::Motor kibble_tray(Pins::MOTOR1_PIN, loop_progress, MOTOR_SPEED_DEFAULT, LED::dark_blue, LED::red_colour, MyUtils::ActiveComponents::Component::MotorLeft);
    Serial.println("Left motor declared");
    Serial.println("Sharing left motor pointer...");
    SharedDependencies::leftMotor = &kibble_tray;
    Serial.println("Left motor pointer shared");
    Serial.println("Initialising left motor...");
    kibble_tray.init();
    Serial.println("Running test turn on left motor...");
    kibble_tray.calibrate();
    Serial.println("Left motor initialized");

    Serial.println("Initializing right motor...");
    static Motors::Motor food_trap(Pins::MOTOR2_PIN, loop_progress, MOTOR_SPEED_DEFAULT, LED::dark_blue, LED::red_colour, MyUtils::ActiveComponents::Component::MotorRight);
    Serial.println("Rigth motor declared");
    Serial.println("Sharing left motor pointer...");
    SharedDependencies::rightMotor = &food_trap;
    Serial.println("Left motor pointer shared");
    Serial.println("Initialising right motor...");
    food_trap.init();
    Serial.println("Right motor initialized");
    Serial.println("Running test turn on right motor...");
    food_trap.calibrate();
    Serial.println("Right motor initialized");

    // ─────────────── HTTP Server ───────────────
    Serial.println("Starting HTTP server...");
    HttpServer::initialize_server();
    Serial.println("HTTP server started");
    LED::led_set_colour(LED::blue_colour, LED_DURATION, -1);

    // ─────────────── Bluetooth ───────────────
    Serial.println("Setting up bluetooth...");
    BluetoothLE::BLEHandler bleHandler(BLUETOOTH_BAUDRATE);
    Serial.println("Sharing bluetooth handler pointer...");
    SharedDependencies::bleHandler = &bleHandler;
    Serial.println("Bluetooth handler pointer shared");
    Serial.println("Initializing bluetooth...");
    bleHandler.init();
    Serial.println("Enabling bluetooth...");
    bleHandler.enable();
    Serial.println("Serial BT started");

    // Final render to clear all setup artifacts
    Serial.println("Clearing setup artifacts...");
    MyUtils::ActiveComponents::Panel::render();
    Serial.println("Setup complete - entering main loop");
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
        Serial.println("Iteration counter overflow imminent, resetting to 0");
        iteration = 0;
    } else {
        iteration++;
    }
}

void loop()
{
    if (iteration % 1000 == 0) {
        // Serial.println("In main loop, iteration: " + String(iteration));
        MyUtils::ActiveComponents::Panel::tick();
        MyUtils::ActiveComponents::Panel::render();
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
    // bool ble_status = SharedDependencies::bleHandler->isConnected();
    // Serial.println("Bluetooth connected: " + String(ble_status ? "Yes" : "No"));
    increment_iteration();
}
