import csv
import numpy as np
import pycodes.mlit_obsv as mlit_obsv
import re
import sqlite3

reader = csv.reader(open('./models/topo_essp20.csv', 'r'))

dictPos = {}

reader = [row for row in reader][1:]

for pos in reader:
    dictPos[(float(pos[2]), float(pos[3]))] = (int(pos[0]), int(pos[1]))

def getPos(obsvPos):
    distance = 1
    for (lgtd, lttd) in dictPos:
        if distance > pow(pow((obsvPos[0] - lgtd), 2) + pow((obsvPos[1] - lttd), 2), 1/2):
            distance = pow(pow((obsvPos[0] - lgtd), 2) + pow((obsvPos[1] - lttd), 2), 1/2)
            getPos = dictPos[(lgtd, lttd)]
    return getPos

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

def findPos(obsvId):
    listPos = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    center = getPos(obsvPos(obsvId))
    listPos = [(pos[0] + center[0], pos[1] + center[1]) for pos in listPos]
    result = []
    for pos in listPos:
        if pos[0] <= 190 and pos[0] >= 0 and pos[1] <= 154 and pos[1] >= 0:
            result.append(pos)
    return result

def _dias_data(posX: int, posY: int, beginDate = None, endDate = None):
    tblName = 'X' + str(posX) + '_Y' + str(posY)
    if beginDate == None:
        db_cnct = sqlite3.connect('./databases/DIASpastm001.db')
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
        db_cnct = sqlite3.connect('./databases/DIASpastm001.db')
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