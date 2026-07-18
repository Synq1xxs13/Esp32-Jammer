<p align="center">
  <!-- Pentest & Hacking -->
  <img src="https://img.shields.io/badge/pentest-000000?style=for-the-badge&logo=kali-linux&logoColor=white" />
  <img src="https://img.shields.io/badge/hacking-FF0000?style=for-the-badge&logo=hack-the-box&logoColor=white" />
  <img src="https://img.shields.io/badge/security-000000?style=for-the-badge&logo=securityscorecard&logoColor=white" />
  
  <!-- ESP32 & Hardware -->
  <img src="https://img.shields.io/badge/ESP32-E74429?style=for-the-badge&logo=espressif&logoColor=white" />
  <img src="https://img.shields.io/badge/Hardware-4A4A4A?style=for-the-badge&logo=arduino&logoColor=white" />
</p>




# Jammer WiFi/Bluetooth ESP32 + 4x NRF24L01+
Description

Spectrum jamming system for the 2.4 GHz band based on ESP32 and four NRF24L01+ modules. Designed to disrupt WiFi and Bluetooth communications through massive packet injection in the channels used by these protocols.

The device operates in three modes:

    WiFi: concentrated attack on channels 1, 6, 11, 13

    Bluetooth: random channel hopping in the 0-78 range

    Hybrid: combination of fixed WiFi channels and random Bluetooth channels

Required Hardware

    1x ESP32 (any variant with sufficient pins)

    4x NRF24L01+ (with external antenna or PCB)

    1x OLED 128x64 I2C display (SSD1306)

    2x Push buttons

    Electrolytic capacitors 100uF to 470uF (one per NRF module)

    Cabling and breadboard

Pin Connections
SPI Bus (shared)
ESP32 Pin	Function
GPIO18	SCK
GPIO19	MISO
GPIO23	MOSI
NRF24L01+ Control
ESP32 Pin	Function
GPIO4	CE (common for all 4)
GPIO5	CSN module 1
GPIO17	CSN module 2
GPIO16	CSN module 3
GPIO15	CSN module 4
Peripherals
ESP32 Pin	Component
GPIO21	OLED SDA
GPIO22	OLED SCL
GPIO13	Button Start/Stop (pull-up)
GPIO14	Button Mode (pull-up)
Power Supply

    ESP32: 5V via USB or external regulated supply

    NRF24L01+: 3.3V (with decoupling capacitor near each module)

    OLED: 3.3V

Installation
Prerequisites

    MicroPython 1.20 or higher installed on ESP32

    Tool for file transfer (Thonny, mpfshell, ampy, etc.)

Steps

    Download the main Python file

    Connect ESP32 to your computer

    Upload the file to ESP32 as main.py (for auto-start) or with any name (for manual execution)

    Reset or power cycle the device

File Transfer Examples

Using mpfshell:
text

mpfshell
> open ttyUSB0
> put jammer.py
> exec jammer.py

Using ampy:
text

ampy --port /dev/ttyUSB0 put jammer.py /main.py

Operation
Controls

    Button Start/Stop (GPIO13): starts or stops the jamming process

    Button Mode (GPIO14): cycles through WiFi, Bluetooth, and Hybrid modes

Display Information

    M: current mode (WIFI, BT, HYBRID)

    S: status (ON or OFF)

    CH: active channels for each NRF module

Technical Details
Attack Parameters

    Packet size: 32 bytes (maximum for NRF24L01+)

    Burst count: 15 packets per cycle per module

    Total packets per cycle: 60 (4 modules x 15 packets)

    Cycle interval: 5ms

    SPI speed: 10 MHz

    Packet content: fully random bytes

Channel Allocation

    WiFi mode: fixed channels 1, 6, 11, 13 (one per module)

    Bluetooth mode: four random channels from 0-78 (one per module)

    Hybrid mode: channels 1, 6, 11, 13 with random Bluetooth channel substitution

Anti-Filtering Features

    Rotating TX addresses (changes every 4 cycles)

    Random packet payload

    No ACK requests (transmit-only mode)

    Parallel transmission across 4 channels simultaneously

Performance Considerations
Power Requirements

    Each NRF24L01+ draws approximately 12-15mA during transmission

    Total current draw: 50-60mA for NRF modules + ESP32 consumption

    Recommended power supply: at least 500mA for stable operation

Effective Range

    With PCB antenna: up to 10-20 meters

    With external antenna: up to 100-200 meters

    Range depends on obstacles and environmental interference

Limitations

    Only affects the 2.4 GHz band (channels 1-13 for WiFi, 0-78 for Bluetooth)

    Does not affect 5 GHz WiFi networks

    Effectiveness depends on proximity and transmission power

    Cannot selectively target specific devices

Firmware Dependencies

All required modules are included in standard MicroPython:

    machine: GPIO, SPI, I2C, Timer

    time: delays and timing

    random: channel selection and packet generation

    ustruct: not explicitly used but available for extensions

    gc: garbage collection (implicit)

Legal Notice

This device and associated software are intended for educational and research purposes only. The use of jammers is illegal in most jurisdictions and can result in severe penalties including fines and imprisonment. The author assumes no responsibility for illegal or unethical use.
Troubleshooting
No display output

    Check I2C connections (SDA, SCL)

    Verify OLED address (default 0x3C)

    Ensure OLED is powered (3.3V)

No transmission

    Check SPI connections (SCK, MOSI, MISO)

    Verify each NRF module has unique CSN pin

    Confirm CE pin is properly connected

    Check power supply for NRF modules

    Verify capacitors are installed close to each module

Unstable operation

    Add larger capacitors (470uF) near the power source

    Reduce SPI speed if instability persists

    Ensure all ground connections are solid

    Check for loose connections on the breadboard

Buttons not responding

    Verify pull-up resistors (internal pull-ups are used)

    Check pin connections (GPIO13 and GPIO14)

    Debounce delay is already implemented in software

Modifications and Extensions
Changing Burst Count

Modify the loop range in the attack function:
text

for _ in range(15):  # Change this value
    n1.tx(pkt)
    ...

Adding More Modules

Support for up to 8 NRF modules is possible by adding more CSN pins and instantiating additional objects.
Changing TX Power

The NRF24L01+ power level can be adjusted in the RF_SETUP register (0x06). Default is maximum power (0x0F). Lower values reduce power consumption but decrease range.
Credits

Developed for educational purposes in the field of embedded systems and wireless communications security research.
Version History

    v1.0: Initial release with three modes and four module support

    v1.1: Added anti-filtering address rotation

    v1.2: Increased burst density to 15 packets

