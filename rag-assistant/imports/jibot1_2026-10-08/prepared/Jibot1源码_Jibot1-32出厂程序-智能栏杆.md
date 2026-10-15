## z_main.c | 文件开头/全局定义 | 原文件第1-25行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
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
13: 
14: 	舵机引脚：
15: 		DJ0-PB3
16: 		DJ1-PB8
17: 		DJ2-PB9
18: 		DJ3-PB6
19: 		DJ4-PB7
20: 		DJ5-PB4
21: 	蜂鸣器引脚：
22: 		BEEP-PB5
23: 	LED引脚：
24: 		NLED-PB13
25:   PS2手柄引脚：	
```

## z_main.c | 文件开头/全局定义 | 原文件第26-44行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
26: 	  PS1-DAT-PA15
27: 	  PS2-CMD-PA14
28: 	  PS6-ATT-PA13
29: 	  PS7-CLK-PA12
30: 	按键引脚：
31: 	  KEY1-PA8 KEY2-PA11
32: 	
33: 	统一总线口： TX3 RX3
34: 	
35: 	主频：72M
36: 	单片机型号：STM32F103C8T6
37: 	
38: ***************************************************************/
39: 
40: #include "z_rcc.h"		//配置时钟文件
41: #include "z_gpio.h"		//配置IO口文件
42: #include "z_global.h"	//存放全局变量
43: #include "z_delay.h"	//存放延时函数
44: #include "z_type.h"		//存放类型定义
```

## z_main.c | 文件开头/全局定义 | 原文件第45-57行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
45: #include "z_usart.h"	//存放串口功能文件
46: #include "z_timer.h"	//存放定时器功能文件
47: #include "z_ps2.h"		//存放索尼手柄
48: #include "z_w25q64.h"	//存储芯片的操作
49: #include "z_adc.h"		//ADC初始化
50: #include <stdio.h>		//标准库文件
51: #include <string.h>		//标准库文件
52: #include <math.h>		//标准库文件
53: #include "z_kinematics.h"	//逆运动学算法
54: #include "z_actiongroupcontrol.h" //动作组执行文件
55: #include "stm32f10x_iwdg.h"
56: #include "z_sensor.h"
57: 
```

## z_main.c | 文件开头/全局定义 | 原文件第58-71行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
58: #define MODULE "Jibot1-32"
59: 
60: /*
61: 	全局变量定义
62: */
63: //int i;								    //常用的一个临时变量
64: 
65: u8 psx_buf[9]={0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00}; //存储手柄的数据 	
66: 
67: kinematics_t kinematics;
68: 
69: const char *pre_cmd_set_red[PSX_BUTTON_NUM] = {//红灯模式下按键的配置			
70: 	"<PS2_RED01:#005P0600T2000!^#005PDST!>",	//L2						  
71: 	"<PS2_RED02:#005P2400T2000!^#005PDST!>",	//R2						  
```

## z_main.c | 文件开头/全局定义 | 原文件第72-78行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
72: 	"<PS2_RED03:#004P0600T2000!^#004PDST!>",	//L1						  
73: 	"<PS2_RED04:#004P2400T2000!^#004PDST!>",	//R1			
74: 	"<PS2_RED05:#002P2400T2000!^#002PDST!>",	//RU						  
75: 	"<PS2_RED06:#003P2400T2000!^#003PDST!>",	//RR						  
76: 	"<PS2_RED07:#002P0600T2000!^#002PDST!>",	//RD						  
77: 	"<PS2_RED08:#003P0600T2000!^#003PDST!>",	//RL				
78: 	"<PS2_RED09:$DJR!>",					            //SE    				  
```

## z_main.c | 文件开头/全局定义 | 原文件第79-87行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
79: 	"<PS2_RED10:>",					                  //AL						   
80: 	"<PS2_RED11:>",					                  //AR						  
81: 	"<PS2_RED12:$DJR!>",					            //ST		
82: 	"<PS2_RED13:#001P0600T2000!^#001PDST!>",	//LU						  
83: 	"<PS2_RED14:#000P0600T2000!^#000PDST!>",	//LR								  
84: 	"<PS2_RED15:#001P2400T2000!^#001PDST!>",	//LD						  
85: 	"<PS2_RED16:#000P2400T2000!^#000PDST!>",	//LL								
86: };
87: 
```

## z_main.c | 文件开头/全局定义 | 原文件第88-95行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
88: //绿灯模式下，摇杆会映射到按键，防止影响，去掉绿灯模式功能
89: /*
90: const char *pre_cmd_set_grn[PSX_BUTTON_NUM] = {//绿灯模式下按键的配置			
91: 	"<PS2_GRN01:#005P0600T2000!^#005PDST!>",	 //L2						  
92: 	"<PS2_GRN02:#005P2400T2000!^#005PDST!>",	 //R2						  
93: 	"<PS2_GRN03:#004P0600T2000!^#004PDST!>",	 //L1						  
94: 	"<PS2_GRN04:#004P2400T2000!^#004PDST!>",	 //R1			
95: 	"<PS2_GRN05:#002P2400T2000!^#002PDST!>",	 //RU						  
```

## z_main.c | 文件开头/全局定义 | 原文件第96-102行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
96: 	"<PS2_GRN06:#003P2400T2000!^#003PDST!>",	 //RR						  
97: 	"<PS2_GRN07:#002P0600T2000!^#002PDST!>",	 //RD						  
98: 	"<PS2_GRN08:#003P0600T2000!^#003PDST!>",	 //RL				
99: 	"<PS2_GRN09:$DJR!>",					             //SE    				  
100: 	"<PS2_GRN10:>",					                   //AL						   
101: 	"<PS2_GRN11:>",					                   //AR						  
102: 	"<PS2_GRN12:$DJR!>",					             //ST		
```

## z_main.c | 文件开头/全局定义 | 原文件第103-111行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
103: 	"<PS2_GRN13:#001P0600T2000!^#001PDST!>",	 //LU						  
104: 	"<PS2_GRN14:#000P0600T2000!^#000PDST!>",	 //LR								  
105: 	"<PS2_GRN15:#001P2400T2000!^#001PDST!>",	 //LD						  
106: 	"<PS2_GRN16:#000P2400T2000!^#000PDST!>",	 //LL								
107: };
108: */
109: 
110: /*-------------------------------------------------------------------------------------------------------
111: *  程序从这里执行				
```

## z_main.c | 文件开头/全局定义 | 原文件第112-114行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
112: *  这个启动代码 完成时钟配置 使用外部晶振作为STM32的运行时钟 并倍频到72M
113: -------------------------------------------------------------------------------------------------------*/
114: 
```

## z_main.c | main | 原文件第115-126行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
115: int main(void) {	
116: 	setup_rcc();		  //初始化时钟
117: 	setup_global();		//初始化全局变量
118: 	setup_gpio();		  //初始化IO口
119: 	setup_nled();		  //初始化工作指示灯
120: 	setup_beep();		  //初始化定时器
121: 	setup_djio();		  //初始化舵机IO口
122: 	setup_w25q64();		//初始化存储器W25Q64
123: 	setup_ps2();		  //初始化PS2手柄
124: 	setup_uart1();		//初始化串口1 用于下载动作组
125: 	setup_uart3();		//初始化串口3 用于底板总线、蓝牙、lora
126: 	setup_systick();	//初始化滴答时钟，1S增加一次millis()的值
```

## z_main.c | main | 原文件第127-137行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
127: 	setup_dj_timer();	//初始化定时器2 处理舵机PWM输出	
128: 	setup_interrupt();//初始化总中断		
129: 	setup_kinematics(110, 105, 75, 190, &kinematics); //kinematics 90mm 105mm 98mm 150mm
130: 	setup_servo_bias();  //初始化舵机，将偏差代入初始值
131: 	IWDG_Init();       //初始化独立看门狗
132: 	setup_start();		//初始化启动信号
133: 	setup_do_group(); //开机动作
134: 	setup_sensor();
135: 	
136: 	while(1) {
137: 		loop_nled();		//循环执行工作指示灯，500ms跳动一次 和声音公用一个IO口 这里在声音功能启用的时候就关闭nled
```

## z_main.c | main | 原文件第138-151行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
138: 		loop_uart();		//串口数据接收处理
139: 		loop_action();	//动作组批量执行
140: 		loop_ps2_data();//循环读取PS2手柄数据
141: 		loop_ps2_button();//处理手柄上的按钮
142: 		//loop_monitor();   //定时保存一些变量
143: 		loop_sensor();
144: 	}
145: }
146: 
147: //--------------------------------------------------------------------------------
148: /*
149: 	初始化函数实现
150: */
151: 
```

## z_main.c | setup_rcc | 原文件第152-155行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
152: void setup_rcc(void) {   //初始化时钟
153: 	tb_rcc_init();	  	   //时钟初始化
154: }
155: 
```

## z_main.c | setup_global | 原文件第156-159行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
156: void setup_global(void) {//初始化全局变量
157: 	tb_global_init();	
158: }
159: 
```

## z_main.c | setup_gpio | 原文件第160-163行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
160: void setup_gpio(void) {  //初始化IO口
161: 	tb_gpio_init();		    
162: }
163: 
```

## z_main.c | setup_nled | 原文件第164-168行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
164: void setup_nled(void) {  //初始化工作指示灯
165: 	nled_init();		
166: 	nled_off();		         //工作指示灯关闭
167: }
168: 
```

## z_main.c | setup_beep | 原文件第169-172行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
169: void setup_beep(void) {  //初始化定时器蜂鸣器
170: 	beep_init();		
171: 	beep_off();			       //关闭蜂鸣器
172: }			
```

## z_main.c | setup_w25q64 | 原文件第173-183行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
173: void setup_w25q64(void) {//初始化存储器W25Q64
174: 	u8 i;
175: 	spiFlahsOn(1);
176: 	w25x_init();				   //动作组存储芯片初始化
177: 	w25x_read((u8 *)(&eeprom_info), W25Q64_INFO_ADDR_SAVE_STR, sizeof(eeprom_info));//读取全局变量
178: 	
179: 	if(eeprom_info.version != VERSION) {//判断版本是否是当前版本
180: 		eeprom_info.version = VERSION;		//复制当前版本
181: 		eeprom_info.dj_record_num = 0;		//学习动作组变量赋值0
182: 	}
183: 	
```

## z_main.c | setup_w25q64 | 原文件第184-198行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
184: 	if(eeprom_info.dj_bias_pwm[DJ_NUM] != FLAG_VERIFY) {
185: 		for(i=0;i<DJ_NUM;i++) {
186: 			eeprom_info.dj_bias_pwm[i] = 0;
187: 		}
188: 		eeprom_info.dj_bias_pwm[DJ_NUM] = FLAG_VERIFY;
189: 	}
190: 	
191: 	for(i=0;i<DJ_NUM;i++) {
192: 		duoji_doing[i].aim = 1500 + eeprom_info.dj_bias_pwm[i];
193: 		duoji_doing[i].cur = 1500 + eeprom_info.dj_bias_pwm[i];
194: 		duoji_doing[i].inc = 0;
195: 	}
196: 	spiFlahsOn(0);
197: }	
198: 
```

## z_main.c | setup_adc | 原文件第199-202行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
199: void setup_adc(void) {//初始化ADC采集 使用DMA初始化
200: 	ADC_init();
201: }
202: 
```

## z_main.c | setup_ps2 | 原文件第203-206行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
203: void setup_ps2(void) {//初始化PS2手柄
204: 	PSX_init();	
205: }
206: 
```

## z_main.c | setup_uart1 | 原文件第207-215行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
207: void setup_uart1(void) {
208:   //串口1初始化
209: 	tb_usart1_init(115200);
210: 	//串口1打开
211: 	uart1_open();
212: 	//串口发送测试字符
213: 	uart1_send_str((u8 *)"uart1 check ok!");
214: }
215: //初始化串口2
```

## z_main.c | setup_uart2 | 原文件第216-224行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
216: void setup_uart2(void) {
217: 	//串口2初始化
218: 	tb_usart2_init(115200);
219: 	//串口2打开
220: 	uart2_open();
221: 	//串口发送测试字符
222: 	uart2_send_str((u8 *)"uart2 check ok!");
223: }	
224: //初始化串口3
```

## z_main.c | setup_uart3 | 原文件第225-235行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
225: void setup_uart3(void) {
226: 	//串口3初始化
227: 	tb_usart3_init(115200);
228: 	//串口3打开
229: 	uart3_open();
230: 	//串口发送测试字符
231: 	uart3_send_str((u8 *)"uart3 check ok!");
232: 	//总线输出 复位总线舵机 串口3即为总线串口
233: 	zx_uart_send_str((u8 *)"#255P1500T2000!");
234: }	
235: //初始化滴答时钟，1S增加一次millis()的值
```

## z_main.c | setup_systick | 原文件第236-240行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
236: void setup_systick(void) {
237: 	//系统滴答时钟初始化	
238: 	SysTick_Int_Init();
239: }	
240: //初始化启动信号
```

## z_main.c | setup_start | 原文件第241-249行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
241: void setup_start(void) {
242: 	//蜂鸣器LED 名叫闪烁 示意系统启动
243: 	beep_on();nled_on();tb_delay_ms(100);beep_off();nled_off();tb_delay_ms(100);
244: 	beep_on();nled_on();tb_delay_ms(100);beep_off();nled_off();tb_delay_ms(100);
245: 	beep_on();nled_on();tb_delay_ms(100);beep_off();nled_off();tb_delay_ms(100);
246: }	
247: 
248: 
249: //初始化总中断
```

## z_main.c | setup_interrupt | 原文件第250-261行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
250: void setup_interrupt(void) {
251: 	//总中断打开
252: 	tb_interrupt_open();
253: }	
254: //--------------------------------------------------------------------------------
255: 
256: 
257: //--------------------------------------------------------------------------------
258: /*
259: 	主循环函数实现
260: */
261: //循环执行工作指示灯，500ms跳动一次
```

## z_main.c | loop_nled | 原文件第262-275行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
262: void loop_nled(void) {
263: 	static u32 time_count=0;
264: 	static u8 flag = 0;
265: 	if(millis()-time_count > 1000)  {
266: 		time_count = millis();
267: 		if(flag) {
268: 			nled_on();
269: 		} else {
270: 			nled_off();
271: 		}
272: 		flag= ~flag;
273: 	}
274: }		
275: //串口数据接收处理
```

## z_main.c | loop_uart | 原文件第276-286行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
276: void loop_uart(void) {
277: 	if(uart1_get_ok) {
278: 		if(uart1_mode == 1) {					    //命令模式
279: 			parse_group_cmd(uart_receive_buf);
280: 			parse_cmd(uart_receive_buf);			
281: 		} else if(uart1_mode == 2) {			//单个舵机调试
282: 			parse_action(uart_receive_buf);
283: 		} else if(uart1_mode == 3) {		  //多路舵机调试
284: 			parse_action(uart_receive_buf);
285: 		} else if(uart1_mode == 4) {		  //存储模式
286: 			save_action(uart_receive_buf);
```

## z_main.c | loop_uart | 原文件第287-295行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
287: 		} 
288: 		uart1_mode = 0;
289: 		uart1_get_ok = 0;
290: 		uart1_open();
291: 	}
292: 	return;
293: }	
294: 
295: //循环读取PS2手柄数据
```

## z_main.c | loop_ps2_data | 原文件第296-308行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
296: void loop_ps2_data(void) {
297: 	static u32 systick_ms_bak = 0;
298: 	//每50ms处理1次
299: 	if(millis() - systick_ms_bak < 50) {
300: 		return;
301: 	}
302: 	systick_ms_bak = millis();
303: 	//读写手柄数据
304: 	psx_write_read(psx_buf);
305: 	
306: #if 0
307: 	//测试手柄数据，1为打开 0为关闭
308: 	sprintf((char *)cmd_return, "0x%02x,0x%02x,0x%02x,0x%02x,0x%02x,0x%02x,0x%02x,0x%02x,0x%02x\r\n", 
```

## z_main.c | loop_ps2_data | 原文件第309-316行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
309: 	(int)psx_buf[0], (int)psx_buf[1], (int)psx_buf[2], (int)psx_buf[3],
310: 	(int)psx_buf[4], (int)psx_buf[5], (int)psx_buf[6], (int)psx_buf[7], (int)psx_buf[8]);
311: 	uart1_send_str(cmd_return);
312: #endif 	
313: 	
314: 	return;
315: }	
316: //处理手柄上的按钮
```

## z_main.c | loop_ps2_button | 原文件第317-330行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
317: void loop_ps2_button(void) {
318: 	static unsigned char psx_button_bak[2] = {0};
319: 
320: 	//对比两次获取的按键值是否相同 ，相同就不处理，不相同则处理
321: 	if((psx_button_bak[0] == psx_buf[3])
322: 	&& (psx_button_bak[1] == psx_buf[4])) {				
323: 	} else {		
324: 		//处理buf3和buf4两个字节，这两个字节存储这手柄16个按键的状态
325: 		parse_psx_buf(psx_buf+3, psx_buf[1]);
326: 		psx_button_bak[0] = psx_buf[3];
327: 		psx_button_bak[1] = psx_buf[4];
328: 	}
329: 	return;
330: }	
```

## z_main.c | loop_ps2_button | 原文件第331-334行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
331: 
332: //--------------------------------------------------------------------------------
333: 
334: //软件复位函数，调用后单片机自动复位
```

## z_main.c | soft_reset | 原文件第335-340行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
335: void soft_reset(void) {
336: 	__set_FAULTMASK(1);     
337: 	NVIC_SystemReset();
338: }
339: 
340: //处理手柄按键字符，buf为字符数组，mode是指模式 主要是红灯和绿灯模式
```

## z_main.c | parse_psx_buf | 原文件第341-353行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
341: void parse_psx_buf(unsigned char *buf, unsigned char mode) {
342: 	u8 i, pos = 0;
343: 	static u16 bak=0xffff, temp, temp2;
344: 	temp = (buf[0]<<8) + buf[1];
345: 	
346: 	if(bak != temp) {
347: 		temp2 = temp;
348: 		temp &= bak;
349: 		for(i=0;i<16;i++) {     //16个按键一次轮询
350: 			if((1<<i) & temp) {
351: 			} else {
352: 				if((1<<i) & bak) {	//press 表示按键按下了
353: 															
```

## z_main.c | parse_psx_buf | 原文件第354-360行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
354: 					memset(uart_receive_buf, 0, sizeof(uart_receive_buf));					
355: 					if(mode == PS2_LED_RED) {
356: 						memcpy((char *)uart_receive_buf, (char *)pre_cmd_set_red[i], strlen(pre_cmd_set_red[i]));
357: 					} else continue;
358: 					//zx_uart_send_str(uart_receive_buf);
359: 					pos = str_contain_str(uart_receive_buf, (u8 *)"^");
360: 					if(pos) uart_receive_buf[pos-1] = '\0';
```

## z_main.c | parse_psx_buf | 原文件第361-370行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
361: 					if(str_contain_str(uart_receive_buf, (u8 *)"$")) {
362: 						uart1_close();
363: 						uart1_get_ok = 0;
364: 						strcpy((char *)cmd_return, (char *)uart_receive_buf+11);
365: 						strcpy((char *)uart_receive_buf, (char *)cmd_return);
366: 						uart1_get_ok = 1;
367: 						uart1_open();
368: 						uart1_mode = 1;
369: 					} else if(str_contain_str(uart_receive_buf, (u8 *)"#")) {
370: 						uart1_close();
```

## z_main.c | parse_psx_buf | 原文件第371-382行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
371: 						uart1_get_ok = 0;
372: 						strcpy((char *)cmd_return, (char *)uart_receive_buf+11);
373: 						strcpy((char *)uart_receive_buf,(char *) cmd_return);
374: 						uart1_get_ok = 1;
375: 						uart1_open();
376: 						uart1_mode = 2;
377: 					}
378: 					bak = 0xffff;
379: 				} else {//release 表示按键松开了
380: 										
381: 					memset(uart_receive_buf, 0, sizeof(uart_receive_buf));					
382: 					if(mode == PS2_LED_RED) {
```

## z_main.c | parse_psx_buf | 原文件第383-391行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
383: 						memcpy((char *)uart_receive_buf, (char *)pre_cmd_set_red[i], strlen(pre_cmd_set_red[i]));
384: 					} else continue;	
385: 					
386: 					pos = str_contain_str(uart_receive_buf, (u8 *)"^");
387: 					if(pos) {
388: 						if(str_contain_str(uart_receive_buf+pos, (u8 *)"$")) {
389: 							//uart1_close();
390: 							//uart1_get_ok = 0;
391: 							strcpy((char *)cmd_return, (char *)uart_receive_buf+pos);
```

## z_main.c | parse_psx_buf | 原文件第392-400行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
392: 							cmd_return[strlen((char *)cmd_return) - 1] = '\0';
393: 							strcpy((char *)uart_receive_buf, (char *)cmd_return);
394: 							parse_cmd(uart_receive_buf);
395: 							//uart1_get_ok = 1;
396: 							//uart1_mode = 1;
397: 						} else if(str_contain_str(uart_receive_buf+pos, (u8 *)"#")) {
398: 							//uart1_close();
399: 							//uart1_get_ok = 0;
400: 							strcpy((char *)cmd_return, (char *)uart_receive_buf+pos);
```

## z_main.c | parse_psx_buf | 原文件第401-417行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
401: 							cmd_return[strlen((char *)cmd_return) - 1] = '\0';
402: 							strcpy((char *)uart_receive_buf, (char *)cmd_return);
403: 							parse_action(uart_receive_buf);
404: 							//uart1_get_ok = 1;
405: 							//uart1_mode = 2;
406: 						}
407: 						//uart1_send_str(uart_receive_buf);
408: 					}	
409: 				}
410: 			}
411: 		}
412: 		bak = temp2;
413: 		beep_on();mdelay(10);beep_off();
414: 	}	
415: 	return;
416: }
417: 
```

## z_main.c | parse_psx_buf | 原文件第418-418行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
418: //命令解析函数
```

## z_main.c | parse_cmd | 原文件第419-427行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
419: void parse_cmd(u8 *cmd) {
420: 	int pos, i, index, int1, int2, int3, int4;
421: 	//uart1_send_str(cmd);
422: 
423: 	if(pos = str_contain_str(cmd, (u8 *)"$KMS:"), pos) {		
424: 		if(sscanf((char *)cmd, "$KMS:%d,%d,%d,%d!", &int1, &int2, &int3, &int4)) {
425: 			uart1_send_str((u8 *)"Try to find best pos:\r\n");
426: 			if(kinematics_move(int1, int2, int3, int4)) {
427: 				beep_on();mdelay(50);beep_off();mdelay(50);
```

## z_main.c | parse_cmd | 原文件第428-437行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
428: 			} else {
429: 				beep_on();mdelay(50);beep_off();mdelay(50);
430: 				beep_on();mdelay(50);beep_off();mdelay(50);
431: 				uart1_send_str((u8 *)"Can't find best pos!!!");
432: 			}					
433: 		}
434: 	}
435: }
436: 
437: 
```

## z_main.c | kinematics_move | 原文件第438-454行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
438: int kinematics_move(float x, float y, float z, int time) {
439: 	int i,j, min = 0, flag = 0;
440: 	
441: 	if(y < 0)return 0;
442: 	
443: 	//寻找最佳角度
444: 	flag = 0;
445: 	for(i=0;i>=-135;i--) {
446: 		if(0 == kinematics_analysis(x,y,z,i,&kinematics)){
447: 			if(i<min)min = i;
448: 			flag = 1;
449: 		}
450: 	}
451: 	
452: 	//用3号舵机与水平最大的夹角作为最佳值
453: 	if(flag) {
454: 		kinematics_analysis(x,y,z,min,&kinematics);
```

## z_main.c | kinematics_move | 原文件第455-465行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_main.c
以下为原始源码，不是截图OCR。
```
455: 		for(j=0;j<4;j++) {
456: 			set_servo(j, kinematics.servo_pwm[j], time);
457: 		}
458: 		return 1;
459: 	}
460: 	
461: 	return 0;
462: }
463: 
464: 
465: 
```

## z_sensor.c | 文件开头/全局定义 | 原文件第1-13行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_sensor.c
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

## z_sensor.c | 文件开头/全局定义 | 原文件第14-34行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_sensor.c
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
25: 	
26: 	红外传感器左 S3  PA2 - 绿线
27:   红外传感器右 S4  PA3 - 绿线
28: 	
29: 	超声波传感器 S6  TRIG - PA7 - 白线  Echo - PA5 - 绿线
30: 		
31: */
32: 
33: 
34: //初始化传感器IO口
```

## z_sensor.c | setup_sensor | 原文件第35-39行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
35: void setup_sensor(void) {
36: 	setup_csb();
37: 	setup_hw();	
38: }
39: 
```

## z_sensor.c | setup_hw | 原文件第40-49行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
40: void setup_hw(void){
41: 	GPIO_InitTypeDef GPIO_InitStructure;
42: 	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA , ENABLE);  
43: 	
44: 	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_2 | GPIO_Pin_3;   
45: 	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IPU;   
46: 	GPIO_Init(GPIOA, &GPIO_InitStructure);
47: 
48: }
49: 
```

## z_sensor.c | setup_csb | 原文件第50-60行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
50: void setup_csb(void){
51: 	GPIO_InitTypeDef GPIO_InitStructure;
52: 	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);  
53: 	
54: 	//初始化超声波IO口 Trig PA7  Echo PA5
55: 	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_7;  
56: 	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;  
57: 	GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;	
58: 	GPIO_Init(GPIOA, &GPIO_InitStructure); 	
59: 	
60: 	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_5;   
```

## z_sensor.c | setup_csb | 原文件第61-76行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
61: 	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;  
62: 	GPIO_Init(GPIOA, &GPIO_InitStructure); 	
63: 	
64: 	//初始化超声波定时器
65: 	TIM3_Int_Init(30000, 71);
66: }
67: 
68: 
69: void csb_Delay_Us(uint16_t time)  //延时函数
70: { 
71: 	uint16_t i,j;
72: 	for(i=0;i<time;i++)
73:   		for(j=0;j<9;j++);
74: }
75: 
76: 
```

## z_sensor.c | loop_sensor | 原文件第77-92行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
77: void loop_sensor(void) {
78: 	static u8 mode = 0;
79: 	static u8 adc_csb = 0;
80: 
81: 	adc_csb = get_csb_value();
82: 	//sprintf(cmd_return, "distance = %d cm\r\n", adc_csb);
83: 	//uart1_send_str(cmd_return);
84: 	if(mode==0){
85: 		set_servo(1, 900, 2000);
86: 		if(adc_csb < 10){
87: 			beep_on_times(1, 500);		
88: 		}
89: 		if(hw_l()==0){
90: 			mdelay(50);
91: 			if(hw_l()==0){
92: 				set_servo(1, 1500, 1000);
```

## z_sensor.c | loop_sensor | 原文件第93-110行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
93: 				mdelay(2000);
94: 				mode=1;
95: 			}
96: 		}
97: 		if(hw_r()==0){
98: 			mdelay(50);
99: 			if(hw_r()==0){
100: 				set_servo(1, 1500, 1000);
101: 				mdelay(2000);
102: 				mode=2;
103: 			}
104: 		}
105: 		
106: 	}else if(mode==1){
107: 		if(hw_l()==0){
108: 			beep_on_times(1, 100);
109: 			set_servo(1, 1500, 1000);
110: 		}
```

## z_sensor.c | if | 原文件第111-121行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
111: 		else if(hw_r()==0 && adc_csb > 10){
112: 			set_servo(1, 900, 2000);
113: 			mdelay(2000);
114: 			mode = 0;
115: 		}
116: 		
117: 	}else if(mode==2){
118: 		if(hw_r()==0){
119: 			beep_on_times(1, 500);
120: 			set_servo(1, 1500, 1000);
121: 		}
```

## z_sensor.c | if | 原文件第122-137行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
122: 		else if(hw_l()==0 && adc_csb > 10){
123: 			set_servo(1, 500, 1000);
124: 			mdelay(2000);
125: 			mode = 0;
126: 		} 
127: 	}
128: }
129: 
130: 
131: 
132: /*************************************************************
133: 函数名称：get_csb_value()
134: 功能介绍：采集超声波数据
135: 函数参数：无
136: 返回值：  采集的数据  
137: *************************************************************/
```

## z_sensor.c | get_csb_value | 原文件第138-151行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
138: int get_csb_value(void) {
139: 	u16 csb_t;
140: 	long timeout= 0;
141: 	Trig(1);
142: 	csb_Delay_Us(30);
143: 	Trig(0);
144: 	timeout= 0;
145: 	while(Echo() == 0&&(timeout++<10000)) //等待接收口高电平输出
146: 	if(timeout>=500000)return 0;
147: 	TIM_SetCounter(TIM3,0);//清除计数
148: 	TIM_Cmd(TIM3, ENABLE);  //使能TIMx外设
149: 	while(Echo() == 1&&(timeout++<10000))
150: 	if(timeout>=500000)return 0;
151: 	TIM_Cmd(TIM3, DISABLE);  //使能TIMx外设      
```

## z_sensor.c | get_csb_value | 原文件第152-162行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
152: 	csb_t = TIM_GetCounter(TIM3);//获取时间,分辨率为1US
153: 	//340m/s = 0.017cm/us
154: 	if(csb_t < 25000) {
155: 		//sprintf((char *)cmd_return, "csb_time=%d\r\n", (int)(csb_t*0.17));
156: 		//uart1_send_str(cmd_return);
157: 		csb_t = csb_t*0.017;
158: 		return csb_t;
159: 	}
160: 	return 0;
161: }
162: 
```

## z_sensor.h | 文件开头/全局定义 | 原文件第1-16行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_sensor.h
以下为原始源码，不是截图OCR。
```
1: #ifndef __SENSOR_H__
2: #define __SENSOR_H__
3: 
4: #include "stm32f10x_conf.h"
5: 
6: #define Trig(x) gpioA_pin_set(7, x);
7: #define Echo() GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_5)
8: 
9: #define hw_l() GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_2)
10: #define hw_r() GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_3)
11: 
12: //处理智能传感器功能
13: void setup_sensor(void);
14: void setup_hw(void);
15: void setup_csb(void);
16: 
```

## z_sensor.h | 文件开头/全局定义 | 原文件第17-21行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-智能栏杆.zip!/Jibot1-32出厂程序-智能栏杆/USER/z_sensor.h
以下为原始源码，不是截图OCR。
```
17: void loop_sensor(void);
18: 
19: int get_csb_value(void);
20: 
21: #endif
```
