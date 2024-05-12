from openai import OpenAI
from logManager import LogManager
import urllib.request
from os import path, mkdir, remove
from PIL import Image

# TODO Add a method, for playlist picture generation 

class ChatBot:
    def __init__(self, API_KEY: str) -> None:
        #? Client
        self.client = OpenAI(api_key=API_KEY)
        
        #? Model parameters
        
        self.model = "gpt-4-0125-preview"
        self.temperature = 0.8
        self.top_p = 0.9
        self.n = 1
        self.frequency_penalty = 0.8
        self.delimiter = ";"
        
        #? Return values
        
        self.last_full_response = None
        self.last_response_tokens = 0
        self.artist_and_songs = None
        self.session_tokens = 0
    
    def _answerParser(self, split_char: str = ";") -> None:
        '''This function parses the text into the desired format'''
        
        un_parsed_answer = self.last_full_response.choices[0].message.content.split("\n")
        self.artist_and_songs = []
        
        for i, element in enumerate(un_parsed_answer):
            un_parsed_answer[i] = element.split(split_char)
            
            if len(un_parsed_answer[i]) == 1:
                un_parsed_answer[i] = element.split("-")
                
                if len(un_parsed_answer[i]) == 1:
                    un_parsed_answer[i] = element.split(":")
            
            self.artist_and_songs.append([un_parsed_answer[i][1], un_parsed_answer[i][0]])
            
    def _autoSave(self) -> None: 
        '''This function saves the last response into a file'''
        
        with open("responses.txt", "a", encoding="utf-8") as file:
            file.write(f"\n\n--------------used_tokens: {self.last_response_tokens}---------------\n")
            
            for element in self.artist_and_songs:
                file.write(f"track:{element[0]} artist:{element[1]}")
                
            file.write("\n")
            file.write(self.last_full_response.choices[0].message.content)
            file.write(f"\n\n--------session token usage: {self.session_tokens}--------------------\n")
    
    def generateAnswer(self, most_listened_artists) -> None: #! This needs to be made to multiple methods, with function overloading
        self.last_full_response = self.client.chat.completions.create(
            model=self.model,
            messages=[ 
                {"role": "system", "content": f"You are a music assistant who generates song in the format of ARTIST{self.delimiter}SONG_NAME always separated with a new line, who only reccomends a song if it is not made by a Hungarian artist. Your job is to suggest songs, based on the artists, that the user listens to. The artists, are: {most_listened_artists} avoid suggesting songs from these artist, or come up with new ones related to these. Be creative and don't recommend a song more than once! Don't advse fictional songs!"},
                {"role": "user", "content": "Can you recommend me 3 songs?"},
                {"role": "assistant", "content": "Travis Scott;SICKO MODE\nBeyonce;Single Ladies\nMacklemore;Can't Hold Us"},
                {"role": "user", "content": "Can you recommend me 15 songs? Please don't recommend a lot of songs from artists, who i listened to earlier, but make sure they are similar, and rap or pop songs too."}
            ],
            temperature=self.temperature*1.25,
            top_p=self.top_p,
            n=self.n,
            frequency_penalty=self.frequency_penalty
        )
        self.last_response_tokens = self.last_full_response.usage.completion_tokens
        self.session_tokens += self.last_response_tokens
        
        self._answerParser()
        self._autoSave() 
    
    def generateWelcomeText(self, name: str) -> str:
        answer = self.client.chat.completions.create(
            model=self.model,
            messages=[ 
                {"role": "system", "content": f"You are a young slangy playlist generator. Your name is Listify Assistant, always introduce yourself, and you have to greet the new user (His/her name is {name}),with a welcoming text. Advise to make playlist, but don't ask for name, type, etc."},
                {"role": "assistant", "content": "Hey, what's up dude I'm Listify Assistant, let me generate you some new playlist."},
            ],
            temperature=self.temperature,
            top_p=self.top_p,
            n=self.n,
            frequency_penalty=self.frequency_penalty
        )
        self.last_response_tokens = answer.usage.total_tokens
        self.session_tokens += answer.usage.total_tokens

        return answer.choices[0].message.content
    
    def generateReturnText(self) -> str:
        answer = self.client.chat.completions.create(
            model=self.model,
            messages=[ 
                {"role": "system", "content": f"You are a young slangy playlist generator. Your name is Listify Assistant, And you've generated a playlist already, and have to put a text, to return the results. Do not generate song names please."},
                {"role": "assistant", "content": "Okay, I'm ready with the playlist, here are the songs:\n"},
            ],
            temperature=self.temperature*1.25,
            top_p=self.top_p,
            n=self.n,
            frequency_penalty=self.frequency_penalty
        )
        self.last_response_tokens = answer.usage.total_tokens
        self.session_tokens += answer.usage.total_tokens
        
        returnString = "" + answer.choices[0].message.content + "\n"
        
        for i, element in enumerate(self.artist_and_songs):
            returnString += f"{element[1]} - {element[0]}\n"
            
        return returnString
    
    def generateImage(self, prompt:str, filename:str, debug_mode:bool = False) -> str:
        if debug_mode:
             return f"images\\{filename}.jpeg"
        
        resp = self.client.images.generate(prompt= prompt, model="dall-e-2", size="256x256", n=1, response_format="url")
        url = resp.data[0].url
        
        if not path.isdir("images"):
            mkdir("images")

        name = f"images\\{filename}.jpeg"

        urllib.request.urlretrieve(url, name)
        file = Image.open(name)
        file.save(f"images\\{filename}_optimized.jpeg", "JPEG", optimize=True, quality=75)
        file.close()
        remove(name)
        return f"images\\{filename}_optimized.jpeg" 


        