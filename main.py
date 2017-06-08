from window import View
import encodings.idna
from logger import Logger

if __name__ == '__main__':
    logger = Logger(name='main')
    root = View(1000, 600)
    root.title('斗鱼弹幕姬')
    root.minsize(height=500, width=800)
    root.mainloop()
