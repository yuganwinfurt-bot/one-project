## z_actiongroupcontrol.c | 文件开头/全局定义 | 原文件第1-18行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
1: /*
2: 	动作组控制相关函数
3: 	
4: 	指令表：
5: 	$DST!              所有舵机停在当前位置，包括总线舵机和pwm舵机
6: 	$DST:x!            x号舵机停在当前位置，包括总线舵机和pwm舵机
7: 	$RST!              软件复位
8: 	$PGP:%d-%d!        将存储器中的动作组从USB（uart1）打印出来     
9: 	$DGS:x!            执行GXXXX一组动作组
10: 	$DGT:%d-%d,%d!     执行x-x动作组x次
11: 	$DJR!              所有舵机复位
12: 	$GETA!
13: 		
14: 	波特率 22.1184	
15: */
16: 
17: #include "z_rcc.h"		//配置时钟文件
18: #include "z_gpio.h"		//配置IO口文件
```

## z_actiongroupcontrol.c | 文件开头/全局定义 | 原文件第19-31行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
19: #include "z_global.h"	//存放全局变量
20: #include "z_delay.h"	//存放延时函数
21: #include "z_type.h"		//存放类型定义
22: #include "z_usart.h"	//存放串口功能文件
23: #include "z_timer.h"	//存放定时器功能文件
24: #include "z_ps2.h"		//存放索尼手柄
25: #include "z_w25q64.h"	//存储芯片的操作
26: #include "z_adc.h"		//ADC初始化
27: #include <stdio.h>		//标准库文件
28: #include <string.h>		//标准库文件
29: #include <math.h>		//标准库文件
30: 
31: #include "z_kinematics.h"	//逆运动学算法
```

## z_actiongroupcontrol.c | 文件开头/全局定义 | 原文件第32-45行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
32: #include "stm32f10x_iwdg.h"
33: #include "z_actiongroupcontrol.h"
34: 
35: 
36: //int i;								    //常用的一个临时变量
37: int do_start_index;				//动作组执行 起始序号
38: int do_times;						  //动作组执行 执行次数
39: int group_num_start;			//动作组执行 起始序号
40: int group_num_end;				//动作组执行 终止序号
41: int group_num_times;			//动作组执行 起始变量
42: //u32 dj_record_time = 1000;//学习时间默认1000
43: 
44: u8 needSaveFlag = 0;		    //偏差保存标志
45: //u32 save_addr_sector = 0;   
```

## z_actiongroupcontrol.c | 文件开头/全局定义 | 原文件第46-54行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
46: u32 bias_systick_ms_bak = 0;//偏差保存标志时间
47: u32 action_time = 0;        //动作组执行时间间隔
48: 
49: //--------------------------------------------------------------------------------
50: /*
51: 	初始化函数实现
52: */
53: 
54: //初始化舵机IO口
```

## z_actiongroupcontrol.c | setup_djio | 原文件第55-59行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
55: void setup_djio(void) {
56: 	dj_io_init();		//舵机IO口初始化
57: }	
58: 
59: //初始化定时器2 处理舵机PWM输出
```

## z_actiongroupcontrol.c | setup_dj_timer | 原文件第60-70行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
60: void setup_dj_timer(void) {
61: 	//timer0_init();	//51中的定时器初始化
62: 	TIM2_Int_Init(20000, 71);	 //32中的定时器初始化
63: }
64: 
65: /***********************************************
66: 	函数名称：setup_servo_bias() 
67: 	功能介绍：初始化舵机，将偏差带入初始值
68: 	函数参数：无
69: 	返回值：	无
70:  ***********************************************/
```

## z_actiongroupcontrol.c | setup_servo_bias | 原文件第71-80行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
71: void setup_servo_bias(void) {
72: 	u8 i;
73: 	for(i=0;i<DJ_NUM;i++) {
74: 		duoji_doing[i].aim = 1500+eeprom_info.dj_bias_pwm[i];
75: 		duoji_doing[i].cur = duoji_doing[i].aim;
76: 		duoji_doing[i].inc = 0;		
77: 	}
78: }
79: 
80: //执行开机动作组
```

## z_actiongroupcontrol.c | setup_do_group | 原文件第81-90行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
81: void setup_do_group(void) {
82: 		u8 i;
83: 	//执行预存命令 {G0000#000P1500T1000!#000P1500T1000!}
84: 	if(eeprom_info.pre_cmd[PRE_CMD_SIZE] == FLAG_VERIFY) {
85: 		strcpy((char *)uart_receive_buf, (char *)eeprom_info.pre_cmd);
86: 		if(eeprom_info.pre_cmd[0] == '$') {
87: 			parse_group_cmd(eeprom_info.pre_cmd);
88: 		} else {
89: 			for(i=16;i<strlen((char *)uart_receive_buf);i+=15) {
90: 				uart_receive_buf[i] = '0';
```

## z_actiongroupcontrol.c | setup_do_group | 原文件第91-107行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
91: 				uart_receive_buf[i+1] = '0';
92: 				uart_receive_buf[i+2] = '0';
93: 				uart_receive_buf[i+3] = '0';
94: 			}
95: 			parse_action(uart_receive_buf);
96: 		}
97: 	}
98: }
99: 
100: 
101: //--------------------------------------------------------------------------------
102: 
103: 
104: //--------------------------------------------------------------------------------
105: /*
106: 	主循环函数实现
107: */
```

## z_actiongroupcontrol.c | setup_do_group | 原文件第108-113行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
108: /***********************************************
109: 	函数名称：loop_monitor() 
110: 	功能介绍：设置pwm舵机偏差值
111: 	函数参数：无
112: 	返回值：	无
113:  ***********************************************/
```

## z_actiongroupcontrol.c | loop_monitor | 原文件第114-128行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
114: void loop_monitor(void) {
115: 	static u32 saveTime = 3000;
116: 	if((needSaveFlag == 1) || (millis() - bias_systick_ms_bak > saveTime)) {
117: 		needSaveFlag = 0;
118: 		bias_systick_ms_bak = millis();
119: 		rewrite_eeprom();
120: 	}	
121: 	return;
122: }	
123: 
124: /***********************************************
125: 	函数名称：loop_action() 
126: 	功能介绍：执行动作组指令
127: 	函数参数：无
128: 	返回值：	无
```

## z_actiongroupcontrol.c | loop_monitor | 原文件第129-129行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
129:  ***********************************************/
```

## z_actiongroupcontrol.c | loop_action | 原文件第130-142行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
130: void loop_action(void) {
131: 	static u32 systick_ms_bak = 0;
132: 	if(group_do_ok == 0) {
133: 		if(millis() - systick_ms_bak > action_time) {
134: 			systick_ms_bak =  millis();
135: 			if(group_num_times != 0 && do_times == 0) {
136: 			  group_do_ok = 1;
137: 			  uart1_send_str((u8 *)"@GroupDone!");
138: 			  return;
139: 			}
140: 			//调用do_start_index个动作
141: 			do_group_once(do_start_index);
142: 			
```

## z_actiongroupcontrol.c | loop_action | 原文件第143-156行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
143: 			if(group_num_start<group_num_end) {
144: 				if(do_start_index == group_num_end) {
145: 					do_start_index = group_num_start;
146: 					if(group_num_times != 0) {
147: 						do_times--;
148: 					}
149: 					return;
150: 				}
151: 				do_start_index++;
152: 			} else {
153: 				if(do_start_index == group_num_end) {
154: 					do_start_index = group_num_start;
155: 					if(group_num_times != 0) {
156: 						do_times--;
```

## z_actiongroupcontrol.c | loop_action | 原文件第157-173行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
157: 					}
158: 					return;
159: 				}
160: 				do_start_index--;
161: 			}
162: 		}
163: 	} else {
164:       action_time = 10;
165: 	}
166: }
167: 
168: /***********************************************
169: 	函数名称：parse_group_cmd() 
170: 	功能介绍：解析 $ 开头 ! 结尾的指令，处理动作组相关指令
171: 	函数参数：字符串指令表中的指令
172: 	返回值：	无
173:  ***********************************************/
```

## z_actiongroupcontrol.c | parse_group_cmd | 原文件第174-185行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
174: void parse_group_cmd(u8 *cmd) {
175: 	int pos, i, index, int1, int2;
176: 	//uart1_send_str(cmd);
177: 
178: 	if(pos = str_contain_str(cmd, (u8 *)"$DRS!"), pos) {
179: 		uart1_send_str((u8 *)"module:");
180: 		//uart1_send_str((u8 *)MODULE);
181: 		uart1_send_str((u8 *)"\r\n");
182: 		
183: 		uart1_send_str((u8 *)"bias:");
184: 		for(i=0;i<DJ_NUM;i++) {
185: 	    sprintf((char*)cmd_return, "%d  ", eeprom_info.dj_bias_pwm[i]);
```

## z_actiongroupcontrol.c | parse_group_cmd | 原文件第186-198行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
186: 			uart1_send_str(cmd_return);
187: 		}
188: 		uart1_send_str((u8 *)"\r\n");
189: 		
190: 		uart1_send_str((u8 *)"preCmd:");
191: 		uart1_send_str( eeprom_info.pre_cmd);
192: 		
193: 	} else if(pos = str_contain_str(cmd, (u8 *)"$DST!"), pos) {
194: 		group_do_ok  = 1;
195: 		for(i=0;i<DJ_NUM;i++) {
196: 			duoji_doing[i].inc = 0;	
197: 			duoji_doing[i].aim = duoji_doing[i].cur;
198: 		}
```

## z_actiongroupcontrol.c | parse_group_cmd | 原文件第199-207行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
199: 		zx_uart_send_str((u8 *)"#255PDST!");//总线停止
200: 	} else if(pos = str_contain_str(cmd, (u8 *)"$DST:"), pos) {
201: 		if(sscanf((char *)cmd, "$DST:%d!", &index)) {
202: 			duoji_doing[index].inc = 0;	
203: 			duoji_doing[index].aim = duoji_doing[index].cur;
204: 			sprintf((char *)cmd_return, "#%03dPDST!\r\n", (int)index);
205: 			zx_uart_send_str(cmd_return);
206: 			memset(cmd_return, 0, sizeof(cmd_return));
207: 		}
```

## z_actiongroupcontrol.c | parse_group_cmd | 原文件第208-217行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
208: 	} else if(pos = str_contain_str(cmd, (u8 *)"$RST!"), pos) {		
209: 		soft_reset();
210: 	} else if(pos = str_contain_str(cmd, (u8 *)"$PTG:"), pos) {		
211: 		if(sscanf((char *)cmd, "$PTG:%d-%d!", &int1, &int2)) {
212: 			print_group(int1, int2);
213: 		}
214: 	} else if(pos = str_contain_str(cmd, (u8 *)"$DGS:"), pos) {		
215: 		if(sscanf((char *)cmd, "$DGS:%d!", &int1)) {
216: 			group_do_ok = 1;
217: 			do_group_once(int1);
```

## z_actiongroupcontrol.c | parse_group_cmd | 原文件第218-228行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
218: 		}
219: 	} else if(pos = str_contain_str(cmd, (u8 *)"$DGT:"), pos) {		
220: 		if(sscanf((char *)cmd, "$DGT:%d-%d,%d!", &group_num_start, &group_num_end, &group_num_times)) {		
221: 			if(group_num_start != group_num_end) {
222: 				do_start_index = group_num_start;
223: 				do_times = group_num_times;
224: 				group_do_ok = 0;
225: 			} else {
226: 				do_group_once(group_num_start);
227: 			}
228: 		}
```

## z_actiongroupcontrol.c | parse_group_cmd | 原文件第229-236行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
229: 	} else if(pos = str_contain_str(cmd, (u8 *)"$DJR!"), pos) {	
230: 		zx_uart_send_str((u8 *)"#255P1500T2000!\r\n");
231: 		for(i=0;i<DJ_NUM;i++) {
232: 			duoji_doing[i].aim = 1500+eeprom_info.dj_bias_pwm[i];
233: 			duoji_doing[i].time = 2000;
234: 			duoji_doing[i].inc = (duoji_doing[i].aim -  duoji_doing[i].cur) / (duoji_doing[i].time/20.000);
235: 		}		
236: 	} else if(pos = str_contain_str(cmd, (u8 *)"$GETA!"), pos) {		
```

## z_actiongroupcontrol.c | parse_group_cmd | 原文件第237-247行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
237: 			uart1_send_str((u8 *)"AAA");
238: 	} 
239: }
240: 
241: 
242: /***********************************************
243: 	函数名称：save_action() 
244:   功能介绍：动作组保存函数，设置开机动作组
245: 	函数参数：只有用<>包含的字符串才能在此函数中进行解析
246: 	返回值：	无
247:  ***********************************************/
```

## z_actiongroupcontrol.c | save_action | 原文件第248-258行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
248: void save_action(u8 *str) {
249: 	int action_index = 0;
250: 	//预存命令处理
251: 	spiFlahsOn(1);
252: 	if(str[1] == '$' && str[2] == '!') {
253: 		eeprom_info.pre_cmd[PRE_CMD_SIZE] = 0;
254: 		rewrite_eeprom();   //去掉开机动作组
255: 		uart1_send_str((u8 *)"@CLEAR PRE_CMD OK!");
256: 		return;
257: 	}else if(str[1] == '$') {
258: 		//设置开机动作组
```

## z_actiongroupcontrol.c | save_action | 原文件第259-264行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
259: 		if(sscanf((char *)str, "<$DGT:%d-%d,%d!>", &group_num_start, &group_num_end, &group_num_times)) {
260: 			if(group_num_start == group_num_end) {
261: 				w25x_read(eeprom_info.pre_cmd, group_num_start*ACTION_SIZE, ACTION_SIZE);	
262: 			} else {
263: 				memset(eeprom_info.pre_cmd, 0, sizeof(eeprom_info.pre_cmd));
264: 				strcpy((char *)eeprom_info.pre_cmd, (char *)str+1);
```

## z_actiongroupcontrol.c | save_action | 原文件第265-277行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
265: 				eeprom_info.pre_cmd[strlen((char *)str) - 2] = '\0';
266: 			}
267: 			eeprom_info.pre_cmd[PRE_CMD_SIZE] = FLAG_VERIFY;
268: 			rewrite_eeprom();
269: 			//uart1_send_str(eeprom_info.pre_cmd);
270: 			uart1_send_str((u8 *)"@SET PRE_CMD OK!");
271: 		}
272: 		return;
273: 	}
274: 	
275: 	action_index = get_action_index(str);
276: 	//<G0001#001...>
277: 	if((action_index == -1) || str[6] != '#'){
```

## z_actiongroupcontrol.c | save_action | 原文件第278-288行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
278: 	//if( action_index == -1 ){
279: 		uart1_send_str((u8*)"E");
280: 		return;
281: 	}
282: 	//save_action_index_bak++;
283: 	//把尖括号替换成大括号直接存储到存储芯片里面去，则在执行动作组的时候直接拿出来解析就可以了
284: 	replace_char(str, '<', '{');
285: 	replace_char(str, '>', '}');
286: 	
287: 	if(action_index*ACTION_SIZE % W25Q64_SECTOR_SIZE == 0)w25x_erase_sector(action_index*ACTION_SIZE/W25Q64_SECTOR_SIZE);
288: 
```

## z_actiongroupcontrol.c | save_action | 原文件第289-301行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
289: 	w25x_write(str, action_index*ACTION_SIZE, strlen(str) + 1);
290: 	//uart1_send_str(str);
291: 	uart1_send_str((u8*)"A");
292: 	spiFlahsOn(0);
293: 	return;	
294: }
295: 
296: /***********************************************
297: 	函数名称：get_action_index() 
298: 	功能介绍：获取动作组序号
299: 	函数参数：无
300: 	返回值：	无
301:  ***********************************************/
```

## z_actiongroupcontrol.c | get_action_index | 原文件第302-321行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
302: int get_action_index(u8 *str) {
303: 	int index = 0;
304: 	//uart_send_str(str);
305: 	while(*str) {
306: 		if(*str == 'G') {
307: 			str++;
308: 			while((*str != '#') && (*str != '$')) {
309: 				index = index*10 + *str-'0';
310: 				str++;	
311: 			}
312: 			return index;
313: 		} else {
314: 			str++;
315: 		}
316: 	}
317: 	return -1;
318: }
319: 
320: /***********************************************
321: 	函数名称：print_group() 
```

## z_actiongroupcontrol.c | get_action_index | 原文件第322-325行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
322: 	功能介绍：打印存储器中的动作组
323: 	函数参数：起始位置，终止位置
324: 	返回值：	无
325:  ***********************************************/
```

## z_actiongroupcontrol.c | print_group | 原文件第326-339行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
326: void print_group(int start, int end) {
327: 	spiFlahsOn(1);
328: 	
329: 	if(start > end) {
330: 		int_exchange(&start, &end);
331: 	}
332: 	
333: 	for(;start<=end;start++) {
334: 		memset(uart_receive_buf, 0, sizeof(uart_receive_buf));
335: 		w25x_read(uart_receive_buf, start*ACTION_SIZE, ACTION_SIZE);
336: 		uart1_send_str(uart_receive_buf);
337: 		uart1_send_str((u8 *)"\r\n");
338: 		
339: 		uart3_send_str(uart_receive_buf);
```

## z_actiongroupcontrol.c | print_group | 原文件第340-351行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
340: 		uart3_send_str((u8 *)"\r\n");
341: 	}
342: 	
343: 	spiFlahsOn(0);
344: }
345: 
346: /***********************************************
347: 	函数名称：int_exchange() 
348: 	功能介绍：数据交换
349: 	函数参数：无
350: 	返回值：	无
351:  ***********************************************/
```

## z_actiongroupcontrol.c | int_exchange | 原文件第352-365行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
352: void int_exchange(int *int1, int *int2) {
353: 	int int_temp;
354: 	int_temp = *int1;
355: 	*int1 = *int2;
356: 	*int2 = int_temp;
357: }
358: 
359: /***********************************************
360: 	函数名称：erase_sector() 
361: 	功能介绍：擦除动作组指令
362: 	函数参数：无
363: 	返回值：	无
364:  ***********************************************/
365: /*
```

## z_actiongroupcontrol.c | erase_sector | 原文件第366-381行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
366: void erase_sector(int start, int end) {
367: 	if(start > end) {
368: 		int_exchange(&start, &end);
369: 	}
370: 	if(end >= 127)end = 127;
371: 	for(;start<=end;start++) {
372: 		SpiFlashEraseSector(start);
373: 		sprintf(cmd_return, "@Erase %d OK!", start);
374: 		uart1_send_str(cmd_return);
375: 	}
376: 	save_action_index_bak = 0;
377: }
378: */
379: 
380: /***********************************************
381: 	函数名称：getMaxTime() 
```

## z_actiongroupcontrol.c | erase_sector | 原文件第382-385行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
382: 	功能介绍：获取最大时间
383: 	函数参数：无
384: 	返回值：	无
385:  ***********************************************/
```

## z_actiongroupcontrol.c | getMaxTime | 原文件第386-399行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
386: int getMaxTime(u8 *str) {
387:    int i = 0, max_time = 0, tmp_time = 0;
388:    while(str[i]) {
389:       if(str[i] == 'T') {
390:           tmp_time = (str[i+1]-'0')*1000 + (str[i+2]-'0')*100 + (str[i+3]-'0')*10 + (str[i+4]-'0');
391:           if(tmp_time>max_time)max_time = tmp_time;
392:           i = i+4;
393:           continue;
394:       }
395:       i++;
396:    }
397:    return max_time;
398: }
399: 
```

## z_actiongroupcontrol.c | getMaxTime | 原文件第400-405行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
400: /***********************************************
401: 	函数名称：do_group_once() 
402: 	功能介绍：从存储芯片中读取第group_num个动作组，执行动作组
403: 	函数参数：动作组序号
404: 	返回值：	无
405:  ***********************************************/
```

## z_actiongroupcontrol.c | do_group_once | 原文件第406-419行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
406: void do_group_once(int group_num) {
407: 	spiFlahsOn(1);
408: 	//将uart_receive_buf清零
409: 	memset(uart_receive_buf, 0, sizeof(uart_receive_buf));
410: 	//从存储芯片中读取第group_num个动作组
411: 	w25x_read(uart_receive_buf, group_num*ACTION_SIZE, ACTION_SIZE-1);	
412: 	//获取最大的组时间
413: 	action_time = getMaxTime(uart_receive_buf);
414: 	
415: 	//把读取出来的动作组传递到parse_action执行
416: 	parse_action(uart_receive_buf);
417: 	spiFlahsOn(0);
418: }
419: 
```

## z_actiongroupcontrol.c | do_group_once | 原文件第420-425行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
420: /***********************************************
421: 	函数名称：parse_action() 
422: 	功能介绍：解析以#开头！结尾的指令
423: 	函数参数：无
424: 	返回值：	无
425:  ***********************************************/
```

## z_actiongroupcontrol.c | parse_action | 原文件第426-433行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
426: void parse_action(u8 *uart_receive_buf) {
427: 	u16 index,  time, i = 0, j, step = 0;
428: 	int bias;
429: 	float pwm;
430: 	float aim_temp;
431: 	zx_uart_send_str(uart_receive_buf);
432: 	//解析#000PSCK+001!指令，调节pwm舵机偏差
433: 	if(uart_receive_buf[0] == '#' && uart_receive_buf[4] == 'P' && uart_receive_buf[5] == 'S' && uart_receive_buf[6] == 'C' && uart_receive_buf[7] == 'K' && uart_receive_buf[12] == '!') {
```

## z_actiongroupcontrol.c | parse_action | 原文件第434-440行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
434: 		index = (uart_receive_buf[1] - '0')*100 + (uart_receive_buf[2] - '0')*10 + (uart_receive_buf[3] - '0');
435: 		bias = (uart_receive_buf[9] - '0')*100 + (uart_receive_buf[10] - '0')*10 + (uart_receive_buf[11] - '0');
436: 		if((bias >= -500) && (bias <= 500) && (index < DJ_NUM)) {
437: 			if(uart_receive_buf[8] == '+') {
438: 			} else if(uart_receive_buf[8] == '-') {
439: 				bias = -bias;
440: 			}
```

## z_actiongroupcontrol.c | parse_action | 原文件第441-451行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
441: 			aim_temp = duoji_doing[index].cur - eeprom_info.dj_bias_pwm[index] + bias;
442: 			eeprom_info.dj_bias_pwm[index] = bias;			
443: 			if(aim_temp > 2497){
444: 				aim_temp = 2497;
445: 			} else if(aim_temp < 500) {
446: 				aim_temp = 500;
447: 			}
448: 			
449: 			duoji_doing[index].aim = aim_temp;
450: 			duoji_doing[index].inc = (duoji_doing[index].aim - duoji_doing[index].cur)/5;
451: 			bias_systick_ms_bak = millis();
```

## z_actiongroupcontrol.c | parse_action | 原文件第452-458行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
452: 			needSaveFlag = 1;
453: 		}
454: 		return;
455: 		//解析#000PDST!指令，使PWM舵机停止在当前位置
456: 	} else if(uart_receive_buf[0] == '#' && uart_receive_buf[4] == 'P' && uart_receive_buf[5] == 'D' && uart_receive_buf[6] == 'S' && uart_receive_buf[7] == 'T' && uart_receive_buf[8] == '!') {
457: 		index = (uart_receive_buf[1] - '0')*100 + (uart_receive_buf[2] - '0')*10 + (uart_receive_buf[3] - '0');		
458: 		if(index < DJ_NUM) {
```

## z_actiongroupcontrol.c | parse_action | 原文件第459-473行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
459: 			duoji_doing[index].inc = 0;	
460: 			duoji_doing[index].aim = duoji_doing[index].cur;
461: 		}
462: 		return;
463: 	}
464: 	
465: 	step = 1;
466: 	while(uart_receive_buf[i]) {
467: 		if(uart_receive_buf[i] == '#' && step == 1) {
468: 			j = i;
469: 			index = 0;i++;
470: 			while(uart_receive_buf[i] && uart_receive_buf[i] != 'P') {
471: 				index = index*10 + uart_receive_buf[i]-'0';i++;
472: 			}
473: 			if(i-j-1 != 3) {
```

## z_actiongroupcontrol.c | parse_action | 原文件第474-488行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
474: 				step = 1;
475: 			} else {
476: 				step = 2;
477: 			}
478: 		} else if(uart_receive_buf[i] == 'P' && step == 2) {
479: 			j = i;
480: 			pwm = 0;i++;
481: 			while(uart_receive_buf[i] && uart_receive_buf[i] != 'T') {
482: 				pwm = pwm*10 + uart_receive_buf[i]-'0';i++;
483: 			}
484: 			if(i-j-1 != 4) {
485: 				step = 1;
486: 			} else {
487: 				step = 3;
488: 			}
```

## z_actiongroupcontrol.c | parse_action | 原文件第489-503行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
489: 		} else if(uart_receive_buf[i] == 'T' && step == 3) {
490: 			j = i;
491: 			time = 0;i++;
492: 			while(uart_receive_buf[i] && uart_receive_buf[i] != '!') {
493: 				time = time*10 + uart_receive_buf[i]-'0';i++;
494: 			}
495: 			
496: 			//同步的时候防止数据太快不稳定
497: 			if(time<500) {
498: 				time = time+300;
499: 			}
500: 			
501: 			step = 1;
502: 			if(i-j-1 != 4) {
503: 			} else {
```

## z_actiongroupcontrol.c | parse_action | 原文件第504-515行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
504: 				if(index < DJ_NUM && (pwm<=2500)&& (pwm>=500) && (time<=10000)) {
505: 					pwm += eeprom_info.dj_bias_pwm[index];
506: 					
507: 					if(pwm>2497)pwm=2497;
508: 					if(pwm<500)pwm=500;
509: 					
510: 					if(time < 20) {
511: 						duoji_doing[index].aim = pwm;
512: 						duoji_doing[index].cur = pwm;
513: 						duoji_doing[index].inc = 0;
514: 					} else {
515: 						duoji_doing[index].aim = pwm;
```

## z_actiongroupcontrol.c | parse_action | 原文件第516-525行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
516: 						duoji_doing[index].time = time;
517: 						duoji_doing[index].inc = (duoji_doing[index].aim -  duoji_doing[index].cur) / (duoji_doing[index].time/20.000);
518: 					}
519: 
520: 					//sprintf(cmd_return, "#%03dP%04dT%04d! %f \r\n", index, pwm, time, duoji_doing[index].inc);
521: 					//uart1_send_str(cmd_return);
522: 				} 
523: 				
524: 				if(index == 255) {
525: 					for(index=0;index<DJ_NUM;index++) {
```

## z_actiongroupcontrol.c | parse_action | 原文件第526-540行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
526: 						pwm =1500 + eeprom_info.dj_bias_pwm[index];
527: 						duoji_doing[index].aim = pwm;
528: 						duoji_doing[index].time = time;
529: 						duoji_doing[index].inc = (duoji_doing[index].aim -  duoji_doing[index].cur) / (duoji_doing[index].time/20.000);
530: 					}
531: 				}
532: 			}
533: 		} else {
534: 			i++;
535: 		}
536: 	}	
537: }
538: 
539: /***********************************************
540: 	函数名称：replace_char() 
```

## z_actiongroupcontrol.c | parse_action | 原文件第541-544行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
541: 	功能介绍：字符串中的字符替代函数 把str字符串中所有的ch1换成ch2
542: 	函数参数：字符串
543: 	返回值：	无
544:  ***********************************************/
```

## z_actiongroupcontrol.c | replace_char | 原文件第545-560行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
545: void replace_char(u8*str, u8 ch1, u8 ch2) {
546: 	while(*str) {
547: 		if(*str == ch1) {
548: 			*str = ch2;
549: 		} 
550: 		str++;
551: 	}
552: 	return;
553: }
554: 
555: /***********************************************
556: 	函数名称：rewrite_eeprom() 
557: 	功能介绍：把eeprom_info写入到W25Q64_INFO_ADDR_SAVE_STR位置
558: 	函数参数：无
559: 	返回值：	无
560:  ***********************************************/
```

## z_actiongroupcontrol.c | rewrite_eeprom | 原文件第561-573行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
561: void rewrite_eeprom(void) {
562: 	spiFlahsOn(1);
563: 	w25x_erase_sector(W25Q64_INFO_ADDR_SAVE_STR/4096);
564: 	w25x_writeS((u8 *)(&eeprom_info), W25Q64_INFO_ADDR_SAVE_STR, sizeof(eeprom_info));
565: 	spiFlahsOn(0);
566: }
567: 
568: /***********************************************
569: 	函数名称：set_servo() 
570: 	功能介绍：舵机控制
571: 	函数参数：id，pwm值，转动时间
572: 	返回值：	无
573:  ***********************************************/
```

## z_actiongroupcontrol.c | set_servo | 原文件第574-580行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
574: void set_servo(int index, int pwm, int time) {
575: 	duoji_doing[index].aim = pwm;
576: 	duoji_doing[index].time = time;
577: 	duoji_doing[index].inc = (duoji_doing[index].aim -  duoji_doing[index].cur) / (duoji_doing[index].time/20.000);
578: 	sprintf((char *)cmd_return, "#%03dP%04dT%04d!\r\n", index, pwm, time);
579: 	zx_uart_send_str(cmd_return);	
580: }
```

## z_actiongroupcontrol.h | 文件开头/全局定义 | 原文件第1-18行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.h
以下为原始源码，不是截图OCR。
```
1: #ifndef __ACTIONGROUPCONTROL_H__
2: #define __ACTIONGROUPCONTROL_H__
3: 
4: #define CAR_PWM						0
5: #define ADC_VOL						7
6: #define ACTION_SIZE					256
7: #define W25Q64_INFO_ADDR_SAVE_STR	(((8<<10)-4)<<10)//(8*1024-4)*1024		//eeprom_info结构体存储的位置
8: #define FLAG_VERIFY 				0x38
9: 
10: #include "stm32f10x_conf.h"
11: 
12: /*
13: 	初始化函数声明
14: */
15: 			
16: //初始化低压报警
17: void setup_vol(void);		
18: //初始化舵机IO口
```

## z_actiongroupcontrol.h | 文件开头/全局定义 | 原文件第19-39行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.h
以下为原始源码，不是截图OCR。
```
19: void setup_djio(void);			
20: //初始化定时器2 处理舵机PWM输出
21: void setup_dj_timer(void);		
22: 			
23: //初始化舵机偏差
24: void setup_servo_bias(void);
25: //执行开机动作组
26: void setup_do_group(void);
27: 
28: //动作组批量执行
29: void loop_action(void);		
30: //定时保存偏差变量
31: void loop_monitor(void);	
32: 
33: /*
34: 	子循环函数声明
35: */
36: void parse_group_cmd(u8 *cmd);
37: 
38: void save_action(u8 *str);
39: int get_action_index(u8 *str);//获取动作序号
```

## z_actiongroupcontrol.h | 文件开头/全局定义 | 原文件第40-52行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_actiongroupcontrol.h
以下为原始源码，不是截图OCR。
```
40: void print_group(int start, int end);
41: void int_exchange(int *int1, int *int2);
42: void erase_sector(int start, int end);
43: 
44: void do_group_once(int group_num); 
45: u8 check_dj_state(void);//检查舵机状态，是否全部到位
46: 
47: void parse_action(u8 *uart_receive_buf);
48: void replace_char(u8*str, u8 ch1, u8 ch2);
49: void rewrite_eeprom(void);
50: 
51: void set_servo(int index, int pwm, int time);	//设置舵机角度					
52: #endif 
```

## z_adc.c | 文件开头/全局定义 | 原文件第1-31行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_adc.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_adc.c
以下为原始源码，不是截图OCR。
```
32: #define ADC1_DR_Address ((u32)0x40012400+0x4c)
33: u16 ADC_ConvertedValue[ADC_NUM] = {0};
34: 
```

## z_adc.c | ADC_init | 原文件第35-40行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_adc.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_adc.c
以下为原始源码，不是截图OCR。
```
41: void ADC1_GPIO_Configuration(void) {
42: 	GPIO_InitTypeDef GPIO_InitStructure;
43: 	
44: 	RCC_AHBPeriphClockCmd(RCC_AHBPeriph_DMA1, ENABLE);
45: 	RCC_APB2PeriphClockCmd(RCC_APB2Periph_ADC1 | RCC_APB2Periph_GPIOA, ENABLE); 
46: 
47: 	GPIO_InitStructure.GPIO_Pin  = GPIO_Pin_0; 
48: 	
49: 	GPIO_InitStructure.GPIO_Mode =GPIO_Mode_AIN; 
50: 	GPIO_Init(GPIOA,&GPIO_InitStructure); 	
51: }
52: 
53: 
```

## z_adc.c | ADC1_Configuration | 原文件第54-61行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_adc.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_adc.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_adc.c
以下为原始源码，不是截图OCR。
```
70: 	//ADC_RegularChannelConfig(ADC1, ADC_Channel_1, 2, ADC_SampleTime_239Cycles5 );
71: 	//ADC_RegularChannelConfig(ADC1, ADC_Channel_2, 3, ADC_SampleTime_239Cycles5 );
72: 	//ADC_RegularChannelConfig(ADC1, ADC_Channel_3, 1, ADC_SampleTime_239Cycles5 );
73: 	//ADC_RegularChannelConfig(ADC1, ADC_Channel_4, 1, ADC_SampleTime_239Cycles5 );
74: 	//ADC_RegularChannelConfig(ADC1, ADC_Channel_1, 2, ADC_SampleTime_239Cycles5 );
```

## z_adc.c | ADC1_Configuration | 原文件第75-81行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_adc.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_adc.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_adc.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_adc.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_adc.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_adc.c
以下为原始源码，不是截图OCR。
```
116: 	DMA_InitStructure.DMA_BufferSize = ADC_NUM; //DMA通道的DMA缓存的大小*****
117: 	DMA_InitStructure.DMA_PeripheralInc = DMA_PeripheralInc_Disable; //外设地址寄存器不变
118: 	DMA_InitStructure.DMA_MemoryInc = DMA_MemoryInc_Enable; //内存地址寄存器递增
119: 	DMA_InitStructure.DMA_PeripheralDataSize = DMA_PeripheralDataSize_HalfWord; //数据宽度为16位
120: 	DMA_InitStructure.DMA_MemoryDataSize = DMA_MemoryDataSize_HalfWord; //数据宽度为16位
```

## z_adc.c | DMA_Configuration | 原文件第121-128行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_adc.c
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

## z_timer.h | 文件开头/全局定义 | 原文件第1-16行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_timer.h
以下为原始源码，不是截图OCR。
```
1: #ifndef __TB_TIMER_H__
2: #define __TB_TIMER_H__
3: 
4: #include "stm32f10x.h"
5: 
6: void SysTick_Int_Init(void);
7: void TIM1_Int_Init(u16 arr,u16 psc);
8: void TIM2_Int_Init(u16 arr,u16 psc);
9: 
10: void TIM3_Int_Init(u16 arr,u16 psc);
11: u32 millis(void);
12: 
13: void TIM3_Pwm_Init(u16 arr,u16 psc);
14: void TIM4_Pwm_Init(u16 arr,u16 psc);
15: void duoji_inc_handle(u8 index);
16: 
```

## z_timer.h | 文件开头/全局定义 | 原文件第17-27行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/src/z_timer.h
以下为原始源码，不是截图OCR。
```
17: #define Timeout_ON()	TIM_ITConfig(TIM1, TIM_IT_Update, ENABLE)
18: #define Timeout_OFF()	TIM_ITConfig(TIM1, TIM_IT_Update, DISABLE)
19: #define CCP_Falling()	TIM_OC1PolarityConfig(TIM1,TIM_ICPolarity_Falling)
20: #define CCP_Rising()	TIM_OC1PolarityConfig(TIM1,TIM_ICPolarity_Rising)
21: void timer1_ir_init(u16 arr,u16 psc);				
22: 
23: 
24: void IWDG_Init(void);
25: 
26: 
27: #endif
```

## z_main.c | 文件开头/全局定义 | 原文件第1-22行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
以下为原始源码，不是截图OCR。
```
114: /*-------------------------------------------------------------------------------------------------------
115: *  程序从这里执行				
116: *  这个启动代码 完成时钟配置 使用外部晶振作为STM32的运行时钟 并倍频到72M
117: -------------------------------------------------------------------------------------------------------*/
118: 
```

## z_main.c | main | 原文件第119-130行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
以下为原始源码，不是截图OCR。
```
142: 		loop_uart();		//串口数据接收处理
143: 		loop_action();	//动作组批量执行
144: 		loop_ps2_data();//循环读取PS2手柄数据
145: 		loop_ps2_button();//处理手柄上的按钮
146: 		loop_monitor();   //定时保存一些变量
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
以下为原始源码，不是截图OCR。
```
156: void setup_rcc(void) {   //初始化时钟
157: 	tb_rcc_init();	  	   //时钟初始化
158: }
159: 
```

## z_main.c | setup_global | 原文件第160-163行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
以下为原始源码，不是截图OCR。
```
160: void setup_global(void) {//初始化全局变量
161: 	tb_global_init();	
162: }
163: 
```

## z_main.c | setup_gpio | 原文件第164-167行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
以下为原始源码，不是截图OCR。
```
164: void setup_gpio(void) {  //初始化IO口
165: 	tb_gpio_init();		    
166: }
167: 
```

## z_main.c | setup_nled | 原文件第168-172行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
以下为原始源码，不是截图OCR。
```
168: void setup_nled(void) {  //初始化工作指示灯
169: 	nled_init();		
170: 	nled_off();		         //工作指示灯关闭
171: }
172: 
```

## z_main.c | setup_beep | 原文件第173-176行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
以下为原始源码，不是截图OCR。
```
173: void setup_beep(void) {  //初始化定时器蜂鸣器
174: 	beep_init();		
175: 	beep_off();			       //关闭蜂鸣器
176: }			
```

## z_main.c | setup_w25q64 | 原文件第177-187行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
以下为原始源码，不是截图OCR。
```
203: void setup_adc(void) {//初始化ADC采集 使用DMA初始化
204: 	ADC_init();
205: }
206: 
```

## z_main.c | setup_ps2 | 原文件第207-210行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
以下为原始源码，不是截图OCR。
```
207: void setup_ps2(void) {//初始化PS2手柄
208: 	PSX_init();	
209: }
210: 
```

## z_main.c | setup_uart1 | 原文件第211-219行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
以下为原始源码，不是截图OCR。
```
240: void setup_systick(void) {
241: 	//系统滴答时钟初始化	
242: 	SysTick_Int_Init();
243: }	
244: //初始化启动信号
```

## z_main.c | setup_start | 原文件第245-253行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
以下为原始源码，不是截图OCR。
```
335: 
336: //--------------------------------------------------------------------------------
337: 
338: //软件复位函数，调用后单片机自动复位
```

## z_main.c | soft_reset | 原文件第339-344行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
以下为原始源码，不是截图OCR。
```
422: //命令解析函数
```

## z_main.c | parse_cmd | 原文件第423-431行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.c
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

## z_main.h | 文件开头/全局定义 | 原文件第1-16行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.h
以下为原始源码，不是截图OCR。
```
1: #ifndef __MAIN_H__
2: #define __MAIN_H__
3: 
4: #include "stm32f10x_conf.h"
5: 
6: 
7: /*
8: 	宏定义数据
9: */
10: #define VERSION				  20220728	//版本定义
11: #define ACTION_USE_ROM	0			   //1:动作组使用内部数组动作组	0:动作组使用上位机下载动作组
12: #define CYCLE 				  1000		//PWM模块周期
13: #define PS2_LED_RED  		0x73		//PS2手柄红灯模式
14: #define PS2_LED_GRN  		0x41		//PS2手柄绿灯模式
15: #define PSX_BUTTON_NUM 	16			//手柄按键数目
16: #define PS2_MAX_LEN 		64			//手柄命令最大字节数
```

## z_main.h | 文件开头/全局定义 | 原文件第17-31行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.h
以下为原始源码，不是截图OCR。
```
17: #define FLAG_VERIFY 		0x25		//校验标志
18: #define ACTION_SIZE 		0x80		//一个动作的存储大小
19: 
20: 
21: #define W25Q64_INFO_ADDR_SAVE_STR			(((8<<10)-2)<<10)  //(8*1024-1)*1024		//eeprom_info结构体存储的位置
22: 
23: /*
24: 	初始化函数声明
25: */
26: 
27: void setup_rcc(void);     //初始化时钟
28: void setup_global(void);  //初始化全局变量		
29: void setup_gpio(void);    //初始化IO口			
30: void setup_nled(void);    //初始化工作指示灯
31: void setup_beep(void);	  //初始化蜂鸣器		
```

## z_main.h | 文件开头/全局定义 | 原文件第32-43行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.h
以下为原始源码，不是截图OCR。
```
32: void setup_djio(void);	  //初始化舵机IO口
33: void setup_w25q64(void);	//初始化存储器W25Q64
34: void setup_ps2(void);      //初始化PS2手柄
35: void setup_uart1(void);	  //初始化串口1
36: void setup_uart2(void);	  //初始化串口2
37: void setup_uart3(void);	  //初始化串口3
38: void setup_systick(void);	//初始化滴答时钟，1S增加一次systick_ms的值
39: void setup_start(void);		//初始化启动信号
40: void setup_interrupt(void);//初始化总中断
41: /*
42: 	主循环函数声明
43: */
```

## z_main.h | 文件开头/全局定义 | 原文件第44-54行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.h
以下为原始源码，不是截图OCR。
```
44: void loop_nled(void);	        //循环执行工作指示灯，500ms跳动一次	
45: void loop_uart(void);	        //串口数据接收处理
46: void loop_action(void);	        //动作组批量执行
47: void loop_bt_once(void);	    //蓝牙修改波特率和名称	
48: void loop_ps2_data(void);	    //循环读取PS2手柄数据
49: void loop_ps2_button(void);	    //处理手柄上的按钮
50: void loop_ps2_car(void);    //处理小车电机摇杆控制
51: void loop_vol_warning(void);    //处理低压报警
52: void loop_inc(void);			//循环处理增量
53: 
54: 
```

## z_main.h | 文件开头/全局定义 | 原文件第55-64行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_main.h
以下为原始源码，不是截图OCR。
```
55: void soft_reset(void);					               //软件复位
56: 
57: void parse_psx_buf(u8 *buf, u8 mode);     	   //手柄按键解析子函数
58: void parse_cmd(u8 *cmd);			            	   //命令解析
59: 
60: int kinematics_move(float x, float y, float z, int time);//逆运动学转动
61: 
62: 
63: #endif
64: 
```

## z_sensor.c | 文件开头/全局定义 | 原文件第1-13行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_sensor.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_sensor.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
33: void setup_sensor(void) {
34: 	ADC_init();
35: }
36: 
```

## z_sensor.c | loop_sensor | 原文件第37-46行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
37: void loop_sensor(void) {
38: 	light_control();
39: }
40: 
41: 
42: /*************************************************************
43: 功能介绍：获取光敏传感器的AD值，换算为PWM值，控制机械臂弯曲
44: 函数参数：无
45: 返回值：  无  
46: *************************************************************/
```

## z_sensor.c | light_control | 原文件第47-57行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
47: void light_control(void) {	
48: 	u8 j;
49: 	u16 light_value;	
50: 	static u32 systick_ms_light = 0;
51: 	//每隔500毫秒执行一次
52: 	if(millis() - systick_ms_light >= 500){
53: 		systick_ms_light = millis(); 	
54: 		light_value = ADC_ConvertedValue[0];  //获取光敏传感器的AD值
55: 		//sprintf((char *)cmd_return,"light_value:%d\r\n",(int)light_value);
56: 		//uart1_send_str(cmd_return);
57: 		//无光照时，光敏值最大1024，计算得出机械臂弯曲时的舵机pwm值
```

## z_sensor.c | light_control | 原文件第58-70行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
58: 		servo_pwm[1] = 1150 + light_value/4;
59: 		servo_pwm[2] = 1250 + light_value/4;
60: 		servo_pwm[3] = 1950 - light_value/4;
61: 		//光照强时机械臂直立
62: 		if(servo_pwm[1] < 1500){servo_pwm[1] = 1500;}
63: 		if(servo_pwm[2] < 1500){servo_pwm[2] = 1500;}
64: 		if(servo_pwm[3] > 1500){servo_pwm[3] = 1500;}
65: 		//控制1，2，3号舵机使机械臂弯曲
66: 		for(j=1;j<4;j++) {
67: 			set_servo(j, servo_pwm[j], 1000);
68: 		}		
69: 	}
70: }
```

## z_sensor.h | 文件开头/全局定义 | 原文件第1-18行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-光控弯曲.zip!/Jibot1-32出厂程序-光控弯曲/USER/z_sensor.h
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
15: void light_control(void);			//按键夹取
16: 
17: 
18: #endif
```
