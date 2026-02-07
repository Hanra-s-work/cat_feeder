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
* FILE: motors.hpp
* CREATION DATE: 07-02-2026
* LAST Modified: 1:45:14 07-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the module for controlling servo motors.
* // AR
* +==== END CatFeeder =================+
*/
#pragma once
#include <Arduino.h>
#include <Servo.h>
#include "leds.hpp"
#include "colours.hpp"
#include "sentinels.hpp"
#include "active_components.hpp"

namespace Motors
{
    class Motor
    {
        public:
        explicit Motor(const uint8_t motor_pin, LED::ColourPos *led_items, const int8_t speed = MOTOR_SPEED_DEFAULT, const LED::Colour &led_background = LED::default_background, const LED::Colour &led_stop_colour = LED::red_colour, const MyUtils::ActiveComponents::Component component = MyUtils::ActiveComponents::Component::MotorLeft);

        void init();
        void set_speed(int8_t speed = MOTOR_SPEED_DEFAULT);   // -100 .. 100
        void stop();

        void turn_left(unsigned long duration_ms = MOTOR_TURN_DURATION_DEFAULT);
        void turn_right(unsigned long duration_ms = MOTOR_TURN_DURATION_DEFAULT);

        void turn_left_degrees(float degrees = MOTOR_TURN_DEGREES_DEFAULT);
        void turn_right_degrees(float degrees = MOTOR_TURN_DEGREES_DEFAULT);

        float degrees_to_delay(int8_t speed = MOTOR_SPEED_DEFAULT, float degrees = MOTOR_TURN_DEGREES_DEFAULT) const;

        void calibrate();

        private:

        void _display_test_progress(const size_t step) const;
        void _increment_calibration_step();

        Servo _servo;
        uint8_t _pin;

        LED::ColourPos *_leds;

        int8_t _speed;

        static constexpr uint8_t SERVO_STOP = 90;

        const LED::Colour &_background;
        const LED::Colour &_led_stop_colour;
        size_t _leds_length;

        MyUtils::ActiveComponents::Component _component;

        bool _test_mode = false;
        size_t _calibration_step = 0;
        static constexpr size_t _calibration_total_steps = 7;

        static constexpr uint16_t _strip_start = 0;
        static constexpr uint16_t _strip_middle = LED_NUMBER / 2;
        static constexpr uint16_t _strip_end = LED_NUMBER - 1;

        static constexpr int8_t _min_speed = -100;
        static constexpr int8_t _max_speed = 100;
    };
}
