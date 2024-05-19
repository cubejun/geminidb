<?php
// 동영상 프레임 캡처 및 데이터베이스 연결에 필요한 Python Flask 애플리케이션의 엔드포인트에 POST 요청을 보냅니다.
$response = file_get_contents('http://localhost:8765/capture', false, stream_context_create([
    'http' => [
        'method' => 'POST',
    ],
]));

// 요청이 성공했는지 확인하고 메시지를 출력합니다.
if ($response === false) {
    echo 'Failed to capture frame';
} else {
    echo 'Frame captured successfully';
}
?>
