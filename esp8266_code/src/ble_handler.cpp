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
* FILE: ble_handler.cpp
* CREATION DATE: 07-02-2026
* LAST Modified: 2:12:52 12-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the implementation for the ble library.
* // AR
* +==== END CatFeeder =================+
*/
#include "ble_handler.hpp"
#include "ble_AT_quickies.hpp"
#include "ble_constants.hpp"
#include <cstring>  // For strstr, strchr, atoi, strncpy

BluetoothLE::BLEHandler::BLEHandler(uint32_t baud)
    : _serial(Pins::BLE_RXD_PIN, Pins::BLE_TXD_PIN), _baud(baud)
{
}

void BluetoothLE::BLEHandler::init()
{
    pinMode(Pins::BLE_EN_PIN, OUTPUT);
    digitalWrite(Pins::BLE_EN_PIN, LOW);  // default off
    pinMode(Pins::BLE_STATE_PIN, INPUT);
    MyUtils::ActiveComponents::Panel::enable(_ble_component);
}

void BluetoothLE::BLEHandler::enable()
{
    _serial.begin(_baud);  // Initialize serial communication
    digitalWrite(Pins::BLE_EN_PIN, HIGH);
    delay(Constants::POWER_UP_DELAY_MS);  // let the module power up and stabilize
    MyUtils::ActiveComponents::Panel::enable(_ble_component);
    _flushSerial();
}

void BluetoothLE::BLEHandler::disable()
{
    digitalWrite(Pins::BLE_EN_PIN, LOW);
    _serial.end();  // Free serial resources (interrupts, buffers)
    MyUtils::ActiveComponents::Panel::disable(_ble_component);
}

void BluetoothLE::BLEHandler::changeBaudRate(uint32_t new_baud)
{
    _baud = new_baud;
    _serial.end();  // Close current serial connection
    delay(Constants::SERIAL_REINIT_DELAY_MS);      // Small delay for cleanup
    _serial.begin(_baud);  // Reinitialize at new baud rate
    delay(Constants::SERIAL_STABILIZE_DELAY_MS);      // Let it stabilize
    _flushSerial(); // Clear any garbage
}

bool BluetoothLE::BLEHandler::isConnected() const
{
    const bool status = digitalRead(Pins::BLE_STATE_PIN) == HIGH;
    MyUtils::ActiveComponents::Panel::activity(_ble_component, status);
    return status;
}

// ==================== Send/Receive Operations ====================

// Buffer-based send (no heap allocation)
void BluetoothLE::BLEHandler::send(const char *data, size_t length)
{
    MyUtils::ActiveComponents::Panel::activity(_ble_component, true);
    _serial.write(reinterpret_cast<const uint8_t *>(data), length);

    // flash a dot to indicate sending
    uint8_t size = (length > Constants::MAX_TRANSMISSION_SIZE) ? Constants::MAX_TRANSMISSION_SIZE : static_cast<uint8_t>(length);
    MyUtils::ActiveComponents::Panel::data_transmission(_ble_component, size);
    MyUtils::ActiveComponents::Panel::activity(_ble_component, false);
}

// String-based send (for convenience)
void BluetoothLE::BLEHandler::send(const String &data)
{
    send(data.c_str(), data.length());
}

// Buffer-based receive (no heap allocation)
size_t BluetoothLE::BLEHandler::receive(char *buffer, size_t buffer_size)
{
    MyUtils::ActiveComponents::Panel::activity(_ble_component, true);
    size_t bytes_read = 0;

    while (_serial.available() && bytes_read < buffer_size - 1) {  // Leave room for null terminator
        buffer[bytes_read] = _serial.read();
        bytes_read++;
        MyUtils::ActiveComponents::Panel::data_transmission(_ble_component, 1);
    }
    buffer[bytes_read] = '\0';  // Null terminate

    MyUtils::ActiveComponents::Panel::activity(_ble_component, false);
    return bytes_read;
}

// String-based receive (for convenience, allocates)
String BluetoothLE::BLEHandler::receive()
{
    MyUtils::ActiveComponents::Panel::activity(_ble_component, true);
    String received;
    while (_serial.available()) {
        char c = _serial.read();
        received += c;
        MyUtils::ActiveComponents::Panel::data_transmission(_ble_component, 1);
    }
    MyUtils::ActiveComponents::Panel::activity(_ble_component, false);
    return received;
}

// ==================== AT Command Operations ====================

// Buffer-based sendATCommand (no heap allocation - hot path)
size_t BluetoothLE::BLEHandler::sendATCommand(const std::string_view &cmd, char *response_buffer, size_t buffer_size, uint32_t timeout_ms)
{
    MyUtils::ActiveComponents::Panel::activity(_ble_component, true);
    _flushSerial();

    // Commands already include \r\n in constants
    _serial.write(cmd.data(), cmd.size());
    Serial << "[BLE] Sent: " << cmd << endl;

    size_t bytes_read = _readResponseToBuffer(response_buffer, buffer_size, timeout_ms);

    // Log response (safe to print - buffer is null-terminated)
    Serial << "[BLE] Response: " << response_buffer << endl;

    MyUtils::ActiveComponents::Panel::activity(_ble_component, false);
    return bytes_read;
}

// String-based sendATCommand (for diagnostics/convenience, allocates)
String BluetoothLE::BLEHandler::sendATCommand(const std::string_view &cmd, uint32_t timeout_ms)
{
    MyUtils::ActiveComponents::Panel::activity(_ble_component, true);
    _flushSerial();

    // Commands already include \r\n in constants
    _serial.write(cmd.data(), cmd.size());
    Serial << "[BLE] Sent: " << cmd << endl;

    String response = _readResponse(timeout_ms);
    Serial << "[BLE] Response: " << response << endl;

    MyUtils::ActiveComponents::Panel::activity(_ble_component, false);
    return response;
}

BluetoothLE::ATCommandResult BluetoothLE::BLEHandler::testConnection()
{
    // Use buffer version to avoid heap allocation
    char response[Constants::TEST_RESPONSE_BUFFER_SIZE];  // Small buffer on stack
    size_t len = sendATCommand(AT::TEST, response, sizeof(response), 1000);

    // Trim whitespace manually
    while (len > 0 && (response[len - 1] == ' ' || response[len - 1] == '\r' || response[len - 1] == '\n')) {
        response[--len] = '\0';
    }

    // Check for OK in response (case-insensitive check not needed, AT responses are uppercase)
    if (len > 0 && strstr(response, AT::Responses::Ok::OK.data()) != nullptr) {
        return ATCommandResult::OK;
    } else if (strstr(response, AT::Responses::Error::ERROR.data()) != nullptr) {
        return ATCommandResult::ERROR;
    } else if (len == 0) {
        return ATCommandResult::TIMEOUT;
    }
    return ATCommandResult::UNKNOWN;
}

String BluetoothLE::BLEHandler::getModuleName()
{
    String response = sendATCommand(AT::NAME_GET, 1000);
    // Response format: "OK+NAME:DeviceName"
    int nameStart = response.indexOf(AT::Responses::Ok::NAME.data());
    if (nameStart >= 0) {
        nameStart += Constants::RESPONSE_PREFIX_NAME_LENGTH; // Skip "NAME:"
        int nameEnd = response.indexOf('\r', nameStart);
        if (nameEnd < 0) nameEnd = response.indexOf('\n', nameStart);
        if (nameEnd < 0) nameEnd = response.length();
        return response.substring(nameStart, nameEnd);
    }
    return "";
}

String BluetoothLE::BLEHandler::getModuleAddress()
{
    String response = sendATCommand(AT::ADDR_GET, 1000);
    // Response format: "OK+ADDR:001122334455"
    int addrStart = response.indexOf(AT::Responses::Ok::ADDR.data());
    if (addrStart >= 0) {
        addrStart += Constants::RESPONSE_PREFIX_ADDR_LENGTH; // Skip "ADDR:"
        int addrEnd = response.indexOf('\r', addrStart);
        if (addrEnd < 0) addrEnd = response.indexOf('\n', addrStart);
        if (addrEnd < 0) addrEnd = response.length();
        return response.substring(addrStart, addrEnd);
    }
    return "";
}

String BluetoothLE::BLEHandler::getVersion()
{
    String response = sendATCommand(AT::VERSION_GET, 1000);
    // Response format: "OK+VERS:HMSoft V523"
    int versStart = response.indexOf(AT::Responses::Ok::VERS.data());
    if (versStart >= 0) {
        versStart += Constants::RESPONSE_PREFIX_VERS_LENGTH;
        int versEnd = response.indexOf('\r', versStart);
        if (versEnd < 0) versEnd = response.indexOf('\n', versStart);
        if (versEnd < 0) versEnd = response.length();
        return response.substring(versStart, versEnd);
    }
    return "";
}

BluetoothLE::BLERole BluetoothLE::BLEHandler::getRole()
{
    String response = sendATCommand(AT::ROLE_GET, 1000);
    // Response format varies: "OK+Get:0", "+Get:0", or may return ERROR
    // Check for Slave (Role 0)
    if (response.indexOf(AT::Responses::Ok::Role::SLAVE.data()) >= 0 ||
        response.indexOf(AT::Responses::Ok::Role::ALT_SLAVE.data()) >= 0) {
        _current_role = BLERole::Slave;
        return BLERole::Slave;
    }
    // Check for Master (Role 1)
    else if (response.indexOf(AT::Responses::Ok::Role::MASTER.data()) >= 0 ||
        response.indexOf(AT::Responses::Ok::Role::ALT_MASTER.data()) >= 0) {
        _current_role = BLERole::Master;
        return BLERole::Master;
    }
    // If query fails, try to infer from SET_ROLE responses
    else if (response.indexOf(AT::Responses::Ok::Role::SET_SLAVE.data()) >= 0) {
        _current_role = BLERole::Slave;
        return BLERole::Slave;
    } else if (response.indexOf(AT::Responses::Ok::Role::SET_MASTER.data()) >= 0) {
        _current_role = BLERole::Master;
        return BLERole::Master;
    }

    Serial << "[BLE] Unable to determine role from response: " << response << endl;
    _current_role = BLERole::Unknown;
    return BLERole::Unknown;
}

bool BluetoothLE::BLEHandler::setRole(BLERole role)
{
    // Use compile-time constants to avoid string allocation
    const std::string_view cmd = (role == BLERole::Master) ? AT::ROLE_MASTER : AT::ROLE_SLAVE;
    String response = sendATCommand(cmd, 1000);

    // Check for various success responses: "OK", "+ROLE=1", "+ROLE=0"
    bool success = false;
    if (role == BLERole::Master) {
        success = (response.indexOf(AT::Responses::Ok::OK.data()) >= 0 ||
            response.indexOf(AT::Responses::Ok::Role::SET_MASTER.data()) >= 0);
    } else {
        success = (response.indexOf(AT::Responses::Ok::OK.data()) >= 0 ||
            response.indexOf(AT::Responses::Ok::Role::SET_SLAVE.data()) >= 0);
    }

    if (success) {
        _current_role = role;
        Serial << "[BLE] Role set to: " << ((role == BLERole::Master) ? "Master" : "Slave") << endl;
        // Module may need reset after role change
        delay(Constants::ROLE_CHANGE_DELAY_MS);
        return true;
    }

    Serial << "[BLE] Failed to set role. Response: " << response << endl;
    return false;
}

// ==================== Scanning Operations ====================

bool BluetoothLE::BLEHandler::startScan(uint32_t timeout_ms)
{
    // Ensure we're in master mode
    if (_current_role == BLERole::Unknown) {
        getRole(); // Query current role
    }

    if (_current_role != BLERole::Master) {
        Serial << "[BLE] Not in Master mode. Switching..." << endl;
        if (!setRole(BLERole::Master)) {
            Serial << "[BLE] Failed to set Master mode!" << endl;
            return false;
        }
    }

    clearScannedDevices();
    Serial << "[BLE] Starting device discovery..." << endl;

    String response = sendATCommand(AT::DISCOVER, timeout_ms + 1000);

    // Parse response for discovered devices
    // Response format (varies by firmware):
    // "OK+DISC:001122334455:-045" (address:rssi)
    // or "OK+DISCS" followed by multiple "OK+DIS0:001122334455:DevName"

    unsigned int pos = 0;
    while (pos < response.length()) {
        int lineEnd = response.indexOf('\n', pos);
        if (lineEnd < 0) lineEnd = response.length();

        String line = response.substring(pos, lineEnd);
        line.trim();

        BLEDevice device = _parseDiscoveryLine(line);
        if (device.valid) {
            if (_device_count < MAX_BLE_DEVICES) {
                _scanned_devices[_device_count] = device;
                _device_count++;
                Serial << "[BLE] Found device: " << device.address << " (" << device.name << ") RSSI: " << device.rssi << endl;
            } else {
                _overflow_count++;
                Serial << "[BLE] Device buffer full! Lost device: " << device.address << endl;
            }
        }

        pos = lineEnd + 1;
    }

    Serial << "[BLE] Scan complete. Found " << _device_count << " device(s)" << endl;
    if (_overflow_count > 0) {
        Serial << "[BLE] WARNING: " << _overflow_count << " device(s) lost due to buffer overflow!" << endl;
    }
    return _device_count > 0;
}

const BluetoothLE::BLEDevice *BluetoothLE::BLEHandler::getScannedDevices() const
{
    return _scanned_devices;
}

uint8_t BluetoothLE::BLEHandler::getDeviceCount() const
{
    return _device_count;
}

uint8_t BluetoothLE::BLEHandler::getOverflowCount() const
{
    return _overflow_count;
}

void BluetoothLE::BLEHandler::clearScannedDevices()
{
    _device_count = 0;
    _overflow_count = 0;
    // Optionally clear the array data
    for (uint8_t i = 0; i < MAX_BLE_DEVICES; i++) {
        _scanned_devices[i].valid = false;
    }
}

// Buffer-based connectToDevice (no String allocation)
bool BluetoothLE::BLEHandler::connectToDevice(const char *address)
{
    // Ensure we're in master mode
    if (_current_role != BLERole::Master) {
        Serial << "[BLE] Must be in Master mode to connect" << endl;
        return false;
    }

    // Build command with no String usage
    char cmd[Constants::CONNECT_COMMAND_BUFFER_SIZE];  // "AT+CON" + 12 hex digits + AT_NEWLINE + null
    snprintf(cmd, sizeof(cmd), "AT+CON%s" AT_NEWLINE, address);

    // Use string_view to wrap the buffer for sendATCommand
    std::string_view cmd_view(cmd);

    char response[Constants::COMMAND_RESPONSE_BUFFER_SIZE];  // Buffer for response
    size_t len = sendATCommand(cmd_view, response, sizeof(response), 5000);

    if (len > 0 && strstr(response, AT::Responses::Ok::CONN.data()) != nullptr) {
        Serial << "[BLE] Connected to: " << address << endl;
        return true;
    }

    Serial << "[BLE] Connection failed to: " << address << endl;
    return false;
}

// String-based connectToDevice (for convenience)
bool BluetoothLE::BLEHandler::connectToDevice(const String &address)
{
    return connectToDevice(address.c_str());
}

bool BluetoothLE::BLEHandler::disconnect()
{
    String response = sendATCommand(AT::TEST, 1000);  // Sending AT will disconnect
    if (response.indexOf(AT::Responses::Ok::LOST.data()) >= 0) {
        Serial << "[BLE] Disconnected" << endl;
        return true;
    }
    return false;
}

// ==================== Utility Functions ====================

void BluetoothLE::BLEHandler::reset()
{
    Serial << "[BLE] Resetting module..." << endl;
    sendATCommand(AT::RESET, 2000);
    delay(1000);  // Give module time to reset
    _current_role = BLERole::Unknown;
    clearScannedDevices();
}

void BluetoothLE::BLEHandler::printStatus()
{
    BLERole role = getRole();
    bool connected = isConnected();
    Serial << "========== BLE Module Status ==========" << endl;
    Serial << "Module Name: " << getModuleName() << endl;
    Serial << "Module Address: " << getModuleAddress() << endl;
    Serial << "Version: " << getVersion() << endl;

    Serial << "Role: ";
    Serial << ((role == BLERole::Master) ? "Master" : (role == BLERole::Slave) ? "Slave" : "Unknown");
    Serial << endl;
    Serial << "Connected: " << (connected ? "Yes" : "No") << endl;
    Serial << "Scanned Devices: " << _device_count << "/" << MAX_BLE_DEVICES << endl;
    if (_overflow_count > 0) {
        Serial << "Lost Devices: " << _overflow_count << endl;
    }
    Serial << "=======================================" << endl;
}

// ==================== Private Helper Methods ====================

// Buffer-based response reader (no heap allocation - hot path)
size_t BluetoothLE::BLEHandler::_readResponseToBuffer(char *buffer, size_t buffer_size, uint32_t timeout_ms)
{
    size_t pos = 0;
    unsigned long start = millis();
    buffer[0] = '\0';  // Initialize as empty string

    while (millis() - start < timeout_ms && pos < buffer_size - 1) {
        while (_serial.available() && pos < buffer_size - 1) {
            char c = _serial.read();
            buffer[pos++] = c;
            start = millis(); // Reset timeout on receiving data
        }
        buffer[pos] = '\0';  // Always null-terminate

        // Check if we got a complete response
        if (strstr(buffer, AT::Responses::Ok::OK.data()) != nullptr || strstr(buffer, AT::Responses::Error::ERROR.data()) != nullptr) {
            delay(Constants::RESPONSE_TRAILING_DELAY_MS); // Small delay to catch any trailing characters
            while (_serial.available() && pos < buffer_size - 1) {
                buffer[pos++] = _serial.read();
            }
            buffer[pos] = '\0';
            break;
        }

        delay(Constants::RESPONSE_POLL_DELAY_MS);
    }

    return pos;
}

// String-based response reader (allocates - for convenience/diagnostics)
String BluetoothLE::BLEHandler::_readResponse(uint32_t timeout_ms)
{
    String response = "";
    unsigned long start = millis();

    while (millis() - start < timeout_ms) {
        while (_serial.available()) {
            char c = _serial.read();
            response += c;
            start = millis(); // Reset timeout on receiving data
        }

        // Check if we got a complete response
        if (response.indexOf(AT::Responses::Ok::OK.data()) >= 0 || response.indexOf(AT::Responses::Error::ERROR.data()) >= 0) {
            delay(Constants::RESPONSE_TRAILING_DELAY_MS); // Small delay to catch any trailing characters
            while (_serial.available()) {
                response += (char)_serial.read();
            }
            break;
        }

        delay(Constants::RESPONSE_POLL_DELAY_MS);
    }

    return response;
}

// Buffer-based discovery line parser (no heap allocation)
BluetoothLE::BLEDevice BluetoothLE::BLEHandler::_parseDiscoveryLine(const char *line, size_t length)
{
    BLEDevice device;
    device.valid = false;
    device.address[0] = '\0';
    device.name[0] = '\0';
    device.rssi = 0;

    // Try different response formats:
    // Format 1: "OK+DISC:001122334455:-045"
    // Format 2: "OK+DIS0:001122334455:DeviceName"
    // Format 3: "OK+DISA:001122334455:DevName:-045"

    const char *disc_marker = strstr(line, AT::Responses::Ok::DISC.data());
    const char *dis_marker = (disc_marker == nullptr) ? strstr(line, AT::Responses::Ok::DIS.data()) : disc_marker;

    if (dis_marker != nullptr) {
        const char *firstColon = strchr(dis_marker, ':');
        if (firstColon == nullptr) return device;

        const char *secondColon = strchr(firstColon + 1, ':');
        const char *thirdColon = (secondColon != nullptr) ? strchr(secondColon + 1, ':') : nullptr;

        // Extract address (12 hex digits)
        const char *addr_start = firstColon + 1;
        const char *addr_end = (secondColon != nullptr) ? secondColon : (line + length);
        size_t addr_len = addr_end - addr_start;

        // Validate address format (12 hex characters)
        if (addr_len >= Constants::BLE_ADDRESS_LENGTH) {
            // Copy address (max 12 chars)
            size_t copy_len = (addr_len > Constants::BLE_ADDRESS_LENGTH) ? Constants::BLE_ADDRESS_LENGTH : addr_len;
            strncpy(device.address, addr_start, copy_len);
            device.address[copy_len] = '\0';
            device.valid = true;

            // Extract name if present
            if (secondColon != nullptr && thirdColon != nullptr) {
                const char *name_start = secondColon + 1;
                const char *name_end = thirdColon;
                size_t name_len = name_end - name_start;

                if (name_len > 0 && name_len < sizeof(device.name)) {
                    // Trim leading/trailing whitespace
                    while (name_len > 0 && (*name_start == ' ' || *name_start == '\r' || *name_start == '\n')) {
                        name_start++;
                        name_len--;
                    }
                    while (name_len > 0 && (name_start[name_len - 1] == ' ' || name_start[name_len - 1] == '\r' || name_start[name_len - 1] == '\n')) {
                        name_len--;
                    }

                    if (name_len > 0) {
                        strncpy(device.name, name_start, name_len);
                        device.name[name_len] = '\0';
                    }
                }

                // Extract RSSI if present
                const char *rssi_start = thirdColon + 1;
                device.rssi = atoi(rssi_start);
            } else if (secondColon != nullptr) {
                // Could be either name or RSSI
                const char *last_start = secondColon + 1;

                // Skip whitespace
                while (*last_start == ' ' || *last_start == '\r' || *last_start == '\n') {
                    last_start++;
                }

                if (*last_start == '-' || *last_start == '+' || (*last_start >= '0' && *last_start <= '9')) {
                    // It's RSSI
                    device.rssi = atoi(last_start);
                } else {
                    // It's a name
                    size_t name_len = (line + length) - last_start;
                    if (name_len > 0 && name_len < sizeof(device.name)) {
                        // Trim trailing whitespace
                        while (name_len > 0 && (last_start[name_len - 1] == ' ' || last_start[name_len - 1] == '\r' || last_start[name_len - 1] == '\n')) {
                            name_len--;
                        }
                        if (name_len > 0) {
                            strncpy(device.name, last_start, name_len);
                            device.name[name_len] = '\0';
                        }
                    }
                }
            }
        }
    }

    return device;
}

// String-based discovery line parser (for backwards compatibility)
BluetoothLE::BLEDevice BluetoothLE::BLEHandler::_parseDiscoveryLine(const String &line)
{
    return _parseDiscoveryLine(line.c_str(), line.length());
}

void BluetoothLE::BLEHandler::_flushSerial()
{
    while (_serial.available()) {
        _serial.read();
    }
}

// ==================== Diagnostic & Testing Functions ====================

void BluetoothLE::BLEHandler::testHardware()
{
    Serial << "\n=== BLE Hardware Diagnostics ===" << endl;
    Serial << "BLE_EN_PIN (GPIO" << Pins::BLE_EN_PIN << ") state: " << (digitalRead(Pins::BLE_EN_PIN) ? "HIGH" : "LOW") << endl;
    Serial << "BLE_STATE_PIN (A0) value: " << analogRead(Pins::BLE_STATE_PIN) << endl;
    Serial << "BLE_RXD_PIN: GPIO" << Pins::BLE_RXD_PIN << " (should connect to AT-09 TX)" << endl;
    Serial << "BLE_TXD_PIN: GPIO" << Pins::BLE_TXD_PIN << " (should connect to AT-09 RX)" << endl;
    Serial << "Baud rate: " << _baud << endl;

    Serial << "\nTrying basic AT command..." << endl;
    ATCommandResult result = testConnection();
    Serial << "Result: ";
    switch (result) {
        case ATCommandResult::OK: Serial << "OK"; break;
        case ATCommandResult::ERROR: Serial << "ERROR"; break;
        case ATCommandResult::TIMEOUT: Serial << "TIMEOUT"; break;
        default: Serial << "UNKNOWN"; break;
    }
    Serial << endl;
    Serial << "=================================\n" << endl;
}

void BluetoothLE::BLEHandler::testBaudRates()
{
    Serial << "\n=== Testing Common Baud Rates ===" << endl;

    const uint32_t baud_rates[] = { 9600, 19200, 38400, 57600, 115200 };
    const uint8_t num_rates = sizeof(baud_rates) / sizeof(baud_rates[0]);

    for (uint8_t i = 0; i < num_rates; i++) {
        Serial << "\n[" << (i + 1) << "/" << num_rates << "] Testing " << baud_rates[i] << " baud..." << endl;

        changeBaudRate(baud_rates[i]);
        delay(200);

        ATCommandResult result = testConnection();
        Serial << "Result: ";
        switch (result) {
            case ATCommandResult::OK:
                Serial << "OK - FOUND WORKING BAUD RATE!" << endl;
                Serial << "=================================\n" << endl;
                Serial << "*** SUCCESS: Module responds at " << baud_rates[i] << " baud ***\n" << endl;
                return;
            case ATCommandResult::ERROR:
                Serial << "ERROR" << endl;
                break;
            case ATCommandResult::TIMEOUT:
                Serial << "TIMEOUT" << endl;
                break;
            default:
                Serial << "UNKNOWN" << endl;
                break;
        }
    }

    Serial << "\n=== No working baud rate found ===" << endl;
    Serial << "This suggests a hardware issue (TX/RX swap or power problem)" << endl;
    Serial << "\nRestoring to original baud rate (" << BLUETOOTH_BAUDRATE << ")..." << endl;
    changeBaudRate(BLUETOOTH_BAUDRATE);
    Serial << "=================================\n" << endl;
}

void BluetoothLE::BLEHandler::printInitialScan(uint32_t scan_duration_ms)
{
    const bool scan_response = startScan(scan_duration_ms);
    if (scan_response) {
        const uint8_t deviceCount = getDeviceCount();
        const uint8_t overflow = getOverflowCount();
        const BLEDevice *devices = getScannedDevices();

        Serial << "Found " << deviceCount << " BLE devices:" << endl;
        for (uint8_t i = 0; i < deviceCount; i++) {
            Serial << " - " << devices[i].address;
            if (strlen(devices[i].name) > 0) {
                Serial << " (" << devices[i].name << ")";
            }
            Serial << " RSSI: " << devices[i].rssi << " dBm" << endl;
        }

        if (overflow > 0) {
            Serial << "WARNING: " << overflow << " devices were not captured (buffer full)" << endl;
        }
    } else {
        Serial << "No devices found or scan failed" << endl;
    }
}

void BluetoothLE::BLEHandler::printConnectionStatus()
{
    Serial << "Checking BLE connection status" << endl;
    ATCommandResult status = testConnection();
    Serial << "Connection status: ";
    switch (status) {
        case ATCommandResult::OK:
            Serial << "[OK]" << endl;
            break;
        case ATCommandResult::TIMEOUT:
            Serial << "[TIMEOUT]" << endl;
            break;
        case ATCommandResult::ERROR:
            Serial << "[ERROR]" << endl;
            break;
        case ATCommandResult::UNKNOWN:
            Serial << "[UNKNOWN]" << endl;
            break;
        default:
            Serial << "[UNKNOWN TYPE]" << endl;
            break;
    }
}

void BluetoothLE::BLEHandler::printPeriodicScan()
{
    Serial << "\n========== Periodic BLE Scan ==========" << endl;
    startScan(BLE_PERIODIC_SCAN_DURATION);

    uint8_t count = getDeviceCount();
    uint8_t overflow = getOverflowCount();

    Serial << "Detected " << count << " nearby BLE device(s)" << endl;

    if (count > 0) {
        const BLEDevice *devices = getScannedDevices();
        for (uint8_t i = 0; i < count; i++) {
            Serial << "  [" << (i + 1) << "] " << devices[i].address;
            if (strlen(devices[i].name) > 0) {
                Serial << " - " << devices[i].name;
            }
            Serial << " (RSSI: " << devices[i].rssi << " dBm)" << endl;
        }
    }

    if (overflow > 0) {
        Serial << "⚠ Lost " << overflow << " devices (increase MAX_BLE_DEVICES if needed)" << endl;
    }
    Serial << "=======================================" << endl;
}
