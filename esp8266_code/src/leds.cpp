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
* FILE: leds.cpp
* CREATION DATE: 07-02-2026
* LAST Modified: 1:50:38 07-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: These are the functions for the LED module.
* // AR
* +==== END CatFeeder =================+
*/
#include <Arduino.h>
#include <Adafruit_NeoPixel.h>
#include "pins.hpp"
#include "leds.hpp"
#include "config.hpp"
#include "my_utils.hpp"

Adafruit_NeoPixel LED::LedStrip(LED_NUMBER, Pins::LED_STRIP_PIN, LED_TYPE + LED_COLOUR_ORDER);
bool LED::LedStripInitialized = false;

// External variables for forced color management
bool LED::forcedColor = false;

// External variables for time in the force colour management
uint32_t LED::forcedColorEndTime = 0; // Time (millis) when forced color should expire

bool LED::ledsEnabled = true;

LED::Colour LED::forcedColourValue;

const LED::Colour LED::white_colour = LED::led_get_colour_from_pointer(&LED::Colours::White);
const LED::Colour LED::black_colour = LED::led_get_colour_from_pointer(&LED::Colours::Black);
const LED::Colour LED::default_foreground = LED::led_get_colour_from_pointer(&LED::Colours::White);
const LED::Colour LED::default_background = LED::led_get_colour_from_pointer(&LED::Colours::Black);
const LED::Colour LED::red_colour = LED::led_get_colour_from_pointer(&LED::Colours::Red);
const LED::Colour LED::yellow_colour = LED::led_get_colour_from_pointer(&LED::Colours::Yellow);
const LED::Colour LED::green_colour = LED::led_get_colour_from_pointer(&LED::Colours::Green);
const LED::Colour LED::blue_colour = LED::led_get_colour_from_pointer(&LED::Colours::Blue);
const LED::Colour LED::dark_blue = LED::led_get_colour_from_pointer(&LED::Colours::DarkBlue);

void LED::led_init()
{
    if (LedStripInitialized) {
        return;
    }
    LedStrip.begin();             // initialize GPIO / strip
    LedStrip.setBrightness(LED_BRIGHTNESS);
    LedStrip.show();              // clear LEDs
    LedStripInitialized = true;
}

void LED::led_off()
{
    ledsEnabled = false;
    LedStrip.clear();
    LedStrip.show();
}

void LED::led_on()
{
    ledsEnabled = true;
    forcedColor = false;
    LedStrip.begin();
    LedStrip.setBrightness(LED_BRIGHTNESS);
    LedStrip.show();
}

void LED::led_clear()
{
    forcedColor = false;
    LedStrip.clear();
    LedStrip.show();
}

void LED::led_step(int16_t count)
{
    _led_update_forced_color_duration();
    count = _clamp_count(count);

    // If still forced, maintain the forced color
    if (forcedColor) {
        _led_fill_colour(forcedColourValue, count);
        return;
    }

    if (!ledsEnabled) {
        return;
    }

    // Pick a new random color
    Colour currentColour = led_read_colour_from_list(-1);

    _led_fill_colour(currentColour, count);
    return;
}

void LED::led_set_colour(const LED::Colour &colour, const uint32_t duration, const int16_t count, const LED::Colour &background)
{
    int16_t count_clamped = _clamp_count(count);
    forcedColor = true;
    forcedColourValue = colour;

    _led_fill_colour(colour, count_clamped, background);

    _led_process_timer(duration);
}

void LED::led_set_led_position(const uint16_t led_index, const Colour &colour, const uint32_t duration, const bool refresh)
{

    // Clamp indices to valid range
    uint16_t led_index_cleaned = _clamp_index_inclusif(led_index);

    const uint32_t fgPacked = LedStrip.Color(
        colour.r,
        colour.g,
        colour.b,
        colour.w
    );
    // Fill background first
    LedStrip.setPixelColor(led_index_cleaned, fgPacked);
    if (refresh) {
        LedStrip.show();
    }
    _led_process_timer(duration);
}

void LED::led_set_colour_from_offset(const uint16_t start_index, const uint16_t end_index, const Colour &foreground, const Colour &background, const uint32_t duration)
{
    forcedColor = true;
    forcedColourValue = foreground;

    // Ensure start_index <= end_index
    uint16_t start_index_cleaned = start_index;
    uint16_t end_index_cleaned = end_index;
    if (start_index_cleaned > end_index_cleaned) {
        MyUtils::swap(start_index_cleaned, end_index_cleaned);
    }

    // Clamp indices to valid range
    start_index_cleaned = _clamp_index_inclusif(start_index_cleaned);
    end_index_cleaned = _clamp_index_inclusif(end_index_cleaned);

    const uint32_t fgPacked = LedStrip.Color(
        foreground.r,
        foreground.g,
        foreground.b,
        foreground.w
    );

    const uint32_t bgPacked = LedStrip.Color(
        background.r,
        background.g,
        background.b,
        background.w
    );


    // Fill background first
    for (uint16_t i = 0; i < LED_NUMBER; i++) {
        if (i >= start_index_cleaned && i <= end_index_cleaned) {
            LedStrip.setPixelColor(i, fgPacked);
        } else {
            LedStrip.setPixelColor(i, bgPacked);
        }
    }
    LedStrip.show();
    _led_process_timer(duration);
}

void LED::led_fancy(LED::ColourPos *items, const size_t length, const LED::Colour &background, const uint32_t duration)
{
    forcedColor = true;

    const uint32_t bgPacked = LedStrip.Color(
        background.r,
        background.g,
        background.b,
        background.w
    );

    // 1. Fill background
    for (uint16_t i = 0; i < LED_NUMBER; i++) {
        LedStrip.setPixelColor(i, bgPacked);
    }

    // 2. Apply overlays
    for (size_t i = 0; i < length; i++) {

        // skip inactive items
        if (!items[i].node_enabled) {
            continue;
        }

        // Check that the position is not out of bounds
        const uint16_t pos = items[i].pos;
        if (pos < LED_NUMBER) {
            // Set pixel color
            const Colour &c = items[i].colour;
            LedStrip.setPixelColor(
                pos,
                LedStrip.Color(c.r, c.g, c.b, c.w)
            );
        }

        // Advance position
        _move_pixel(items[i], pos);
    }

    LedStrip.show();

    _led_process_timer(duration);
}

