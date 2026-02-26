// 모터 드라이버 핀 설정
const int IN1 = 2;
const int IN2 = 3;
const int IN3 = 4;
const int IN4 = 5;
const int IN5 = 6;
const int IN6 = 7;



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

// 좌회전
void turnLeft(int degree) {
  digitalWrite(IN1, degree);
  digitalWrite(IN2, 0);

}

// 우회전
void turnRight() {
  digitalWrite(IN1, 0);
  digitalWrite(IN2, 100);
 
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


}

void loop() {
  if(Serial.available()>0){
    Serial.println("working");
    char command = Serial.read();
    if(command=='L'){
      turnLeft();
    }
    if(command=='R'){
      turnRight();
    }
    if(command=='F'){
      moveForward();
    
    }
    if(command=='B'){
      moveBackward();
    }
    if(command=='S'){
      stop();
    }
    if(command=='Q'){
      exit(0);
    }
    if(command='W'){
      stop();
    }
  }
  delay(100);

}
