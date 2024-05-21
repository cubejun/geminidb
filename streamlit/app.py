import streamlit as st
import requests
from PIL import Image
import base64
import io
import mysql.connector

# MySQL �����ͺ��̽� ���� ����
db_config = {
    'user': 'myuser',
    'password': 'mypassword',
    'host': '192.168.0.19',
    'database': 'exampledb',
}

# MySQL �����ͺ��̽����� �̹����� �����?������ ��������
def get_data_from_db():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT id, image_path, object_name, object_info, audio_path FROM captured_data")
    data = cursor.fetchall()
    conn.close()
    return data

# MySQL �����ͺ��̽����� ������ �����ϱ�
def delete_data_from_db(id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM captured_data WHERE id = %s", (id,))
    conn.commit()
    conn.close()

# �̹����� �����?������ ���ڵ� �� ǥ��
def capture_frame():
    url = "http://yourip:8765/video_feed"
    response = requests.get(url)
    if response.status_code == 204:
        return Image.open(io.BytesIO(response.content))
    else:
        st.error('Capture failed. Please try again.')
        return None

st.title("Video Streaming with Capture")

# ���� �ǵ� ǥ��
st.image("http://yourip:8765/video_feed", caption="Video Feed")

if st.button('Capture Frame'):
    response = requests.post('http://192.168.0.19:8765/capture')
    if response.status_code == 200:
        st.success('Frame captured successfully')
        st.rerun()
   

st.header("Captured Data")

data = get_data_from_db()

if data:
    for row in data:
        id, image_path, object_name, object_info, audio_path = row
        # �̹��� ���ڵ� �� ǥ��
        image = Image.open(io.BytesIO(base64.b64decode(image_path)))
        resized_image = image.resize((540, 480))
# ������ �̹����� Streamlit�� ǥ��
        caption = f"{object_name}\n\n**{object_info}**"  # object_info�� ����ü�� ǥ��caption = f"{object_name}\n\n**{object_info}**"  # object_info�� ����ü�� ǥ��
        st.image(resized_image, caption=object_name, use_column_width=True)
        st.markdown(object_info)
        # �����?���ڵ� �� �÷���
        st.audio(base64.b64decode(audio_path), format="audio/mp3", start_time=0)
        # ���� ��ư
        if st.button('Delete', key=id):
            delete_data_from_db(id)
            st.rerun()
        st.markdown("---")
else:
    st.write("No data available.")
