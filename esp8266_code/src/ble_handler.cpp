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
* LAST Modified: 23:2:14 11-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the implementation for the ble library.
* // AR
* +==== END CatFeeder =================+
*/
#include "ble_handler.hpp"

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
    delay(100);  // let the module power up and stabilize
    MyUtils::ActiveComponents::Panel::enable(_ble_component);
    _flushSerial();
}

void BluetoothLE::BLEHandler::disable()
{
    digitalWrite(Pins::BLE_EN_PIN, LOW);
    _serial.end();  // Free serial resources (interrupts, buffers)
    MyUtils::ActiveComponents::Panel::disable(_ble_component);
}

bool BluetoothLE::BLEHandler::isConnected() const
{
    const bool status = digitalRead(Pins::BLE_STATE_PIN) == HIGH;
    MyUtils::ActiveComponents::Panel::activity(_ble_component, status);
    return status;
}

void BluetoothLE::BLEHandler::send(const String &data)
{
    MyUtils::ActiveComponents::Panel::activity(_ble_component, true);
    _serial.print(data);

    // flash a dot to indicate sending
    const unsigned int size_raw = data.length();
    uint8_t size;
    if (size_raw == 0) {
        size = 1;
    } else if (size_raw > 255) {
        size = 255;
    } else {
        size = static_cast<uint8_t>(size_raw);
    }
    MyUtils::ActiveComponents::Panel::data_transmission(_ble_component, size);
    MyUtils::ActiveComponents::Panel::activity(_ble_component, false);

}

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

String BluetoothLE::BLEHandler::sendATCommand(const std::string_view &cmd, uint32_t timeout_ms)
{
    MyUtils::ActiveComponents::Panel::activity(_ble_component, true);
    _flushSerial();

    _serial.write(cmd.data(), cmd.size());
    Serial << "[BLE] Sent: " << cmd << endl;

    String response = _readResponse(timeout_ms);
    Serial << "[BLE] Response: " << response << endl;

    MyUtils::ActiveComponents::Panel::activity(_ble_component, false);
    return response;
}

BluetoothLE::ATCommandResult BluetoothLE::BLEHandler::testConnection()
{
    String response = sendATCommand("AT", 1000);
    response.trim();

    if (response.indexOf("OK") >= 0) {
        return ATCommandResult::OK;
    } else if (response.indexOf("ERROR") >= 0) {
        return ATCommandResult::ERROR;
    } else if (response.length() == 0) {
        return ATCommandResult::TIMEOUT;
    }
    return ATCommandResult::UNKNOWN;
}

String BluetoothLE::BLEHandler::getModuleName()
{
    String response = sendATCommand("AT+NAME?", 1000);
    // Response format: "OK+NAME:DeviceName"
    int nameStart = response.indexOf("NAME:");
    if (nameStart >= 0) {
        nameStart += 5; // Skip "NAME:"
        int nameEnd = response.indexOf('\r', nameStart);
        if (nameEnd < 0) nameEnd = response.indexOf('\n', nameStart);
        if (nameEnd < 0) nameEnd = response.length();
        return response.substring(nameStart, nameEnd);
    }
    return "";
}

String BluetoothLE::BLEHandler::getModuleAddress()
{
    String response = sendATCommand("AT+ADDR?", 1000);
    // Response format: "OK+ADDR:001122334455"
    int addrStart = response.indexOf("ADDR:");
    if (addrStart >= 0) {
        addrStart += 5; // Skip "ADDR:"
        int addrEnd = response.indexOf('\r', addrStart);
        if (addrEnd < 0) addrEnd = response.indexOf('\n', addrStart);
        if (addrEnd < 0) addrEnd = response.length();
        return response.substring(addrStart, addrEnd);
    }
    return "";
}

String BluetoothLE::BLEHandler::getVersion()
{
    String response = sendATCommand("AT+VERS?", 1000);
    // Response format: "OK+VERS:HMSoft V523"
    int versStart = response.indexOf("VERS:");
    if (versStart >= 0) {
        versStart += 5;
        int versEnd = response.indexOf('\r', versStart);
        if (versEnd < 0) versEnd = response.indexOf('\n', versStart);
        if (versEnd < 0) versEnd = response.length();
        return response.substring(versStart, versEnd);
    }
    return "";
}

BluetoothLE::BLERole BluetoothLE::BLEHandler::getRole()
{
    String response = sendATCommand("AT+ROLE?", 1000);
    // Response format: "OK+ROLE:0" or "OK+ROLE:1"
    if (response.indexOf("ROLE:0") >= 0) {
        _current_role = BLERole::Slave;
        return BLERole::Slave;
    } else if (response.indexOf("ROLE:1") >= 0) {
        _current_role = BLERole::Master;
        return BLERole::Master;
    }
    _current_role = BLERole::Unknown;
    return BLERole::Unknown;
}

bool BluetoothLE::BLEHandler::setRole(BLERole role)
{
    String cmd = "AT+ROLE";
    cmd += (role == BLERole::Master) ? "1" : "0";

    String response = sendATCommand(cmd.c_str(), 1000);

    if (response.indexOf("OK") >= 0) {
        _current_role = role;
        Serial << "[BLE] Role set to: " << ((role == BLERole::Master) ? "Master" : "Slave") << endl;
        // Module may need reset after role change
        delay(100);
        return true;
    }
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

    String response = sendATCommand(BluetoothLE::AT::DISCOVER, timeout_ms + 1000);

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

bool BluetoothLE::BLEHandler::connectToDevice(const String &address)
{
    // Ensure we're in master mode
    if (_current_role != BLERole::Master) {
        Serial << "[BLE] Must be in Master mode to connect" << endl;
        return false;
    }

    String cmd = "AT+CON" + address;
    String response = sendATCommand(cmd.c_str(), 5000);

    if (response.indexOf("OK+CONN") >= 0) {
        Serial << "[BLE] Connected to: " << address << endl;
        return true;
    }

    Serial << "[BLE] Connection failed to: " << address << endl;
    return false;
}

bool BluetoothLE::BLEHandler::disconnect()
{
    String response = sendATCommand("AT", 1000);  // Sending AT will disconnect
    if (response.indexOf("OK+LOST") >= 0) {
        Serial << "[BLE] Disconnected" << endl;
        return true;
    }
    return false;
}

// ==================== Utility Functions ====================

void BluetoothLE::BLEHandler::reset()
{
    Serial << "[BLE] Resetting module..." << endl;
    sendATCommand("AT+RESET", 2000);
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
        if (response.indexOf("OK") >= 0 || response.indexOf("ERROR") >= 0) {
            delay(50); // Small delay to catch any trailing characters
            while (_serial.available()) {
                response += (char)_serial.read();
            }
            break;
        }

        delay(10);
    }

    return response;
}

BluetoothLE::BLEDevice BluetoothLE::BLEHandler::_parseDiscoveryLine(const String &line)
{
    BLEDevice device;

    // Try different response formats:
    // Format 1: "OK+DISC:001122334455:-045"
    // Format 2: "OK+DIS0:001122334455:DeviceName"
    // Format 3: "OK+DISA:001122334455:DevName:-045"

    if (line.indexOf("OK+DISC:") >= 0 || line.indexOf("OK+DIS") >= 0) {
        int firstColon = line.indexOf(':');
        if (firstColon < 0) return device;

        int secondColon = line.indexOf(':', firstColon + 1);
        int thirdColon = line.indexOf(':', secondColon + 1);

        // Extract address (12 hex digits)
        String address = line.substring(firstColon + 1, (secondColon >= 0) ? secondColon : line.length());
        address.trim();

        // Validate address format (12 hex characters)
        if (address.length() >= 12) {
            device.address = address.substring(0, 12);
            device.valid = true;

            // Extract name if present
            if (secondColon >= 0 && thirdColon >= 0) {
                device.name = line.substring(secondColon + 1, thirdColon);
                device.name.trim();

                // Extract RSSI if present
                String rssiStr = line.substring(thirdColon + 1);
                rssiStr.trim();
                device.rssi = rssiStr.toInt();
            } else if (secondColon >= 0) {
                // Could be either name or RSSI
                String lastPart = line.substring(secondColon + 1);
                lastPart.trim();

                if (lastPart.startsWith("-") || lastPart.startsWith("+")) {
                    // It's RSSI
                    device.rssi = lastPart.toInt();
                } else {
                    // It's a name
                    device.name = lastPart;
                }
            }
        }
    }

    return device;
}

void BluetoothLE::BLEHandler::_flushSerial()
{
    while (_serial.available()) {
        _serial.read();
    }
}
