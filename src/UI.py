import tkinter as tk
from tkinter import font
from .music import Music
from .chatbot import ChatBot
from .apis import *
from .logManager import LogManager
from tkinter import ttk
from os import path

# Global Clients and logger

logger = LogManager()
spotify = Music(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE, logger=logger)
gpt = ChatBot(OPENAI_API)


class TextWithVar(tk.Text):
    """This class is a text widget, that updates itself, when the tex_variable changes."""

    def __init__(self, master=None, text_variable=None, **kwargs):
        super().__init__(master, **kwargs)
        self._text_variable = text_variable
        if text_variable is not None:
            self._text_variable.trace("w", self._update_text)
            self._update_text()

    def _update_text(self, *_):
        """This function updates the text widget, when the text_variable changes."""
        self.config(state=tk.NORMAL)
        self.delete(1.0, tk.END)
        self.insert(tk.END, self._text_variable.get())
        self.tag_configure("center", justify='center')
        self.tag_add("center", 1.0, "end")
        self.config(state=tk.DISABLED)


class LoginPage(tk.Tk):
    """This class is the login page, where the user can authorize the application to use the Spotify API."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Login Page")
        self.configure(bg="#191414")  # Spotify green
        self.geometry("800x600")
        self.iconbitmap('icons\\icon.ico')

        script_dir = path.dirname(path.realpath(__file__))
        image_path = path.join(script_dir, '..', 'icons', 'mainLogo.png')

        self.image = tk.PhotoImage(file=image_path)
        self.def_font = font.Font(family="Dubai Medium", size=12)

        self.create_widgets()

    def create_widgets(self) -> None:
        """This function creates the widgets for the login page."""
        canvas = tk.Canvas(self, width=self.image.width(), height=self.image.height(), background="#191414", bd=0,
                           highlightthickness=0)
        canvas.create_image(0, 0, anchor=tk.NW, image=self.image)
        canvas.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        login_button = tk.Button(self, text="Login", bg="#008C16", fg="white", width=15, height=2, font=self.def_font,
                                 command=self.redirect)  # Spotify grey
        login_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

    def redirect(self) -> None:
        """This function redirects the user from the Login Page."""
        spotify.authorize_user()
        if spotify.is_authorized:
            self.destroy()
        else:
            self.failed_login()

    def failed_login(self) -> None:
        """This function creates a text, if the login was unsuccessful."""
        failed_login_text = tk.Label(self, text="Login failed, please try again.", bg="#191414", fg="red",
                                     font=self.def_font)
        failed_login_text.place(relx=0.5, rely=0.9, anchor=tk.CENTER)


class MainPage(tk.Tk):
    """This class is the page where the user can interact with the AI, and generate playlists based on the given
    input."""

    def __init__(self) -> None:
        super().__init__()
        self.selected_model = None
        self.selected_generation_term = None
        self.title("Playlist Generator")
        self.configure(bg="#191414")  # Spotify green
        self.geometry("800x600")

        script_dir = path.dirname(path.realpath(__file__))
        image_path = path.join(script_dir, '..', 'icons', 'icon.ico')

        self.iconbitmap(image_path)
        self.def_font = font.Font(family="Dubai Medium", size=12)

        self.generated_flag = tk.BooleanVar(self, False)

        self.display_answer = tk.StringVar(self, "")
        self.display_answer.set(gpt.generate_welcome_text(spotify.get_user_name()))
        self.generate_image_flag = tk.BooleanVar(self, True)

        self.create_widgets()

    def create_buttons(self) -> None:
        """This function creates the buttons for the main page."""
        generate_answer_button = tk.Button(self, text="Generate Music", bg="#008C16", width=15, height=2, fg="white",
                                           font=self.def_font, command=self.generate_answer)
        generate_answer_button.place(relx=0.3, rely=0.85, anchor=tk.CENTER)

        generate_playlist_button = tk.Button(self, text="Generate Playlist", bg="#008C16", width=15, height=2,
                                             fg="white", font=self.def_font, command=self.generate_playlist)
        generate_playlist_button.wait_variable(self.generated_flag)
        generate_playlist_button.place(relx=0.7, rely=0.85, anchor=tk.CENTER)

    def create_gpt_text_space(self) -> None:
        """This function creates the text space for the GPT models answer."""
        text_canvas = tk.Canvas(self, width=500, height=400, bg="#F0F0F0", bd=0, highlightthickness=0)
        text_canvas.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        scrollbar = tk.Scrollbar(text_canvas)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        answer_text = TextWithVar(text_canvas, text_variable=self.display_answer, yscrollcommand=scrollbar.set,
                                  bg="#F0F0F0", fg="black", wrap=tk.WORD, font=self.def_font, width=60, height=15,
                                  state=tk.DISABLED)
        answer_text.pack(side=tk.LEFT, fill=tk.BOTH)

        scrollbar.config(command=answer_text.yview)

    def create_dropdown_menus(self) -> None:
        """This function creates the dropdown menus for the main page, where we can adjust the generation time
        interval, and the model."""
        generation_terms_options = TIME_RANGE.copy()
        model_options = ["gpt-4-turbo-2024-04-09", "gpt-3.5-turbo"]

        self.selected_generation_term = tk.StringVar(self)
        self.selected_model = tk.StringVar(self)

        self.selected_generation_term.set(generation_terms_options[1])
        self.selected_model.set(model_options[0])

        style = ttk.Style()
        style.configure('TCombobox', font=self.def_font)

        generation_terms_menu = ttk.Combobox(self, textvariable=self.selected_generation_term,
                                             values=generation_terms_options, style="TCombobox", state="readonly")
        model_menu = ttk.Combobox(self, textvariable=self.selected_model, values=model_options, style="TCombobox",
                                  state="readonly")

        generation_terms_menu.place(relx=0.10, rely=0.85, anchor=tk.CENTER)
        model_menu.place(relx=0.10, rely=0.9, anchor=tk.CENTER)

    def create_checkbox(self) -> None:
        """This function creates the checkbox for the main page."""
        style = ttk.Style()
        style.configure('TCheckbutton', background="#191414", font=self.def_font, foreground="white")

        generate_image_checkbox = ttk.Checkbutton(self, text="Generate Image", style="TCheckbutton",
                                                  variable=self.generate_image_flag)
        generate_image_checkbox.place(relx=0.1, rely=0.8, anchor=tk.CENTER)

    def create_widgets(self) -> None:
        """This function creates the widgets for the main page."""
        self.create_gpt_text_space()
        self.create_dropdown_menus()
        self.create_checkbox()
        self.create_buttons()

    def generate_answer(self) -> None:
        """This function generates the answer for the user, based on the selected model and time interval."""
        gpt.model = self.selected_model.get()
        gpt.generate_answer(spotify.most_listened_artist(time_interval=self.selected_generation_term.get()))
        self.generated_flag.set(True)
        self.display_answer.set(gpt.generate_return_text())

    def generate_playlist(self):
        """This function calls the spotify playlist creator and if needed, calls the picture generation."""
        spotify.set_timestamp()
        prompt = f"A pixelart of {gpt.artist_and_songs[0][1]} (the musician)"

        if not self.generate_image_flag.get():
            spotify.playlist()
            spotify.add_song_to_playlist(song_uri=spotify.get_song_id_by_name(gpt.artist_and_songs))
        else:
            spotify.playlist(picture_path=gpt.generate_image(prompt, f"Playlist_image"))
            spotify.add_song_to_playlist(song_uri=spotify.get_song_id_by_name(gpt.artist_and_songs))
