#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ---------- OLED configuration ----------

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_ADDRESS 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// ---------- Button pins ----------

const byte FROM_BUTTON = 2;
const byte TO_BUTTON = 3;
const byte LISTEN_BUTTON = 4;
const byte REVERSE_BUTTON = 5;

// ---------- Button events sent to Raspberry Pi ----------

const byte EVENT_NONE = 0;
const byte EVENT_FROM = 'F';
const byte EVENT_TO = 'T';
const byte EVENT_LISTEN_PRESS = 'P';
const byte EVENT_LISTEN_RELEASE = 'p';
const byte EVENT_REVERSE = 'R';

// Pi acknowledges a button event with this byte.
const byte SPI_ACK = 'A';

// ---------- OLED status codes received from Pi ----------

const byte STATUS_READY = '1';
const byte STATUS_LISTENING = '2';
const byte STATUS_PROCESSING = '3';
const byte STATUS_SPEAKING = '4';
const byte STATUS_DONE = '5';
const byte STATUS_ERROR = '6';

const byte STATUS_FROM_EN = '7';
const byte STATUS_TO_HI = '8';
const byte STATUS_FROM_HI = '9';
const byte STATUS_TO_EN = '0';

// ---------- Shared SPI state ----------

volatile byte pendingEvent = EVENT_NONE;
volatile byte requestedStatus = 0;

// ---------- Button state ----------

bool lastFrom = HIGH;
bool lastTo = HIGH;
bool lastListen = HIGH;
bool lastReverse = HIGH;

// ---------- OLED functions ----------

void showStatus(const char *line1, const char *line2 = "") {
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);

  display.setCursor(0, 16);
  display.println(line1);

  if (line2[0] != '\0') {
    display.setCursor(0, 36);
    display.println(line2);
  }

  display.display();
}

void applyStatus(byte code) {
  switch (code) {
    case STATUS_READY:
      showStatus("TRANSLATOR", "READY");
      break;

    case STATUS_LISTENING:
      showStatus("STATUS:", "LISTENING");
      break;

    case STATUS_PROCESSING:
      showStatus("STATUS:", "PROCESSING");
      break;

    case STATUS_SPEAKING:
      showStatus("STATUS:", "SPEAKING");
      break;

    case STATUS_DONE:
      showStatus("STATUS:", "DONE");
      break;

    case STATUS_ERROR:
      showStatus("STATUS:", "ERROR");
      break;

    case STATUS_FROM_EN:
      showStatus("FROM:", "ENGLISH");
      break;

    case STATUS_TO_HI:
      showStatus("TO:", "HINDI");
      break;

    case STATUS_FROM_HI:
      showStatus("FROM:", "HINDI");
      break;

    case STATUS_TO_EN:
      showStatus("TO:", "ENGLISH");
      break;
  }
}

// ---------- Event queue ----------

void queueEvent(byte eventCode) {
  noInterrupts();

  // Do not overwrite an event that Pi has not acknowledged.
  if (pendingEvent == EVENT_NONE) {
    pendingEvent = eventCode;
  }

  interrupts();
}

// ---------- SPI interrupt ----------

ISR(SPI_STC_vect) {
  byte received = SPDR;

  if (received == SPI_ACK) {
    pendingEvent = EVENT_NONE;
  } else if ((received >= '1' && received <= '9') ||
             received == '0') {
    requestedStatus = received;
  }

  // Return the pending event in the next SPI transfer.
  SPDR = pendingEvent;
}

// ---------- Setup ----------

void setup() {
  Serial.begin(9600);

  pinMode(FROM_BUTTON, INPUT_PULLUP);
  pinMode(TO_BUTTON, INPUT_PULLUP);
  pinMode(LISTEN_BUTTON, INPUT_PULLUP);
  pinMode(REVERSE_BUTTON, INPUT_PULLUP);

  Wire.begin();

  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDRESS)) {
    Serial.println("OLED ERROR");

    while (true) {
      delay(100);
    }
  }

  showStatus("TRANSLATOR", "READY");

  // Arduino Uno is an SPI slave.
  pinMode(MISO, OUTPUT);
  pinMode(SS, INPUT_PULLUP);

  SPCR = _BV(SPE) | _BV(SPIE);
  SPDR = EVENT_NONE;

  Serial.println("Arduino ready");
}

// ---------- Button handling ----------

void checkButtons() {
  bool f = digitalRead(FROM_BUTTON);
  bool t = digitalRead(TO_BUTTON);
  bool p = digitalRead(LISTEN_BUTTON);
  bool r = digitalRead(REVERSE_BUTTON);

  if (f == LOW && lastFrom == HIGH) {
    Serial.println("FROM pressed");
    showStatus("FROM:", "ENGLISH");
    queueEvent(EVENT_FROM);
  }

  if (t == LOW && lastTo == HIGH) {
    Serial.println("TO pressed");
    showStatus("TO:", "HINDI");
    queueEvent(EVENT_TO);
  }

  if (p == LOW && lastListen == HIGH) {
    Serial.println("LISTEN pressed");
    showStatus("STATUS:", "LISTENING");
    queueEvent(EVENT_LISTEN_PRESS);
  }

  if (p == HIGH && lastListen == LOW) {
    Serial.println("LISTEN released");
    showStatus("STATUS:", "PROCESSING");
    queueEvent(EVENT_LISTEN_RELEASE);
  }

  if (r == LOW && lastReverse == HIGH) {
    Serial.println("REVERSE pressed");
    showStatus("LANGUAGE", "REVERSED");
    queueEvent(EVENT_REVERSE);
  }

  lastFrom = f;
  lastTo = t;
  lastListen = p;
  lastReverse = r;
}

// ---------- Main loop ----------

void loop() {
  byte statusToShow = 0;

  // Safely read the status received by the SPI interrupt.
  noInterrupts();
  statusToShow = requestedStatus;
  requestedStatus = 0;
  interrupts();

  if (statusToShow != 0) {
    applyStatus(statusToShow);
  }

  checkButtons();
  delay(10);
}