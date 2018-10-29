ifeq ($(HOST_OS),Win32)
SCAT := "$(SOURCE_ROOT)/platform/mcu/$(HOST_MCU_FAMILY)/merge_fw/srec_cat.exe"
else #
$(error not surport for $(HOST_OS))
endif # Win32

CLONER_BIN_FILE		:= "$(SOURCE_ROOT)/platform/mcu/$(HOST_MCU_FAMILY)/merge_fw/AOS_Bootloader_Cloner.bin"
BOOTLOADER_BIN_FILE	:= "$(SOURCE_ROOT)/platform/mcu/$(HOST_MCU_FAMILY)/merge_fw/AOS_Bootloader_LDROM.bin"

CRC_BIN_OUTPUT_FILE := $(LINK_OUTPUT_FILE:$(LINK_OUTPUT_SUFFIX)=_crc$(BIN_OUTPUT_SUFFIX))
OTA_BIN_OUTPUT_FILE := $(LINK_OUTPUT_FILE:$(LINK_OUTPUT_SUFFIX)=.ota$(BIN_OUTPUT_SUFFIX))
OTA_MD5_BIN_OUTPUT_FILE := $(LINK_OUTPUT_FILE:$(LINK_OUTPUT_SUFFIX)=.ota.md5$(BIN_OUTPUT_SUFFIX))

OTA_MD5_HEX_OUTPUT_FILE := $(LINK_OUTPUT_FILE:$(LINK_OUTPUT_SUFFIX)=.ota.md5.hex)
CLONER_HEX_OUTPUT_FILE := $(OUTPUT_DIR)/binary/AOS_Bootloader_Cloner.hex
BOOTLOADER_HEX_OUTPUT_FILE :=$(OUTPUT_DIR)/binary/AOS_Bootloader_LDROM.hex
AOS_HEX_OUTPUT_FILE := $(OUTPUT_DIR)/binary/Merged_AOS.hex

EXTRA_POST_BUILD_TARGETS += gen_crc_bin
gen_crc_bin:
	$(QUIET)$(CP) $(BIN_OUTPUT_FILE) $(OTA_BIN_OUTPUT_FILE)
	python $(SCRIPTS_PATH)/ota_gen_md5_bin.py $(OTA_BIN_OUTPUT_FILE)
	
EXTRA_POST_BUILD_TARGETS += merge_aos_to_hex
merge_aos_to_hex:
	$(SCAT)	$(OTA_MD5_BIN_OUTPUT_FILE) 	-binary -offset 0x0 	-output $(OTA_MD5_HEX_OUTPUT_FILE) -Intel
	$(SCAT)	$(CLONER_BIN_FILE) 	-binary -offset 0x7c000 	-output $(CLONER_HEX_OUTPUT_FILE) -Intel
	$(SCAT)	$(BOOTLOADER_BIN_FILE) 		-binary -offset 0x100000 	-output $(BOOTLOADER_HEX_OUTPUT_FILE) -Intel

	echo "$(SCAT)	$(OTA_MD5_HEX_OUTPUT_FILE) -Intel $(CLONER_HEX_OUTPUT_FILE) -Intel $(BOOTLOADER_HEX_OUTPUT_FILE) -Intel -output $(AOS_HEX_OUTPUT_FILE) -Intel"
	$(SCAT)	$(OTA_MD5_HEX_OUTPUT_FILE) -Intel $(CLONER_HEX_OUTPUT_FILE) -Intel $(BOOTLOADER_HEX_OUTPUT_FILE) -Intel -output $(AOS_HEX_OUTPUT_FILE) -Intel
