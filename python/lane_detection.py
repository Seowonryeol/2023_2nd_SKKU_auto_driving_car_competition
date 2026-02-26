import cv2
import numpy as np

def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def draw_lines(img, lines_with_angles, color=[255, 0, 0], thickness=10):
    if lines_with_angles is None:
        return
    for line, angle in lines_with_angles:
        for x1, y1, x2, y2 in line:
            cv2.line(img, (x1, y1), (x2, y2), color, thickness)
            # 각도를 텍스트로 추가
            midpoint = (int((x1 + x2) / 2), int((y1 + y2) / 2))
            cv2.putText(
                img,
                f"{angle:.2f}",
                midpoint,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2,
            )

def filter_white_lines(frame):
    # 색상 필터링을 위한 HSV 변환
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 흰색 차선 필터링
    lower_white = np.array([0, 0, 200], dtype=np.uint8)
    upper_white = np.array([255, 255, 255], dtype=np.uint8)
    white_mask = cv2.inRange(hsv, lower_white, upper_white)
    white_result = cv2.bitwise_and(frame, frame, mask=white_mask)

    return white_result


def preprocess_image(white_result):
    # 그레이스케일 변환
    gray = cv2.cvtColor(white_result, cv2.COLOR_BGR2GRAY)

    # 가우시안 블러 적용
    kernel_size = 5
    blur_gray = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)

    return blur_gray

def detect_edges(blur_gray):
    # Canny 에지 검출
    low_threshold = 50
    high_threshold = 150
    edges = cv2.Canny(blur_gray, low_threshold, high_threshold)

    return edges

def detect_lines(edges, width):
    # 허프 변환 파라미터 설정 및 선 검출
    rho = 1  # distance resolution in pixels of the Hough grid
    theta = np.pi / 180  # angular resolution in radians of the Hough grid
    threshold = 15  # minimum number of votes (intersections in Hough grid cell)
    min_line_length = 50  # minimum number of pixels making up a line
    max_line_gap = 20  # maximum gap in pixels between connectable line segments

    lines = cv2.HoughLinesP(
        edges, rho, theta, threshold, np.array([]), min_line_length, max_line_gap
    )

    left_lines_with_angles = []
    right_lines_with_angles = []
    mid = width // 2

    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                slope = (x2 - x1) / (y2 - y1 + 1e-6)  # Avoid division by zero
                angle = np.degrees(
                    np.arctan(slope)
                )  # Convert slope to angle in degrees
                if -40 <= angle <= 40:  # Filter out lines with angle outside the range
                    if x1 < mid and x2 < mid:  # 왼쪽 영역
                        left_lines_with_angles.append((line, -angle))
                        # print("왼쪽 = ", x2, x1, y2, y1)
                    elif x1 >= mid and x2 >= mid:  # 오른쪽 영역
                        # print("오른쪽 = ", x2, x1, y2, y1)
                        right_lines_with_angles.append((line, angle))

    return left_lines_with_angles, right_lines_with_angles

def process_frame(frame):
    avg_left_angle = 0
    avg_right_angle = 0
    height, width = frame.shape[:2]

    # 흰색 차선 필터링
    white_result = filter_white_lines(frame)

    # 이미지 전처리 (그레이스케일 변환 및 가우시안 블러)
    blur_gray = preprocess_image(white_result)

    # 에지 검출
    edges = detect_edges(blur_gray)

    # 선 검출
    left_lines_with_angles, right_lines_with_angles = detect_lines(edges, width)

    # 선 그리기
    line_image = np.copy(frame) * 0  # creating a blank to draw lines on
    draw_lines(line_image, left_lines_with_angles, color=[255, 0, 0], thickness=10)
    draw_lines(line_image, right_lines_with_angles, color=[0, 255, 0], thickness=10)

    lines_edges = cv2.addWeighted(frame, 0.8, line_image, 1, 0)

    # 평균 각도 텍스트 추가
    left_angles = [angle for _, angle in left_lines_with_angles]
    right_angles = [angle for _, angle in right_lines_with_angles]
    if left_angles:
        avg_left_angle = sum(left_angles) / len(left_angles)
        cv2.putText(
            lines_edges,
            f"Left angle: {avg_left_angle:.2f}",
            (10, height - 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 0, 0),
            2,
        )
    if right_angles:
        avg_right_angle = sum(right_angles) / len(right_angles)
        cv2.putText(
            lines_edges,
            f"Right angle: {avg_right_angle:.2f}",
            (10, height - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )

    # 화면에 표시
    cv2.imshow("Lane Detection", lines_edges)
    # 반올림
    # avg_left_angle = round(avg_left_angle, 2)
    # avg_right_angle = round(avg_right_angle, 2)

    return avg_left_angle, avg_right_angle