from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import json
import os


class GeniusApi():
    def __init__(self, access_token, song, artist):
        self.token = access_token
        self.song = song
        self.artist = artist

    def search(self, page_limit):
        url = "http://api.genius.com/search"
        headers = {'Authorization': "Bearer " + self.token}
        data = {'q': self.song, 'per_page': page_limit}
        response = requests.get(url, headers=headers, params=data)
        if response.status_code == 200:
            data = response.json()
            # with open('api-data.json', 'w+') as f:
            #    json.dump(data, f, indent=2, sort_keys=True)
            #f = open('api-data.json', 'r')
            #api_data = f.read()
            #data = json.loads(api_data)
            try:
                for hit in data["response"]["hits"]:
                    if hit["result"]["primary_artist"]["name"] == self.artist:
                        song_info = hit
                        break
                if song_info:
                    song_api_path = song_info["result"]["api_path"]
                    return song_api_path
            except Exception:
                return None
        else:
            print("Request Failed!")
            # print(response.text)
            return None

    def get_lyrics(self, song_param):
        base_url = "http://api.genius.com"
        song_url = base_url + song_param
        headers = {'Authorization': "Bearer " + self.token}
        response = requests.get(song_url, headers=headers)
        json = response.json()
        path = json["response"]["song"]["path"]
        page_url = "http://genius.com" + path
        page = requests.get(page_url)
        soup = BeautifulSoup(page.text, "html.parser")
        # Removing annotation script tags
        [h.extract() for h in soup('script')]
        # Searching the css class lyrics
        lyrics = soup.find('div', class_='lyrics').get_text()
        return lyrics


if __name__ == "__main__":
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(env_file)
    # Requires access token from genius
    token = os.environ.get('GENIUS_TOKEN')
    music_name = 'Wanna Know'
    music_artist = 'Dave'
    g = GeniusApi(token, music_name, music_artist)
    song_param = g.search(10)
    if song_param is not None:
        lyrics = g.get_lyrics(song_param)
        if lyrics:
            with open(music_name + " Lyrics.txt", 'w+') as f:
                f.write(lyrics.rstrip().strip())
    else:
        print(f"Lyrics for {music_name} by {music_artist} not found!")
