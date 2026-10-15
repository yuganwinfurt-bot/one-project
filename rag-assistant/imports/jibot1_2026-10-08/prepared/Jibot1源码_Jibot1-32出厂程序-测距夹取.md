## z_delay.h | 文件开头/全局定义 | 原文件第1-19行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_delay.h
以下为原始源码，不是截图OCR。
```
1: #ifndef __TB_DELAY_H__
2: #define __TB_DELAY_H__
3: 
4: #include "z_type.h"
5: 
6: #define mdelay(x) tb_delay_ms(x)
7: #define udelay(x) tb_delay_us(x)
8: 
9: void tb_delay_init(void);
10: void tb_delay(u16 t);
11: void tb_delay_ns(u16 t);
12: void tb_delay_us(u16 t);
13: void tb_delay_ms(u16 t);
14: 
15: 
16: 
17: 
18: #endif
19: 
```

## z_oled.c | 文件开头/全局定义 | 原文件第1-11行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
1: /****************************************************************************
2: 	*	@笔者	：	W
3: 	*	@日期	：	2019年12月03日
4: 	*	@所属	：	杭州众灵科技
5: 	*	@论坛	：	www.ZL-robot.com
6: 	*	@功能	：	存放OLED相关的函数
7: 	*	@函数列表：
8: 	*	1.	void I2C_Start() -- 开启I2C总线
9: 	*	2.	void I2C_Stop() -- 关闭I2C总线
10: 	*	3.	void I2C_WriteByte(unsigned char I2C_Byte) -- 通过I2C总线写一个byte的数据
11: 	*	4.	void OLED_Write_Dat(unsigned char I2C_Data) -- 向OLED屏写数据
```

## z_oled.c | 文件开头/全局定义 | 原文件第12-18行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
12: 	*	5.	void OLED_Write_Cmd(unsigned char I2C_Command) -- 向OLED屏写命令
13: 	*	6.	void OLED_ON(void) -- OLED开启
14: 	*	7.	void OLED_OFF(void) -- OLED关闭
15: 	*	8.	void OLED_Set_Pos(unsigned char x, unsigned char y) -- 设置显示坐标
16: 	*	9.	void OLED_Fill(unsigned char fill_Data) -- 全屏显示(显示BMP图片时才会用到此功能)
17: 	*	10.	void OLED_CLS(void) -- 复位/清屏
18: 	*	11.	void OLED_Init(void) -- OLED屏初始化程序，此函数应在操作屏幕之前最先调用
```

## z_oled.c | 文件开头/全局定义 | 原文件第19-22行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
19: 	*	12.	void OLED_P6x8Str(unsigned char x, y,unsigned char ch[]) -- 6x8点整，用于显示ASCII码的最小阵列，不太清晰
20: 	*	13.	void OLED_P8x16Str(unsigned char x, y,unsigned char ch[]) -- 8x16点整，用于显示ASCII码，非常清晰
21: 	*	14.	void OLED_ShowStr(unsigned char x, unsigned char y, unsigned char ch[], unsigned char TextSize) -- 用于显示ASCII码，非常清晰
22: 	*	15.	void OLED_P16x16Ch(unsigned char x, y, N) -- 16x16点整，用于显示汉字的最小阵列，可设置各种字体、加粗、倾斜、下划线等
```

## z_oled.c | 文件开头/全局定义 | 原文件第23-34行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
23: 	*	16.	void OLED_DrawBMP(unsigned char x0, y0,x1, y1,unsigned char BMP[]) -- 将128x64像素的BMP位图在取字软件中算出字表，然后复制到codetab中，此函数调用即可
24: 	*	17.	void OLED_TEST(void) -- OLED测试程序
25:  *****************************************************************************/
26: 
27: #include "z_oled.h"
28: #include "z_codetab.h"
29: 
30: /***********************************************
31: 	函数名称：I2C_Start() 
32: 	功能介绍：I2C启动
33: 	函数参数：无
34: 	返回值：	无
```

## z_oled.c | 文件开头/全局定义 | 原文件第35-35行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
35:  ***********************************************/
```

## z_oled.c | I2C_Start | 原文件第36-48行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
36: void I2C_Start(void) {
37:    SCL(1);
38:    SDA(1);
39:    SDA(0);
40:    SCL(0);
41: }
42: 
43: /***********************************************
44: 	函数名称：I2C_Stop() 
45: 	功能介绍：I2C停止
46: 	函数参数：无
47: 	返回值：	无
48:  ***********************************************/
```

## z_oled.c | I2C_Stop | 原文件第49-61行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
49: void I2C_Stop(void) {
50:    SCL(0);
51:    SDA(0);
52:    SCL(1);
53:    SDA(1);
54: }
55: 
56: /***********************************************
57: 	函数名称：I2C_WriteByte(I2C_Byte) 
58: 	功能介绍：I2C写一个字节
59: 	函数参数：I2C_Byte 写入的字节
60: 	返回值：	无
61:  ***********************************************/
```

## z_oled.c | I2C_WriteByte | 原文件第62-83行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
62: void I2C_WriteByte(unsigned char I2C_Byte) {
63: 	unsigned char i;
64: 	for(i=0;i<8;i++) {
65: 		if(I2C_Byte & 0x80)
66: 			SDA(1);
67: 		else
68: 			SDA(0);
69: 		udelay(2);
70: 		SCL(1);
71: 		udelay(2);
72: 		SCL(0);
73: 		udelay(2);
74: 		I2C_Byte<<=1;
75: 	}
76: 	SDA(1);
77: 	SCL(1);
78: 	SCL(0);
79: }
80: 
81: /***********************************************
82: 	函数名称：OLED_Write_Dat(I2C_Data) 
83: 	功能介绍：OLED写一个数据字节
```

## z_oled.c | I2C_WriteByte | 原文件第84-86行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
84: 	函数参数：I2C_Data 写入的数据字节
85: 	返回值：	无
86:  ***********************************************/
```

## z_oled.c | OLED_Write_Dat | 原文件第87-100行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
87: void OLED_Write_Dat(unsigned char I2C_Data) {
88: 	I2C_Start();
89: 	I2C_WriteByte(0x78);
90: 	I2C_WriteByte(0x40);
91: 	I2C_WriteByte(I2C_Data);
92: 	I2C_Stop();
93: }
94: 
95: /***********************************************
96: 	函数名称：OLED_Write_Cmd(I2C_Command) 
97: 	功能介绍：OLED写一个命令字节
98: 	函数参数：I2C_Command 写入的命令字节
99: 	返回值：	无
100:  ***********************************************/
```

## z_oled.c | OLED_Write_Cmd | 原文件第101-114行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
101: void OLED_Write_Cmd(unsigned char I2C_Command) {
102: 	I2C_Start();
103: 	I2C_WriteByte(0x78);
104: 	I2C_WriteByte(0x00);
105: 	I2C_WriteByte(I2C_Command);
106: 	I2C_Stop();
107: }
108: 
109: /***********************************************
110: 	函数名称：OLED_ON() 
111: 	功能介绍：OLED开启
112: 	函数参数：无
113: 	返回值：	无
114:  ***********************************************/
```

## z_oled.c | OLED_ON | 原文件第115-127行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
115: void OLED_ON(void)
116: {
117: 	OLED_Write_Cmd(0X8D);
118: 	OLED_Write_Cmd(0X14);
119: 	OLED_Write_Cmd(0XAF);
120: }
121: 
122: /***********************************************
123: 	函数名称：OLED_OFF() 
124: 	功能介绍：OLED关闭
125: 	函数参数：无
126: 	返回值：	无
127:  ***********************************************/
```

## z_oled.c | OLED_OFF | 原文件第128-140行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
128: void OLED_OFF(void)
129: {
130: 	OLED_Write_Cmd(0X8D);
131: 	OLED_Write_Cmd(0X10);
132: 	OLED_Write_Cmd(0XAE);
133: }
134: 
135: /***********************************************
136: 	函数名称：OLED_Set_Pos(x,y) 
137: 	功能介绍：设置OLED写入坐标
138: 	函数参数：x 横坐标 y 纵坐标
139: 	返回值：	无
140:  ***********************************************/
```

## z_oled.c | OLED_Set_Pos | 原文件第141-152行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
141: void OLED_Set_Pos(unsigned char x, unsigned char y) { 
142: 	OLED_Write_Cmd(0xb0+y);
143: 	OLED_Write_Cmd(((x&0xf0)>>4)|0x10);
144: 	OLED_Write_Cmd((x&0x0f)|0x01);
145: } 
146: 
147: /***********************************************
148: 	函数名称：OLED_Fill(fill_Data) 
149: 	功能介绍：OLED全屏显示
150: 	函数参数：fill_Data 全屏指令
151: 	返回值：	无
152:  ***********************************************/
```

## z_oled.c | OLED_Fill | 原文件第153-168行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
153: void OLED_Fill(unsigned char fill_Data) {
154: 	unsigned char y,x;
155: 	for(y=0;y<8;y++) {
156: 		OLED_Write_Cmd(0xb0+y);
157: 		OLED_Write_Cmd(0x01);
158: 		OLED_Write_Cmd(0x10);
159: 		for(x=0;x<X_WIDTH;x++)
160: 			OLED_Write_Dat(fill_Data);
161: 	}
162: }
163: 
164: /***********************************************
165: 	函数名称：OLED_CLS() 
166: 	功能介绍：OLED复位 全屏清除
167: 	函数参数：无
168: 	返回值：	无
```

## z_oled.c | OLED_Fill | 原文件第169-169行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
169:  ***********************************************/
```

## z_oled.c | OLED_CLS | 原文件第170-179行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
170: void OLED_CLS(void) {
171: 	OLED_Fill(0x00);
172: }
173: 
174: /***********************************************
175: 	函数名称：OLED_Init() 
176: 	功能介绍：OLED初始化
177: 	函数参数：无
178: 	返回值：	无
179:  ***********************************************/
```

## z_oled.c | OLED_Init | 原文件第180-190行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
180: void OLED_Init(void) {
181: 	GPIO_InitTypeDef  GPIO_InitStructure; 
182: 
183: 	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA,ENABLE);
184: 
185: 	GPIO_InitStructure.GPIO_Pin =  GPIO_Pin_5 | GPIO_Pin_7;
186: 	GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
187: 	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_OD;
188: 	GPIO_Init(GPIOA, &GPIO_InitStructure);
189: 	
190: 	mdelay(500);							//初始化之前的延时很重要！
```

## z_oled.c | OLED_Init | 原文件第191-198行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
191: 	OLED_Write_Cmd(0xae);				//关闭oled面板
192: 	OLED_Write_Cmd(0x00);				//设置低列地址
193: 	OLED_Write_Cmd(0x10);				//设置高列地址
194: 	OLED_Write_Cmd(0x40);				//设置起始行地址  设置映射RAM显示起始行(0x00~0x3F)
195: 	OLED_Write_Cmd(0x81);				//设置对比度控制寄存器
196: 	OLED_Write_Cmd(Brightness); //设置SEG输出电流亮度
197: 	OLED_Write_Cmd(0xa1);				//设置SEG/列映射     0xa0左右反置 0xa1正常
198: 	OLED_Write_Cmd(0xc8);				//设置COM/行扫描方向   0xc0上下反置 0xc8正常
```

## z_oled.c | OLED_Init | 原文件第199-207行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
199: 	OLED_Write_Cmd(0xa6);				//设置正常显示
200: 	OLED_Write_Cmd(0xa8);				//设置多路复用比(1~64)
201: 	OLED_Write_Cmd(0x3f);				//1/64 duty
202: 	OLED_Write_Cmd(0xd3);				//设置显示偏移位移映射RAM计数器(0x00~0x3F)
203: 	OLED_Write_Cmd(0x00);				//不偏移
204: 	OLED_Write_Cmd(0xd5);				//设置显示时钟分频比/振荡频率
205: 	OLED_Write_Cmd(0x80);				//设置分频比，设置时钟为100帧/秒
206: 	OLED_Write_Cmd(0xd9);				//设置预充电周期
207: 	OLED_Write_Cmd(0xf1);				//设定预充电为15个时钟，放电为1个时钟
```

## z_oled.c | OLED_Init | 原文件第208-217行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
208: 	OLED_Write_Cmd(0xda);				//设置com引脚硬件配置
209: 	OLED_Write_Cmd(0x12);
210: 	OLED_Write_Cmd(0xdb);				//设置VCOM高
211: 	OLED_Write_Cmd(0x40);				//设置VCOM取消选择电平
212: 	OLED_Write_Cmd(0x20);				//设置页面寻址模式(0x00/0x01/0x02)
213: 	OLED_Write_Cmd(0x02);
214: 	OLED_Write_Cmd(0x8d);				//设置充电泵启用/禁用
215: 	OLED_Write_Cmd(0x14);				//设置(0x10)禁用
216: 	OLED_Write_Cmd(0xa4);				//禁用整个显示(0xa4/0xa5)
217: 	OLED_Write_Cmd(0xa6);				//禁用反向显示(0xa6/0xa7) 
```

## z_oled.c | OLED_Init | 原文件第218-230行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
218: 	OLED_Write_Cmd(0xaf);				//打开oled面板
219: 	OLED_Fill(0x00); 						//初始清屏
220: 	OLED_Set_Pos(0,0);
221: 	
222: 	OLED_CLS();
223: }
224: 
225: /***********************************************
226: 	函数名称：OLED_P6x8Str(x,y,ch[]) 
227: 	功能介绍：显示6*8一组标准ASCII字符串
228: 	函数参数：x 起始点横坐标(0~127) y 起始点纵坐标(0~7) ch[] 要显示的字符串
229: 	返回值：	无
230:  ***********************************************/
```

## z_oled.c | OLED_P6x8Str | 原文件第231-248行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
231: void OLED_P6x8Str(unsigned char x,unsigned char y,unsigned char ch[]) {
232: 	unsigned char c=0,i=0,j=0;
233: 	while (ch[j]!='\0') {
234: 		c =ch[j]-32;
235: 		if(x>126) {
236: 			x=0;
237: 			y++;
238: 		}
239: 		OLED_Set_Pos(x,y);
240: 		for(i=0;i<6;i++)
241: 			OLED_Write_Dat(F6x8[c][i]);
242: 		x+=6;
243: 		j++;
244: 	}
245: }
246: 
247: /***********************************************
248: 	函数名称：OLED_P8x16Str(x,y,ch[]) 
```

## z_oled.c | OLED_P6x8Str | 原文件第249-252行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
249: 	功能介绍：显示8*16一组标准ASCII字符串
250: 	函数参数：x 起始点横坐标(0~127) y 起始点纵坐标(0~7) ch[] 要显示的字符串
251: 	返回值：	无
252:  ***********************************************/
```

## z_oled.c | OLED_P8x16Str | 原文件第253-270行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
253: void OLED_P8x16Str(unsigned char x,unsigned char y,unsigned char ch[]) {
254: 	unsigned char c=0,i=0,j=0;
255: 	while (ch[j]!='\0') {
256: 		c =ch[j]-32;
257: 		if(x>120) {
258: 			x=0;
259: 			y++;
260: 		}
261: 		OLED_Set_Pos(x,y);
262: 		for(i=0;i<8;i++)
263: 			OLED_Write_Dat(F8X16[c*16+i]);
264: 		OLED_Set_Pos(x,y+1);
265: 		for(i=0;i<8;i++)
266: 			OLED_Write_Dat(F8X16[c*16+i+8]);
267: 		x+=8;
268: 		j++;
269: 	}
270: }
```

## z_oled.c | OLED_P8x16Str | 原文件第271-277行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
271: 
272: /***********************************************
273: 	函数名称：OLED_ShowStr(x,y,ch[],TextSize) 
274: 	功能介绍：显示codetab.h中的ASCII字符
275: 	函数参数：x 起始点横坐标(0~127) y 起始点纵坐标(0~7) ch[] 要显示的字符串 TextSize 字符大小(1:6*8 ; 2:8*16)
276: 	返回值：	无
277:  ***********************************************/
```

## z_oled.c | OLED_ShowStr | 原文件第278-293行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
278: void OLED_ShowStr(unsigned char x, unsigned char y, unsigned char ch[], unsigned char TextSize) {
279: 	unsigned char c = 0,i = 0,j = 0;
280: 	switch(TextSize) {
281: 		case 1: {
282: 			while (ch[j]!='\0') {
283: 				c =ch[j]-32;
284: 				if(x>126) {
285: 					x=0;
286: 					y++;
287: 				}
288: 				OLED_Set_Pos(x,y);
289: 				for(i=0;i<6;i++)
290: 					OLED_Write_Dat(F6x8[c][i]);
291: 				x+=6;
292: 				j++;
293: 			}
```

## z_oled.c | OLED_ShowStr | 原文件第294-314行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
294: 		}	break;
295: 		case 2: {
296: 			while (ch[j]!='\0') {
297: 				c =ch[j]-32;
298: 				if(x>120) {
299: 					x=0;
300: 					y++;
301: 				}
302: 				OLED_Set_Pos(x,y);
303: 				for(i=0;i<8;i++)
304: 					OLED_Write_Dat(F8X16[c*16+i]);
305: 				OLED_Set_Pos(x,y+1);
306: 				for(i=0;i<8;i++)
307: 					OLED_Write_Dat(F8X16[c*16+i+8]);
308: 				x+=8;
309: 				j++;
310: 			}
311: 		}	break;
312: 	}
313: }
314: 
```

## z_oled.c | OLED_ShowStr | 原文件第315-320行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
315: /***********************************************
316: 	函数名称：OLED_P16x16Ch(x,y,N) 
317: 	功能介绍：显示16*16点阵
318: 	函数参数：x 起始点横坐标(0~127) y 起始点纵坐标(0~7) N 显示个数
319: 	返回值：	无
320:  ***********************************************/
```

## z_oled.c | OLED_P16x16Ch | 原文件第321-336行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
321: void OLED_P16x16Ch(unsigned char x,unsigned char y,unsigned char N) {
322: 	unsigned char wm=0;
323: 	unsigned int adder=32*N;
324: 	OLED_Set_Pos(x , y);
325: 	for(wm = 0;wm < 16;wm++) {
326: 		OLED_Write_Dat(F16x16[adder]);
327: 		
328: 		adder += 1;
329: 	}
330: 	OLED_Set_Pos(x,y + 1);
331: 	for(wm = 0;wm < 16;wm++) {
332: 		OLED_Write_Dat(F16x16[adder]);
333: 		adder += 1;
334: 	} 	  	
335: }
336: 
```

## z_oled.c | OLED_P16x16Ch | 原文件第337-342行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
337: /***********************************************
338: 	函数名称：OLED_DrawBMP(x0,y0,x1,y1,BMP[]) 
339: 	功能介绍：显示显示BMP图片128×64
340: 	函数参数：x 起始点横坐标(0~127) y 起始点纵坐标(0~7) BMP[] 要显示的图片
341: 	返回值：	无
342:  ***********************************************/
```

## z_oled.c | OLED_DrawBMP | 原文件第343-357行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
343: void OLED_DrawBMP(unsigned char x0,unsigned char y0,unsigned char x1,unsigned char y1,unsigned char BMP[]) {
344: 	unsigned int j=0;
345: 	unsigned char x,y;
346: 
347:   if(y1%8==0) y=y1/8;      
348:   else y=y1/8+1;
349: 	for(y=y0;y<y1;y++) {
350: 		OLED_Set_Pos(x0,y);
351:     for(x=x0;x<x1;x++) {      
352: 			OLED_Write_Dat(BMP[j++]);
353: 		}
354: 	}
355: }
356: 
357: /***********************************************
```

## z_oled.c | OLED_DrawBMP | 原文件第358-362行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
358: 	函数名称：OLED_TEST() 
359: 	功能介绍：OLED测试程序
360: 	函数参数：无
361: 	返回值：	无
362:  ***********************************************/
```

## z_oled.c | OLED_TEST | 原文件第363-381行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
363: void OLED_TEST(void) {
364: 	static u8 i;
365: 
366: 	OLED_Fill(0xFF);
367: 	mdelay(3000);
368: 	
369: 	OLED_Fill(0);
370: 	mdelay(3000);
371: 
372: 	for(i=0;i<4;i++) {
373: 		OLED_P16x16Ch(i*16,2,i);
374: 	}
375: 	mdelay(3000);
376: 	
377: 	OLED_CLS();
378: 	OLED_P8x16Str(0,0,"ZLTech 2019");
379: 	OLED_P8x16Str(0,2,"ZLTech 2019");
380: 	OLED_ShowStr(0,4,"ZLTech 2019",2);
381: 	OLED_ShowStr(0,6,"ZLTech 2019",1);
```

## z_oled.c | OLED_TEST | 原文件第382-388行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.c
以下为原始源码，不是截图OCR。
```
382: 	OLED_P6x8Str (0,7,"ZLTech 2019");
383: 	mdelay(3000);
384: 	
385: 	OLED_CLS();
386: 	//OLED_DrawBMP(0,0,128,8,BMP1);
387: 	mdelay(3000);
388: }
```

## z_oled.h | 文件开头/全局定义 | 原文件第1-14行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.h
以下为原始源码，不是截图OCR。
```
1: /****************************************************************************
2: 	*	@笔者	：	W
3: 	*	@日期	：	2019年12月03日
4: 	*	@所属	：	杭州众灵科技
5: 	*	@论坛	：	www.ZL-robot.com
6:  ****************************************************************************/
7: 
8: #ifndef __OLED_H__
9: #define __OLED_H__
10: 
11: #include "stm32f10x.h"
12: #include "z_delay.h"
13: 
14: /*******传感器快捷指令表*******/
```

## z_oled.h | 文件开头/全局定义 | 原文件第15-27行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.h
以下为原始源码，不是截图OCR。
```
15: #define SCL(x) GPIO_WriteBit(GPIOA, GPIO_Pin_7, (BitAction)x)
16: #define SDA(x) GPIO_WriteBit(GPIOA, GPIO_Pin_5, (BitAction)x)
17: 
18: /*******OLED配置命令宏定义*******/
19: #define	Brightness	0xCF 
20: #define X_WIDTH 	128
21: #define Y_WIDTH 	64
22: 
23: /*******OLED相关函数声明*******/
24: void OLED_Write_Dat(unsigned char I2C_Data);
25: void OLED_Write_Cmd(unsigned char I2C_Command);
26: void OLED_ON(void);
27: void OLED_OFF(void);
```

## z_oled.h | 文件开头/全局定义 | 原文件第28-34行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.h
以下为原始源码，不是截图OCR。
```
28: void OLED_Set_Pos(unsigned char x, unsigned char y);
29: void OLED_Fill(unsigned char fill_Data);
30: void OLED_CLS(void);
31: void OLED_Init(void);
32: void OLED_P6x8Str(unsigned char x,unsigned char y,unsigned char ch[]);
33: void OLED_P8x16Str(unsigned char x,unsigned char y,unsigned char ch[]);
34: void OLED_P16x16Ch(unsigned char x,unsigned char y,unsigned char N);
```

## z_oled.h | 文件开头/全局定义 | 原文件第35-39行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/src/z_oled.h
以下为原始源码，不是截图OCR。
```
35: void OLED_ShowStr(unsigned char x, unsigned char y, unsigned char ch[], unsigned char TextSize);
36: void OLED_DrawBMP(unsigned char x0,unsigned char y0,unsigned char x1,unsigned char y1,unsigned char BMP[]);
37: void OLED_TEST(void);
38: 
39: #endif
```

## z_sensor.c | 文件开头/全局定义 | 原文件第1-13行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/USER/z_sensor.c
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
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
14: #include "z_kinematics.h"	//逆运动学算法
15: #include "stm32f10x_iwdg.h"
16: #include "z_oled.h"
17: #include "z_sensor.h"
18: #include "z_actiongroupcontrol.h"
19: 
20: u16 kms_y = 0;
21: u8 get_count = 0;
22: u8 carry_step = 0;
23: /*
24: 	智能功能代码
25: 	
26: 	IO口分布
27: 	超声波传感器 S3  TRIG - PB0 - 白线  Echo - PA2 - 绿线
28: 	
29: 	oled显示屏 S6  PA1 -绿线
30: 		
31: */
32: 
33: 
34: //初始化传感器IO口
```

## z_sensor.c | setup_sensor | 原文件第35-39行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
35: void setup_sensor(void) {
36: 	setup_oled();
37: 	setup_csb();
38: }
39: 
```

## z_sensor.c | setup_csb | 原文件第40-49行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
40: void setup_csb(void){
41: 	GPIO_InitTypeDef GPIO_InitStructure;
42: 	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOB | RCC_APB2Periph_GPIOA, ENABLE);  
43: 	
44: 	//初始化超声波IO口 Trig PB0  Echo PA2
45: 	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0;  
46: 	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;  
47: 	GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;	
48: 	GPIO_Init(GPIOB, &GPIO_InitStructure); 	
49: 	
```

## z_sensor.c | setup_csb | 原文件第50-58行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
50: 	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_2;   
51: 	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;  
52: 	GPIO_Init(GPIOA, &GPIO_InitStructure); 	
53: 	
54: 	//初始化超声波定时器
55: 	TIM3_Int_Init(30000, 71);
56: }
57: 
58: 
```

## z_sensor.c | setup_oled | 原文件第59-75行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
59: void setup_oled(void){
60: 	u8 i;
61: 	OLED_Init();
62: 	OLED_Fill(0xFF);
63: 	mdelay(3000);
64: 	
65: 	OLED_Fill(0);
66: 	mdelay(3000);
67: 
68: 	for(i=0;i<4;i++) {
69: 		OLED_P16x16Ch(i*16,2,i);
70: 	}
71: 	mdelay(3000);
72: 	OLED_CLS();
73: }
74: 
75: 
```

## z_sensor.c | loop_sensor | 原文件第76-92行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
76: void loop_sensor(void) {
77: 	ceju_jiaqu();
78: }
79: 
80: void csb_Delay_Us(uint16_t time)  //延时函数
81: { 
82: 	uint16_t i,j;
83: 	for(i=0;i<time;i++)
84:   		for(j=0;j<9;j++);
85: }
86: 
87: /*************************************************************
88: 函数名称：get_csb_value()
89: 功能介绍：采集超声波数据
90: 函数参数：无
91: 返回值：  采集的数据  
92: *************************************************************/
```

## z_sensor.c | get_csb_value | 原文件第93-106行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
93: int get_csb_value(void) {
94: 	u16 csb_t;
95: 	long timeout= 0;
96: 	Trig(1);
97: 	csb_Delay_Us(30);
98: 	Trig(0);
99: 	timeout= 0;
100: 	while(Echo() == 0&&(timeout++<10000)) //等待接收口高电平输出
101: 	if(timeout>=500000)return 0;
102: 	TIM_SetCounter(TIM3,0);//清除计数
103: 	TIM_Cmd(TIM3, ENABLE);  //使能TIMx外设
104: 	while(Echo() == 1&&(timeout++<10000))
105: 	if(timeout>=500000)return 0;
106: 	TIM_Cmd(TIM3, DISABLE);  //使能TIMx外设      
```

## z_sensor.c | get_csb_value | 原文件第107-120行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
107: 	csb_t = TIM_GetCounter(TIM3);//获取时间,分辨率为1US
108: 	//340m/s = 0.017cm/us
109: 	if(csb_t < 25000) {
110: 		//sprintf((char *)cmd_return, "csb_time=%d\r\n", (int)(csb_t*0.17));
111: 		//uart1_send_str(cmd_return);
112: 		csb_t = csb_t*0.017;
113: 		return csb_t;
114: 	}
115: 	return 0;
116: }
117: /*************************************************************
118: 函数名称：get_adc_csb_middle()
119: 功能介绍：处理超声波采集到的数据，取采集到的中间值
120: 函数参数：无
```

## z_sensor.c | get_csb_value | 原文件第121-122行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
121: 返回值：  处理后的超声波数据  
122: *************************************************************/
```

## z_sensor.c | get_adc_csb_middle | 原文件第123-134行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
123: int get_adc_csb_middle() {
124: 	u8 i;
125: 	static int ad_value[5] = {0}, myvalue;// ad_value_bak[5] = {0}, 
126: 	for(i=0;i<5;i++)ad_value[i] = get_csb_value();
127: 	selection_sort(ad_value, 5);
128: 	myvalue = ad_value[2];
129: // 	for(i=0;i<5;i++)ad_value[i] = ad_value_bak[i];
130: 	return myvalue;  
131: }
132: 
133: /*************************************************************
134: 函数名称：ceju_jiaqu()
```

## z_sensor.c | get_adc_csb_middle | 原文件第135-138行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
135: 功能介绍：超声波检测距离，换算成逆运动学坐标，执行测距夹取动作
136: 函数参数：无
137: 返回值：  无  
138: *************************************************************/
```

## z_sensor.c | ceju_jiaqu | 原文件第139-151行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
139: void ceju_jiaqu(void) {
140: 	static int dis_cur;
141: 	static int dis = 100;		
142: 	static u32 systick_ms_ceju = 0;
143: 	
144: 	if(group_do_ok == 0)return;//有动作执行，直接返回	
145: 	if(millis() - systick_ms_ceju >= 50 && carry_step == 0){
146: 		dis = get_adc_csb_middle();
147: 		
148: 		if(5 < dis < 20){
149: 			dis_cur = get_adc_csb_middle();
150: 			//偏差小于2，增加get_count的值
151: 			if(dis_cur - dis < 2 || dis - dis_cur < 2){
```

## z_sensor.c | ceju_jiaqu | 原文件第152-169行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
152: 				get_count++;			
153: 			}
154: 			else{
155: 				get_count = 0;
156: 			}		
157: 		}
158: 		else{
159: 			get_count = 0;
160: 		}
161: 	}
162: 	//oled显示
163: 	OLED_P8x16Str(0,0,"ZLTech 2022");
164: 	OLED_P8x16Str(0,2,"Jibot-ONE");
165: 	sprintf((char*)cmd_return, "dis=%d",dis);
166: 	OLED_P8x16Str(0,4,cmd_return);
167: 	
168: 	if(get_count > 20){
169: 		kms_y = dis*10 + 120;
```

## z_sensor.c | ceju_jiaqu | 原文件第170-176行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
170: 		sprintf((char*)cmd_return, "dis=%d,kms_y=%d  ",dis,kms_y);
171: 		//uart1_send_str(cmd_return);
172: 		OLED_P8x16Str(0,4,cmd_return);
173: 		carry_wood();							
174: 	}						
175: }
176: 
```

## z_sensor.c | carry_wood | 原文件第177-194行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
177: void carry_wood(void){	
178: 	//张开爪子
179: 	if(carry_step == 0){
180: 		set_servo(5,1200,500);		
181: 		mdelay(500);
182: 		carry_step = 1;
183: 	//运行到目标位置
184: 	}else if(carry_step == 1){
185: 		if(kinematics_move(0,kms_y,15,1500)){
186: 			beep_on_times(1,100);
187: 			mdelay(2000);	
188: 			carry_step = 2;							
189: 		}else{
190: 			carry_step = 0;
191: 			return;
192: 		}		
193: 	//夹取
194: 	}else if(carry_step == 2){
```

## z_sensor.c | carry_wood | 原文件第195-206行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
195: 		set_servo(5,1700,500);		
196: 		mdelay(500);
197: 		carry_step = 3;
198: 	//抬起
199: 	}else if(carry_step == 3){
200: 		//parse_action("#001P2200T2000!#002P2150T2000!#003P0850T2000!");
201: 		zx_uart_send_str((u8*)"#001P2200T2000!#002P2150T2000!#003P0850T2000!");	
202: 		mdelay(2000);
203: 		carry_step = 4;
204: 	}else if(carry_step == 4){
205: 		parse_group_cmd((u8 *)"$DGT:22-26,1!");  //执行脱机动作组左放
206: 		carry_step = 5;
```

## z_sensor.c | carry_wood | 原文件第207-214行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/USER/z_sensor.c
以下为原始源码，不是截图OCR。
```
207: 	}else if(carry_step == 5){
208: 		if(group_do_ok == 1){
209: 			carry_step = 0;
210: 			get_count = 0;
211: 			OLED_CLS();
212: 		}
213: 	}
214: }
```

## z_sensor.h | 文件开头/全局定义 | 原文件第1-19行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/USER/z_sensor.h
以下为原始源码，不是截图OCR。
```
1: #ifndef __SENSOR_H__
2: #define __SENSOR_H__
3: 
4: #include "stm32f10x_conf.h"
5: 
6: #define Trig(x) gpioB_pin_set(0, x);
7: #define Echo() GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_2)
8: 
9: 
10: //处理智能传感器功能
11: void setup_sensor(void);
12: void setup_oled(void);
13: void setup_csb(void);
14: 
15: void loop_sensor(void);
16: 
17: void ceju_jiaqu(void);
18: void carry_wood(void);
19: int get_csb_value(void);
```

## z_sensor.h | 文件开头/全局定义 | 原文件第20-22行
来源：003-源码例程\03-传感器例程源码\Jibot1-32出厂程序-测距夹取.zip!/Jibot1-32出厂程序-测距夹取/USER/z_sensor.h
以下为原始源码，不是截图OCR。
```
20: int get_adc_csb_middle();   
21: 
22: #endif
```
