import sqlite3
import numpy as np
import datetime
from pycodes.mlit_precipitation import _search_by_id_and_date as search_r
from pycodes.mlit_water_level import _search_by_id_and_date as search_w

waterSystems =    ['福地川',
            '新川川',
            '安波川',
            '辺野喜川',
            '漢那福地川',
            '羽地大川',
            '億首川',
            '天願川',
            '大保川',
            '大井川',
            '報得川',
            '増幌川',
            '声問川',
            '富士川',
            '大社湾',
            '蒲生川',
            '港川',
            'ジニサン川',
            '長浜川',
            '白水川',
            '有津川',
            '大浦川',
            '与那川',
            '比地川',
            '田嘉里川',
            '大保川',
            '源河川',
            '汀間川',
            '奥川',
            '億首川',
            '座津武川',
            '比謝川',
            '武見川',
            '宇嘉川',
            '佐手川',
            '佐手前川',
            '宇良川',
            '外掘田川',
            '根路銘ポンプ場',
            '天塩川',
            '渚滑川',
            '湧別川',
            '常呂川',
            '網走川',
            '留萌川',
            '石狩川',
            '尻別川',
            '後志利別川',
            '鵡川',
            '沙流川',
            '釧路川',
            '十勝川',
            '声問川',
            '勇払川',
            '標津川',
            '岩木川',
            '高瀬川',
            '馬淵川',
            '北上川',
            '鳴瀬川',
            '名取川',
            '阿武隈川',
            '米代川',
            '雄物川',
            '子吉川',
            '最上川',
            '赤川',
            '久慈川',
            '那珂川',
            '利根川',
            '荒川',
            '多摩川',
            '鶴見川',
            '相模川',
            '富士川',
            '荒川',
            '阿賀野川',
            '信濃川',
            '関川',
            '姫川',
            '黒部川',
            '常願寺川',
            '神通川',
            '庄川',
            '小矢部川',
            '手取川',
            '梯川',
            '胎内川',
            '加治川',
            '狩野川',
            '安倍川',
            '大井川',
            '菊川',
            '天竜川',
            '豊川',
            '矢作川',
            '庄内川',
            '木曽川',
            '鈴鹿川',
            '雲出川',
            '櫛田川',
            '宮川',
            '中部その他',
            '由良川',
            '淀川',
            '大和川',
            '円山川',
            '加古川',
            '揖保川',
            '紀の川',
            '新宮川',
            '九頭竜川',
            '北川',
            '武庫川',
            '六甲山系',
            '中国その他',
            '千代川',
            '天神川',
            '日野川',
            '斐伊川',
            '江の川',
            '高津川',
            '吉井川',
            '旭川',
            '高梁川',
            '芦田川',
            '太田川',
            '小瀬川',
            '佐波川',
            '神戸川',
            '三隅川',
            '阿武川',
            '沼田川',
            '黒瀬川',
            '錦川',
            '椹野川',
            '厚東川',
            '益田川',
            '中国その他2',
            '中国その他3',
            '四国その他',
            '吉野川',
            '那賀川',
            '土器川',
            '重信川',
            '肱川',
            '物部川',
            '仁淀川',
            '渡川',
            '勝浦川',
            '香東川',
            '財田川',
            '加茂川',
            '海部川',
            '奈半利川',
            '伊尾木川',
            '鏡川',
            '松田川',
            '新川',
            '打樋川',
            '四国その他2',
            '四国その他3',
            '四国その他4',
            '遠賀川',
            '山国川',
            '筑後川',
            '矢部川',
            '松浦川',
            '六角川',
            '嘉瀬川',
            '本明川',
            '菊池川',
            '白川',
            '緑川',
            '球磨川',
            '大分川',
            '大野川',
            '番匠川',
            '五ヶ瀬川',
            '小丸川',
            '大淀川',
            '川内川',
            '肝属川',
            '九州その他']

def _date_range(beginDate, endDate):
    dates = []
    dt = datetime.datetime.strptime(beginDate, "%Y%m%d")
    date = beginDate[:]
    while date <= endDate:
        dates.append(date)
        dt = dt + datetime.timedelta(1)
        date = dt.strftime("%Y%m%d")
    return dates

def _search_by_water_system_type(waterSystem: str, obsvType: str):
    assert waterSystem in waterSystems
    assert obsvType == 'rain' or obsvType == 'water'
    dictWaterSystems = np.load('./models/dictWaterSystems.npy', allow_pickle = True).item()
    return dictWaterSystems[waterSystem + obsvType]

def _obsv_detail(obsvId: int):
    db_cnct = sqlite3.connect('./databases/waterlevel.db')
    cursor = db_cnct.cursor()
    cursor.execute("SELECT Observatories_name, Observatories_type, Water_system, River, Prefectures_id, Latitude_longitude FROM Observatories_info WHERE Observatories_id = '%s'" %str(obsvId))
    data = cursor.fetchall()
    obsvInfo = data[0]
    return obsvInfo

def _obsv_data(obsvId: int, beginDate = None, endDate = None):
    if _obsv_detail(obsvId)[1] == '水位流量':
        tblName = 'WaterData_' + str(obsvId)
    elif _obsv_detail(obsvId)[1] == '雨量':
        tblName = 'RainData_' + str(obsvId)
    if beginDate == None:
        db_cnct = sqlite3.connect('./databases/waterlevel.db')
        cursor = db_cnct.cursor()
        cursor.execute("SELECT * FROM %s" %tblName)
        data = cursor.fetchall()
        obsvData = []
        for datum in data:
            hour = 1
            for x in datum[1:]:
                obsvData.append((datum[0] * 100 + hour, x))
                hour += 1
    else:
        beginDate = int(beginDate)
        endDate = int(endDate)
        db_cnct = sqlite3.connect('./databases/waterlevel.db')
        cursor = db_cnct.cursor()
        cursor.execute("SELECT * FROM %s" %tblName)
        data = cursor.fetchall()
        obsvData = []
        for datum in data:
            if datum[0] >= beginDate and datum[0] <= endDate:
                hour = 1
                for x in datum[1:]:
                    obsvData.append((datum[0] * 100 + hour, x))
                    hour += 1
    obsvData.sort()
    obsvData = [x[1] for x in obsvData]
    return obsvData

def _convert_data_format(list_in):
    list_out = []
    list_out.append(list_in[0][:4] + list_in[0][5:7] + list_in[0][8:])
    for index in range(1, 25):
        if list_in[index] == '欠測':
            list_out.append('9e999')
        elif list_in[index] == '閉局':
            list_out.append('-9e999')
        elif list_in[index] == '未知':
            list_out.append('9e999 / 9e999')
        else:
            list_out.append(list_in[index])
    return list_out

def _update_by_id_and_date(obsvId: int, beginDate: str, endDate: str):
    if _obsv_detail(obsvId)[1] == '水位流量':
        tblName = 'WaterData_' + str(obsvId)
    elif _obsv_detail(obsvId)[1] == '雨量':
        tblName = 'RainData_' + str(obsvId)
    dates = _date_range(beginDate, endDate)
    for date in dates:
        db_cnct = sqlite3.connect('./databases/waterlevel.db')
        cursor = db_cnct.cursor()
        cursor.execute("SELECT * FROM %s WHERE Date = '%s'" %(tblName, date))
        data = cursor.fetchall()
        # print(data)
        if data == []:
            if tblName[0] == 'W':
                datum = _convert_data_format(search_w(obsvId, int(date[:4]), int(date[4:6]), int(date[6:])))
                # print('insert', datum)
            if tblName[0] == 'R':
                datum = _convert_data_format(search_r(obsvId, int(date[:4]), int(date[4:6]), int(date[6:])))
                # print('insert', datum)
            print("INSERT into %s (Date, `1oclock`, `2oclock`, `3oclock`, `4oclock`, `5oclock`, `6oclock`, `7oclock`, `8oclock`, `9oclock`, `10oclock`, `11oclock`, `12oclock`, `13oclock`, `14oclock`, `15oclock`, `16oclock`, `17oclock`, `18oclock`, `19oclock`, `20oclock`, `21oclock`, `22oclock`, `23oclock`, `24oclock`) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % tuple([tblName] + datum))
            cursor.execute("INSERT into %s (Date, `1oclock`, `2oclock`, `3oclock`, `4oclock`, `5oclock`, `6oclock`, `7oclock`, `8oclock`, `9oclock`, `10oclock`, `11oclock`, `12oclock`, `13oclock`, `14oclock`, `15oclock`, `16oclock`, `17oclock`, `18oclock`, `19oclock`, `20oclock`, `21oclock`, `22oclock`, `23oclock`, `24oclock`) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % tuple([tblName] + datum))
        else:
            if tblName[0] == 'W':
                datum = _convert_data_format(search_w(obsvId, int(date[:4]), int(date[4:6]), int(date[6:])))
                # print('change', datum)
            if tblName[0] == 'R':
                datum = _convert_data_format(search_r(obsvId, int(date[:4]), int(date[4:6]), int(date[6:])))
                # print('change', datum)
            print("UPDATE %s SET `1oclock` = %s, `2oclock` = %s, `3oclock` = %s, `4oclock` = %s, `5oclock` = %s, `6oclock` = %s, `7oclock` = %s, `8oclock` = %s, `9oclock` = %s, `10oclock` = %s, `11oclock` = %s, `12oclock` = %s, `13oclock` = %s, `14oclock` = %s, `15oclock` = %s, `16oclock` = %s, `17oclock` = %s, `18oclock` = %s, `19oclock` = %s, `20oclock` = %s, `21oclock` = %s, `22oclock` = %s, `23oclock` = %s, `24oclock` = %s WHERE Date = '%s'" % tuple([tblName] + datum[1:] + [datum[0]]))
            cursor.execute("UPDATE %s SET `1oclock` = %s, `2oclock` = %s, `3oclock` = %s, `4oclock` = %s, `5oclock` = %s, `6oclock` = %s, `7oclock` = %s, `8oclock` = %s, `9oclock` = %s, `10oclock` = %s, `11oclock` = %s, `12oclock` = %s, `13oclock` = %s, `14oclock` = %s, `15oclock` = %s, `16oclock` = %s, `17oclock` = %s, `18oclock` = %s, `19oclock` = %s, `20oclock` = %s, `21oclock` = %s, `22oclock` = %s, `23oclock` = %s, `24oclock` = %s WHERE Date = '%s'" % tuple([tblName] + datum[1:] + [datum[0]]))
        db_cnct.commit()