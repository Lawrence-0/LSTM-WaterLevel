#------------------------import-modules-----------------------------------------------------#
from flask import url_for, escape, Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from scipy import interpolate
import os
import sys
import click
import datetime
import datetime
import re
import cv2
import time
import numpy as np
import pycodes.make_prd as make_prd
import pycodes.make_prd1 as make_prd1
import pycodes.dias_prd as dias_prd
import pycodes.get_obsv_weights as get_obsv_weights
#------------------------start-environment--------------------------------------------------#
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, './databases/waterlevel.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
#------------------------struct-database-modules--------------------------------------------#
class Prefectures_info(db.Model):
    __tablename__ = 'Prefectures_info'
    Prefectures_id = db.Column(db.Integer, primary_key=True)
    Prefectures_name = db.Column(db.Text)
class Observatories_info(db.Model):
    __tablename__ = 'Observatories_info'
    Observatories_id = db.Column(db.Integer, primary_key=True)
    Observatories_name = db.Column(db.Text)
    Observatories_type = db.Column(db.Text)
    Water_system = db.Column(db.Text)
    River = db.Column(db.Text)
    Prefectures_id = db.Column(db.Integer)
    Location = db.Column(db.Text)
    Latitude_longitude = db.Column(db.Text)
    url = db.Column(db.Text)
class RainData:
    Date = db.Column(db.Integer, primary_key=True)
    OC1 = db.Column('1oclock', db.Text)
    OC2 = db.Column('2oclock', db.Text)
    OC3 = db.Column('3oclock', db.Text)
    OC4 = db.Column('4oclock', db.Text)
    OC5 = db.Column('5oclock', db.Text)
    OC6 = db.Column('6oclock', db.Text)
    OC7 = db.Column('7oclock', db.Text)
    OC8 = db.Column('8oclock', db.Text)
    OC9 = db.Column('9oclock', db.Text)
    OC10 = db.Column('10oclock', db.Text)
    OC11 = db.Column('11oclock', db.Text)
    OC12 = db.Column('12oclock', db.Text)
    OC13 = db.Column('13oclock', db.Text)
    OC14 = db.Column('14oclock', db.Text)
    OC15 = db.Column('15oclock', db.Text)
    OC16 = db.Column('16oclock', db.Text)
    OC17 = db.Column('17oclock', db.Text)
    OC18 = db.Column('18oclock', db.Text)
    OC19 = db.Column('19oclock', db.Text)
    OC20 = db.Column('20oclock', db.Text)
    OC21 = db.Column('21oclock', db.Text)
    OC22 = db.Column('22oclock', db.Text)
    OC23 = db.Column('23oclock', db.Text)
    OC24 = db.Column('24oclock', db.Text)
#------------------------make-selection-id-to-info------------------------------------------#
observatory_type_codes = {
    "-1": "全観測項目",
    "01": "雨量",
    "02": "水位流量",
    "03": "水質・底質",
    "04": "地下水位・水質",
    "05": "ダム・堰",
    "06": "海象",
    "07": "積雪深"
}
observatory_type_orders = {
    "-1": 0,
    "01": 1,
    "02": 2,
    "03": 3,
    "04": 4,
    "05": 5,
    "06": 6,
    "07": 7
}
water_system_codes = {
    "-1": "全水系",
    "90331000": "福地川",
    "90332000": "新川川",
    "90333000": "安波川",
    "90334000": "辺野喜川",
    "90335000": "漢那福地川",
    "90336000": "羽地大川",
    "90338000": "億首川",
    "90339000": "天願川",
    "90509000": "大保川",
    "90512000": "大井川",
    "90538000": "報得川",
    "981198": "増幌川",
    "981199": "声問川",
    "983308": "富士川",
    "987111": "大社湾",
    "987799": "蒲生川",
    "99901000": "港川",
    "99902000": "ジニサン川",
    "99903000": "長浜川",
    "99904000": "白水川",
    "147999": "有津川",
    "247004": "大浦川",
    "547102": "与那川",
    "547103": "比地川",
    "547104": "田嘉里川",
    "547105": "大保川",
    "547106": "源河川",
    "547130": "汀間川",
    "547135": "奥川",
    "547146": "億首川",
    "547147": "座津武川",
    "547148": "比謝川",
    "547151": "武見川",
    "547152": "宇嘉川",
    "547153": "佐手川",
    "547154": "佐手前川",
    "547155": "宇良川",
    "547157": "外掘田川",
    "547158": "根路銘ポンプ場",
    "81001000": "天塩川",
    "81002000": "渚滑川",
    "81003000": "湧別川",
    "81004000": "常呂川",
    "81005000": "網走川",
    "81006000": "留萌川",
    "81007000": "石狩川",
    "81008000": "尻別川",
    "81009000": "後志利別川",
    "81010000": "鵡川",
    "81011000": "沙流川",
    "81012000": "釧路川",
    "81013000": "十勝川",
    "81201000": "声問川",
    "81221000": "勇払川",
    "81241000": "標津川",
    "82014000": "岩木川",
    "82015000": "高瀬川",
    "82016000": "馬淵川",
    "82017000": "北上川",
    "82018000": "鳴瀬川",
    "82019000": "名取川",
    "82020000": "阿武隈川",
    "82021000": "米代川",
    "82022000": "雄物川",
    "82023000": "子吉川",
    "82024000": "最上川",
    "82025000": "赤川",
    "83026000": "久慈川",
    "83027000": "那珂川",
    "83028000": "利根川",
    "83029000": "荒川",
    "83030000": "多摩川",
    "83031000": "鶴見川",
    "83032000": "相模川",
    "83046000": "富士川",
    "84033000": "荒川",
    "84034000": "阿賀野川",
    "84035000": "信濃川",
    "84036000": "関川",
    "84037000": "姫川",
    "84038000": "黒部川",
    "84039000": "常願寺川",
    "84040000": "神通川",
    "84041000": "庄川",
    "84042000": "小矢部川",
    "84043000": "手取川",
    "84044000": "梯川",
    "84270000": "胎内川",
    "84271000": "加治川",
    "85045000": "狩野川",
    "85047000": "安倍川",
    "85048000": "大井川",
    "85049000": "菊川",
    "85050000": "天竜川",
    "85051000": "豊川",
    "85052000": "矢作川",
    "85053000": "庄内川",
    "85054000": "木曽川",
    "85056000": "鈴鹿川",
    "85057000": "雲出川",
    "85058000": "櫛田川",
    "85059000": "宮川",
    "85999000": "中部その他",
    "86060000": "由良川",
    "86061000": "淀川",
    "86062000": "大和川",
    "86063000": "円山川",
    "86064000": "加古川",
    "86065000": "揖保川",
    "86066000": "紀の川",
    "86067000": "新宮川",
    "86068000": "九頭竜川",
    "86069000": "北川",
    "86282000": "武庫川",
    "86500000": "六甲山系",
    "87000000": "中国その他",
    "87071000": "千代川",
    "87072000": "天神川",
    "87073000": "日野川",
    "87074000": "斐伊川",
    "87075000": "江の川",
    "87076000": "高津川",
    "87077000": "吉井川",
    "87078000": "旭川",
    "87079000": "高梁川",
    "87080000": "芦田川",
    "87081000": "太田川",
    "87082000": "小瀬川",
    "87083000": "佐波川",
    "87291000": "神戸川",
    "87293000": "三隅川",
    "87295000": "阿武川",
    "87296000": "沼田川",
    "87297000": "黒瀬川",
    "87298000": "錦川",
    "87300000": "椹野川",
    "87301000": "厚東川",
    "87307000": "益田川",
    "87500000": "中国その他2",
    "87888000": "中国その他3",
    "88000000": "四国その他",
    "88084000": "吉野川",
    "88085000": "那賀川",
    "88086000": "土器川",
    "88087000": "重信川",
    "88088000": "肱川",
    "88089000": "物部川",
    "88090000": "仁淀川",
    "88091000": "渡川",
    "88304000": "勝浦川",
    "88305000": "香東川",
    "88306000": "財田川",
    "88307000": "加茂川",
    "88308000": "海部川",
    "88309000": "奈半利川",
    "88310000": "伊尾木川",
    "88311000": "鏡川",
    "88312000": "松田川",
    "88313000": "新川",
    "88314000": "打樋川",
    "88500000": "四国その他2",
    "88888000": "四国その他3",
    "88999000": "四国その他4",
    "89092000": "遠賀川",
    "89093000": "山国川",
    "89094000": "筑後川",
    "89095000": "矢部川",
    "89096000": "松浦川",
    "89097000": "六角川",
    "89098000": "嘉瀬川",
    "89099000": "本明川",
    "89100000": "菊池川",
    "89101000": "白川",
    "89102000": "緑川",
    "89103000": "球磨川",
    "89104000": "大分川",
    "89105000": "大野川",
    "89106000": "番匠川",
    "89107000": "五ヶ瀬川",
    "89108000": "小丸川",
    "89109000": "大淀川",
    "89110000": "川内川",
    "89111000": "肝属川",
    "89999000": "九州その他"
}
water_system_orders = {
    "-1": 0,
    "90331000": 1,
    "90332000": 2,
    "90333000": 3,
    "90334000": 4,
    "90335000": 5,
    "90336000": 6,
    "90338000": 7,
    "90339000": 8,
    "90509000": 9,
    "90512000": 10,
    "90538000": 11,
    "981198": 12,
    "981199": 13,
    "983308": 14,
    "987111": 15,
    "987799": 16,
    "99901000": 17,
    "99902000": 18,
    "99903000": 19,
    "99904000": 20,
    "147999": 21,
    "247004": 22,
    "547102": 23,
    "547103": 24,
    "547104": 25,
    "547105": 26,
    "547106": 27,
    "547130": 28,
    "547135": 29,
    "547146": 30,
    "547147": 31,
    "547148": 32,
    "547151": 33,
    "547152": 34,
    "547153": 35,
    "547154": 36,
    "547155": 37,
    "547157": 38,
    "547158": 39,
    "81001000": 40,
    "81002000": 41,
    "81003000": 42,
    "81004000": 43,
    "81005000": 44,
    "81006000": 45,
    "81007000": 46,
    "81008000": 47,
    "81009000": 48,
    "81010000": 49,
    "81011000": 50,
    "81012000": 51,
    "81013000": 52,
    "81201000": 53,
    "81221000": 54,
    "81241000": 55,
    "82014000": 56,
    "82015000": 57,
    "82016000": 58,
    "82017000": 59,
    "82018000": 60,
    "82019000": 61,
    "82020000": 62,
    "82021000": 63,
    "82022000": 64,
    "82023000": 65,
    "82024000": 66,
    "82025000": 67,
    "83026000": 68,
    "83027000": 69,
    "83028000": 70,
    "83029000": 71,
    "83030000": 72,
    "83031000": 73,
    "83032000": 74,
    "83046000": 75,
    "84033000": 76,
    "84034000": 77,
    "84035000": 78,
    "84036000": 79,
    "84037000": 80,
    "84038000": 81,
    "84039000": 82,
    "84040000": 83,
    "84041000": 84,
    "84042000": 85,
    "84043000": 86,
    "84044000": 87,
    "84270000": 88,
    "84271000": 89,
    "85045000": 90,
    "85047000": 91,
    "85048000": 92,
    "85049000": 93,
    "85050000": 94,
    "85051000": 95,
    "85052000": 96,
    "85053000": 97,
    "85054000": 98,
    "85056000": 99,
    "85057000": 100,
    "85058000": 101,
    "85059000": 102,
    "85999000": 103,
    "86060000": 104,
    "86061000": 105,
    "86062000": 106,
    "86063000": 107,
    "86064000": 108,
    "86065000": 109,
    "86066000": 110,
    "86067000": 111,
    "86068000": 112,
    "86069000": 113,
    "86282000": 114,
    "86500000": 115,
    "87000000": 116,
    "87071000": 117,
    "87072000": 118,
    "87073000": 119,
    "87074000": 120,
    "87075000": 121,
    "87076000": 122,
    "87077000": 123,
    "87078000": 124,
    "87079000": 125,
    "87080000": 126,
    "87081000": 127,
    "87082000": 128,
    "87083000": 129,
    "87291000": 130,
    "87293000": 131,
    "87295000": 132,
    "87296000": 133,
    "87297000": 134,
    "87298000": 135,
    "87300000": 136,
    "87301000": 137,
    "87307000": 138,
    "87500000": 139,
    "87888000": 140,
    "88000000": 141,
    "88084000": 142,
    "88085000": 143,
    "88086000": 144,
    "88087000": 145,
    "88088000": 146,
    "88089000": 147,
    "88090000": 148,
    "88091000": 149,
    "88304000": 150,
    "88305000": 151,
    "88306000": 152,
    "88307000": 153,
    "88308000": 154,
    "88309000": 155,
    "88310000": 156,
    "88311000": 157,
    "88312000": 158,
    "88313000": 159,
    "88314000": 160,
    "88500000": 161,
    "88888000": 162,
    "88999000": 163,
    "89092000": 164,
    "89093000": 165,
    "89094000": 166,
    "89095000": 167,
    "89096000": 168,
    "89097000": 169,
    "89098000": 170,
    "89099000": 171,
    "89100000": 172,
    "89101000": 173,
    "89102000": 174,
    "89103000": 175,
    "89104000": 176,
    "89105000": 177,
    "89106000": 178,
    "89107000": 179,
    "89108000": 180,
    "89109000": 181,
    "89110000": 182,
    "89111000": 183,
    "89999000": 184
}
Prefectures_codes = {
    "-1": "全国",
    "0101": "北海道",
    "0201": "青森県",
    "0301": "岩手県",
    "0401": "宮城県",
    "0501": "秋田県",
    "0601": "山形県",
    "0701": "福島県",
    "0801": "茨城県",
    "0901": "栃木県",
    "1001": "群馬県",
    "1101": "埼玉県",
    "1201": "千葉県",
    "1301": "東京都",
    "1401": "神奈川県",
    "1501": "新潟県",
    "1601": "富山県",
    "1701": "石川県",
    "1801": "福井県",
    "1901": "山梨県",
    "2001": "長野県",
    "2101": "岐阜県",
    "2201": "静岡県",
    "2301": "愛知県",
    "2401": "三重県",
    "2501": "滋賀県",
    "2601": "京都府",
    "2701": "大阪府",
    "2801": "兵庫県",
    "2901": "奈良県",
    "3001": "和歌山県",
    "3101": "鳥取県",
    "3201": "島根県",
    "3301": "岡山県",
    "3401": "広島県",
    "3501": "山口県",
    "3601": "徳島県",
    "3701": "香川県",
    "3801": "愛媛県",
    "3901": "高知県",
    "4001": "福岡県",
    "4101": "佐賀県",
    "4201": "長崎県",
    "4301": "熊本県",
    "4401": "大分県",
    "4501": "宮崎県",
    "4601": "鹿児島県",
    "4701": "沖縄県"
}
Prefectures_orders = {
    "-1": 0,
    "0101": 1,
    "0201": 2,
    "0301": 3,
    "0401": 4,
    "0501": 5,
    "0601": 6,
    "0701": 7,
    "0801": 8,
    "0901": 9,
    "1001": 10,
    "1101": 11,
    "1201": 12,
    "1301": 13,
    "1401": 14,
    "1501": 15,
    "1601": 16,
    "1701": 17,
    "1801": 18,
    "1901": 19,
    "2001": 20,
    "2101": 21,
    "2201": 22,
    "2301": 23,
    "2401": 24,
    "2501": 25,
    "2601": 26,
    "2701": 27,
    "2801": 28,
    "2901": 29,
    "3001": 30,
    "3101": 31,
    "3201": 32,
    "3301": 33,
    "3401": 34,
    "3501": 35,
    "3601": 36,
    "3701": 37,
    "3801": 38,
    "3901": 39,
    "4001": 40,
    "4101": 41,
    "4201": 42,
    "4301": 43,
    "4401": 44,
    "4501": 45,
    "4601": 46,
    "4701": 47
}
Year_orders = {
    "-1": 0,
    "2010": 1,
    "2011": 2,
    "2012": 3,
    "2013": 4,
    "2014": 5,
    "2015": 6,
    "2016": 7,
    "2017": 8,
    "2018": 9,
    "2019": 10
}
Month_orders = {
    "-1": 0,
    "01": 1,
    "02": 2,
    "03": 3,
    "04": 4,
    "05": 5,
    "06": 6,
    "07": 7,
    "08": 8,
    "09": 9,
    "10": 10,
    "11": 11,
    "12": 12
}
Day_orders = {
    "-1": 0,
    "01": 1, 
    "02": 2, 
    "03": 3, 
    "04": 4, 
    "05": 5, 
    "06": 6, 
    "07": 7, 
    "08": 8, 
    "09": 9, 
    "10": 10,
    "11": 11,
    "12": 12,
    "13": 13,
    "14": 14,
    "15": 15,
    "16": 16,
    "17": 17,
    "18": 18,
    "19": 19,
    "20": 20,
    "21": 21,
    "22": 22,
    "23": 23,
    "24": 24,
    "25": 25,
    "26": 26,
    "27": 27,
    "28": 28,
    "29": 29,
    "30": 30,
    "31": 31
}
Year_orders1 = {
    "-1": 0,
    "2031": 1,
    "2032": 2,
    "2033": 3,
    "2034": 4,
    "2035": 5,
    "2036": 6,
    "2037": 7,
    "2038": 8,
    "2039": 9,
    "2040": 10,
    "2041": 11,
    "2042": 12,
    "2043": 13,
    "2044": 14,
    "2045": 15,
    "2046": 16,
    "2047": 17,
    "2048": 18,
    "2049": 19,
    "2050": 20,
    "2051": 21,
    "2052": 22,
    "2053": 23,
    "2054": 24,
    "2055": 25,
    "2056": 26,
    "2057": 27,
    "2058": 28,
    "2059": 29
}
#------------------------make-selected-lists------------------------------------------------#
def make_observatory_type_selecteds(code = '-1'):
    observatory_type_selecteds = []
    for i in range(8):
        observatory_type_selecteds.append('')
    observatory_type_selecteds[observatory_type_orders[code]] = 'selected'
    return observatory_type_selecteds
def make_water_system_selecteds(code = '-1'):
    water_system_selecteds = []
    for i in range(185):
        water_system_selecteds.append('')
    water_system_selecteds[water_system_orders[code]] = 'selected'
    return water_system_selecteds
def make_prefecture_selecteds(code = '-1'):
    prefecture_selecteds = []
    for i in range(48):
        prefecture_selecteds.append('')
    prefecture_selecteds[Prefectures_orders[code]] = 'selected'
    return prefecture_selecteds
def make_year_selecteds(code = '-1'):
    year_selecteds = []
    for i in range(11):
        year_selecteds.append('')
    year_selecteds[Year_orders[code]] = 'selected'
    return year_selecteds
def make_month_selecteds(code = '-1'):
    month_selecteds = []
    for i in range(13):
        month_selecteds.append('')
    month_selecteds[Month_orders[code]] = 'selected'
    return month_selecteds
def make_day_selecteds(code = '-1'):
    day_selecteds = []
    for i in range(32):
        day_selecteds.append('')
    day_selecteds[Day_orders[code]] = 'selected'
    return day_selecteds
def make_year_selecteds1(code = '-1'):
    year_selecteds1 = []
    for i in range(30):
        year_selecteds1.append('')
    year_selecteds1[Year_orders1[code]] = 'selected'
    return year_selecteds1
observatory_type_selecteds = make_observatory_type_selecteds()
water_system_selecteds = make_water_system_selecteds()
prefecture_selecteds = make_prefecture_selecteds()
#------------------------find-dates---------------------------------------------------------#
def getday(date0,n):
    y = int(date0[:4])
    m = int(date0[4:6])
    d = int(date0[6:8])
    the_date = datetime.datetime(y,m,d)
    result_date = the_date + datetime.timedelta(days=n)
    d = result_date.strftime('%Y%m%d')
    return d
#------------------------make-observatories-selections--------------------------------------#
observatories = [
    # {'id': '1041110624110', 'name': '長和（おさわ）'}
]
#------------------------make-search--------------------------------------------------------#
def make_search(Observatories_info, observatory_type = '-1', water_system = '-1', prefecture = '-1'):
    observatories = []
    search_results = Observatories_info.query
    if observatory_type != '-1':
        search_results = search_results.filter_by(Observatories_type=observatory_type_codes[observatory_type])
    if water_system != '-1':
        search_results = search_results.filter_by(Water_system=water_system_codes[water_system])
    if prefecture != '-1':
        search_results = search_results.filter_by(Prefectures_id=prefecture[:2])
    for observatory in search_results:
        observatories.append({'id': observatory.Observatories_id, 'name': str(observatory.Observatories_name)})
    return observatories
#------------------------find-location------------------------------------------------------#
def getCross(int1, int2):
    int1 -= 8
    int2 -= 8
    cross = cv2.imread('static/img/cross.png')
    CR = []
    for i in range(17):
        for j in range(17):
            if list(cross[i][j]) == [0, 0, 0]:
                CR.append((int1 + i, int2 + j))
    return CR
def getChart(int1, int2, weights):
    x = []
    for j in range(len(weights)):
        x.append(19 + j * 10)
    x = np.array(x)
    y = []
    for j in range(len(weights)):
        y.append(round(weights[j] * 100))
    y = np.array(y)
    xnew =np.arange(19, (len(weights) + 1) * 10, 1)
    func = interpolate.interp1d(x, y, kind='cubic')
    ynew = func(xnew)
    CR = []
    for j in range(9, (len(weights) + 1) * 10):
        CR.append((int1, int2 + j))
    for j in range(19, (len(weights) + 1) * 10):
        for i in range(0, round(ynew[j - 19])):
            CR.append((int1 - 1 - i, int2 + j))
    return CR
def findLoaction(observatory_id, observatory_type):
    Loc = Observatories_info.query.get(observatory_id).Latitude_longitude
    LocN_0 = re.findall('(.*?)°.*′.*″N_',Loc)[0]
    if LocN_0 == '':
        img = cv2.imread('static/img/results/white.png')
        cv2.imwrite('static/img/chosen.png', img)
        return 0, 0, 85, 50
    else:
        LocN_0 = int(LocN_0)
        LocN_1 = int(re.findall('°(.*?)′.*″N_.*',Loc)[0])
        LocN_2 = int(re.findall('°.*′(.*?)″N_.*',Loc)[0])
        LocE_0 = int(re.findall('.*_(.*?)°.*′.*″',Loc)[0])
        LocE_1 = int(re.findall('.*_.*°(.*?)′.*″',Loc)[0])
        LocE_2 = int(re.findall('.*_.*°.*′(.*?)″',Loc)[0])
        LocN = LocN_0 + LocN_1 / 60 + LocN_2 /3600
        LocE = LocE_0 + LocE_1 / 60 + LocE_2 /3600
        if LocE <= 123.25 or LocE >= 153.75 or LocN <= 20.25 or LocN >= 45.25:
            img = cv2.imread('static/img/results/white.png')
            cv2.imwrite('static/img/chosen.png', img)
            return 0, 0, 85, 50
        else:
            for i in range(247, 308):
                if abs(LocE - i / 2) <= 0.25:
                    LTTD = str((i - 1) / 2).replace('.', '_')
                    setLeft = int(313 - 3144 * (LocE - (i - 1) / 2))
                    break
            for i in range(41, 91):
                if abs(LocN - i / 2) <= 0.25:
                    LGTD = str((i - 1) / 2).replace('.', '_')
                    setTop = int(290 - 3152 * ((i + 1) / 2 - LocN))
                    break
            img = cv2.imread('static/img/results/' + LTTD + '&' + LGTD + '.png')
            for x in getCross(290 - setTop, 313 - setLeft):
                img[x[0]][x[1]] = [0, 0, 0]
            cv2.imwrite('static/img/chosen.png', img)
            if observatory_type == "02":
                weights = get_obsv_weights._get_weights(int(observatory_id), 'w')
                for i in range(len(weights)):
                    addLocation(weights[i], LTTD, LGTD)
            Mx = int((LocE - 123) * 5)
            My = int((45.5 - LocN) * 5)
            return setLeft, setTop, Mx, My
def addLocation(weights, LTTD, LGTD):
    observatory_id = int(weights[0])
    weights = weights[1:]
    LTTD = float(LTTD.replace('_', '.'))
    LGTD = float(LGTD.replace('_', '.'))
    Loc = Observatories_info.query.get(observatory_id).Latitude_longitude
    LocN_0 = re.findall('(.*?)°.*′.*″N_',Loc)[0]
    if LocN_0 == '':
        img = cv2.imread('static/img/results/white.png')
        cv2.imwrite('static/img/chosen.png', img)
        return False
    else:
        LocN_0 = int(LocN_0)
        LocN_1 = int(re.findall('°(.*?)′.*″N_.*',Loc)[0])
        LocN_2 = int(re.findall('°.*′(.*?)″N_.*',Loc)[0])
        LocE_0 = int(re.findall('.*_(.*?)°.*′.*″',Loc)[0])
        LocE_1 = int(re.findall('.*_.*°(.*?)′.*″',Loc)[0])
        LocE_2 = int(re.findall('.*_.*°.*′(.*?)″',Loc)[0])
        LocN = LocN_0 + LocN_1 / 60 + LocN_2 /3600
        LocE = LocE_0 + LocE_1 / 60 + LocE_2 /3600
        if LocE <= (LTTD) or LocE >= (LTTD + 1) or LocN <= (LGTD) or LocN >= (LGTD + 1):
            return False
        else:
            img = cv2.imread('static/img/chosen.png')
            pinLeft = int(3144 * (LocE - LTTD))
            pinTop = int(3152 * (LGTD - LocN + 1))
            for x in getCross(pinTop, pinLeft):
                img[x[0]][x[1]] = [0, 0, 255]
            for x in getChart(pinTop, pinLeft, weights):
                img[x[0]][x[1]] = [0, 0, 255]
            cv2.imwrite('static/img/chosen.png', img)
            return True
#------------------------get-daily-data-----------------------------------------------------#
def getDailyData(observatory_type, observatory_id, year, month, day):
    if observatory_type == '01':
        obs_type = 'RainData'
    elif observatory_type == '02':
        obs_type = 'WaterData'
    date = year + month + day
    # if int(date) >= 20100101 and int(date) <= 20191231:
    table = type(obs_type + observatory_id, (RainData, db.Model), {'__tablename__': obs_type + '_' + observatory_id, '__table_args__': {'extend_existing': True}})
    data = table.query.get(date)
    if data is None:
        dailyData = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        markData = ['未知', '未知', '未知', '未知', '未知', '未知', '未知', '未知', '未知', '未知', '未知', '未知', '未知', '未知', '未知', '未知', '未知', '未知', '未知', '未知', '未知', '未知', '未知', '未知']
    else:
        dailyData = [data.OC1, data.OC2, data.OC3, data.OC4, data.OC5, data.OC6, data.OC7, data.OC8, data.OC9, data.OC10, data.OC11, data.OC12, data.OC13, data.OC14, data.OC15, data.OC16, data.OC17, data.OC18, data.OC19, data.OC20, data.OC21, data.OC22, data.OC23, data.OC24]
        markData = []
        for i in range(len(dailyData)):
            if dailyData[i] is None:
                markData.append('未知')
                dailyData[i] = 0
            elif dailyData[i] == float('inf'):
                markData.append('欠測')
                dailyData[i] = 0
            elif dailyData[i] == float('-inf'):
                markData.append('閉館')
                dailyData[i] = 0
            else:
                markData.append(dailyData[i])
    table = None
    return dailyData, markData
#------------------------open-index-page----------------------------------------------------#
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('submit') == 'Confirm0':
            observatory_type = request.form.get('observatory_type')
            water_system = request.form.get('water_system')
            prefecture = request.form.get('prefecture')
            return redirect(url_for('search', observatory_type=observatory_type, water_system=water_system, prefecture=prefecture))
    return render_template('index.html', observatory_type_selecteds = observatory_type_selecteds, water_system_selecteds = water_system_selecteds, prefecture_selecteds = prefecture_selecteds)
@app.route('/search', methods=['GET', 'POST'])
def search():
    paras = request.args
    observatory_type = paras['observatory_type']
    water_system = paras['water_system']
    prefecture = paras['prefecture']
    observatory_type_selecteds = make_observatory_type_selecteds(observatory_type)
    water_system_selecteds = make_water_system_selecteds(water_system)
    prefecture_selecteds = make_prefecture_selecteds(prefecture)
    observatories = make_search(Observatories_info, observatory_type, water_system, prefecture)
    if request.method == 'POST':
        if request.form.get('submit') == 'Confirm0':
            observatory_type = request.form.get('observatory_type')
            water_system = request.form.get('water_system')
            prefecture = request.form.get('prefecture')
            return redirect(url_for('search', observatory_type=observatory_type, water_system=water_system, prefecture=prefecture))
        elif request.form.get('submit') == 'Confirm1':
            observatory_id = request.form.get('observatory')
            return redirect(url_for('check', observatory_type=observatory_type, water_system=water_system, prefecture=prefecture, observatory_id=observatory_id))
    return render_template('index.html', observatories = observatories, observatory_type_selecteds = observatory_type_selecteds, water_system_selecteds = water_system_selecteds, prefecture_selecteds = prefecture_selecteds)
@app.route('/check', methods=['GET', 'POST'])
def check():
    paras = request.args
    observatory_type = paras['observatory_type']
    water_system = paras['water_system']
    prefecture = paras['prefecture']
    observatory_id = paras['observatory_id']
    observatory_type_selecteds = make_observatory_type_selecteds(observatory_type)
    water_system_selecteds = make_water_system_selecteds(water_system)
    prefecture_selecteds = make_prefecture_selecteds(prefecture)
    observatories = make_search(Observatories_info, observatory_type, water_system, prefecture)
    setLeft, setTop, Mx, My = findLoaction(observatory_id, observatory_type)
    if request.method == 'POST':
        if request.form.get('submit') == 'Confirm0':
            observatory_type = request.form.get('observatory_type')
            water_system = request.form.get('water_system')
            prefecture = request.form.get('prefecture')
            return redirect(url_for('search', observatory_type=observatory_type, water_system=water_system, prefecture=prefecture))
        elif request.form.get('submit') == 'Confirm1':
            observatory_id = request.form.get('observatory')
            return redirect(url_for('check', observatory_type=observatory_type, water_system=water_system, prefecture=prefecture, observatory_id=observatory_id))
        elif request.form.get('submit') == 'Confirm2':
            year = request.form.get('year')
            month = request.form.get('month')
            day = request.form.get('day')
            return redirect(url_for('show', observatory_type=observatory_type, water_system=water_system, prefecture=prefecture, observatory_id=observatory_id, year=year, month=month, day=day, setLeft=setLeft, setTop=setTop, Mx=Mx, My=My))
        elif (request.form.get('submit') == 'Predict' and observatory_type == '02'):
            year1 = request.form.get('year1')
            month1 = request.form.get('month1')
            day1 = request.form.get('day1')
            year_selecteds1 = make_year_selecteds1(year1)
            month_selecteds1 = make_month_selecteds(month1)
            day_selecteds1 = make_day_selecteds(day1)
            return redirect(url_for('show_p', observatory_type=observatory_type, water_system=water_system, prefecture=prefecture, observatory_id=observatory_id, year1=year1, month1=month1, day1=day1, year_selecteds1=year_selecteds1, month_selecteds1=month_selecteds1, day_selecteds1=day_selecteds1, setLeft=setLeft, setTop=setTop, Mx=Mx, My=My))
    return render_template('check.html', observatories = observatories, observatory_type_selecteds = observatory_type_selecteds, water_system_selecteds = water_system_selecteds, prefecture_selecteds = prefecture_selecteds, setLeft = setLeft, setTop = setTop, getTime = time.time(), Mx = Mx, My = My, observatory_id = observatory_id)
@app.route('/show', methods=['GET', 'POST'])
def show():
    paras = request.args
    observatory_type = paras['observatory_type']
    water_system = paras['water_system']
    prefecture = paras['prefecture']
    observatory_id = paras['observatory_id']
    year = paras['year']
    month = paras['month']
    day = paras['day']
    setLeft = paras['setLeft']
    setTop = paras['setTop']
    Mx = paras['Mx']
    My = paras['My']
    observatory_type_selecteds = make_observatory_type_selecteds(observatory_type)
    water_system_selecteds = make_water_system_selecteds(water_system)
    prefecture_selecteds = make_prefecture_selecteds(prefecture)
    observatories = make_search(Observatories_info, observatory_type, water_system, prefecture)
    year_selecteds = make_year_selecteds(year)
    month_selecteds = make_month_selecteds(month)
    day_selecteds = make_day_selecteds(day)
    observatory_name = Observatories_info.query.get(observatory_id).Observatories_name
    dailyData, markData = getDailyData(observatory_type, observatory_id, year, month, day)
    beginDate = datetime.datetime(2010, 1, 1)
    endDate = datetime.datetime(int(year), int(month), int(day))
    hours = (endDate - beginDate).days * 24
    if request.method == 'POST':
        if request.form.get('submit') == 'Confirm0':
            observatory_type = request.form.get('observatory_type')
            water_system = request.form.get('water_system')
            prefecture = request.form.get('prefecture')
            return redirect(url_for('search', observatory_type=observatory_type, water_system=water_system, prefecture=prefecture))
        elif request.form.get('submit') == 'Confirm1':
            observatory_id = request.form.get('observatory')
            return redirect(url_for('check', observatory_type=observatory_type, water_system=water_system, prefecture=prefecture, observatory_id=observatory_id))
        elif request.form.get('submit') == 'Confirm2':
            year = request.form.get('year')
            month = request.form.get('month')
            day = request.form.get('day')
            return redirect(url_for('show', observatory_type=observatory_type, water_system=water_system, prefecture=prefecture, observatory_id=observatory_id, year=year, month=month, day=day, year_selecteds=year_selecteds, month_selecteds=month_selecteds, day_selecteds=day_selecteds, setLeft=setLeft, setTop=setTop, Mx=Mx, My=My))
        elif (request.form.get('submit') == 'Predict' and observatory_type == '02'):
            year1 = request.form.get('year1')
            month1 = request.form.get('month1')
            day1 = request.form.get('day1')
            year_selecteds1 = make_year_selecteds1(year1)
            month_selecteds1 = make_month_selecteds(month1)
            day_selecteds1 = make_day_selecteds(day1)
            return redirect(url_for('show_p', observatory_type=observatory_type, water_system=water_system, prefecture=prefecture, observatory_id=observatory_id, year1=year1, month1=month1, day1=day1, year_selecteds1=year_selecteds1, month_selecteds1=month_selecteds1, day_selecteds1=day_selecteds1, setLeft=setLeft, setTop=setTop, Mx=Mx, My=My))
    if observatory_type == '01':
        return render_template('show1.html', observatories = observatories, observatory_type_selecteds = observatory_type_selecteds, water_system_selecteds = water_system_selecteds, prefecture_selecteds = prefecture_selecteds, dailyData=dailyData, markData = markData, observatory_name = observatory_name, year = year, month = month, day = day, year_selecteds=year_selecteds, month_selecteds=month_selecteds, day_selecteds=day_selecteds, setLeft = setLeft, setTop = setTop, getTime = time.time(), Mx = Mx, My = My, observatory_id = observatory_id)
    elif observatory_type == '02':
        dailyData_p = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        dailyData_p = make_prd._prediction_getting(int(observatory_id), 'r')[hours: hours + 24]
        markData_p = dailyData_p
        return render_template('show2.html', observatories = observatories, observatory_type_selecteds = observatory_type_selecteds, water_system_selecteds = water_system_selecteds, prefecture_selecteds = prefecture_selecteds, dailyData=dailyData, markData = markData, observatory_name = observatory_name, year = year, month = month, day = day, year_selecteds=year_selecteds, month_selecteds=month_selecteds, day_selecteds=day_selecteds, setLeft = setLeft, setTop = setTop, getTime = time.time(), Mx = Mx, My = My, dailyData_p = dailyData_p, markData_p = markData_p, observatory_id = observatory_id)
    else:
        return 'MAKE IT LATER'
@app.route('/show_p', methods=['GET', 'POST'])
def show_p():
    paras = request.args
    observatory_type = paras['observatory_type']
    water_system = paras['water_system']
    prefecture = paras['prefecture']
    observatory_id = paras['observatory_id']
    year1 = paras['year1']
    month1 = paras['month1']
    day1 = paras['day1']
    setLeft = paras['setLeft']
    setTop = paras['setTop']
    Mx = paras['Mx']
    My = paras['My']
    observatory_type_selecteds = make_observatory_type_selecteds(observatory_type)
    water_system_selecteds = make_water_system_selecteds(water_system)
    prefecture_selecteds = make_prefecture_selecteds(prefecture)
    observatories = make_search(Observatories_info, observatory_type, water_system, prefecture)
    year_selecteds1 = make_year_selecteds1(year1)
    month_selecteds1 = make_month_selecteds(month1)
    day_selecteds1 = make_day_selecteds(day1)
    observatory_name = Observatories_info.query.get(observatory_id).Observatories_name
    beginDate1 = datetime.datetime(2031, 1, 1)
    endDate1 = datetime.datetime(int(year1), int(month1), int(day1))
    hours = (endDate1 - beginDate1).days * 24
    dailyData_p = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    # dailyData_p = dias_prd._prediction_getting(int(observatory_id))[hours: hours + 24]
    dailyData_p = make_prd1._prediction_getting(int(observatory_id))[hours: hours + 24]
    markData_p = dailyData_p
    if request.method == 'POST':
        if request.form.get('submit') == 'Confirm0':
            observatory_type = request.form.get('observatory_type')
            water_system = request.form.get('water_system')
            prefecture = request.form.get('prefecture')
            return redirect(url_for('search', observatory_type=observatory_type, water_system=water_system, prefecture=prefecture))
        elif request.form.get('submit') == 'Confirm1':
            observatory_id = request.form.get('observatory')
            return redirect(url_for('check', observatory_type=observatory_type, water_system=water_system, prefecture=prefecture, observatory_id=observatory_id))
        elif request.form.get('submit') == 'Confirm2':
            year = request.form.get('year')
            month = request.form.get('month')
            day = request.form.get('day')
            year_selecteds = make_year_selecteds(year)
            month_selecteds = make_month_selecteds(month)
            day_selecteds = make_day_selecteds(day)
            return redirect(url_for('show', observatory_type=observatory_type, water_system=water_system, prefecture=prefecture, observatory_id=observatory_id, year=year, month=month, day=day, year_selecteds=year_selecteds, month_selecteds=month_selecteds, day_selecteds=day_selecteds, setLeft=setLeft, setTop=setTop, Mx=Mx, My=My))
        elif (request.form.get('submit') == 'Predict' and observatory_type == '02'):
            year1 = request.form.get('year1')
            month1 = request.form.get('month1')
            day1 = request.form.get('day1')
            year_selecteds1 = make_year_selecteds1(year1)
            month_selecteds1 = make_month_selecteds(month1)
            day_selecteds1 = make_day_selecteds(day1)
            return redirect(url_for('show_p', observatory_type=observatory_type, water_system=water_system, prefecture=prefecture, observatory_id=observatory_id, year1=year1, month1=month1, day1=day1, year_selecteds1=year_selecteds1, month_selecteds1=month_selecteds1, day_selecteds1=day_selecteds1, setLeft=setLeft, setTop=setTop, Mx=Mx, My=My))
    return render_template('show3.html', observatories = observatories, observatory_type_selecteds = observatory_type_selecteds, water_system_selecteds = water_system_selecteds, prefecture_selecteds = prefecture_selecteds, observatory_name = observatory_name, year1 = year1, month1 = month1, day1 = day1, year_selecteds1 = year_selecteds1, month_selecteds1 = month_selecteds1, day_selecteds1 = day_selecteds1, setLeft = setLeft, setTop = setTop, getTime = time.time(), Mx = Mx, My = My, dailyData_p = dailyData_p, markData_p = markData_p, observatory_id = observatory_id)