<!DOCTYPE html>
<html>
<head>
    <title>Video Streaming with Capture</title>
    <script>
        function captureFrame() {
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "capture.php", true);
            xhr.onload = function () {
                if (xhr.status === 200) {
                    // 요청이 성공하면 이미지를 다시 불러옵니다.
                    document.getElementById("video_feed").src = "http://yourip:8765/video_feed";
                    // 새로운 데이터를 표시하기 위해 페이지를 새로고침합니다.
                    location.reload();
                } else {
                    alert('Capture failed. Please try again.');
                }
            };
            xhr.send();
        }

        function deleteData(id) {
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "delete.php", true);
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            xhr.onload = function () {
                if (xhr.status === 200) {
                    // 요청이 성공하면 페이지를 새로고침합니다.
                    location.reload();
                } else {
                    alert('Delete failed. Please try again.');
                }
            };
            xhr.send("id=" + id);
        }
    </script>
</head>
<body>
    <h1>Video Streaming with Capture</h1>
    <img id="video_feed" src="http://yourip:8765/video_feed" alt="Video Feed">
    <br>
    <button onclick="captureFrame()">Capture Frame</button>

    <h2>Captured Data</h2>
    <table border="1">
        <tr>
            <th>Image</th>
            <th>Object Name</th>
            <th>Object Info</th>
            <th>Audio</th>
            <th>Delete</th>
        </tr>
        <?php
            // 데이터베이스 연결 설정
            $servername = "localhost";
            $username = "plab";
            $password = "plab";
            $dbname = "exampledb";
            $conn = new mysqli($servername, $username, $password, $dbname);
            // 연결 확인
            if ($conn->connect_error) {
                die("Connection failed: " . $conn->connect_error);
            }
            // 데이터베이스에서 데이터 가져오기
            $sql = "SELECT id, image_path, object_name, object_info, audio_path FROM captured_data";
            $result = $conn->query($sql);
            if ($result->num_rows > 0) {
                // 결과 출력
                while($row = $result->fetch_assoc()) {
                    echo "<tr>";
                    // 이미지 출력
                    echo "<td><img src='data:image/jpeg;base64,".$row["image_path"]."' width='540' height='480'/></td>";
                    // 객체 이름 출력
                    echo "<td>" . $row['object_name'] . "</td>";
                    // 객체 정보 출력
                    echo "<td>" . $row['object_info'] . "</td>";
                    // 오디오 재생 링크 출력
                    echo "<td><audio controls>";
                    echo "<source src='data:audio/mpeg;base64,".$row["audio_path"]."' type='audio/mpeg'>";
                    echo "Your browser does not support the audio element.";
                    echo "</audio></td>";
                    // 삭제 버튼 추가
                    echo "<td><button onclick='deleteData(" . $row['id'] . ")'>Delete</button></td>";
                    echo "</tr>";
                }
            } else {
                echo "0 results";
            }
            $conn->close();
        ?>
    </table>
</body>
</html>
