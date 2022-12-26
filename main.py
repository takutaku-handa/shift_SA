# （課題）「シフトの制約をBQMに落とし込む」

# ＜ハード制約＞出勤希望・連勤上限・勤務日数上限・１シフトに入る人数 = 1or2
# 出勤希望度：出勤したくない度合いに比例した係数をバイナリ変数に乗ずる
# 連勤上限１：昼夜の連勤は普通に隣接するバイナリ変数の平方に係数を乗ずる
# 連勤上限２：その他の連勤に関する制約は、ソフト制約にゆだねる
# 勤務日数上限：（バイナリ変数の横の和 - 上限）に係数を乗ずる
# １シフトに入る人数：（バイナリ変数の縦の和 - 1or2）^2 に係数を乗ずる

# ＜ソフト制約＞ハード制約を満たしたシフトの中で、ソフト制約のペナルティ値のバランスを見て人間が恣意的に選ぶというのが無難か？

import csv
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
    MANPOWER = len(CONST)
    DAY = len(CONST[0])
    SEQ_CONST = 100
    ONE_DAY_CONST = 10

    # １次
    liner = {}

    for i1 in range(MANPOWER):
        for j in range(DAY):
            liner["x_{0}_{1}".format(i1, j)] = CONST[i1][j] - 2 * ONE_DAY_CONST  # -2は１シフトに入る人数制約による

    # ２次
    quadratic = {}
    for i in range(MANPOWER):
        for j in range(int(DAY / 2)):
            j *= 2
            quadratic[("x_{0}_{1}".format(i, j), "x_{0}_{1}".format(i, j + 1))] = SEQ_CONST

    for i1 in range(MANPOWER):
        for i2 in range(MANPOWER):
            if i1 == i2:
                for j in range(DAY):
                    quadratic[("x_{0}_{1}".format(i1, j), "x_{0}_{1}".format(i1, j))] = 1 * ONE_DAY_CONST
            else:
                for j in range(DAY):
                    quadratic[("x_{0}_{1}".format(i1, j), "x_{0}_{1}".format(i2, j))] = 2 * ONE_DAY_CONST

    # BQMモデルに変換
    bqm = dimod.BinaryQuadraticModel(liner, quadratic, 0, "BINARY")

    # サンプリング
    SA_sampler = SimulatedAnnealingSampler()
    sample_set = SA_sampler.sample(bqm, num_reads=100)
    order = np.argsort(sample_set.record["energy"])

    # 表示
    for m in range(MANPOWER):
        print(sample_set.record[order][0][0][60 * m: 60 * m + 60][:30])
