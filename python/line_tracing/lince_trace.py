import cv2
import numpy as np

# 관심 영역을 설정하는 함수
def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

# 주어진 이미지에 선을 그리는 함수
def draw_lines(img, lines_with_angles, color=[255, 0, 0], thickness=10):
    if lines_with_angles is None:
        return
    for line, angle in lines_with_angles:
        for x1, y1, x2, y2 in line:
            cv2.line(img, (x1, y1), (x2, y2), color, thickness)

# 흰색 차선을 필터링하는 함수
def filter_white_lines(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0, 0, 200], dtype=np.uint8)
    upper_white = np.array([255, 255, 255], dtype=np.uint8)
    white_mask = cv2.inRange(hsv, lower_white, upper_white) # 지정한 흰색의 범위 내의 픽셀만 남김
    white_result = cv2.bitwise_and(frame, frame, mask=white_mask)
    return white_result

# 이미지를 전처리하는 함수
def preprocess_image(white_result):
    gray = cv2.cvtColor(white_result, cv2.COLOR_BGR2GRAY) # 그레이스케일 변환 (에지 검출 단순화)
    kernel_size = 5
    blur_gray = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0) # 가우시안 블러 적용 (노이즈 줄임)
    return blur_gray

# 에지를 검출하는 함수
def detect_edges(blur_gray):
    low_threshold = 50
    high_threshold = 150
    edges = cv2.Canny(blur_gray, low_threshold, high_threshold)
    return edges

# 허프 변환을 사용하여 선을 검출하는 함수
def detect_lines(edges, f_angle):
    rho = 1
    theta = np.pi / 180
    threshold = 15
    min_line_length = 50
    max_line_gap = 20

    lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]), min_line_length, max_line_gap)
    filtered_lines = []

    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                slope = (x2 - x1) / (y2 - y1 + 1e-6)
                angle = np.degrees(np.arctan(slope))
                if -f_angle <= angle <= f_angle:
                    filtered_lines.append((line, angle))

    return filtered_lines

# 각도의 평균을 계산하는 함수
def calculate_average_angle(lines_with_angles):
    if not lines_with_angles:
        return 0
    angles = [angle for _, angle in lines_with_angles]
    return np.mean(angles)

# 좌우 차선의 중앙에 가상의 선을 그리는 함수
def draw_virtual_midline(img, left_lines, right_lines):
    height, width = img.shape[:2]
    y1 = height
    y2 = int(height / 2)

    def average_lines(lines):
        if len(lines) == 0:
            return None
        x1s = [line[0][0] for line, _ in lines]
        x2s = [line[0][2] for line, _ in lines]
        avg_x1 = int(sum(x1s) / len(x1s))
        avg_x2 = int(sum(x2s) / len(x2s))
        return avg_x1, avg_x2

    left_avg = average_lines(left_lines)
    right_avg = average_lines(right_lines)

    if left_avg and right_avg:
        mid_x1 = (left_avg[0] + right_avg[0]) // 2
        mid_x2 = (left_avg[1] + right_avg[1]) // 2
        cv2.line(img, (mid_x1, y1), (mid_x2, y2), (0, 255, 255), 5)

# 선 옆에 작은 원을 그리는 함수
def draw_circle_near_lines(img, lines_with_angles, color=[0, 255, 0], radius=5, thickness=2):
    if lines_with_angles is None:
        return
    for line, angle in lines_with_angles:
        for x1, y1, x2, y2 in line:
            mid_x = (x1 + x2) // 2
            mid_y = (y1 + y2) // 2
            cv2.circle(img, (mid_x, mid_y), radius, color, thickness)

# 주어진 프레임을 처리하는 함수
def process_frame(frame, color):
    white_result = filter_white_lines(frame)
    blur_gray = preprocess_image(white_result)  # 이미지 전처리
    edges = detect_edges(blur_gray)  # 에지 검출
    lines_with_angles = detect_lines(edges, 40)  # 라인 감지

    line_image = np.copy(frame) * 0
    draw_lines(line_image, lines_with_angles, color=color, thickness=10)
    # draw_circle_near_lines(line_image, lines_with_angles)  # 선 옆에 작은 원을 그리는 함수 호출

    added_img = cv2.addWeighted(frame, 0.8, line_image, 1, 0)

    height, width = frame.shape[:2]
    half_height = height // 2

    lower_lines_with_angles = [line for line in lines_with_angles if (line[0][0][1] > half_height and line[0][0][3] > half_height)]
    line_count = len(lower_lines_with_angles)
    average_angle = calculate_average_angle(lower_lines_with_angles)

    return added_img, lines_with_angles, line_count, average_angle

# 비디오 파일 열기
cap = cv2.VideoCapture('sample.mp4')

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

scale_factor = 0.5

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)

    height, width, _ = frame.shape
    mid_width = width // 2

    left_frame = frame[:, :mid_width]
    right_frame = frame[:, mid_width:]

    left_img, left_lines, left_line_count, left_avg_angle = process_frame(left_frame, color=[255, 0, 0])
    right_img, right_lines, right_line_count, right_avg_angle = process_frame(right_frame, color=[0, 0, 255])

    combined_result = np.hstack((left_img, right_img))  # 두 이미지 수평 연결하여 하나의 이미지로 결합

    # 화면 중앙에 세로선 추가
    combined_height, combined_width, _ = combined_result.shape
    center_x = combined_width // 2
    cv2.line(combined_result, (center_x, 0), (center_x, combined_height), (0, 255, 0), 2)

    # 왼쪽과 오른쪽 라인 개수 및 각도 평균을 화면에 표시
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(combined_result, f'Left lines: {left_line_count}', (50, 50), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(combined_result, f'Right lines: {right_line_count}', (center_x + 50, 50), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(combined_result, f'Left avg angle: {left_avg_angle:.2f}', (50, 100), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(combined_result, f'Right avg angle: {right_avg_angle:.2f}', (center_x + 50, 100), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow('Lane Detection', combined_result)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
