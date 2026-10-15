## z_sensor.c | 文件开头/全局定义 | 原文件第1-13行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-触摸夹取.zip!/Jibot1-32出厂程序-触摸夹取/USER/z_sensor.c
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

## z_sensor.c | 文件开头/全局定义 | 原文件第14-31行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-触摸夹取.zip!/Jibot1-32出厂程序-触摸夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
14: #include "z_kinematics.h"	//逆运动学算法
15: #include "stm32f10x_iwdg.h"
16: 
17: #include "z_sensor.h"
18: #include "z_actiongroupcontrol.h"
19: 
20: u8 mode;
21: /*
22: 	智能功能代码
23: 	
24: 	IO口分布
25: 	模式切换按键 S3  PA2 -绿线
26: 
27: 		
28: */
29: 
30: 
31: //初始化传感器IO口
```

## z_sensor.c | setup_sensor | 原文件第32-40行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-触摸夹取.zip!/Jibot1-32出厂程序-触摸夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
32: void setup_sensor(void) {
33: 	GPIO_InitTypeDef GPIO_InitStructure;
34: 	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA , ENABLE);  
35: 	
36: 	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_2;   
37: 	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IPU;   
38: 	GPIO_Init(GPIOA, &GPIO_InitStructure); 
39: }
40: 
```

## z_sensor.c | loop_sensor | 原文件第41-50行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-触摸夹取.zip!/Jibot1-32出厂程序-触摸夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
41: void loop_sensor(void) {
42: 	chumo_jiaqu();
43: }
44: 
45: 
46: /*************************************************************
47: 功能介绍：长按执行前抓动作组，双击执行前放动作组
48: 函数参数：无
49: 返回值：  无  
50: *************************************************************/
```

## z_sensor.c | chumo_jiaqu | 原文件第51-64行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-触摸夹取.zip!/Jibot1-32出厂程序-触摸夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
51: void chumo_jiaqu(void) {	
52: 	static u32 systick_ms_button = 0;
53: 	u8 chu_mode = 0;
54: 	if(group_do_ok == 0)return;//有动作执行，直接返回
55: 	if(chumo1() == 1){
56: 		mdelay(20);
57: 		if(chumo1() == 1) {
58: 			beep_on_times(1, 100);
59: 			chu_mode = 1;
60: 			systick_ms_button = millis(); //记录系统时间和chu_mode变量
61: 			while(chumo1() == 1){
62: 				//长按大于1秒执行
63: 				if(millis() - systick_ms_button >= 1000){
64: 					chu_mode = 0;
```

## z_sensor.c | chumo_jiaqu | 原文件第65-80行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-触摸夹取.zip!/Jibot1-32出厂程序-触摸夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
65: 					beep_on_times(1, 500);					
66: 					parse_group_cmd((u8 *)"$DGT:3-7,1!");  //长按执行前抓动作					
67: 				}		
68: 			}	
69: 		}
70: 	}
71: 	if(chumo1() == 0 && chu_mode == 1){
72: 		beep_on_times(1, 100);
73: 		chu_mode = 2;		
74: 	}
75: 	if(chumo1() == 1 && chu_mode == 2){
76: 		beep_on_times(1, 100);
77: 		chu_mode = 3;
78: 	}
79: 	if(chumo1() == 0 && chu_mode == 3){	
80: 		beep_on_times(1, 100);
```

## z_sensor.c | chumo_jiaqu | 原文件第81-84行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-触摸夹取.zip!/Jibot1-32出厂程序-触摸夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
81: 		parse_group_cmd((u8 *)"$DGT:18-21,1!");  //前放
82: 		chu_mode = 0;
83: 	}				
84: }
```

## z_sensor.h | 文件开头/全局定义 | 原文件第1-18行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-触摸夹取.zip!/Jibot1-32出厂程序-触摸夹取/USER/z_sensor.h
以下为原始源码，不是截图OCR。
```
1: #ifndef __SENSOR_H__
2: #define __SENSOR_H__
3: 
4: #include "stm32f10x_conf.h"
5: 
6: #define chumo1() GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_2)
7: #define chumo2() GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_1)
8: 
9: 
10: //处理智能传感器功能
11: void setup_sensor(void);
12: 
13: void loop_sensor(void);
14: 
15: void chumo_jiaqu(void);			//触摸夹取
16: 
17: 
18: #endif
```
