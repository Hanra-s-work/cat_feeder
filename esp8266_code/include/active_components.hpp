#pragma once
#include "leds.hpp"
#include "config.hpp"
#include "my_utils.hpp"

namespace MyUtils
{
    namespace ActiveComponents
    {
        /**
         * @brief Command structure for LED display operations.
         *
         * Represents a single LED command with position, color, timing, and state.
         * Used for both persistent base frame slots and temporary overlay commands.
         * Direct struct assignment is safe for LED::Colour members.
         */
        struct LEDCommand
        {
            uint16_t pos = 0;       // LED index
            LED::Colour colour;     // Colour to display
            uint32_t duration = 0;  // duration in ms (0 = infinite)
            uint32_t startTime = 0; // millis() when set
            bool active = false;    // should it currently be displayed?
            constexpr LEDCommand(uint16_t pos = 0, const LED::Colour &colour = LED::Colour(0, 0, 0, 0), uint32_t duration = 0, uint32_t startTime = 0, bool active = false)
                : pos(pos), colour(colour), duration(duration), startTime(startTime), active(active)
            {
            }
        };

        static constexpr uint16_t LED_TOTAL_CMDS = LED_NUMBER;
        extern LEDCommand _led_commands[LED_TOTAL_CMDS];
        extern LEDCommand LED_DEFAULT_BACKGROUND;

        enum class Component : uint8_t {
            Clock,
            WifiStatus,
            MotorLeft,
            MotorRight,
            Bluetooth,
            Server,
            Error,
            _COUNT
        };

        static constexpr size_t component_id(const Component &c) noexcept
        {
            return static_cast<size_t>(c);
        }

        /**
         * @brief Main controller for the dual-strip LED component display system.
         *
         * Manages a 30-LED strip arranged as two 15-LED strips in a U-configuration:
         * - Bottom strip (0-14): Component node positions and movement
         * - Top strip (15-29): Activity indicators and data transmission status
         *
         * The system uses a command buffer with base frame slots (persistent) and
         * temporary command slots (auto-expiring) to efficiently manage complex
         * LED patterns without frame buffer conflicts.
         */
        class Panel
        {
            public:
            static void build_base_frame();

            static void initialize_clock();
            static void initialize_component_status(const Component &c, const bool visible = true);

            static LED::ColourPos &get(Component c);

            static void enable(Component c);
            static void disable(Component c);

            static void activity(const Component c, const bool active = true);
            static void data_transmission(const Component comp, const uint8_t size);

            static void set_colour(Component &c, const LED::Colour &colour);
            static void set_position(Component &c, uint16_t pos);
            static void set_step(Component &c, int16_t step);

            static void tick();      // advance animations
            static void render();    // push to LED::led_fancy

            static constexpr size_t size();

            static LEDCommand *allocate_led_command();
            static void debug_print_commands(); // debug helper

            private:
            static int16_t _led_position;
            static LED::ColourPos _nodes[
                static_cast<size_t>(Component::_COUNT)
            ];
        };

        void initialise_active_components();
    }
}
