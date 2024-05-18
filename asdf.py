import cv2
from flask import Flask, render_template, Response, request
import threading
import time
import os
import pathlib
import cv2
import base64
import textwrap
import os
import PIL.Image
import mysql.connector
from gtts import gTTS
import requests
import json
import sys
import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown
app = Flask(__name__)

# 전역 변수 설정
video_frame = None
lock = threading.Lock()

db_connection = mysql.connector.connect(
    host="localhost",
    user="plab",
    password="plab",
    database="exampledb"
)

# 커서 생성
db_cursor = db_connection.cursor()

# Or use `os.getenv('GOOGLE_API_KEY')` to fetch an environment variable.
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

def encode_image_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer)

def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

def text_to_speech(text):
    tts = gTTS(text=text, lang='ko', tld='co.kr', slow=False)
    tts.save("output.mp3")
    #os.system("mpg321 output.mp3")

# MySQL에 데이터 삽입 함수
def insert_data_to_db(image_path, object_name, object_info, audio_path):
    sql = "INSERT INTO captured_data (image_path, object_name, object_info, audio_path) VALUES (%s, %s, %s, %s)"
    val = (image_path, object_name, object_info, audio_path)
    db_cursor.execute(sql, val)
    db_connection.commit()

def encode_base64(image_path):
    """
    이미지 파일을 base64로 인코딩하는 함수

    :param image_path: 이미지 파일 경로
    :return: base64로 인코딩된 이미지 문자열
    """
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    return encoded_string
  
model = genai.GenerativeModel('gemini-pro-vision')

def capture_video():
    global video_frame, lock

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        with lock:
            video_frame = frame.copy()

    cap.release()

def encode_frame():
    global video_frame, lock

    while True:
        with lock:
            if video_frame is None:
                continue
            ret, buffer = cv2.imencode('.jpg', video_frame)
            frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(encode_frame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture', methods=['POST'])
def capture():
    global video_frame, lock

    filename = '/home/plab/Desktop/testflask/static/capture.jpg'
    with lock:
        if video_frame is not None:
            image_path = '/home/plab/Desktop/testflask/static/capture.jpg'
            audio_path = "/home/plab/Desktop/testflask/output.mp3"
            cv2.imwrite(filename, video_frame)
            print(f'{filename} 저장됨')
            img = PIL.Image.open('/home/plab/Desktop/testflask/static/capture.jpg')
            # Base64로 이미지 인코딩
            encoded_image = encode_base64(filename)
            
            response1 = model.generate_content(["사진에 찍힌 것의 이름을 알려줘", img])
            response1.resolve()
            response2 = model.generate_content(["사진에 대해 자세하게 설명해줘", img])
            response2.resolve()
            print(response1.text)
            print(response2.text)
            # print(encoded_image)

            text_to_speech(response1.text + response2.text)
            encoded_audio = encode_base64(audio_path)
            # MySQL에 데이터 삽입
            insert_data_to_db(encoded_image, response1.text, response2.text, encoded_audio)
            
    return '', 204

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    t = threading.Thread(target=capture_video)
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', port=8765)
