import time
import ctypes


SendInput = ctypes.windll.user32.SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)


class Sound:

    def mute():
        Keyboard.key(Keyboard.VK_VOLUME_MUTE)


class KeyboardInput(ctypes.Structure):

    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):

    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):

    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class InputInterfaces(ctypes.Union):

    _fields_ = [("ki", KeyboardInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):

    _fields_ = [("type", ctypes.c_ulong),
                ("ii", InputInterfaces)]


class Keyboard:

    VK_VOLUME_MUTE = 0xAD

    def key_down(code):
        extra = ctypes.c_ulong(0)
        ii_ = InputInterfaces()
        ii_.ki = KeyboardInput(code, 0x48, 0, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def key_up(code):
        extra = ctypes.c_ulong(0)
        ii_ = InputInterfaces()
        ii_.ki = KeyboardInput(code, 0x48, 0x0002, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def key(code):
        Keyboard.key_down(code)
        Keyboard.key_up(code)
