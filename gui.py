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
        self.notebook = ttk.Notebook(self.master)

        self.menubar = tk.Menu()
        self.master.config(menu=self.menubar)

        self.menu_file = tk.Menu()
        self.menubar.add_cascade(label="File", menu=self.menu_file)
        self.menu_file.add_command(label="ファイル選択", command=self.initModel)

        self.tab_desire = tk.Frame(self.notebook)
        self.tab_param = tk.Frame(self.notebook)
        self.tab_result = tk.Frame(self.notebook)

        self.notebook.add(self.tab_desire, text="　出勤希望　")
        self.notebook.add(self.tab_param, text="　パラメータ　")
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        self.button_opt = tk.Button(text="▶ 【実行】", width=10, height=1, bd=0, fg="green", command=self.optimize)
        self.button_opt.place(x=900, y=10, anchor=tk.NW)

        self.show_desire()
        # self.tab_param は後から。
        self.tr_res = None

    def initModel(self):
        self.model = shift_SA.ShiftAnneal()
        self.model.setCSV(selectCSV())
        self.model.setParam()

    # tab_desireの表示（更新）
    def show_desire(self, fw=1, fh=2, pad=1):
        font_width = fw
        font_height = fh
        pad = pad
        name_list = self.model.NAME

        f_const = tk.Frame(self.tab_desire, padx=10, pady=10)
        f_const.grid(row=0, column=0, padx=10, pady=10)
        for i in range(1, self.model.DAY + 1):
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

    # tab_resultの表示（更新）
    def show_result(self):
        self.tr_res = ttk.Treeview(self.tab_result, height=15)
        tmp_pena = self.model.getPenalty(self.model.sample_set.record[0][0])
        self.tr_res["columns"] = [r for r in range(len(tmp_pena) + 1)]
        self.tr_res["show"] = "headings"
        heading_id = 1
        self.tr_res.column(0, width=50)
        self.tr_res.heading(0, text="ID")
        for p in tmp_pena:
            self.tr_res.column(heading_id, width=len(p[0]) * 23)
            self.tr_res.heading(heading_id, text=p[0])
            heading_id += 1
        for sample_id in self.model.order:
            sample = self.model.sample_set.record[sample_id][0]
            penalty_list = self.model.getPenalty(sample)
            values = [v[1] for v in penalty_list]
            values.insert(0, sample_id)
            self.tr_res.insert("", "end", values=values)
        self.tr_res.grid(row=0, column=0, padx=10, pady=10)

        vbar = ttk.Scrollbar(self.tab_result, orient="vertical", command=self.tr_res.yview)
        self.tr_res.configure(yscrollcommand=vbar.set)
        vbar.grid(row=0, column=1, padx=10, pady=10, sticky=tk.N + tk.S)

        self.tr_res.bind("<Double-1>", self.TrResDouble)

    # ツリービューをダブルクリックして詳細表示
    def TrResDouble(self, event):
        selected_item = self.tr_res.selection()[0]
        values_1 = self.tr_res.item(selected_item)['values'][0]
        sample = self.model.sample_set.record[values_1][0]
        self.show_sample(title="サンプル{0}".format(values_1), sample=sample)

    # サンプルの表示
    def show_sample(self, title="サンプル", sample=None, fw=1, fh=2, pad=1, row=0, column=0):
        font_width = fw
        font_height = fh
        pad = pad
        name_list = self.model.NAME
        const = self.model.const

        new_tab = tk.Frame(self.notebook)
        self.notebook.add(new_tab, text=title)

        f_sam = tk.Frame(new_tab, padx=10, pady=10)
        f_sam.grid(row=row, column=column, padx=10, pady=10)
        for i in range(1, self.model.DAY + 1):
            lb_date = tk.Label(f_sam, text=str(int((i + 1) / 2)), width=font_width, height=font_height)
            lb_date.grid(row=0, column=i, padx=pad)

        for m in range(self.model.MANPOWER):
            day = sample[self.model.DAY * m: self.model.DAY * m + self.model.DAY]
            lb_name = tk.Label(f_sam, text=name_list[m], width=font_width + 3, height=font_height)
            lb_name.grid(row=m + 1, column=0, padx=pad)
            for d in range(len(day)):
                point = day[d]
                if not point:
                    lb_sam = tk.Label(f_sam, text="", width=font_width, height=font_height, relief="solid",
                                      borderwidth=1)
                else:
                    if const[m][d] == 0:
                        lb_sam = tk.Label(f_sam, text="", width=font_width, height=font_height, relief="solid",
                                          borderwidth=1, background="green")
                    elif const[m][d] == 1:
                        lb_sam = tk.Label(f_sam, text="", width=font_width, height=font_height, relief="solid",
                                          borderwidth=1, background="yellow")
                    elif const[m][d] == 2:
                        lb_sam = tk.Label(f_sam, text="", width=font_width, height=font_height, relief="solid",
                                          borderwidth=1, background="orange")
                    else:
                        lb_sam = tk.Label(f_sam, text="", width=font_width, height=font_height, relief="solid",
                                          borderwidth=1, background="red")
                lb_sam.grid(row=m + 1, column=d + 1, padx=pad)

        self.notebook.select(new_tab)

    # 最適化
    def optimize(self):
        self.model.setConst()
        self.model.sample()
        self.notebook.add(self.tab_result, text="　結果リスト　")
        ind = 0
        # self.show_sample(sample=self.model.sample_set.record[self.model.order][0][0], column=0)
        self.show_result()
        self.notebook.select(self.tab_result)


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
