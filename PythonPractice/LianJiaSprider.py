import urllib.request as req
import re
import urllib.error
import sqlite3 as sql

def genUrlList():
    urlList=[]
    url = "http://sh.lianjia.com/ershoufang/d%d/"
    for i in range(100, 300):
        urlList.append(url%i)
    return urlList;

def getUrlInfo(url):
    try:
        #heads = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"}
        request = req.Request(url)
        f = req.urlopen(request);
        data = f.read().decode("utf-8")
        #data = data.decode("utf-8")
        #1.首先找到房源列表
        #2.找到每个房源信息
        #3.依次找到标题、房屋简介、总价、小区名、地区、街道、年限、单价、距离地铁情况、是否满五
        pattern = re.compile('<a class="text link-hover-green js_triggerGray js_fanglist_title".*?title="(.*?)">.*?'#.*?<div',#标题
                             '</use></svg>(.*?)</span>.*?'#房屋简介
                             '<span class="total-price strong-num">(.*?)</span>.*?'#总价
                             '<span title.*?>(.*?)</span>.*?'#小区名
                             '<a href=.*?>(.*?)</a>.*?'#地区
                             '<a href=.*?>(.*?)</a>(.*?)</span>.*?'#街道、年限
                             '<span class="info-col price-item minor">(.*?)</span>',#单价
                             re.S);
        items = re.findall(pattern, data)
        return items;
        for item in items:
            print("title: %s"%item[0].strip(" \n\r"))
            print(u"房屋简介: %s"%item[1].strip(" \n\r"))
            print(u"总价: %s万"%item[2].strip(" \n\r"))
            print(u"小区名：%s"%item[3].strip(" \n\r"))
            print(u"地区：%s 街道：%s 年限：%s"%(item[4].strip(" \n\r"),item[5].strip(" \n\r"),item[6].strip(" \n\r")))
            print(u"单价：%s"%item[7].strip(" \n\r"))
    except urllib.error.HTTPError as e:
        print(e.code);
    except urllib.error.URLError as e:
        print(e.reason);
    else:
        print("Executed!");

def parseRawItem(item):
    #解析出：名称、房间数、客厅数、卫生间数、年限、平方、区域、街道、小区、满五、总的楼层、当前楼层、地铁、距离地铁距离、朝向、单价、总价
    houseDetailInfo = {};
    if (len(item) >= 8):
        houseDetailInfo['Title'] = item[0] #title 标题
        houseDetailInfo['TotalPrice'] = item[2] #total price  总价
        houseDetailInfo['UnitPrice'] = float(re.search('\d+',item[7]).group())/10000.0#Unit Price 单价
        searchObj = re.search('(\d)室.*?(\d)厅.*?(\d+\.?\d+)平.*?\| (.*?)/(\d+?)层', item[1],re.DOTALL) #对象
        if searchObj is not None:
            houseDetailInfo['SquaresVal'] = searchObj.group(3) #平方数
            houseDetailInfo['RoomNum'] = searchObj.group(1) #房间数
            houseDetailInfo['LivingRoomNum'] = searchObj.group(2) #客厅数
            houseDetailInfo['CurFloor'] = searchObj.group(4)
            houseDetailInfo['TotalFloor'] = searchObj.group(5)
        else:
            houseDetailInfo['SquaresVal'] = 0  # 平方数
            houseDetailInfo['RoomNum'] = 0  # 房间数
            houseDetailInfo['LivingRoomNum'] = 0  # 客厅数
            houseDetailInfo['CurFloor'] = 0
            houseDetailInfo['TotalFloor'] = 0
        houseDetailInfo['Area'] = item[4].strip(' \n\r') #地区
        houseDetailInfo['Street'] = item[5].strip(' \n\r'); #街道
        searchObj = re.search('\d+', item[6])
        houseDetailInfo['Years'] = 0
        if searchObj is not None: houseDetailInfo['Years'] = re.search('\d+', item[6]).group() #年限
        return houseDetailInfo;

def stroeItem2Db(houseInfoList):
    #打开数据库
    db = sql.connect('LianJiaData.db')
    cursor = db.cursor();
    for houseInfo in houseInfoList:
        str =  '''insert into HouseDetailData \
        (Title,RoomNum,LivingRoomNum,Years, SquaresVal,Area,Street,TotalFloor,CurFloor,UnitPrice,TotalPrice)\
         values(\"%s\",%s,%s,%s,%s,\"%s\",\"%s\",%d,\"%s\",%s,%s)''';
        str = str%(houseInfo['Title'],
                        houseInfo['RoomNum'],
                        houseInfo['LivingRoomNum'],
                        houseInfo['Years'],
                        houseInfo['SquaresVal'],
                        houseInfo['Area'],
                        houseInfo['Street'],
                        int(houseInfo['TotalFloor']),
                        houseInfo['CurFloor'],
                        houseInfo['UnitPrice'],
                        houseInfo['TotalPrice']);
        cursor.execute(str);
    db.commit()
    db.close()
    return ;

urlList = genUrlList();
i = 100;
for url in urlList:
    items = getUrlInfo(url)
    houseInfos = []
    for item in items:
        houseInfos.append(parseRawItem(item));
    stroeItem2Db(houseInfos)
    print("存放了第%d页数据"%i)
    i = i + 1

