from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import webbrowser
import time
import base64
from logManager import LogManager

class Music:
    '''Spotify zenegeneralo. Inicializalasnal fontos, hogy a megadott parameterekbol mindegyikhez szerepljen megfelelo adat.'''
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, scope: list[str], logger:LogManager) -> None:
        #None-ra inicializalva az osszes belso valtozo, ami a kliensnek kellhet
        self.client= None 
        self.client_id= client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.is_authorized = False
        
        # Innentol a playlisthez szukseges inicializaciok vannak
        
        self.playlist_id = None
        self.last_timestamp = None
        
        self.logger = logger
    
    def _setClient(self, auth: SpotifyOAuth) -> None:
        '''Belso fuggveny, letrehoz egy klienst, amin keresztul mukodik az API'''
        try:
            self.client = Spotify(auth_manager=auth)
            self.is_authorized = True
        except SpotifyOAuth as e:
            self.logger.logEvent(f"(User/Connection Error) LoginError: {e}")
            self.is_authorized = False
        
    def authorizeUser(self) -> None:
        '''Beleptetes, letrehoz egy authorizert, majd ezzel egy klienst, es leellenorzi, hogy sikeres volt e.'''
        authorizer = SpotifyOAuth(client_id=self.client_id,
                            client_secret=self.client_secret,
                            redirect_uri=self.redirect_uri,
                            scope=self.scope)

        auth_url = authorizer.get_authorize_url()
        webbrowser.open(auth_url)
        self._setClient(authorizer)
    
    def _setTimestamp(self) -> None:
        '''General egy timestampet, playlistek nevehez/esetleg kesobb logolashoz'''
        self.last_timestamp = f"{time.localtime(time.time()).tm_hour}:{time.localtime(time.time()).tm_min}"
    
    def _makePlaylist(self, name: str = None, description: str = None) -> None:
        '''Belso fuggveny, letrehozza a kivant playlistet'''
        
        if name == None:
            self._setTimestamp()
            name = f"New playlist made by AI (at {self.last_timestamp})"

        if description == None:
            description = "This was made by my prompt engineering AI project. my Github page: https://github.com/krusoadi"

        playlist = self.client.user_playlist_create(self.client.current_user()["id"], name, True, False, description)
        self.playlist_id = playlist["id"]
    
    def _loadDefaultPicture(self) -> str:
        '''Belso fuggveny, ha nem kertek korabban, akkor itt tolti be az alap playlist kepet'''
        with open('picture1.jpeg', 'rb') as image_file:
            base64_bytes = base64.b64encode(image_file.read())
            base64_string = base64_bytes.decode()

        return base64_string
    
    def _setPlaylistPicture(self, base64_string: str = None) -> None: # TODO valoszinuleg gyorsabban probal neha kepet feltolteni mint a playlist letrejon
        '''Ez a belso fuggveny hasznalhato a kep feltoltesehez az uj playlistnel.'''
        if base64_string == None:
            base64_string = self._loadDefaultPicture()
    
        try:
            self.client.playlist_upload_cover_image(self.playlist_id, base64_string) # TODO Talan asyncio-val meg lehet oldani
        except:
            self.logger.logEvent("(Minor Error) Picture upload failed\n")
            
    def addSongToPlaylist(self, song_uri: str | list[str]) -> None:
        '''Zenet/zeneket tesz egy playlistbe, a song_id lehet egy id, de akar egy list is'''
        if song_uri != None:
            try:
                self.client.playlist_add_items(playlist_id=self.playlist_id, items=song_uri)
            except TypeError:
                self.logger.logEvent(f"(Major Error) TypeError (song_uri: {song_uri}) at addSongToPlaylist\n")
                
    def playlist(self, name: str = None, picture_base64: str = None, song_id: str | list[str] = None, description: str = None) -> None:
        '''Osszekoti az eddigi belso playlist fuggvenyeket, letrehoz a megadottak alapjan egy playlistet.'''
        self._makePlaylist(name, description)
        self._setPlaylistPicture(picture_base64)
        
        if song_id != None:
           self.addSongToPlaylist(song_id)
    
    def mostListenedArtist(self, time_interval: str = "long_term", top_n: int = 5) -> list[str]:
        '''Megadja a legtobbet hallgatott (top n darab) eloadokat egy idointervallumra'''
        
        top_artists = self.client.current_user_top_artists(limit=top_n, time_range=time_interval)
        most_listened = []

        for i in range(top_n):
            most_listened.append(top_artists['items'][i]['name'])
        
        return most_listened
    
    def getSongIdByName(self, parsed_gpt_response: str) -> str: # !! Empty str-t es listat hajlamos generalni, meg kell csinalni
        '''Megkapja a chatgpt egy MAR FELDOLGOZOTT query-jet aminek az elso eleme az eloado es a masodik eleme a zene cime. Visszaad egy stringet, ami tartalmazza a zene Spotify ID-jet
        \nMINDENKEPP NONE SZUREST IGENYEL AMUGY MEGBOLONDUL'''
        query = f"track:{parsed_gpt_response[0]} artist:{parsed_gpt_response[1]}"
        results = self.client.search(q=query, type='track')
        
        try:
            parsed_gpt_response = results['tracks']['items'][0]['uri']
            return parsed_gpt_response
        except IndexError:
            self.logger.logEvent(f"(Minor Error) Song not found: {parsed_gpt_response} (Song won't be in the playlist)\n")
            return None # !! Itt a baj    
        
    def getSongIdByName(self, parsed_gpt_response: list[str]) -> str:
        '''Megkapja a chatgpt egy MAR FELDOLGOZOTT query-jet aminek az elso eleme az eloado es a masodik eleme a zene cime. Visszaad egy stringet, ami tartalmazza a zene Spotify ID-jet'''
        
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

# Potencialisan optimalisabb kod, tesztelni kene
"""        parsed_gpt_response = results.get('tracks', {}).get('items', [])
        if parsed_gpt_response:
            return parsed_gpt_response[0]['id']
        else:
            return None
"""