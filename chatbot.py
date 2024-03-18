from openai import OpenAI
from logManager import LogManager

# TODO felkesz meg kell fejleszteni, tobb agra bontani a generateAnswer-t

class ChatBot:
    def __init__(self, API_KEY: str) -> None:
        #kliens
        self.client = OpenAI(api_key=API_KEY)
        
        #Modell belso adatai
        
        self.model = "gpt-3.5-turbo" #"gpt-4-0125-preview"
        self.temperature = 0.7
        self.top_p = 0.9
        self.n = 1
        self.frequency_penalty = 0.8
        self.delimiter = ";"
        
        #Visszaadott belso ertekek
        
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
    
    def generateAnswer(self, most_listened_artists) -> None:
        self.last_full_response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"You are a music assistant who generates song in the format of ARTIST{self.delimiter}SONG_NAME always separated with a new line, who only reccomends a song if it is not made by a Hungarian artist. Your job is to suggest songs, based on the artists, that the user listens to.The artists, are: {most_listened_artists} you can't suggest songs from these artist, you always come up with new ones related to these. Be creative and don't recommend a song more than once!"},
                {"role": "user", "content": "Can you recommend me 3 songs?"},
                {"role": "assistant", "content": "Travis Scott;SICKO MODE\nBeyonce;Single Ladies\nMacklemore;Can't Hold Us"},
                {"role": "user", "content": "Can you recommend me 15 songs? Please don't recommend songs from artist, who i listened to earlier, but make sure they are similar, and rap or pop songs too."}
            ],
            temperature=self.temperature,
            top_p=self.top_p,
            n=self.n,
            frequency_penalty=self.frequency_penalty
        )
        self.last_response_tokens = self.last_full_response.usage.completion_tokens
        self.session_tokens += self.last_response_tokens
        
        self._answerParser()
        self._autoSave()
        
