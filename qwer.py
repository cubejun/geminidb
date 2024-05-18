import cv2
import time
import os

# 카메라 설정
cap = cv2.VideoCapture(0)
if not os.path.exists('static'):
    os.makedirs('static')

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 프레임을 'static/current_frame.jpg'에 저장
    cv2.imwrite('static/current_frame.jpg', frame)
    time.sleep(0.1)  # 100ms마다 프레임 갱신

cap.release()
