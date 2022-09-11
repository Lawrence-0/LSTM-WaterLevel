from bs4 import BeautifulSoup
import re
import urllib.request, urllib.error
import pandas as pd
from pycodes.date_tools import isValidDate

head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
baseurl0 = 'http://www1.river.go.jp/cgi-bin/DspWaterData.exe?KIND=2&ID='
baseurl1 = '&BGNDATE='
baseurl2 = '01&ENDDATE=20201231&KAWABOU=NO'
pat_dat_url = '<a href="/dat/dload/download/(.*?).dat" target="_blank">'

def _search_by_id_and_date(id: int, year: int, month: int, day = None):
    assert year >= 1900 and year <=2100 and month >= 1 and month <= 12
    if day != None:
        assert isValidDate(year, month, day)
    id = str(id).zfill(15)
    year = str(year).zfill(4)
    month = str(month).zfill(2)
    url = baseurl0 + id + baseurl1 + year + month + baseurl2
    html = urllib.request.urlopen(url).read().decode('euc_jp')
    soup = BeautifulSoup(html,"html.parser")
    dat_str = str(soup.select('body h2 a')[0])
    dat_url = 'http://www1.river.go.jp/dat/dload/download/' + re.findall(pat_dat_url, dat_str)[0] + '.dat'
    dat_dat = pd.read_csv(dat_url, sep = "::", header=None, encoding = 'shift_jis')
    dat_dat = dat_dat[10:]
    dat_list = dat_dat.values.tolist()
    dat_list = [d[0] for d in dat_list]
    result = []
    for d in dat_list:
        temp = d.split(',')
        for i in range(1, 49):
            temp[i] = temp[i].strip()
        clct = [temp[0]]
        for i in range(1, 25):
            if temp[i * 2] == '$':
                clct.append('欠測')
            elif temp[i * 2] == '#':
                clct.append('閉局')
            elif temp[i * 2] == '-':
                clct.append('未知')
            else:
                clct.append(temp[i * 2 - 1])
        # print(clct)
        result.append(clct)
    if day == None:
        return result
    if day != None:
        return result[day - 1]