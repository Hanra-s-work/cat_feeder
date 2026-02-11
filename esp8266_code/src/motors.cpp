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
* FILE: motors.cpp
* CREATION DATE: 07-02-2026
* LAST Modified: 23:12:14 11-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: These are the functions for the motor library.
* // AR
* +==== END CatFeeder =================+
*/
#include "motors.hpp"

Motors::Motor::Motor(const uint8_t motor_pin, LED::ColourPos *led_items, const int8_t speed, const LED::Colour &led_background, const LED::Colour &led_stop_colour, const MyUtils::ActiveComponents::Component component)
    : _pin(motor_pin), _leds(led_items), _speed(speed), _background(led_background), _led_stop_colour(led_stop_colour), _leds_length(LED::led_colourpos_length(led_items)), _component(component)
{
    // Do not call set_speed() here — it may attach the servo during
    // static construction. Servo attachment is deferred until first use
    // (see set_speed()).
}

void Motors::Motor::init()
{
    Serial << "Initializing motor on pin " << _pin << endl;
    LED::led_fancy(_leds, _leds_length, _background, 100);
    uint32_t free_heap = ESP.getFreeHeap();
    uint8_t fragmented_heap = ESP.getHeapFragmentation();
    Serial << "Heap before: " << free_heap << " frag:" << fragmented_heap << endl;
    // Do not attach servo here: attach on-demand in set_speed() to avoid
    // keeping multiple servo timers active simultaneously which can
    // interfere with timing-critical LED updates on ESP8266.
    Serial << "(servo attach deferred until first movement)" << endl;
    // Quick attach/detach validation to ensure the servo can be controlled
    // without leaving the timer running. This briefly exercises the driver
    // while keeping it detached for normal operation.
    Serial << "Validating servo attach/detach on pin " << _pin << endl;
    _servo.attach(_pin);
    delay(5);
    stop();
    _servo.detach();
    Serial << "Servo attach/detach validation complete" << endl;
    // Ensure motor is stopped (will attach/detach when used)
    MyUtils::ActiveComponents::Panel::enable(_component);
}


void Motors::Motor::set_speed(int8_t speed)
{
    speed = constrain(speed, _min_speed, _max_speed);

    // Map -100..100 → 0..180 (centered at 90)
    int pulse = SERVO_STOP + map(speed, -100, 100, -90, 90);
    // Attach servo on-demand if not already attached. This reduces the
    // number of active servo timers and avoids conflicts when multiple
    // Motor instances exist.
    if (!_servo.attached()) {
        _servo.attach(_pin);
        // small settle delay to ensure pulses start
        delay(5);
    }

    _servo.write(pulse);
}

void Motors::Motor::stop()
{
    _servo.write(SERVO_STOP);
    // Detach after stopping to free timer resources and avoid ISR
    // interference with the LED strip updates. Re-attach when next movement occurs.
    if (_servo.attached()) {
        delay(5); // brief settle
        _servo.detach();
    }
}

void Motors::Motor::turn_left(unsigned long duration_ms)
{
    MyUtils::ActiveComponents::Panel::activity(_component, true);
    set_speed(-100);
    delay(duration_ms);
    stop();
    MyUtils::ActiveComponents::Panel::activity(_component, false);
}

void Motors::Motor::turn_right(unsigned long duration_ms)
{
    MyUtils::ActiveComponents::Panel::activity(_component, true);
    set_speed(100);
    delay(duration_ms);
    stop();
    MyUtils::ActiveComponents::Panel::activity(_component, false);
}

void Motors::Motor::turn_left_degrees(float degrees)
{
    MyUtils::ActiveComponents::Panel::activity(_component, true);
    set_speed(-100);
    delay(degrees_to_delay(-100, degrees));
    stop();
    MyUtils::ActiveComponents::Panel::activity(_component, false);
}

void Motors::Motor::turn_right_degrees(float degrees)
{
    MyUtils::ActiveComponents::Panel::activity(_component, true);
    set_speed(100);
    delay(degrees_to_delay(100, degrees));
    stop();
    MyUtils::ActiveComponents::Panel::activity(_component, false);
}

float Motors::Motor::degrees_to_delay(int8_t speed, float degrees) const
{
    // speed: -100 .. 100
    // degrees: desired rotation in degrees
    // returns milliseconds needed to achieve this rotation at the given speed

    // Convert speed to fraction of max speed
    float fraction = abs(speed) / 100.0f;

    if (fraction == 0.0f) {
        return 0; // no movement
    }

    // Assume max speed achieves X degrees per second (calibrate experimentally)
    constexpr float MAX_DEGREES_PER_SECOND = 360.0f; // adjust to your motor
    float seconds_needed = degrees / (MAX_DEGREES_PER_SECOND * fraction);
    return seconds_needed * 1000.0f; // convert to milliseconds
}

void Motors::Motor::calibrate()
{
    _test_mode = true;
    _calibration_step = 0;
    Serial << "Calibrating motor on pin " << _pin << endl;
    LED::led_fancy(_leds, _leds_length, _background, 100);

    Serial << " - Setting to max speed" << endl;
    set_speed(_min_speed);
    delay(MOTOR_SPEED_DEFAULT);
    _increment_calibration_step();

    Serial << " - Setting to min speed" << endl;
    set_speed(_max_speed);
    delay(MOTOR_SPEED_DEFAULT);
    _increment_calibration_step();

    Serial << " - turning left for " << MOTOR_SPEED_DEFAULT << " second" << endl;
    turn_left(MOTOR_SPEED_DEFAULT);
    _increment_calibration_step();

    Serial << " - turning right for " << MOTOR_SPEED_DEFAULT << " second" << endl;
    turn_right(MOTOR_SPEED_DEFAULT);
    _increment_calibration_step();

    Serial << " - turning left for 90°" << endl;
    turn_left_degrees(90);
    _increment_calibration_step();

    Serial << " - turning right for 90°" << endl;
    turn_right_degrees(90);
    _increment_calibration_step();

    Serial << " - Stopping motor" << endl;
    stop();
    _increment_calibration_step();
    Serial << "Motor calibration complete" << endl;
    _test_mode = false;
}


void Motors::Motor::_display_test_progress(const size_t step) const
{
    if (!_test_mode) {
        return;
    }

    // Compute the number of LEDs per step (as float to avoid rounding errors)
    float leds_per_step = static_cast<float>(LED_NUMBER) / static_cast<float>(_calibration_total_steps);

    // Compute end index for this step
    size_t end_led = static_cast<size_t>((step + 1) * leds_per_step) - 1;

    // Clamp to maximum LED index
    if (end_led >= LED_NUMBER) {
        end_led = LED_NUMBER - 1;
    }

    // Light the strip from 0 to end_led
    LED::led_set_colour_from_offset(0, end_led, LED::green_colour, _background, LED_DURATION);
}

void Motors::Motor::_increment_calibration_step()
{
    if (!_test_mode) {
        return;
    }
    if (_calibration_step < _calibration_total_steps) {
        _calibration_step++;
    }
    _display_test_progress(_calibration_step);
}
