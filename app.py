import json

from flask import Flask, request, redirect, session, url_for, render_template, jsonify
from flask_cors import CORS
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
CORS(app)
app.secret_key = "2l321jiohasd"
app.config['SESSION_COOKIE_NAME'] = "Spotify Cookie"

# Thông tin Client ID, Client Secret, và Redirect URI
SPOTIPY_CLIENT_ID = 'f4a7ecfcb7a949eda531a91f9d557304'
SPOTIPY_CLIENT_SECRET = '96238dbe4fb8478781f24cf49771ccb0'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:5000/callback'

sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,
                        redirect_uri=SPOTIPY_REDIRECT_URI)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/callback')
def callback():
    # Lấy mã xác thực từ Spotify
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)

    # Lưu trữ token vào session
    session['token_info'] = token_info
    return redirect(url_for('home'))


@app.route('/home')
def home():
    token_info = session.get('token_info', None)

    if token_info is None:
        return redirect(url_for('login'))

    sp = Spotify(auth=token_info['access_token'])
    access_token = token_info['access_token']

    # Lấy danh sách thịnh hành (trending) - từ mục các bài hát nổi bật
    trending_playlists = sp.featured_playlists(limit=10)

    # Lấy danh sách đề xuất (recommendations) dựa trên các sở thích của người dùng
    recommendations = sp.recommendations(seed_genres=['pop', 'rock', 'hip-hop'], limit=10)

    # Gửi dữ liệu đến template
    return render_template(
        'home.html',
        token_info=token_info,
        trending_songs=trending_playlists['playlists']['items'],
        recommended_songs=recommendations['tracks'],
        access_token=access_token
    )


@app.route('/search')
def search():
    query = request.args.get('query')  # Lấy truy vấn từ URL
    results = None
    if query:
        token_info = sp_oauth.get_access_token()
        sp = Spotify(auth=token_info['access_token'])
        results = sp.search(q=query, type='track', limit=10)
    return render_template('search.html', results=results)


@app.route('/create')
def create_playlist():
    token_info = session.get('token_info', None)

    if token_info is None:
        return redirect(url_for('login'))

    sp = Spotify(auth=token_info['access_token'])

    if request.method == 'POST':
        playlist_name = request.form['playlist_name']
        sp.user_playlist_create(user=sp.me()['id'], name=playlist_name, public=False)
        return redirect(url_for('home'))

    return render_template('create_playlist.html')


@app.route('/get_token', methods=['GET'])
def get_token():
    # Đọc token từ file .cache
    try:
        with open('.cache', 'r') as cache_file:
            token_info = json.load(cache_file)
            token = token_info.get('access_token', None)
            return jsonify({'token': token})
    except FileNotFoundError:
        return jsonify({'error': 'Cache file not found'}), 404
    except json.JSONDecodeError:
        return jsonify({'error': 'Error decoding JSON from cache'}), 500


if __name__ == '__main__':
    app.run(debug=True)
