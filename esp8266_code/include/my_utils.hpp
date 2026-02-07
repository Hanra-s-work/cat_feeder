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
* FILE: my_utils.hpp
* CREATION DATE: 07-02-2026
* LAST Modified: 1:45:55 07-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: These are a set of utility function that essentially contain templates and code that needs to be globally available.
* // AR
* +==== END CatFeeder =================+
*/
#pragma once
#include "leds.hpp"
#include "leds_structs.hpp"
#include "active_components.hpp"

namespace MyUtils
{
    template <typename T>
    static inline void swap(T &a, T &b)
    {
        T tmp = a;
        a = b;
        b = tmp;
    }

    template <typename T>
    static inline T leds_for_progress(T current, T max, T total_leds)
    {
        if (max == 0) {
            return 0;
        } // avoid divide by zero
        float percent = static_cast<float>(current) / static_cast<float>(max);
        return static_cast<T>(percent * static_cast<float>(total_leds));
    }

    inline void display_percentage(const LED::Colour &fg, const LED::Colour &bg, const int16_t current, const int16_t max_steps)
    {
        Serial.println("Displaying progress for step " + String(current) + " of " + String(max_steps));
        int16_t progress = MyUtils::leds_for_progress<int16_t>(
            current,
            max_steps,
            static_cast<int16_t>(LED_NUMBER)
        );
        Serial.println("Displaying progress: " + String(progress) + " LEDs lit for step " + String(current) + " of " + String(max_steps));
        LED::led_set_colour(fg, LED_DURATION, progress, bg);
    };
}
