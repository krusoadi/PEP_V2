#? This file is an example of the api.py file, where you can store your API keys, and other sensitive information. This file is not included in the repository, so you have to create it yourself. The file should look like this:

#OPENAI

OPENAI_API = "YOUR_API_KEY"

#SPOTIFY

CLIENT_ID = 'YOUE_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
REDIRECT_URI = 'http://localhost:3000'

# Scopes, and data needed for our spotify class

SCOPE = ["user-library-read", "user-top-read","playlist-modify-public", "playlist-modify-private", "ugc-image-upload", "user-read-private", "user-read-email"]
TIME_RANGE = ["long_term", "medium_term", "short_term"]
