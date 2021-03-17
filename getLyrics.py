//This code is intended to be used a reference for the project
//Referenced from Github user ravimalde
//originally found at https://towardsdatascience.com/become-a-lyrical-genius-4362e7710e43
//Full writeup in article by Ravi Malde at https://towardsdatascience.com/become-a-lyrical-genius-4362e7710e43
//Executable through the following code:
  //songs = GetLyrics(spotify_client_id, spotify_client_secret, spotify_user_id, spotify_playlist_id, genius_key)
  //song_lyrics = songs.get_lyrics()

//class designed to obtain song lyrics from Spotify playlists using the Spotify and Genius APIS and web scraping
//code inspired by Will Soares from https://dev.to/willamesoares/how-to-integrate-spotify-and-genius-api-to-easily-crawl-song-lyrics-with-python-4o62
//class requires the use of personal credentials for the Spotify and Genius APIs
//class requires Spotify user and playlist IDs
class GetLyrics():
    
    //class constructor
    //spotify_client_id and spotify_client_secret fields taken from personal Spotify developer account dashboard
    //website for Spotify development: https://developer.spotify.com/dashboard/login
    //user_id and playlist_id fields taken from personal Spotify account ((user/playlist)->share->copy Spotify URI)
    //genius_key field taken from authorization code on the main genius developers page
    //Genius developers link: https://docs.genius.com/#/getting-started-h1
    def __init__(self, spotify_client_id, spotify_client_secret, user_id, playlist_id, genius_key):
        self.spotify_client_id = spotify_client_id
        self.spotify_client_secret = spotify_client_secret
        self.user_id = user_id
        self.playlist_id = playlist_id
        self.genius_key = genius_key
     
    //method to connect to the Spotify API using Spotipy
    //returns a JSON object containing information about the requested Spotify playlist 
    def get_playlist_info(self):
        token = SpotifyClientCredentials(client_id=self.spotify_client_id, client_secret=self.spotify_client_secret).get_access_token()
        sp = spotipy.Spotify(token)
        playlist = sp.user_playlist_tracks(self.user_id, self.playlist_id)
        self.playlist = playlist
        return self.playlist
    
    //method to find the name of each song in the playlist
    //stores and returns song names in a list to be used later
    def get_track_names(self):
        track_names = []
        for song in range(len(self.playlist['items'])):
            track_names.append(self.playlist['items'][song]['track']['name'])
        self.track_names = track_names
        return self.track_names
    
    //method to find the artist of each song in the playlist
    //stores and returns artists in a list to be used later
    def get_track_artists(self):
        track_artists = []
        for song in range(len(self.playlist['items'])):
            track_artists.append(self.playlist['items'][song]['track']['artists'][0]['name'])
        self.track_artists = track_artists
        return self.track_artists
       
    //method using the Request library to connect with the Genius API (uses auth key)
    //checks if there are any matches in the API to the track name & artist
    //returns an object containing information relating to matches
    def request_song_info(self, track_name, track_artist):
        self.track_name = track_name
        self.track_artist = track_artist
        base_url = 'https://api.genius.com'
        headers = {'Authorization': 'Bearer ' + self.genius_key}
        search_url = base_url + '/search'
        data = {'q': track_name + ' ' + track_artist}
        response = requests.get(search_url, data=data, headers=headers)
        self.response = response
        return self.response

    //method to decode the JSON obect from a previous method
    //checks which hits are exact matches with artist names
    //if match is found, information on the track is stored in the remote_song_info object
    def check_hits(self):
        json = self.response.json()
        remote_song_info = None
        for hit in json['response']['hits']:
            if self.track_artist.lower() in hit['result']['primary_artist']['name'].lower():
                remote_song_info = hit
                break
        self.remote_song_info = remote_song_info
        return self.remote_song_info
    
    //parse the remote_song_info object to find each song's URL
    def get_url(self):
        song_url = self.remote_song_info['result']['url']
        self.song_url = song_url
        return self.song_url
    
    //method using the Requests library to make a request to the song URL from previous method
    //use of BeutifulSoup to parse HTML (.find() called twice to account for webpage inconsistencies))
    //None case means a 404 error
    def scrape_lyrics(self):
        page = requests.get(self.song_url)
        html = BeautifulSoup(page.text, 'html.parser')
        lyrics1 = html.find("div", class_="lyrics")
        lyrics2 = html.find("div", class_="Lyrics__Container-sc-1ynbvzw-2 jgQsqn")
        if lyrics1:
            lyrics = lyrics1.get_text()
        elif lyrics2:
            lyrics = lyrics2.get_text()
        elif lyrics1 == lyrics2 == None:
            lyrics = None
        return lyrics

    //method utilizing all previous methods to get lyrics simply
    //includes print statements to track program progress
    def get_lyrics(self):
        playlist = GetLyrics.get_playlist_info(self)
        track_names = GetLyrics.get_track_names(self)
        track_artists = GetLyrics.get_track_artists(self)
        song_lyrics = []
        for i in range(len(self.track_names)):
            print("\n")
            print(f"Working on track {i}.")
            response = GetLyrics.request_song_info(self, self.track_names[i], self.track_artists[i])
            remote_song_info = GetLyrics.check_hits(self)
            if remote_song_info == None:
                lyrics = None
                print(f"Track {i} is not in the Genius database.")
            else:
                url = GetLyrics.get_url(self)
                lyrics = GetLyrics.scrape_lyrics(self)
                if lyrics == None:
                    print(f"Track {i} is not in the Genius database.")
                else:
                    print(f"Retrieved track {i} lyrics!")
            song_lyrics.append(lyrics)
        return song_lyrics
