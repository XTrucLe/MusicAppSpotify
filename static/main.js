const token = "{{ token_info['access_token'] }}"; // Lấy token từ Flask

const player = new Spotify.Player({
    name: 'Web Playback SDK Player',
    getOAuthToken: cb => {
        cb(token); // Cung cấp token cho Spotify Player
    },
    volume: 0.5
});

// Khởi động Player
player.connect().then(success => {
    if (success) {
        console.log('The Web Playback SDK is ready!');
    } else {
        console.error('Failed to connect to the Web Playback SDK.');
    }
});

function playSong(trackId, trackName, albumCoverUrl) {
    console.log(`Playing song with ID: ${trackId}, Name: ${trackName}, Cover: ${albumCoverUrl}`); // Ghi nhận thông tin
    fetch(`https://api.spotify.com/v1/tracks/${trackId}`, {
        headers: {
            'Authorization': 'Bearer ' + token // Sử dụng token hợp lệ
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`); // Xử lý lỗi nếu có
            }
            return response.json();
        })
        .then(track => {
            if (track && track.uri) { // Kiểm tra nếu track hợp lệ
                player._options.volume = 0.5; // Đặt âm lượng
                player.queue(track.uri).then(() => {
                    player.resume(); // Bắt đầu phát nhạc
                    // Cập nhật giao diện với thông tin bài hát đang phát
                    updateNowPlaying(trackName, albumCoverUrl);
                }).catch(error => {
                    console.error('Error while queuing track:', error); // Xử lý lỗi khi thêm vào hàng đợi
                });
            } else {
                console.error('Track not found or invalid track:', track);
            }
        })
        .catch(error => {
            console.error('Fetch error:', error); // Xử lý lỗi khi gọi API
        });
}

function updateNowPlaying(trackName, albumCoverUrl, trackUrl) {
    const nowPlayingSection = document.getElementById('now-playing');
    const mediaPlayer = document.getElementById('media-player');
    const audioSource = document.getElementById('audio-source');

    // Cập nhật thông tin bài hát đang phát
    nowPlayingSection.innerHTML = `
        <h3>Đang Phát:</h3>
        <strong>${trackName}</strong>
        <img src="${albumCoverUrl}" alt="Now Playing" class="now-playing-cover">
    `;

    // Cập nhật nguồn cho audio player
    audioSource.src = trackUrl; // Đường dẫn đến audio file
    mediaPlayer.style.display = "block"; // Hiển thị media player

    // Tự động phát bài hát
    const audioPlayer = document.getElementById('audio-player');
    audioPlayer.load(); // Tải lại audio với source mới
    audioPlayer.play().catch(error => {
        console.error('Error playing audio:', error); // Xử lý lỗi khi phát audio
    });
}

