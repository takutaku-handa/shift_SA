# tkinterでGUIを作成する
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import shift_SA


def selectCSV():
    typ = [('csvファイル', '*.csv')]
    fl = filedialog.askopenfilename(title="csvファイルを開く", filetypes=typ, initialdir="./")
    return fl


def print_date(var):
    def ret():
        print(var)

    return ret


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.model = None
        self.button_opt = None

        self.master.title("シフト作成アプリ")

        self.notebook = ttk.Notebook(self.master)

        self.menubar = tk.Menu()
        self.master.config(menu=self.menubar)

        self.menu_file = tk.Menu()
        self.menubar.add_cascade(label="ファイル", menu=self.menu_file)
        self.menu_file.add_command(label="ファイル選択", command=self.initModel)

        self.tab_desire = tk.Frame(self.notebook)
        self.tab_param = tk.Frame(self.notebook)
        self.tab_result = tk.Frame(self.notebook)

        # tab_desire
        self.shift_lim_var_list = []
        self.workday_list = []

        # tab_param
        self.var_0 = tk.IntVar(value=50)
        self.var_1 = tk.IntVar(value=50)
        self.var_2 = tk.IntVar(value=50)
        self.var_3 = tk.IntVar(value=50)
        self.var_4 = tk.IntVar(value=100)

        self.C_des = 0.6
        self.C_seq = 3
        self.C_lim = 3
        self.C_wrk = 0.1

        self.par_sc_0 = tk.Scale(self.tab_param, variable=self.var_0, orient="horizontal", from_=0, to=100, length=500)
        self.par_sc_1 = tk.Scale(self.tab_param, variable=self.var_1, orient="horizontal", from_=0, to=100, length=500)
        self.par_sc_2 = tk.Scale(self.tab_param, variable=self.var_2, orient="horizontal", from_=0, to=100, length=500)
        self.par_sc_3 = tk.Scale(self.tab_param, variable=self.var_3, orient="horizontal", from_=0, to=100, length=500)
        self.par_sc_4 = tk.Scale(self.tab_param, variable=self.var_4, orient="horizontal", from_=1, to=1000, length=500)

        # tab_result
        self.tr_res = None

    def initModel(self):
        self.model = shift_SA.ShiftAnneal()
        self.model.setCSV(selectCSV())

        self.notebook.add(self.tab_desire, text="　出勤希望　")
        self.notebook.add(self.tab_param, text="　パラメータ　")
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        self.button_opt = tk.Button(text="▶ 【実行】", width=10, height=1, bd=0, fg="green", command=self.optimize)
        self.button_opt.place(x=900, y=10, anchor=tk.NW)

        self.show_desire()
        self.show_param()

    # tab_desireの表示（更新）
    def show_desire(self, fw=1, fh=2, pad=1):
        font_width = fw
        font_height = fh
        pad = pad

        f_const = tk.Frame(self.tab_desire, padx=10, pady=10)
        f_const.grid(row=0, column=0, padx=10, pady=10)
        for i in range(1, self.model.DAY + 1):
            lb_date = tk.Label(f_const, text=str(int((i + 1) / 2)), width=font_width, height=font_height)
            lb_date.grid(row=0, column=i, padx=pad)
        lb_lab = tk.Label(f_const, text="希望", width=6, height=font_height)
        lb_lab.grid(row=0, column=self.model.DAY + 1)
        const = self.model.const
        for r1 in range(self.model.MANPOWER):
            c_list = const[r1]
            lb_name = tk.Label(f_const, text=self.model.NAME[r1], width=len(self.model.NAME[r1]) + 1,
                               height=font_height)
            lb_name.grid(row=r1 + 1, column=0, padx=pad)
            for r2 in range(self.model.DAY):
                point = c_list[r2]
                lb_const = tk.Label(f_const, text=str(point), width=font_width, height=font_height)
                lb_const.grid(row=r1 + 1, column=r2 + 1, padx=pad)
            # lb_wd = tk.Label(f_const, text=self.model.WORKDAY[r1], width=font_width, height=font_height)
            # lb_wd.grid(row=r1 + 1, column=self.model.DAY + 1, padx=pad)

            workday_var = tk.IntVar(value=self.model.WORKDAY[r1])
            self.workday_list.append(workday_var)
            workday_sb = tk.Spinbox(f_const, width=font_width + 3, textvariable=workday_var, from_=0, to=31,
                                    increment=1)
            workday_sb.grid(row=r1 + 1, column=self.model.DAY + 1, padx=pad)

        for r3 in range(self.model.DAY):
            shift_lim_var = tk.IntVar(value=1)
            self.shift_lim_var_list.append(shift_lim_var)
            shift_lim_bt = tk.Button(f_const, width=font_width - 1, textvariable=shift_lim_var,
                                     command=self.change_shift_lim(r3), padx=pad - 1)
            shift_lim_bt.grid(row=self.model.MANPOWER + 1, column=r3 + 1, padx=pad - 1)

    def change_shift_lim(self, var_id):
        def ret():
            var = self.shift_lim_var_list[var_id]
            if var.get() == 2:
                var.set(0)
            else:
                var.set(var.get() + 1)

        return ret

    # tab_showの表示（更新）
    def show_param(self):
        param_list = ["出勤希望度", "昼夜連勤", "人数過不足", "勤務日数", "サンプリング回数"]

        par_lb_0 = tk.Label(self.tab_param, padx=10, pady=10, text=param_list[0])
        par_lb_1 = tk.Label(self.tab_param, padx=10, pady=10, text=param_list[1])
        par_lb_2 = tk.Label(self.tab_param, padx=10, pady=10, text=param_list[2])
        par_lb_3 = tk.Label(self.tab_param, padx=10, pady=10, text=param_list[3])
        par_lb_4 = tk.Label(self.tab_param, padx=10, pady=10, text=param_list[4])

        par_lb_0.grid(row=0, column=0)
        par_lb_1.grid(row=1, column=0)
        par_lb_2.grid(row=2, column=0)
        par_lb_3.grid(row=3, column=0)
        par_lb_4.grid(row=4, column=0)

        self.par_sc_0.grid(row=0, column=1)
        self.par_sc_1.grid(row=1, column=1)
        self.par_sc_2.grid(row=2, column=1)
        self.par_sc_3.grid(row=3, column=1)
        self.par_sc_4.grid(row=4, column=1)

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
        ss = []
        wd = []
        for var in self.shift_lim_var_list:
            ss.append(int(var.get()))
        for var2 in self.workday_list:
            wd.append(int(var2.get()))
        self.model.setParam(des_const=int(self.var_0.get() * self.C_des),
                            seq_const=int(self.var_1.get() * self.C_seq),
                            shift_size_const=int(self.var_2.get() * self.C_lim),
                            workday_const=int(self.var_3.get() * self.C_wrk),
                            shift_size_limit=ss,
                            workday=wd,
                            num_reads=self.var_4.get())
        self.model.setConst()
        self.model.sample()
        self.notebook.add(self.tab_result, text="　結果リスト　")
        self.show_result()
        self.notebook.select(self.tab_result)


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
