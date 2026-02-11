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
* FILE: leds.hpp
* CREATION DATE: 07-02-2026
* LAST Modified: 22:45:9 11-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the led module for driving different led strips thanks to the underlying adafruit library.
* // AR
* +==== END CatFeeder =================+
*/
#pragma once
#include <Arduino.h>
#include "config.hpp"
#include "colours.hpp"
#include "my_overloads.hpp"

namespace LED
{
    /**
     * @file leds.hpp
     * @brief Public LED strip API and small inline helper utilities.
     *
     * This header exposes the LED subsystem's public interface (initialisation,
     * enable/disable, periodic stepping, and forced-colour operations) and a
     * collection of compact inline helpers used throughout the implementation.
     *
     * The file also defines a PROGMEM-backed colour table to minimise RAM
     * usage. Helper functions are provided to read colours from program memory
     * into RAM-safe `Colour` instances.
     */

     /** External NeoPixel strip instance (defined in the companion source file). */
    extern Adafruit_NeoPixel LedStrip;

    /** True once `led_init()` has successfully initialised `LedStrip`. */
    extern bool LedStripInitialized;

    /** Global enable flag — when false, LED updates are suppressed. */
    extern bool ledsEnabled;

    /** Default foreground `Colour` used by helper APIs when no colour is supplied. */
    extern const Colour default_foreground;

    /** Default background `Colour` used by helper APIs when no background is supplied. */
    extern const Colour default_background;

    /** Common named colour constants for convenience. */
    extern const Colour white_colour; /**< White (convenience alias). */
    extern const Colour black_colour; /**< Black (convenience alias). */
    extern const Colour red_colour; /**< Red (convenience alias). */
    extern const Colour yellow_colour; /**< Yellow (convenience alias). */
    extern const Colour green_colour; /**< Green (convenience alias). */
    extern const Colour blue_colour; /**< Blue (convenience alias). */
    extern const Colour dark_blue; /**< Dark blue (convenience alias). */

    /**
     * Colour currently used for forced-colour operations. Stores the active
     * forced colour value while a forced display is in effect.
     */
    extern Colour forcedColourValue;
    /**
     * @brief PROGMEM table of pointers to predefined `Colour` values.
     *
     * The table stores pointers to `Colour` objects placed in PROGMEM to keep
     * RAM usage minimal. Use `led_read_colour_from_list()` to obtain a RAM
     * copy of a colour stored here.
     */
    static const Colour *const colorList[] PROGMEM = {
    &Colours::AliceBlue,&Colours::AntiqueWhite,&Colours::AntiqueWhite1,&Colours::AntiqueWhite2,&Colours::AntiqueWhite3,&Colours::AntiqueWhite4,&Colours::Aqua,
    &Colours::Aquamarine, &Colours::Aquamarine1, &Colours::Aquamarine2, &Colours::Azure, &Colours::Azure1, &Colours::Azure2, &Colours::Azure3, &Colours::Beige, &Colours::Bisque,
    &Colours::Bisque1, &Colours::Bisque2, &Colours::Bisque3, &Colours::Black, &Colours::BlanchedAlmond, &Colours::Blue, &Colours::Blue1, &Colours::BlueViolet, &Colours::Brown,
    &Colours::Brown1, &Colours::Brown2, &Colours::Brown3, &Colours::Brown4, &Colours::Burlywood, &Colours::Burlywood1, &Colours::Burlywood2, &Colours::Burlywood3, &Colours::Burlywood4,
    &Colours::CadetBlue, &Colours::CadetBlue1, &Colours::CadetBlue2, &Colours::CadetBlue3, &Colours::CadetBlue4, &Colours::Chartreuse, &Colours::Chartreuse1, &Colours::Chartreuse2,
    &Colours::Chartreuse3, &Colours::Chocolate, &Colours::Chocolate1, &Colours::Chocolate2, &Colours::Chocolate3, &Colours::Coral, &Colours::Coral1, &Colours::Coral2,
    &Colours::Coral3, &Colours::Coral4, &Colours::CornflowerBlue, &Colours::Cornsilk, &Colours::Cornsilk1, &Colours::Cornsilk2, &Colours::Cornsilk3, &Colours::Crimson,
    &Colours::Cyan, &Colours::Cyan1, &Colours::DarkBlue, &Colours::DarkCyan, &Colours::DarkGoldenrod, &Colours::DarkGoldenrod1, &Colours::DarkGoldenrod2,
    &Colours::DarkGoldenrod3, &Colours::DarkGoldenrod4, &Colours::DarkGreen, &Colours::DarkGrey, &Colours::DarkKhaki, &Colours::DarkMagenta, &Colours::DarkOliveGreen,
    &Colours::DarkOliveGreen1, &Colours::DarkOliveGreen2, &Colours::DarkOliveGreen3, &Colours::DarkOliveGreen4, &Colours::DarkOrange, &Colours::DarkOrange1,
    &Colours::DarkOrange2, &Colours::DarkOrange3, &Colours::DarkOrange4, &Colours::DarkOrchid, &Colours::DarkOrchid1, &Colours::DarkOrchid2, &Colours::DarkOrchid3,
    &Colours::DarkOrchid4, &Colours::DarkRed, &Colours::DarkSalmon, &Colours::DarkSeaGreen, &Colours::DarkSeaGreen1, &Colours::DarkSeaGreen2, &Colours::DarkSeaGreen3,
    &Colours::DarkSeaGreen4,&Colours::DarkSlateBlue,&Colours::DarkSlateGrey,&Colours::DarkSlateGrey1,&Colours::DarkSlateGrey2, &Colours::DarkSlateGrey3,
    &Colours::DarkSlateGrey4,&Colours::DarkTurquoise,&Colours::DarkViolet,&Colours::DeepPink,&Colours::DeepPink1,&Colours::DeepPink2, &Colours::DeepPink3,
    &Colours::DeepSkyBlue,&Colours::DeepSkyBlue1,&Colours::DeepSkyBlue2,&Colours::DeepSkyBlue3,&Colours::DodgerBlue,&Colours::DodgerBlue1,
    &Colours::DodgerBlue2, &Colours::DodgerBlue3, &Colours::Firebrick, &Colours::Firebrick1, &Colours::Firebrick2, &Colours::Firebrick3, &Colours::Firebrick4,
    &Colours::FloralWhite,&Colours::ForestGreen,&Colours::Fractal,&Colours::Fuchsia,&Colours::Gainsboro,&Colours::GhostWhite,&Colours::Gold,&Colours::Gold1,&Colours::Gold2,
    &Colours::Gold3,&Colours::Goldenrod,&Colours::Goldenrod1,&Colours::Goldenrod2,&Colours::Goldenrod3,&Colours::Goldenrod4,&Colours::Grey,&Colours::Green,&Colours::Green1,
    &Colours::Green2,&Colours::Green3,&Colours::GreenYellow,&Colours::Grey1,&Colours::Grey10,&Colours::Grey100,&Colours::Grey11,&Colours::Grey12,&Colours::Grey13,&Colours::Grey14,
    &Colours::Grey15,&Colours::Grey16,&Colours::Grey17,&Colours::Grey18,&Colours::Grey19,&Colours::Grey2,&Colours::Grey20,&Colours::Grey21,&Colours::Grey22,&Colours::Grey23,&Colours::Grey24,
    &Colours::Grey25,&Colours::Grey26,&Colours::Grey27,&Colours::Grey28,&Colours::Grey29,&Colours::Grey3,&Colours::Grey30,&Colours::Grey31,&Colours::Grey32,&Colours::Grey33,&Colours::Grey34,
    &Colours::Grey35, &Colours::Grey36, &Colours::Grey37, &Colours::Grey38, &Colours::Grey39, &Colours::Grey4, &Colours::Grey40, &Colours::Grey41, &Colours::Grey42, &Colours::Grey43, &Colours::Grey44,
    &Colours::Grey45, &Colours::Grey46, &Colours::Grey47, &Colours::Grey48, &Colours::Grey49, &Colours::Grey5, &Colours::Grey50, &Colours::Grey51, &Colours::Grey52, &Colours::Grey53, &Colours::Grey54,
    &Colours::Grey55, &Colours::Grey56, &Colours::Grey57, &Colours::Grey58, &Colours::Grey59, &Colours::Grey6, &Colours::Grey60, &Colours::Grey61, &Colours::Grey62, &Colours::Grey63, &Colours::Grey64,
    &Colours::Grey65, &Colours::Grey66, &Colours::Grey67, &Colours::Grey68, &Colours::Grey69, &Colours::Grey7, &Colours::Grey70, &Colours::Grey71, &Colours::Grey72, &Colours::Grey73, &Colours::Grey74,
    &Colours::Grey75, &Colours::Grey76, &Colours::Grey77, &Colours::Grey78, &Colours::Grey79, &Colours::Grey8, &Colours::Grey80, &Colours::Grey81, &Colours::Grey82, &Colours::Grey83, &Colours::Grey84,
    &Colours::Grey85, &Colours::Grey86, &Colours::Grey87, &Colours::Grey88, &Colours::Grey89, &Colours::Grey9, &Colours::Grey90, &Colours::Grey91, &Colours::Grey92, &Colours::Grey93, &Colours::Grey94,
    &Colours::Grey95, &Colours::Grey96, &Colours::Grey97, &Colours::Grey98, &Colours::Grey99, &Colours::Honeydew, &Colours::Honeydew1, &Colours::Honeydew2, &Colours::Honeydew3, &Colours::HotPink,
    &Colours::HotPink1, &Colours::HotPink2, &Colours::HotPink3, &Colours::HotPink4, &Colours::IndianRed, &Colours::IndianRed1, &Colours::IndianRed2, &Colours::IndianRed3, &Colours::IndianRed4, &Colours::Indigo, &Colours::Ivory, &Colours::Ivory1,
    &Colours::Ivory2, &Colours::Ivory3, &Colours::Khaki, &Colours::Khaki1, &Colours::Khaki2, &Colours::Khaki3, &Colours::Khaki4, &Colours::Lavender, &Colours::LavenderBlush, &Colours::LavenderBlush1, &Colours::LavenderBlush2,
    &Colours::LavenderBlush3, &Colours::LawnGreen, &Colours::LemonChiffon, &Colours::LemonChiffon1, &Colours::LemonChiffon2, &Colours::LemonChiffon3, &Colours::LightBlue, &Colours::LightBlue1,
    &Colours::LightBlue2, &Colours::LightBlue3, &Colours::LightBlue4, &Colours::LightCoral, &Colours::LightCyan, &Colours::LightCyan1, &Colours::LightCyan2,
    &Colours::LightCyan3, &Colours::LightGoldenrod, &Colours::LightGoldenrod1, &Colours::LightGoldenrod2, &Colours::LightGoldenrod3, &Colours::LightGoldenrod4, &Colours::LightGoldenrodYellow, &Colours::LightGreen, &Colours::LightGrey, &Colours::LightPink, &Colours::LightPink1, &Colours::LightPink2,
    &Colours::LightPink3,&Colours::LightPink4,&Colours::LightSalmon,&Colours::LightSalmon1,&Colours::LightSalmon2,&Colours::LightSalmon3,&Colours::LightSeaGreen,&Colours::LightSkyBlue,&Colours::LightSkyBlue1,
    &Colours::LightSkyBlue2,&Colours::LightSkyBlue3,&Colours::LightSkyBlue4,&Colours::LightSlateBlue,&Colours::LightSlateGrey,&Colours::LightSteelBlue,&Colours::LightSteelBlue1,&Colours::LightSteelBlue2,&Colours::LightSteelBlue3,&Colours::LightSteelBlue4,&Colours::LightYellow,
    &Colours::LightYellow1,&Colours::LightYellow2,&Colours::LightYellow3,&Colours::Lime,&Colours::LimeGreen,&Colours::Linen,&Colours::Magenta,&Colours::Magenta2,&Colours::Magenta3,&Colours::Maroon,
    &Colours::Maroon1,&Colours::Maroon2,&Colours::Maroon3,&Colours::Maroon4,&Colours::Maroon5,&Colours::MediumAquamarine,&Colours::MediumBlue,&Colours::MediumForestGreen,&Colours::MediumGoldenRod,
    &Colours::MediumOrchid,&Colours::MediumOrchid1,&Colours::MediumOrchid2,&Colours::MediumOrchid3,&Colours::MediumOrchid4,&Colours::MediumPurple,&Colours::MediumPurple1,&Colours::MediumPurple2,&Colours::MediumPurple3,&Colours::MediumPurple4,
    &Colours::MediumSeaGreen,&Colours::MediumSlateBlue,&Colours::MediumSpringGreen,&Colours::MediumTurquoise,&Colours::MediumVioletRed,&Colours::MidnightBlue,&Colours::MintCream,&Colours::MistyRose,&Colours::MistyRose1,
    &Colours::MistyRose2,&Colours::MistyRose3,&Colours::Moccasin,&Colours::NavajoWhite,&Colours::NavajoWhite1,&Colours::NavajoWhite2,&Colours::NavajoWhite3,&Colours::NavyBlue,
    &Colours::OldLace,&Colours::Olive,&Colours::OliveDrab,&Colours::OliveDrab1,&Colours::OliveDrab2,&Colours::OliveDrab3,&Colours::Orange,
    &Colours::Orange1,&Colours::Orange2,&Colours::Orange3,&Colours::OrangeRed,&Colours::OrangeRed1,&Colours::OrangeRed2,&Colours::OrangeRed3,&Colours::Orchid,&Colours::Orchid1,&Colours::Orchid2,&Colours::Orchid3,&Colours::Orchid4,
    &Colours::PaleGoldenrod,&Colours::PaleGreen,&Colours::PaleGreen1,&Colours::PaleGreen2,&Colours::PaleGreen3,&Colours::PaleTurquoise,&Colours::PaleTurquoise1,&Colours::PaleTurquoise2,&Colours::PaleTurquoise3,&Colours::PaleTurquoise4,&Colours::PaleVioletRed,&Colours::PaleVioletRed1,
    &Colours::PaleVioletRed2,&Colours::PaleVioletRed3,&Colours::PaleVioletRed4,&Colours::PapayaWhip,&Colours::PeachPuff,&Colours::PeachPuff1,&Colours::PeachPuff2,&Colours::PeachPuff3,&Colours::Peru,&Colours::Pink,&Colours::Pink1,&Colours::Pink2,&Colours::Pink3,&Colours::Pink4,&Colours::Plum,&Colours::Plum1,&Colours::Plum2,
    &Colours::Plum3,&Colours::Plum4,&Colours::PowderBlue,&Colours::Purple,&Colours::Purple1,&Colours::Purple2,&Colours::Purple3,&Colours::Purple4,&Colours::Purple5,&Colours::Red,
    &Colours::Red2,&Colours::Red3,&Colours::RosyBrown,&Colours::RosyBrown1,&Colours::RosyBrown2,&Colours::RosyBrown3,&Colours::RosyBrown4,&Colours::RoyalBlue,&Colours::RoyalBlue1,&Colours::RoyalBlue2,&Colours::RoyalBlue3,&Colours::RoyalBlue4,&Colours::SaddleBrown,
    &Colours::Salmon,&Colours::Salmon1,&Colours::Salmon2,&Colours::Salmon3,&Colours::Salmon4,&Colours::SandyBrown,&Colours::SeaGreen,&Colours::SeaGreen1,&Colours::SeaGreen2,&Colours::SeaGreen3,&Colours::Seashell,
    &Colours::Seashell1,&Colours::Seashell2,&Colours::Seashell3,&Colours::Sienna,&Colours::Sienna1,&Colours::Sienna2,&Colours::Sienna3,&Colours::Sienna4,&Colours::Silver,&Colours::SkyBlue,&Colours::SkyBlue1,&Colours::SkyBlue2,&Colours::SkyBlue3,&Colours::SkyBlue4,&Colours::SlateBlue,
    &Colours::SlateBlue1, &Colours::SlateBlue2, &Colours::SlateBlue3, &Colours::SlateBlue4, &Colours::SlateGray, &Colours::SlateGray1, &Colours::SlateGray2, &Colours::SlateGray3, &Colours::SlateGray4, &Colours::Snow,
    &Colours::Snow1,&Colours::Snow3,&Colours::Snow4,&Colours::SpringGreen,&Colours::SpringGreen1,&Colours::SpringGreen2,&Colours::SpringGreen3,&Colours::SteelBlue,&Colours::SteelBlue1,&Colours::SteelBlue2,&Colours::SteelBlue3,&Colours::SteelBlue4,&Colours::Tan,
    &Colours::Tan1,&Colours::Tan2,&Colours::Tan3,&Colours::Teal,&Colours::Thistle,&Colours::Thistle1,&Colours::Thistle2,&Colours::Thistle3,&Colours::Thistle4,&Colours::Tomato,&Colours::Tomato1,
    &Colours::Tomato2, &Colours::Tomato3, &Colours::Transparent, &Colours::Turquoise, &Colours::Turquoise1, &Colours::Turquoise2, &Colours::Turquoise3, &Colours::Turquoise4,
    &Colours::Violet, &Colours::VioletRed, &Colours::VioletRed1, &Colours::VioletRed2, &Colours::VioletRed3, &Colours::VioletRed4, &Colours::Wheat, &Colours::Wheat1, &Colours::Wheat2,
    &Colours::Wheat3, &Colours::Wheat4, &Colours::White, &Colours::WhiteSmoke, &Colours::Yellow, &Colours::Yellow1, &Colours::Yellow2, &Colours::Yellow3, &Colours::YellowGreen,
    };

    constexpr size_t colorListSize = sizeof(colorList) / sizeof(colorList[0]);

    // External variables for forced-colour management
    /** Flag indicating a forced colour is currently active. */
    extern bool forcedColor;

    /**
     * Timestamp (millis) at which the forced-colour period ends. A value of 0
     * means no expiry (i.e. infinite duration).
     */
    extern uint32_t forcedColorEndTime;

    /**
     * @brief Small helpers for manipulating `ColourPos` nodes.
     *
     * These inline helpers provide concise operations for setting node
     * properties (position, colour, stepping and animation/timing values) and
     * are intended for use when constructing or updating `ColourPos` arrays.
     */
    namespace Nodes
    {
        static inline void set_position(ColourPos &item, const int16_t pos)
        {
            item.pos = pos;
        }

        static inline void set_colour(ColourPos &item, const Colour &colour)
        {
            item.colour = colour;
        }

        static inline void set_pos_step(ColourPos &item, const int16_t step)
        {
            item.pos_step = step;
        }

        static inline void show_node(ColourPos &item)
        {
            item.node_enabled = true;
        }

        static inline void hide_node(ColourPos &item)
        {
            item.node_enabled = false;
        }

        static inline void set_disable_on_complete(ColourPos &item, const bool disable)
        {
            item.disable_on_complete = disable;
        }

        static inline void set_tick_interval(ColourPos &item, const uint16_t interval)
        {
            item.tick_animation.interval_ms = interval;
        }

        static inline uint32_t get_last_update(ColourPos &item)
        {
            return item.tick_animation.last_update_ms;
        }

        static inline uint32_t get_current_frame(ColourPos &item)
        {
            return item.tick_animation.current_frame;
        }
    }
    // Tiny helpers

    /**
     * @brief Clear the forced-colour flag when its timeout expires.
     *
     * If `forcedColor` is active and `forcedColorEndTime` is non-zero and has
     * been reached, this helper resets `forcedColor` to false and clears the
     * timer. Intended to be called regularly from the LED update path.
     */
    static inline void _led_update_forced_color_duration()
    {
        if (forcedColor && forcedColorEndTime > 0 && millis() >= forcedColorEndTime) {
            forcedColor = false;          // allow automatic colors again
            forcedColorEndTime = 0;       // reset timer
        }
    }

    /**
     * @brief Ensure a requested LED count is within [0, LED_NUMBER].
     *
     * Out-of-range values are normalised to `LED_NUMBER`.
     *
     * @param count Requested number of LEDs (defaults to `LED_NUMBER`).
     * @return int16_t Clamped, valid count.
     */
    static inline int16_t _clamp_count(const int16_t count = LED_NUMBER)
    {
        if (count < 0 || count > LED_NUMBER) {
            return LED_NUMBER;
        }
        return count;
    }

    /**
     * @brief Clamp an index to the inclusive range [0, LED_NUMBER-1].
     *
     * Unlike `_clamp_count` this helper treats `LED_NUMBER-1` as the maximum
     * valid index. If `count` is out-of-range the function returns the last
     * valid index (`LED_NUMBER-1`).
     *
     * @param count Index to clamp (defaults to `LED_NUMBER`).
     * @return int16_t Clamped index within [0, LED_NUMBER-1].
     */
    static inline int16_t _clamp_index_inclusif(const int16_t count = LED_NUMBER)
    {
        if (count < 0 || count >= LED_NUMBER) {
            return LED_NUMBER - 1;
        }
        return count;
    }

    /**
     * @brief Clear (set) pixels after `count` to a background colour and return the effective count.
     *
     * The function clamps `count` to a valid range and writes `colour` to
     * pixels in the range [count .. LED_NUMBER-1]. Returns the clamped value.
     *
     * @param count Number of LEDs to keep active (defaults to `LED_NUMBER`).
     * @param colour Background `Colour` to write to remaining pixels.
     * @return int16_t Effective (clamped) count.
     */
    static inline int16_t _clear_remaining_count(int16_t count = LED_NUMBER, const Colour &colour = default_background)
    {
        if (count < 0 || count > LED_NUMBER) {
            count = LED_NUMBER;
        }
        const uint32_t col = LedStrip.Color(colour.r, colour.g, colour.b, colour.w);
        for (uint16_t i = count; i < LED_NUMBER; i++) {
            LedStrip.setPixelColor(i, col); // turn off remaining LEDs
        }
        return count;
    }

    /**
     * @brief Write `colour` to the first `count` pixels and fill the remainder with `background`.
     *
     * `count` is clamped to a valid range. Pixels [0..count-1] are set to
     * `colour` (using the strip's `Color()` helper). Remaining pixels are
     * written with `background` and the strip is updated with `LedStrip.show()`.
     *
     * @param colour Foreground `Colour` to display (defaults to `default_foreground`).
     * @param count Number of pixels to set (default: all pixels).
     * @param background Background `Colour` to write to remaining pixels.
     */
    static inline void _led_fill_colour(const Colour &colour = default_foreground, int16_t count = -1, const Colour &background = default_background)
    {
        count = _clamp_count(count);
        const uint32_t FgCol = LedStrip.Color(colour.r, colour.g, colour.b, colour.w);
        for (uint16_t i = 0; i < count; i++) {
            LedStrip.setPixelColor(i, FgCol);
        }
        _clear_remaining_count(count, background);
        LedStrip.show();
    }

    static inline void _led_process_timer(const uint32_t duration)
    {
        if (duration > 0) {
            forcedColorEndTime = millis() + duration;
        } else {
            forcedColorEndTime = 0; // infinite
        }
    }

    /**
     * @brief Move a node's position according to its step and timing settings.
     *
     * This helper advances `item.pos` by `item.pos_step` when the node's
     * internal tick timer indicates it is time to update. Positions are
     * clamped within `[0 .. LED_NUMBER-1]`. Node wrapping/disabling is triggered
     * only when the computed new position would exceed bounds, avoiding off-by-one
     * issues where nodes wrap prematurely when simply reaching the edge.
     *
     * Fixed in recent updates:
     * - Uses int32_t arithmetic to prevent unsigned underflow
     * - Wrap condition based on computed position, not current position
     * - Proper bounds checking for both directions
     *
     * @param item `ColourPos` node to move.
     * @param pos Current reference position (unused but kept for compatibility).
     */
    static inline void _move_pixel(ColourPos &item, const uint16_t pos)
    {
        item.tick_animation.tick();
        if (!item.tick_animation.ticked()) {
            return; // not time yet
        }

        // CRITICAL: Use int32_t to safely handle uint16_t + int16_t arithmetic
        // This prevents unsigned underflow when pos_step is negative
        int32_t new_pos = (int32_t)item.pos + (int32_t)item.pos_step;

        // Clamp position within bounds
        int16_t new_pos_clamped = _clamp_index_inclusif((int16_t)new_pos);

        item.pos = (uint16_t)new_pos_clamped;

        // Optional: auto-disable after hitting the end.
        // Only trigger wrap/disable when the computed `new_pos` goes beyond bounds.
        // This prevents wrapping when the node simply reaches the last index
        // but hasn't attempted to move past it (avoids off-by-one).
        if ((item.pos_step >= 0 && new_pos > (int32_t)LED_NUMBER - 1) ||
            (item.pos_step < 0 && new_pos < 0)) {
            if (item.disable_on_complete) {
                item.node_enabled = false;
            } else {
                if (item.pos_step >= 0) {
                    item.pos = 0; // wrap to start
                } else {
                    item.pos = LED_NUMBER - 1; // wrap to end
                }
            }
        }
    }

    /**
     * @brief Read a `Colour` structure from PROGMEM into RAM.
     *
     * Performs a `memcpy_P` from the program-memory pointer `ptr` into a
     * temporary `Colour` object that is returned by value.
     *
     * @param ptr Pointer to a `Colour` in PROGMEM.
     * @return Colour Copy of the PROGMEM value in RAM.
     */
    static inline Colour led_get_colour_from_pointer(const Colour *ptr)
    {
        Colour color;
        memcpy_P(&color, ptr, sizeof(Colour));
        return color;
    }

    /**
     * @brief Obtain a `Colour` from the PROGMEM `colorList` by index.
     *
     * If `index` is negative a random entry from `colorList` is selected.
     * The function bounds-checks the index and returns a RAM copy of the
     * selected `Colour`.
     *
     * @param index Index into `colorList`, or negative to pick randomly.
     * @return Colour Colour copied into RAM.
     */
    static inline Colour led_read_colour_from_list(int16_t index = -1)
    {
        // Random selection
        if (index < 0) {
            index = random(colorListSize);
        }

        // Bounds check
        if ((size_t)index >= colorListSize) {
            index = 0;
        }

        // Read pointer from PROGMEM
        const Colour *ptr =
            (const Colour *)pgm_read_ptr(&colorList[index]);

        // Copy color from PROGMEM into RAM
        return led_get_colour_from_pointer(ptr);
    }

    /**
     * @brief Compute the number of entries in a `ColourPos` sequence.
     *
     * The sequence must be terminated by an entry whose `pos` equals
     * `COLOURPOS_END`. The function returns the number of valid entries before
     * the terminator.
     *
     * @param items Pointer to the `ColourPos` array.
     * @return size_t Number of entries (does not include terminator).
     */
    static inline size_t led_colourpos_length(const ColourPos *items)
    {
        size_t len = 0;
        while (items[len].pos != COLOURPOS_END) {
            ++len;
        }
        return len;
    }


    /**
     * @name Public API
     * @brief Functions forming the external LED control interface.
     *
     * These functions provide initialisation, on/off control, periodic
     * stepping (to be called from the main loop) and forced-colour helpers.
     *@{
     */

     /** Initialize the LED subsystem (idempotent). */
    void led_init();

    /** Disable LEDs and clear the strip. */
    void led_off();

    /** Enable LEDs and resume automatic updates. */
    void led_on();

    /** Clear the strip and cancel any forced colour. */
    void led_clear();

    /**
     * @brief Return whether LED updates are currently enabled.
     *
     * @return true if LEDs are enabled; false otherwise.
     */
    static inline bool led_is_enabled()
    {
        return ledsEnabled;
    }

    /**
     * @brief Immediately refresh the LED strip (calls `LedStrip.show()`).
     *
     * Useful when caller has updated pixel values directly and requires an
     * immediate push to the hardware.
     */
    static inline void led_refresh()
    {
        LedStrip.show();
    }

    /**
     * @brief Periodic LED subsystem update; call from the application's main loop.
     *
     * @param count Optional number of LEDs to update (defaults to all).
     */
    void led_step(int16_t count = -1);

    /**
     * @brief Force the strip to show a single `Colour` for a period.
     *
     * The forced colour overrides any automatic animations until the duration
     * expires (or until `led_clear()` / `led_on()` is called). A `duration` of
     * 0 indicates an infinite forced period.
     *
     * @param colour Colour to display.
     * @param brightness Brightness level (0-255).
     * @param duration Duration in milliseconds to keep the forced colour (0 = infinite).
     * @param count Number of LEDs to set (defaults to all).
     */
     /**
      * @brief Force the strip to show a single `Colour` for a period.
      *
      * The forced colour overrides any automatic animations until the duration
      * expires (or until `led_clear()` / `led_on()` is called). A `duration` of
      * 0 indicates an infinite forced period.
      *
      * @param colour Colour to display (defaults to `default_foreground`).
      * @param duration Duration in milliseconds to keep the forced colour (0 = infinite).
      * @param count Number of LEDs to set (defaults to all).
      * @param background Optional background `Colour` for remaining pixels.
      */
    void led_set_colour(const Colour &colour = default_foreground, const uint32_t duration = LED_DURATION, const int16_t count = -1, const LED::Colour &background = default_background);

    /**
     * @brief Convenience: force a colour chosen from the PROGMEM `colorList`.
     *
     * Reads the requested colour from `colorList` and forwards it to
     * `led_set_colour()` with the provided brightness/duration/count.
     *
     * @param index Index into `colorList` (negative chooses randomly).
     * @param brightness Brightness level passed to `led_set_colour`.
     * @param duration Duration passed to `led_set_colour`.
     * @param count Number of LEDs to set (defaults to all).
     */
     /**
      * @brief Convenience: select a colour from `colorList` and force it.
      *
      * @param index Index into `colorList` (negative chooses randomly).
      * @param duration Duration in milliseconds to keep the forced colour (0 = infinite).
      * @param count Number of LEDs to set (defaults to all).
      */
    static inline void led_set_color_from_list(const int16_t index = 0, const uint32_t duration = LED_DURATION, const int16_t count = -1)
    {
        Colour colour = led_read_colour_from_list(index);
        LED::led_set_colour(colour, duration, count);
    }

    /**
     * @brief Set a single LED pixel to a colour for a duration.
     *
     * @param led_index Index of LED to set.
     * @param colour Colour to write to the LED (defaults to `default_foreground`).
     * @param duration Duration in milliseconds to keep the colour (0 = infinite).
     * @param refresh If true the strip is refreshed immediately (`LedStrip.show()`).
     */
    void led_set_led_position(const uint16_t led_index, const Colour &colour = default_foreground, const uint32_t duration = LED_DURATION, const bool refresh = true);

    /**
     * @brief Convenience wrapper for `led_set_led_position` that selects the colour from `colorList`.
     *
     * @param led_index Index of LED to set.
     * @param colour_index Index into `colorList` (negative = random).
     * @param duration Duration in milliseconds to keep the colour (0 = infinite).
     * @param refresh If true the strip is refreshed immediately.
     */
    static inline void led_set_led_position_from_list(const uint16_t led_index, const int16_t colour_index = 0, const uint32_t duration = LED_DURATION, const bool refresh = true)
    {
        const Colour foreground = led_read_colour_from_list(colour_index);
        led_set_led_position(led_index, foreground, duration, refresh);
    }

    /**
     * @brief Apply a foreground/background colour to a range of LEDs.
     *
     * Sets LEDs in the inclusive range [`start_index`, `end_index`] to
     * `foreground` and writes `background` to the remaining pixels. The
     * operation honours the given `brightness` and is active for `duration`
     * milliseconds (0 = infinite).
     *
     * @param start_index Starting LED index (inclusive).
     * @param end_index Ending LED index (inclusive).
     * @param foreground Foreground `Colour` for the slice.
     * @param background Background `Colour` for the rest of the strip.
     * @param brightness Brightness level (0-255).
     * @param duration Duration in milliseconds to display (0 = infinite).
     */
     /**
      * @brief Apply a foreground/background colour to a range of LEDs.
      *
      * Sets LEDs in the inclusive range [`start_index`, `end_index`] to
      * `foreground` and writes `background` to the remaining pixels. The
      * operation is active for `duration` milliseconds (0 = infinite).
      *
      * @param start_index Starting LED index (inclusive).
      * @param end_index Ending LED index (inclusive).
      * @param foreground Foreground `Colour` for the slice.
      * @param background Background `Colour` for the rest of the strip.
      * @param duration Duration in milliseconds to display (0 = infinite).
      */
    void led_set_colour_from_offset(const uint16_t start_index = 0, const uint16_t end_index = LED_NUMBER - 1, const Colour &foreground = default_foreground, const Colour &background = default_background, const uint32_t duration = LED_DURATION);

    /**
     * @brief Variant of `led_set_colour_from_offset` that selects colours from `colorList`.
     *
     * `index_foreground` and `index_background` are indices into the
     * PROGMEM `colorList`. Negative indices select a random colour. Other
     * parameters behave as in `led_set_colour_from_offset`.
     *
     * @param start_index Starting LED index (inclusive).
     * @param end_index Ending LED index (inclusive).
     * @param index_foreground Index into `colorList` for the foreground colour (negative = random).
     * @param index_background Index into `colorList` for the background colour (negative = random).
     * @param brightness Brightness level (0-255).
     * @param duration Duration in milliseconds to display (0 = infinite).
     */
     /**
      * @brief Variant of `led_set_colour_from_offset` that selects colours from `colorList`.
      *
      * `index_foreground` and `index_background` are indices into the
      * PROGMEM `colorList`. Negative indices select a random colour. Other
      * parameters behave as in `led_set_colour_from_offset`.
      *
      * @param start_index Starting LED index (inclusive).
      * @param end_index Ending LED index (inclusive).
      * @param index_foreground Index into `colorList` for the foreground colour (negative = random).
      * @param index_background Index into `colorList` for the background colour (negative = random).
      * @param duration Duration in milliseconds to display (0 = infinite).
      */
    static inline void led_set_colour_from_offset_from_list(const uint16_t start_index = 0, const uint16_t end_index = LED_NUMBER - 1, const int16_t index_foreground = -1, const int16_t index_background = -1, const uint32_t duration = LED_DURATION)
    {
        const Colour foreground = led_read_colour_from_list(index_foreground);
        const Colour background = led_read_colour_from_list(index_background);
        led_set_colour_from_offset(start_index, end_index, foreground, background, duration);
    }

    /**
     * @brief Render a multi-colour "fancy" pattern onto the strip.
     *
     * The pattern is defined by an array of `ColourPos` entries describing
     * colours and their positions. `length` is the number of valid entries in
     * `items` (use `led_colourpos_length()` to compute this when appropriate).
     * The `background` colour is used for pixels not covered by the pattern.
     * The optional `duration` parameter specifies how long, in milliseconds,
     * the pattern should be shown (0 = keep indefinitely).
     *
     * @param items Pointer to an array of `ColourPos` entries describing the pattern.
     * @param length Number of valid entries in `items`.
     * @param background Background `Colour` to draw behind the pattern.
     * @param duration Milliseconds to display the pattern (0 = infinite).
     */
    void led_fancy(ColourPos *items, const size_t length, const Colour &background = default_background, const uint32_t duration = LED_DURATION);


    /**@*/
}
