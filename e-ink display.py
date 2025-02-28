#pip install spotipy requests pillow openmeteo_requests requests_cache pandas retry_requests
#pip install openmeteo-requests
#pip install requests-cache retry-requests numpy pandas

import time
import requests
from PIL import Image, ImageDraw, ImageFont
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

# Replace with your own credentials
SPOTIPY_CLIENT_ID = '18ae005a578848fb894aa61ced42582f'
SPOTIPY_CLIENT_SECRET = 'cc42eb9f7ef54a10a6aca0297b126b82'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'

# Weather API credentials
WEATHER_LOCATION_LAT = -33.7871
WEATHER_LOCATION_LON = 151.221
WEATHER_TIMEZONE = "Australia/Sydney"

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
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Make sure all required weather variables are listed here
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": WEATHER_LOCATION_LAT,
        "longitude": WEATHER_LOCATION_LON,
        "hourly": ["temperature_2m", "rain"],
        "daily": ["sunrise", "sunset", "uv_index_max"],
        "timezone": WEATHER_TIMEZONE
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location
    response = responses[0]
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_rain = hourly.Variables(1).ValuesAsNumpy()

    # Get the current temperature and rain
    current_temp = hourly_temperature_2m[0]
    current_rain = hourly_rain[0]

    return f"Temp: {current_temp}°C, Rain: {current_rain}mm"

def get_time():
    return time.strftime("%H:%M:%S")

def update_display():
    # Create an image with white background
    image = Image.new('1', (400, 300), 255)  # Increased size to 400x300
    draw = ImageDraw.Draw(image)
    
    # Load a larger font
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Update this path to a valid font file on your system
    font = ImageFont.truetype(font_path, 24)  # Increased font size to 24
    
    # Get data
    song = get_currently_playing()
    weather = get_weather()
    current_time = get_time()
    
    # Draw text on the image with some styling
    draw.text((20, 20), f"Now Playing:", font=font, fill=0)
    draw.text((20, 60), song, font=font, fill=0)
    draw.text((20, 120), f"Weather:", font=font, fill=0)
    draw.text((20, 160), weather, font=font, fill=0)
    draw.text((20, 220), f"Time:", font=font, fill=0)
    draw.text((20, 260), current_time, font=font, fill=0)
    
    # Display the image on the e-ink display
    # Note: Replace this with your e-ink display library's method to display the image
    # For example, if using the Waveshare e-ink display:
    # epd.display(epd.getbuffer(image))
    image.show()  # For testing purposes, display the image on the screen

if __name__ == "__main__":
    while True:
        update_display()
        time.sleep(60)  # Update every minute