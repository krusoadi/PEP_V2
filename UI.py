import tkinter as tk
from tkinter import font
from music import Music
from chatbot import ChatBot
import apis
from logManager import LogManager
from tkinter import ttk

# TODO Making answer display better and commenting the code
logger = LogManager()
spoti = Music(apis.CLIENT_ID, apis.CLIENT_SECRET, apis.REDIRECT_URI, apis.SCOPE, logger=logger)
gpt = ChatBot(apis.OPENAI_API)

class LoginPage(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Login Page")
        self.configure(bg="#191414")  # Spotify green
        self.geometry("800x600")
        self.iconbitmap('icon.ico')
        self.image = image = tk.PhotoImage(file="mainLogo.png")
        self.def_font = font.Font(family="Dubai Medium", size=12)
        
        self.create_widgets()

    def create_widgets(self) -> None: 
        canvas = tk.Canvas(self, width=self.image.width(), height=self.image.height(), background="#191414", bd=0, highlightthickness=0)
        canvas.create_image(0, 0, anchor=tk.NW, image=self.image)     
        canvas.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        
        login_button = tk.Button(self, text="Login", bg="#008C16", fg="white", width=15, height=2, font=self.def_font, command=self.redirect)  #? Spotify grey
        login_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

    def redirect(self) -> None:
        spoti.authorizeUser()
        self.destroy()
        pass

class ChatPage(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Playlist Generator")
        self.configure(bg="#191414")  # Spotify green
        self.geometry("800x600")
        self.iconbitmap('icon.ico')
        self.def_font = font.Font(family="Dubai Medium", size=12)
        
        self.generated_flag = tk.BooleanVar(self, False)
        
        self.display_answer = tk.StringVar(self, "")
        self.display_answer.set(gpt.generateWelcomeText(spoti.getUserName()))
    
        self.create_widgets()

    def createButtons(self) -> None:
        generate_answer_button = tk.Button(self, text="Generate Music", bg="#008C16", width=15, height=2, fg="white", font=self.def_font, command=self.generate_answer)
        generate_answer_button.place(relx=0.3, rely=0.85, anchor=tk.CENTER)

        generate_playlist_button = tk.Button(self, text="Generate Playlist", bg="#008C16", width=15, height=2, fg="white", font=self.def_font, command=self.generate_playlist)
        generate_playlist_button.wait_variable(self.generated_flag)
        generate_playlist_button.place(relx=0.7, rely=0.85, anchor=tk.CENTER)

    def createGPTTextSpace(self) -> None:
        text_canvas = tk.Canvas(self, width=500, height=400, bg="#F0F0F0", bd=0, highlightthickness=0)
        text_canvas.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        
        answer_label = tk.Label(text_canvas, textvariable=self.display_answer, bg="#F0F0F0", fg="black", wraplength=480, font=self.def_font, justify="center")
        answer_label.place(x=10, y=10)
        
    def createDropdownMenus(self) -> None:
            generation_terms_options = apis.TIME_RANGE.copy()
            model_options = ["gpt-3.5-turbo", "gpt-4-0125-preview"]

            self.selected_generation_term = tk.StringVar(self)
            self.selected_model = tk.StringVar(self)

            self.selected_generation_term.set(generation_terms_options[1])
            self.selected_model.set(model_options[0])

            generation_terms_menu = ttk.Combobox(self, textvariable=self.selected_generation_term, values=generation_terms_options)
            model_menu = ttk.Combobox(self, textvariable=self.selected_model, values=model_options)

            generation_terms_menu.place(relx=0.10, rely=0.85, anchor=tk.CENTER)
            model_menu.place(relx=0.10, rely=0.9, anchor=tk.CENTER)


    def create_widgets(self) -> None:
        self.createGPTTextSpace()
        self.createDropdownMenus()
        self.createButtons()
        
    def generate_answer(self) -> None:
        gpt.model = self.selected_model.get()
        gpt.generateAnswer(spoti.mostListenedArtist(time_interval=self.selected_generation_term.get()))
        self.generated_flag.set(True)
        self.display_answer.set(gpt.generateReturnText())

    def generate_playlist(self): # TODO Finish this function
        spoti.playlist(picture_path="images\\secTest.jpeg") #gpt.generateImage("Music with headphones", "firstTest") 
        spoti.addSongToPlaylist(song_uri=spoti.getSongIdByName(gpt.artist_and_songs))


if __name__ == "__main__":
    app = LoginPage()
    app.mainloop()
    if spoti.is_authorized == True:
        app = ChatPage()
        app.mainloop()