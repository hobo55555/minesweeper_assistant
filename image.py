import ctypes
import ctypes.wintypes
import cv2
import numpy as np
import win32gui
from PIL import ImageGrab


# 手工测量得到block的尺寸为24px*24px
a = 24


# 切割
def crop_block(whole_img, x, y):
    """
    :param whole_img: img
    :param x: int
    :param y: int
    :return: image of a single block
    """
    x1, y1 = x * a, y * a
    x2, y2 = x1 + a, y1 + a
    return whole_img.crop((x1, y1, x2, y2))


# PIL格式转为OpenCV格式，BGR
def pil_to_cv(img):
    """
    :param img: img
    :return: array
    """
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


def get_window_rect(hwnd):
    """
    :param hwnd: handle
    :return: left, top, right, bottom
    """
    try:
        f = ctypes.windll.dwmapi.DwmGetWindowAttribute
    except WindowsError:
        f = None
    if f:
        rect = ctypes.wintypes.RECT()
        DWMWA_EXTENDED_FRAME_BOUNDS = 9
        f(ctypes.wintypes.HWND(hwnd),
          ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
          ctypes.byref(rect),
          ctypes.sizeof(rect)
          )
        return rect.left, rect.top, rect.right, rect.bottom


def get_frame():
    my_handle = win32gui.FindWindow(0, 'Minesweeper Arbiter ')
    my_rect = get_window_rect(my_handle)
    l, t, r, b = my_rect
    l += 20
    t += 153
    r -= 19
    b -= 60
    my_rect = (l, t, r, b)
    img = ImageGrab.grab(my_rect)
    # img.show()
    # img.save('C:\\Users\\21109\\OneDrive - 南京大学\\课程\\Python\\saolei\\save2.png')
    # img.save('C:\\Users\\21109\\OneDrive - 南京大学\\课程\\Python\\saolei\\save.png')

    width = r - l
    height = b - t
    num_x, num_y = width // a, height // a

    blocks_img = [[0 for i in range(num_y)] for i in range(num_x)]

    for y in range(num_y):
        for x in range(num_x):
            blocks_img[x][y] = crop_block(img, x, y)

    return img, blocks_img, (num_x, num_y), (width, height), my_rect

