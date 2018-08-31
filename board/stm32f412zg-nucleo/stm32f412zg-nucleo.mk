NAME := stm32f412zg-nucleo


$(NAME)_TYPE := kernel
MODULE               := 1062
HOST_ARCH            := Cortex-M4
HOST_MCU_FAMILY      := stm32f4xx_cube
SUPPORT_BINS         := no
HOST_MCU_NAME        := STM32F412ZGTX
ENABLE_VFP           := 1

$(NAME)_SOURCES += aos/board_partition.c \
                   aos/soc_init.c
                   
$(NAME)_SOURCES += Src/stm32f4xx_hal_msp.c \
                   Src/gpio.c \
                   Src/usart.c \
                   Src/i2c.c \
                   Src/usb_otg.c \
                   Src/main.c

$(NAME)_SOURCES += drv/board_drv_led.c

sal ?= 1
ifeq (1,$(sal))
$(NAME)_COMPONENTS += sal
module ?= wifi.mk3060
endif



                   
ifeq ($(COMPILER), armcc)
$(NAME)_SOURCES += startup_stm32f412zx_keil.s    
else ifeq ($(COMPILER), iar)
$(NAME)_SOURCES += startup_stm32f412xx_iar.s  
else
$(NAME)_SOURCES += startup_stm32f412zx.s
endif

GLOBAL_INCLUDES += . \
                   hal/ \
                   aos/ \
                   Inc/
				   
GLOBAL_CFLAGS += -DSTM32F412Zx -DCENTRALIZE_MAPPING



ifeq ($(COMPILER),armcc)
GLOBAL_LDFLAGS += -L --scatter=board/stm32f412zg-nucleo/stm32f412zx.sct
else ifeq ($(COMPILER),iar)
GLOBAL_LDFLAGS += --config board/stm32f412zg-nucleo/STM32L412.icf
else
GLOBAL_LDFLAGS += -T board/stm32f412zg-nucleo/STM32F412ZGTx_FLASH.ld
endif



CONFIG_SYSINFO_PRODUCT_MODEL := ALI_AOS_f412-nucleo
CONFIG_SYSINFO_DEVICE_NAME := f412-nucleo

GLOBAL_CFLAGS += -DSYSINFO_OS_VERSION=\"$(CONFIG_SYSINFO_OS_VERSION)\"
GLOBAL_CFLAGS += -DSYSINFO_PRODUCT_MODEL=\"$(CONFIG_SYSINFO_PRODUCT_MODEL)\"
GLOBAL_CFLAGS += -DSYSINFO_DEVICE_NAME=\"$(CONFIG_SYSINFO_DEVICE_NAME)\"
