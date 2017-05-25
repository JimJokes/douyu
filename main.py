from window import View
import encodings.idna

if __name__ == '__main__':
    root = View()
    root.master.title('斗鱼弹幕姬')
    root.master.minsize(height=500, width=800)
    root.mainloop()
