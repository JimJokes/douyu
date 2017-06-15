from window import View
import encodings.idna
from logger import Logger

from . import __version__

if __name__ == '__main__':
    logger = Logger(name='main')
    root = View(1000, 600)
    root.title('斗鱼弹幕姬%s   by：缘总包养的小三儿' % __version__)
    root.minsize(height=500, width=800)
    root.mainloop()
