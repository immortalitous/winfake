import ctypes
import os
from PIL import ImageTk, Image, ImageDraw, ImageOps
import pyHook
import pythoncom
import random
import screeninfo
import threading
import time
import tkinter
from tkinter.font import Font

from config import *
from sound import Sound


class KeyBlocker(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.start()

    def run(self):
        hook_manager = pyHook.HookManager()
        hook_manager.KeyDown = self.press
        hook_manager.HookKeyboard()
        pythoncom.PumpMessages()

    def press(self, event):
        if event.Key.lower() in ["lcontrol", "delete"]:
            ctypes.windll.user32.LockWorkStation()
        elif event.Key.lower() == "escape":
            return True
        return False


class IncreaseProgress(threading.Thread):

    def __init__(self, winfake, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.daemon = True

        self.winfake = winfake
        self.progress = 0

        self.start()

    def run(self):
        while True:
            time.sleep(random.randint(1, 5))
            self.progress += random.randint(1, 20)
            if self.progress > 100:
                self.progress = 100
            self.winfake.bluescreen.delete("progress")
            self.winfake.bluescreen.create_text(210, 620, anchor = "nw", fill = "white", font = self.winfake.font, text = f"{self.progress}% complete", tag = "progress")
            if self.progress == 100:
                time.sleep(random.randint(1, 5))
                self.winfake.bluescreen.destroy()
                self.winfake.blackscreen.wm_attributes("-topmost", True)
                time.sleep(random.randint(3, 10))
                self.winfake.blackscreen.wm_attributes("-topmost", False)
                self.winfake.create_loginscreen()
                break


class Winfake():

    def __init__(self):
        KeyBlocker()

        self.screen = tkinter.Tk()
        self.screen.title("")
        self.screen.iconbitmap(f"{IMAGES_PATH}transparent.ico")
        self.monitors = screeninfo.get_monitors()
        self.width_primary, self.height_primary = self.monitors[0].width, self.monitors[0].height
        self.screen.geometry(f"{self.width_primary}x{self.height_primary}")
        self.screen.state("zoomed")
        self.screen.overrideredirect(True)
        self.screen.wm_attributes("-topmost", True)
        self.screen.config(cursor = "none")

        def ignore(event = None):
            return
        self.screen.protocol("WM_DELETE_WINDOW", ignore)
        self.screen.bind("<Escape>", lambda _: self.screen.destroy())

        self.load_assets()
        self.calculate_dimensions()

        self.create_blackscreen()
        self.create_bluescreen()
        IncreaseProgress(self)

        self.screen.mainloop()

    def load_assets(self):
        self.load_fonts()
        self.load_images()
        self.load_error_codes()

    def load_fonts(self):
        self.font_big = Font(family = "Segoe UI Semilight", size = 150)
        self.font_large = Font(family = "Segoe UI Light", size = 40)
        self.font = Font(family = "Segoe UI Light", size = 30)
        self.font_small = Font(family = "Segoe UI Light", size = 14)
        self.font_tiny = Font(family = "Segoe UI Light", size = 10)
        self.entry_font_big = Font(family = "Calibri", size = 16)
        self.entry_font = Font(family = "Calibri", size = 12)

    def load_images(self):
        self.qr_code_image = tkinter.PhotoImage(file = f"{IMAGES_PATH}qr_code.png")
        self.background_image = ImageTk.PhotoImage(Image.open(f"{IMAGES_PATH}background.jfif").resize((self.width_primary, self.height_primary)))
        self.profile_image = self.shaping_profile_image()

    def shaping_profile_image(self):
        profile_image = Image.open(f"{IMAGES_PATH}user.png").resize((self.width_primary//10, self.width_primary//10))
        mask = Image.new("L", (profile_image.size[0]*10, profile_image.size[1]*10), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + mask.size, fill = 255)
        mask = mask.resize(profile_image.size, Image.ANTIALIAS)
        profile_image = ImageOps.fit(profile_image, mask.size, centering = (0.5, 0.5))
        profile_image.putalpha(mask)
        profile_image = ImageTk.PhotoImage(profile_image)
        return profile_image

    def load_error_codes(self):
        with open(f"{DOCUMENTS_PATH}error_codes", "r") as error_codes_file:
            self.error_codes = error_codes_file.readlines()

    def calculate_dimensions(self):
        self.x_origin, self.y_origin = None, None
        self.width, self.height = 0, 0

        for monitor in self.monitors:
            if self.x_origin is None or monitor.x < self.x_origin:
                self.x_origin = monitor.x
            if self.y_origin is None or monitor.y < self.y_origin:
                self.y_origin = monitor.y
            self.width += monitor.width
            self.height += monitor.height

    def create_blackscreen(self):
        self.blackscreen = tkinter.Toplevel(self.screen)
        self.blackscreen.configure(background = "black")
        self.blackscreen.geometry(f"{self.width}x{self.height}+{self.x_origin}+{self.y_origin}")
        self.blackscreen.overrideredirect(True)
        self.blackscreen.config(cursor = "none")

    def create_bluescreen(self):
        self.bluescreen = tkinter.Canvas(self.screen, bd = 0, bg = "#0078D7", width = self.width_primary, height = self.height_primary)
        self.bluescreen.place(x = -2, y = -2)
        self.bluescreen.create_text(200, 150, anchor = "nw", fill = "white", font = self.font_big, text = ":(")
        self.bluescreen.create_text(210, 420, anchor = "nw", fill = "white", font = self.font, text = "Your PC ran into a problem and needs to restart. We're\njust collecting some error info, and then we'll restart for\nyou.")
        self.bluescreen.create_text(210, 620, anchor = "nw", fill = "white", font = self.font, text = "0% complete", tag="progress")
        self.bluescreen.create_text(350, 725, anchor = "nw", fill = "white", font = self.font_small, text = "For more information about this issue and possible fixes, visit https://www.windows.com/stopcode")
        self.bluescreen.create_text(350, 800, anchor = "nw", fill = "white", font = self.font_tiny, text = "If you call a support person, give them this info:")
        self.bluescreen.create_text(350, 830, anchor = "nw", fill = "white", font = self.font_tiny, text = "Stop code: " + random.choice(self.error_codes).split(" ")[1])
        self.bluescreen.create_image(210, 730, anchor = "nw", image = self.qr_code_image)

    def create_loginscreen(self):

        def entry_focus_in(_):
            self.loginscreen.attributes("-alpha", 1)
            entry.config(foreground = "#999999", background = "#FEFEFE")
            entry.icursor(0)

        def entry_focus_out(_):
            self.loginscreen.attributes("-alpha", 0.5)
            entry.config(foreground = "#FEFEFE", background = "#000000")

        def entry_enter(_):
            entry_frame.config(background = "#FEFEFE")

        def entry_leave(_):
            entry_frame.config(background = "#AAAAAA")

        self.screen.config(cursor = "arrow")
        background = tkinter.Canvas(self.screen, border = 0, width = self.width_primary, height = self.height_primary)
        background.place(x = -2, y = -2)
        background.create_image(2, 2, anchor = "nw", image = self.background_image)
        background.create_image(self.width_primary/2, self.height_primary/2-170, image = self.profile_image)

        # C:\Users\user\AppData\Roaming\Microsoft\Windows\AccountPictures
        username = os.getlogin()
        background.create_text(self.width_primary/2, self.height_primary/2, fill = "white", font = self.font_large, text = username)

        self.loginscreen = tkinter.Toplevel()
        self.loginscreen.bind("<FocusOut>", lambda _: self.loginscreen.wm_attributes("-topmost", True))
        self.loginscreen.overrideredirect(True)
        self.loginscreen.resizable(False, False)
        self.loginscreen.wm_attributes("-topmost", True)
        self.loginscreen.attributes("-alpha", 0.5)
        self.loginscreen.wm_geometry(f"+{self.width_primary//2-180}+{self.height_primary//2+90}")
        entry_frame = tkinter.Frame(self.loginscreen, border = 2, background = "#AAAAAA", relief = "flat")
        entry_frame.pack()
        entry_frame.bind
        password = tkinter.StringVar()
        entry = tkinter.Entry(entry_frame, width = 30, border = 8, foreground = "#FEFEFE", background = "#000000", relief = "flat", font = "Calibri", textvariable = password, exportselection = 0)
        entry.pack(side = "left")
        entry.bind("<FocusIn>", entry_focus_in)
        entry.bind("<FocusOut>", entry_focus_out)
        entry.bind("<Enter>", entry_enter)
        entry.bind("<Leave>", entry_leave)
        entry.insert(0, "Password")
        button = tkinter.Button(entry_frame, width = 3, border = 0, foreground = "#FEFEFE", background = "#777777", relief = "flat", font = self.entry_font_big, text = "→")
        button.pack(side = "right")


if __name__ == "__main__":
    #Sound.mute()
    #time.sleep(4)

    Winfake()
