# coding=utf-8
import network
import ujson
import utime as time
import modem
from  aliyunIoT import Device
import kv


global deviceName,g_connect_status,device_dyn_resigter_succed,netw
g_connect_status = False
netw = None
device = None
deviceSecret = None
device_dyn_resigter_succed = False

#初始化物联网平台Device类，获取device实例
device = Device()
# 定义升级包的下载和安装路径，其中url,hash_type和hash 会通过服务端推送被保存下来

info = {
        'url': '',
        'store_path': '/data/pyamp/app.zip',
        'install_path': '/data/pyamp/',
        'length': 0,
        'hash_type': '',
        'hash': ''
}


# 当iot设备连接到物联网平台的时候触发'connect' 事件
def on_connect(data):
    global module_name,default_ver,productKey,deviceName,deviceSecret,on_trigger,on_download,on_verify,on_upgrade
    print('***** connect lp succeed****')
    data_handle = {}
    data_handle['device_handle'] = device.getDeviceHandle()


#当iot云端下发属性设置时，触发'props'事件
def on_props(request):
    print('clound req data is {}'.format(request))


#当连接断开时，触发'disconnect'事件
def on_disconnect():
    print('linkkit is disconnected')


#当iot云端调用设备service时，触发'service'事件
def on_service(id,request):
    print('clound req id  is {} , req is {}'.format(id,request))
#当设备跟iot平台通信过程中遇到错误时，触发'error'事件
def on_error(err):
    print('err msg is {} '.format(err))

#网络连接的回调函数
def on_4g_cb(args):
    global g_connect_status
    pdp = args[0]
    netwk_sta = args[1]
    if netwk_sta == 1:
        g_connect_status = True

    else:
        g_connect_status = False


#网络连接
def connect_network():
    global netw,on_4g_cb,g_connect_status
    netw = network.NetWorkClient()
    g_register_network = False
    if netw._stagecode is not None and netw._stagecode == 3 and netw._subcode == 1:
        g_register_network = True
    else:
        g_register_network = False
    if g_register_network:
    #注册网络连接的回调函数on(self,id,func);  1代表连接，func 回调函数  ；return 0 成功
        netw.on(1,on_4g_cb)
        netw.connect(None)
    else:
        print('网络注册失败')
    while True:
        if g_connect_status:
            print('网络连接成功')
            break
        time.sleep_ms(20)

#动态注册回调函数
def on_dynreg_cb(data):
    global deviceSecret,device_dyn_resigter_succed
    deviceSecret = data
    device_dyn_resigter_succed = True

# 连接物联网平台
def dyn_register_device(productKey,productSecret,deviceName):
    global on_dynreg_cb,device,deviceSecret,device_dyn_resigter_succed

    key = '_amp_customer_devicesecret'
    deviceSecretdict = kv.get(key)
    print("deviceSecretdict:",deviceSecretdict)
    if isinstance(deviceSecretdict,str):
        deviceSecret = deviceSecretdict

    if deviceSecretdict is None or deviceSecret is None:
        key_info = {
            'productKey': productKey  ,
            'productSecret': productSecret ,
            'deviceName': deviceName
            }
        # 动态注册一个设备，获取设备的deviceSecret
        #下面的if防止多次注册，当前若是注册过一次了，重启设备再次注册就会卡住，
        if not device_dyn_resigter_succed:
            device.register(key_info,on_dynreg_cb)

def connect(productKey, productSecret):
    global deviceName,g_connect_status,device_dyn_resigter_succed
    deviceName = None
     # 获取设备的IMEI 作为deviceName 进行动态注册
    deviceName = modem.info.getDevImei()
    # 连接网络
    connect_network()
    if deviceName is not None and len(deviceName) > 0 :
        #动态注册一个设备
        dyn_register_device(productKey,productSecret,deviceName)
    else:
        print("获取设备IMEI失败，无法进行动态注册")
    while deviceSecret is None:
        time.sleep(0.2)
    print('动态注册成功:' + deviceSecret)
    key_info = {
        'region' : 'cn-shanghai' ,
        'productKey': productKey ,
        'deviceName': deviceName ,
        'deviceSecret': deviceSecret ,
        'keepaliveSec': 60,
        }
    #打印设备信息
    print(key_info)
    #device.ON_CONNECT 是事件，on_connect是事件处理函数/回调函数
    device.on(device.ON_CONNECT,on_connect)
    device.on(device.ON_DISCONNECT,on_disconnect)
    device.on(device.ON_PROPS,on_props)
    device.on(device.ON_SERVICE,on_service)
    device.on(device.ON_ERROR,on_error)
    device.connect(key_info)


def up_data(d):
    d_str = ujson.dumps(d)
    data={
        'params':d_str
        }
    device.postProps(data)




