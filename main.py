from src.UI import *

if __name__ == "__main__":
    app = LoginPage()
    app.mainloop()
    if spotify.is_authorized:
        app = MainPage()
        app.mainloop()
