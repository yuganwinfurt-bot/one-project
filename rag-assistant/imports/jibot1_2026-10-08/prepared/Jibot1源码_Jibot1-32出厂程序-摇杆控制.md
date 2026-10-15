## z_adc.c | 文件开头/全局定义 | 原文件第1-31行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/src/z_adc.c
以下为原始源码，不是截图OCR。
```
1: /*
2: 	通道对照表：
3: 	ch0-PA0
4: 	ch1-PA1
5: 	ch2-PA2
6: 	ch3-PA3
7: 	ch4-PA4
8: 	ch5-PA5
9: 	ch6-PA6
10: 	ch7-PA7
11: 	ch8-PB0
12: 	ch9-PB1
13: 	ch10-PC0
14: 	ch11-PC1
15: 	ch12-PC2
16: 	ch13-PC3
17: 	ch14-PC4
18: 	ch15-PC5
19: 	
20: 	ch16-温度传感器
21: 	ch17-内部参照电压
22: 	
23: 	需要修改的数据 
24: 	1、ADC_NUM 通道数量
25: 	2、ADC1_Configuration 中的通道配置，和ADC_NUM数量保持一致
26: 	3、数据直接获取数组 ADC_ConvertedValue
27: 	
28: */
29: 
30: #include "z_adc.h"
31: 
```

## z_adc.c | 文件开头/全局定义 | 原文件第32-34行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/src/z_adc.c
以下为原始源码，不是截图OCR。
```
32: #define ADC1_DR_Address ((u32)0x40012400+0x4c)
33: u16 ADC_ConvertedValue[2] = {0};
34: 
```

## z_adc.c | ADC_init | 原文件第35-40行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/src/z_adc.c
以下为原始源码，不是截图OCR。
```
35: void ADC_init(void) {
36: 	ADC1_GPIO_Configuration();
37: 	DMA_Configuration();
38: 	ADC1_Configuration();
39: }
40: 
```

## z_adc.c | ADC1_GPIO_Configuration | 原文件第41-53行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/src/z_adc.c
以下为原始源码，不是截图OCR。
```
41: void ADC1_GPIO_Configuration(void) {
42: 	GPIO_InitTypeDef GPIO_InitStructure;
43: 	
44: 	RCC_AHBPeriphClockCmd(RCC_AHBPeriph_DMA1, ENABLE);
45: 	RCC_APB2PeriphClockCmd(RCC_APB2Periph_ADC1 | RCC_APB2Periph_GPIOA, ENABLE); 
46: 
47: 	GPIO_InitStructure.GPIO_Pin  = GPIO_Pin_0 | GPIO_Pin_1; 
48: 	
49: 	GPIO_InitStructure.GPIO_Mode =GPIO_Mode_AIN; 
50: 	GPIO_Init(GPIOA,&GPIO_InitStructure); 	
51: }
52: 
53: 
```

## z_adc.c | ADC1_Configuration | 原文件第54-61行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/src/z_adc.c
以下为原始源码，不是截图OCR。
```
54: void ADC1_Configuration(void) {
55: 	ADC_InitTypeDef ADC_InitStructure;
56: 
57: 	ADC_DeInit(ADC1); //将外设 ADC1 的全部寄存器重设为缺省值
58: 	ADC_InitStructure.ADC_Mode = ADC_Mode_Independent; //ADC工作模式:ADC1和ADC2工作在独立模式
59: 	ADC_InitStructure.ADC_ScanConvMode =ENABLE; //模数转换工作在扫描模式
60: 	ADC_InitStructure.ADC_ContinuousConvMode = ENABLE; //模数转换工作在连续转换模式 不停的转换
61: 	ADC_InitStructure.ADC_ExternalTrigConv = ADC_ExternalTrigConv_None; //外部触发转换关闭
```

## z_adc.c | ADC1_Configuration | 原文件第62-69行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/src/z_adc.c
以下为原始源码，不是截图OCR。
```
62: 	ADC_InitStructure.ADC_DataAlign = ADC_DataAlign_Right; //ADC数据右对齐
63: 	ADC_InitStructure.ADC_NbrOfChannel = ADC_NUM; //顺序进行规则转换的ADC通道的数目
64: 	ADC_Init(ADC1, &ADC_InitStructure); //根据ADC_InitStruct中指定的参数初始化外设ADCx的寄存器
65: 
66: 	RCC_ADCCLKConfig(RCC_PCLK2_Div6);
67: 	//设置指定ADC的规则组通道，设置它们的转化顺序和采样时间
68: 	//ADC1,ADC通道x,规则采样顺序值为y,采样时间为239.5周期
69: 	ADC_RegularChannelConfig(ADC1, ADC_Channel_0, 1, ADC_SampleTime_239Cycles5 );
```

## z_adc.c | ADC1_Configuration | 原文件第70-74行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/src/z_adc.c
以下为原始源码，不是截图OCR。
```
70: 	ADC_RegularChannelConfig(ADC1, ADC_Channel_1, 2, ADC_SampleTime_239Cycles5 );
71: 	//ADC_RegularChannelConfig(ADC1, ADC_Channel_2, 3, ADC_SampleTime_239Cycles5 );
72: 	//ADC_RegularChannelConfig(ADC1, ADC_Channel_3, 1, ADC_SampleTime_239Cycles5 );
73: 	//ADC_RegularChannelConfig(ADC1, ADC_Channel_4, 1, ADC_SampleTime_239Cycles5 );
74: 	//ADC_RegularChannelConfig(ADC1, ADC_Channel_1, 2, ADC_SampleTime_239Cycles5 );
```

## z_adc.c | ADC1_Configuration | 原文件第75-81行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/src/z_adc.c
以下为原始源码，不是截图OCR。
```
75: 	//ADC_RegularChannelConfig(ADC1, ADC_Channel_0, 3, ADC_SampleTime_239Cycles5 );
76: 	
77: 	//ADC_RegularChannelConfig(ADC1, ADC_Channel_5, 1, ADC_SampleTime_239Cycles5 );
78: 	//ADC_RegularChannelConfig(ADC1, ADC_Channel_6, 7, ADC_SampleTime_239Cycles5 );
79: 	//ADC_RegularChannelConfig(ADC1, ADC_Channel_7, 8, ADC_SampleTime_239Cycles5 );
80: 	//ADC_RegularChannelConfig(ADC1, ADC_Channel_8, 1, ADC_SampleTime_239Cycles5 );
81: 	
```

## z_adc.c | ADC1_Configuration | 原文件第82-87行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/src/z_adc.c
以下为原始源码，不是截图OCR。
```
82: 	//ADC_RegularChannelConfig(ADC1, ADC_Channel_10, 1, ADC_SampleTime_239Cycles5 );
83: 	//ADC_RegularChannelConfig(ADC1, ADC_Channel_11, 2, ADC_SampleTime_239Cycles5 );
84: 	
85: 	//ADC_RegularChannelConfig(ADC1, ADC_Channel_12, 9, ADC_SampleTime_239Cycles5 );
86: 	//ADC_RegularChannelConfig(ADC1, ADC_Channel_13, 10, ADC_SampleTime_239Cycles5 );
87: 	//ADC_RegularChannelConfig(ADC1, ADC_Channel_14, 11, ADC_SampleTime_239Cycles5 );
```

## z_adc.c | ADC1_Configuration | 原文件第88-100行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/src/z_adc.c
以下为原始源码，不是截图OCR。
```
88: 	//ADC_RegularChannelConfig(ADC1, ADC_Channel_15, 12, ADC_SampleTime_239Cycles5 );
89: 
90: 	// 开启ADC的DMA支持（要实现DMA功能，还需独立配置DMA通道等参数）
91: 	ADC_DMACmd(ADC1, ENABLE);
92: 
93: 	ADC_Cmd(ADC1, ENABLE); //使能指定的ADC1
94: 
95: 	ADC_ResetCalibration(ADC1); //复位指定的ADC1的校准寄存器
96: 
97: 	while(ADC_GetResetCalibrationStatus(ADC1)); //获取ADC1复位校准寄存器的状态,设置状态则等待
98: 
99: 	ADC_StartCalibration(ADC1); //开始指定ADC1的校准状态
100: 
```

## z_adc.c | ADC1_Configuration | 原文件第101-108行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/src/z_adc.c
以下为原始源码，不是截图OCR。
```
101: 	while(ADC_GetCalibrationStatus(ADC1)); //获取指定ADC1的校准程序,设置状态则等待          
102: 	
103: 	ADC_SoftwareStartConvCmd(ADC1, ENABLE);
104: 
105: }
106: 
107: 
108: 
```

## z_adc.c | DMA_Configuration | 原文件第109-115行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/src/z_adc.c
以下为原始源码，不是截图OCR。
```
109: void DMA_Configuration(void)
110: {
111: 	DMA_InitTypeDef DMA_InitStructure;
112: 	DMA_DeInit(DMA1_Channel1); //将DMA的通道1寄存器重设为缺省值
113: 	DMA_InitStructure.DMA_PeripheralBaseAddr = ADC1_DR_Address; //DMA外设ADC基地址*****
114: 	DMA_InitStructure.DMA_MemoryBaseAddr = (u32)ADC_ConvertedValue; //DMA内存基地址*****
115: 	DMA_InitStructure.DMA_DIR = DMA_DIR_PeripheralSRC; //内存作为数据传输的目的地
```

## z_adc.c | DMA_Configuration | 原文件第116-120行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/src/z_adc.c
以下为原始源码，不是截图OCR。
```
116: 	DMA_InitStructure.DMA_BufferSize = ADC_NUM; //DMA通道的DMA缓存的大小*****
117: 	DMA_InitStructure.DMA_PeripheralInc = DMA_PeripheralInc_Disable; //外设地址寄存器不变
118: 	DMA_InitStructure.DMA_MemoryInc = DMA_MemoryInc_Enable; //内存地址寄存器递增
119: 	DMA_InitStructure.DMA_PeripheralDataSize = DMA_PeripheralDataSize_HalfWord; //数据宽度为16位
120: 	DMA_InitStructure.DMA_MemoryDataSize = DMA_MemoryDataSize_HalfWord; //数据宽度为16位
```

## z_adc.c | DMA_Configuration | 原文件第121-128行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/src/z_adc.c
以下为原始源码，不是截图OCR。
```
121: 	DMA_InitStructure.DMA_Mode = DMA_Mode_Circular; //工作在循环缓存模式
122: 	DMA_InitStructure.DMA_Priority = DMA_Priority_High; //DMA通道 x拥有高优先级
123: 	DMA_InitStructure.DMA_M2M = DMA_M2M_Disable; //DMA通道x没有设置为内存到内存传输
124: 	DMA_Init(DMA1_Channel1, &DMA_InitStructure); //根据DMA_InitStruct中指定的参数初始化DMA的通道
125: 	DMA_Cmd(DMA1_Channel1, ENABLE);
126: 	
127: }
128: 
```

## z_adc.h | 文件开头/全局定义 | 原文件第1-19行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/src/z_adc.h
以下为原始源码，不是截图OCR。
```
1: 
2: #ifndef __ADC_H__
3: #define __ADC_H__
4: 
5: #include "z_main.h"
6: #include "z_type.h"
7: #include "stm32f10x_conf.h"
8: 
9: #define ADC_NUM 2
10: 
11: 
12: void ADC_init(void);
13: void ADC1_GPIO_Configuration(void);
14: void ADC1_Configuration(void);
15: void DMA_Configuration(void);
16: 
17: extern u16 ADC_ConvertedValue[ADC_NUM];
18: 
19: #endif
```

## z_main.c | 文件开头/全局定义 | 原文件第1-22行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
1: /***************************************************************
2: 	*	@笔者	：	tacbo
3: 	*	@日期	：	2020年05月23日
4: 	*	@所属	：	杭州众灵科技
5: 	*	@论坛	：	www.ZL-robot.com
6: 	*	@功能	：	ZL-KPZ51控制板
7: 	
8: 	实现的功能：
9: 	1、手柄按钮控制0-5号舵机，摇杆控制6-7号电机；
10: 	2、zide图形化控制舵机
11: 	3、可脱机存储控制
12: 	
13: 	传感器引脚:
14: 		循迹（S1-PA0 PA1） 
15: 		超声波(S3-PB0 PA2) 
16: 		声音(S4-PB1) 
17: 		颜色识别(S6-PA7 PA5)
18: 	舵机引脚：
19: 		DJ0-PB3
20: 		DJ1-PB8
21: 		DJ2-PB9
22: 		DJ3-PB6
```

## z_main.c | 文件开头/全局定义 | 原文件第23-45行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
23: 		DJ4-PB7
24: 		DJ5-PB4
25: 	蜂鸣器引脚：
26: 		BEEP-PB5
27: 	LED引脚：
28: 		NLED-PB13
29:   PS2手柄引脚：	
30: 	  PS1-DAT-PA15
31: 	  PS2-CMD-PA14
32: 	  PS6-ATT-PA13
33: 	  PS7-CLK-PA12
34: 	按键引脚：
35: 	  KEY1-PA8 KEY2-PA11
36: 	
37: 	统一总线口： TX3 RX3
38: 	
39: 	主频：72M
40: 	单片机型号：STM32F103C8T6
41: 	
42: ***************************************************************/
43: 
44: #include "z_rcc.h"		//配置时钟文件
45: #include "z_gpio.h"		//配置IO口文件
```

## z_main.c | 文件开头/全局定义 | 原文件第46-57行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
46: #include "z_global.h"	//存放全局变量
47: #include "z_delay.h"	//存放延时函数
48: #include "z_type.h"		//存放类型定义
49: #include "z_usart.h"	//存放串口功能文件
50: #include "z_timer.h"	//存放定时器功能文件
51: #include "z_ps2.h"		//存放索尼手柄
52: #include "z_w25q64.h"	//存储芯片的操作
53: #include "z_adc.h"		//ADC初始化
54: #include <stdio.h>		//标准库文件
55: #include <string.h>		//标准库文件
56: #include <math.h>		//标准库文件
57: #include "z_kinematics.h"	//逆运动学算法
```

## z_main.c | 文件开头/全局定义 | 原文件第58-73行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
58: #include "z_actiongroupcontrol.h" //动作组执行文件
59: #include "stm32f10x_iwdg.h"
60: #include "z_sensor.h"
61: 
62: #define MODULE "Jibot1-32"
63: 
64: /*
65: 	全局变量定义
66: */
67: //int i;								    //常用的一个临时变量
68: 
69: u8 psx_buf[9]={0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00}; //存储手柄的数据 	
70: 
71: kinematics_t kinematics;
72: 
73: const char *pre_cmd_set_red[PSX_BUTTON_NUM] = {//红灯模式下按键的配置			
```

## z_main.c | 文件开头/全局定义 | 原文件第74-80行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
74: 	"<PS2_RED01:#005P0600T2000!^#005PDST!>",	//L2						  
75: 	"<PS2_RED02:#005P2400T2000!^#005PDST!>",	//R2						  
76: 	"<PS2_RED03:#004P0600T2000!^#004PDST!>",	//L1						  
77: 	"<PS2_RED04:#004P2400T2000!^#004PDST!>",	//R1			
78: 	"<PS2_RED05:#002P2400T2000!^#002PDST!>",	//RU						  
79: 	"<PS2_RED06:#003P2400T2000!^#003PDST!>",	//RR						  
80: 	"<PS2_RED07:#002P0600T2000!^#002PDST!>",	//RD						  
```

## z_main.c | 文件开头/全局定义 | 原文件第81-87行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
81: 	"<PS2_RED08:#003P0600T2000!^#003PDST!>",	//RL				
82: 	"<PS2_RED09:$DJR!>",					            //SE    				  
83: 	"<PS2_RED10:>",					                  //AL						   
84: 	"<PS2_RED11:>",					                  //AR						  
85: 	"<PS2_RED12:$DJR!>",					            //ST		
86: 	"<PS2_RED13:#001P0600T2000!^#001PDST!>",	//LU						  
87: 	"<PS2_RED14:#000P0600T2000!^#000PDST!>",	//LR								  
```

## z_main.c | 文件开头/全局定义 | 原文件第88-97行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
88: 	"<PS2_RED15:#001P2400T2000!^#001PDST!>",	//LD						  
89: 	"<PS2_RED16:#000P2400T2000!^#000PDST!>",	//LL								
90: };
91: 
92: //绿灯模式下，摇杆会映射到按键，防止影响，去掉绿灯模式功能
93: /*
94: const char *pre_cmd_set_grn[PSX_BUTTON_NUM] = {//绿灯模式下按键的配置			
95: 	"<PS2_GRN01:#005P0600T2000!^#005PDST!>",	 //L2						  
96: 	"<PS2_GRN02:#005P2400T2000!^#005PDST!>",	 //R2						  
97: 	"<PS2_GRN03:#004P0600T2000!^#004PDST!>",	 //L1						  
```

## z_main.c | 文件开头/全局定义 | 原文件第98-104行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
98: 	"<PS2_GRN04:#004P2400T2000!^#004PDST!>",	 //R1			
99: 	"<PS2_GRN05:#002P2400T2000!^#002PDST!>",	 //RU						  
100: 	"<PS2_GRN06:#003P2400T2000!^#003PDST!>",	 //RR						  
101: 	"<PS2_GRN07:#002P0600T2000!^#002PDST!>",	 //RD						  
102: 	"<PS2_GRN08:#003P0600T2000!^#003PDST!>",	 //RL				
103: 	"<PS2_GRN09:$DJR!>",					             //SE    				  
104: 	"<PS2_GRN10:>",					                   //AL						   
```

## z_main.c | 文件开头/全局定义 | 原文件第105-113行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
105: 	"<PS2_GRN11:>",					                   //AR						  
106: 	"<PS2_GRN12:$DJR!>",					             //ST		
107: 	"<PS2_GRN13:#001P0600T2000!^#001PDST!>",	 //LU						  
108: 	"<PS2_GRN14:#000P0600T2000!^#000PDST!>",	 //LR								  
109: 	"<PS2_GRN15:#001P2400T2000!^#001PDST!>",	 //LD						  
110: 	"<PS2_GRN16:#000P2400T2000!^#000PDST!>",	 //LL								
111: };
112: */
113: 
```

## z_main.c | 文件开头/全局定义 | 原文件第114-118行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
114: /*-------------------------------------------------------------------------------------------------------
115: *  程序从这里执行				
116: *  这个启动代码 完成时钟配置 使用外部晶振作为STM32的运行时钟 并倍频到72M
117: -------------------------------------------------------------------------------------------------------*/
118: 
```

## z_main.c | main | 原文件第119-130行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
119: int main(void) {	
120: 	setup_rcc();		  //初始化时钟
121: 	setup_global();		//初始化全局变量
122: 	setup_gpio();		  //初始化IO口
123: 	setup_nled();		  //初始化工作指示灯
124: 	setup_beep();		  //初始化定时器
125: 	setup_djio();		  //初始化舵机IO口
126: 	setup_w25q64();		//初始化存储器W25Q64
127: 	setup_ps2();		  //初始化PS2手柄
128: 	setup_uart1();		//初始化串口1 用于下载动作组
129: 	setup_uart3();		//初始化串口3 用于底板总线、蓝牙、lora
130: 	setup_systick();	//初始化滴答时钟，1S增加一次millis()的值
```

## z_main.c | main | 原文件第131-141行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
131: 	setup_dj_timer();	//初始化定时器2 处理舵机PWM输出	
132: 	setup_interrupt();//初始化总中断		
133: 	setup_kinematics(110, 105, 75, 190, &kinematics); //kinematics 90mm 105mm 98mm 150mm
134: 	setup_servo_bias();  //初始化舵机，将偏差代入初始值
135: 	IWDG_Init();       //初始化独立看门狗
136: 	setup_start();		//初始化启动信号
137: 	setup_do_group(); //开机动作
138: 	setup_sensor();
139: 	
140: 	while(1) {
141: 		loop_nled();		//循环执行工作指示灯，500ms跳动一次 和声音公用一个IO口 这里在声音功能启用的时候就关闭nled
```

## z_main.c | main | 原文件第142-155行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
142: 		loop_uart();		//串口数据接收处理
143: 		loop_action();	//动作组批量执行
144: 		loop_ps2_data();//循环读取PS2手柄数据
145: 		loop_ps2_button();//处理手柄上的按钮
146: 		//loop_monitor();   //定时保存一些变量
147: 		loop_sensor();
148: 	}
149: }
150: 
151: //--------------------------------------------------------------------------------
152: /*
153: 	初始化函数实现
154: */
155: 
```

## z_main.c | setup_rcc | 原文件第156-159行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
156: void setup_rcc(void) {   //初始化时钟
157: 	tb_rcc_init();	  	   //时钟初始化
158: }
159: 
```

## z_main.c | setup_global | 原文件第160-163行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
160: void setup_global(void) {//初始化全局变量
161: 	tb_global_init();	
162: }
163: 
```

## z_main.c | setup_gpio | 原文件第164-167行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
164: void setup_gpio(void) {  //初始化IO口
165: 	tb_gpio_init();		    
166: }
167: 
```

## z_main.c | setup_nled | 原文件第168-172行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
168: void setup_nled(void) {  //初始化工作指示灯
169: 	nled_init();		
170: 	nled_off();		         //工作指示灯关闭
171: }
172: 
```

## z_main.c | setup_beep | 原文件第173-176行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
173: void setup_beep(void) {  //初始化定时器蜂鸣器
174: 	beep_init();		
175: 	beep_off();			       //关闭蜂鸣器
176: }			
```

## z_main.c | setup_w25q64 | 原文件第177-187行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
177: void setup_w25q64(void) {//初始化存储器W25Q64
178: 	u8 i;
179: 	spiFlahsOn(1);
180: 	w25x_init();				   //动作组存储芯片初始化
181: 	w25x_read((u8 *)(&eeprom_info), W25Q64_INFO_ADDR_SAVE_STR, sizeof(eeprom_info));//读取全局变量
182: 	
183: 	if(eeprom_info.version != VERSION) {//判断版本是否是当前版本
184: 		eeprom_info.version = VERSION;		//复制当前版本
185: 		eeprom_info.dj_record_num = 0;		//学习动作组变量赋值0
186: 	}
187: 	
```

## z_main.c | setup_w25q64 | 原文件第188-202行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
188: 	if(eeprom_info.dj_bias_pwm[DJ_NUM] != FLAG_VERIFY) {
189: 		for(i=0;i<DJ_NUM;i++) {
190: 			eeprom_info.dj_bias_pwm[i] = 0;
191: 		}
192: 		eeprom_info.dj_bias_pwm[DJ_NUM] = FLAG_VERIFY;
193: 	}
194: 	
195: 	for(i=0;i<DJ_NUM;i++) {
196: 		duoji_doing[i].aim = 1500 + eeprom_info.dj_bias_pwm[i];
197: 		duoji_doing[i].cur = 1500 + eeprom_info.dj_bias_pwm[i];
198: 		duoji_doing[i].inc = 0;
199: 	}
200: 	spiFlahsOn(0);
201: }	
202: 
```

## z_main.c | setup_adc | 原文件第203-206行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
203: void setup_adc(void) {//初始化ADC采集 使用DMA初始化
204: 	ADC_init();
205: }
206: 
```

## z_main.c | setup_ps2 | 原文件第207-210行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
207: void setup_ps2(void) {//初始化PS2手柄
208: 	PSX_init();	
209: }
210: 
```

## z_main.c | setup_uart1 | 原文件第211-219行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
211: void setup_uart1(void) {
212:   //串口1初始化
213: 	tb_usart1_init(115200);
214: 	//串口1打开
215: 	uart1_open();
216: 	//串口发送测试字符
217: 	uart1_send_str((u8 *)"uart1 check ok!");
218: }
219: //初始化串口2
```

## z_main.c | setup_uart2 | 原文件第220-228行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
220: void setup_uart2(void) {
221: 	//串口2初始化
222: 	tb_usart2_init(115200);
223: 	//串口2打开
224: 	uart2_open();
225: 	//串口发送测试字符
226: 	uart2_send_str((u8 *)"uart2 check ok!");
227: }	
228: //初始化串口3
```

## z_main.c | setup_uart3 | 原文件第229-239行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
229: void setup_uart3(void) {
230: 	//串口3初始化
231: 	tb_usart3_init(115200);
232: 	//串口3打开
233: 	uart3_open();
234: 	//串口发送测试字符
235: 	uart3_send_str((u8 *)"uart3 check ok!");
236: 	//总线输出 复位总线舵机 串口3即为总线串口
237: 	zx_uart_send_str((u8 *)"#255P1500T2000!");
238: }	
239: //初始化滴答时钟，1S增加一次millis()的值
```

## z_main.c | setup_systick | 原文件第240-244行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
240: void setup_systick(void) {
241: 	//系统滴答时钟初始化	
242: 	SysTick_Int_Init();
243: }	
244: //初始化启动信号
```

## z_main.c | setup_start | 原文件第245-253行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
245: void setup_start(void) {
246: 	//蜂鸣器LED 名叫闪烁 示意系统启动
247: 	beep_on();nled_on();tb_delay_ms(100);beep_off();nled_off();tb_delay_ms(100);
248: 	beep_on();nled_on();tb_delay_ms(100);beep_off();nled_off();tb_delay_ms(100);
249: 	beep_on();nled_on();tb_delay_ms(100);beep_off();nled_off();tb_delay_ms(100);
250: }	
251: 
252: 
253: //初始化总中断
```

## z_main.c | setup_interrupt | 原文件第254-265行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
254: void setup_interrupt(void) {
255: 	//总中断打开
256: 	tb_interrupt_open();
257: }	
258: //--------------------------------------------------------------------------------
259: 
260: 
261: //--------------------------------------------------------------------------------
262: /*
263: 	主循环函数实现
264: */
265: //循环执行工作指示灯，500ms跳动一次
```

## z_main.c | loop_nled | 原文件第266-279行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
266: void loop_nled(void) {
267: 	static u32 time_count=0;
268: 	static u8 flag = 0;
269: 	if(millis()-time_count > 1000)  {
270: 		time_count = millis();
271: 		if(flag) {
272: 			nled_on();
273: 		} else {
274: 			nled_off();
275: 		}
276: 		flag= ~flag;
277: 	}
278: }		
279: //串口数据接收处理
```

## z_main.c | loop_uart | 原文件第280-290行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
280: void loop_uart(void) {
281: 	if(uart1_get_ok) {
282: 		if(uart1_mode == 1) {					    //命令模式
283: 			parse_group_cmd(uart_receive_buf);
284: 			parse_cmd(uart_receive_buf);			
285: 		} else if(uart1_mode == 2) {			//单个舵机调试
286: 			parse_action(uart_receive_buf);
287: 		} else if(uart1_mode == 3) {		  //多路舵机调试
288: 			parse_action(uart_receive_buf);
289: 		} else if(uart1_mode == 4) {		  //存储模式
290: 			save_action(uart_receive_buf);
```

## z_main.c | loop_uart | 原文件第291-299行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
291: 		} 
292: 		uart1_mode = 0;
293: 		uart1_get_ok = 0;
294: 		uart1_open();
295: 	}
296: 	return;
297: }	
298: 
299: //循环读取PS2手柄数据
```

## z_main.c | loop_ps2_data | 原文件第300-312行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
300: void loop_ps2_data(void) {
301: 	static u32 systick_ms_bak = 0;
302: 	//每50ms处理1次
303: 	if(millis() - systick_ms_bak < 50) {
304: 		return;
305: 	}
306: 	systick_ms_bak = millis();
307: 	//读写手柄数据
308: 	psx_write_read(psx_buf);
309: 	
310: #if 0
311: 	//测试手柄数据，1为打开 0为关闭
312: 	sprintf((char *)cmd_return, "0x%02x,0x%02x,0x%02x,0x%02x,0x%02x,0x%02x,0x%02x,0x%02x,0x%02x\r\n", 
```

## z_main.c | loop_ps2_data | 原文件第313-320行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
313: 	(int)psx_buf[0], (int)psx_buf[1], (int)psx_buf[2], (int)psx_buf[3],
314: 	(int)psx_buf[4], (int)psx_buf[5], (int)psx_buf[6], (int)psx_buf[7], (int)psx_buf[8]);
315: 	uart1_send_str(cmd_return);
316: #endif 	
317: 	
318: 	return;
319: }	
320: //处理手柄上的按钮
```

## z_main.c | loop_ps2_button | 原文件第321-334行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
321: void loop_ps2_button(void) {
322: 	static unsigned char psx_button_bak[2] = {0};
323: 
324: 	//对比两次获取的按键值是否相同 ，相同就不处理，不相同则处理
325: 	if((psx_button_bak[0] == psx_buf[3])
326: 	&& (psx_button_bak[1] == psx_buf[4])) {				
327: 	} else {		
328: 		//处理buf3和buf4两个字节，这两个字节存储这手柄16个按键的状态
329: 		parse_psx_buf(psx_buf+3, psx_buf[1]);
330: 		psx_button_bak[0] = psx_buf[3];
331: 		psx_button_bak[1] = psx_buf[4];
332: 	}
333: 	return;
334: }	
```

## z_main.c | loop_ps2_button | 原文件第335-338行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
335: 
336: //--------------------------------------------------------------------------------
337: 
338: //软件复位函数，调用后单片机自动复位
```

## z_main.c | soft_reset | 原文件第339-344行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
339: void soft_reset(void) {
340: 	__set_FAULTMASK(1);     
341: 	NVIC_SystemReset();
342: }
343: 
344: //处理手柄按键字符，buf为字符数组，mode是指模式 主要是红灯和绿灯模式
```

## z_main.c | parse_psx_buf | 原文件第345-357行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
345: void parse_psx_buf(unsigned char *buf, unsigned char mode) {
346: 	u8 i, pos = 0;
347: 	static u16 bak=0xffff, temp, temp2;
348: 	temp = (buf[0]<<8) + buf[1];
349: 	
350: 	if(bak != temp) {
351: 		temp2 = temp;
352: 		temp &= bak;
353: 		for(i=0;i<16;i++) {     //16个按键一次轮询
354: 			if((1<<i) & temp) {
355: 			} else {
356: 				if((1<<i) & bak) {	//press 表示按键按下了
357: 															
```

## z_main.c | parse_psx_buf | 原文件第358-364行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
358: 					memset(uart_receive_buf, 0, sizeof(uart_receive_buf));					
359: 					if(mode == PS2_LED_RED) {
360: 						memcpy((char *)uart_receive_buf, (char *)pre_cmd_set_red[i], strlen(pre_cmd_set_red[i]));
361: 					} else continue;
362: 					//zx_uart_send_str(uart_receive_buf);
363: 					pos = str_contain_str(uart_receive_buf, (u8 *)"^");
364: 					if(pos) uart_receive_buf[pos-1] = '\0';
```

## z_main.c | parse_psx_buf | 原文件第365-374行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
365: 					if(str_contain_str(uart_receive_buf, (u8 *)"$")) {
366: 						uart1_close();
367: 						uart1_get_ok = 0;
368: 						strcpy((char *)cmd_return, (char *)uart_receive_buf+11);
369: 						strcpy((char *)uart_receive_buf, (char *)cmd_return);
370: 						uart1_get_ok = 1;
371: 						uart1_open();
372: 						uart1_mode = 1;
373: 					} else if(str_contain_str(uart_receive_buf, (u8 *)"#")) {
374: 						uart1_close();
```

## z_main.c | parse_psx_buf | 原文件第375-386行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
375: 						uart1_get_ok = 0;
376: 						strcpy((char *)cmd_return, (char *)uart_receive_buf+11);
377: 						strcpy((char *)uart_receive_buf,(char *) cmd_return);
378: 						uart1_get_ok = 1;
379: 						uart1_open();
380: 						uart1_mode = 2;
381: 					}
382: 					bak = 0xffff;
383: 				} else {//release 表示按键松开了
384: 										
385: 					memset(uart_receive_buf, 0, sizeof(uart_receive_buf));					
386: 					if(mode == PS2_LED_RED) {
```

## z_main.c | parse_psx_buf | 原文件第387-395行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
387: 						memcpy((char *)uart_receive_buf, (char *)pre_cmd_set_red[i], strlen(pre_cmd_set_red[i]));
388: 					} else continue;	
389: 					
390: 					pos = str_contain_str(uart_receive_buf, (u8 *)"^");
391: 					if(pos) {
392: 						if(str_contain_str(uart_receive_buf+pos, (u8 *)"$")) {
393: 							//uart1_close();
394: 							//uart1_get_ok = 0;
395: 							strcpy((char *)cmd_return, (char *)uart_receive_buf+pos);
```

## z_main.c | parse_psx_buf | 原文件第396-404行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
396: 							cmd_return[strlen((char *)cmd_return) - 1] = '\0';
397: 							strcpy((char *)uart_receive_buf, (char *)cmd_return);
398: 							parse_cmd(uart_receive_buf);
399: 							//uart1_get_ok = 1;
400: 							//uart1_mode = 1;
401: 						} else if(str_contain_str(uart_receive_buf+pos, (u8 *)"#")) {
402: 							//uart1_close();
403: 							//uart1_get_ok = 0;
404: 							strcpy((char *)cmd_return, (char *)uart_receive_buf+pos);
```

## z_main.c | parse_psx_buf | 原文件第405-421行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
405: 							cmd_return[strlen((char *)cmd_return) - 1] = '\0';
406: 							strcpy((char *)uart_receive_buf, (char *)cmd_return);
407: 							parse_action(uart_receive_buf);
408: 							//uart1_get_ok = 1;
409: 							//uart1_mode = 2;
410: 						}
411: 						//uart1_send_str(uart_receive_buf);
412: 					}	
413: 				}
414: 			}
415: 		}
416: 		bak = temp2;
417: 		beep_on();mdelay(10);beep_off();
418: 	}	
419: 	return;
420: }
421: 
```

## z_main.c | parse_psx_buf | 原文件第422-422行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
422: //命令解析函数
```

## z_main.c | parse_cmd | 原文件第423-431行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
423: void parse_cmd(u8 *cmd) {
424: 	int pos, i, index, int1, int2, int3, int4;
425: 	//uart1_send_str(cmd);
426: 
427: 	if(pos = str_contain_str(cmd, (u8 *)"$KMS:"), pos) {		
428: 		if(sscanf((char *)cmd, "$KMS:%d,%d,%d,%d!", &int1, &int2, &int3, &int4)) {
429: 			uart1_send_str((u8 *)"Try to find best pos:\r\n");
430: 			if(kinematics_move(int1, int2, int3, int4)) {
431: 				beep_on();mdelay(50);beep_off();mdelay(50);
```

## z_main.c | parse_cmd | 原文件第432-441行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
432: 			} else {
433: 				beep_on();mdelay(50);beep_off();mdelay(50);
434: 				beep_on();mdelay(50);beep_off();mdelay(50);
435: 				uart1_send_str((u8 *)"Can't find best pos!!!");
436: 			}					
437: 		}
438: 	}
439: }
440: 
441: 
```

## z_main.c | kinematics_move | 原文件第442-458行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
442: int kinematics_move(float x, float y, float z, int time) {
443: 	int i,j, min = 0, flag = 0;
444: 	
445: 	if(y < 0)return 0;
446: 	
447: 	//寻找最佳角度
448: 	flag = 0;
449: 	for(i=0;i>=-135;i--) {
450: 		if(0 == kinematics_analysis(x,y,z,i,&kinematics)){
451: 			if(i<min)min = i;
452: 			flag = 1;
453: 		}
454: 	}
455: 	
456: 	//用3号舵机与水平最大的夹角作为最佳值
457: 	if(flag) {
458: 		kinematics_analysis(x,y,z,min,&kinematics);
```

## z_main.c | kinematics_move | 原文件第459-469行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_main.c
以下为原始源码，不是截图OCR。
```
459: 		for(j=0;j<4;j++) {
460: 			set_servo(j, kinematics.servo_pwm[j], time);
461: 		}
462: 		return 1;
463: 	}
464: 	
465: 	return 0;
466: }
467: 
468: 
469: 
```

## z_sensor.c | 文件开头/全局定义 | 原文件第1-13行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
1: #include "z_rcc.h"		//配置时钟文件
2: #include "z_gpio.h"		//配置IO口文件
3: #include "z_global.h"	//存放全局变量
4: #include "z_delay.h"	//存放延时函数
5: #include "z_type.h"		//存放类型定义
6: #include "z_usart.h"	//存放串口功能文件
7: #include "z_timer.h"	//存放定时器功能文件
8: #include "z_ps2.h"		//存放索尼手柄
9: #include "z_w25q64.h"	//存储芯片的操作
10: #include "z_adc.h"		//ADC初始化
11: #include <stdio.h>		//标准库文件
12: #include <string.h>		//标准库文件
13: #include <math.h>		//标准库文件
```

## z_sensor.c | 文件开头/全局定义 | 原文件第14-32行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
14: #include "z_kinematics.h"	//逆运动学算法
15: #include "stm32f10x_iwdg.h"
16: 
17: #include "z_sensor.h"
18: #include "z_actiongroupcontrol.h"
19: 
20: float servo_pwm[4];
21: /*
22: 	智能功能代码
23: 	
24: 	IO口分布
25: 	
26: 	光敏传感器 S1  PA0 -绿线
27: 		
28: */
29: 
30: 
31: 
32: //初始化传感器IO口
```

## z_sensor.c | setup_sensor | 原文件第33-36行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
33: void setup_sensor(void) {
34: 	ADC_init();
35: }
36: 
```

## z_sensor.c | loop_sensor | 原文件第37-46行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
37: void loop_sensor(void) {
38: 	rocker_control();
39: }
40: 
41: 
42: /*************************************************************
43: 功能介绍：
44: 函数参数：无
45: 返回值：  无  
46: *************************************************************/
```

## z_sensor.c | rocker_control | 原文件第47-60行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
47: void rocker_control(void) {	
48: 	u8 j;
49: 	u16 x_value,y_value;
50: 	static int kms_x,kms_y;
51: 	static u32 systick_ms_light = 0;
52: 	//每隔100毫秒执行一次
53: 	if(millis() - systick_ms_light >= 100){
54: 		systick_ms_light = millis();
55: 		
56: 		y_value = ADC_ConvertedValue[0]/16; 
57: 		x_value = ADC_ConvertedValue[1]/16; 
58: 		
59: 		//sprintf((char *)cmd_return,"x_value:%d\r\n",(int)x_value);
60: 		//uart1_send_str(cmd_return);
```

## z_sensor.c | rocker_control | 原文件第61-75行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
61: 		//sprintf((char *)cmd_return,"y_value:%d\r\n",(int)y_value);
62: 		//uart1_send_str(cmd_return);
63: 		
64: 		kms_x = y_value-190;
65: 		
66: 		if(kms_x <= -50){
67: 			kms_x = -50;
68: 		}
69: 		
70: 		kms_y = x_value+100; 
71: 		if(kinematics_move(kms_x, kms_y, 100, 1000)) {
72: 			mdelay(1);
73: 		}		
74: 	}
75: }
```

## z_sensor.h | 文件开头/全局定义 | 原文件第1-18行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-摇杆控制.zip!/Jibot1-32出厂程序-摇杆控制/USER/z_sensor.h
以下为原始源码，不是截图OCR。
```
1: #ifndef __SENSOR_H__
2: #define __SENSOR_H__
3: 
4: #include "stm32f10x_conf.h"
5: 
6: #define button1() GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_0)
7: #define button2() GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_1)
8: 
9: 
10: //处理智能传感器功能
11: void setup_sensor(void);
12: 
13: void loop_sensor(void);
14: 
15: void rocker_control(void);			//按键夹取
16: 
17: 
18: #endif
```
