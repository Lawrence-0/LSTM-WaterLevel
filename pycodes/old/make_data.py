import pycodes.mlit_obsv as mlit_obsv
import pycodes.dias_tools as dias_tools
import pandas

def make_data(obsvId, mode):
    assert mode == 'w' or mode == 'r'
    assert len(mlit_obsv._obsv_data(obsvId, '20100101', '20191231')) == 87648
    river = mlit_obsv._obsv_detail(obsvId)[2]
    obsvRain = mlit_obsv._search_by_water_system_type(river, 'rain')
    obsvWater = mlit_obsv._search_by_water_system_type(river, 'water')
    obsvWater.remove(obsvId)
    trainingData = []
    names = []
    names.append(obsvId)
    datumW = mlit_obsv._obsv_data(obsvId, '20100101', '20191231')
    for index in range(len(datumW)):
        if datumW[index] == float("-inf") or datumW[index] == float("inf") or datumW[index] == float("nan"):
            if index != 0:
                datumW[index] = datumW[index - 1]
            else:
                print('no initial water level', obsvId)
                for index0 in range(len(datumW)):
                    if datumW[index0] != float("-inf") and datumW[index0] != float("inf") and datumW[index0] != float("nan"):
                        break
                for index1 in range(index0 - 1, -1, -1):
                    datumW[index1] = datumW[index1 + 1]
    trainingData.append(datumW)
    if mode == 'w':
        for w in obsvWater:
            if len(mlit_obsv._obsv_data(w, '20100101', '20191231')) == 87648:
                names.append(w)
                datumW = mlit_obsv._obsv_data(w, '20100101', '20191231')
                for index in range(len(datumW)):
                    if datumW[index] == float("-inf") or datumW[index] == float("inf") or datumW[index] == float("nan"):
                        if index != 0:
                            datumW[index] = datumW[index - 1]
                        else:
                            print('no initial water level', w)
                            for index0 in range(len(datumW)):
                                if datumW[index0] != float("-inf") and datumW[index0] != float("inf") and datumW[index0] != float("nan"):
                                    break
                            for index1 in range(index0 - 1, -1, -1):
                                datumW[index1] = datumW[index1 + 1]
                trainingData.append(datumW)
    if mode == 'r':
        for r in obsvRain:
            if len(mlit_obsv._obsv_data(r, '20100101', '20191231')) == 87648:
                names.append(r)
                datumR = mlit_obsv._obsv_data(r, '20100101', '20191231')
                for index in range(len(datumR)):
                    if datumR[index] == float("-inf") or datumR[index] == float("inf") or datumR[index] == float("nan"):
                        datumR[index] = float(0)
                trainingData.append(datumR)
    trainingData = pandas.DataFrame(trainingData).T
    trainingData.columns = names
    return trainingData

def make_dias(obsvId):
    assert len(mlit_obsv._obsv_data(obsvId, '20000101', '20091231')) == 87672
    posXY = dias_tools.findPos(obsvId)
    trainingData = []
    names = []
    names.append(obsvId)
    datumW = mlit_obsv._obsv_data(obsvId, '20000101', '20091231')
    for index in range(len(datumW)):
        if datumW[index] == float("-inf") or datumW[index] == float("inf") or datumW[index] == float("nan"):
            if index != 0:
                datumW[index] = datumW[index - 1]
            else:
                print('no initial water level', obsvId)
                for index0 in range(len(datumW)):
                    if datumW[index0] != float("-inf") and datumW[index0] != float("inf") and datumW[index0] != float("nan"):
                        break
                for index1 in range(index0 - 1, -1, -1):
                    datumW[index1] = datumW[index1 + 1]
    trainingData.append(datumW)
    for pos in posXY:
        if len(dias_tools._dias_data(pos[0], pos[1], '20000101', '20091231')) == 87672:
            names.append('X' + str(pos[0]) + '_Y' + str(pos[1]))
            trainingData.append(dias_tools._dias_data(pos[0], pos[1], '20000101', '20091231'))
    trainingData = pandas.DataFrame(trainingData).T
    trainingData.columns = names
    return trainingData