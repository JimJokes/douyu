import tkinter as tk
import encodings.idna

from ttkWindow import App
from logger import Logger

__version__ = 'v2.1.0'

if __name__ == '__main__':
    logger = Logger(name='main')
    root = tk.Tk()
    App(root)
    root.title('斗鱼弹幕姬%s   by：缘总包养的小三儿' % __version__)
    # root.minsize(height=500, width=800)
    root.mainloop()
