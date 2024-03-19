# Spotify Playlist Generator Project

## Basic infos

This project is made for my Prompt Engineering class at BME. With this project I've learned the basics of Spotipy and Openai python libraries. In this project I'm also learning how to use Github, and Github Copilot efficiently for my studies.

## Time ranges, and models

### Time ranges

The program supports the default Spotify time intervals. The long_term option will get every  listening data made since the creation of the Spotify account. Approximately medium_term uses the last 6 months data, and short_term only uses the last four weeks.

### GPT 3.5 vs GPT4

Right now the program supports the GPT 3.5 Turbo and GPT4 model. The first model is better when we want more genereric, more deterministic answers, it mostly generates popular music made before 2021-22. However the GPT 4 is better at generating lesser-known music, and give as more verbose results. I advise using the GPT 4 model.

### DALL-E 2

For playlist picture generation, the program uses DALL-E 2. This can make the process much slower, and more expensive, so by default this function is turned off, but in the dropdown menu, this can be changed 

## Used extensions, etc.

### Comments

The comments are colored by "Better Comments" VSCode extension. The "#?" comments are descriptions for variables. The "#!" comments are warnings, and the "#TODO" comments mark unfinished methods and files.

### Github Copilot

I've used Github Copilot, for the comments, Docstrings and to generate more readable codes.

### Python Libraries
Used Python libraries are:

- openai
- webbrowser
- spotipy
- time
- base64
- tkinter

### Logo
The logo was created with [Onlinelogomaker](https://www.onlinelogomaker.com/),and the pictures are made with [DALL-E 2.0](https://openai.com/dall-e-2).

> [!WARNING]
> Still under development

