#define RED1 21
#define YELLOW1 19
#define GREEN1 18

#define RED2 27
#define YELLOW2 26
#define GREEN2 25

int greenDuration = 8000; // in milliseconds

void setup() {
  Serial.begin(9600);

  pinMode(RED1, OUTPUT);
  pinMode(YELLOW1, OUTPUT);
  pinMode(GREEN1, OUTPUT);
  pinMode(RED2, OUTPUT);
  pinMode(YELLOW2, OUTPUT);
  pinMode(GREEN2, OUTPUT);

  allRed(); // Initial state
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.startsWith("L1_")) {
      greenDuration = cmd.substring(3).toInt() * 1000;
      lane1Green();
      Serial.println("ACK"); // Confirm L1 done
    } 
    else if (cmd.startsWith("L2_")) {
      greenDuration = cmd.substring(3).toInt() * 1000;
      lane2Green();
      Serial.println("ACK"); // Confirm L2 done
    } 
    else if (cmd == "NO") {
      yellowBlink();
    }
  }
}

void allRed() {
  digitalWrite(RED1, HIGH);
  digitalWrite(YELLOW1, LOW);
  digitalWrite(GREEN1, LOW);

  digitalWrite(RED2, HIGH);
  digitalWrite(YELLOW2, LOW);
  digitalWrite(GREEN2, LOW);
}

void resetLEDs() {
  digitalWrite(RED1, LOW);
  digitalWrite(YELLOW1, LOW);
  digitalWrite(GREEN1, LOW);

  digitalWrite(RED2, LOW);
  digitalWrite(YELLOW2, LOW);
  digitalWrite(GREEN2, LOW);
}

void lane1Green() {
  allRed();
  digitalWrite(RED1, LOW);
  digitalWrite(GREEN1, HIGH);
  delay(greenDuration);
  digitalWrite(GREEN1, LOW);
  digitalWrite(YELLOW1, HIGH);
  delay(3000);
  digitalWrite(YELLOW1, LOW);
  digitalWrite(RED1, HIGH);
}

void lane2Green() {
  allRed();
  digitalWrite(RED2, LOW);
  digitalWrite(GREEN2, HIGH);
  delay(greenDuration);
  digitalWrite(GREEN2, LOW);
  digitalWrite(YELLOW2, HIGH);
  delay(3000);
  digitalWrite(YELLOW2, LOW);
  digitalWrite(RED2, HIGH);
}

void yellowBlink() {
  resetLEDs();
  for (int i = 0; i < 10; i++) {
    digitalWrite(YELLOW1, HIGH);
    digitalWrite(YELLOW2, HIGH);
    delay(500);
    digitalWrite(YELLOW1, LOW);
    digitalWrite(YELLOW2, LOW);
    delay(500);
    if (Serial.available()) break;
  }
}
