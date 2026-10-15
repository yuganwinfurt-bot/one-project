## ZGloveR_J1.ino | 文件开头/全局定义 | 原文件第1-17行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
1: /*
2:     硬件IO分布：
3:     1、x轴 y轴 I2C芯片
4:     2、电位器 A6 A7 A0 A2 A3
5:     3、舵机引脚 11 10 9 8 7 6
6:     4、led引脚13 蜂鸣器引脚 5 校准按键 3 模式按键 4
7: 
8:     功能：
9:     一、
10:         校准按键：记录手指在闭合和张开状态下的手指旋钮值和陀螺仪值
11:         模式按键：控制仿生手掌类产品使用，此处暂无功能
12:     二、
13:         手指闭合，手掌平行状态下超过3秒，机械臂弯曲，进入地盘移动控制模式
14:         手指伸展，手掌伸展保持平行状态超过3秒，机械臂直立，进入机械臂控制模式       
15:     三、 
16:         机械臂控制（默认模式）
17:             手掌-张开-闭合，控制爪子
```

## ZGloveR_J1.ino | 文件开头/全局定义 | 原文件第18-31行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
18:             直接发送#！控制机械臂（默认模式），通过模式按键切换机械臂控制方式
19:             手掌控制机械臂，发送逆运动学控制指令，控制机械臂移动
20:                       
21:         握拳状态下：
22:             手掌前后左右倾斜控制车体前后左右移动，倾斜程度控制车体移动速度   
23: */
24: 
25: #include <Wire.h>
26: #include <I2Cdev.h>
27: #include <ADXL345.h>
28: #include <EEPROM.h>           //调用<EEPROM.h库
29: 
30: #define DWQ_NUM     5               //宏定义电位器数量
31: #define PIN_beep    5               //宏定义蜂鸣器引脚
```

## ZGloveR_J1.ino | 文件开头/全局定义 | 原文件第32-41行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
32: #define PIN_nled    13              //宏定义工作指示灯引脚
33: #define PIN_KEY_J   3               //宏定义校准引脚
34: #define PIN_KEY_M   4               //宏定义模式引脚
35: 
36: #define ADC_MIN_ADDR   0            //握紧时采集电位器值起始地址
37: #define ADC_MAX_ADDR   20           //张手时采集电位器值起始地址
38: #define POS_X_ADDR     30           //X的存储地址
39: #define POS_Y_ADDR     34           //Y的存储地址
40: 
41: 
```

## ZGloveR_J1.ino | 文件开头/全局定义 | 原文件第42-52行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
42: #define INT_DATA_TYPE  2     //数据类型,数据类型=几个字节就是几，相当于数据拆分成字节
43: #define JXB_PWM_RANGE  1000.0 //量程
44: #define JXB_PWM_STRAT  (500+(2000-JXB_PWM_RANGE)/2)     //机械臂PWM起始值
45: #define X_MIDDLE 0
46: #define Y_MIDDLE 0
47: 
48: #define beep_on() digitalWrite(PIN_beep, HIGH);
49: #define beep_off() digitalWrite(PIN_beep, LOW);
50: 
51: #define nled_on() digitalWrite(PIN_nled, LOW);
52: #define nled_off() digitalWrite(PIN_nled, HIGH);
```

## ZGloveR_J1.ino | 文件开头/全局定义 | 原文件第53-59行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
53: 
54: char cmd_return[100], cmd_return_bak[100];
55: byte dwq_pin[DWQ_NUM] = {A6, A7, A0, A2, A3};       //定义电位器引脚数组
56: int  ADC_MAX[DWQ_NUM] = {0, 0, 0, 0, 0};            //默认握紧时采集电位器值
57: int  ADC_MIN[DWQ_NUM] = {0, 0, 0, 0, 0};            //默认张手时采集电位器值
58: int  ADC_MID[DWQ_NUM] = {0, 0, 0, 0, 0};            //默认握紧和张开之间的中间值
59: int  pos[DWQ_NUM] = {0}, pos_x=0, pos_y=0;          //变量pos用来存储转化后的电位器数据
```

## ZGloveR_J1.ino | 文件开头/全局定义 | 原文件第60-70行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
60: int  pos_bak[5] = {0}, pos_x_bak=0, pos_y_bak=0;    //变量pos备份值
61: int  pwm_value[DWQ_NUM] = {0};                      //变量pwm值
62: float pos_p[DWQ_NUM] = {1,1,1,1,1};                 //放大倍数
63: u8 control_mode = 0;                                //手套控制模式
64: u8 robot_mode = 0;
65: int pos_x_verify = 0, pos_y_verify = 0;             //x y校验值
66: 
67: 
68: ADXL345 myAdxl345;
69: int16_t ax, ay, az;
70: 
```

## ZGloveR_J1.ino | setup | 原文件第71-79行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
71: void setup(){
72:     Serial.begin(115200);                           //初始化波特率为115200
73:     pinMode(PIN_nled, OUTPUT);                      //设置LED引脚为输出模式
74:     pinMode(PIN_beep, OUTPUT);                      //设置蜂鸣器引脚为输出模式
75:     pinMode(PIN_KEY_M, INPUT_PULLUP);               //将模式按键对应引脚设置为内部上拉输入模式，防止误判
76:     pinMode(PIN_KEY_J, INPUT_PULLUP);               //将校准按键对应引脚设置为内部上拉输入模式，防止误判
77: 
78: 
79:     Wire.begin();
```

## ZGloveR_J1.ino | setup | 原文件第80-89行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
80:     myAdxl345.initialize();
81:     myAdxl345.testConnection();
82: 
83:     eepromRead(ADC_MIN_ADDR, sizeof(ADC_MIN), (u8 *)ADC_MIN);//读取存储电位器最小值
84:     eepromRead(ADC_MAX_ADDR, sizeof(ADC_MAX), (u8 *)ADC_MAX);//读取存储电位器最大值
85:     for(int i=0;i<DWQ_NUM;i++) {
86:         ADC_MID[i] = (ADC_MIN[i] + ADC_MAX[i])/2;
87:         pos_p[i] = JXB_PWM_RANGE/abs(ADC_MIN[i] - ADC_MAX[i]);//放大倍数
88:     }
89: 
```

## ZGloveR_J1.ino | setup | 原文件第90-97行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
90:     pos_x_verify = EEPROM.read(POS_X_ADDR)*256 + EEPROM.read(POS_X_ADDR+1)-1024;//读陀螺仪X的校准值
91:     pos_y_verify = EEPROM.read(POS_Y_ADDR)*256 + EEPROM.read(POS_Y_ADDR+1)-1024;//读陀螺仪Y的校准值
92: 
93: 
94:     //启动示意
95:     nled_on();beep_on();delay(100);nled_off();beep_off();delay(100);
96:     nled_on();beep_on();delay(100);nled_off();beep_off();delay(100);
97:     nled_on();beep_on();delay(100);nled_off();beep_off();delay(100);
```

## ZGloveR_J1.ino | setup | 原文件第98-108行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
98: 
99: #if 0
100:       sprintf(cmd_return,"ADC_MIN:%04d %04d %04d %04d %04d",
101:                           ADC_MIN[0], ADC_MIN[1], ADC_MIN[2], ADC_MIN[3], ADC_MIN[4]);
102:       Serial.println(cmd_return);  
103: 
104:       sprintf(cmd_return,"ADC_MAX:%04d %04d %04d %04d %04d",
105:                           ADC_MAX[0], ADC_MAX[1], ADC_MAX[2], ADC_MAX[3], ADC_MAX[4]);
106:       Serial.println(cmd_return);   
107: #endif
108: }
```

## ZGloveR_J1.ino | setup | 原文件第109-109行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
109: 
```

## ZGloveR_J1.ino | loop | 原文件第110-121行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
110: void loop(){ 
111:     loop_nled();        //led灯闪烁函数
112:     loop_key_j();       //校验函数
113:     loop_Gihand_R();        //旋钮控制
114: }
115: 
116: /*
117:     读写eeprom数据
118:     addr 地址
119:     len 数据长度
120:     mydat 数据buf
121: */
```

## ZGloveR_J1.ino | eepromRead | 原文件第122-133行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
122: void eepromRead(u32 addr, u8 len, u8 *mydat){
123:     for(u8 i = 0; i < len; i++) {//求取旋钮平均值，存储到EEPROM
124:         mydat[i] = EEPROM.read(addr+i);
125:     }        
126: }
127: 
128: /*
129:     读写eeprom数据
130:     addr 地址
131:     len 数据长度
132:     mydat 数据buf
133: */
```

## ZGloveR_J1.ino | eepromWrite | 原文件第134-140行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
134: void eepromWrite(u32 addr, u8 len, u8 *mydat){
135:     for(u8 i = 0; i < len; i++) {//求取旋钮平均值，存储到EEPROM
136:         EEPROM.write(addr+i, mydat[i]);
137:     }        
138: }
139: 
140: //蜂鸣器响每隔 times 毫秒时间响 tim 次
```

## ZGloveR_J1.ino | beep_on_times | 原文件第141-151行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
141: void beep_on_times(int times, int tim) {
142:     int i;
143:     for(i=0;i<times;i++) {
144:         beep_on();
145:         delay(tim);
146:         beep_off();
147:         delay(tim);
148:     }
149: }
150: 
151: //校准按键
```

## ZGloveR_J1.ino | loop_key_j | 原文件第152-161行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
152: void loop_key_j() {
153:     static u8 flag=0;
154:     if((digitalRead(PIN_KEY_J)==LOW) && (flag==0)) {//第一次校准，握手值：在舒适的方式下最大程度的握紧手指，此时按下校准按钮
155:         delay(10);    
156:         if((digitalRead(PIN_KEY_J)==LOW) && (flag==0)){
157:             while(digitalRead(PIN_KEY_J)==LOW);
158:             adc_read2buf();
159:             for(int i=0;i<DWQ_NUM;i++) {
160:                 ADC_MIN[i] = pos[i];
161:             }
```

## ZGloveR_J1.ino | loop_key_j | 原文件第162-169行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
162:             beep_on();delay(100);beep_off();
163:             eepromWrite(ADC_MIN_ADDR, sizeof(ADC_MIN), (u8 *)ADC_MIN);
164:             flag = 1; 
165: 
166:             sprintf(cmd_return,"ad0:%d ad1:%d ad2:%d ad3:%d ad4:%d ad5:%d ad6:%d ",
167:             pos_x, pos_y, pos[0], pos[1], pos[2], pos[3], pos[4]);
168:             Serial.println(cmd_return);  
169:         }
```

## ZGloveR_J1.ino | loop_key_j | 原文件第170-178行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
170:     } else if((digitalRead(PIN_KEY_J)==LOW) && (flag==1)) {//第二次校准，伸手值：在舒适的方式下最大程度的伸开手指，此时按下校准按钮
171:         delay(10);    
172:         if((digitalRead(PIN_KEY_J)==LOW ) && (flag==1)){
173:             while(digitalRead(PIN_KEY_J)==LOW);
174:             adc_read2buf();
175:             for(int i=0;i<DWQ_NUM;i++) {
176:                 ADC_MAX[i] = pos[i];
177:             }
178:             for(int i=0;i<DWQ_NUM;i++) {
```

## ZGloveR_J1.ino | loop_key_j | 原文件第179-187行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
179:                 ADC_MID[i] = (ADC_MIN[i] + ADC_MAX[i])/2;
180:                 pos_p[i] = 1.0*JXB_PWM_RANGE/(abs(ADC_MIN[i] - ADC_MAX[i]));//放大倍数
181:             }
182:             beep_on();delay(500);beep_off();
183:             eepromWrite(ADC_MAX_ADDR,  sizeof(ADC_MAX), (u8 *)ADC_MAX);
184:             flag = 0;  
185: 
186:             
187:             pos_x_verify = pos_x+1024;//+1024防止出现负数
```

## ZGloveR_J1.ino | loop_key_j | 原文件第188-196行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
188:             pos_y_verify = pos_y+1024;//防止出现负数
189:             
190:             EEPROM.write(POS_X_ADDR, pos_x_verify/256);
191:             EEPROM.write(POS_X_ADDR+1, pos_x_verify%256);//写陀螺仪X的校准值
192: 
193:             EEPROM.write(POS_Y_ADDR, pos_y_verify/256);
194:             EEPROM.write(POS_Y_ADDR+1, pos_y_verify%256);//写陀螺仪Y的校准值
195: 
196:             pos_x_verify = pos_x_verify-1024;
```

## ZGloveR_J1.ino | loop_key_j | 原文件第197-207行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
197:             pos_y_verify = pos_y_verify-1024;
198:             
199: 
200:             sprintf(cmd_return,"x:%d y:%d ad0:%d ad1:%d ad1:%d ad3:%d ad4:%d ",
201:             pos_x, pos_y, pos[0], pos[1], pos[2], pos[3], pos[4]);
202:             Serial.println(cmd_return);    
203:             delay(3000);       
204:         }    
205:     }
206:     //切换机械臂控制模式
207:     if(digitalRead(PIN_KEY_M)==LOW) {//模式切换按钮
```

## ZGloveR_J1.ino | loop_key_j | 原文件第208-221行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
208:         delay(10);    
209:         if(digitalRead(PIN_KEY_M)==LOW){
210:             robot_mode++;
211:         }
212: 
213:         if(robot_mode==2)robot_mode=0;//最多2种模式
214:         for(int i=0;i<robot_mode+1;i++) {
215:             beep_on();delay(300);beep_off();delay(100);
216:         }
217:     }    
218: }
219: 
220: /*
221: //获取旋钮模拟值的中间值
```

## ZGloveR_J1.ino | Filter | 原文件第222-233行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
222: int Filter(int FILTER_N, int pin) {
223:   int filter_buf[FILTER_N];
224:   int i, j;
225:   int filter_temp;
226:   for(i = 0; i < FILTER_N; i++) {
227:     filter_buf[i] = analogRead(pin);
228:     delayMicroseconds(300);
229:   }
230:   // 采样值从小到大排列（冒泡法）
231:   for(j = 0; j < FILTER_N - 1; j++) {
232:     for(i = 0; i < FILTER_N - 1 - j; i++) {
233:       if(filter_buf[i] > filter_buf[i + 1]) {
```

## ZGloveR_J1.ino | Filter | 原文件第234-243行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
234:         filter_temp = filter_buf[i];
235:         filter_buf[i] = filter_buf[i + 1];
236:         filter_buf[i + 1] = filter_temp;
237:       }
238:     }
239:   }
240:   return filter_buf[(FILTER_N - 1) / 2];
241: }
242: */
243: 
```

## ZGloveR_J1.ino | adc_read2buf | 原文件第244-255行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
244: void adc_read2buf() {
245:     int filter_temp;
246:     static u32 knob_value;
247:     static int16_t ax_t[5],ay_t[5],az_t[5];
248:    //获取手指旋钮的模拟值
249:     for(int i=0;i<5;i++) {
250:         knob_value = 0;
251:         for(int j=0;j<10;j++) {
252:             knob_value+=analogRead(dwq_pin[i]);
253:             delayMicroseconds(100);
254:          }
255:          knob_value = knob_value/10.0;
```

## ZGloveR_J1.ino | adc_read2buf | 原文件第256-268行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
256:          pos[i] = knob_value;
257:     }
258: 
259:     for(int i=0;i<5;i++) {
260:         myAdxl345.getAcceleration(&ax_t[i], &ay_t[i], &az_t[i]);
261:     }
262:     
263:     // 采样值从小到大排列（冒泡法），采样5次，获取陀螺仪的中间值    
264:     for(int j = 0; j < 4; j++) {
265:         for(int i = 0; i < 4 - j; i++) {
266:           if(ax_t[i] > ax_t[i + 1]) {
267:             filter_temp = ax_t[i];
268:             ax_t[i] = ax_t[i + 1];
```

## ZGloveR_J1.ino | adc_read2buf | 原文件第269-284行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
269:             ax_t[i + 1] = filter_temp;
270:           }
271: 
272:           if(ay_t[i] > ay_t[i + 1]) {
273:             filter_temp = ay_t[i];
274:             ay_t[i] = ay_t[i + 1];
275:             ay_t[i + 1] = filter_temp;
276:           }
277:         }
278:     }
279:        
280:     pos_x = ax_t[2];
281:     pos_y = ay_t[2];
282:     
283: #if 0
284:         
```

## ZGloveR_J1.ino | adc_read2buf | 原文件第285-292行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
285:       sprintf(cmd_return,"ax:%04d ay:%04d ad1:%04d ad2:%04d ad3:%04d ad4:%04d ad5:%04d ",
286:                           pos_x, pos_y, pos[0], pos[1], pos[2], pos[3], pos[4]);
287:       Serial.println(cmd_return);           // 握拳时，1，4，5值大，2，3小
288:       delay(100);
289:       
290: #endif
291: }
292: 
```

## ZGloveR_J1.ino | loop_nled | 原文件第293-305行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
293: void loop_nled() {
294:     static u32 systick_ms_bak = 0;
295:     static u8 flag=0;
296:     if(millis() - systick_ms_bak<500)return;
297:     systick_ms_bak = millis();
298:     flag = !flag;
299:     if(flag) {
300:         nled_on();
301:     } else {
302:         nled_off();
303:     }
304: }
305: 
```

## ZGloveR_J1.ino | loop_Gihand_R | 原文件第306-315行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
306: void loop_Gihand_R(){
307:     u8 pos_bias = 20;  //与极限值的偏差
308:     static u8 claw_flag = 0;
309:     static u16 kms_x = 0,kms_y = 0,kms_z = 50;
310:     static u16 kms_x_bak = 0,kms_y_bak = 0;
311:     static u16 servo_pwm = 0,servo_pwm_bak = 0;
312:     static u32 systick_ms_bak = 0,systick_ms_bak_mode = 0;
313:     adc_read2buf();
314:     //获取校准后的陀螺仪值，-250~+250
315:     pos_x= pos_x-pos_x_verify;
```

## ZGloveR_J1.ino | loop_Gihand_R | 原文件第316-320行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
316:     pos_y= pos_y-pos_y_verify;
317:            
318:     //采集手套陀螺仪和手指旋钮的值,判断是否是握紧状态且手平行
319:     if((abs(pos_x) < 30) && (abs(pos_y) < 30) && (pos[0] > (ADC_MIN[0]-pos_bias)) && (pos[1] < (ADC_MIN[1]+pos_bias)) && (pos[2] < (ADC_MIN[2]+pos_bias)) && (pos[3] > (ADC_MIN[3]-pos_bias)) && (pos[4] > (ADC_MIN[4]-pos_bias))){  
320:         systick_ms_bak_mode = millis();
```

## ZGloveR_J1.ino | loop_Gihand_R | 原文件第321-324行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
321:         while((abs(pos_x) < 50) && (abs(pos_y) < 50) && (pos[0] > (ADC_MIN[0]-pos_bias)) && (pos[1] < (ADC_MIN[1]+pos_bias)) && (pos[2] < (ADC_MIN[2]+pos_bias)) && (pos[3] > (ADC_MIN[3]-pos_bias)) && (pos[4] > (ADC_MIN[4]-pos_bias))){
322:             //握紧状态超过3秒进入地盘控制模式
323:             if(millis() - systick_ms_bak_mode > 3000){             
324:                 control_mode = 1; //切换到地盘控制模式 
```

## ZGloveR_J1.ino | loop_Gihand_R | 原文件第325-332行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
325:                 //beep_on_tiems(1,1000); 
326:                 sprintf(cmd_return,"{#000P1500T1000!#001P2150T1000!#002P2200T1000!#003P0850T1000!#004P1500T1000!#005P1500T1000!}");//机械臂蜷缩
327:                 Serial.println(cmd_return);
328:                 return;         
329:             }
330:         }
331:         if(millis() - systick_ms_bak_mode < 1000){
332:             sprintf(cmd_return,"{#005P1700T1000!}");//爪子闭合
```

## ZGloveR_J1.ino | loop_Gihand_R | 原文件第333-338行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
333:             Serial.println(cmd_return); 
334:         }       
335:     }
336:     //判断手指是否是张开状态且手平行
337:     if((abs(pos_x) < 50) && (abs(pos_y) < 50) && (pos[0] < (ADC_MAX[0]+pos_bias)) && (pos[1] > (ADC_MAX[1]-pos_bias)) && (pos[2] > (ADC_MAX[2]-pos_bias)) && (pos[3] < (ADC_MAX[3]+pos_bias)) && (pos[4] < (ADC_MAX[4]+pos_bias))){  
338:         systick_ms_bak_mode = millis();
```

## ZGloveR_J1.ino | loop_Gihand_R | 原文件第339-342行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
339:         while((abs(pos_x) < 50) && (abs(pos_y) < 50) && (pos[0] < (ADC_MAX[0]+pos_bias)) && (pos[1] > (ADC_MAX[1]-pos_bias)) && (pos[2] > (ADC_MAX[2]-pos_bias)) && (pos[3] < (ADC_MAX[3]+pos_bias)) && (pos[4] < (ADC_MAX[4]+pos_bias))){
340:             //伸展状态超过3秒进入机械臂控制模式
341:             if(millis() - systick_ms_bak_mode > 3000){             
342:                 control_mode = 0; //切换到机械臂控制模式
```

## ZGloveR_J1.ino | loop_Gihand_R | 原文件第343-350行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
343:                 //beep_on_tiems(2,100);  
344:                 sprintf(cmd_return,"{#000P1500T1000!#001P1500T1000!#002P1500T1000!#003P1500T1000!#004P1500T1000!#005P1500T1000!}");//机械臂直立
345:                 Serial.println(cmd_return); 
346:                 return;        
347:             }
348:         }
349:         if(millis() - systick_ms_bak_mode < 1000){
350:             sprintf(cmd_return,"{#005P1200T1000!}");//爪子张开
```

## ZGloveR_J1.ino | loop_Gihand_R | 原文件第351-362行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
351:             Serial.println(cmd_return); 
352:         }       
353:     }
354:   
355:     if(millis() - systick_ms_bak > 100) {
356:         systick_ms_bak = millis();
357:         
358:          //获取校准后的旋钮值
359:         for(int i=0;i<5;i++){
360:             pos[i] = (int)(pos[i]-ADC_MID[i]);
361:         }
362:         //sprintf(cmd_return,"ax:%04d ay:%04d ad1:%04d ad2:%04d ad3:%04d ad4:%04d ad5:%04d ",
```

## ZGloveR_J1.ino | loop_Gihand_R | 原文件第363-372行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
363:                          // pos_x, pos_y, pos[0], pos[1], pos[2], pos[3], pos[4]);
364:         //Serial.println(cmd_return);           // 握拳时，0，3，4值大，1，2小
365:         //机械臂控制模式
366:         if(control_mode == 0){
367:             //值太小不动
368:             if(abs(pos_x) < 20)pos_x = 0;               
369:             if(abs(pos_y) < 20) pos_y = 0; 
370:             
371:             if(robot_mode == 0){
372:                 
```

## ZGloveR_J1.ino | loop_Gihand_R | 原文件第373-377行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
373:                 servo_pwm = 1500-pos[2]*2;//控制爪子，用中指的值就行，
374:                 //机械臂控制模式,已低姿夹取姿态为基准位置，计算陀螺仪x值控制机械臂向前移动，手套后倾换另一种计算方式
375:                 if(pos_x < -40) {
376:                     sprintf(cmd_return, "{#000P%04dT1000!#001P%04dT1000!#002P%04dT0500!#003P%04dT0500!#005P%04dT0500!}", 1500-pos_y*4,1350+pos_x*1,2100+pos_x*1,1000-pos_x*1,servo_pwm); 
377:                     //向前倾。1号舵机前伸值减小，2号舵机后伸值减小,3号舵机值增大
```

## ZGloveR_J1.ino | loop_Gihand_R | 原文件第378-383行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
378:                     Serial.println(cmd_return);
379:                 }  else if(pos_x > 40){
380:                     sprintf(cmd_return, "{#000P%04dT1000!#001P%04dT0500!#002P%04dT0500!#003P%04dT0500!#005P%04dT0500!}", 1500-pos_y*4,1350+pos_x*2,2100-pos_x*1,1000+pos_x*1,servo_pwm); 
381:                     //抬起。1号舵机后伸值增大，2号舵机后伸值减小,3号舵机值增大
382:                     Serial.println(cmd_return);
383:                 }
```

## ZGloveR_J1.ino | loop_Gihand_R | 原文件第384-392行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
384:                                
385:              }else if(robot_mode == 1){
386:                 //逆运动学的控制方式                                                                                       
387:                 kms_x = pos_y;
388:                 kms_y = 200-pos_x;
389:                 kms_z = 20;
390:                  //手后倾时控制机械臂高度，
391:                 if(pos_x > 40){
392:                    kms_z = pos_x;
```

## ZGloveR_J1.ino | loop_Gihand_R | 原文件第393-402行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
393:                    kms_y = 150; 
394:                  }
395:                
396:                 kms_x_bak = kms_x;
397:                 kms_y_bak = kms_y;
398:     
399:                 //数据发送快，控制板解析不了，控制爪子的时候就不控制机械臂
400:                 servo_pwm = 1500-pos[2]*2;
401:                 if(abs(servo_pwm - servo_pwm_bak) > 100){
402:                     servo_pwm_bak = servo_pwm;  
```

## ZGloveR_J1.ino | loop_Gihand_R | 原文件第403-409行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
403:                     sprintf(cmd_return, "#005P%04dT0500!", servo_pwm); 
404:                     Serial.println(cmd_return);
405:                 }else{
406:                    sprintf(cmd_return, "$KMS:%d,%d,%d,%d!", kms_x,kms_y,kms_z,300); 
407:                    Serial.println(cmd_return);                  
408:                 }               
409:              }                                  
```

## ZGloveR_J1.ino | loop_Gihand_R | 原文件第410-414行
来源：003-源码例程\04-右体感手套源码\02-体感手套程序源码\ZGloveR_J1\ZGloveR_J1.ino
以下为原始源码，不是截图OCR。
```
410:         }else if(control_mode == 1){
411:             
412:         }
413:     }       
414: }
```
