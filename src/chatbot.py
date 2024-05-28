from openai import OpenAI
import urllib.request
from os import path, mkdir, remove
from PIL import Image


class ChatBot:
    def __init__(self, api_key: str) -> None:
        # Client
        self.client = OpenAI(api_key=api_key)

        # Model parameters

        self.model = "gpt-4-turbo-2024-04-09"  # This model gives, the best output.
        self.temperature = 0.8  # High temperature is needed, for more verbose outputs.
        self.top_p = 0.9
        self.n = 1
        self.frequency_penalty = 0.8
        self.delimiter = ";"

        # Return values

        self.last_full_response = None
        self.last_response_tokens = 0
        self.artist_and_songs = None
        self.session_tokens = 0

    def _answer_parser(self, split_char: str = ";") -> None:
        """This function parses the text into the desired format, what we will need to use for the spotipy API. It
        splits the text by the given character, and creates a list of lists, where the first element is the song,
        and the second is the artist."""

        un_parsed_answer = self.last_full_response.choices[0].message.content.split("\n")
        self.artist_and_songs = []

        for i, element in enumerate(un_parsed_answer):
            # Parsing with different delimiters (sometimes the model generates with other limiters)
            un_parsed_answer[i] = element.split(split_char)

            if len(un_parsed_answer[i]) == 1:
                un_parsed_answer[i] = element.split("-")

                if len(un_parsed_answer[i]) == 1:
                    un_parsed_answer[i] = element.split(":")

            self.artist_and_songs.append([un_parsed_answer[i][1], un_parsed_answer[i][0]])

    def _auto_save(self) -> None:
        """This function saves the last response into a file."""

        script_dir = path.dirname(path.realpath(__file__))
        response_path = path.join(script_dir, '..', 'log', 'responses.txt')

        with open(response_path, "a", encoding="utf-8") as file:
            file.write(f"\n\n--------------used_tokens: {self.last_response_tokens}---------------\n")

            for element in self.artist_and_songs:
                file.write(f"track:{element[0]} artist:{element[1]}")

            file.write("\n")
            file.write(self.last_full_response.choices[0].message.content)
            file.write(f"\n\n--------session token usage: {self.session_tokens}--------------------\n")

    def generate_answer(self, most_listened_artists, debug_mode: bool = False) -> None:
        """This function generates the songs, based on the given parameters. It uses the OpenAI API to generate the
        response. The response is then parsed, and saved into a file, if the debug_mode is True."""
        self.last_full_response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system",
                 "content": f"You are a music assistant who advises song in the format of"
                            f"ARTIST{self.delimiter}SONG_NAME always separated"
                            f" with a new line, who only recommends a song if it is not made by a Hungarian artist."
                            f" Your job is to suggest songs, based on the artists,"
                            f" that the user listens to. The artists, are: {most_listened_artists} avoid suggesting"
                            f" songs from these artist, or come up with new ones related to these. "
                            f"Be creative and don't recommend a song more than once! Don't advise fictional songs!"},
                {"role": "user", "content": "Can you recommend me 3 songs?"},
                {"role": "assistant",
                 "content": "Travis Scott;SICKO MODE\nBeyonce;Single Ladies\nMacklemore;Can't Hold Us"},
                {"role": "user",
                 "content": "Can you recommend me 15 songs? Please don't recommend a lot of songs from artists, "
                            "who i listened to earlier, but make sure they are similar, and rap or pop songs too."}
            ],
            temperature=self.temperature * 1.25,
            top_p=self.top_p,
            n=self.n,
            frequency_penalty=self.frequency_penalty
        )

        self.last_response_tokens = self.last_full_response.usage.completion_tokens
        self.session_tokens += self.last_response_tokens

        self._answer_parser()
        if debug_mode:  # We only need to save the responses, when we are in debug mode.
            self._auto_save()

    def generate_welcome_text(self, name: str) -> str:
        """This function generates the welcome text for the user. It uses the OpenAI API to generate the response."""
        answer = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system",
                 "content": f"You are a young slangy playlist maker. Your name is Listify Assistant, always introduce "
                            f"yourself, and you have to greet the new user (His/her name is {name}),with a welcoming "
                            f"text. Advise to make playlist, but don't ask for name, type, etc."},
                {"role": "assistant",
                 "content": "Hey, what's up dude I'm Listify Assistant, lemme make you some new playlist."},
            ],
            temperature=self.temperature,
            top_p=self.top_p,
            n=self.n,
            frequency_penalty=self.frequency_penalty
        )

        self.last_response_tokens = answer.usage.total_tokens
        self.session_tokens += answer.usage.total_tokens

        return answer.choices[0].message.content

    def generate_return_text(self) -> str:
        """This function generates a text to present the generated songs."""
        answer = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system",
                 "content": f"You are a young slangy playlist generator. Your name is Listify Assistant, And you've "
                            f"made a playlist already, and have to put a text, to return the results. Do not advise "
                            f"song names please."},
                {"role": "assistant", "content": "Okay, I'm ready with the playlist, here are the songs:\n"},
            ],
            temperature=self.temperature * 1.25,
            top_p=self.top_p,
            n=self.n,
            frequency_penalty=self.frequency_penalty
        )
        self.last_response_tokens = answer.usage.total_tokens
        self.session_tokens += answer.usage.total_tokens

        return_string = "" + answer.choices[0].message.content + "\n"

        for i, element in enumerate(self.artist_and_songs):
            return_string += f"{element[1]} - {element[0]}\n"

        return return_string

    def generate_image(self, prompt: str, filename: str, debug_mode: bool = False) -> str:
        """This function generates an image for the spotify playlist, if debug_mode is on."""
        if debug_mode:
            return f"images\\{filename}.jpeg"

        resp = self.client.images.generate(prompt=prompt, model="dall-e-2", size="256x256", n=1, response_format="url")
        url = resp.data[0].url

        if not path.isdir("images"):
            mkdir("images")

        name = f"images\\{filename}.jpeg"

        # We need to optimize the size of the generated picture, because spotipy tends to be buggy when a big file
        # is given.

        urllib.request.urlretrieve(url, name)  # It's easier to download from the given url.
        file = Image.open(name)
        file.save(f"images\\{filename}_optimized.jpeg", "JPEG", optimize=True, quality=75)
        file.close()
        remove(name)
        return f"images\\{filename}_optimized.jpeg"
