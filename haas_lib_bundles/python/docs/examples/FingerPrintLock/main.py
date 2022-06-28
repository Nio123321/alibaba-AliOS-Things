import utime
from micropython import const
from driver import UART
import sh1106              # SH1106 OLED������
from driver import SPI     # ����SPI���߿�
from driver import GPIO    # ����GPIO��
import framebuf            # framebuf���࣬�������������
import _thread             # �߳̿�
import as608               # AS608ָ��ʶ��ģ���

fig = None
p= -1
SaveResult = -1

from audio import Player, Snd

resDir = "/data/pyamp/resource/"
PUT_ON_FINGER = "putonfinger.wav"                    # �뽫��ָ��ѹ��ָ��ʶ�������
PUT_OFF_FINGER = "putofffinger.wav"                  # ���ƿ���ָ
FINGER_RECORD_SUCCESS = "fingerrecordsuccess.wav"    # ָ��¼�Ƴɹ�
FINGER_SEARCH_FAIL = "searchfail.wav"                # ָ��ʶ��ʧ�� ������һ��
FINGER_SEARCH_SUCCESS = "searchfingersuccess.wav"    # ��ӭ�ؼ�
FINGER_NOT_MATCH = "fingernotmatch.wav"              # ����ָ�Ʋ���ָ�ƿ���
PUT_ON_FINGER_AGAIN = "putonagain.wav"               # ���ٴν���ָ����ָ��ʶ�������
FINGER_RECORD_FAIL = "fingerrecordfail"              # ָ��¼��ʧ�� ������¼��
AUDIO_HEADER = 'fs:'

player = None
oled = None

K1 = None
K2 = None
K3 = None
K4 = None
keyEvents = {'K1':False, 'K2':False, 'K3':False, 'K4':False}

SYS_INIT = const(1)
SYS_ENROLLING = const(2)
SYS_DETECTING = const(3)

promptName = None

# OLED��ʼ��
def oledInit():
    global oled

    # �ֿ��ļ��������ĿĿ¼ font, ע�����õ�����Ӣ���ֿ�����Ҫ����
    framebuf.set_font_path(framebuf.FONT_HZK12, '/data/font/HZK12')
    framebuf.set_font_path(framebuf.FONT_HZK16, '/data/font/HZK16')
    framebuf.set_font_path(framebuf.FONT_HZK24, '/data/font/HZK24')
    framebuf.set_font_path(framebuf.FONT_HZK32, '/data/font/HZK32')
    framebuf.set_font_path(framebuf.FONT_ASC12_8, '/data/font/ASC12_8')
    framebuf.set_font_path(framebuf.FONT_ASC16_8, '/data/font/ASC16_8')
    framebuf.set_font_path(framebuf.FONT_ASC24_12, '/data/font/ASC24_12')
    framebuf.set_font_path(framebuf.FONT_ASC32_16, '/data/font/ASC32_16')

    oled_spi = SPI()
    oled_spi.open("oled_spi")

    oled_res = GPIO()
    oled_res.open("oled_res")

    oled_dc = GPIO()
    oled_dc.open("oled_dc")

    #oled����132*64
    oled = sh1106.SH1106_SPI(132, 64, oled_spi, oled_dc, oled_res)

# ����K1~K4�ĳ�ʼ��
def keyInit():
    global K1, K2, K3, K4
    K1 = GPIO()
    K1.open("KEY_1")
    K1.on(k1Handler)

    K2 = GPIO()
    K2.open("KEY_2")
    K2.on(k2Handler)

    K3 = GPIO()
    K3.open("KEY_3")
    K3.on(k3Handler)

    K4 = GPIO()
    K4.open("KEY_4")
    K4.on(k4Handler)

def k1Handler(obj):
    print('K1 pressed')
    keyEvents['K1'] = True


def k2Handler(obj):
    print('K2 pressed')
    keyEvents['K2'] = True

def k3Handler(obj):
    print('K3 pressed')
    keyEvents['K3'] = True

def k4Handler(obj):
    print('K4 pressed')
    keyEvents['K4'] = True

# ����Ƿ��а��������¼�����pending״̬
def keyEventsPending():
    if all(value == False for value in keyEvents.values()):
        return False
    return True

# ��������¼�
def clearKeyEvents():
    keyEvents['K1'] = False
    keyEvents['K2'] = False
    keyEvents['K3'] = False
    keyEvents['K4'] = False
    pass

# OLED��ʾ
# text:��ʾ���ı�
# x:ˮƽ���� y:��ֱ���� 
# color:��ɫ
# clear: True-������ʾ False-��������ʾ
# sz:�����С
def oledShowText(text, x, y, color, clear, sz):
    global oled
    if clear:
        oled.fill(0) # ����
    oled.text(text, x, y, color, size = sz)
    oled.show()

# �����Ļ
def oledClear():
    oled.fill(0) # ����
    oled.show()

# ��������ʼ��
def playerInit():
    global player
    Snd.init()
    player = Player()
    player.open()
    player.setVolume(8)

# ������ʾ��
def playVoicePrompt(prompt):

    global promptName
    promptName = prompt
    '''
    global player

    if player.getState():
        player.stop()

    # ��Ƶ�ļ�·����ʽ����fs:/data/pyamp/resource/xxx.wav��
    player.play(AUDIO_HEADER + resDir + prompt)
    '''

def playVoicePromptSync(prompt):
    '''
    global promptName
    promptName = prompt
    '''

    global player

    if player.getState():
        player.stop()

    # ��Ƶ�ļ�·����ʽ����fs:/data/pyamp/resource/xxx.wav��
    player.play(AUDIO_HEADER + resDir + prompt)
    player.waitComplete()


# ָ��¼��
def fingerEnroll(id):
    p = as608.FAIL
    global SaveResult

    # �����ʶ��ָ�ƹ����б����س�ʼҳ�������ϣ����˳���ѭ��
    if keyEvents['K4'] or keyEvents['K2']:
        return
    playVoicePrompt(PUT_ON_FINGER)
    oledShowText('�밴ѹ���ذ�', 32, 28, 1, True, 12)
    print('wait for finger print on the pannel...')

    while p != as608.NO_FINGER:
        p = fig.getImage()

    print('invalid, please put your finger on the pannel again...')
    # ��ʼ�ɼ�ָ��
    while p != as608.SUCCESS:
        p = fig.getImage()
        # �����ʶ��ָ�ƹ����б����س�ʼҳ�������ϣ����˳���ѭ��
        if keyEvents['K4'] or keyEvents['K2']:
            return

    print('finger detected')
    # ָ��ͼƬת��Ϊ����ֵ
    p = fig.image2Character(1)
    if p != as608.SUCCESS:
        SaveResult = 0
        print('image to text failed, exit...')
        playVoicePrompt(FINGER_RECORD_FAIL)
        return 0

    # putofffinger
    print('take off your finger please')
    oledShowText('���ƿ���ָ', 32, 28, 1, True, 12)
    playVoicePrompt(PUT_OFF_FINGER)

    #Take off your finger
    p = 0

    while p != as608.NO_FINGER:
        p = fig.getImage()

    # put on again
    #Get image again
    print('put on your finger again, please...')
    oledShowText('���ٴΰ�ѹ���ذ�', 17, 28, 1, True, 12)
    playVoicePrompt(PUT_ON_FINGER_AGAIN)

    while p != as608.SUCCESS:
        p = fig.getImage()

    # ָ��ͼƬת��Ϊ����ֵ
    p = fig.image2Character(2)
    if p != as608.SUCCESS:
        SaveResult = 0
        print('image to text failed, exit...')
        playVoicePrompt(FINGER_RECORD_FAIL)
        return 0
    
    print('creating finger model...')
    # ����ָ��ģ��
    p = fig.createModel()
    if p != as608.SUCCESS:
        SaveResult = 0
        print('creating model failed')
        return 0

    print('store finger model...')
    # �洢ָ��ģ��
    p = fig.storeModel(id)
    if p != as608.SUCCESS:
        SaveResult = 0
        # fingerrecordfail
        oledShowText('ָ��¼��ʧ��', 25, 28, 1, True, 12)
        playVoicePromptSync(FINGER_RECORD_FAIL)
        return 0
    SaveResult = 1
    # fingerrecordsuccess
    oledShowText('ָ��¼��ɹ�', 25, 28, 1, True, 12)
    playVoicePromptSync(FINGER_RECORD_SUCCESS)

    return 1

# ָ��ʶ��
def fingerSearch():
    p = as608.FAIL
    print('search finger...')
    print('wait for finger print on the pannel...')
    while p != as608.NO_FINGER:
        p = fig.getImage()

    while p != as608.SUCCESS:
        p = fig.getImage()
        # �����ʶ��ָ�ƹ����б����س�ʼҳ�������ϣ����˳���ѭ��
        if keyEvents['K4'] or keyEvents['K2']:
            return

    print('finger detected')

    p = fig.image2Character(1)
    if p != as608.SUCCESS:
        # ָ��ͼƬת��Ϊ����ֵʧ��
        print('image to text failed, exit...')
        playVoicePrompt(FINGER_SEARCH_FAIL)

        return -1

    # ��ָ�ƿ�������ָ��
    p, id, confidence = fig.search() 
    if p == as608.SUCCESS:
        print('finger id:', id, ' confidence:', confidence)
        # searchfingersuccess
        oledShowText('ָ��ʶ��ɹ�', 32, 28, 1, True, 12)
        playVoicePrompt(FINGER_SEARCH_SUCCESS)
        return id
    else:
        print('no match finger found')
        # fingernotmatch
        oledShowText('ָ��δע��', 32, 28, 1, True, 12)
        playVoicePrompt(FINGER_NOT_MATCH)
        return -1

def promptThread(arg):
    global player, promptName

    while True:
        if promptName:
            prompt = promptName
            promptName = None
            # ������������ڲ���״̬����ֹͣ���ŵ�ǰ��ʾ��
            if player.getState():
                player.stop()

            # ��Ƶ�ļ�·����ʽ����fs:/data/pyamp/resource/xxx.wav��
            player.play(AUDIO_HEADER + resDir + prompt)
            player.waitComplete()
        else:
            utime.sleep(0.1)
            #print('promptThread')
            pass

# ������
if __name__ == '__main__':
    # ϵͳ״̬����ʼ��
    systemState = SYS_INIT
    # OLED��Ļ��ʼ��
    oledInit()

    # ��������ʼ��
    playerInit()

    # �����豸��ʼ��
    uartDev = UART()
    uartDev.open('as608')
    # AS608ָ��ʶ��װ�ó�ʼ��
    fig = as608.AS608(uartDev)
    # ������ʼ��
    keyInit()

    try:
        # �������������߳�
        _thread.stack_size(10 * 1024)
        _thread.start_new_thread(promptThread, ['promptThread'])
    except:
       print("Error: unable to start thread")


    # �������״̬
    clearKeyEvents()
    while True:

        # �԰���ʱ�����д���
        if keyEvents['K1']:
            if systemState == SYS_INIT:
                systemState = SYS_ENROLLING

        if keyEvents['K3']:
            if systemState == SYS_INIT:
                systemState = SYS_DETECTING

        if keyEvents['K4'] or keyEvents['K2']:
            # ���ذ���
            systemState = SYS_INIT

        # ��������ж��¼�
        clearKeyEvents()

        # ϵͳ״̬���л�
        if systemState == SYS_INIT:
            oledShowText('<              >', 2, 28, 1, True, 16)
            oledShowText('ָ��ע��  ָ��ʶ��', 10, 30, 1, False, 12)
            # �ȴ��û�����
            while not keyEventsPending():
                utime.sleep(0.1)
                pass

        elif systemState == SYS_ENROLLING:
            oledShowText('ָ��ע����', 32, 28, 1, True, 12)
            # ���ҿ��п���id
            id = fig.getEmptyPosition()

            # ָ��ע��
            fingerEnroll(id)
            systemState = SYS_INIT
        elif systemState == SYS_DETECTING:
            # ��ʼָ��ʶ��
            oledShowText('ָ��ʶ����', 38, 28, 1, True, 12)
            fingerSearch()
    
    uartDev.close()
    del fig