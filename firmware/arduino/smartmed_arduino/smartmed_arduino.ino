const int SLOT_COUNT = 3;

// Pin-Belegung: Fach 1 ist die an echter Hardware getestete Verdrahtung
// (Motor 1). Fach 2/3 sind danach analog weiterverdrahtet - falls die
// tatsächliche Verkabelung von Fach 2/3 davon abweicht, hier anpassen.
const int STEP_PINS[SLOT_COUNT] = {3, 9, 12};
const int DIR_PINS[SLOT_COUNT]  = {2, 8, 11};
const int EN_PINS[SLOT_COUNT]   = {4, 10, 13};

const bool SLOT_ENABLED[SLOT_COUNT] = {true, true, true};

// DRV8825-Mikroschritt-Auswahlpins (M0/M1/M2). Alle drei Treiber sind auf
// dieselbe Mikroschrittauflösung eingestellt und teilen sich daher dieselben
// drei Pins, statt separate M0/M1/M2 pro Motor zu belegen.
const int M0_PIN = 7;
const int M1_PIN = 6;
const int M2_PIN = 5;

// Diese Zahl bestimmt, wie weit der Motor pro "1 Ausgabe"-Einheit dreht.
// Kalibrierung pro Fach hier eintragen.
//
// WICHTIG: Das ist die EINZIGE Stelle, die festlegt, wie viele Schritte
// (= wie viel Grad) eine Ausgabe-Einheit physisch dreht. Die Raspberry-Pi-
// Software (Python) kennt diese Werte nicht und rät sie auch nicht - sie
// schickt für einen Plan-Eintrag nur "DISPENSE <Fach> <Anzahl>" (Anzahl =
// die im Einnahmeplan konfigurierte Stückzahl). Wird hier ein Wert für ein
// Fach angepasst/neu kalibriert, wirkt sich das automatisch korrekt auf
// jede künftige Ausgabe dieses Fachs aus, ohne dass am Python-Code etwas
// geändert werden muss.
//
// 1600 = an Motor 1 getesteter Wert für 90° bei 1/32-Mikroschritt.
const int STEPS_PER_DISPENSE_UNIT[SLOT_COUNT] = {1600, 1600, 1600};

const unsigned int STEP_PULSE_HIGH_US = 1000;
const unsigned int STEP_PULSE_LOW_US = 1000;

// Kurze Pause zwischen Treiber-Aktivierung und erstem Schritt-Impuls, damit
// der DRV8825 sicher aufgewacht ist (an Motor 1 mit 5ms getestet).
const unsigned int DRIVER_WAKEUP_MS = 5;

String inputLine;

void handleCommand(const String& line);
void handleDispenseCommand(const String& line);
bool performDispense(int slotIndex, int count);
void enableDriver(int slotIndex, bool enabled);
void rotateOneDispenseUnit(int slotIndex);

void setup() {
  Serial.begin(115200);

  pinMode(M0_PIN, OUTPUT);
  pinMode(M1_PIN, OUTPUT);
  pinMode(M2_PIN, OUTPUT);

  // 1/32 Mikroschritt beim DRV8825: M0 = HIGH, M1 = LOW, M2 = HIGH
  digitalWrite(M0_PIN, HIGH);
  digitalWrite(M1_PIN, LOW);
  digitalWrite(M2_PIN, HIGH);

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
  delay(DRIVER_WAKEUP_MS);

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
  digitalWrite(DIR_PINS[slotIndex], HIGH);

  int steps = STEPS_PER_DISPENSE_UNIT[slotIndex];

  for (int i = 0; i < steps; i++) {
    digitalWrite(STEP_PINS[slotIndex], HIGH);
    delayMicroseconds(STEP_PULSE_HIGH_US);

    digitalWrite(STEP_PINS[slotIndex], LOW);
    delayMicroseconds(STEP_PULSE_LOW_US);
  }
}