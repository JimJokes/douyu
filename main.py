from window import View
import encodings.idna
from logger import Logger

if __name__ == '__main__':
    logger = Logger(name='main')
    root = View()
    root.master.title('斗鱼弹幕姬')
    root.master.minsize(height=500, width=800)
    root.mainloop()
