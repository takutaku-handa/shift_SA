import csv
import numpy as np

import dimod
from neal import SimulatedAnnealingSampler

from dwave.system.composites import EmbeddingComposite
from dwave.system.samplers import DWaveSampler


class ShiftAnneal:
    def __init__(self):
        self.const = []

        self.MANPOWER = 0
        self.DAY = 0
        self.DESIRE_CONST = 0
        self.SEQ_CONST = 0
        self.SHIFT_SIZE_CONST = 0
        self.SHIFT_SIZE_LIMIT = 0
        self.WORKDAY = []
        self.WORKDAY_CONST = 0
        self.NUM_READS = 0

        self.liner = {}
        self.quadratic = {}
        self.sample_set = None
        self.order = None

    def setCSV(self, filename):
        with open(filename, encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            for row in reader:
                self.const.append([int(i) for i in row])

    def setParam(self):
        self.MANPOWER = 8
        self.DAY = 60
        self.DESIRE_CONST = 9
        self.SEQ_CONST = 500
        self.SHIFT_SIZE_CONST = 5000
        self.SHIFT_SIZE_LIMIT = 1
        self.WORKDAY = [7, 7, 7, 7, 7, 7, 7, 7]
        self.WORKDAY_CONST = 10
        self.NUM_READS = 100

    def setConst(self):
        # １次
        for i in range(self.MANPOWER):
            for j in range(self.DAY):
                liner_const = (self.const[i][j] ^ self.DESIRE_CONST)  # 出勤希望度による
                liner_const += - (2 * self.SHIFT_SIZE_LIMIT) * self.SHIFT_SIZE_CONST  # １シフトに入る人数制約による
                # liner_const += - (2 * self.WORKDAY[i]) * self.WORKDAY_CONST  # 勤務日数希望による
                try:
                    self.liner["x_{0}_{1}".format(i, j)] += liner_const
                except KeyError:
                    self.liner["x_{0}_{1}".format(i, j)] = liner_const

        # ２次
        # 昼夜連勤の禁止による
        for i in range(self.MANPOWER):
            for j in range(int(self.DAY / 2)):
                j *= 2
                try:
                    self.quadratic[("x_{0}_{1}".format(i, j), "x_{0}_{1}".format(i, j + 1))] += self.SEQ_CONST
                except KeyError:
                    self.quadratic[("x_{0}_{1}".format(i, j), "x_{0}_{1}".format(i, j + 1))] = self.SEQ_CONST

        # １シフトに入る人数制約による
        for i1 in range(self.MANPOWER):
            for i2 in range(self.MANPOWER):
                if i1 == i2:
                    for j in range(self.DAY):
                        try:
                            self.quadratic[
                                ("x_{0}_{1}".format(i1, j), "x_{0}_{1}".format(i2, j))] += 1 * self.SHIFT_SIZE_CONST
                        except KeyError:
                            self.quadratic[
                                ("x_{0}_{1}".format(i1, j), "x_{0}_{1}".format(i2, j))] = 1 * self.SHIFT_SIZE_CONST
                else:
                    for j in range(self.DAY):
                        try:
                            self.quadratic[
                                ("x_{0}_{1}".format(i1, j), "x_{0}_{1}".format(i2, j))] += 2 * self.SHIFT_SIZE_CONST
                        except KeyError:
                            self.quadratic[
                                ("x_{0}_{1}".format(i1, j), "x_{0}_{1}".format(i2, j))] = 2 * self.SHIFT_SIZE_CONST

        # 勤務日数希望による(いったん無視する)
        """
        for j1 in range(self.DAY):
            for j2 in range(self.DAY):
                if j1 == j2:
                    for i in range(self.MANPOWER):
                        try:
                            self.quadratic[
                                ("x_{0}_{1}".format(i, j1), "x_{0}_{1}".format(i, j2))] += 1 * self.WORKDAY_CONST
                        except KeyError:
                            self.quadratic[
                                ("x_{0}_{1}".format(i, j1), "x_{0}_{1}".format(i, j2))] = 1 * self.WORKDAY_CONST
                else:
                    for i in range(self.MANPOWER):
                        try:
                            self.quadratic[
                                ("x_{0}_{1}".format(i, j1), "x_{0}_{1}".format(i, j2))] += 2 * self.WORKDAY_CONST
                        except KeyError:
                            self.quadratic[
                                ("x_{0}_{1}".format(i, j1), "x_{0}_{1}".format(i, j2))] = 2 * self.WORKDAY_CONST
        """

    def sample(self):
        # BQMモデルに変換
        bqm = dimod.BinaryQuadraticModel(self.liner, self.quadratic, 0, "BINARY")
        # サンプリング
        SA_sampler = SimulatedAnnealingSampler()
        self.sample_set = SA_sampler.sample(bqm, num_reads=self.NUM_READS)
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

    def getPenalty(self):
        pass

    def calcPenalty(self):
        pass

    def getDetail(self):
        pass
