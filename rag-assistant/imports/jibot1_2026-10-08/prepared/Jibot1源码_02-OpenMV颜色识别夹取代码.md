## J1-OpenMV颜色识别夹取-240106.py | 文件开头/全局定义 | 原文件第1-14行
来源：003-源码例程\06-视觉OpenMV拓展\02-OpenMV颜色识别夹取代码\J1-OpenMV颜色识别夹取-240106.py
以下为原始源码，不是截图OCR。
```
1: '''
2: 颜色识别夹取木块
3: 实验效果：
4:     将红绿蓝其中任意一种颜色的木块放置在机械臂正前方8厘米左右处，OpenMV会根据识别到的木块颜色来将
5:     对应的木块放置到对应位置：
6:         如果识别到的是红色木块，则夹取红色模块放置到前方偏远位置；
7:         如果识别到的是绿色木块，则夹取绿色模块放置到左侧偏远位置；
8:         如果识别到的是蓝色木块，则夹取蓝色模块放置到右侧偏远位置；
9:         未识别到红绿蓝木块时，保持不动。
10: 红绿蓝三种颜色可以同时识别，还可自行添加其他颜色阈值来识别其他颜色
11: # 注意：环境光会对识别有影响，找比较合适的环境来运行此程序。
12: 颜色阈值采集方法：
13: 方法一：
14:     1.可以在‘工具’-->‘机器视觉’-->‘阈值编辑器’-->‘帧缓冲区’中采集，
```

## J1-OpenMV颜色识别夹取-240106.py | 文件开头/全局定义 | 原文件第15-29行
来源：003-源码例程\06-视觉OpenMV拓展\02-OpenMV颜色识别夹取代码\J1-OpenMV颜色识别夹取-240106.py
以下为原始源码，不是截图OCR。
```
15:     2.拖动6个滑块来调整图像，直到要采集的颜色都呈白色，其他都呈黑色为止，
16:     3.采集好之后将LAB阈值复制到代码中的阈值处使用即可。
17: 方法二：
18:     1.可以在右侧‘帧缓冲区’和‘直方图’的’LAB色彩空间‘配合采集
19:     2.先在帧缓冲区中用鼠标左键框出要采集的颜色区域，
20:     3.然后在直方图中的LAB色彩空间中，分别复制L、A、B的最小值和最大值到代码中的颜色阈值元组中使用即可
21: '''
22: import sensor, time
23: from pyb import UART
24: import utime
25: import json
26: 
27: # 目标颜色实际出现的次数，每次目标颜色出现的次数超过5次时，才认为真的识别到了目标颜色，是为了防止误识别
28: target_color_appear_count = 0
29: 
```

## J1-OpenMV颜色识别夹取-240106.py | 文件开头/全局定义 | 原文件第30-38行
来源：003-源码例程\06-视觉OpenMV拓展\02-OpenMV颜色识别夹取代码\J1-OpenMV颜色识别夹取-240106.py
以下为原始源码，不是截图OCR。
```
30: # 设置颜色阈值，此处设置红绿蓝三种颜色的阈值
31: thresholds = {
32:               'red': (3, 85, 33, 112, 73, -7),        # 红色阈值
33:               'green': (72, 31, -27, -50, 48, -11),   # 绿色阈值
34:               'blue': (16, 74, -53, 76, -32, -76)     # 蓝色阈值
35:              }
36: # 各颜色对应要执行的动作组
37: actions = {
38:            'detection_position_action': '$DGT:2-2,1!',# 机械臂最适合识别木块的位置的动作组
```

## J1-OpenMV颜色识别夹取-240106.py | 文件开头/全局定义 | 原文件第39-45行
来源：003-源码例程\06-视觉OpenMV拓展\02-OpenMV颜色识别夹取代码\J1-OpenMV颜色识别夹取-240106.py
以下为原始源码，不是截图OCR。
```
39:            'clamp_action': '$DGT:3-7,1!',             # 夹取动作组，即前抓动作组
40:            'red_clamp_action': '$DGT:18-21,1!',       # 红色木块的放置动作组，即前放动作组
41:            'green_clamp_action': '$DGT:22-26,1!',     # 绿色木块的放置动作组，即左放动作组
42:            'blue_clamp_action': '$DGT:27-31,1!'       # 蓝色木块的放置动作组，即右放动作组
43:           }
44: 
45: # 初始化函数
```

## J1-OpenMV颜色识别夹取-240106.py | init_setup | 原文件第46-51行
来源：003-源码例程\06-视觉OpenMV拓展\02-OpenMV颜色识别夹取代码\J1-OpenMV颜色识别夹取-240106.py
以下为原始源码，不是截图OCR。
```
46: def init_setup():
47:     global sensor, clock, uart3            # 设置为全局变量
48:     sensor.reset()                         # 初始化感光元件
49:     sensor.set_pixformat(sensor.RGB565)    # 设置感光元件图像色彩格式为 RGB565 (RGB565为彩图，GRAYSCALE为灰度图)
50:     sensor.set_framesize(sensor.QVGA)      # 设置感光元件分辨率大小为 QVGA (QVGA是320x240)
51:     sensor.skip_frames(10)                 # 跳过一些帧，使以上的设置生效
```

## J1-OpenMV颜色识别夹取-240106.py | init_setup | 原文件第52-59行
来源：003-源码例程\06-视觉OpenMV拓展\02-OpenMV颜色识别夹取代码\J1-OpenMV颜色识别夹取-240106.py
以下为原始源码，不是截图OCR。
```
52:     sensor.set_auto_gain(True)             # 打开自动增益, 默认打开；追踪颜色时需关闭白平衡
53:     sensor.set_auto_whitebal(True)         # 打开自动白平衡。默认打开；追踪颜色时需关闭白平衡
54:     sensor.set_auto_exposure(True)         # 打开自动曝光。默认打开
55:     clock = time.clock()                   # 创建时钟对象
56:     uart3 = UART(3, 115200)                # 初始化串口3，设置波特率为115200
57:     print('初始化完成')
58:     utime.sleep(3)
59:     uart3_send(actions['detection_position_action'])
```

## J1-OpenMV颜色识别夹取-240106.py | init_setup | 原文件第60-62行
来源：003-源码例程\06-视觉OpenMV拓展\02-OpenMV颜色识别夹取代码\J1-OpenMV颜色识别夹取-240106.py
以下为原始源码，不是截图OCR。
```
60:     utime.sleep(2)
61: 
62: # 串口接收数据
```

## J1-OpenMV颜色识别夹取-240106.py | uart3_recv | 原文件第63-68行
来源：003-源码例程\06-视觉OpenMV拓展\02-OpenMV颜色识别夹取代码\J1-OpenMV颜色识别夹取-240106.py
以下为原始源码，不是截图OCR。
```
63: def uart3_recv():
64:     recv_data = uart3.read()
65:     print('recv data: %s' % recv_data)
66:     return recv_data
67: 
68: # 串口发送数据
```

## J1-OpenMV颜色识别夹取-240106.py | uart3_send | 原文件第69-73行
来源：003-源码例程\06-视觉OpenMV拓展\02-OpenMV颜色识别夹取代码\J1-OpenMV颜色识别夹取-240106.py
以下为原始源码，不是截图OCR。
```
69: def uart3_send(send_data):
70:     global uart3
71:     uart3.write(send_data)
72: 
73: # 查找图像中最大的色块
```

## J1-OpenMV颜色识别夹取-240106.py | find_max | 原文件第74-82行
来源：003-源码例程\06-视觉OpenMV拓展\02-OpenMV颜色识别夹取代码\J1-OpenMV颜色识别夹取-240106.py
以下为原始源码，不是截图OCR。
```
74: def find_max(blobs):
75:     max_size = 0
76:     for blob in blobs:
77:         if blob[2] * blob[3] > max_size:
78:             max_blob = blob
79:             max_size = blob[2] * blob[3]
80:     return max_blob
81: 
82: # 主函数
```

## J1-OpenMV颜色识别夹取-240106.py | main | 原文件第83-90行
来源：003-源码例程\06-视觉OpenMV拓展\02-OpenMV颜色识别夹取代码\J1-OpenMV颜色识别夹取-240106.py
以下为原始源码，不是截图OCR。
```
83: def main():
84:     global target_color_appear_count
85:     while 1:                               # 无限循环
86:         clock.tick()                       # 更新FPS帧率时钟
87:         img = sensor.snapshot()            # 拍一张照片并返回图像
88:         # 循环3种颜色阈值，在图像中查看是否有对应颜色并做一些操作，thresholds需为字典格式
89:         for threshold in thresholds:
90:             blobs = img.find_blobs([thresholds[threshold]])  # 在图像中查找目标颜色区域
```

## J1-OpenMV颜色识别夹取-240106.py | main | 原文件第91-95行
来源：003-源码例程\06-视觉OpenMV拓展\02-OpenMV颜色识别夹取代码\J1-OpenMV颜色识别夹取-240106.py
以下为原始源码，不是截图OCR。
```
91:             if blobs:                                        # 当查找到目标颜色区域后
92:                 max_blob = find_max(blobs)                   # 查找图像中最大的目标色块
93:                 img.draw_rectangle(max_blob[0:4])            # 将找到的目标颜色区域用矩形框出来
94:                 img.draw_cross(max_blob[5], max_blob[6])     # 在目标颜色区域的中心点处画十字
95:                 target_area = max_blob.area()                # 获取目标颜色区域的面积
```

## J1-OpenMV颜色识别夹取-240106.py | main | 原文件第96-103行
来源：003-源码例程\06-视觉OpenMV拓展\02-OpenMV颜色识别夹取代码\J1-OpenMV颜色识别夹取-240106.py
以下为原始源码，不是截图OCR。
```
96:                 print('area is  ', target_area)              # 打印识别到的目标颜色区域面积
97: 
98:                 if 6000 < target_area < 30000:               # 面积合适时
99:                     target_color_appear_count += 1           # 目标颜色实际出现的次数+1
100: 
101:                 if target_color_appear_count > 5:            # 识别到的面积合适时的次数大于5次时串口发数据
102:                     print('uart3 send color is ', threshold)
103:                     #break
```

## J1-OpenMV颜色识别夹取-240106.py | main | 原文件第104-111行
来源：003-源码例程\06-视觉OpenMV拓展\02-OpenMV颜色识别夹取代码\J1-OpenMV颜色识别夹取-240106.py
以下为原始源码，不是截图OCR。
```
104:                     # 夹取木块
105:                     uart3_send(actions['clamp_action'])      # 串口将前抓动作组指令发出去
106:                     utime.sleep(8)                           # 延时以便让动作组执行完成
107: 
108:                     # 放置木块
109:                     if threshold == 'red':
110:                         uart3_send(actions['red_clamp_action'])    # 串口将红色木块对应的放置动作组发出去
111:                     elif threshold == 'green':
```

## J1-OpenMV颜色识别夹取-240106.py | main | 原文件第112-117行
来源：003-源码例程\06-视觉OpenMV拓展\02-OpenMV颜色识别夹取代码\J1-OpenMV颜色识别夹取-240106.py
以下为原始源码，不是截图OCR。
```
112:                         uart3_send(actions['green_clamp_action'])  # 串口将绿色木块对应的放置动作组发出去
113:                     elif threshold == 'blue':
114:                         uart3_send(actions['blue_clamp_action'])   # 串口将蓝色木块对应的放置动作组发出去
115:                     utime.sleep(8)                           # 延时以便让动作组执行完成
116:                     # 放置完木块后，再次运行到最适合的识别位置
117:                     uart3_send(actions['detection_position_action'])
```

## J1-OpenMV颜色识别夹取-240106.py | main | 原文件第118-127行
来源：003-源码例程\06-视觉OpenMV拓展\02-OpenMV颜色识别夹取代码\J1-OpenMV颜色识别夹取-240106.py
以下为原始源码，不是截图OCR。
```
118:                     utime.sleep(2)
119:                     target_color_appear_count = 0
120: 
121: # 程序入口
122: if __name__ == '__main__':
123:     init_setup()            # 执行初始化函数
124:     try:                    # 异常处理
125:         main()              # 执行主函数
126:     except:
127:         pass
```
