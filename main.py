# （課題）「シフトの制約をBQMに落とし込む」

# ＜ハード制約＞出勤希望・連勤上限・勤務日数上限・１シフトに入る人数 = 1or2
# 出勤希望度：出勤したくない度合いに比例した係数をバイナリ変数に乗ずる
# 連勤上限１：昼夜の連勤は普通に隣接するバイナリ変数の平方に係数を乗ずる
# 連勤上限２：その他の連勤に関する制約は、ソフト制約にゆだねる
# 勤務日数上限：（バイナリ変数の横の和 - 上限）に係数を乗ずる
# １シフトに入る人数：（バイナリ変数の縦の和 - 1or2）^2 に係数を乗ずる

# ＜ソフト制約＞ハード制約を満たしたシフトの中で、ソフト制約のペナルティ値のバランスを見て人間が恣意的に選ぶというのが無難か？

import csv
import time
import numpy as np

import dimod
from neal import SimulatedAnnealingSampler

if __name__ == "__main__":

    # csvファイルから出勤希望度の制約を入力
    CONST = []
    with open('shift.csv', encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            CONST.append([int(i) for i in row])

    # パラメータ
    MANPOWER = 8
    DAY = 60

    DESIRE_CONST = 100
    SEQ_CONST = 500
    SHIFT_SIZE_CONST = 500
    SHIFT_SIZE_LIMIT = 1
    WORKDAY = [7, 7, 7, 7, 7, 7, 7, 7]
    WORKDAY_CONST = 10

    NUM_READS = 100

    # １次
    liner = {}
    for i in range(MANPOWER):
        for j in range(DAY):
            liner_const = CONST[i][j] * DESIRE_CONST  # 出勤希望度による
            liner_const += - (2 * SHIFT_SIZE_LIMIT) * SHIFT_SIZE_CONST  # １シフトに入る人数制約による
            liner_const += - (2 * WORKDAY[i]) * WORKDAY_CONST  # 勤務日数希望による
            try:
                liner["x_{0}_{1}".format(i, j)] += liner_const
            except KeyError:
                liner["x_{0}_{1}".format(i, j)] = liner_const

    # ２次
    quadratic = {}

    # 昼夜連勤の禁止による
    for i in range(MANPOWER):
        for j in range(int(DAY / 2)):
            j *= 2
            try:
                quadratic[("x_{0}_{1}".format(i, j), "x_{0}_{1}".format(i, j + 1))] += SEQ_CONST
            except KeyError:
                quadratic[("x_{0}_{1}".format(i, j), "x_{0}_{1}".format(i, j + 1))] = SEQ_CONST

    # １シフトに入る人数制約による
    for i1 in range(MANPOWER):
        for i2 in range(MANPOWER):
            if i1 == i2:
                for j in range(DAY):
                    try:
                        quadratic[("x_{0}_{1}".format(i1, j), "x_{0}_{1}".format(i2, j))] += 1 * SHIFT_SIZE_CONST
                    except KeyError:
                        quadratic[("x_{0}_{1}".format(i1, j), "x_{0}_{1}".format(i2, j))] = 1 * SHIFT_SIZE_CONST
            else:
                for j in range(DAY):
                    try:
                        quadratic[("x_{0}_{1}".format(i1, j), "x_{0}_{1}".format(i2, j))] += 2 * SHIFT_SIZE_CONST
                    except KeyError:
                        quadratic[("x_{0}_{1}".format(i1, j), "x_{0}_{1}".format(i2, j))] = 2 * SHIFT_SIZE_CONST

    # 勤務日数希望による
    for j1 in range(DAY):
        for j2 in range(DAY):
            if j1 == j2:
                for i in range(MANPOWER):
                    try:
                        quadratic[("x_{0}_{1}".format(i, j1), "x_{0}_{1}".format(i, j2))] += 1 * WORKDAY_CONST
                    except KeyError:
                        quadratic[("x_{0}_{1}".format(i, j1), "x_{0}_{1}".format(i, j2))] = 1 * WORKDAY_CONST
            else:
                for i in range(MANPOWER):
                    try:
                        quadratic[("x_{0}_{1}".format(i, j1), "x_{0}_{1}".format(i, j2))] += 2 * WORKDAY_CONST
                    except KeyError:
                        quadratic[("x_{0}_{1}".format(i, j1), "x_{0}_{1}".format(i, j2))] = 2 * WORKDAY_CONST

    # BQMモデルに変換
    bqm = dimod.BinaryQuadraticModel(liner, quadratic, 0, "BINARY")

    # サンプリング
    SA_sampler = SimulatedAnnealingSampler()
    start_time = time.time()
    sample_set = SA_sampler.sample(bqm, num_reads=NUM_READS)
    print("SAの場合: {0:.4}秒 ({1}回試行)".format(time.time() - start_time, NUM_READS))
    order = np.argsort(sample_set.record["energy"])

    # csvファイルへの出力
    with open("result.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([d for d in range(61)])
        for m in range(MANPOWER):
            res_list = ["M{0}".format(m + 1)]
            res_list.extend(sample_set.record[order][0][0][60 * m: 60 * m + 60])
            writer.writerow(res_list)
