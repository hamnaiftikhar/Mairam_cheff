from flask import Flask, render_template, request, redirect, url_for
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

app = Flask(__name__)

# Set up YouTube API credentials
CLIENT_SECRETS_FILE = 'client_secret.json'
API_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return build(API_NAME, API_VERSION, credentials=credentials)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    ingredients = request.form.get('ingredients')

    # Authenticate with YouTube API
    youtube = get_authenticated_service()

    # Search for recipes using user-provided ingredients
    search_response = youtube.search().list(
        q=ingredients + " recipe",
        part='id,snippet',
        maxResults=5
    ).execute()

    videos = []
    for item in search_response['items']:
        video_id = item['id']['videoId']
        title = item['snippet']['title']
        videos.append({'title': title, 'video_id': video_id})

    return render_template('results.html', videos=videos)

@app.route('/watch/<video_id>')
def watch(video_id):
    return redirect(f'https://www.youtube.com/watch?v={video_id}')

if __name__ == '__main__':
    app.run(debug=True)
