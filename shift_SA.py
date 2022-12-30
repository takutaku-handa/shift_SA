import csv
import math

import numpy as np

import dimod
from neal import SimulatedAnnealingSampler

from dwave.system.composites import EmbeddingComposite
from dwave.system.samplers import DWaveSampler


class ShiftAnneal:
    def __init__(self):
        self.NAME = ["A", "B", "C", "D", "E", "F", "G", "H"]
        self.MANPOWER = 0
        self.DAY = 0
        self.DESIRE_CONST = 0
        self.SEQ_CONST = 0
        self.SHIFT_SIZE_CONST = 0
        self.SHIFT_SIZE_LIMIT = 0
        self.WORKDAY = []
        self.WORKDAY_CONST = 0
        self.NUM_READS = 0

        self.const = []
        self.liner = {}
        self.quadratic = {}
        self.sample_set = None
        self.order = None

    def getID(self, m, d):
        return self.DAY * m + d + 100000000

    def setCSV(self, filename):
        with open(filename, encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            for row in reader:
                self.const.append([int(i) for i in row])

    def setParam(self):
        self.MANPOWER = 8
        self.DAY = 60

        self.DESIRE_CONST = 30
        self.SEQ_CONST = 150
        self.SHIFT_SIZE_CONST = 150
        self.SHIFT_SIZE_LIMIT = 1
        self.WORKDAY = [7, 7, 7, 7, 7, 7, 7, 7]
        self.WORKDAY_CONST = 5

        self.NUM_READS = 100

    def setConst(self):
        # １次
        for i in range(self.MANPOWER):
            for j in range(self.DAY):
                liner_const = (self.const[i][j] * self.DESIRE_CONST)  # 出勤希望度による
                liner_const += - (2 * self.SHIFT_SIZE_LIMIT) * self.SHIFT_SIZE_CONST  # １シフトに入る人数制約による
                liner_const += - (2 * self.WORKDAY[i]) * self.WORKDAY_CONST  # 勤務日数希望による
                key = "x_{0}".format(self.getID(i, j))
                try:
                    self.liner[key] += liner_const
                except KeyError:
                    self.liner[key] = liner_const

        # ２次
        # 昼夜連勤の禁止による
        for i in range(self.MANPOWER):
            for j in range(int(self.DAY / 2)):
                j *= 2
                key = ("x_{0}".format(self.getID(i, j)), "x_{0}".format(self.getID(i, j + 1)))
                try:
                    self.quadratic[key] += self.SEQ_CONST
                except KeyError:
                    self.quadratic[key] = self.SEQ_CONST

        # １シフトに入る人数制約による
        for i1 in range(self.MANPOWER):
            for i2 in range(self.MANPOWER):
                if i1 == i2:
                    for j in range(self.DAY):
                        key = ("x_{0}".format(self.getID(i1, j)), "x_{0}".format(self.getID(i2, j)))
                        try:
                            self.quadratic[key] += 1 * self.SHIFT_SIZE_CONST
                        except KeyError:
                            self.quadratic[key] = 1 * self.SHIFT_SIZE_CONST
                else:
                    for j in range(self.DAY):
                        key = ("x_{0}".format(self.getID(i1, j)), "x_{0}".format(self.getID(i2, j)))
                        try:
                            self.quadratic[key] += 2 * self.SHIFT_SIZE_CONST
                        except KeyError:
                            self.quadratic[key] = 2 * self.SHIFT_SIZE_CONST

        # 勤務日数希望による
        for j1 in range(self.DAY):
            for j2 in range(self.DAY):
                if j1 == j2:
                    for i in range(self.MANPOWER):
                        key = ("x_{0}".format(self.getID(i, j1)), "x_{0}".format(self.getID(i, j2)))
                        try:
                            self.quadratic[key] += 1 * self.WORKDAY_CONST
                        except KeyError:
                            self.quadratic[key] = 1 * self.WORKDAY_CONST
                else:
                    for i in range(self.MANPOWER):
                        key = ("x_{0}".format(self.getID(i, j1)), "x_{0}".format(self.getID(i, j2)))
                        try:
                            self.quadratic[key] += 2 * self.WORKDAY_CONST
                        except KeyError:
                            self.quadratic[key] = 2 * self.WORKDAY_CONST

    def sample(self):
        # BQMモデルに変換
        bqm = dimod.BinaryQuadraticModel(self.liner, self.quadratic, 0, "BINARY")
        # サンプリング
        SA_sampler = SimulatedAnnealingSampler()
        self.sample_set = SA_sampler.sample(bqm, num_reads=self.NUM_READS, beta_schedule_type="geometric",
                                            num_sweeps_per_beta=100, num_sweeps=10000)
        self.order = np.argsort(self.sample_set.record["energy"])

    # 面倒なので、量子アニーラはいったん考えない。
    """
    def Qsample(self):
        bqm = dimod.BinaryQuadraticModel(self.liner, self.quadratic, 0, "BINARY")
        # 量子アニーラによる解
        Qu_sampler = EmbeddingComposite(DWaveSampler())
        self.sample_set = Qu_sampler.sample(bqm,
                                            chain_strength=2,
                                            num_reads=self.NUM_READS,
                                            label='shift_scheduling({0}×{1})'.format(self.MANPOWER, self.DAY))
        self.order = np.argsort(self.sample_set.record["energy"])
    """

    def outputCSV(self):
        pass

    def getPenalty(self, sample):
        # ペナルティ：出勤希望度違反数、昼夜連勤数、人数超過日数、人数不足日数、勤務日のばらつき、勤務日数のばらつき
        pena_desire = [0, 0, 0, 0]
        pena_seq = 0
        pena_over = 0
        pena_lack = 0
        pena_dist = 0
        pena_workday = 0

        count_horizontal = [0 for i in range(self.MANPOWER)]
        count_vertical = [0 for i in range(self.DAY)]
        max_seq_work = 0
        max_seq_off = 0

        index = 0
        for m in range(self.MANPOWER):
            work_date = []
            date = 1
            seq_work = 0
            seq_off = 0
            for d in range(self.DAY):
                s = sample[index]
                if s:
                    work_date.append(date)
                    seq_work += 1
                    seq_off = 0
                else:
                    seq_work = 0
                    seq_off += 1
                if seq_work > max_seq_work:
                    max_seq_work = seq_work
                if seq_off > max_seq_off:
                    max_seq_off = seq_off
                date += 1
                pena_desire[self.const[m][d]] += s
                if (d % self.DAY) % 2 == 0 and d < self.DAY and s * sample[index + 1]:
                    pena_seq += 1
                count_horizontal[m] += s
                count_vertical[d] += s
                index += 1
            pena_dist += math.sqrt(np.var(work_date))

        for cv in count_vertical:
            if cv > 1:
                pena_over += 1
            if cv < 1:
                pena_lack += 1

        for m in range(self.MANPOWER):
            gap = (self.WORKDAY[m] - count_horizontal[m]) * (self.WORKDAY[m] - count_horizontal[m])
            pena_workday += gap

        ret = [("0", pena_desire[0]), ("1", pena_desire[1]), ("2", pena_desire[2]), ("3", pena_desire[3]),
               ("昼夜連勤", pena_seq), ("人数超過", pena_over), ("人数不足", pena_lack),
               ("ばらけ具合", int(pena_dist)), ("勤務日数希望違反", pena_workday),
               ("最大連勤", max_seq_work), ("最大連休", max_seq_off)]

        return ret

    def calcPenalty(self):
        pass

    def getDetail(self):
        pass
