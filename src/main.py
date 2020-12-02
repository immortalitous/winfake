from comtypes import CLSCTX_ALL
import ctypes
import os
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageTk
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pyHook
import random
import screeninfo
import sys
import threading
import time
import tkinter
from tkinter.font import Font

from config import *


class BluescreenProgress(threading.Thread):

    def __init__(self, winfake, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.daemon = True

        self.winfake = winfake
        self.progress = 0

        self.start()

    def run(self):
        while True:
            time.sleep(random.randint(1, 5))
            self.progress += random.randint(5, 20)
            if self.progress > 100:
                self.progress = 100
            self.winfake.bluescreen.delete("progress")
            self.winfake.bluescreen.create_text(210, 620, anchor = "nw", fill = "white", font = self.winfake.font, text = f"{self.progress}% complete", tag = "progress")
            if self.progress == 100:
                time.sleep(random.randint(1, 5))
                self.winfake.blackscreen.wm_attributes("-topmost", True)
                self.winfake.bluescreen.destroy()
                time.sleep(random.randint(3, 10))
                self.winfake.create_loadingscreen()
                self.winfake.blackscreen.wm_attributes("-topmost", False)
                break


class LoadingscreenAnimation(threading.Thread):

    def __init__(self, winfake, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.daemon = True

        self.winfake = winfake
        self.frame = 0
        self.end = random.randint(75, 375)

        self.start()

    def run(self):
        while self.frame < self.end:
            time.sleep(0.05)
            self.frame += 1
            self.winfake.loadingscreen.itemconfig(self.winfake.loadingscreen_loading_image_ref, image = self.winfake.loading_image_frames[self.frame % 75])
        self.winfake.blackscreen.wm_attributes("-topmost", True)
        self.winfake.loadingscreen.destroy()
        time.sleep(random.randint(1, 3))
        self.winfake.create_lockscreen()
        self.winfake.blackscreen.wm_attributes("-topmost", False)


class LockscreenAnimation(threading.Thread):

    def __init__(self, winfake, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.daemon = True

        self.winfake = winfake

        self.start()

    def run(self):
        while self.winfake.lockscreen.coords(self.winfake.lockscreen_ethernet_icon_ref)[1] > -100:
            time.sleep(0.005)
            self.winfake.lockscreen.move(self.winfake.lockscreen_localtime_ref, 0, -100)
            self.winfake.lockscreen.move(self.winfake.lockscreen_localdate_ref, 0, -100)
            self.winfake.lockscreen.move(self.winfake.lockscreen_ethernet_icon_ref, 0, -100)
        self.winfake.create_loginscreen()
        self.winfake.lockscreen.destroy()


class Winfake():

    def __init__(self):
        self.block = True

        def press(event):
            if event.Key.lower() == "lcontrol":
                ctypes.windll.user32.LockWorkStation()
            elif event.Key.lower() == "escape" or event.Key.lower() == "space":
                return True
            return not self.block

        self.hook_manager = pyHook.HookManager()
        self.hook_manager.KeyDown = press
        self.hook_manager.HookKeyboard()

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
        BluescreenProgress(self)

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
        self.qr_code_image = ImageTk.PhotoImage(file = f"{IMAGES_PATH}qr_code.png")
        self.windows_logo_image = ImageTk.PhotoImage(Image.open(f"{IMAGES_PATH}windows_logo.png").resize((300, 300)))
        self.loading_image_frames = [tkinter.PhotoImage(file = f"{IMAGES_PATH}loading.gif", format = f"gif -index {i}") for i in range(75)]
        self.background_image = ImageTk.PhotoImage(Image.open(f"{IMAGES_PATH}background.jpg").resize((self.width_primary, self.height_primary)))
        self.background_image_blurred = ImageTk.PhotoImage(Image.open(f"{IMAGES_PATH}background.jpg").resize((self.width_primary, self.height_primary)).filter(ImageFilter.GaussianBlur(30)))
        self.profile_image = ImageTk.PhotoImage(Image.open(f"{IMAGES_PATH}user.png").resize((self.width_primary//12, self.width_primary//12)))

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
        self.bluescreen.create_text(210, 620, anchor = "nw", fill = "white", font = self.font, text = "0% complete", tag = "progress")
        self.bluescreen.create_text(350, 725, anchor = "nw", fill = "white", font = self.font_small, text = "For more information about this issue and possible fixes, visit https://www.windows.com/stopcode")
        self.bluescreen.create_text(350, 800, anchor = "nw", fill = "white", font = self.font_tiny, text = "If you call a support person, give them this info:")
        self.bluescreen.create_text(350, 830, anchor = "nw", fill = "white", font = self.font_tiny, text = "Stop code: " + random.choice(self.error_codes).split(" ")[1])
        self.bluescreen.create_image(210, 730, anchor = "nw", image = self.qr_code_image)

    def create_loadingscreen(self):
        self.loadingscreen = tkinter.Canvas(self.screen, bd = 0, bg = "#000000", width = self.width_primary, height = self.height_primary)
        self.loadingscreen.place(x = -2, y = -2)
        self.loadingscreen.create_image(self.width_primary/2, self.height_primary*0.1, anchor = "n", image = self.windows_logo_image)
        self.loadingscreen_loading_image_ref = self.loadingscreen.create_image(self.width_primary/2, self.height_primary*0.8, anchor = "n", image = self.loading_image_frames[0])
        LoadingscreenAnimation(self)

    def create_lockscreen(self):
        self.screen.config(cursor = "arrow")

        self.lockscreen = tkinter.Canvas(self.screen, bd = 0, width = self.width_primary, height = self.height_primary)
        self.lockscreen.place(x = -2, y = -2)
        self.lockscreen.create_image(2, 2, anchor = "nw", image = self.background_image)
        localtime = time.strftime("%H:%M", time.localtime())
        self.lockscreen_localtime_ref = self.lockscreen.create_text(80, self.height_primary*0.7, anchor = "nw", fill = "white", font = Font(family = "Segoe UI Light", size = 110), text = f"{localtime}")
        localdate = time.strftime("%A, %e. %B", time.localtime())
        self.lockscreen_localdate_ref = self.lockscreen.create_text(80, self.height_primary*0.82, anchor = "nw", fill = "white", font = Font(family = "Segoe UI Light", size = 50), text = f"{localdate}")
        self.lockscreen_ethernet_icon_ref = self.lockscreen.create_text(self.width_primary*0.96, self.height_primary*0.93, anchor = "nw", fill = "white", font = Font(family = "Segoe MDL2 Assets", size = 18), text = "\uE839")
        self.lockscreen.bind("<Button-1>", lambda _: LockscreenAnimation(self))
        self.lockscreen.bind("<space>", lambda _: LockscreenAnimation(self))
        self.lockscreen.focus_set()

    def create_loginscreen(self):
        self.block = False

        self.screen.config(cursor = "arrow")

        self.loginscreen = tkinter.Canvas(self.screen, border = 0, width = self.width_primary, height = self.height_primary)
        self.loginscreen.place(x = -2, y = -2)
        self.loginscreen.create_image(2, 2, anchor = "nw", image = self.background_image_blurred)
        self.loginscreen.create_image(self.width_primary/2, self.height_primary/2-150, image = self.profile_image)

        # C:\Users\user\AppData\Roaming\Microsoft\Windows\AccountPictures
        username = os.getlogin()
        self.loginscreen.create_text(self.width_primary/2, self.height_primary/2+20, fill = "white", font = self.font_large, text = username)

        def entry_frame_enter(event):
            self.entry_frame.config(background = "#FFFFFF")

        def entry_frame_leave(event):
            self.entry_frame.config(background = "#999999")

        self.entry_frame = tkinter.Frame(self.screen, border = 2, background = "#999999", relief = "flat")
        self.entry_frame.place(x = self.width_primary/2, y = self.height_primary/2+100, height = 45, width = 350, anchor = "center")
        self.entry_frame.bind("<Enter>", entry_frame_enter)
        self.entry_frame.bind("<Leave>", entry_frame_leave)

        def set_cursor(event):
            self.screen.after_idle(self.entry.icursor, 0)
            self.entry.icursor(0)

        def is_valid(character):
            if character.isalpha() or character.isdigit():
                return True
            return False

        def entry_reveal(event):
            self.entry.config(show = "")

        def entry_hide(event):
            self.entry.config(show = "\u25CF")

        def entry_check(event):
            value = self.entry.get()
            if value == "Password" and is_valid(event.char):
                self.entry.delete(0, "end")
                self.entry.config(foreground = "#000000", show = "\u25CF")
                self.entry.unbind("<Button-1>")

                self.reveal_button = tkinter.Button(self.entry_frame, width = 5, border = 0, foreground = "#555555", background = "#FFFFFF", activeforeground = "#FFFFFF", activebackground = "#666666", relief = "flat", font = Font(family = "Segoe MDL2 Assets", size = 12), text = "\uF78D")
                self.reveal_button.place(x = 266, y = 0, height = 41)
                self.reveal_button.bind("<ButtonPress-1>", entry_reveal)
                self.reveal_button.bind("<ButtonRelease-1>", entry_hide)
            elif len(value) == 1 and event.keycode == 8:
                self.entry.delete(0)
                self.entry.insert(0, "Password")
                self.entry.icursor(0)
                self.entry.config(foreground = "#555555", show = "")
                self.entry.bind("<Button-1>", set_cursor)

                self.reveal_button.destroy()

        def entry_enter(event = None):
            password = self.entry.get()
            sys.exit(0)

        self.entry_value = tkinter.StringVar()
        self.entry = tkinter.Entry(self.entry_frame, width = 36, border = 9, foreground = "#555555", background = "#FFFFFF", selectforeground = "#FFFFFF", selectbackground = "#767676", relief = "flat", font = Font(family = "Segoe UI Semilight", size = 12), textvariable = self.entry_value, exportselection = 0)
        self.entry.pack(side = "left")
        self.entry.insert(0, "Password")
        self.entry.icursor(0)
        self.entry.focus_set()
        self.entry.bind("<Button-1>", set_cursor)
        self.entry.bind("<Key>", entry_check)
        self.entry.bind("<Return>", entry_enter)

        self.enter_button = tkinter.Button(self.entry_frame, width = 4, height = 2, border = 0, foreground = "#FFFFFF", background = "#777777", activeforeground = "#FFFFFF", activebackground = "#AAAAAA", relief = "flat", font = Font(family = "Segoe MDL2 Assets", size = 14), text = "\uE0AB", command = entry_enter)
        self.enter_button.pack(side = "right")

        self.loginscreen.create_text(self.width_primary*0.9075, self.height_primary*0.958, anchor = "nw", fill = "white", font = Font(family = "Segoe UI", size = 13), text = "ENG")
        self.loginscreen.create_text(self.width_primary*0.93, self.height_primary*0.955, anchor = "nw", fill = "white", font = Font(family = "Segoe MDL2 Assets", size = 25), text = "\uE839")
        self.loginscreen.create_text(self.width_primary*0.9525, self.height_primary*0.955, anchor = "nw", fill = "white", font = Font(family = "Segoe MDL2 Assets", size = 25), text = "\uE776")
        self.loginscreen.create_text(self.width_primary*0.975, self.height_primary*0.955, anchor = "nw", fill = "white", font = Font(family = "Segoe MDL2 Assets", size = 25), text = "\uE7E8")



if __name__ == "__main__":
    Winfake()
