from spotipy import Spotify
from spotipy.oauth2 import *
import webbrowser
import time
import base64
from logManager import LogManager
from time import sleep
import os

class Music:
    '''Spotify Music platform. at intialization it needs a client_id, client_secret, redirect_uri, scope and a logger.'''
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, scope: list[str], logger:LogManager) -> None:
        
        #? Client variables
        self.client = None 
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
        self.client = Spotify(auth_manager=auth)
            
    def authorizeUser(self) -> None:
        '''This method opens a webbrowser, and authorizes the user to use the Spotify API. It also sets the client, with the new user.'''
        
        authorizer = SpotifyOAuth(client_id=self.client_id,
                            client_secret=self.client_secret,
                            redirect_uri=self.redirect_uri,
                            scope=self.scope)


        auth_url = authorizer.get_authorize_url()
        webbrowser.open(auth_url)
        
                
        self._setClient(authorizer)
        try:
            self.getUserName() 
        except Exception as e:
            self.logger.logEvent(f"(Connection Error) {e}\n")
            self.is_authorized = False
            return
        
        self.is_authorized = True
        os.remove(authorizer.cache_handler.cache_path)
            
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
            description = "This was made by my prompt engineering AI project. My Github page: https://github.com/krusoadi"

        playlist = self.client.user_playlist_create(self.client.current_user()["id"], name, True, False, description)
        self.playlist_id = playlist["id"]
    
    def _loadCustomPlaylistPicture(self, path: str) -> str:
        '''Private method, loads the picture from the given path, and returns it in base64 format.'''
        
        try:
            with open(path, 'rb') as image_file: #? Reading in the image file in base 64
                base64_bytes = base64.b64encode(image_file.read())
                base64_string = base64_bytes.decode()
            time.sleep(5) #? It needs a little time to load the picture.
            return base64_string
        except FileNotFoundError:
            self.logger.logEvent(f"(Minor Error) Picture not found at: {path}\n")
            return self._loadDefaultPicture()
        
    def _loadDefaultPicture(self) -> str:
        '''Private method, loads the default picture for the playlist.'''
        
        with open('icons\picture1.jpeg', 'rb') as image_file: #? Reading in the image file in base 64
            base64_bytes = base64.b64encode(image_file.read())
            base64_string = base64_bytes.decode()

        time.sleep(5) #? It needs a little time to load the picture.

        return base64_string
    
    def _setPlaylistPicture(self, path: str = None) -> None:
        '''Private method, sets the picture of the playlist to the given base64 string. If no string is given, it will use the default picture.'''
        
        if path == None:
            base64_string = self._loadDefaultPicture()
        else:
            base64_string = self._loadCustomPlaylistPicture(path)
            
        #? Error Handling
        
        try:
            self.client.playlist_upload_cover_image(self.playlist_id, base64_string) #? Uploading the picture to the playlist
        except Exception as e:
            self.logger.logEvent(f"(Minor Error) Picture upload failed (Ex.: {e})\n")
            
    def addSongToPlaylist(self, song_uri: str | list[str]) -> None:
        '''Adds a song to the playlist. If the song_uri is a list, it will add all the songs in the list. If the song_uri is a string, it will add the song with the given uri.'''
        #? The song_uri can be a string or a list of strings, it's the spotifys own id for the song.
        if song_uri != None:
            try:
                self.client.playlist_add_items(playlist_id=self.playlist_id, items=song_uri)
            except TypeError:
                self.logger.logEvent(f"(Major Error) TypeError (song_uri: {song_uri}) at addSongToPlaylist\n")
                
    def playlist(self, name: str = None, picture_path: str = None, song_id: str | list[str] = None, description: str = None) -> None:
        '''This method creates a playlist with the given name, description and picture. If no name is given, it will be named "New playlist made by AI (at {current_time})" and if no description is given, it will be "This was made by my prompt engineering AI project. my Github page:'''
        
        self._makePlaylist(name, description)
        
        if song_id != None:
           self.addSongToPlaylist(song_id)
           
        self._setPlaylistPicture(picture_path)
    
    def mostListenedArtist(self, time_interval: str = "long_term", top_n: int = 8) -> list[str]:
        '''Returns the top n most listened artists in the given time interval. The default time interval is "long_term" and the default n is 8. The time interval can be "short_term", "medium_term" or "long_term" and the n can be any positive integer.'''
        
        top_artists = self.client.current_user_top_artists(limit=top_n, time_range=time_interval)
        most_listened = []

        for i in range(top_n):
            most_listened.append(top_artists['items'][i]['name'])
        
        return most_listened
    
    def getSongIdByName(self, parsed_gpt_response: list[str]) -> str: #TODO torolni
        '''Gets a list of two strings, the first one is the artist and the second one is the song. Returns a string, which contains the song's Spotify ID.'''
        
        query = f"track:{parsed_gpt_response[0]} artist:{parsed_gpt_response[1]}" #? Spotify search query syntax
        results = self.client.search(q=query, type='track')
        
        try:
            parsed_gpt_response = results['tracks']['items'][0]['uri']
            return parsed_gpt_response
        except IndexError: #? IndexError happens when we couldn't find the song, because it returns and empty list.
            self.logger.logEvent(f"(Minor Error) Song not found: {parsed_gpt_response} (Song won't be in the playlist)\n")
            return None  
        
    def getSongIdByName(self, parsed_gpt_response: list[list[str]]) -> str:
        '''Gets a list of two strings, the first one is the artist and the second one is the song. Returns a string, which contains the song's Spotify ID.'''
        
        local_parsed_response = parsed_gpt_response.copy() #? copying is essential, because the loop changes the elements of the list.
        
        for i, element in enumerate(local_parsed_response):
            query = f"track:{element[0]} artist:{element[1]}"
            results = self.client.search(q=query, type='track')
            
            try:
                local_parsed_response[i] = results['tracks']['items'][0]['uri']
            except IndexError:
                self.logger.logEvent(f"(Minor Error) Song not found: {local_parsed_response[i]} (Song won't be in the playlist)\n")
                pass
        
        for i, element in enumerate(local_parsed_response):
            if type(element) is not str:
                local_parsed_response.remove(element)
        
        return local_parsed_response #? Returning the list of song ids.