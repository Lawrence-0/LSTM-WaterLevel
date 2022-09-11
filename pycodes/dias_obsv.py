import csv
import numpy as np
import pycodes.mlit_obsv as mlit_obsv
import re
import sqlite3

# japan position: 122°55′57″E - 153°59′12″E , 20°25′31″N - 45°33′26″N

def _dias_data1(posX: int, posY: int, beginDate = None, endDate = None):
    tblName = 'X' + str(posX) + '_Y' + str(posY)
    if beginDate == None:
        db_cnct = sqlite3.connect('./databases/DIASfuture.db')
        cursor = db_cnct.cursor()
        cursor.execute("SELECT * FROM %s" %tblName)
        data = cursor.fetchall()
        diasData = []
        for datum in data:
            hour = 1
            for x in datum[1:]:
                diasData.append((datum[0] * 100 + hour, x))
                hour += 1
    else:
        beginDate = int(beginDate)
        endDate = int(endDate)
        db_cnct = sqlite3.connect('./databases/DIASfuture.db')
        cursor = db_cnct.cursor()
        cursor.execute("SELECT * FROM %s" %tblName)
        data = cursor.fetchall()
        diasData = []
        for datum in data:
            if datum[0] >= beginDate and datum[0] <= endDate:
                hour = 1
                for x in datum[1:]:
                    diasData.append((datum[0] * 100 + hour, x))
                    hour += 1
    diasData.sort()
    diasData = [x[1] for x in diasData]
    return diasData

class posGrid(object):
    def __init__(self, lgtd1_lttd1, lgtd2_lttd2, lgtd3_lttd3, lgtd4_lttd4):
        assert type(lgtd1_lttd1) == tuple and len(lgtd1_lttd1) == 2 and type(lgtd1_lttd1[0]) == float and type(lgtd1_lttd1[1]) == float and lgtd1_lttd1[0] >= 0 and lgtd1_lttd1[0] <= 180 and lgtd1_lttd1[1] >= 0 and lgtd1_lttd1[1] <= 90
        assert type(lgtd2_lttd2) == tuple and len(lgtd2_lttd2) == 2 and type(lgtd2_lttd2[0]) == float and type(lgtd2_lttd2[1]) == float and lgtd2_lttd2[0] >= 0 and lgtd2_lttd2[0] <= 180 and lgtd2_lttd2[1] >= 0 and lgtd2_lttd2[1] <= 90
        assert type(lgtd3_lttd3) == tuple and len(lgtd3_lttd3) == 2 and type(lgtd3_lttd3[0]) == float and type(lgtd3_lttd3[1]) == float and lgtd3_lttd3[0] >= 0 and lgtd3_lttd3[0] <= 180 and lgtd3_lttd3[1] >= 0 and lgtd3_lttd3[1] <= 90
        assert type(lgtd4_lttd4) == tuple and len(lgtd4_lttd4) == 2 and type(lgtd4_lttd4[0]) == float and type(lgtd4_lttd4[1]) == float and lgtd4_lttd4[0] >= 0 and lgtd4_lttd4[0] <= 180 and lgtd4_lttd4[1] >= 0 and lgtd4_lttd4[1] <= 90
        self.lgtd1 = lgtd1_lttd1[0]
        self.lttd1 = lgtd1_lttd1[1]
        self.lgtd2 = lgtd2_lttd2[0]
        self.lttd2 = lgtd2_lttd2[1]
        self.lgtd3 = lgtd3_lttd3[0]
        self.lttd3 = lgtd3_lttd3[1]
        self.lgtd4 = lgtd4_lttd4[0]
        self.lttd4 = lgtd4_lttd4[1]
    def isIn(self, lgtd, lttd):
        jg0 = ((self.lttd1 - self.lttd2) * lgtd + self.lgtd1 * self.lttd2 - self.lgtd2 * self.lttd1) >= lttd * (self.lgtd1 - self.lgtd2)
        jg1 = ((self.lttd4 - self.lttd3) * lgtd + self.lgtd4 * self.lttd3 - self.lgtd3 * self.lttd4) >= lttd * (self.lgtd4 - self.lgtd3)
        jg2 = ((self.lttd1 - self.lttd4) * lgtd + self.lgtd1 * self.lttd4 - self.lgtd4 * self.lttd1) >= lttd * (self.lgtd1 - self.lgtd4)
        jg3 = ((self.lttd2 - self.lttd3) * lgtd + self.lgtd2 * self.lttd3 - self.lgtd3 * self.lttd2) >= lttd * (self.lgtd2 - self.lgtd3)
        return (jg0 != jg1) and (jg2 != jg3)
    def distances(self, lgtd, lttd):
        assert self.isIn(lgtd, lttd)
        dstc1 = pow(pow(lgtd - self.lgtd1, 2) + pow(lttd - self.lttd1, 2), 1/2)
        dstc2 = pow(pow(lgtd - self.lgtd2, 2) + pow(lttd - self.lttd2, 2), 1/2)
        dstc3 = pow(pow(lgtd - self.lgtd3, 2) + pow(lttd - self.lttd3, 2), 1/2)
        dstc4 = pow(pow(lgtd - self.lgtd4, 2) + pow(lttd - self.lttd4, 2), 1/2)
        return (dstc1, dstc2, dstc3, dstc4)
    def getWeights(self, lgtd, lttd):
        (dstc1, dstc2, dstc3, dstc4) = self.distances(lgtd, lttd)
        if dstc1 == 0:
            return (1, 0, 0, 0)
        if dstc2 == 0:
            return (0, 1, 0, 0)
        if dstc3 == 0:
            return (0, 0, 1, 0)
        if dstc4 == 0:
            return (0, 0, 0, 1)
        else:
            weight1 = 1 / dstc1
            weight2 = 1 / dstc2
            weight3 = 1 / dstc3
            weight4 = 1 / dstc4
            return (weight1, weight2, weight3, weight4)
    def getValue(self, lgtd, lttd, values):
        assert type(values) == tuple and len(values) == 4
        (dstc1, dstc2, dstc3, dstc4) = self.distances(lgtd, lttd)
        if dstc1 == 0:
            return values[0]
        if dstc2 == 0:
            return values[1]
        if dstc3 == 0:
            return values[2]
        if dstc4 == 0:
            return values[3]
        else:
            weight1 = 1 / dstc1
            weight2 = 1 / dstc2
            weight3 = 1 / dstc3
            weight4 = 1 / dstc4
            return (weight1 * values[0] + weight2 * values[1] + weight3 * values[2] + weight4 * values[3]) / (weight1 + weight2 + weight3 + weight4)

class posMap(object):
    def __init__(self):
        reader = csv.reader(open('./models/topo_essp20.csv', 'r'))
        dictPos = {}
        reader = [row for row in reader][1:]
        for pos in reader:
            dictPos[(int(pos[0]), int(pos[1]))] = (float(pos[2]), float(pos[3]))
        dictPosGrid = {}
        for x in range(190):
            for y in range(154):
                dictPosGrid[(x, y)] = posGrid(dictPos[(x, y)], dictPos[(x + 1, y)], dictPos[(x + 1, y + 1)], dictPos[(x, y + 1)])
        self.dictPosGrid = dictPosGrid
    def findGrid(self, lgtd, lttd):
        for (x, y) in self.dictPosGrid:
            if self.dictPosGrid[(x, y)].isIn(lgtd, lttd):
                return (x, y)
    def getValue(self, lgtd, lttd, values):
        (x, y) = self.findGrid(lgtd, lttd)
        return self.dictPosGrid[(x, y)].getValue(lgtd, lttd, values)

posMap = posMap()

def obsvPos(obsvId):
    Loc = mlit_obsv._obsv_detail(obsvId)[5]
    LocN_0 = re.findall('(.*?)°.*′.*″N_',Loc)[0]
    if LocN_0 == '':
        return None
    else:
        LocN_0 = int(LocN_0)
        LocN_1 = int(re.findall('°(.*?)′.*″N_.*',Loc)[0])
        LocN_2 = int(re.findall('°.*′(.*?)″N_.*',Loc)[0])
        LocE_0 = int(re.findall('.*_(.*?)°.*′.*″',Loc)[0])
        LocE_1 = int(re.findall('.*_.*°(.*?)′.*″',Loc)[0])
        LocE_2 = int(re.findall('.*_.*°.*′(.*?)″',Loc)[0])
        LocN = LocN_0 + LocN_1 / 60 + LocN_2 /3600
        LocE = LocE_0 + LocE_1 / 60 + LocE_2 /3600
        return(LocE, LocN)

def _obsv_data(obsvId: int, beginDate = None, endDate = None):
    (LocE, LocN) = obsvPos(obsvId)
    (x, y) = posMap.findGrid(LocE, LocN)
    (weight1, weight2, weight3, weight4) = posMap.dictPosGrid[(x, y)].getWeights(LocE, LocN)
    if beginDate == None:
        diasData1 = _dias_data1(x, y)
        diasData2 = _dias_data1(x + 1, y)
        diasData3 = _dias_data1(x + 1, y + 1)
        diasData4 = _dias_data1(x, y + 1)
    else:
        diasData1 = _dias_data1(x, y, beginDate, endDate)
        diasData2 = _dias_data1(x + 1, y, beginDate, endDate)
        diasData3 = _dias_data1(x + 1, y + 1, beginDate, endDate)
        diasData4 = _dias_data1(x, y + 1, beginDate, endDate)
    diasData = []
    for h in range(len(diasData1)):
        diasData.append(weight1 * diasData1[h] + weight2 * diasData2[h] + weight3 * diasData3[h] + weight4 * diasData4[h])
    return diasData