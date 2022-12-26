# （課題）「シフトの制約をBQMに落とし込む」

# ＜ハード制約＞出勤希望・連勤上限・勤務日数上限・１シフトに入る人数 = 1or2
# 出勤希望度：出勤したくない度合いに比例した係数をバイナリ変数に乗ずる
# 連勤上限１：昼夜の連勤は普通に隣接するバイナリ変数の平方に係数を乗ずる
# 連勤上限２：その他の連勤に関する制約は、ソフト制約にゆだねる
# 勤務日数上限：（バイナリ変数の横の和 - 上限）に係数を乗ずる
# １シフトに入る人数：（バイナリ変数の縦の和 - 1or2）^2 に係数を乗ずる

# ＜ソフト制約＞ハード制約を満たしたシフトの中で、ソフト制約のペナルティ値のバランスを見て人間が恣意的に選ぶというのが無難か？


import time
import numpy as np

import dimod
from neal import SimulatedAnnealingSampler

if __name__ == "__main__":
    """  BinaryQuadraticModel(linear, quadratic, offset, vartype  """
    bqm = dimod.BinaryQuadraticModel(
        {'cupcakes_0,0': -2.0, 'cupcakes_0,1': -2.0, 'cupcakes_1,3': 0.0, 'cupcakes_1,2': -2.0,
         'smoothie_0,2': -2.0, 'smoothie_0,3': 0.0, 'smoothie_0,1': -2.0, 'smoothie_0,0': -2.0,
         'lasagna_0,1': -2.0, 'lasagna_0,2': 0.0, 'lasagna_0,0': -2.0},
        {('cupcakes_0,1', 'cupcakes_0,0'): 4.0, ('cupcakes_1,2', 'cupcakes_0,1'): 4.0,
         ('cupcakes_1,2', 'cupcakes_1,3'): 4.0, ('smoothie_0,2', 'cupcakes_0,1'): 4.0,
         ('smoothie_0,3', 'smoothie_0,2'): 4.0, ('smoothie_0,1', 'cupcakes_0,0'): 4.0,
         ('smoothie_0,1', 'cupcakes_0,1'): 8.0, ('smoothie_0,1', 'smoothie_0,2'): 4.0,
         ('smoothie_0,1', 'smoothie_0,3'): 4.0, ('smoothie_0,0', 'cupcakes_0,0'): 8.0,
         ('smoothie_0,0', 'smoothie_0,2'): 4.0, ('smoothie_0,0', 'smoothie_0,3'): 4.0,
         ('smoothie_0,0', 'smoothie_0,1'): 4.0, ('lasagna_0,1', 'cupcakes_1,2'): 4.0,
         ('lasagna_0,2', 'cupcakes_1,3'): 4.0, ('lasagna_0,2', 'cupcakes_1,2'): 8.0,
         ('lasagna_0,2', 'lasagna_0,1'): 4.0, ('lasagna_0,0', 'lasagna_0,1'): 4.0,
         ('lasagna_0,0', 'lasagna_0,2'): 4.0}, 8.0, 'BINARY')

    SA_sampler = SimulatedAnnealingSampler()
    sample_set = SA_sampler.sample(bqm, num_reads=100)
    # SAサンプラーだと、num_ocが全部１になってしまう。(この問題は恐らくソルバー内部の問題で、根本的解決は不可能）

    # 代わりに、エネルギーが小さい順に取り出し、同じのが出たことある奴なら無視するという方法なら採れる。
    order = np.argsort(sample_set.record["energy"])
    print(sample_set.record[order][:10])
