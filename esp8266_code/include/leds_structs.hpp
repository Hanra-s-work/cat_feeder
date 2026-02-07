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
* FILE: leds_structs.hpp
* CREATION DATE: 07-02-2026
* LAST Modified: 1:44:13 07-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: These are the structures used for the led module overlay.
* // AR
* +==== END CatFeeder =================+
*/
#pragma once
#include <stdint.h>
#include <Arduino.h>
#include "sentinels.hpp"

namespace LED
{
    struct Colour {
        uint8_t r;
        uint8_t g;
        uint8_t b;
        uint8_t w;

        constexpr Colour(uint8_t _r, uint8_t _g, uint8_t _b, uint8_t _w)
            : r(_r), g(_g), b(_b), w(_w)
        {
        }
        constexpr Colour()
            : r(0), g(0), b(0), w(0)
        {
        }
    };

    struct TickAnimation {
        uint16_t interval_ms;
        uint32_t last_update_ms;
        uint32_t current_frame;
        bool _ticked_since_last_check;

        TickAnimation(uint16_t _interval_ms)
            : interval_ms(_interval_ms), last_update_ms(0), current_frame(0), _ticked_since_last_check(false)
        {
        }

        // Call this regularly to update the tick
        void tick()
        {
            uint32_t now = millis();
            if (now - last_update_ms >= interval_ms) {
                current_frame++;
                last_update_ms = now;
                _ticked_since_last_check = true;
            }
        }

        void update() { tick(); }

        // Returns true if ticked since last check, then clears the flag
        bool ticked()
        {
            if (_ticked_since_last_check) {
                _ticked_since_last_check = false;
                return true;
            }
            return false;
        }

        // Optional: peek if it would tick now, without clearing the flag
        bool will_tick() const
        {
            return _ticked_since_last_check;
        }
    };

    struct ColourPos {
        uint16_t pos;
        Colour   colour;
        int16_t pos_step = 0;
        bool node_enabled = true;
        bool disable_on_complete = false;
        TickAnimation tick_animation = TickAnimation(100);

        ColourPos(uint16_t _pos, Colour _colour, int _pos_step = true, bool _node_enabled = true, bool _disable_on_complete = false, TickAnimation _tick_animation = TickAnimation(100))
            : pos(_pos), colour(_colour), pos_step(_pos_step), node_enabled(_node_enabled), disable_on_complete(_disable_on_complete), tick_animation(_tick_animation)
        {
        }
    };

    /* ───────────────────────── Common sentinels ───────────────────────── */

    /**
     * @brief Sentinel indicating "no position" or "end of list" for LED indices.
     *
     * Suitable for terminating arrays of ColourPos or similar structures.
     */
    constexpr uint16_t COLOURPOS_END = UINT16_MAX_VALUE;
} // namespace LED
