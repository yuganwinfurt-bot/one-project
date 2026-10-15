## 图片 word/media/image3.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table4.ADC寄存器
寄存器
描述
SR
ADC状态寄存器
CR1
ADC控制寄存器1
CR2
ADC控制寄存器2
SMPR1
ADC采样时间寄存器1
SMPR2
ADC采样时间寄存器2
JOFR1
ADC注入通道偏移寄存器1
JOFR2
ADC注入通道偏移寄存器2
JOFR3
ADC注入通道偏移寄存器3
JOFR4
ADC注入通道偏移寄存器4
HTR
ADC看门狗高阀值寄存器
LTR
ADC看门狗低阀值寄存器
SQR1
ADC规则序列寄存器1
SQR2
ADC规则序列寄存器2
SQR3
ADC规则序列寄存器3
JSQR1
ADC注入序列寄存器
DR1
ADC规则数据寄存器1

## 图片 word/media/image4.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

DR2
ADC规则数据寄存器2
DR3
ADC规则数据寄存器3
DR4
ADC规则数据寄存器4

## 图片 word/media/image5.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table5.ADC固件库函数
函数名
描述
ADCDelnit
将外设ADCx的全部寄存器重设为缺省值
ADC Init
根据ADCInitStruct中指定的参数初始化外设ADCx的寄存器
ADC Structlnit
把ADCInitStruct中的每一个参数按缺省值填入
ADC Cmd
使能或者失能指定的ADC
ADCDMACmd
使能或者失能指定的ADC的DMA请求
ADC ITConfig
使能或者失能指定的ADC的中断

## 图片 word/media/image6.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

ADC_ResetCalibration
重置指定的ADC的校准寄存器
ADC GetResetCalibrationStatus
获取ADC重置校准寄存器的状态
ADC_StartCalibration
开始指定ADC的校准程序
ADC_GetCalibrationStatus
获取指定ADC的校准状态
ADC_SoftwareStartConvCmd
使能或者失能指定的ADC的软件转换启动功能
ADC GetSoftwareStartConvStatus
获取ADC软件转换启动状态
ADC_DiscModeChannelCountConfig
对 ADC规则组通道配置间断模式
ADC_DiscModeCmd
使能或者失能指定的ADC规则组通道的间断模式
设置指定ADC的规则组通道，设置它们的转化顺序和采样时
ADC_RegularChannelConfig
间
ADC_ExternalTrigConvConfig
使能或者失能ADCx的经外部触发启动转换功能
ADC_GetConversionValue
返回最近一次ADCx规则组的转换结果
ADC_GetDuelModeConversionValue
返回最近一次双ADC模式下的转换结果
ADC_AutoInjectedConvCmd
使能或者失能指定ADC在规则组转化后自动开始注入组转换
ADC_InjectedDiscModeCmd
使能或者失能指定 ADC的注入组间断模式
ADC_ExternalTrigInjectedConvConfig
配置ADCx的外部触发启动注入组转换功能
ADC_ExternalTrigInjectedConvCmd
使能或者失能ADCx的经外部触发启动注入组转换功能
ADC_SoftwareStartinjectedConvCmd
使能或者失能ADCx软件启动注入组转换功能
ADC_GetsoftwareStartinjectedConvStatus
获取指定ADC的软件启动注入组转换状态
ADC_InjectedChannleConfig
设置指定ADC的注入组通道，设置它们的转化顺序和采样时
间
ADC_InjectedSequencerLengthConfig
设置注入组通道的转换序列长度
ADC_SetinjectedOffset
设置注入组通道的转换偏移值
ADC GetInjectedConversionValue
返回ADC指定注入通道的转换结果

## 图片 word/media/image7.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

使能或者失能指定单个/全体，规则/注入组通道上的模拟看门
ADC_AnalogWatchdogCmd
狗
ADCAnalogWatchdongThresholdsConfig
设置模拟看门狗的高/低阈值
ADC_AnalogWatchdongSingleChannelCon
对单个ADC通道设置模拟看门狗
fig
ADC TampSensorVrefintCmd
使能或者失能温度传感器和内部参考电压通道
ADC GetFlagStatus
检查制定ADC标志位置1与否
ADC ClearFlag
清除ADCx的待处理标志位
ADC GetITStatus
检查指定的ADC中断是否发生
ADC ClearITPendingBit
清除ADCx的中断待处理位

## 图片 word/media/image8.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

5.备份寄存器
BKP
备份寄存器由10个16位寄存器组成，可用来存储20个字节的用户应用程序数据。他们处在备份域里，
当VDD电源被切断，他们仍然由VBAT维持供电。当系统在待机模式下被唤醒，或系统复位或电源复位
时，他们也不会被复位。
此外，BKP
控制寄存器用来管理侵入检测和RTC
校准功能。

## 图片 word/media/image9.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table53.BKP寄存器
寄存器
描述
DR 1-10
数据后备寄存器1到10
RTCCR
RTC时钟校准寄存器
CR
后备控制寄存器
CSR
后备控制状态寄存器

## 图片 word/media/image10.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table54.BKP库函数
函数名
描述
BKP DeInit
将外设BKP的全部寄存器重设为缺省值
BKP TamperPinLevelConfig
设置侵入检测管脚的有效电平
BKP_TamperPinCmd
使能或者失能管脚的侵入检测功能
BKP ITConfig
使能或者失能侵入检测中断
BKP RTCOutputConfig
选择在侵入检测管脚上输出的RTC时钟源
BKP SetRTCCalibrationValue
设置RTC时钟校准值
BKPWriteBackupRegister
向指定的后备寄存器中写入用户程序数据
BKP_ReadBackupRegister
从指定的后备寄存器中读出数据
BKP_GetFlagStatus
检查侵入检测管脚事件的标志位被设置与否
BKP_ClearFlag
清除侵入检测管脚事件的待处理标志位
BKP GetITStatus
检查侵入检测中断发生与否
BKPClearITPendingBit
清除侵侵入检测中断的待处理位

## 图片 word/media/image11.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

控制器局域网（CAN）
本外设作为CAN网络的界面，支持CAN协议2.0A和2.0B。它的设计目标是，以最小的CPU负荷来高
效处理大量收到的报文。它也支持报文发送的优先级要求（优先级特性可软件配置）。
Section6.1描述了CAN固件函数库所使用的数据结构，Section6.2固件库函数介绍了函数库里的所有函
数。

## 图片 word/media/image12.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table70.CAN寄存器
寄存器
描述
CAN_MCR
CAN主控制寄存器
CAN_MSR
CAN主状态寄存器
CAN_TSR
CAN发送状态寄存器
CAN_RFOR
CAN接收FIFOO寄存器
CAN RF1R
CAN接收FIFO1寄存器
CAN_IER
CAN中断允许寄存器
CAN_ESR
CAN错误状态寄存器
CAN_BTR
CAN位时间特性寄存器
TIR
发送邮箱标识符寄存器
TDTR
发送邮箱数据长度和时间戳寄存器
TDLR
发送邮箱低字节数据寄存器
TDHR
发送邮箱高字节数据寄存器
RIR
接收FIFO邮箱标识符寄存器
RDTR
接收FIFO邮箱数据长度和时间戳寄存器
RDLR
接收FIFO邮箱低字节数据寄存器
RDHR
接收FIFO邮箱高字节数据寄存器
CAN_FMR
CAN过滤器主控寄存器
CAN_FMOR
CAN过滤器模式寄存器
CAN_FSCOR
CAN过滤器位宽寄存器
CAN_FFAOR
CAN过滤器FIFO关联寄存器
CAN_FAOR
CAN过滤器激活寄存器
CAN_FRO
过滤器组0寄存器
CAN_FR1
过滤器组1寄存器

## 图片 word/media/image13.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table71.CAN库函数
函数名
描述
CAN Delnit
将外设CAN的全部寄存器重设为缺省值
CAN_Init
根据CANInitStruct中指定的参数初始化外设CAN的寄存器
CAN Filterlnit
根据CANFilterInitStruct中指定的参数初始化外设CAN的寄存器
CAN StructInit
把CANInitStruct中的每一个参数按缺省值填入
CAN ITConfig
使能或者失能指定的CAN中断
CAN Transmit
开始一个消息的传输
CAN TransmitStatus
检查消息传输的状态
CAN CancelTransmit
取消一个传输请求
CAN FIFORelease
释放一个FFO
CAN_MessagePending
返回挂号的信息数量
CAN_Receive
接收一个消息
CAN_Sleep
使CAN进入低功耗模式
CAN_WakeUp
将CAN唤醒
CAN_GetFlagStatus
检查指定的CAN标志位被设置与否
CAN_ClearFlag
清除CAN的待处理标志位
CAN GetITStatus
检查指定的CAN中断发生与否
CAN_ClearITPendingBit
清除CAN的中断待处理标志位

## 图片 word/media/image14.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

DIMA控制器
（DMA）
DMA
控制器提供7个数据通道的访问。由于外设实现了向存储器的映射，因此数据对来自或者发向外设
的数据传输，也可以像内存之间的数据传输一样管理。

## 图片 word/media/image15.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table104.DMA寄存器
寄存器
描述
ISR
DMA中断状态寄存器
IFCR
DMA中断标志位清除寄存器
CCRx
DMA通道x设置寄存器
CNDTRx
DMA通道x待传输数据数目寄存器
CPARx
DMA通道x外设地址寄存器
CMARx
DMA通道x内存地址寄存器

## 图片 word/media/image16.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table105.DMA库函数
函数名
描述
DMA Delnit
将DMA的通道x寄存器重设为缺省值
DMA Init
根据DMAInitStruct中指定的参数初始化DMA的通道x寄存器
DMA StructInit
把DMAInitStruct中的每一个参数按缺省值填入
DMA Cmd
使能或者失能指定的通道x
DMA ITConfig
使能或者失能指定的通道x中断
DMA GetCurrDataCounte
返回当前DMA通道x剩余的待传输数据数目
DMAGetFlagStatus
检查指定的DMA通道x标志位设置与否
DMA ClearFlag
清除DMA通道x待处理标志位
DMA GetITStatus
检查指定的DMA通道x中断发生与否
DMA ClearITPendingBit
清除DMA通道x中断待处理标志位

## 图片 word/media/image17.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

外部中断/事件控制器
8
（EXTI)
外部中断/事件控制器由19个产生事件/中断要求的边沿检测器组成。每个输入线可以独立地配置输入类型
（脉冲或挂起）和对应的触发事件（上升沿或下降沿或者双边沿都触发）。每个输入线都可以被独立的屏
蔽。挂起寄存器保持着状态线的中断要求。

## 图片 word/media/image18.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table128.EXTI寄存器
寄存器
描述
IMR
中断屏蔽寄存器
EMR
事件屏蔽寄存器
RTSR
上升沿触发选择寄存器
FTSR
下降沿触发选择寄存器
SWIR
软件中断事件寄存器
PR
挂起寄存器

## 图片 word/media/image19.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table129.EXTI库函数
函数名
描述
EXTI DeInit
将外设EXTI寄存器重设为缺省值
EXTI Init
根据EXTIInitStruct中指定的参数初始化外设EXTI寄存器
EXTIStructlnit
把EXTIInitStruct中的每一个参数按缺省值填入
EXTIGenerateSWInterrupt
产生一个软件中断
EXTIGetFlagStatus
检查指定的EXTI线路标志位设置与否
EXTI ClearFlag
清除EXTI线路挂起标志位
EXTIGetITStatus
检查指定的EXTI线路触发请求发生与否
EXTI ClearITPendingBit
清除EXTI线路挂起位

## 图片 word/media/image21.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table142.FLASH寄存器
寄存器
描述
ACR
FLASH访问控制寄存器
KEYR
FPEC密钥寄存器
OPTKEYR
选择字节密钥寄存器
SR
FLASH状态寄存器
CR
FLASH控制寄存器
AR
FLASH地址寄存器
OBR
选择字节和状态寄存器
WRPR
选择字节写保护寄存器
Table143.OptionByte（OB）寄存器
寄存器
描述
RDR
读出选择字节
USER
用户选择字节
Data0
Data0选择字节
Datal
Datal选择字节
WRPO
写保护0选择字节
WRP1
写保护1选择字节

## 图片 word/media/image22.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

WRP2
写保护2选择字节
WRP3
写保护3选择字节

## 图片 word/media/image23.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table144.FLASH库函数
函数名
描述
FLASH_SetLatency
设置代码延时值
FLASH _HalfCycleAccessCmd
使能或者失能FLASH半周期访问
FLASH PrefetchBufferCmd
使能或者失能预取指缓存
FLASH Unlock
解锁FLASH编写擦除控制器
FLASH Lock
锁定FLASH编写擦除控制器
FLASH_ErasePage
擦除一个FLASH页面
FLASH_EraseAlIPages
擦除全部FLASH页面
FLASH_EraseOptionBytes
擦除FLASH选择字节
FLASH _ProgramWord
在指定地址编写一个字
FLASH_ProgramHalfWord
在指定地址编写半字
FLASH_ProgramOptionByteData
在指定FLASH选择字节地址编写半字
FLASH EnableWriteProtection
对期望的页面写保护
FLASH ReadOutProtection
使能或者失能读出保护
编写FLASH用户选择字节：IWDG_SW/RST_STOP
FLASH _UserOptionByteConfig
/RSTSTDBY
FLASH_GetUserOptionByte
返回FLASH用户选择字节的值
FLASH_GetWriteProtectionOptionByte
返回FLASH写保护选择字节的值
FLASH GetReadOutProtectionStatus
检查FLASH读出保护设置与否

## 图片 word/media/image24.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

FLASHGetPrefetchBufferStatus
检查FLASH预取指缓存设置与否
FLASHITConfig
使能或者失能指定FLASH中断
FLASHGetFlagStatus
检查指定的FLASH标志位设置与否
FLASH ClearFlag
清除FLASH待处理标志位
FLASH GetStatus
返回FLASH状态
FLASHWaitForLastOperation
等待某一个Flash操作完成，或者发生TIMEOUT

## 图片 word/media/image25.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

10通用输入/输出 （GPIO)

## 图片 word/media/image26.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table178.GPIO寄存器
寄存器
描述
CRL
端口配置低寄存器
CRH
端口配置高寄存器
IDR
端口输入数据寄存器
ODR
端口输出数据寄存器
BSRR
端口位设置/复位寄存器
BRR
端口位复位寄存器
LCKR
端口配置锁定寄存器
EVCR
事件控制寄存器
MAPR
复用重映射和调试I/O配置寄存器
EXTICR
外部中断线路0-15配置寄存器

## 图片 word/media/image27.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table179.GPIO库函数
函数名
描述
GPIO_DeInit
将外设GPIOx寄存器重设为缺省值
GPIO AFIODeInit
将复用功能（重映射事件控制和EXTI设置）重设为缺省值
GPIO_Init
根据GPIOInitStruct中指定的参数初始化外设GPIOx寄存器
GPIO StructInit
把GPIOInitStruct中的每一个参数按缺省值填入
GPIO_ReadInputDataBit
读取指定端口管脚的输入
GPIO_ReadInputData
读取指定的GPIO端口输入
GPIO_ReadOutputDataBit
读取指定端口管脚的输出
GPIO_ReadOutputData
读取指定的GPIO端口输出
GPIO_SetBits
设置指定的数据端口位
GPIO_ResetBits
清除指定的数据端口位
GPIO WriteBit
设置或者清除指定的数据端口位
GPIO Write
向指定GPIO数据端口写入数据
GPIO_PinLockConfig
锁定GPIO管脚设置寄存器
GPIO_EventOutputConfig
选择GPIO管脚用作事件输出
GPIO_EventOutputCmd
使能或者失能事件输出
GPIO_PinRemapConfig
改变指定管脚的映射
GPIO EXTILineConfig
选择GPIO管脚用作外部中断线路

## 图片 word/media/image28.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

11
内部集成电路
I2C总线接口连接微控制器和串行I2C总线。它提供多主机功能，控制所有I2C总线特定的时序、协议、
仲裁和定时。支持标准和快速两种模式，同时与SMBus2.0兼容。I2C总线有多种用途，包括CRC码的
生成和校验、SMBus(系统管理总线SystemManagementBus)PMBus(电源管理总线PowerManagementBus)。
I2C驱动可以用来通过I2C界面发送和接收数据，还可以返回传输操作的状态。

## 图片 word/media/image29.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table204.I2C寄存器
寄存器
描述
CR1
I2C控制寄存器1
CR2
I2C控制寄存器2
OAR1
I2C自身地址寄存器1
OAR2
I2C自身地址寄存器2
DR
I2C数据寄存器
SR1
I2C状态寄存器1
SR2
I2C状态寄存器2
CCR
I2C时钟控制寄存器
TRISE
I2C上升时间寄存器

## 图片 word/media/image30.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table205.I2C库函数
函数名
描述
I2C Delnit
将外设I2Cx寄存器重设为缺省值
I2C_Init
根据I2CInitStruct中指定的参数初始化外设I2Cx寄存器
I2C_StructInit
把I2CInitStruct中的每一个参数按缺省值填入
12C Cmd
使能或者失能I2C外设
I2C DMACmd
使能或者失能指定I2C的DMA请求
I2C DMALastTransferCmd
使下一次DMA传输为最后一次传输
I2C GenerateSTART
产生I2Cx传输START条件
I2C_GenerateSTOP
产生I2Cx传输STOP条件
I2C_AcknowledgeConfig
使能或者失能指定I2C的应答功能
I2C_OwnAddress2Config
设置指定I2C的自身地址2
I2C DualAddressCmd
使能或者失能指定I2C的双地址模式
I2C GeneralCallCmd
使能或者失能指定I2C的广播呼叫功能
I2C_ITConfig
使能或者失能指定的I2C 中断
I2C SendData
通过外设I2Cx发送一个数据
I2C ReceiveData
返回通过I2Cx最近接收的数据
I2C Send7bitAddress
向指定的从I2C设备传送地址字

## 图片 word/media/image31.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

I2C_ReadRegister
读取指定的I2C寄存器并返回其值
I2C SoftwareResetCmd
使能或者失能指定I2C的软件复位
I2C SMBusAlertConfig
驱动指定I2Cx的SMBusAlert管脚电平为高或低
I2C TransmitPEC
使能或者失能指定I2C的PEC传输
I2C PECPositionConfig
选择指定I2C的PEC位置
I2C CalculatePEC
使能或者失能指定I2C的传输字PEC值计算
I2C GetPEC
返回指定I2C的PEC值
I2C ARPCmd
使能或者失能指定I2C的ARP
I2C StretchClockCmd
使能或者失能指定I2C的时钟延展
I2CFastModeDutyCycleConfig
选择指定I2C的快速模式占空比
I2C GetLastEvent
返回最近一次I2C事件
I2C CheckEvent
检查最近一次I2C事件是否是输入的事件
I2C_GetFlagStatus
检查指定的I2C标志位设置与否
I2C_ClearFlag
清除I2Cx的待处理标志位
I2C_GetITStatus
检查指定的I2C 中断发生与否
I2C ClearITPendingBit
清除I2Cx的中断待处理位

## 图片 word/media/image32.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

12
独立看门狗
(IWDG)
独立看门狗
（IWDG）用来解决应软件或者硬件引起的处理器故障。它也可以在停止（Stop）模式和待命
（Standby)
模式下工作。

## 图片 word/media/image33.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table254.IWDG寄存器
寄存器
描述
KR
IWDG键值寄存器
PR
IWDG预分频寄存器
RLR
IWDG重装载寄存器
SR
IWDG状态寄存器

## 图片 word/media/image34.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table255.IWDG库函数
函数名
描述
IWDGWriteAccessCmd
使能或者失能对寄存器IWDGPR和IWDGRLR的写操作
IWDGSetPrescaler
设置IWDG预分频值
IWDGSetReload
设置IWDG重装载值
IWDGReloadCounter
按照IWDG重装载寄存器的值重装载IWDG计数器
IWDGEnable
使能IWDG
IWDGGetFlagStatus
检查指定的IWDG标志位被设置与否

## 图片 word/media/image35.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

13卡
嵌套向量中断控制器（NVIC）
NVIC 驱动有多种用途：例如使能或者失能IRQ 中断，使能或者失能单独的IRQ通道，改变IRQ通道的优
先级等等。

## 图片 word/media/image36.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table265.NVIC寄存器
寄存器
描述
Enable
中断设置使能寄存器
Disable
中断清除使能寄存器
Set
中断设置待处理寄存器
Clear
中断清除待处理寄存器
Active
中断活动位寄存器
Priority
中断优先级寄存器
CPUID
CPUID基寄存器
IRQControlStatus
中断控制状态寄存器
ExceptionTableOffset
向量表移位寄存器

## 图片 word/media/image37.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

AIRC
应用控制/重置寄存器
SysCtrl
系统控制寄存器
ConfigCtrl
设置控制寄存器
SystemPriority
系统处理优先级寄存器
SysHandlerCtrl
系统处理控制和状态寄存器
ConfigFaultStatus
设置错误状态寄存器
HardFaultStatus
硬件错误状态寄存器
DebugFaultStatus
除错错误寄存器
MemorymanageFaultAddr
存储器管理错误地址寄存器
BusFaultAddr
总线错误地址寄存器

## 图片 word/media/image38.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table266.NVIC库函数
函数名
描述
NVIC_DeInit
将外设NVIC寄存器重设为缺省值
NVIC_SCBDeInit
将外设SCB寄存器重设为缺省值
NVIC_PriorityGroupConfig
设置优先级分组：先占优先级和从优先级
NVIC_Init
根据NVIC_InitStruct中指定的参数初始化外设NVIC寄存器
NVIC_StructInit
把NVIC_InitStruct中的每一个参数按缺省值填入
NVIC_SETPRIMASK
使能PRIMASK优先级：提升执行优先级至0
NVIC_RESETPRIMASK
失能PRIMASK优先级
NVIC_SETFAULTMASK
使能FAULTMASK优先级：提升执行优先级至-1
NVIC RESETFAULTMASK
失能FAULTMASK优先级
NVIC _BASEPRICONFIG
改变执行优先级从N（最低可设置优先级）提升至1
NVIC_GetBASEPRI
返回 BASEPRI屏蔽值
NVIC_GetCurrentPendingIRQChannel
返回当前待处理IRQ标识符
NVIC_GetIRQChannelPendingBitStatus
检查指定的IRQ通道待处理位设置与否
NVIC_SetIRQChannelPendingBit
设置指定的IRQ通道待处理位
NVIC_ClearIRQChannelPendingBit
清除指定的IRQ通道待处理位
NVIC GetCurrentActiveHandler
返回当前活动的Handler（IRQ通道和系统Handler）的标识符
NVIC_GetIRQChannelActiveBitStatus
检查指定的IRQ通道活动位设置与否
NVIC_GetCPUID
返回ID号码，Cortex-M3内核的版本号和实现细节
NVIC_SetVectorTable
设置向量表的位置和偏移
NVIC_GenerateSystemReset
产生一个系统复位
NVIC_GenerateCoreReset
产生一个内核（内核+NVIC）复位
NVIC_SystemLPConfig
选择系统进入低功耗模式的条件
NVIC_SystemHandlerConfig
使能或者失能指定的系统Handler
NVIC_SystemHandlerPriorityConfig
设置指定的系统Handler优先级

## 图片 word/media/image39.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

NVIC GetSystemHandlerPendingBitStatus
检查指定的系统Handler待处理位设置与否
NVIC SetSystemHandlerPendingBit
设置系统Handler待处理位
NVIC ClearSystemHandlerPendingBit
清除系统Handler待处理位
NVIC GetSystemHandlerActiveBitStatus
检查系统Handler活动位设置与否
NVIC GetFaultHandlerSources
返回表示出错的系统Handler源
NVIC GetFaultAddress
返回产生表示出错的系统Handler所在位置的地址

## 图片 word/media/image40.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

14
功耗控制
(PWR)
PWR有多种用途，包括功耗管理和低功耗模式选择。

## 图片 word/media/image41.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table321.PWR寄存器
寄存器
描述
CR
功耗控制寄存器
CSR
功耗控制状态寄存器

## 图片 word/media/image42.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table322.PWR库函数
函数名
描述
PWR Delnit
将外设PWR寄存器重设为缺省值
PWR BackupAccessCmd
使能或者失能RTC和后备寄存器访问
PWR PVDCmd
使能或者失能可编程电压探测器（PVD）
PWR PVDLevelConfig
设置PVD的探测电压闽值
PWR_WakeUpPinCmd
使能或者失能唤醒管脚功能
PWR EnterSTOPMode
进入停止（STOP）模式
PWREnterSTANDBYMode
进入待命（STANDBY）模式
PWRGetFlagStatus
检查指定PWR标志位设置与否
PWR ClearFlag
清除PWR的待处理标志位

## 图片 word/media/image44.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table336.RCC寄存器
寄存器
描述
CR
时钟控制寄存器
CFGR
时钟配置寄存器
CIR
时钟中断寄存器
APB2RSTR
APB2外设复位寄存器
APBIRSTR
APB1外设复位寄存器
AHBENR
AHB外设时钟使能寄存器
APB2ENR
APB2外设时钟使能寄存器
APB1ENR
APB1外设时钟使能寄存器
BDCR
备份域控制寄存器
CSR
控制/状态寄存器

## 图片 word/media/image45.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table337.RCC库函数
函数名
描述
RCC_Delnit
将外设RCC寄存器重设为缺省值
RCC_HSEConfig
设置外部高速晶振（HSE)
RCC_WaitForHSEStartUp
等待HSE起振
RCC_AdjustHSICalibration Value
调整内部高速晶振（HSI）校准值
RCC_HSICmd
使能或者失能内部高速晶振(HSI)
RCC_PLLConfig
设置PLL时钟源及倍频系数
RCC_PLLCmd
使能或者失能PLL
RCC_SYSCLKConfig
设置系统时钟（SYSCLK）
RCC_GetSYSCLKSource
返回用作系统时钟的时钟源
RCC _HCLKConfig
设置AHB时钟（HCLK）
RCC_PCLK1Config
设置低速AHB 时钟（PCLK1)
RCC _PCLK2Config
设置高速AHB时钟（PCLK2）
RCC_ITConfig
使能或者失能指定的RCC 中断
RCC_USBCLKConfig
设置USB时钟（USBCLK)
RCC_ADCCLKConfig
设置ADC时钟（ADCCLK）
RCC_LSEConfig
设置外部低速晶振（LSE）
RCC_LSICmd
使能或者失能内部低速晶振 (LSI)
RCC_RTCCLKConfig
设置RTC时钟（RTCCLK）
RCC_RTCCLKCmd
使能或者失能RTC 时钟
RCC_GetClocksFreq
返回不同片上时钟的频率
RCC_AHBPeriphClockCmd
使能或者失能 AHB 外设时钟
RCC_APB2PeriphClockCmd
使能或者失能APB2外设时钟
RCC_APB1PeriphClockCmd
使能或者失能APB1外设时钟

## 图片 word/media/image46.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

RCC APB2PeriphResetCmd
强制或者释放高速APB（APB2）外设复位
RCC APB1PeriphResetCmd
强制或者释放低速APB（APB1）外设复位
RCC BackupResetCmd
强制或者释放后备域复位
RCC_ClockSecuritySystemCmd
使能或者失能时钟安全系统
RCC MCOConfig
选择在MCO管脚上输出的时钟源
RCC GetFlagStatus
检查指定的RCC标志位设置与否
RCC ClearFlag
清除RCC的复位标志位
RCC GetITStatus
检查指定的RCC中断发生与否
RCC ClearITPendingBit
清除RCC的中断待处理位

## 图片 word/media/image47.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

16
实时时钟
中(RTC)
RTC
提供了一系列连续工作的计数器，配合适当的软件，具有提供时钟-日历的功能。写入计数器的值可
以设置整个系统的时间/日期。

## 图片 word/media/image48.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table389.RTC寄存器
寄存器
描述
CRH
控制寄存器高位
CRL
控制寄存器低位
PRLH
预分频装载寄存器高位
PRLL
预分频装载寄存器低位
DIVH
预分频分频因子寄存器高位
DIVL
预分频分频因子寄存器低位
CNTH
计数器寄存器高位
CNTL
计数器寄存器低位
ALRH
闹钟寄存器高位
ALRL
闹钟寄存器低位

## 图片 word/media/image49.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table390.RTC库函数
函数名
描述
RTC_ITConfig
使能或者失能指定的RTC中断
RTC_EnterConfigMode
进入RTC配置模式
RTC_ExitConfigMode
退出RTC配置模式
RTC GetCounter
获取RTC计数器的值
RTC SetCounter
设置RTC计数器的值
RTC SetPrescaler
设置RTC预分频的值
RTC_SetAlarm
设置RTC闹钟的值
RTC GetDivider
获取RTC预分频分频因子的值
RTC WaitForLastTask
等待最近一次对RTC寄存器的写操作完成
RTC_WaitForSynchro
等待RTC寄存器(RTC CNT，RTC ALR and RTC PRL)与
RTC的APB时钟同步
RTC_GetFlagStatus
检查指定的RTC标志位设置与否
RTC_ClearFlag
清除RTC的待处理标志位
RTC GetITStatus
检查指定的RTC中断发生与否
RTC_ClearITPendingBit
清除RTC的中断待处理位

## 图片 word/media/image50.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

17串行外设接口
I(SPI)
串行外设接口（SPI）提供与外部设备进行同步串行通讯的功能。接口可以被设置工作在主模式或者从模
式。

## 图片 word/media/image51.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table407.SPI寄存器
寄存器
描述
CR1
SPI控制寄存器1
CR2
SPI控制寄存器2
SR
SPI状态寄存器
DR
SPI数据寄存器
CRCPR
SPICRC多项式寄存器
RxCRCR
SPI接收CRC寄存器
TxCRCR
SPI发送CRC寄存器

## 图片 word/media/image52.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table408.SPI库函数
函数名
描述
SPI _DeInit
将外设SPIx寄存器重设为缺省值
SPI_Init
根据SPI_InitStruct 中指定的参数初始化外设SPIx寄存器
SPI_StructInit
把 SPIInitStruct中的每一个参数按缺省值填入
SPI_Cmd
使能或者失能 SPI外设
SPI_ITConfig
使能或者失能指定的 SPI中断
SPI _DMACmd
使能或者失能指定SPI的DMA请求
SPI SendData
通过外设SPIx发送一个数据
SPI ReceiveData
返回通过SPIx最近接收的数据
SPI DMALastTransferCmd
使下一次DMA传输为最后一次传输
SPI_NSSInternalSoftwareConfig
为选定的 SPI软件配置内部NSS 管脚
SPI_SSOutputCmd
使能或者失能指定的 SPISS 输出
SPI_DataSizeConfig
设置选定的 SPI数据大小
SPI_TransmitCRC
发送 SPIx的 CRC值
SPI CalculateCRC
使能或者失能指定SPI的传输字CRC值计算
SPI_GetCRC
返回指定SPI的发送或者接受CRC寄存器值
SPI_GetCRCPolynomial
返回指定SPI的CRC多项式寄存器值
SPI_BiDirectionalLineConfig
选择指定SPI在双向模式下的数据传输方向
SPI_GetFlagStatus
检查指定的SPI标志位设置与否
SPI_ClearFlag
清除 SPIx的待处理标志位
SPI_GetITStatus
检查指定的 SPI中断发生与否
SPI ClearITPendingBit
清除 SPIx的中断待处理位

## 图片 word/media/image53.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

18 Cortex3
系统定时器
器(SysTick)
SysTick提供1个24位、降序、零约束、写清除的计数器，具有灵活的控制机制。

## 图片 word/media/image54.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table446.SysTick寄存器
寄存器
描述
CTRL
SysTick控制和状态寄存器
LOAD
SysTick重装载值寄存器
VAL
SysTick当前值寄存器
CALIB
SysTick校准值寄存器

## 图片 word/media/image55.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table447.SysTick库函数
函数名
描述
SysTick_CLKSourceConfig
设置SysTick时钟源
SysTick SetReload
设置SysTick重装载值
SysTick_CounterCmd
使能或者失能SysTick计数器
SysTick_ITConfig
使能或者失能SysTick中断
SysTick GetCounter
获取SysTick计数器的值
SysTick_GetFlagStatus
检查指定的SysTick标志位设置与否

## 图片 word/media/image56.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

19
通用定时器
(TIM)
通用定时器是一个通过可编程预分频器驱动的16位自动装载计数器构成。
它适用于多种场合，包括测量输入信号的脉冲长度（输入采集）或者产生输出波形
输出比较和PWM）。
使用定时器预分频器和RCC时钟控制器预分频器，脉冲长度和波形周期可以在
几个微秒到几个毫秒间调整。

## 图片 word/media/image57.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table457.TIM寄存器
寄存器
描述
CR1
控制寄存器1
CR2
控制寄存器2
SMCR
从模式控制寄存器
DIER
DMA/中断使能寄存器
SR
状态寄存器
EGR
事件产生寄存器
CCMR1
捕获/比较模式寄存器1
CCMR2
捕获/比较模式寄存器2
CCER
捕获/比较使能寄存器
CNT
计数器寄存器
PSC
预分频寄存器
APR
自动重装载寄存器
CCR1
捕获/比较寄存器1
CCR2
捕获/比较寄存器2
CCR3
捕获/比较寄存器3
CCR4
捕获/比较寄存器4
DCR
DMA控制寄存器
DMAR
连续模式的DMA地址寄存器

## 图片 word/media/image59.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

TIMForcedOC3Config
置TIMx输出3为活动或者非活动电平
TIMForcedOC4Config
置TIMx输出4为活动或者非活动电平
TIMARRPreloadConfig
使能或者失能TIMx在ARR上的预装载寄存器
TIM SelectCCDMA
选择TIMx外设的捕获比较DMA源
TIMOCiPreloadConfig
使能或者失能TIMx在CCR1上的预装载寄存器
TIMOC2PreloadConfig
使能或者失能TIIMx在CCR2上的预装载寄存器
TIMOC3PreloadConfig
使能或者失能TIMx在CCR3上的预装载寄存器
TIMOC4PreloadConfig
使能或者失能TIMx在CCR4上的预装载寄存器
TIMOCiFastConfig
设置TIMx捕获比较1快速特征

## 图片 word/media/image60.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

TIM_OC2FastConfig
设置TIMx捕获比较2快速特征
TIM_OC3FastConfig
设置TIMx捕获比较3快速特征
TIM_OC4FastConfig
设置 TIMx捕获比较4快速特征
TIM_ClearOCiRef
在一个外部事件时清除或者保持OCREF1信号
TIM_ClearOC2Ref
在一个外部事件时清除或者保持OCREF2信号
TIM_ClearOC3Ref
在一个外部事件时清除或者保持OCREF3信号
TIM_ClearOC4Ref
在一个外部事件时清除或者保持OCREF4信号
TIM_UpdateDisableConfig
使能或者失能TIMx更新事件
TIM_EncoderlnterfaceConfig
设置TIMx编码界面
TIM_GenerateEvent
设置 TIMx事件由软件产生
TIM_OC1PolarityConfig
设置TIMx通道1极性
TIM_OC2PolarityConfig
设置TIMx通道2极性
TIM_OC3PolarityConfig
设置TIMx通道3极性
TIM_OC4PolarityConfig
设置TIMx通道4极性
TIM_UpdateRequestConfig
设置TIMx更新请求源
TIM_SelectHallSensor
使能或者失能TIMx霍尔传感器接口
TIM_SelectOnePulseMode
设置TIMx单脉冲模式
TIM_SelectOutputTrigger
选择 TIMx触发输出模式
TIM_SelectSlaveMode
选择TIMx从模式
TIM_SelectMasterSlaveMode
设置或者重置TIMx主/从模式
TIM_SetCounter
设置TIMx计数器寄存器值
TIM_SetAutoreload
设置TIMx自动重装载寄存器值
TIM_SetCompare1
设置TIMx捕获比较1寄存器值
TIM_SetCompare2
设置TIMx捕获比较2寄存器值

## 图片 word/media/image61.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

TIM_SetCompare3
设置TIMx捕获比较3寄存器值
TIM_SetCompare4
设置TIMx捕获比较4寄存器值
TIM SetICiPrescaler
设置TIMx输入捕获1预分频
TIM SetIC2Prescaler
设置TIMx输入捕获2预分频
TIM SetIC3Prescaler
设置TIMx输入捕获3预分频
TIM SetIC4Prescaler
设置TIMx输入捕获4预分频
TIM SetClockDivision
设置TIMx的时钟分割值
TIM_GetCapture1
获得TIMx输入捕获1的值
TIM_GetCapture2
获得TIMx输入捕获2的值
TIM GetCapture3
获得TIMx输入捕获3的值
TIM_GetCapture4
获得TIMx输入捕获4的值
TIM_GetCounter
获得TIMx计数器的值
TIM GetPrescaler
获得TIMx预分频值
TIM_GetFlagStatus
检查指定的TIM标志位设置与否
TIM ClearFlag
清除TIMx的待处理标志位
TIM GetITStatus
检查指定的TIM中断发生与否
TIM_ClearITPendingBit
清除TIMx的中断待处理位

## 图片 word/media/image62.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

20
高级控制定时器
(TIM1)
高级控制定时器（TIM1）由一个16位的自动装载计数器组成，它由一个可编程预分
频器驱动。
它适合多种用途，包含测量输入信号的脉冲宽度（输入捕获），或者产生输出波形（输出比较，PWM，嵌入死
区时间的互补PWM等）。
使用定时器预分频器和RCC时钟控制预分频器，可以实现脉冲宽度和波形周期从几个微秒到儿个毫秒的调
节

## 图片 word/media/image63.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

21通用同步异步收发器
USART)
通用同步异步收发器（USART）提供了一种灵活的方法来与使用工业标准NRZ异步串行数据格式的外部
设备之间进行全双工数据交换。USART利用分数波特率发生器提供宽范围的波特率选择。它支持同步单
向通信和半双工单线通信。它也支持LIN（局部互连网），智能卡协议和IrDA（红外数据组织)SIRENDEC规
范，以及调制解调器（CTS/RTS)操作。它还允许多处理器通信。使用多缓冲器配置的DMA方式，可以实
现高速数据通信。

## 图片 word/media/image64.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table704.USART寄存器
寄存器
描述
SR
USART状态寄存器
DR
USART数据寄存器
BRR
USART波特率寄存器
CR1
USART控制寄存器1
CR2
USART控制寄存器2
CR3
USART控制寄存器3
GTPR
USART保护时间和预分频寄存器

## 图片 word/media/image65.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table705.USART库函数
函数名
描述
USART DeInit
将外设USARTx寄存器重设为缺省值
USART Init
根据USARTInitStruct中指定的参数初始化外设USARTx寄存
器
USART StructInit
把USARTInitStruct中的每一个参数按缺省值填入
USART Cmd
使能或者失能USART外设
USART ITConfig
使能或者失能指定的USART中断
USART DMACmd
使能或者失能指定USART的DMA请求
USART SetAddress
设置USART节点的地址
USART WakeUpConfig
选择USART的唤醒方式
USART ReceiverWakeUpCmd
检查USART是否处于静默模式
USARTLINBreakDetectLengthConfig
设置USARTLIN中断检测长度
USART LINCmd
使能或者失能USARTx的LIN模式
USART SendData
通过外设USARTx发送单个数据

## 图片 word/media/image66.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

USART ReceiveData
返回USARTx最近接收到的数据
USART SendBreak
发送中断字
USARTSetGuardTime
设置指定的USART保护时间
USART SetPrescaler
设置USART时钟预分频
USART SmartCardCmd
使能或者失能指定USART的智能卡模式
USART SmartCardNackCmd
使能或者失能NACK传输
USARTHalfDuplexCmd
使能或者失能USART半双工模式
USART_IrDAConfig
设置USARTIrDA模式
USART IrDACmd
使能或者失能USARTIrDA模式
USARTGetFlagStatus
检查指定的USART标志位设置与否
USART ClearFlag
清除USARTx的待处理标志位
USART GetITStatus
检查指定的USART中断发生与否
USART ClearITPendingBit
清除USARTx的中断待处理位

## 图片 word/media/image67.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

22
窗口看门狗
(WWDG)
窗口看门狗用来检测是否发生过软件错误。通常软件错误是由外部干涉或者不可预见的逻辑冲突引起的，
这些错误将打断正常的程序流程。

## 图片 word/media/image58.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table458.TIM库函数
函数名
描述
TIM_Delnit
将外设TIMx寄存器重设为缺省值
根据TIMTimeBaseInitStruct中指定的参数初始化TIMx的时
TIM_TimeBaselnit
间基数单位
TIM_OCInit
根据TIM_OCInitStruct中指定的参数初始化外设TIMx
TIM_ICInit
根据TIM_ICInitStruct中指定的参数初始化外设TIMx
TIM_TimeBaseStructInit
把TIMTimeBaseInitStruct中的每一个参数按缺省值填入
TIM_OCStructInit
把TIMOCInitStruct中的每一个参数按缺省值填入
TIM_ICStructInit
把TIM_ICInitStruct中的每一个参数按缺省值填入
TIM_Cmd
使能或者失能TIMx外设
TIM _ITConfig
使能或者失能指定的TIM中断
TIM_DMAConfig
设置TIMx的DMA接口
TIM_DMACmd
使能或者失能指定的 TIMx的DMA请求
TIM _IntemalClockConfig
设置 TIMx内部时钟
TIM_ITRxExternalClockConfig
设置 TIMx内部触发为外部时钟模式
TIM_TIxExtermalClockConfig
设置 TIMx触发为外部时钟
TIM_ETRClockModelConfig
配置TIMx外部时钟模式1
TIM_ETRClockMode2Config
配置TIMx外部时钟模式2
TIM_ETRConfig
配置TIMx外部触发
TIM_SelectInputTrigger
选择TIMx输入触发源
TIM_PrescalerConfig
设置TIMx预分频
TIM_CounterModeConfig
设置TIMx计数器模式
TIM_ForcedOC1Config
置 TIMx输出1为活动或者非活动电平
TIM_ForcedOC2Config
置TIMx输出2为活动或者非活动电平

## 图片 word/media/image69.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table750.WWDG库函数
函数名
描述
WWDGDelnit
将外设WWDG寄存器重设为缺省值
WWDGSetPrescaler
设置WWDG预分频值
WWDGSetWindowValue
设置WWDG窗口值
WWDGEnableIT
使能WWDG早期唤醒中断（EWI)
WWDGSetCounter
设置WWDG计数器值
WWDG Enable
使能WWDG并装入计数器值
WWDGGetFlagStatus
检查WWDG早期唤醒中断标志位被设置与否
WWDGClearFlag
清除早期唤醒中断标志位

## 图片 word/media/image1.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table1.本文档所有缩写定义
缩写
外设/单元
ADC
模数转换器
BKP
备份寄存器
CAN
控制器局域网模块
DMA
直接内存存取控制器
EXTI
外部中断事件控制器
FLASH
闪存存储器
GPIO
通用输入输出
I2C
内部集成电路
IWDG
独立看门狗
NVIC
嵌套中断向量列表控制器
PWR
电源/功耗控制
RCC
复位与时钟控制器
RTC
实时时钟
SPI
串行外设接口
SysTick
系统嘀嗒定时器
TIM
通用定时器
TIM1
高级控制定时器
USART
通用同步异步接收发射端
WWDG
窗口看门狗

## 图片 word/media/image2.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

模拟/数字转换器
模拟/数字转换器
：（ADC）是一种提供可选择多通道输入，逐次逼近型的模数转换器。分辨率为12位。

## 图片 word/media/image68.png
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\1，STM32F1xx固件库.zip!/1，STM32F1xx固件库/Stm32寄存器与库函数概览(摘自固件库使用手册).doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

Table749.WWDG寄存器
寄存器
描述
CR
WWDG控制寄存器
CFR
WWDG设置寄存器
SR
WWDG状态寄存器
