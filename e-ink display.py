#pip install spotipy requests pillow

import time
import requests
from PIL import Image, ImageDraw, ImageFont
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

# Replace with your own credentials
SPOTIPY_CLIENT_ID = '18ae005a578848fb894aa61ced42582f'
SPOTIPY_CLIENT_SECRET = 'cc42eb9f7ef54a10a6aca0297b126b82'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'

# Weather API credentials
WEATHER_API_KEY = 'your_weather_api_key'
WEATHER_LOCATION = 'your_location'

# Initialize Spotify client
sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                        client_secret=SPOTIPY_CLIENT_SECRET,
                        redirect_uri=SPOTIPY_REDIRECT_URI,
                        scope="user-read-currently-playing")

token_info = sp_oauth.get_cached_token()

if not token_info:
    auth_url = sp_oauth.get_authorize_url()
    print(f"Please navigate here: {auth_url}")
    response = input("Paste the URL you were redirected to: ")
    code = sp_oauth.parse_response_code(response)
    token_info = sp_oauth.get_access_token(code)

sp = Spotify(auth=token_info['access_token'])

def get_currently_playing():
    current_track = sp.current_user_playing_track()
    if current_track is not None:
        track = current_track['item']
        artist = track['artists'][0]['name']
        song = track['name']
        return f"{artist} - {song}"
    return "No song playing"

def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={WEATHER_LOCATION}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"{weather.capitalize()}, {temp}°C"
    return "Weather data unavailable"

def get_time():
    return time.strftime("%H:%M:%S")

def update_display():
    # Create an image with white background
    image = Image.new('1', (200, 200), 255)
    draw = ImageDraw.Draw(image)
    
    # Load a font
    font = ImageFont.load_default()
    
    # Get data
    song = get_currently_playing()
    weather = get_weather()
    current_time = get_time()
    
    # Draw text on the image
    draw.text((10, 10), f"Now Playing: {song}", font=font, fill=0)
    draw.text((10, 50), f"Weather: {weather}", font=font, fill=0)
    draw.text((10, 90), f"Time: {current_time}", font=font, fill=0)
    
    # Display the image on the e-ink display
    # Note: Replace this with your e-ink display library's method to display the image
    # For example, if using the Waveshare e-ink display:
    # epd.display(epd.getbuffer(image))
    image.show()  # For testing purposes, display the image on the screen

if __name__ == "__main__":
    while True:
        update_display()
        time.sleep(60)  # Update every minute