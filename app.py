from flask import Flask, request, redirect, session, url_for, render_template, flash
from flask_cors import CORS
from spotipy import Spotify, SpotifyException
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
CORS(app)
app.secret_key = "2l321jiohasd"
app.config['SESSION_COOKIE_NAME'] = "Spotify Cookie"

# Spotify API credentials
SPOTIPY_CLIENT_ID = 'f4a7ecfcb7a949eda531a91f9d557304'
SPOTIPY_CLIENT_SECRET = '96238dbe4fb8478781f24cf49771ccb0'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:5000/callback'

sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-read-private user-library-read playlist-modify-public playlist-modify-private"
)


def get_token():
    token_info = session.get('token_info', None)

    if token_info:
        if sp_oauth.is_token_expired(token_info):
            try:
                token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
                session['token_info'] = token_info
            except SpotifyException as e:
                print(f"Token refresh failed: {e}")
                return None
        return token_info
    else:
        return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/callback')
def callback():
    code = request.args.get('code')
    try:
        token_info = sp_oauth.get_access_token(code)
        session['token_info'] = token_info
    except SpotifyException as e:
        print(f"Error getting access token: {e}")
        return redirect(url_for('login'))
    return redirect(url_for('home'))


@app.route('/home')
def home():
    token_info = get_token()

    if token_info is None:
        return redirect(url_for('login'))

    sp = Spotify(auth=token_info['access_token'])

    try:
        trending_playlists = sp.featured_playlists(limit=10)
    except SpotifyException as e:
        print(f"SpotifyException: {e}")
        return redirect(url_for('login'))

    recommendations = sp.recommendations(seed_genres=['pop', 'rock', 'hip-hop'], limit=10)

    user_info = sp.current_user()
    premium_status = user_info.get('product', 'free') == 'premium'

    return render_template('home.html',
                           trending_songs=trending_playlists['playlists']['items'],
                           recommended_songs=recommendations['tracks'],
                           premium=premium_status)


@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return render_template('search.html', results=None, error="Please enter a search query.")

    token_info = get_token()

    if token_info is None:
        return redirect(url_for('login'))

    sp = Spotify(auth=token_info['access_token'])

    try:
        results = sp.search(q=query, type='track', limit=10)
    except SpotifyException as e:
        print(f"SpotifyException: {e}")
        return render_template('search.html', results=None, error="Error during search.")

    return render_template('search.html', results=results)


@app.route('/create_playlist', methods=['GET', 'POST'])
def create_playlist():
    token_info = get_token()

    if not token_info:
        return redirect(url_for('login'))

    sp = Spotify(auth=token_info['access_token'])

    if request.method == 'POST':
        playlist_name = request.form.get('playlist_name')

        if playlist_name:
            try:
                sp.user_playlist_create(user=sp.me()['id'], name=playlist_name, public=False)
                flash('Playlist created successfully!')
            except SpotifyException as e:
                flash(f"Failed to create playlist: {e}")
            return redirect(url_for('home'))

    return render_template('create_playlist.html')


@app.route('/view_playlists')
def view_playlists():
    token_info = get_token()

    if not token_info:
        return redirect(url_for('login'))

    sp = Spotify(auth=token_info['access_token'])

    try:
        playlists = sp.current_user_playlists(limit=10)
    except SpotifyException as e:
        flash(f"Error fetching playlists: {e}")
        playlists = {'items': []}

    return render_template('view_playlists.html',)

@app.route('/logout')
def logout():
    session.pop('token_info', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
