#代驾小程序
# 用户APP接口测试
import sys,json, time,hashlib,random, requests as reqs
from urllib.parse import urlencode
from xlpkg import x
sys.path.append(r'f:/test/web/stress/')
#import wm_d as d

# 公共变量
content_type={'www':'application/x-www-urlencoded;charset=UTF-8','json':'application/json;charset=UTF-8'}
alias = '868040035985321'
deviceId = '868040035985321'
loginMode = 'mobile_pwd'
mobile = '15975576669'
mobileType = '3'
password = 'af7d9d0c02d9c28eafb5b4bf1e70950e'
paypassword = 'af7d9d0c02d9c28eafb5b4bf1e70950e'
smsCode = ''

#cid = '100007' #代送cid
cid = '110002' #代驾cid
cv = 'test123.8.30.test1'
ts = x.f_ts()
u_token = '11111111'
sk ='fc2f2c4da9d23ac2d224425e849c0de1'

imei = '57ac2377-92c5-4dee-bafa-5cc626dae4cf'
businessId = '2050025'
userLat = '22.979434'
userLng = '113.370103'
toAddressId = '4423427'
# toAddressId ='4423674'

# 用户登录
d_login = {
    'alias': alias,
    'deviceId': deviceId,
    'loginMode': loginMode,
    'mobile': mobile,
    'mobileType': mobileType,
    'password': password
    # 'sign':'',
    # 'smsCode':''
}

k = {
    'cid': cid,
    'ts': ts,
    'cv': cv,
    'u_token': u_token,
    'sk': sk
}


e_sum = 0.0
url_base = 'http://test-gw.gxptkc.com'
flog = open('log99.txt', 'w')

url_base='https://test-driving.gxptkc.com/'
#url_base='https://api-driving.gxptkc.com/'
#0.校验登录记录
url_verify=url_base+'manage/loginlockrecord/needVerify?loginType=1&account=15975576669&clientId=110002'
d_verify={
'loginType': '1',
'account': '15975576669',
'clientId': '110002',
}
def f_verify(url=url_verify,d=d_verify):
    try:
        x.f_pc(32, x.f_pt(' =',5,'00.校验登录记录'))
        r = reqs.get(url, headers=h_login, data=d)
        x.f_pc(31, r.json()['code'],r.json()['msg'],
        r.json()['data']['loginType'],
        r.json()['data']['account'],
        r.json()['data']['clientId'] )

        if r.reason=='OK' and r.status_code==200:
            x.f_pc(42, x.f_elapsed(r),r.reason,r.status_code,r.ok)
        else:
            x.f_pc(31,'Failed',r.text)
    except Exception as e:
        x.f_pc(31,e)
    pass


# 1.商家登录
h_login = {
    'Content-Type': content_type['json'],
    'clientId': cid,
    'clientVersion': cv,
    'timestamp': ts,
    'IMEI': imei,
    'token': '11111111',
    'sign': x.f_sign(d_login, k),
}


ds_login={
    'name':'15975576669',
    'password':'af7d9d0c02d9c28eafb5b4bf1e70950e',
    'openId':'oO9RQ5DIXiyf5wkL7Gh5AHrFcE1Y',
    'loginMode':'1'
}


dj_login={
'username': '15975576669',
'clientId': '110002',
'loginType': '1',
'loginString': 'wd000000'
}
#1.代驾用户登录
#url_login=url_base+'/server-daisong/daisong/user/noken/nsign/login1'
url=url_base+'user/login?username=15975576669&clientId=110002&loginType=1&loginString=wd000000'

token=''
def f_login(url, h_login, dj_login):
    # 发送POST请求,获取服务器响应:
    try:
        x.f_pc(32, x.f_pt(' =',5,'01.代驾用户登录'))
        r = reqs.get(url, headers=h_login, data=dj_login)
        #x.f_pc(33, r.text)
        #token=(r.json()['data']['token'])
        token=(r.json()['access_token'])
        if r.reason=='OK' and r.status_code==200:
            x.f_pc(42, x.f_elapsed(r),'tenant_id:',r.json()['tenant_id'],'user_id:',r.json()['user_id'],'username:',r.json()['username'])
            #x.f_pc(32,r.reason,r.status_code,r.ok, '\n', r.text)
            return(token)
        else:
            x.f_pc(31,'Failed',r.text)
    except Exception as e:
        x.f_pc(31,e)
    pass

#2.代驾用户无目标地址叫车
url_call=url_base+'special/publish'
d_call={
'duration': '0',
'distance': '0',
'serviceType': '4',
#'uid': '1661305826', #生产环境
'uid': '1657760937', #测试环境

'adCode': '440113',
'carType': '',
'changeMobile': '',
'changeName': '',
'cityName': '广州市',
'originAddress': '番禺区人民政府内',
'originLat': '22.943954',
'originLon': '113.390709',
'destinationAdCode': '',
'destinationAddress': '',
'destinationCityName': '',
'destinationLat': '',
'destinationLon': '',
'driverNum': '1',
'isChange': '0',
'isInform': '0',
'placeOrderAddress': '番禺区人民政府内',
'placeOrderLat': '22.943954',
'placeOrderLon': '113.390709',
'platform': 'wechat',
'price': '',
'orderPath': '',
'isAppointment': '1',
'startTime':''
}

def f_call(token,url=url_call,d=d_call):
    # 发送POST请求,获取服务器响应:
    headers = {
        'Content-Type': content_type['www'],
        'clientId': cid,
        'clientVersion': cv,
        'IMEI': imei,
        'sign': x.f_sign(d,k),
        'timestamp': str(ts),
        'TENANT-ID': '18',
        'Authorization': 'bearer '+token

    }
    try:
        x.f_pc(31, x.f_pt(' =',5,'02.代驾用户下单'))
        r = reqs.post(url, headers=headers, data=d,params=d)
        #x.f_pc(31,token)
        #x.f_pc(33,headers)
        x.f_pc(33, r.json())
        #x.f_pc(34,r.reason, r.status_code, r.ok)
        orderid=r.json()['data']['orderId']
        #token=(r.json()['data']['token'])
        #token=(r.json()['access_token'])
        if r.reason=='OK' and r.status_code==200:
            x.f_pc(42, x.f_elapsed(r), orderid)
            #print(r.reason,r.status_code,r.ok, '\n', r.text)
            return(orderid)
        else:
            x.f_pc(31,'Failed',r.text)
    except Exception as e:
        x.f_pc(31,e)
    pass

#查询未结束行程的订单
url_cxdd=url_base+'order/passengerOrderList?serviceType=4&pageSize=10&pageCode=1'
d_cxdd={
    'serviceType': '4',
    'pageSize': '3',
    'pageCode': '1'
}

#url_cxdd="https://api-driving.gxptkc.com/order/order-info/{17755}?isDriver=0&orderId={17755}"
#d_cxdd={ 'isDriver': '0', 'orderId': '17755' }


def f_djcxdd(token,url=url_cxdd,d=d_cxdd):

    # 发送POST请求,获取服务器响应:
    headers = {
        'Content-Type': content_type['www'],
        'clientId': cid,
        'clientVersion': cv,
        'IMEI': imei,
        'sign': x.f_sign(d,k),
        'timestamp': str(ts),
        'TENANT-ID': '18',
        'Authorization': 'bearer '+token

    }
    try:
        x.f_pc(31, x.f_pt(' =',5,'03.代驾用户查询未结束行程订单'))
        r = reqs.get(url, headers=headers, data=d,params=d)
        #x.f_pc(31,token)
        #x.f_pc(33,headers)
        #x.f_pc(33, r.json())
        #x.f_pc(34,r.reason, r.status_code, r.ok)

        #token=(r.json()['data']['token'])
        #token=(r.json()['access_token'])
        if r.reason=='OK' and r.status_code==200 and r.json()['code']==0:
        #if r.json()['code'] == 0:
            orderid = ''
            for i in r.json()['data']['records']:
                #x.f_pc(43,{'id':i['id'],'orderStatus':i['orderStatus']})
                if i['orderStatus'] == 0:
                    orderid = i['id']
                    x.f_pc(42, x.f_elapsed(r),'orderId:',orderid)
                    #print(r.reason,r.status_code,r.ok, '\n', r.text)
                    return(orderid)
        else:
            x.f_pc(31,'Failed!',r.text)
    except Exception as e:
        x.f_pc(31,e)
    pass
#代送用户取消订单
url_djcancel=url_base+'special/cancel'
d_djcancel={
'cancelLat': '',
'cancelLon': '',
'isDriver': '0',
'isSelf': '',
'orderId': '17745',
'reason': ''
}
def f_djcancel(token,url=url_djcancel,d=d_djcancel):

    # 发送POST请求,获取服务器响应:
    headers = {
        'Content-Type': content_type['www'],
        'clientId': cid,
        'clientVersion': cv,
        'IMEI': imei,
        'sign': x.f_sign(d,k),
        'timestamp': str(ts),
        'TENANT-ID': '18',
        'Authorization': 'bearer '+token

    }
    try:
        #x.f_pc(42,d['orderId'])
        x.f_pc(35, x.f_pt(' =',5,'03.代驾用户取消订单'))
        r = reqs.post(url, headers=headers, data=d,params=d)
        #x.f_pc(31,token)
        #x.f_pc(33,headers)
        #x.f_pc(33, r.json())
        #x.f_pc(34,r.reason, r.status_code, r.ok)
        #token=(r.json()['data']['token'])
        #token=(r.json()['access_token'])
        if r.reason=='OK' and r.status_code==200:
            x.f_pc(32, x.f_elapsed(r),'orderId:',d['orderId'])
            #print(r.reason,r.status_code,r.ok, '\n', r.text)
            return(r)
        else:
            x.f_pc(31,'Failed',r.text)
    except Exception as e:
        x.f_pc(31,e)
    pass
    pass


#获取附近地址列表
url_nearbyaddr=url_base+'/server-daisong/daisong/address/send/getList'
d2={
    'isDefault': '1',
    'isShopAddress': '1'
}

def f_nearbyaddr(token,url=url_nearbyaddr,d=d2):
    """
    s = ''
    s += 'isDefault=' + d['isDefault']
    s += '&isShopAddress=' + d['isShopAddress']

    s += cid
    s += str(ts)
    s += cv
    s += token
    s += sk

    # print('string9999:' + s)
    obj = hashlib.md5(s.encode())
    sign = obj.hexdigest()
    s += sign
    """

    headers = {
        'Content-Type': content_type['www'],
        'clientId': cid,
        'clientVersion': cv,
        'IMEI': imei,
        'sign': x.f_sign(d,k),
        'timestamp': str(ts),
        'token': token
    }
    x.f_pc(33, x.f_pt(' =',5,'02.获取附近地址列表'))
    r = reqs.post(url, headers=headers, data=d, params=d)
    #print(r.reason,'\n',r.text)
    if x.f_assert(r):
        x.f_pc(33,x.f_elapsed(r))
        # e_sum+=round(r.elapsed.total_seconds()*1000,2)
        return (r)
    else:
        x.f_pc(31,'Failed!',r.text)
        pass
    pass


d3={
    'address': '-'+str(x.f_randint(1301,1399)),
    'gender': str(x.f_randint(0,1)),
    'isDefault': '0',
    'latitude': '22.9392'+str(x.f_randint(0,99)).zfill(2),
    'longitude': '113.3824'+str(x.f_randint(0,99)).zfill(2),
    'mobile': '159755766'+str(x.f_randint(0,99)).zfill(2),
    'name': 'xiaolong'+str(x.f_randint(0,99)).zfill(2),
    'userAddress': '番禺大厦F-'+str(x.f_randint(10,33)).zfill(2)
}

#地址列表
url_addr=url_base+'/server-daisong/daisong/address/send/getList'
d_addr={
    'current': '1',
    'isShopAddress': '2',
    'likeQuery': '',
    'size': '100'}

def f_addrlist(token,url=url_addr,d=d_addr):
    """
    s = ''
    s+='current='+d['current']
    s+='&isShopAddress='+d['isShopAddress']
    s+='&likeQuery='+ d['likeQuery']
    s+='&size='+d['size']

    s += cid
    s += str(ts)
    s += cv
    s += token
    s += sk
    # print('string9999:' + s)
    obj = hashlib.md5(s.encode())
    sign = obj.hexdigest()
    s += sign
    """

    headers = {
        'Content-Type': content_type['www'],
        'clientId': cid,
        'clientVersion': cv,
        'IMEI': imei,
        'sign': x.f_sign(d,k),
        'timestamp': str(ts),
        'token': token
    }
    x.f_pc(34, x.f_pt(' =',5,'033.地址列表'))
    r = reqs.post(url, headers=headers, data=d, params=d)
    if x.f_assert(r):
        #print(r.reason,'\n',r.text)
        #print(r.reason,'\n',r.json()['data']['records'])
        n=(len(r.json()['data']['records']))
        addrlist=[]
        for i in range(n):
            print(r.json()['data']['records'][i]['id'])
            addrlist.append(r.json()['data']['records'][i]['id'])
        print('addrlist:',n)
        x.f_pc(34,x.f_elapsed(r))
        # e_sum+=round(r.elapsed.total_seconds()*1000,2)
        return (addrlist)
    else:
        x.f_pc(31,'Failed!',r.text)
    pass


#增加收货地址
url_add_addr=url_base+'/server-daisong/daisong/address/send/add'
def f_add_addr(token,url=url_add_addr,d=d3):
    """
    s = ''
    s += 'address='     +d['address']
    s += '&gender='     +d['gender']
    s += '&isDefault='  +d['isDefault']
    s += '&latitude='   +d['latitude']
    s += '&longitude='  +d['longitude']
    s += '&mobile='     +d['mobile']
    s += '&name='       +d['name']
    s += '&userAddress='+d['userAddress']
    s += cid
    s += str(ts)
    s += cv
    s += token
    s += sk
    # print('string9999:' + s)
    obj = hashlib.md5(s.encode())
    sign = obj.hexdigest()
    s += sign
    """

    headers = {
        'Content-Type': content_type['www'],
        'clientId': cid,
        'clientVersion': cv,
        'IMEI': imei,
        'sign': x.f_sign(d,k),
        'timestamp': str(ts),
        'token': token
    }
    x.f_pc(34, x.f_pt(' =',5,'03.增加收货地址'))
    r = reqs.post(url, headers=headers, data=d, params=d)
    #print(r.reason,'\n',r.text)
    if x.f_assert(r):
        x.f_pc(34,x.f_elapsed(r))
        # e_sum+=round(r.elapsed.total_seconds()*1000,2)
        return (r)
    else:
        x.f_pc(31,'Failed!',r.text)
    pass

#更新代送地址
url_update_addr=url_base+'/server-daisong/daisong/address/send/update'
d4={
    'address': '1303',
    'gender': '1',
    'id': '476',
    'isDefault': '0',
    'latitude': '22.939235',
    'longitude': '113.382419',
    'mobile': '15975576667',
    'name': 'xiaolong',
    'userAddress': '番禺大厦'
}

def f_update_addr(token,url=url_update_addr,d=d4):
    """
    s = ''
    s += 'address='     +d['address']
    s += '&gender='     +d['gender']
    s += '&id='         +d['id']
    s += '&isDefault='  +d['isDefault']
    s += '&latitude='   +d['latitude']
    s += '&longitude='  +d['longitude']
    s += '&mobile='     +d['mobile']
    s += '&name='       +d['name']
    s += '&userAddress='+d['userAddress']
    s += cid
    s += str(ts)
    s += cv
    s += token
    s += sk
    # print('string9999:' + s)
    obj = hashlib.md5(s.encode())
    sign = obj.hexdigest()
    s += sign
    """

    headers = {
        'Content-Type': content_type['www'],
        'clientId': cid,
        'clientVersion': cv,
        'IMEI': imei,
        'sign': x.f_sign(d,k),
        'timestamp': str(ts),
        'token': token
    }
    x.f_pc(35, x.f_pt(' =',5,'04.更新地址'))
    r = reqs.post(url, headers=headers, data=d, params=d)
    #print(r.reason,'\n',r.text)
    if x.f_assert(r):
        x.f_pc(35,x.f_elapsed(r))
        # e_sum+=round(r.elapsed.total_seconds()*1000,2)
        return (r)
    else:
        x.f_pc(31,'Failed!',r.text)
    pass

#删除地址
url_del_addr=url_base+'/server-daisong/daisong/address/send/delete'

def f_del_addr(token,url=url_del_addr,d=None):
    """
    s = ''
    s += 'id=' +d['id']

    s += cid
    s += str(ts)
    s += cv
    s += token
    s += sk
    # print('string9999:' + s)
    obj = hashlib.md5(s.encode())
    sign = obj.hexdigest()
    s += sign
    """

    headers = {
        'Content-Type': content_type['www'],
        'clientId': cid,
        'clientVersion': cv,
        'IMEI': imei,
        'sign': x.f_sign(d,k),
        'timestamp': str(ts),
        'token': token
    }
    x.f_pc(31, x.f_pt(' =',5,'05.删除收货地址'))
    r = reqs.post(url, headers=headers, data=d, params=d)
    if x.f_assert(r):
        x.f_pc(31,x.f_elapsed(r))
        # e_sum+=round(r.elapsed.total_seconds()*1000,2)
        return (r)
    else:
        x.f_pc(31,'Failed!',r.text)
    pass

#选择地址
url_sele_addr=url_base+'/server-daisong/daisong/address/send/addressSort'
d5={
    'fromId': '404',
    'toLatitude': '22.939235',
    'toLongitude': '113.382419',
    'type': 'DAISONG'
}
def f_sele_addr(token,url=url_sele_addr,d=d5):
    """
    s = ''
    s += 'fromId='          +d['fromId']
    s += '&toLatitude='     +d['toLatitude']
    s += '&toLongitude='    +d['toLongitude']
    s += '&type='           +d['type']
    s += cid
    s += str(ts)
    s += cv
    s += token
    s += sk
    # print('string9999:' + s)
    obj = hashlib.md5(s.encode())
    sign = obj.hexdigest()
    s += sign
    """

    headers = {
        'Content-Type': content_type['www'],
        'clientId': cid,
        'clientVersion': cv,
        'IMEI': imei,
        'sign': x.f_sign(d,k),
        'timestamp': str(ts),
        'token': token
    }
    x.f_pc(34, x.f_pt(' =',5,'05.选择收货地址'))
    r = reqs.post(url, headers=headers, data=d, params=d)
    if x.f_assert(r):
        x.f_pc(33,x.f_elapsed(r))
        # e_sum+=round(r.elapsed.total_seconds()*1000,2)
        return (r)
    else:
        x.f_pc(31,'Failed!',r.text)
    pass

#发单
url_fd=url_base+'/server-daisong/daisong/order/confirm'
url_reorder=url_base+'/server-daisong/daisong/order/fillIn'
d_fd={
    'address': '1801',
    'deliveryFee': '1200',
    'fromId': '404',
    'fromType': 'DAISONG',
    'goodsType': '餐饮',
    'mobile': '15975576004',
    'name': '刘先生',
    'pickTime': '',
    'remark': '',
    'tag': '',
    'tip': '0',
    'to2UserAddress': '广州市番禺区人民政府',
    'toAddress': '1304',
    'toGender': '1',
    'toId': '0',
    'toLatitude': '22.93772',
    'toLongitude': '113.38424',
    'toMobile': '15975576667',
    'toName': 'xiaolong',
    'type': 'DAISONG',
    'unionPay': '1',
    'userAddress': '天安总部中心1号楼'
}

def f_fd(token,url=url_reorder,d=d_fd):
    """

    s = ''
    s+='address='           +d['address']
    s+='&deliveryFee='      +d['deliveryFee']
    s+='&fromId='           +d['fromId']
    s+='&fromType='         +d['fromType']
    s+='&goodsType='        +d['goodsType']
    s+='&mobile='           +d['mobile']
    s+='&name='             +d['name']
    s+='&pickTime='         +d['pickTime']
    s+='&remark='           +d['remark']
    s+='&tag='              +d['tag']
    s+='&tip='              +d['tip']
    s+='&to2UserAddress='   +d['to2UserAddress']
    s+='&toAddress='        +d['toAddress']
    s+='&toGender='         +d['toGender']
    s+='&toId='             +d['toId']
    s+='&toLatitude='       +d['toLatitude']
    s+='&toLongitude='      +d['toLongitude']
    s+='&toMobile='         +d['toMobile']
    s+='&toName='           +d['toName']
    s+='&type='             +d['type']
    s+='&unionPay='         +d['unionPay']
    s+='&userAddress='      +d['userAddress']

    s += cid
    s += str(ts)
    s += cv
    s += token
    s += sk

    # print('string9999:' + s)
    obj = hashlib.md5(s.encode())
    sign = obj.hexdigest()
    s += sign

    """
    headers = {
        'Content-Type': content_type['www'],
        'clientId': cid,
        'clientVersion': cv,
        'IMEI': imei,
        'sign': x.f_sign(d,k),
        'timestamp': str(ts),
        'token': token
    }
    x.f_pc(36, x.f_pt(' =',5,'066.发单'))
    r = reqs.post(url, headers=headers, data=d, params=d)
    if x.f_assert(r):
        x.f_pc(36,x.f_elapsed(r))
        # e_sum+=round(r.elapsed.total_seconds()*1000,2)
        return (r)
    else:
        x.f_pc(31,'Failed!',r.text)
    pass


#提交订单
url_confirm=url_base+'/server-daisong/daisong/order/confirm'
def f_fdconfirm(token,url=url_confirm,d=d_fd):
    """
    s = ''
    s += 'address='         +d['address']
    s += '&deliveryFee='    +d['deliveryFee']
    s += '&fromId='         +d['fromId']
    s += '&fromType='       +d['fromType']
    s += '&=mobile'         +d['mobile']
    s += '&=name'           +d['name']
    s += '&=pickTime'       +d['pickTime']
    s += '&=remark'         +d['remark']
    s += '&=tag'            +d['tag']
    s += '&=tip'            +d['tip']
    s += '&=to2UserAddress' +d['to2UserAddress']
    s += '&=toAddress'      +d['toAddress']
    s += '&=toLatitude'     +d['toLatitude']
    s += '&=toLongitude'    +d['toLongitude']
    s += '&=toMobile'       +d['toMobile']
    s += '&=toName'         +d['toName']
    s += '&=type'           +d['type']
    s += '&=unionPay'       +d['unionPay']
    s += '&=userAddress'    +d['userAddress']

    s += cid
    s += str(ts)
    s += cv
    s += token
    s += sk
    # print('string9999:' + s)
    obj = hashlib.md5(s.encode())
    sign = obj.hexdigest()
    s += sign
    """

    headers = {
        'Content-Type': content_type['www'],
        'clientId': cid,
        'clientVersion': cv,
        'IMEI': imei,
        'sign': x.f_sign(d,k),
        'timestamp': str(ts),
        'token': token
    }
    x.f_pc(33, x.f_pt(' =',5,'077.提交订单'))
    r = reqs.post(url, headers=headers, data=d, params=d)
    if x.f_assert(r):
        orderId=r.json()['data']['id']
        x.f_pc(33,x.f_elapsed(r))
        # e_sum+=round(r.elapsed.total_seconds()*1000,2)
        return(orderId)
    else:
        x.f_pc(31,'Failed!',r.text)
    pass

#重新下单
url_reorder=url_base+'/server-daisong/daisong/order/fillIn'
d6={
    'fromId': '404',
    'toLatitude': '22.939235',
    'toLongitude': '113.382419',
    'type': 'DAISONG'
}

def f_reorder(token,url=url_reorder,d=d6):
    """
    s = ''
    s += 'fromId='      +d['fromId']
    s += '&toLatitude=' +d['toLatitude']
    s += '&toLongitude='+d['toLongitude']
    s += '&type='       +d['type']

    s += cid
    s += str(ts)
    s += cv
    s += token
    s += sk

    # print('string9999:' + s)
    obj = hashlib.md5(s.encode())
    sign = obj.hexdigest()
    s += sign
    """

    headers = {
        'Content-Type': content_type['www'],
        'clientId': cid,
        'clientVersion': cv,
        'IMEI': imei,
        'sign': x.f_sign(d,k),
        'timestamp': str(ts),
        'token': token
    }
    x.f_pc(36, x.f_pt(' =',5,'06.重新下单'))
    r = reqs.post(url, headers=headers, data=d, params=d)
    #print(r.reason,'\n',r.text)
    if x.f_assert(r):
        x.f_pc(36,x.f_elapsed(r))
        # e_sum+=round(r.elapsed.total_seconds()*1000,2)
        return (r)
    else:
        x.f_pc(31,'Failed!',r.text)
    pass

#提交订单
url_confirm=url_base+'/server-daisong/daisong/order/confirm'

d7= {'address': '1801',
     'deliveryFee': '1300',
     'fromId': '404',
     'fromType': 'DAISONG',
     'gender': '1',
     'goodsType': '文件',
     'latitude': '22.979186697',
     'longitude': '113.370542715',
     'mobile': '15975576004',
     'name': '刘先生',
     'pickTime': '',
     'remark': '物品备注',
     'tag': '',
     'tip': str(random.randint(1,10)),
     'to2UserAddress': '番禺大厦',
     'toAddress': '1303',
     'toGender': '1',
     'toId': '474',
     'toLatitude': '22.939235',
     'toLongitude': '113.382419',
     'toMobile': '15975576667',
     'toName': 'xiaolong',
     'type': 'DAISONG',
     'unionPay': '1',
     'userAddress': '天安总部中心1号楼'
     }

#提交订单
def f_confirm(token,url=url_confirm,d=d7):
    """
    s = ''
    s += 'address='         +d['address']
    s += '&deliveryFee='    +d['deliveryFee']
    s += '&fromId='         +d['fromId']
    s += '&fromType='       +d['fromType']
    s += '&=latitude'       +d['latitude']
    s += '&=longitude'      +d['longitude']
    s += '&=mobile'         +d['mobile']
    s += '&=name'           +d['name']
    s += '&=pickTime'       +d['pickTime']
    s += '&=remark'         +d['remark']
    s += '&=tag'            +d['tag']
    s += '&=tip'            +d['tip']
    s += '&=to2UserAddress' +d['to2UserAddress']
    s += '&=toAddress'      +d['toAddress']
    s += '&=toLatitude'     +d['toLatitude']
    s += '&=toLongitude'    +d['toLongitude']
    s += '&=toMobile'       +d['toMobile']
    s += '&=toName'         +d['toName']
    s += '&=type'           +d['type']
    s += '&=unionPay'       +d['unionPay']
    s += '&=userAddress'    +d['userAddress']

    s += cid
    s += str(ts)
    s += cv
    s += token
    s += sk
    # print('string9999:' + s)
    obj = hashlib.md5(s.encode())
    sign = obj.hexdigest()
    s += sign
    """

    headers = {
        'Content-Type': content_type['www'],
        'clientId': cid,
        'clientVersion': cv,
        'IMEI': imei,
        'sign': x.f_sign(d,k),
        'timestamp': str(ts),
        'token': token
    }
    x.f_pc(31, x.f_pt(' =',5,'07.提交订单'))
    r = reqs.post(url, headers=headers, data=d, params=d)
    #print(r.reason,'\n',r.text)

    if x.f_assert(r):
        orderId=r.json()['data']['id']
        x.f_pc(31,x.f_elapsed(r))
        return(orderId)
    else:
        x.f_pc(31,'Failed!',r.text)
    pass

#额度支付
url_walletpay=url_base+'/server-daisong/daisong/user/wallletPay'
d8={
    'orderId': '67928580'
}

def f_walletpay(token,url=url_walletpay,d=d8):
    """
    s = ''
    s += '&=orderId'    +d['orderId']

    s += cid
    s += str(ts)
    s += cv
    s += token
    s += sk
    # print('string9999:' + s)
    obj = hashlib.md5(s.encode())
    sign = obj.hexdigest()
    s += sign
    """

    headers = {
        'Content-Type': content_type['www'],
        'clientId': cid,
        'clientVersion': cv,
        'IMEI': imei,
        'sign': x.f_sign(d,k),
        'timestamp': str(ts),
        'token': token
    }
    x.f_pc(32, x.f_pt(' =',5,'08.额度支付'))
    r = reqs.post(url, headers=headers, data=d, params=d)
    #print(r.reason,'\n',r.text)

    if x.f_assert(r):
        x.f_pc(42,x.f_elapsed(r))
        # e_sum+=round(r.elapsed.total_seconds()*1000,2)
        return (r)
    else:
        x.f_pc(31,'Failed!',r.text)
    pass

#查询订单列表
url_dslist=url_base+'/server-daisong/daisong/order/list'
d10={
    'page': '0',
    'size': '10',
}
def f_dslist(token,url=url_dslist,d=d10):
    """
    s = ''
    s += '=page'    +d['page']
    s += '&=size'   +d['size']

    s += cid
    s += str(ts)
    s += cv
    s += token
    s += sk
    # print('string9999:' + s)
    obj = hashlib.md5(s.encode())
    sign = obj.hexdigest()
    s += sign
    """

    headers = {
        'Content-Type': content_type['www'],
        'clientId': cid,
        'clientVersion': cv,
        'IMEI': imei,
        'sign': x.f_sign(d,k),
        'timestamp': str(ts),
        'token': token
    }
    x.f_pc(31, x.f_pt(' =',5,'10.代送订单列表'))
    r = reqs.post(url, headers=headers, data=d, params=d)
    if x.f_assert(r):
        with open('dslist.txt','w') as f:
            print(r.json()['data'],file=f)
        x.f_pc(31,x.f_elapsed(r))
        # e_sum+=round(r.elapsed.total_seconds()*1000,2)
    else:
        x.f_pc(31,'Failed!',r.text)
    pass

#取消订单
url_dscancel=url_base+'/server-daisong/daisong/order/cancel?orderId=67928611&isReturn=1'

d9={
    'isReturn': '1',
    'orderId': '67928614',
}
def f_dscancel(token,url=url_dscancel,d=d9):
    """
    s = ''
    s += '=isReturn'    +d['isReturn']
    s += '&=orderId'    +d['orderId']

    s += cid
    s += str(ts)
    s += cv
    s += token
    s += sk
    # print('string9999:' + s)
    obj = hashlib.md5(s.encode())
    sign = obj.hexdigest()
    s += sign
    """

    headers = {
        'Content-Type': content_type['www'],
        'clientId': cid,
        'clientVersion': cv,
        'IMEI': imei,
        'sign': x.f_sign(d,k),
        'timestamp': str(ts),
        'token': token
    }
    x.f_pc(31, x.f_pt(' =',5,'09.取消订单'))
    r = reqs.post(url, headers=headers, data=d, params=d)
    if x.f_assert(r):
        x.f_pc(31,x.f_elapsed(r))
        # e_sum+=round(r.elapsed.total_seconds()*1000,2)
    else:
        x.f_pc(31,'Failed!',r.text)
    pass

def main():
    #1.代驾用户登录
    f_verify()
    token=f_login(url,h_login,ds_login)

    if len(sys.argv)>1:
        opt=sys.argv[1]
        match opt:
            #代驾用户下单
            case 'djxd'|'call':
                f_call(token,url=url_call,d=d_call)
                pass

            #代驾用户查询未结束行程的订单
            case 'djcxdd'|'cxdd':
                f_djcxdd(token,url=url_cxdd,d=d_cxdd)
                pass
            #代驾用户取消订单
            case 'djcancel':
                #orderid=f_call(token,url=url_call,d=d_call)
                orderid=f_djcxdd(token,url=url_cxdd,d=d_cxdd)
                d_djcancel['orderId']=orderid
                f_djcancel(token,url=url_djcancel,d=d_djcancel)
                pass

            #地址列表
            case 'addrlist':
                f_addrlist(token,url=url_addr,d=d_addr)
                pass

            #批量删除地址
            case 'deladdr':
                addrlist= f_addrlist(token,url=url_addr,d=d_addr)
                for i in range(len(addrlist)):
                    d_del_addr={'id':str(addrlist[i])}
                    f_del_addr(token,url=url_del_addr,d=d_del_addr)
                pass

            #3.增加收货地址
            case 'addaddr':
                f_add_addr(token,url_add_addr,d3)
                pass

            # 取消订单
            case 'cancel':
                #查询订单列表，获取未支付的订单 'status':'CREATED'
                f_dslist(token,url=url_dslist,d=d10)
                #sys.exit()
                d9 = {
                    'isReturn': '1',
                    'orderId': '67937808',
                }
                cancel=''
                cancel = '/server-daisong/daisong/order/cancel?isReturn='+d9['isReturn']+'&orderId='+d9['orderId']
                url_cancel=url_base+cancel
                #print(url_cancel)
                f_dscancel(token, url=url_cancel, d=d9)

            #再来一单
            case 'xd':
                i=0
                n=int(sys.argv[2])
                #print(n)
                while i<n:
                    #重新下单
                    f_reorder(token,url_reorder,d6)

                    #提交订单，返回订单号
                    d7['tip']=str(random.randint(1,10))
                    orderid=f_confirm(token,url=url_confirm,d=d7)

                    #额度支付
                    d8['orderId']=str(orderid)
                    f_walletpay(token, url=url_walletpay, d=d8)
                    i+=1

            #发单
            case 'fd':
                i=0
                n=int(sys.argv[2])
                #print(n)
                while i<n:
                    #发单
                    f_fd(token,url_reorder,d_fd)

                    #提交订单，返回订单号
                    d6['tip']=str(random.randint(1,10))
                    orderid=f_fdconfirm(token,url=url_confirm,d=d_fd)

                    #额度支付
                    d8['orderId']=str(orderid)
                    f_walletpay(token, url=url_walletpay, d=d8)
                    i+=1
                pass
    else:
        #2.获取附近地址列表
        f_nearbyaddr(token,url_nearbyaddr,d2)

        #3.增加收货地址
        f_add_addr(token,url_add_addr,d3)

        #更新收货地址
        f_update_addr(token,url_update_addr,d4)

        #选择收货地址
        #f_sele_addr(token,url_sele_addr,d5)

        #重新下单
        f_reorder(token,url_reorder,d6)

        #提交订单，返回订单号
        orderid=f_confirm(token,url=url_confirm,d=d7)

        d8['orderId']=str(orderid)
        f_walletpay(token, url=url_walletpay, d=d8)

        #骑手功能 py wm_d.py dsall
        #骑手登录

        #查询订单

        #骑手抢单

        #骑手签到

        #骑手取货

        #骑手送达


if __name__=='__main__':
    main()
    #print(d.f_add(1,2,3,4))
    pass
