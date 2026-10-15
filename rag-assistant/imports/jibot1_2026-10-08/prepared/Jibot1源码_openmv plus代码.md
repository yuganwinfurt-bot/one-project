## main.py | 文件开头/全局定义 | 原文件第1-16行
来源：005-拓展资料\04-气泵拓展openmv案例\openmv plus代码.zip!/openmvplus代码/main.py
以下为原始源码，不是截图OCR。
```
1: # Tensorflow垃圾分类
2: 
3: import sensor, image, time, os, tf, uos, gc
4: from pyb import UART
5: import utime
6: net = None
7: labels = None
8: 
9: # 各对应要执行的动作组
10: actions = {
11:            'detection_position_action': '$DGT:2-2,1!',# 机械臂最适合识别木块的位置的动作组
12:            'clamp_action': '$DGT:3-7,1!',             # 夹取动作组，即前抓动作组
13:            'dc_clamp_action': '$DGT:18-21,1!',       # 红色木块的放置动作组，即前放动作组
14:           }
15: 
16: # 初始化函数
```

## main.py | rubbish_init_setup | 原文件第17-25行
来源：005-拓展资料\04-气泵拓展openmv案例\openmv plus代码.zip!/openmvplus代码/main.py
以下为原始源码，不是截图OCR。
```
17: def rubbish_init_setup():
18:     global sensor, net, labels, clock,uart3      # 设置为全局变量
19:     sensor.reset()                         # 初始化感光元件
20:     sensor.set_pixformat(sensor.RGB565)  # 设置图像格式为RGB
21:     sensor.set_framesize(sensor.QVGA)      # 设置图像大小为 QVGA (320x240)
22: #    sensor.set_windowing((240, 240))       # 设置窗口大小为 240x240
23:     sensor.skip_frames(10)                 # 跳过一些帧，使以上设置生效
24: 
25:     try:
```

## main.py | rubbish_init_setup | 原文件第26-29行
来源：005-拓展资料\04-气泵拓展openmv案例\openmv plus代码.zip!/openmvplus代码/main.py
以下为原始源码，不是截图OCR。
```
26:         # 加载模型文件
27:         net = tf.load("trained.tflite", load_to_fb=uos.stat('trained.tflite')[6] > (gc.mem_free() - (64*1024)))
28:     except Exception as e:
29:         print(e)
```

## main.py | Exception | 原文件第30-34行
来源：005-拓展资料\04-气泵拓展openmv案例\openmv plus代码.zip!/openmvplus代码/main.py
以下为原始源码，不是截图OCR。
```
30:         raise Exception('Failed to load "trained.tflite", did you copy the .tflite and labels.txt file onto the mass-storage device? (' + str(e) + ')')
31: 
32:     try:
33:         labels = [line.rstrip('\n') for line in open("labels.txt")]
34:     except Exception as e:
```

## main.py | Exception | 原文件第35-44行
来源：005-拓展资料\04-气泵拓展openmv案例\openmv plus代码.zip!/openmvplus代码/main.py
以下为原始源码，不是截图OCR。
```
35:         raise Exception('Failed to load "labels.txt", did you copy the .tflite and labels.txt file onto the mass-storage device? (' + str(e) + ')')
36: 
37:     clock = time.clock()        # 创建时钟对象
38:     uart3 = UART(3, 115200)                # 初始化串口3，设置波特率为115200
39:     print('初始化完成')
40:     utime.sleep(2)
41:     uart3_send(actions['detection_position_action'])
42:     utime.sleep(2)
43: 
44: # 串口发送数据
```

## main.py | uart3_send | 原文件第45-49行
来源：005-拓展资料\04-气泵拓展openmv案例\openmv plus代码.zip!/openmvplus代码/main.py
以下为原始源码，不是截图OCR。
```
45: def uart3_send(send_data):
46:     global uart3
47:     uart3.write(send_data)
48: 
49: # 主函数
```

## main.py | rubbish_main | 原文件第50-56行
来源：005-拓展资料\04-气泵拓展openmv案例\openmv plus代码.zip!/openmvplus代码/main.py
以下为原始源码，不是截图OCR。
```
50: def rubbish_main():
51:     while 1:
52:         clock.tick()                # 更新FPS帧率时钟
53:         img = sensor.snapshot()     # 拍一张照片并返回图像
54:         rubbish_name = None  # 初始化垃圾名称
55:         # default settings just do one detection... change them to search the image...
56:         for obj in net.classify(img, min_scale=1.0, scale_mul=0.8, x_overlap=0.5, y_overlap=0.5):
```

## main.py | rubbish_main | 原文件第57-63行
来源：005-拓展资料\04-气泵拓展openmv案例\openmv plus代码.zip!/openmvplus代码/main.py
以下为原始源码，不是截图OCR。
```
57:             #print("**********\nPredictions at [x=%d,y=%d,w=%d,h=%d]" % obj.rect())
58:             img.draw_rectangle(obj.rect())
59:             # 将分类和对应的相似度以列表套元组形式返回
60:             predictions_list = list(zip(labels, obj.output()))
61:             # 打印分类和与图像中检测到的物体的对应的相似度
62:             #for i in range(len(predictions_list)):
63:                 #print("%s = %f" % (predictions_list[i][0], predictions_list[i][1]))
```

## main.py | rubbish_main | 原文件第64-70行
来源：005-拓展资料\04-气泵拓展openmv案例\openmv plus代码.zip!/openmvplus代码/main.py
以下为原始源码，不是截图OCR。
```
64:             if max(obj.output()) > 0.7:   # 当识别到的最大的相似度大于0.7时才认为是识别到了垃圾
65:                 # 将识别到的垃圾名称赋值给rubbish_name
66:                 img = sensor.snapshot()     # 拍一张照片并返回图像
67:                 rubbish_name = labels[obj.output().index(max(obj.output()))]
68:                 if rubbish_name == 'dc':
69:                    print('识别到的是 %s' % rubbish_name)
70:                    rubbish_name = None  # 初始化垃圾名称
```

## main.py | rubbish_main | 原文件第71-77行
来源：005-拓展资料\04-气泵拓展openmv案例\openmv plus代码.zip!/openmvplus代码/main.py
以下为原始源码，不是截图OCR。
```
71:                    uart3_send(actions['clamp_action'])      # 串口将前抓动作组指令发出去
72:                    utime.sleep(8)
73:                    uart3_send(actions['dc_clamp_action'])
74:                    utime.sleep(8)                           # 延时以便让动作组执行完成
75:                    # 放置完木块后，再次运行到最适合的识别位置
76:                    uart3_send(actions['detection_position_action'])
77:                    utime.sleep(2)
```

## main.py | rubbish_main | 原文件第78-88行
来源：005-拓展资料\04-气泵拓展openmv案例\openmv plus代码.zip!/openmvplus代码/main.py
以下为原始源码，不是截图OCR。
```
78:                    print('数据已发送完成')
79:                 if rubbish_name == 'DJ':
80:                    print('识别到的是 %s' % rubbish_name)
81:                    uart3_send(actions['detection_position_action'])
82:                    rubbish_name = None  # 初始化垃圾名称
83:                    utime.sleep(2)
84:         #print(clock.fps(), "fps")  # 打印帧率
85: 
86: # 程序入口
87: if __name__ == '__main__':
88:     rubbish_init_setup()  # 执行初始化函数
```

## main.py | rubbish_main | 原文件第89-92行
来源：005-拓展资料\04-气泵拓展openmv案例\openmv plus代码.zip!/openmvplus代码/main.py
以下为原始源码，不是截图OCR。
```
89:     try:
90:         rubbish_main()    # 执行主函数
91:     except:
92:         pass
```
