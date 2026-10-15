## J1-OpenMV颜色跟随-240106.py | 文件开头/全局定义 | 原文件第1-15行
来源：003-源码例程\06-视觉OpenMV拓展\01-OpenMV颜色跟随代码\J1-OpenMV颜色跟随-240106.py
以下为原始源码，不是截图OCR。
```
1: '''
2: 颜色跟随
3: 实验效果：
4:     本实验以跟随红色木块为例。
5:     将红色木块在OpenMV前至少10厘米开外上下左右移动时，机械臂摄像头会跟随红色模块运动。
6: 还可自行将红色阈值替换为其他颜色阈值来识别。
7: # 注意：环境光会对识别有影响，找比较合适的环境来运行此程序。
8: 颜色阈值采集方法：
9: 方法一：
10:     1.可以在‘工具’-->‘机器视觉’-->‘阈值编辑器’-->‘帧缓冲区’中采集，
11:     2.拖动6个滑块来调整图像，直到要采集的颜色都呈白色，其他都呈黑色为止，
12:     3.采集好之后将LAB阈值复制到代码中的阈值处使用即可。
13: 方法二：
14:     1.可以在右侧‘帧缓冲区’和‘直方图’的’LAB色彩空间‘配合采集
15:     2.先在帧缓冲区中用鼠标左键框出要采集的颜色区域，
```

## J1-OpenMV颜色跟随-240106.py | 文件开头/全局定义 | 原文件第16-28行
来源：003-源码例程\06-视觉OpenMV拓展\01-OpenMV颜色跟随代码\J1-OpenMV颜色跟随-240106.py
以下为原始源码，不是截图OCR。
```
16:     3.然后在直方图中的LAB色彩空间中，分别复制L、A、B的最小值和最大值到代码中的颜色阈值元组中使用即可
17: '''
18: from pyb import millis, UART, Servo
19: from math import pi, isnan
20: import sensor, image, time
21: import utime
22: 
23: target_threshold  = (18, 74, 20, 127, -25, 127)    # 此处以红色为例
24: pwm_value1 = 1500     # 云台下方舵机的pwm值
25: pwm_value2 = 1000     # 003号舵机的pwm值
26: systick_ms_bak = 0    # 记录系统运行时间
27: 
28: # 初始化函数
```

## J1-OpenMV颜色跟随-240106.py | init_setup | 原文件第29-35行
来源：003-源码例程\06-视觉OpenMV拓展\01-OpenMV颜色跟随代码\J1-OpenMV颜色跟随-240106.py
以下为原始源码，不是截图OCR。
```
29: def init_setup():
30:     global sensor, clock, uart3
31:     sensor.reset()                               # 初始化感光元件
32:     sensor.set_pixformat(sensor.RGB565)          # 图像格式设置为彩色
33:     sensor.set_framesize(sensor.QQVGA)           # 图像大小设置为QQVGA，即160x120
34:     sensor.skip_frames(10)                       # 跳过10帧，使以上设置生效
35:     sensor.set_auto_whitebal(False)              # 关闭白平衡
```

## J1-OpenMV颜色跟随-240106.py | init_setup | 原文件第36-44行
来源：003-源码例程\06-视觉OpenMV拓展\01-OpenMV颜色跟随代码\J1-OpenMV颜色跟随-240106.py
以下为原始源码，不是截图OCR。
```
36:     clock = time.clock()                         # 创建时钟对象
37:     uart3 = UART(3, 115200)                      # 初始化串口3，设置波特率为115200
38:     print('初始化完成')
39: 
40:     utime.sleep(3)                               # 延时3秒
41:     # 使机械臂呈半弯曲状态，方便摄像头查看物体
42:     uart3_send("{#000P1500T1500!#001P2000T1500!#002P2000T1500!#003P1000T1500!#004P1500T1500!#005P1200T1500!}")
43:     utime.sleep(2)                               # 延时2秒
44: 
```

## J1-OpenMV颜色跟随-240106.py | init_setup | 原文件第45-46行
来源：003-源码例程\06-视觉OpenMV拓展\01-OpenMV颜色跟随代码\J1-OpenMV颜色跟随-240106.py
以下为原始源码，不是截图OCR。
```
45: 
46: # 串口接收数据
```

## J1-OpenMV颜色跟随-240106.py | uart3_recv | 原文件第47-52行
来源：003-源码例程\06-视觉OpenMV拓展\01-OpenMV颜色跟随代码\J1-OpenMV颜色跟随-240106.py
以下为原始源码，不是截图OCR。
```
47: def uart3_recv():
48:     recv_data = uart3.read()
49:     print('recv data: %s' % recv_data)
50:     return recv_data
51: 
52: # 串口发送数据
```

## J1-OpenMV颜色跟随-240106.py | uart3_send | 原文件第53-57行
来源：003-源码例程\06-视觉OpenMV拓展\01-OpenMV颜色跟随代码\J1-OpenMV颜色跟随-240106.py
以下为原始源码，不是截图OCR。
```
53: def uart3_send(send_data):
54:     global uart3
55:     uart3.write(send_data)
56: 
57: # 查找识别到的目标颜色区域中最大区域的函数
```

## J1-OpenMV颜色跟随-240106.py | find_max | 原文件第58-66行
来源：003-源码例程\06-视觉OpenMV拓展\01-OpenMV颜色跟随代码\J1-OpenMV颜色跟随-240106.py
以下为原始源码，不是截图OCR。
```
58: def find_max(blobs):
59:     max_size = 0
60:     for blob in blobs:
61:         if blob[2] * blob[3] > max_size:
62:             max_blob = blob
63:             max_size = blob[2] * blob[3]
64:     return max_blob
65: 
66: # 摄像头跟随
```

## J1-OpenMV颜色跟随-240106.py | camera_follow | 原文件第67-75行
来源：003-源码例程\06-视觉OpenMV拓展\01-OpenMV颜色跟随代码\J1-OpenMV颜色跟随-240106.py
以下为原始源码，不是截图OCR。
```
67: def camera_follow(x_bias, y_bias):
68:     global pwm_value1, pwm_value2
69:     if abs(x_bias) > 2 or abs(y_bias) > 2:
70:         pwm_value1 = pwm_value1 - x_bias//1.3   # 当跟随的幅度太大（或太小）时，将1.3调大（或调小）一点
71:         pwm_value2 = pwm_value2 - y_bias//1.3   # 当跟随的幅度太大（或太小）时，将1.3调大（或调小）一点
72:         # pwm值超出设定范围时的处理
73:         if pwm_value1 > 2000:
74:             pwm_value1 = 2000
75:         if pwm_value1 < 1000:
```

## J1-OpenMV颜色跟随-240106.py | camera_follow | 原文件第76-85行
来源：003-源码例程\06-视觉OpenMV拓展\01-OpenMV颜色跟随代码\J1-OpenMV颜色跟随-240106.py
以下为原始源码，不是截图OCR。
```
76:             pwm_value1 = 1000
77:         if pwm_value2 > 1300:
78:             pwm_value2 = 1300
79:         if pwm_value2 < 600:
80:             pwm_value2 = 600
81:         Str = '{#000P%04dT0000!#003P%04dT0000!}' % (pwm_value1, pwm_value2)
82:         print('str: ', Str)
83:         uart3_send(Str)
84: 
85: # 主函数
```

## J1-OpenMV颜色跟随-240106.py | main | 原文件第86-97行
来源：003-源码例程\06-视觉OpenMV拓展\01-OpenMV颜色跟随代码\J1-OpenMV颜色跟随-240106.py
以下为原始源码，不是截图OCR。
```
86: def main():
87:     global systick_ms_bak
88:     while 1:
89:         if millis() - systick_ms_bak >= 50:
90:             systick_ms_bak = millis()
91:             clock.tick()                             # 更新FPS帧率时钟
92:             img = sensor.snapshot()                  # 拍一张照片并返回图像
93: 
94:             blobs = img.find_blobs([target_threshold])  # 查找图像中的目标颜色
95: 
96:             # 如果图像中有目标颜色
97:             if blobs:
```

## J1-OpenMV颜色跟随-240106.py | main | 原文件第98-106行
来源：003-源码例程\06-视觉OpenMV拓展\01-OpenMV颜色跟随代码\J1-OpenMV颜色跟随-240106.py
以下为原始源码，不是截图OCR。
```
98:                 max_blob = find_max(blobs)           # 找到最大的目标颜色区域
99:                 img.draw_rectangle(max_blob.rect())  # 将最大的目标颜色区域框出来
100:                 img.draw_cross(max_blob.cx(), max_blob.cy())  # 在目标颜色区域的中心点处画十字
101: 
102:                 #获取目标颜色区域的宽度和高度
103:                 c_w = max_blob.w()
104:                 c_h = max_blob.h()
105: 
106:                 #print('c_w: ', c_w, end='\t')
```

## J1-OpenMV颜色跟随-240106.py | main | 原文件第107-117行
来源：003-源码例程\06-视觉OpenMV拓展\01-OpenMV颜色跟随代码\J1-OpenMV颜色跟随-240106.py
以下为原始源码，不是截图OCR。
```
107:                 #print('c_h: ', c_h)
108: 
109:                 #获取目标颜色区域的中点坐标和画面中心点的坐标差值
110:                 x_bias = max_blob.cx() - img.width()/2
111:                 y_bias = max_blob.cy() - img.height()/2
112: 
113:                 #print('x_bias: ', x_bias, end='\t')
114:                 #print('y_bias: ', y_bias)
115: 
116:                 # 当目标颜色区域的宽度和高度满足条件时再跟随
117:                 if 4 < c_w < 80 and 4 < c_h < 80:
```

## J1-OpenMV颜色跟随-240106.py | main | 原文件第118-127行
来源：003-源码例程\06-视觉OpenMV拓展\01-OpenMV颜色跟随代码\J1-OpenMV颜色跟随-240106.py
以下为原始源码，不是截图OCR。
```
118:                     camera_follow(x_bias, y_bias)
119: 
120: # 程序入口
121: if __name__ == '__main__':
122:     init_setup()    # 执行初始化函数
123:     try:
124:         main()      # 执行主函数
125:     finally:
126:         # 使机械臂呈半弯曲状态，方便摄像头查看物体
127:         uart3_send("{#000P1500T1500!#001P2000T1500!#002P2000T1500!#003P1000T1500!#004P1500T1500!#005P1200T1500!}")
```
