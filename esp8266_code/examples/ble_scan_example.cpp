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
* FILE: ble_scan_example.cpp
* CREATION DATE: 11-02-2026
* DESCRIPTION:
* Example usage of the BLE scanning functionality
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: Demonstrates how to use the AT-09 BLE module to scan for devices
* // AR
* +==== END CatFeeder =================+
*/

// This is an example showing how to integrate BLE scanning into your main.cpp

// In setup(), after initializing the BLE handler:
void example_setup()
{
    // ... existing setup code ...

    // Initialize BLE
    BluetoothLE::BLEHandler bleHandler(BLUETOOTH_BAUDRATE);
    SharedDependencies::bleHandler = &bleHandler;
    bleHandler.init();
    bleHandler.enable();

    // Wait for module to stabilize
    delay(500);

    // Test connection to module
    Serial << "Testing BLE module connection...");
    auto result = bleHandler.testConnection();
    if (result == BluetoothLE::ATCommandResult::OK) {
        Serial << "BLE module responding OK!");
    } else {
        Serial << "BLE module not responding properly");
    }

    // Print module information
    bleHandler.printStatus();

    // Optional: Perform initial scan
    Serial << "\nPerforming initial BLE scan...");
    if (bleHandler.startScan(5000)) {  // 5 second scan
        uint8_t deviceCount = bleHandler.getDeviceCount();
        uint8_t overflow = bleHandler.getOverflowCount();
        const BLEDevice *devices = bleHandler.getScannedDevices();

        Serial << "Found " + String(deviceCount) + " BLE devices:");
        for (uint8_t i = 0; i < deviceCount; i++) {
            Serial << "  - " + devices[i].address +
                (devices[i].name.length() > 0 ? " (" + devices[i].name + ")" : "") +
                " RSSI: " + String(devices[i].rssi) + " dBm");
        }

        if (overflow > 0) {
            Serial << "WARNING: " + String(overflow) + " devices were not captured (buffer full)");
        }
    } else {
        Serial << "No devices found or scan failed");
    }

    // ... rest of setup ...
}

// In loop(), you can periodically scan or respond to commands:
static unsigned long lastScan = 0;
const unsigned long SCAN_INTERVAL = 30000;  // Scan every 30 seconds

void example_loop()
{
    // ... existing loop code ...

    // Periodic scanning (optional)
    if (millis() - lastScan > SCAN_INTERVAL) {
        lastScan = millis();
        Serial << "\n--- Periodic BLE Scan ---");
        SharedDependencies::bleHandler->startScan(3000);

        uint8_t count = SharedDependencies::bleHandler->getDeviceCount();
        uint8_t overflow = SharedDependencies::bleHandler->getOverflowCount();
        Serial << "Detected " + String(count) + " nearby devices");
        if (overflow > 0) {
            Serial << "Lost " + String(overflow) + " devices (increase MAX_BLE_DEVICES if needed)");
        }
    }

    // Check for BLE connection status
    bool ble_status = SharedDependencies::bleHandler->isConnected();
    if (ble_status) {
        String received = SharedDependencies::bleHandler->receive();
        if (received.length() > 0) {
            Serial << "Received over Bluetooth: " + received);

            // Example: respond to commands
            if (received.indexOf("SCAN") >= 0) {
                Serial << "Command received: Starting scan...");
                SharedDependencies::bleHandler->startScan(5000);

                // Send results back via BLE
                uint8_t count = SharedDependencies::bleHandler->getDeviceCount();
                const BLEDevice *devices = SharedDependencies::bleHandler->getScannedDevices();

                String response = "Found " + String(count) + " devices\n";
                for (uint8_t i = 0; i < count; i++) {
                    response += devices[i].address + "\n";
                }

                uint8_t overflow = SharedDependencies::bleHandler->getOverflowCount();
                if (overflow > 0) {
                    response += "Lost: " + String(overflow) + "\n";
                }

                SharedDependencies::bleHandler->send(response);
            } else if (received.indexOf("STATUS") >= 0) {
                SharedDependencies::bleHandler->printStatus();
            } else if (received.indexOf("CONNECT:") >= 0) {
                // Extract MAC address (e.g., "CONNECT:001122334455")
                String address = received.substring(8);
                address.trim();
                if (SharedDependencies::bleHandler->connectToDevice(address)) {
                    SharedDependencies::bleHandler->send("Connected to " + address);
                } else {
                    SharedDependencies::bleHandler->send("Connection failed");
                }
            }
        }
    }

    // ... rest of loop ...
}

/*
 * USEFUL AT COMMANDS FOR AT-09 MODULE:
 *
 * Testing & Info:
 *   AT              - Test connection (returns OK)
 *   AT+NAME?        - Get module name
 *   AT+NAMENewName  - Set module name
 *   AT+ADDR?        - Get MAC address
 *   AT+VERS?        - Get firmware version
 *   AT+BAUD?        - Get baud rate
 *
 * Role Management:
 *   AT+ROLE?        - Get role (0=Slave/Peripheral, 1=Master/Central)
 *   AT+ROLE0        - Set to Slave mode (default)
 *   AT+ROLE1        - Set to Master mode (required for scanning)
 *
 * Scanning & Connection (Master mode only):
 *   AT+DISC?        - Start device discovery
 *   AT+CONxxxxxxxxxxxx - Connect to device by MAC (12 hex digits)
 *   AT              - Disconnect from current device
 *
 * Power & Reset:
 *   AT+RESET        - Reset module
 *   AT+SLEEP        - Enter sleep mode
 *
 * Pin & Security:
 *   AT+PASS?        - Get pairing PIN
 *   AT+PASS123456   - Set pairing PIN
 *   AT+TYPE?        - Get pairing mode
 *
 * NOTES:
 * - All commands are case-sensitive
 * - Commands do not end with CR/LF (just send the command string)
 * - Responses typically start with OK+ or ERROR
 * - Some commands require module reset to take effect
 * - Master mode is required for scanning and connecting to other devices
 * - Slave mode is for being discovered and connected to (default)
 */
