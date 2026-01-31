#include "shared_dependencies.hpp"

Motors::Motor *SharedDependencies::leftMotor = nullptr;
Motors::Motor *SharedDependencies::rightMotor = nullptr;
Wifi::WifiHandler *SharedDependencies::wifiHandler = nullptr;
BluetoothLE::BLEHandler *SharedDependencies::bleHandler = nullptr;
