# ������ƣ�����͵�ǰĿ¼���Ʊ���һ��
NAME := msp432p4111launchpad

#It's useless for now, just use this code for no reason
MODULE               := 1062

# The ARCH of the mcu is used on this board
# ARM: ARM968E-S/Cortex-M0/Cortex-M3/Cortex-M4/Cortex-M4F/Cortex-M7/Cortex-R3
# other: armhflinux/xtensa
# csky: ck802/ck803
# MIPS: MIPS-I
# ������buildĿ¼�鿴��ͬ��aos_tools_chain_*�ļ����鿴
HOST_ARCH            := Cortex-M4

# board��MCU�ͺŻ�������ϵ�У������platform/mcu/ Ŀ¼�µĶ�Ӧ��Ŀ¼���Ʊ���һ��
HOST_MCU_FAMILY      := msp432p4xx

# ���ڶ�bin����ʹ�ã�Ŀǰֻ��kernel��app�������ͣ���ȥexample���֣�������ʱȫ������kernel
$(NAME)_TYPE := kernel

# �忨�Ƿ�֧�ֶ�BIN
SUPPORT_BINS         := no

# MCU���ƣ���ͳ��̵��ͺŹٷ����Ʊ���һ�£��������Զ�����keil/iar����ʱ��оƬѡ��
HOST_MCU_NAME        := MSP432P4111

# �Ƿ�ʹ��VFP
ENABLE_VFP           := 1

# ��Ŀ¼��Ҫ�����Դ��
$(NAME)_SOURCES += aos/board_partition.c \
                   aos/soc_init.c \
                   MSP_EXP432P4111.c \
                   system_msp432p4111.c \
                   board_led_drv.c

GLOBAL_INCLUDES += . \
                   aos/

#Global Defines which is needed by the board driver
GLOBAL_CFLAGS += -D__MSP432P4111__ -DDeviceFamily_MSP432P4x1xI -DSTDIO_UART=0

# AliOS Things support to generate keil/iar project automaticly.
# The following content is optional, which is used for the keil/iar project generate
# Gcc compilation is supported by default

# AliOS Things ֧���Զ�����keil/iar���̡����²���Ϊ��ͬ���뻷���������ļ������ӽű�
# �ò���Ϊ��ѡʵ�֣�����gcc���뻷��ΪĬ��֧�֣���gcc�������ļ������ӽű��������
ifeq ($(COMPILER), armcc)
$(NAME)_SOURCES += startup_msp432p4111_uvision.s    
else ifeq ($(COMPILER), iar)
$(NAME)_SOURCES += startup_msp432p4111_ewarm.c
else
$(NAME)_SOURCES += startup_msp432p4111_gcc.c
endif

ifeq ($(COMPILER),armcc)
$(NAME)_LINK_FILES := startup_msp432p4111_uvision.o
endif

ifeq ($(COMPILER),armcc)
GLOBAL_LDFLAGS += -L --scatter=board/msp432p4111launchpad/MSP432P4111.sct
else ifeq ($(COMPILER),iar)
GLOBAL_LDFLAGS += --config board/msp432p4111launchpad/MSP432P4111.icf
else
GLOBAL_LDFLAGS += -T board/msp432p4111launchpad/MSP432P4111.lds
endif

# yloop needs sal or lwip, module means the Plug-in module Type
sal ?= 1
ifeq (1,$(sal))
$(NAME)_COMPONENTS += sal
module ?= wifi.mk3060
else
GLOBAL_DEFINES += CONFIG_NO_TCPIP
endif

# It's defined by the developer
CONFIG_SYSINFO_PRODUCT_MODEL := ALI_AOS_startup_msp432p4111launchpad
CONFIG_SYSINFO_DEVICE_NAME := msp432p4111launchpad

#GLOBAL_CFLAGS += -DSYSINFO_OS_VERSION=\"$(CONFIG_SYSINFO_OS_VERSION)\"
GLOBAL_CFLAGS += -DSYSINFO_PRODUCT_MODEL=\"$(CONFIG_SYSINFO_PRODUCT_MODEL)\"
GLOBAL_CFLAGS += -DSYSINFO_DEVICE_NAME=\"$(CONFIG_SYSINFO_DEVICE_NAME)\"
