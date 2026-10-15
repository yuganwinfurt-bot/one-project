## z_actiongroupcontrol.c | 文件开头/全局定义 | 原文件第1-18行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
55: void setup_djio(void) {
56: 	dj_io_init();		//舵机IO口初始化
57: }	
58: 
59: //初始化定时器2 处理舵机PWM输出
```

## z_actiongroupcontrol.c | setup_dj_timer | 原文件第60-70行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
129:  ***********************************************/
```

## z_actiongroupcontrol.c | loop_action | 原文件第130-142行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
278: 	//if( action_index == -1 ){
279: 		uart1_send_str("E");
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
289: 	w25x_write(str, action_index*ACTION_SIZE, strlen(str) + 1);
290: 	//uart1_send_str(str);
291: 	uart1_send_str("A");
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
322: 	功能介绍：打印存储器中的动作组
323: 	函数参数：起始位置，终止位置
324: 	返回值：	无
325:  ***********************************************/
```

## z_actiongroupcontrol.c | print_group | 原文件第326-339行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
382: 	功能介绍：获取最大时间
383: 	函数参数：无
384: 	返回值：	无
385:  ***********************************************/
```

## z_actiongroupcontrol.c | getMaxTime | 原文件第386-399行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
以下为原始源码，不是截图OCR。
```
541: 	功能介绍：字符串中的字符替代函数 把str字符串中所有的ch1换成ch2
542: 	函数参数：字符串
543: 	返回值：	无
544:  ***********************************************/
```

## z_actiongroupcontrol.c | replace_char | 原文件第545-560行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/src/z_actiongroupcontrol.c
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

## z_sensor.c | 文件开头/全局定义 | 原文件第1-13行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/USER/z_sensor.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
14: #include "z_kinematics.h"	//逆运动学算法
15: #include "stm32f10x_iwdg.h"
16: 
17: #include "z_sensor.h"
18: #include "z_actiongroupcontrol.h"
19: 
20: /*
21: 	智能功能代码
22: 	
23: 	IO口分布
24: 	模式切换按键 S3  PA2 -绿线
25: 	
26: 	动作执行按键 S4  PA3 -绿线
27: 		
28: */
29: 
30: 
31: //初始化传感器IO口
```

## z_sensor.c | setup_sensor | 原文件第32-41行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
32: void setup_sensor(void) {
33: 	GPIO_InitTypeDef GPIO_InitStructure;
34: 	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA , ENABLE);  
35: 	
36: 	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_2 | GPIO_Pin_3;   
37: 	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IPU;   
38: 	GPIO_Init(GPIOA, &GPIO_InitStructure);
39: 	
40: }
41: 
```

## z_sensor.c | loop_sensor | 原文件第42-50行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
42: void loop_sensor(void) {
43: 	button_jiaqu();
44: }
45: 
46: /*************************************************************
47: 功能介绍：一号按键短按切换模式，长按执行前抓动作。二号按键短按根据当前模式执行动作组
48: 函数参数：无
49: 返回值：  无  
50: *************************************************************/
```

## z_sensor.c | button_jiaqu | 原文件第51-64行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
51: void button_jiaqu(void) {
52: 	
53: 	static u8 mode = 0;	
54: 	static u32 systick_ms_button = 0;
55: 	
56: 	if(group_do_ok == 0)return;//有动作执行，直接返回
57: 	if(button1() == 1) {
58: 		mdelay(20);
59: 		if(button1() == 1) {
60: 			systick_ms_button = millis();
61: 			while(button1() == 1){
62: 				if(millis() - systick_ms_button >= 1000){
63: 					parse_group_cmd((u8 *)"$DGT:3-7,1!");  //qianzhua
64: 					beep_on_times(1, 500);
```

## z_sensor.c | button_jiaqu | 原文件第65-83行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
65: 				}		
66: 			}
67: 			if(millis() - systick_ms_button <= 500){
68: 				mode = mode + 1;
69: 				beep_on_times(mode, 100);
70: 				if (mode > 3){
71: 					mode = 0;	
72: 				}
73: 			}			
74: 		}
75: 	}
76: 	
77: 	if(button2() == 1) {
78: 		mdelay(20);
79: 		if(button2() == 1) {			
80: 			while(button2() == 1);
81: 			if(mode == 0){
82: 				parse_group_cmd((u8 *)"$DGT:18-21,1!");
83: 				beep_on_times(1, 100);
```

## z_sensor.c | button_jiaqu | 原文件第84-93行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
84: 			} else if (mode == 1) {
85: 				parse_group_cmd((u8 *)"$DGT:22-26,1!");
86: 				beep_on_times(1, 100);
87: 			}else if (mode == 2) {
88: 				parse_group_cmd((u8 *)"$DGT:27-31,1!");
89: 				beep_on_times(1, 100);	
90: 			}	
91: 		}
92: 	}
93: }
```

## z_sensor.h | 文件开头/全局定义 | 原文件第1-18行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-按键夹取.zip!/Jibot1-32出厂程序-按键夹取/USER/z_sensor.h
以下为原始源码，不是截图OCR。
```
1: #ifndef __SENSOR_H__
2: #define __SENSOR_H__
3: 
4: #include "stm32f10x_conf.h"
5: 
6: #define button1() GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_2)
7: #define button2() GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_3)
8: 
9: 
10: //处理智能传感器功能
11: void setup_sensor(void);
12: 
13: void loop_sensor(void);
14: 
15: void button_jiaqu(void);			//按键夹取
16: 
17: 
18: #endif
```
