let player;
let device_id;
let isPlaying = false;
let currentPlayingTrack = null;

function playSong(trackUri) {
    // Ẩn nút phát nhạc của tất cả các bài hát
    document.querySelectorAll('.playlist-item').forEach(item => {
        item.classList.remove('playing');
    });

    // Kiểm tra nếu có bài hát đang phát
    if (isPlaying && currentPlayingTrack === trackUri) {
        // Nếu đang phát bài hát này, dừng nhạc
        player.pause().then(() => {
            isPlaying = false;
            currentPlayingTrack = null;
        });
    } else {
        // Nếu chưa phát bài hát này, phát bài hát
        fetch(`https://api.spotify.com/v1/me/player/play?device_id=${window.device_id}`, {
            method: 'PUT',
            body: JSON.stringify({ uris: [trackUri] }),
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer {{ access_token }}`,
            },
        }).then(response => {
            if (!response.ok) {
                console.error("Failed to play song", response);
            } else {
                console.log("Playing song:", trackUri);
                isPlaying = true;
                currentPlayingTrack = trackUri;

                // Hiển thị nút phát nhạc của bài hát đang phát
                const trackElement = document.querySelector(`img[onclick="playSong('${trackUri}')"]`).parentElement;
                trackElement.classList.add('playing');
            }
        });
    }
}
