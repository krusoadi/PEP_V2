import tkinter as tk
from music import Music
from chatbot import ChatBot
import apis
from logManager import LogManager

# TODO Making full user interface and commenting the code

logger = LogManager()
spoti = Music(apis.CLIENT_ID, apis.CLIENT_SECRET, apis.REDIRECT_URI, apis.SCOPE, logger=logger)
gpt = ChatBot(apis.OPENAI_API)

class LoginPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login Page")
        self.configure(bg="#191414")  # Spotify green
        
        self.create_widgets()

    def create_widgets(self):
        login_button = tk.Button(self, text="Login", bg="#1DB954", fg="white", command=self.redirect)  # Spotify grey
        login_button.pack()

    def redirect(self):
        spoti.authorizeUser()
        self.destroy()
        pass

class ChatPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chat Page")
        self.configure(bg="#191414")  # Spotify green

        self.create_widgets()

    def create_widgets(self):
        generate_answer_button = tk.Button(self, text="Generate Answer", bg="#1DB954", fg="white", command=self.generate_answer)
        generate_answer_button.pack()

        generate_playlist_button = tk.Button(self, text="Generate Playlist", bg="#1DB954", fg="white", command=self.generate_playlist)
        generate_playlist_button.pack()

        self.answer_frame = tk.Frame(self, bg="#F0F0F0")  # Lighter background color
        self.answer_frame.pack()

        self.answer_label = tk.Label(self.answer_frame, text="Modifyable String", bg="#F0F0F0")  # Label with modifiable string
        self.answer_label.pack()

    def generate_answer(self): # TODO Finish this function, rn it only gets the most listened artist and adds a song to the playlist
        gpt.generateAnswer(spoti.mostListenedArtist(time_interval="short_term"))
        spoti.playlist()
        spoti.addSongToPlaylist(song_uri=spoti.getSongIdByName(gpt.artist_and_songs))


    def generate_playlist(self): # TODO Finish this function
        pass


if __name__ == "__main__":
    app = LoginPage()
    app.mainloop()
    if spoti.is_authorized == True:
        app = ChatPage()
        app.mainloop()