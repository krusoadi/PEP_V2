from UI import *

if __name__ == "__main__":
    app = LoginPage()
    app.mainloop()
    if spoti.is_authorized == True:
        app = MainPage()
        app.mainloop()