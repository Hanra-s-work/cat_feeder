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
* FILE: active_components.cpp
* CREATION DATE: 07-02-2026
* LAST Modified: 22:50:31 11-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the implementation of active components, which are a system for managing the LED strip in a way that allows multiple "components" to display their status and activity without interfering with each other.
* // AR
* +==== END CatFeeder =================+
*/
/**
 * @file active_components.cpp
 * @brief Implementation of the active component LED management system.
 *
 * This file implements a dual-strip LED display system where:
 * - Bottom strip (LEDs 0-14): Shows component node positions
 * - Top strip (LEDs 15-29): Shows data transmission and activity indicators
 *
 * The strips are physically connected in a U-shape, so the top strip is
 * electrically flipped (LED 15 is rightmost, LED 29 is leftmost).
 *
 * Key features:
 * - Persistent base frame with configurable background
 * - Transient node overlays that don't modify the base frame
 * - Temporary command system for activity indicators and data transmission
 * - Automatic expiration of temporary commands
 * - Safe bounds checking and overflow protection
 */
#include "active_components.hpp"

 // NOTE: direct struct assignment is safe for `LED::Colour` so helper removed

int16_t MyUtils::ActiveComponents::Panel::_led_position = 0;
MyUtils::ActiveComponents::LEDCommand MyUtils::ActiveComponents::_led_commands[LED_TOTAL_CMDS] = {};
MyUtils::ActiveComponents::LEDCommand MyUtils::ActiveComponents::LED_DEFAULT_BACKGROUND = MyUtils::ActiveComponents::LEDCommand(
    0,
    LED::led_get_colour_from_pointer(&LED::Colours::Black),
    0,
    0,
    false
);

LED::ColourPos MyUtils::ActiveComponents::Panel::_nodes[] = {
    { component_id(Component::Clock),  LED::yellow_colour },
    { component_id(Component::WifiStatus),  LED::green_colour  },
    { component_id(Component::MotorLeft),  LED::led_get_colour_from_pointer(&LED::Colours::Aqua)   },
    { component_id(Component::MotorRight),  LED::led_get_colour_from_pointer(&LED::Colours::DarkMagenta)   },
    { component_id(Component::Bluetooth),  LED::dark_blue  },
    { component_id(Component::Server),  LED::led_get_colour_from_pointer(&LED::Colours::LimeGreen)   },
    { component_id(Component::Error), LED::red_colour    }
};

void MyUtils::ActiveComponents::Panel::build_base_frame()
{
    // Array is already zero-initialized
    // Set up the base frame slots (0 to LED_NUMBER-1) with proper background color
    for (uint16_t i = 0; i < LED_NUMBER; ++i) {
        _led_commands[i].pos = i;
        _led_commands[i].colour = ActiveComponents::LED_DEFAULT_BACKGROUND.colour;
        _led_commands[i].active = true;
        _led_commands[i].duration = 0; // infinite
    }

    // NOTE: Don't copy node colors here - nodes don't have correct positions yet!
    // They will be set up properly by initialize_component_status() later
}

void MyUtils::ActiveComponents::Panel::initialize_clock()
{
    LED::ColourPos &clock_node = _nodes[static_cast<size_t>(Component::Clock)];
    LED::Nodes::set_position(clock_node, 0);
    LED::Nodes::set_colour(clock_node, LED::yellow_colour);
    LED::Nodes::set_pos_step(clock_node, 1);
    LED::Nodes::set_disable_on_complete(clock_node, false);
    LED::Nodes::set_tick_interval(clock_node, LED_CYCLE_INTERVAL_MS);
}

void MyUtils::ActiveComponents::Panel::initialize_component_status(const Component &c, const bool visible)
{
    LED::ColourPos &component_node = _nodes[static_cast<size_t>(c)];
    LED::Nodes::set_position(component_node, _led_position);
    LED::Nodes::set_pos_step(component_node, LED_COMPONENT_STEP);
    LED::Nodes::set_disable_on_complete(component_node, LED_COMPONENT_DISABLE_ON_COMPLETE);
    LED::Nodes::set_tick_interval(component_node, LED_COMPONENT_INTERVAL_MS);
    if (visible) {
        LED::Nodes::show_node(component_node);
    } else {
        LED::Nodes::hide_node(component_node);
    }
    _led_position += 2;
}

LED::ColourPos &MyUtils::ActiveComponents::Panel::get(Component c)
{
    size_t idx = static_cast<size_t>(c);
    if (idx >= static_cast<size_t>(Component::_COUNT)) {
        Serial << "CRITICAL: Invalid component index: " << idx << endl;
        return _nodes[0]; // Return first node as fallback
    }
    return _nodes[idx];
}

void MyUtils::ActiveComponents::Panel::enable(Component c)
{
    get(c).node_enabled = true;
}

void MyUtils::ActiveComponents::Panel::disable(Component c)
{
    get(c).node_enabled = false;
}

/**
 * @brief Show a temporary activity indicator for a component.
 *
 * Displays a brief pulse at the position adjacent to the component's current
 * position to indicate activity. The pulse automatically expires after 1 second.
 *
 * @param c Component to show activity for
 * @param active If true, shows the activity indicator; if false, does nothing
 */
void MyUtils::ActiveComponents::Panel::activity(const Component c, const bool active)
{
    if (!active) {
        return;
    }

    LED::ColourPos &item = get(c);

    uint16_t pos = item.pos + 1;
    if (pos >= LED_NUMBER) {
        pos = 0;
    }

    // Map component to buffer slot (or find first inactive slot)
    LEDCommand *cmd = allocate_led_command();
    if (!cmd) {
        Serial << "WARNING: LED command buffer full" << endl;
        return; // buffer full, drop ping
    }

    cmd->pos = pos;
    cmd->colour = item.colour;
    cmd->duration = 1000; // long ping (100 seconds)
    cmd->startTime = millis();
    cmd->active = true;

    Serial << "Component activity set at LED pos: " << pos << endl;
}

/**
 * @brief Display data transmission status on the top LED strip.
 *
 * Maps the component's position from the bottom strip (LEDs 0-14) to the corresponding
 * position in the top strip (LEDs 15-29), accounting for the physical U-shaped wiring
 * that flips the top strip. Shows up to 5 LEDs indicating transmission activity.
 *
 * Physical mapping:
 * - Bottom position 0 -> Top position 29 (rightmost)
 * - Bottom position 14 -> Top position 15 (leftmost)
 *
 * @param comp Component whose position determines the starting point
 * @param size Number of LEDs to illuminate (max 5), representing data transmission amount
 */
void MyUtils::ActiveComponents::Panel::data_transmission(const Component comp, const uint8_t size)
{
    constexpr uint8_t BOTTOM_STRIP_SIZE = 15;  // LEDs 0-14
    constexpr uint8_t TOP_STRIP_START = 15;    // LEDs 15-29
    constexpr uint8_t MAX_TRANSMISSION_LEDS = 5;

    // Get the component's current position in the bottom strip
    LED::ColourPos &component_node = get(comp);
    uint16_t bottom_pos = component_node.pos;

    // Validate bottom position is in bottom strip
    if (bottom_pos >= BOTTOM_STRIP_SIZE) {
        Serial << "ERROR: Component position " << bottom_pos << " not in bottom strip" << endl;
        return;
    }

    // Map to top strip position (accounting for physical flip: bottom pos 0 -> top pos 29, bottom pos 14 -> top pos 15)
    const uint16_t top_start = TOP_STRIP_START + (BOTTOM_STRIP_SIZE - 1 - bottom_pos);

    // Limit size to maximum allowed
    const uint8_t shown = min(size, MAX_TRANSMISSION_LEDS);

    LED::Colour &colour = component_node.colour;

    for (uint8_t i = 0; i < MAX_TRANSMISSION_LEDS; ++i) {
        // Calculate LED position (moving left from start position due to flip)
        const uint16_t led_pos = top_start - i;

        // Validate position is within top strip bounds
        if (led_pos < TOP_STRIP_START || led_pos >= LED_NUMBER) {
            break; // Out of top strip bounds
        }

        LEDCommand *cmd = allocate_led_command();
        if (!cmd) {
            Serial << "WARNING: LED command buffer full in data_transmission" << endl;
            return; // buffer full, drop remaining
        }

        cmd->pos = led_pos;
        if (i < shown) {
            cmd->colour = colour;  // Show data transmission
        } else {
            cmd->colour = ActiveComponents::LED_DEFAULT_BACKGROUND.colour;  // Clear remaining
        }
        cmd->duration = 2000; // long duration to keep state visible
        cmd->startTime = millis();
        cmd->active = true;
    }
}


void MyUtils::ActiveComponents::Panel::set_colour(Component &c, const LED::Colour &colour)
{
    get(c).colour = colour;
}

void MyUtils::ActiveComponents::Panel::set_position(Component &c, uint16_t pos)
{
    get(c).pos = pos;
}

void MyUtils::ActiveComponents::Panel::set_step(Component &c, int16_t step)
{
    get(c).pos_step = step;
}

void MyUtils::ActiveComponents::Panel::tick()
{
    for (LED::ColourPos &n : _nodes) {
        if (!n.node_enabled) {
            continue;
        }
        LED::_move_pixel(n, n.pos);
    }
}

/**
 * @brief Render the complete LED display state.
 *
 * Combines the base frame, node overlays, and temporary commands to generate
 * the final LED strip output. Node positions are overlaid transiently without
 * modifying the persistent base frame. Expired temporary commands are cleaned up.
 *
 * Rendering order:
 * 1. Base frame (persistent background colors)
 * 2. Node overlays (component positions, transient)
 * 3. Temporary commands (activity pings, data transmission)
 */
void MyUtils::ActiveComponents::Panel::render()
{
    const uint32_t now = millis();

    // Step 1: Set all LEDs from base frame and update with current node positions
    for (uint16_t i = 0; i < LED_NUMBER; ++i) {
        // CRITICAL: Validate base frame access
        if (i >= LED_TOTAL_CMDS) {
            Serial << "CRITICAL ERROR: Base frame index out of bounds: " << i << endl;
            continue;
        }
        LED::led_set_led_position(i, _led_commands[i].colour, 0, false);
    }

    // Step 2: Update base frame colors if nodes have moved
    for (size_t node_idx = 0; node_idx < static_cast<size_t>(Component::_COUNT); ++node_idx) {
        LED::ColourPos &n = _nodes[node_idx];
        if (!n.node_enabled) {
            continue;
        }

        // Validate position before accessing arrays
        if (n.pos >= LED_NUMBER) {
            Serial << "ERROR: Node[" << node_idx << "] position out of bounds: " << n.pos << endl;
            continue;
        }

        if (n.pos >= LED_TOTAL_CMDS) {
            Serial << "CRITICAL: Node[" << node_idx << "] position exceeds command buffer: " << n.pos << endl;
            continue;
        }

        // Overlay node colour for this render only (do not modify base frame).
        LED::led_set_led_position(n.pos, n.colour, 0, false);
    }

    // Step 3: Apply temporary commands (activity + data_transmission)
    // Start from LED_NUMBER to skip base frame slots
    for (uint16_t i = LED_NUMBER; i < LED_TOTAL_CMDS; ++i) {
        LEDCommand &cmd = _led_commands[i];
        if (!cmd.active) {
            continue;
        }

        // Expire short-duration commands
        if (cmd.duration > 0 && now - cmd.startTime >= cmd.duration) {
            cmd.active = false;
            continue;
        }

        // Validate position before accessing array
        if (cmd.pos >= LED_NUMBER) {
            Serial << "ERROR: Command position out of bounds: " << cmd.pos << endl;
            cmd.active = false; // Deactivate corrupt command
            continue;
        }

        LED::led_set_led_position(cmd.pos, cmd.colour, 0, false);
    }
    LED::led_refresh();
}

constexpr size_t MyUtils::ActiveComponents::Panel::size()
{
    return static_cast<size_t>(Component::_COUNT);
}

MyUtils::ActiveComponents::LEDCommand *MyUtils::ActiveComponents::Panel::allocate_led_command()
{
    // Start from LED_NUMBER to skip base frame slots (0 to LED_NUMBER-1)
    for (uint16_t i = LED_NUMBER; i < LED_TOTAL_CMDS; i++) {
        if (!_led_commands[i].active) {
            // Clear the command slot to prevent stale data
            _led_commands[i].pos = 0;
            _led_commands[i].duration = 0;
            _led_commands[i].startTime = 0;
            _led_commands[i].active = false;
            return &_led_commands[i];
        }
    }
    return nullptr; // no free slot
}

void MyUtils::ActiveComponents::Panel::debug_print_commands()
{
    uint16_t base_count = 0;
    uint16_t temp_count = 0;
    Serial << "=== LED Command Buffer Debug ===" << endl;
    Serial << "Base Frame (0-" << (LED_NUMBER - 1) << "):" << endl;
    for (uint16_t i = 0; i < LED_NUMBER; i++) {
        if (_led_commands[i].active) base_count++;
    }
    Serial << "  Active: " << base_count << "/" << LED_NUMBER << endl;

    Serial << "Temporary Commands (" << LED_NUMBER << "-" << LED_TOTAL_CMDS - 1 << "):" << endl;
    Serial << "Total active: " << base_count + temp_count << "/" << LED_TOTAL_CMDS << endl;
    Serial << "=================================" << endl;
}

void MyUtils::ActiveComponents::initialise_active_components()
{
    unsigned long artificial_delay = 50;
    Panel::build_base_frame();
    int16_t max_steps = component_id(Component::_COUNT);
    Serial << "Total steps: " << max_steps << endl;
    MyUtils::display_percentage(LED::dark_blue, LED::green_colour, 0, max_steps);
    delay(artificial_delay);
    Panel::initialize_clock();
    MyUtils::display_percentage(LED::dark_blue, LED::green_colour, 1, max_steps);
    Serial << "Clock animation set up" << endl;
    delay(artificial_delay);
    Panel::initialize_component_status(Component::WifiStatus, false);
    MyUtils::display_percentage(LED::dark_blue, LED::green_colour, 2, max_steps);
    Serial << "Component status animations set up" << endl;
    delay(artificial_delay);
    Panel::initialize_component_status(Component::Bluetooth, false);
    MyUtils::display_percentage(LED::dark_blue, LED::green_colour, 3, max_steps);
    Serial << " - Bluetooth: success" << endl;
    delay(artificial_delay);
    Panel::initialize_component_status(Component::MotorLeft, false);
    MyUtils::display_percentage(LED::dark_blue, LED::green_colour, 4, max_steps);
    Serial << " - MotorLeft: success" << endl;
    delay(artificial_delay);
    Panel::initialize_component_status(Component::MotorRight, false);
    MyUtils::display_percentage(LED::dark_blue, LED::green_colour, 5, max_steps);
    Serial << " - MotorRight: success" << endl;
    delay(artificial_delay);
    Panel::initialize_component_status(Component::Server, false);
    MyUtils::display_percentage(LED::dark_blue, LED::green_colour, 6, max_steps);
    Serial << " - Server: success" << endl;
    delay(artificial_delay);
    Panel::initialize_component_status(Component::Error, false);
    MyUtils::display_percentage(LED::dark_blue, LED::green_colour, 7, max_steps);
    Serial << " - Error: success" << endl;
    Panel::build_base_frame();

    // Force a render to clear any artifacts from display_percentage calls
    delay(artificial_delay);
    Panel::render();
    Serial << "Active components initialized - render complete" << endl;
}
