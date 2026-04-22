const int SLOT_COUNT = 3;

const int STEP_PINS[SLOT_COUNT] = {2, -1, -1};
const int DIR_PINS[SLOT_COUNT]  = {3, -1, -1};
const int EN_PINS[SLOT_COUNT]   = {4, -1, -1};

const bool SLOT_ENABLED[SLOT_COUNT] = {true, false, false};

// Für den ersten echten Motor-Test:
// Diese Zahl bestimmt, wie weit der Motor pro "1 Ausgabe" dreht.
// Später wird dieser Wert pro Fach kalibriert.
// Für jetzt ist es bewusst nur eine Test-Basis.
const int STEPS_PER_DISPENSE_UNIT[SLOT_COUNT] = {200, 200, 200};

const unsigned int STEP_PULSE_HIGH_US = 800;
const unsigned int STEP_PULSE_LOW_US = 800;

String inputLine;

void handleCommand(const String& line);
void handleDispenseCommand(const String& line);
bool performDispense(int slotIndex, int count);
void enableDriver(int slotIndex, bool enabled);
void rotateOneDispenseUnit(int slotIndex);

void setup() {
  Serial.begin(115200);

  for (int i = 0; i < SLOT_COUNT; i++) {
    if (!SLOT_ENABLED[i]) {
      continue;
    }

    digitalWrite(EN_PINS[i], HIGH);
    pinMode(EN_PINS[i], OUTPUT);

    pinMode(STEP_PINS[i], OUTPUT);
    pinMode(DIR_PINS[i], OUTPUT);

    digitalWrite(STEP_PINS[i], LOW);
    digitalWrite(DIR_PINS[i], LOW);
  }
}


void loop() {
  while (Serial.available() > 0) {
    char c = (char)Serial.read();

    if (c == '\n') {
      inputLine.trim();

      if (inputLine.length() > 0) {
        handleCommand(inputLine);
      }

      inputLine = "";
    } else if (c != '\r') {
      inputLine += c;
    }
  }
}

void handleCommand(const String& line) {
  if (line == "PING") {
    Serial.println("OK PONG");
    return;
  }

  if (line.startsWith("DISPENSE ")) {
    handleDispenseCommand(line);
    return;
  }

  Serial.println("ERR UNKNOWN_COMMAND");
}

void handleDispenseCommand(const String& line) {
  int firstSpace = line.indexOf(' ');
  int secondSpace = line.indexOf(' ', firstSpace + 1);

  if (firstSpace < 0 || secondSpace < 0) {
    Serial.println("ERR INVALID_FORMAT");
    return;
  }

  String slotStr = line.substring(firstSpace + 1, secondSpace);
  String countStr = line.substring(secondSpace + 1);

  int slot = slotStr.toInt();
  int count = countStr.toInt();

  if (slot < 1 || slot > SLOT_COUNT) {
    Serial.println("ERR INVALID_SLOT");
    return;
  }

  if (count < 1) {
    Serial.println("ERR INVALID_COUNT");
    return;
  }

  int slotIndex = slot - 1;

  if (!SLOT_ENABLED[slotIndex]) {
    Serial.println("ERR SLOT_NOT_ENABLED");
    return;
  }

  bool success = performDispense(slotIndex, count);

  if (!success) {
    Serial.println("ERR DISPENSE_FAILED");
    return;
  }

  Serial.print("OK DISPENSE ");
  Serial.print(slot);
  Serial.print(" ");
  Serial.println(count);
}

bool performDispense(int slotIndex, int count) {
  enableDriver(slotIndex, true);

  for (int i = 0; i < count; i++) {
    rotateOneDispenseUnit(slotIndex);
  }

  enableDriver(slotIndex, false);
  return true;
}

void enableDriver(int slotIndex, bool enabled) {
  digitalWrite(EN_PINS[slotIndex], enabled ? LOW : HIGH);
}

void rotateOneDispenseUnit(int slotIndex) {
  digitalWrite(DIR_PINS[slotIndex], LOW);

  int steps = STEPS_PER_DISPENSE_UNIT[slotIndex];

  for (int i = 0; i < steps; i++) {
    digitalWrite(STEP_PINS[slotIndex], HIGH);
    delayMicroseconds(STEP_PULSE_HIGH_US);

    digitalWrite(STEP_PINS[slotIndex], LOW);
    delayMicroseconds(STEP_PULSE_LOW_US);
  }
}