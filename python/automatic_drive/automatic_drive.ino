// 모터 드라이버 핀 설정
const int IN1 = 2;
const int IN2 = 3;
const int IN3 = 4;
const int IN4 = 5;
const int IN5 = 6;
const int IN6 = 7;

int initial_loop_regsist = 0;

// 전진
void moveForward() {
  analogWrite(IN3,100);
  analogWrite(IN4,0);
  analogWrite(IN5,100);
  analogWrite(IN6,0);
}

// 후진
void moveBackward() {
  analogWrite(IN3,0);
  analogWrite(IN4,100);
  analogWrite(IN5,0);
  analogWrite(IN6,100);
}

void neutral(int target, int now) {
  if(target + 1 > now){
    turnLeft(65);
  }
  else if(target - 1 < now) turnRight(65);
}

// 좌회전
void turnLeft(int degree) {
  analogWrite(IN1, degree);
  analogWrite(IN2, 0);

}

// 우회전
void turnRight(int degree) {
  analogWrite(IN1, 0);
  analogWrite(IN2, degree);
}

// 정지
void stop() {
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  digitalWrite(IN5, LOW);
  digitalWrite(IN6, LOW);

}

void setup() {
  // 모터 드라이버 핀을 출력으로 설정
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(IN5, OUTPUT);
  pinMode(IN6, OUTPUT);
  Serial.begin(9600);
  initial_loop_regsist = analogRead(A0);
}

void loop() {
  int variable_resist;

  variable_resist = analogRead(A0);
  if(Serial.available()>0){
    Serial.println("working");
    char command = Serial.read();
    moveForward();
    if(command=='L'){
      //moveForward();
      turnLeft(100);
    }
    if(command=='R'){
      //moveForward();
      turnRight(100);
    }
    if(command=='N'){
      //moveForward();
      neutral(initial_loop_regsist, varaible_resist);
    }
    //if(command=='F'){
    //  moveForward();
    //}
    //if(command=='B'){
    //  moveBackward();
    //}
    if(command=='S'){
      stop();
    }
    if(command=='Q'){
      exit(0);
    }
    if(command=='W'){
      stop();
    }
  }
  delay(100);
  Serial.println(variable_resist);
}