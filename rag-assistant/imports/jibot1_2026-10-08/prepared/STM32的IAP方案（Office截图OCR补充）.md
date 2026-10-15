## 图片 word/media/image1.jpeg
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\4，STM32 IAP学习资料.zip!/4，STM32 IAP学习资料/STM32的IAP方案.doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

0000008x0
闪存物理起始地址
栈顶地址
0x8000004
中断向量表起始
（复位中断向量）
Reset_Handler
递增
非可屏蔽中断向量
NMIException
硬件错误中断向量
HardFaultException
0x8000004+n
复位中断程序入口
Reset_Handler(void)
硬件错误中断程序入口
HardFaultException(void)
xxx中断程序入口
xxxHandler(void)
0x8000004+N
main函数入口
Int main(void)
永不返回
中断请求
电子工程世界
eeworld.com.cn
中国电子开发网（ww.ourde.cn）

## 图片 word/media/image2.jpeg
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\4，STM32 IAP学习资料.zip!/4，STM32 IAP学习资料/STM32的IAP方案.doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

0x8000000
闪存物理起始地址
栈顶地址
0x8000004
中断向量表起始
（复位中断向量）
Reset Handler
递增
非可屏蔽中断向量
NMIIException
硬件错误中断向量
HardFaultException
0x8000000+N
IAP程序main函数入口
Int main(void)
递增
IAP过程
跳转
0x8000004+N+M
新的中断向量表起始
（复位中新向量）
Reset_Handler
复位中断程序入口
递增
Reset_Handler(void)
硬件错误中新程序入口
HardFaultException(void)
xxx中断程序入口
xxxHandler(void)
0x8000004+N+M+n
新程序的main函数入口
Int main(void)
永不返回
中断请求
中国电子开发网（ww.ourdev.cn）

## 图片 word/media/image3.jpeg
来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\005-拓展资料\01-技术文档\4，STM32 IAP学习资料.zip!/4，STM32 IAP学习资料/STM32的IAP方案.doc
本段为图片 OCR 文字，未确定原文页码；识别符号、数字及表格对应须核对原图。

OptionsforTarget'Stm32Usart'
Device
TargetOutputLstingUserC/CAsmLnkerDebugUtities
STMicroelectronicsSTM32F103RB
Code Generation
Xtal (MHz):
Operating system:
None
Use Cross-ModuleOptimization
Use MicroLIB
BigEndian
Use Link-Time CodeGeneration
Read/Only Memory Areas
Read/Wrte Memory Areas
defaultoff-chip
Start
Size
Startup
defaultoff-chip
Size
Nolnit
ROM1:
RAM1:
ROM2:
RAM2:
ROM3:
RAM3:
on-chip
on-chip
IROM1:
0x8002000
0x20000
IRAM1:
x20000000
IROM2:
IRAM2:
OK
Cancel
Defaults
Help
中国电子开发网（wnw.ourdev.cn）
