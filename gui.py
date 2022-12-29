# tkinterでGUIを作成する
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import shift_SA


def selectCSV():
    typ = [('csvファイル', '*.csv')]
    fl = filedialog.askopenfilename(title="csvファイルを開く", filetypes=typ, initialdir="./")
    return fl


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        # self.master.state("zoomed")  # ウィンドウ最大化

        # モデル初期化
        self.model = None
        self.initModel()

        # ウィジェット配置
        notebook = ttk.Notebook(self.master)

        menuBar = tk.Menu()
        self.master.config(menu=menuBar)

        fileMenu = tk.Menu()
        menuBar.add_cascade(label="ファイル", menu=fileMenu)
        # fileMenu.add_command(label="ファイル選択", command=self.initModel)

        desire_tab = tk.Frame(notebook)
        param_tab = tk.Frame(notebook)
        result_tab = tk.Frame(notebook)

        notebook.add(desire_tab, text="　出勤希望　")
        notebook.add(param_tab, text="　パラメータ　")
        notebook.add(result_tab, text="　結果　")
        notebook.pack(expand=True, fill='both', padx=10, pady=10)

        button = tk.Button(text="▶ 【実行】", width=10, height=1, bd=0, fg="green")
        button.place(x=900, y=10, anchor=tk.NW)

        # desire_tab #####################################################################
        font_width = 1
        font_height = 2
        pad = 1
        name_list = ["A", "B", "C", "D", "E", "F", "G", "H"]

        f_const = tk.Frame(desire_tab, padx=10, pady=10)
        f_const.pack(anchor=tk.W, padx=10, pady=10)
        for i in range(1, 61):
            lb_date = tk.Label(f_const, text=str(int((i + 1) / 2)), width=font_width, height=font_height)
            lb_date.grid(row=0, column=i, padx=pad)
        const = self.model.const
        for r1 in range(len(const)):
            c_list = const[r1]
            lb_name = tk.Label(f_const, text=name_list[r1], width=font_width + 3, height=font_height)
            lb_name.grid(row=r1 + 1, column=0, padx=pad)
            for r2 in range(len(c_list)):
                point = c_list[r2]
                lb_const = tk.Label(f_const, text=str(point), width=font_width, height=font_height)
                lb_const.grid(row=r1 + 1, column=r2 + 1, padx=pad)

        # param_tab #######################################################################
        # ここは後から。

        # result_tab ######################################################################
        font_width = 1
        font_height = 2
        pad = 1
        name_list = ["A", "B", "C", "D", "E", "F", "G", "H"]

        f_res = tk.Frame(result_tab, padx=10, pady=10)
        f_res.pack(anchor=tk.W, padx=10, pady=10)
        for i in range(1, 61):
            lb_date = tk.Label(f_res, text=str(int((i + 1) / 2)), width=font_width, height=font_height)
            lb_date.grid(row=0, column=i, padx=pad)

        self.optimize()  # 今後はボタンを押したら最適化を実行するようにする。

        first = self.model.sample_set.record[self.model.order][0][0]
        for m in range(self.model.MANPOWER):
            day = first[self.model.DAY * m: self.model.DAY * m + self.model.DAY]
            lb_name = tk.Label(f_res, text=name_list[m], width=font_width + 3, height=font_height)
            lb_name.grid(row=m + 1, column=0, padx=pad)
            for d in range(len(day)):
                point = day[d]
                if not point:
                    lb_res = tk.Label(f_res, text="", width=font_width, height=font_height, relief="solid",
                                      borderwidth=1)
                else:
                    if const[m][d] == 0:
                        lb_res = tk.Label(f_res, text="", width=font_width, height=font_height, relief="solid",
                                          borderwidth=1, background="green")
                    elif const[m][d] == 1:
                        lb_res = tk.Label(f_res, text="", width=font_width, height=font_height, relief="solid",
                                          borderwidth=1, background="yellow")
                    elif const[m][d] == 2:
                        lb_res = tk.Label(f_res, text="", width=font_width, height=font_height, relief="solid",
                                          borderwidth=1, background="orange")
                    else:
                        lb_res = tk.Label(f_res, text="", width=font_width, height=font_height, relief="solid",
                                          borderwidth=1, background="red")
                lb_res.grid(row=m + 1, column=d + 1, padx=pad)

    def initModel(self):
        self.model = shift_SA.ShiftAnneal()
        self.model.setCSV(selectCSV())
        self.model.setParam()

    # 最適化ボタン
    def optimize(self):
        self.model.setConst()
        self.model.sample()


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
