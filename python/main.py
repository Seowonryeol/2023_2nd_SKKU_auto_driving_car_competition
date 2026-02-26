import lane_detection as lane_dection
import cv2
import serial
import time
import Function_Library as fl

# 아두이노 포트 설정
arduino_port = "COM4"

# 시리얼 통신 초기화
ser = fl.libARDUINO()
comm = ser.init(arduino_port, 9600)
time.sleep(1)

def write_read(command):
    comm.write(command.encode())
    time.sleep(0.05)

def read_from_arduino():
    time.sleep(0.05)
    if comm.in_waiting > 0:
        data = comm.readline().decode('utf-8', errors='ignore').rstrip()
        return data
    return None

def main():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("웹캠을 열 수 없습니다.")
        exit()

    paused = False  # 화면 일시정지
    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                print("프레임을 읽을 수 없습니다.")
                break

            avg_left_angle, avg_right_angle = lane_dection.process_frame(frame)
            #print(avg_left_angle, avg_right_angle)
            try:
                if avg_left_angle < -30:  # 우회전의 경우
                    write_read("R")
                    print("RIGHT")
                elif avg_right_angle > 30:  # 좌회전의 경우
                    write_read("L")
                    print("LEFT")
                elif abs(avg_left_angle) < 30 and abs(avg_right_angle) < 30:  # 직진의 경우
                    write_read("N")
                    print("forward")
                elif False:  # 후진의 경우
                    write_read("B")
                elif cv2.waitKey(1) & 0xFF == ord("S"):  # 정지의 경우
                    write_read("S")
            except KeyboardInterrupt:
                write_read("S")  # 프로그램 종료 시 정지

            if cv2.waitKey(1) & 0xFF == ord("q"):
                write_read("Q")
                break
        if cv2.waitKey(1) & 0xFF == ord("p"):
            paused = not paused
        if cv2.waitKey(1) & 0xFF == ord('W'):
            write_read('W')

        # 아두이노에서 값 읽기
        arduino_data = read_from_arduino()
        if arduino_data is not None:
            print(f"Received from Arduino: {arduino_data}")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
