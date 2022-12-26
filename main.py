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

MANPOWER = 8
DAY = 31

if __name__ == "__main__":
    binary = np.empty((MANPOWER, DAY))

    CONST_1 = []
    with open('shift.csv', encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            CONST_1.append([int(i) for i in row])

    dict_for_bqm = {}
    for i in range(len(CONST_1)):
        for j in range(len(CONST_1[i])):
            dict_for_bqm["x_{0}_{1}".format(i, j)] = CONST_1[i][j]

    bqm = dimod.BinaryQuadraticModel(dict_for_bqm, {}, 0, "BINARY")

    SA_sampler = SimulatedAnnealingSampler()
    sample_set = SA_sampler.sample(bqm, num_reads=100)
    order = np.argsort(sample_set.record["energy"])
    print(sample_set.record[order][:10])
