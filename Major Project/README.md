# Offline Multilingual Speech-to-Speech Language Translator

## Group 54 – Major Project

### 1. Project Overview

The **Multilingual Speech-to-Speech Language Translator** is a prototype designed to enable communication between people speaking different languages.

The system captures speech through a microphone, converts it into text using the Whisper speech recognition model, translates the recognized text into the selected target language, and generates spoken output using a text-to-speech engine.

The prototype currently supports English-to-Hindi and Hindi-to-English translation.

### 2. Project Objectives

- Develop a portable speech-to-speech translation system.
- Recognize spoken input using speech recognition technology.
- Translate text between English and Hindi.
- Generate translated speech output.
- Provide a simple user interface using physical buttons and an OLED display.
- Explore offline processing and future FPGA integration.

### 3. Hardware Components

| Component | Purpose |
|---|---|
| Raspberry Pi 3B+ | Main processing unit |
| Arduino Uno | Button control and user interface |
| 0.96-inch OLED Display | Displays system status |
| Push Buttons (4) | Language selection and operation control |
| Realme Buds Air 3 Neo | Bluetooth microphone input |
| Wired Earphones | Audio output |
| Logic Level Converter | Voltage compatibility between Raspberry Pi and Arduino |

**Note:** PYNQ-Z2 is considered for future integration and is not part of the currently integrated prototype.

### 4. Software and Technologies

- **Python 3** – Main application programming.
- **Whisper.cpp** – Speech recognition.
- **MyMemory Translation API** – Text translation.
- **eSpeak NG** – Text-to-speech conversion.
- **Arduino IDE** – Arduino programming.
- **SPI Communication** – Communication between Raspberry Pi and Arduino.
- **I2C Communication** – OLED display interface.
- **PipeWire / pw-record / pw-play** – Audio recording and playback.

### 5. Working Principle

The system follows this sequence:

1. The user selects the source and target languages using physical buttons.
2. The microphone captures the user's speech.
3. Raspberry Pi processes the recorded audio using Whisper.cpp.
4. The recognized text is sent to the MyMemory Translation API.
5. The translated text is converted into speech using eSpeak NG.
6. The translated audio is played through wired earphones.
7. The OLED display provides system status information.

### 6. Button Functions

| Button | Function |
|---|---|
| FROM | Select source language |
| TO | Select target language |
| LISTEN | Start listening and speech recognition |
| REVERSE | Reverse the translation direction |

### 7. Supported Languages

| Translation Direction | Status |
|---|---|
| English → Hindi | Tested |
| Hindi → English | Tested |

### 8. Project Directory Structure

```text
Major Project/
│
├── README.md
├── prototype_controller.py
├── arduino_button_receiver.py
├── oled_test.py
├── speech_test.py
├── spi_master.py
├── spi_protocol_test.py
├── spi_response_test.py
├── translation_test.py
│
├── Group_54_Major_Abstract.docx
├── Group_54_Major_Abstract.docx.pdf
│
└── Testing Prototype/
```

### 9. How to Run the Project

**Requirements:**
- Raspberry Pi 3B+ with Raspberry Pi OS.
- Arduino Uno connected to Raspberry Pi.
- Microphone paired and configured.
- Wired earphones connected.
- Required software and Python dependencies installed.

**Step 1: Clone the repository**

```bash
git clone https://github.com/Alexx-1609/Group-54.git
```

**Step 2: Navigate to the project folder**

```bash
cd Group-54/"Major Project"
```

**Step 3: Run the main Python program**

```bash
python3 prototype_controller.py
```

**Step 4: Operate the translator**

Use the physical buttons to select languages and start speech translation.

### 10. Current Implementation and Limitations

- Speech recognition is performed locally using Whisper.cpp.
- Translation currently uses the online MyMemory API and therefore requires an internet connection.
- Speech output is generated using eSpeak NG.
- English-Hindi and Hindi-English translation have been tested.
- Recognition accuracy, translation latency, and overall performance have not yet been formally benchmarked.
- Fully offline translation and PYNQ-Z2 integration are planned future improvements.

### 11. Future Scope

- Implement a fully offline translation model.
- Integrate the PYNQ-Z2 FPGA platform.
- Improve speech recognition accuracy.
- Reduce processing and translation latency.
- Improve text-to-speech voice quality.
- Expand support for additional Indian and international languages.
- Develop a compact and portable hardware design.

### 12. Team Members

**Group 54**

- Ananya Singh
- Pranjali Sinha
- Utkarsh Raj
- Yash Panhale

**Project Supervisor:** Prof. Tejaswini Kar

---

### 13. Repository

GitHub: https://github.com/Alexx-1609/Group-54

**Project:** Offline Multilingual Speech-to-Speech Language Translator Using Raspberry Pi and PYNQ-Z2

**Institution:** KIIT
