from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import webbrowser
import time
import base64
from logManager import LogManager

class Music:
    '''Spotify Music platform. at intialization it needs a client_id, client_secret, redirect_uri, scope and a logger.'''
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, scope: list[str], logger:LogManager) -> None:
        #? Client variables
        self.client= None 
        self.client_id= client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.is_authorized = False
        
        #? Playlist variables
        
        self.playlist_id = None
        self.last_timestamp = None
        
        #? Logger
        
        self.logger = logger
    
    def _setClient(self, auth: SpotifyOAuth) -> None:
        '''Private method to create a client with the given authorizer, and to check if it was successful.'''
        try:
            self.client = Spotify(auth_manager=auth)
            self.is_authorized = True
        except SpotifyOAuth as e:
            self.logger.logEvent(f"(User/Connection Error) LoginError: {e}")
            self.is_authorized = False
        
    def authorizeUser(self) -> None:
        '''This method opens a webbrowser, and authorizes the user to use the Spotify API. It also sets the client, with the new user.'''
        authorizer = SpotifyOAuth(client_id=self.client_id,
                            client_secret=self.client_secret,
                            redirect_uri=self.redirect_uri,
                            scope=self.scope)

        auth_url = authorizer.get_authorize_url()
        webbrowser.open(auth_url)
        self._setClient(authorizer)
    def getUserName(self) -> str:
        """This method returns the current users name."""
        return self.client.me()["display_name"]
        
    def _setTimestamp(self) -> None:
        '''Private method, sets the last timestamp to the current time.'''
        self.last_timestamp = f"{time.localtime(time.time()).tm_hour}:{time.localtime(time.time()).tm_min}"
    
    def _makePlaylist(self, name: str = None, description: str = None) -> None:
        '''Private method, creates a playlist with the given name and description. If no name is given, it will be named "New playlist made by AI (at {current_time})" and if no description is given, it will be "This was made by my prompt engineering AI project. my Github page:'''
        
        if name == None:
            self._setTimestamp()
            name = f"New playlist made by AI (at {self.last_timestamp})"

        if description == None:
            description = "This was made by my prompt engineering AI project. my Github page: https://github.com/krusoadi"

        playlist = self.client.user_playlist_create(self.client.current_user()["id"], name, True, False, description)
        self.playlist_id = playlist["id"]
    
    def _loadCustomPlaylistPicture(self, path: str) -> str:
        '''Private method, loads the picture from the given path, and returns it in base64 format.'''
        with open(path, 'rb') as image_file:
            base64_bytes = base64.b64encode(image_file.read())
            base64_string = base64_bytes.decode()
        
        return base64_string
    
    def _loadDefaultPicture(self) -> str:
        '''Private method, loads the default picture for the playlist.'''
        with open('picture1.jpeg', 'rb') as image_file:
            base64_bytes = base64.b64encode(image_file.read())
            base64_string = base64_bytes.decode()

        return base64_string
    
    def _setPlaylistPicture(self, path: str = None) -> None: # TODO valoszinuleg gyorsabban probal neha kepet feltolteni mint a playlist letrejon
        '''Private method, sets the picture of the playlist to the given base64 string. If no string is given, it will use the default picture.'''
        if path == None:
            base64_string = self._loadDefaultPicture()
        else:
            base64_string = self._loadCustomPlaylistPicture(path)
            
        #? Error Handling
        
        try:
            self.client.playlist_upload_cover_image(self.playlist_id, base64_string) # TODO Talan asyncio-val meg lehet oldani
        except:
            self.logger.logEvent("(Minor Error) Picture upload failed\n")
            
    def addSongToPlaylist(self, song_uri: str | list[str]) -> None:
        '''Adds a song to the playlist. If the song_uri is a list, it will add all the songs in the list. If the song_uri is a string, it will add the song with the given uri.'''
        if song_uri != None:
            try:
                self.client.playlist_add_items(playlist_id=self.playlist_id, items=song_uri)
            except TypeError:
                self.logger.logEvent(f"(Major Error) TypeError (song_uri: {song_uri}) at addSongToPlaylist\n")
                
    def playlist(self, name: str = None, picture_path: str = None, song_id: str | list[str] = None, description: str = None) -> None:
        '''This method creates a playlist with the given name, description and picture. If no name is given, it will be named "New playlist made by AI (at {current_time})" and if no description is given, it will be "This was made by my prompt engineering AI project. my Github page:'''
        self._makePlaylist(name, description)
        self._setPlaylistPicture(picture_path)
        
        if song_id != None:
           self.addSongToPlaylist(song_id)
    
    def mostListenedArtist(self, time_interval: str = "long_term", top_n: int = 5) -> list[str]:
        '''Returns the top n most listened artists in the given time interval. The default time interval is "long_term" and the default n is 5. The time interval can be "short_term", "medium_term" or "long_term" and the n can be any positive integer.'''
        
        top_artists = self.client.current_user_top_artists(limit=top_n, time_range=time_interval)
        most_listened = []

        for i in range(top_n):
            most_listened.append(top_artists['items'][i]['name'])
        
        return most_listened
    
    def getSongIdByName(self, parsed_gpt_response: list[str]) -> str: # !! Still missing the error handling and have bugs maybe it should be deleted
        '''Gets a list of two strings, the first one is the artist and the second one is the song. Returns a string, which contains the song's Spotify ID.'''
        query = f"track:{parsed_gpt_response[0]} artist:{parsed_gpt_response[1]}"
        results = self.client.search(q=query, type='track')
        
        try:
            parsed_gpt_response = results['tracks']['items'][0]['uri']
            return parsed_gpt_response
        except IndexError:
            self.logger.logEvent(f"(Minor Error) Song not found: {parsed_gpt_response} (Song won't be in the playlist)\n")
            return None # !! This is the problem, it should return a string, but it returns None   
        
    def getSongIdByName(self, parsed_gpt_response: list[list[str]]) -> str:
        '''Gets a list of two strings, the first one is the artist and the second one is the song. Returns a string, which contains the song's Spotify ID.'''
        
        for i, element in enumerate(parsed_gpt_response):
            query = f"track:{element[0]} artist:{element[1]}"
            results = self.client.search(q=query, type='track')
            
            try:
                parsed_gpt_response[i] = results['tracks']['items'][0]['uri']
            except IndexError: # !! Ilyen mintajura kell a stringes getSongIdByName-t (egy zeneset)
                self.logger.logEvent(f"(Minor Error) Song not found: {parsed_gpt_response[i]} (Song won't be in the playlist)\n")
                pass
        
        for i, element in enumerate(parsed_gpt_response):
            if type(element) is not str:
                parsed_gpt_response.remove(element)
        
        return parsed_gpt_response    

# TODO potentially better code for the getSongIdByName method needs to be tested and implemented
"""        parsed_gpt_response = results.get('tracks', {}).get('items', [])
        if parsed_gpt_response:
            return parsed_gpt_response[0]['id']
        else:
            return None
"""