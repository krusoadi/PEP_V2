from src.UI import *

if __name__ == "__main__":
    app = LoginPage()
    app.mainloop()
    if spoti.is_authorized:
        app = MainPage()
        app.mainloop()