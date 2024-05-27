# Spotify Playlist Generator Project

## Basic infos

This project is made for my Prompt Engineering class at BME. With this project I've learned the basics of Spotipy, Openai python libraries and I'm also learning how to use Github, and Github Copilot efficiently for my studies.

## [src/example_apis.py](example_apis.py)

This file is an example of the apis.py where you can store the API keys, and scopes for the program.

## Time ranges, and models

### Time ranges

The program supports the default Spotify time intervals. The long_term option will get every  listening data made since the creation of the Spotify account. Approximately medium_term uses the last 6 months data, and short_term only uses the last four weeks.

### GPT 3.5 vs GPT4

Right now the program supports the GPT 3.5 Turbo and GPT4 model. The first model is better when we want more genereric, more deterministic answers, it mostly generates popular music made before 2021-22. However the GPT 4 is better at generating less popular music, and give as more verbose results. I advise using the GPT 4 model.

### DALL-E 2.0

For playlist picture generation, the program uses DALL-E 2.0. This can make the process much slower, and more expensive, so by default this function is turned off, but with the checkbox, this can be changed.

> [!IMPORTANT]
> Using Picture generation is 0.016$, which is a lot higher than just generating the playlist. if we'd like to generate a lot of playlists, I advise not to generate pictures.

## Used extensions, etc.

### Comments

The comments are colored by "Better Comments" VSCode extension. The "#?" comments are descriptions for variables. The "#!" comments are warnings, and the "#TODO" comments mark unfinished methods and files.

### Github Copilot

I've used Github Copilot, for the comments, Docstrings and to generate more readable codes. I also used it to debug, and it helped me to learn Pythons TKinter library.

### Python Libraries
Used Python libraries are:

- openai
- spotipy
- webbrowser (Opening Spoitfy Authorization page)
- time (Delaying when uploading playlist picture)
- base64 (Image decoding)
- tkinter (UI)
- os (for file management)
- PIL (for image optimization)

### Logo
The logo was created with [Onlinelogomaker](https://www.onlinelogomaker.com/),and the pictures are made with [DALL-E 2.0](https://openai.com/dall-e-2).

### Picture optimization

The Spotify API doesn't really support images with big size for playlists, so the generated images, are optimized with PIL, for upload stability. Also the picture upload needs to be delayed, so the Spotify has enough time to create the playlist.

### [The photos of the runtime](photos_of_runtime)

The photos in this directory show the app in runtime, and the resulting playlist in spotify.
