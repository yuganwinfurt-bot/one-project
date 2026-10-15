## actiongroup.cpp | 文件开头/全局定义 | 原文件第1-14行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
1: #include "actiongroup.h"
2: #include <qlist.h>
3: #include <qstring.h>
4: #include <QTextCodec>
5: 
6: ActionGroup::ActionGroup()
7: {
8:     for(int i=0;i<MAX_STEER_NUM;i++) {
9:         itemList[i].setIndex(i);
10:         itemList[i].setEnable(true);
11:         itemList[i].setChanged(false);
12:         itemList[i].setId(0);
13:         itemList[i].setBias(0);
14:         itemList[i].setPwm(0);
```

## actiongroup.cpp | 文件开头/全局定义 | 原文件第15-24行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
15:         itemList[i].setTime(0);
16:     }
17:     setIsGroup(true);
18: }
19: 
20: ActionGroup::~ActionGroup()
21: {
22: 
23: }
24: 
```

## actiongroup.cpp | ActionGroup::init | 原文件第25-38行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
25: void ActionGroup::init(){
26:     for(int i=0;i<MAX_STEER_NUM;i++) {
27:         itemList[i].setIndex(i);
28:         itemList[i].setId(i);
29:         itemList[i].setBias(0);
30:         itemList[i].setPwm(1500);
31:         itemList[i].setTime(1000);
32:         itemList[i].setEnable(false);
33:         itemList[i].setChanged(false);
34:     }
35:     setDisperse(false);
36:     setIsGroup(true);
37: }
38: 
```

## actiongroup.cpp | ActionGroup::setItemId | 原文件第39-43行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
39: void ActionGroup::setItemId(int index_s, int id_s) {
40:     itemList[index_s].setId(id_s);
41: }
42: 
43: 
```

## actiongroup.cpp | ActionGroup::toBiasString | 原文件第44-57行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
44: QString ActionGroup::toBiasString(int bias[]){
45: 
46:     QString s;
47:     //s.append(QString("{G%1").arg(index));
48:     s.sprintf("{G%04d", index);
49:     for(int i =0;i < MAX_STEER_NUM;i ++){
50:         if(itemList[i].Enable() && itemList[i].Changed()){
51:             QString temp = itemList[i].toBiasString(bias[i]);
52:             s.append(temp);
53:         }
54:     }
55:     s.append("}");
56:     return s;
57: }
```

## actiongroup.cpp | ActionGroup::toBiasString | 原文件第58-58行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
58: 
```

## actiongroup.cpp | ActionGroup::toNoBiasString | 原文件第59-74行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
59: QString ActionGroup::toNoBiasString(){
60: 
61:     QString s;
62:     //s.append(QString("{G%1").arg(index));
63:     s.sprintf("{G%04d", index);
64:     for(int i =0;i < MAX_STEER_NUM;i ++){
65:         if(itemList[i].Enable() && itemList[i].Changed()){
66:             QString temp = itemList[i].toNoBiasString();
67:             s.append(temp);
68:         }
69:     }
70:     s.append("}");
71:     return s;
72: }
73: 
74: 
```

## actiongroup.cpp | ActionGroup::toDisString | 原文件第75-85行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
75: QString ActionGroup::toDisString(){
76: 
77:     QString s;
78:     //s.append(QString("{G%1").arg(index));
79:     s.sprintf("{G%04d", index);
80:     for(int i =0;i < MAX_STEER_NUM;i ++){
81:         if(itemList[i].Pwm() ==0 && itemList[i].Time()==0){
82:         } else {
83:             if(itemList[i].Enable()) {
84:                 QString temp = itemList[i].toNoBiasString();
85:                 s.append(temp);
```

## actiongroup.cpp | ActionGroup::toDisString | 原文件第86-92行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
86:             }
87:         }
88:     }
89:     s.append("}");
90:     return s;
91: }
92: 
```

## actiongroup.cpp | ActionGroup::toStoreString | 原文件第93-106行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
93: QString ActionGroup::toStoreString(){
94: 
95:     QString s;
96:     s.sprintf("{G%04d", index);
97:     for(int i =0;i < MAX_STEER_NUM;i ++){
98:         //if(itemList[i].Enable() && itemList[i].Changed()){
99:             QString temp = itemList[i].toNoBiasString();
100:             s.append(temp);
101:         //}
102:     }
103:     s.append("}");
104:     return s;
105: }
106: 
```

## actiongroup.cpp | ActionGroup::toSaveString | 原文件第107-119行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
107: QString ActionGroup::toSaveString(int inc) {
108:     QString s;
109:     s.sprintf("<G%04d", index+inc);
110:     for(int i =0;i < MAX_STEER_NUM;i ++){
111:         if(itemList[i].Enable() && itemList[i].Changed()){
112:             QString temp = itemList[i].toNoBiasString();
113:             s.append(temp);
114:         }
115:     }
116:     s.append(">\r\n");
117:     return s;
118: }
119: 
```

## actiongroup.cpp | ActionGroup::toSaveBiasString | 原文件第120-132行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
120: QString ActionGroup::toSaveBiasString(int bias[], int inc) {
121:     QString s;
122:     s.sprintf("<G%04d", index+inc);
123:     for(int i =0;i < MAX_STEER_NUM;i ++){
124:         if(itemList[i].Enable() && itemList[i].Changed()){
125:             QString temp = itemList[i].toBiasString(bias[i]);
126:             s.append(temp);
127:         }
128:     }
129:     s.append(">\r\n");
130:     return s;
131: }
132: 
```

## actiongroup.cpp | ActionGroup::toDsiString | 原文件第133-145行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
133: QString ActionGroup::toDsiString() {
134:     QString s;
135:     s.append(QString("$DSI:"));
136:     for(int i =0;i < MAX_STEER_NUM;i ++){
137:         if(itemList[i].Enable() && itemList[i].Changed()){
138:             QString temp = itemList[i].toDsiString();
139:             s.append(temp);
140:         }
141:     }
142:     s.append("!");
143:     return s;
144: }
145: 
```

## actiongroup.cpp | ActionGroup::toDsiBiasString | 原文件第146-159行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
146: QString ActionGroup::toDsiBiasString(int bias[]) {
147:     QString s;
148:     s.append(QString("$DSI:"));
149:     for(int i =0;i < MAX_STEER_NUM;i ++){
150:         if(itemList[i].Enable() && itemList[i].Changed()){
151:             QString temp = itemList[i].toDsiBiasString(bias);
152:             s.append(temp);
153:         }
154:     }
155:     s.append("!");
156:     return s;
157: }
158: 
159: 
```

## actiongroup.cpp | ActionGroup::saveCmdString | 原文件第160-167行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
160: QString ActionGroup::saveCmdString() {
161:     QString s;
162:     s.sprintf("<G%04d", index);
163:     s.append(getCmdStr() + ">\r\n");
164:     return s;
165: }
166: 
167: 
```

## actiongroup.cpp | ActionGroup::addItem | 原文件第168-175行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
168: bool ActionGroup::addItem(ActionGroupItem &item, int index){
169:     if(index >= MAX_STEER_NUM){
170:         return false;
171:     }
172:     itemList[index] = item;
173:     return true;
174: }
175: 
```

## actiongroup.cpp | ActionGroup::removeItem | 原文件第176-180行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
176: bool ActionGroup::removeItem(int index){
177:     itemList[index].setEnable(false);
178:     return true;
179: }
180: 
```

## actiongroup.cpp | ActionGroup::removeItemAll | 原文件第181-187行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
181: void ActionGroup::removeItemAll(){
182:     for(int i=0; i<MAX_STEER_NUM; i++) {
183:        itemList[i].setEnable(false);
184:     }
185: }
186: 
187: 
```

## actiongroup.cpp | ActionGroup::getItem | 原文件第188-191行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
188: ActionGroupItem* ActionGroup::getItem(int index){
189:     return itemList+index;
190: }
191: 
```

## actiongroup.cpp | ActionGroup::setItem | 原文件第192-195行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
192: bool ActionGroup::setItem(int index, ActionGroupItem item) {
193:     itemList[index] = item;
194:     return true;
195: }
```

## actiongroup.cpp | ActionGroup::setItemEnable | 原文件第196-203行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
196: bool ActionGroup::setItemEnable(int index, bool enable) {
197:     itemList[index].setEnable(enable);
198: 
199: }
200: 
201: 
202: 
203: 
```

## actiongroup.cpp | ActionGroup::setIndex | 原文件第204-207行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
204: void ActionGroup::setIndex(int index_s) {
205:     index = index_s;
206: }
207: 
```

## actiongroup.cpp | ActionGroup::getIndex | 原文件第208-212行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
208: int ActionGroup::getIndex() {
209:     return index;
210: }
211: 
212: 
```

## actiongroup.cpp | ActionGroup::setDisperse | 原文件第213-216行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
213: void ActionGroup::setDisperse(bool flag){
214:     disperse = flag;
215: }
216: 
```

## actiongroup.cpp | ActionGroup::isDisperse | 原文件第217-221行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
217: bool ActionGroup::isDisperse(){
218:     return disperse;
219: }
220: 
221: 
```

## actiongroup.cpp | ActionGroup::setIsGroup | 原文件第222-225行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
222: void ActionGroup::setIsGroup(bool iss) {
223:     is_group = iss;
224: }
225: 
```

## actiongroup.cpp | ActionGroup::isGroup | 原文件第226-230行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
226: bool ActionGroup::isGroup(){
227:     return is_group;
228: }
229: 
230: 
```

## actiongroup.cpp | ActionGroup::setCmdStr | 原文件第231-243行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
231: void ActionGroup::setCmdStr(QString cmdStr) {
232:     int i;
233:     if(cmdStr.length() > 1024) {
234:         return;
235:     }
236:     QByteArray  byteArray = cmdStr.toLocal8Bit();
237:     for(i=0; i<cmdStr.length(); i++) {
238:         cmdCharArray[i] = byteArray.at(i);
239:     }
240:     cmdCharArray[i] = 0;
241:     return;
242: }
243: 
```

## actiongroup.cpp | ActionGroup::getCmdStr | 原文件第244-247行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
244: QString ActionGroup::getCmdStr() {
245:    return QString::fromLocal8Bit(cmdCharArray);
246: }
247: 
```

## actiongroup.cpp | ActionGroup::combineCmdStr | 原文件第248-253行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
248: QString ActionGroup::combineCmdStr() {
249:     QString s;
250:     s.sprintf("{G%04d", index);
251:     s.append(getCmdStr() + "}");
252:     return s;
253: }
```

## actiongroup.cpp | ActionGroup::combinePreCmdStr | 原文件第254-263行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.cpp
以下为原始源码，不是截图OCR。
```
254: QString ActionGroup::combinePreCmdStr() {
255:     QString s;
256:     s.append("<");
257:     s.append(getCmdStr() + ">");
258:     return s;
259: }
260: 
261: 
262: 
263: 
```

## actiongroup.h | 文件开头/全局定义 | 原文件第1-22行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.h
以下为原始源码，不是截图OCR。
```
1: #ifndef ACTIONGROUP_H
2: #define ACTIONGROUP_H
3: 
4: 
5: #include "actiongroupitem.h"
6: #include <qlist.h>
7: 
8: #define MAX_STEER_NUM   8
9: #define MAX_CMD_LEN    64
10: 
11: class ActionGroup
12: {
13: public:
14:     ActionGroup();
15:     ~ActionGroup();
16: 
17:     QString toDisString();
18:     QString toStoreString();
19: 
20:     QString toDsiString();
21:     QString toDsiBiasString(int bias[]);
22: 
```

## actiongroup.h | 文件开头/全局定义 | 原文件第23-37行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.h
以下为原始源码，不是截图OCR。
```
23:     QString toSaveString(int inc);
24:     QString toSaveBiasString(int bias[], int inc);
25: 
26:     QString toNoBiasString();
27:     QString toBiasString(int bias[]);
28: 
29:     void init();
30: 
31:     void setIndex(int index_s);
32:     int getIndex();
33: 
34:     //具体到某个item的ID号修改
35:     void setItemId(int index_s, int id_s);
36: 
37:     bool addItem(ActionGroupItem &item, int index);
```

## actiongroup.h | 文件开头/全局定义 | 原文件第38-52行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.h
以下为原始源码，不是截图OCR。
```
38:     bool removeItem(int index);
39:     void removeItemAll();
40: 
41:     ActionGroupItem* getItem(int index);
42:     bool setItem(int index, ActionGroupItem item);
43:     bool setItemEnable(int index, bool enable);
44: 
45:     void setDisperse(bool flag);
46:     bool isDisperse();
47: 
48:     void setIsGroup(bool iss);
49:     bool isGroup();
50: 
51:     void setCmdStr(QString);
52:     QString getCmdStr();
```

## actiongroup.h | 文件开头/全局定义 | 原文件第53-64行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.h
以下为原始源码，不是截图OCR。
```
53:     QString combineCmdStr();
54:     QString combinePreCmdStr();
55:     QString saveCmdString();
56: 
57: private:
58:     int index;                              //组序号
59:     bool disperse;                          //散组还是全组
60:     bool is_group;                          //是动作组还是命令
61:     char cmdCharArray[MAX_CMD_LEN];         //命令数组
62:     ActionGroupItem itemList[MAX_STEER_NUM]; //32个舵机item
63: };
64: 
```

## actiongroup.h | 文件开头/全局定义 | 原文件第65-65行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroup.h
以下为原始源码，不是截图OCR。
```
65: #endif // ACTIONGROUP_H
```

## actiongroupitem.cpp | 文件开头/全局定义 | 原文件第1-19行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.cpp
以下为原始源码，不是截图OCR。
```
1: #include "actiongroupitem.h"
2: #include <QList>
3: #include <QString>
4: #include <qregexp.h>
5: 
6: ActionGroupItem::ActionGroupItem():
7:     id(0),
8:     enable(false),
9:     bias(0)
10: {
11:     reset();
12: }
13: 
14: ActionGroupItem::ActionGroupItem(int index_s,int id_s,int ipwm,int itime,int ibias,bool ichanged):
15:     index(index_s),
16:     id(id_s),
17:     pwm(ipwm),
18:     time(itime),
19:     enable(false),
```

## actiongroupitem.cpp | 文件开头/全局定义 | 原文件第20-39行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.cpp
以下为原始源码，不是截图OCR。
```
20:     bias(ibias),
21:     changed(ichanged)
22: {
23: 
24: }
25: 
26: ActionGroupItem::ActionGroupItem(const char *str):
27:     id(0),
28:     enable(true)
29: {
30:     QString pattern("^#(.*)P(.+)T(.+)!$");
31:     QRegExp rx(pattern);
32: 
33:     QString myString = QString(str);
34:     int pos = myString.indexOf(rx);
35:     if(pos < 0){
36:         reset();
37:     }
38:     else {
39:         enable = true;
```

## actiongroupitem.cpp | 文件开头/全局定义 | 原文件第40-51行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.cpp
以下为原始源码，不是截图OCR。
```
40:         changed = true;
41:         id = rx.cap(1).toInt();
42:         pwm = rx.cap(2).toInt();
43:         time = rx.cap(3).toInt();
44:     }
45: }
46: 
47: ActionGroupItem::~ActionGroupItem()
48: {
49: 
50: }
51: 
```

## actiongroupitem.cpp | ActionGroupItem::setIndex | 原文件第52-55行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.cpp
以下为原始源码，不是截图OCR。
```
52: void ActionGroupItem::setIndex(int itemIndex){
53:     index = itemIndex;
54: }
55: 
```

## actiongroupitem.cpp | ActionGroupItem::getIndex | 原文件第56-59行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.cpp
以下为原始源码，不是截图OCR。
```
56: int ActionGroupItem::getIndex() {
57:     return index;
58: }
59: 
```

## actiongroupitem.cpp | ActionGroupItem::setId | 原文件第60-63行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.cpp
以下为原始源码，不是截图OCR。
```
60: void ActionGroupItem::setId(int itemId){
61:     id = itemId;
62: }
63: 
```

## actiongroupitem.cpp | ActionGroupItem::Id | 原文件第64-67行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.cpp
以下为原始源码，不是截图OCR。
```
64: int ActionGroupItem::Id(){
65:     return id;
66: }
67: 
```

## actiongroupitem.cpp | ActionGroupItem::setPwm | 原文件第68-71行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.cpp
以下为原始源码，不是截图OCR。
```
68: void ActionGroupItem::setPwm(int itemPwm){
69:     pwm = itemPwm;
70: }
71: 
```

## actiongroupitem.cpp | ActionGroupItem::Pwm | 原文件第72-75行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.cpp
以下为原始源码，不是截图OCR。
```
72: int ActionGroupItem::Pwm(){
73:     return pwm;
74: }
75: 
```

## actiongroupitem.cpp | ActionGroupItem::setTime | 原文件第76-79行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.cpp
以下为原始源码，不是截图OCR。
```
76: void ActionGroupItem::setTime(int itemTime){
77:     time = itemTime;
78: }
79: 
```

## actiongroupitem.cpp | ActionGroupItem::Time | 原文件第80-83行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.cpp
以下为原始源码，不是截图OCR。
```
80: int ActionGroupItem::Time(){
81:     return time;
82: }
83: 
```

## actiongroupitem.cpp | ActionGroupItem::setEnable | 原文件第84-87行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.cpp
以下为原始源码，不是截图OCR。
```
84: void ActionGroupItem::setEnable(bool itemEnable){
85:     enable = itemEnable;
86: }
87: 
```

## actiongroupitem.cpp | ActionGroupItem::Enable | 原文件第88-92行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.cpp
以下为原始源码，不是截图OCR。
```
88: bool ActionGroupItem::Enable(){
89:     return enable;
90: }
91: 
92: 
```

## actiongroupitem.cpp | ActionGroupItem::toBiasString | 原文件第93-98行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.cpp
以下为原始源码，不是截图OCR。
```
93: QString ActionGroupItem::toBiasString(int bias){
94:     QString s;
95:     s.sprintf("#%03dP%04dT%04d!", id, pwm + bias, time);
96:     return s;
97: }
98: 
```

## actiongroupitem.cpp | ActionGroupItem::toNoBiasString | 原文件第99-104行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.cpp
以下为原始源码，不是截图OCR。
```
99: QString ActionGroupItem::toNoBiasString(){
100:     QString s;
101:     s.sprintf("#%03dP%04dT%04d!", id, pwm, time);
102:     return s;
103: }
104: 
```

## actiongroupitem.cpp | ActionGroupItem::toDsiString | 原文件第105-109行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.cpp
以下为原始源码，不是截图OCR。
```
105: QString ActionGroupItem::toDsiString() {
106:     QString s = QString("#%1P%2T%3").arg(id).arg(pwm).arg(time);
107:     return s;
108: }
109: 
```

## actiongroupitem.cpp | ActionGroupItem::toDsiBiasString | 原文件第110-114行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.cpp
以下为原始源码，不是截图OCR。
```
110: QString ActionGroupItem::toDsiBiasString(int bias[]) {
111:     QString s = QString("#%1P%2T%3").arg(id).arg(pwm+bias[index]).arg(time);
112:     return s;
113: }
114: 
```

## actiongroupitem.cpp | ActionGroupItem::reset | 原文件第115-119行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.cpp
以下为原始源码，不是截图OCR。
```
115: void ActionGroupItem::reset(){
116:     pwm = 1500;
117:     time = 1000;
118: }
119: 
```

## actiongroupitem.cpp | ActionGroupItem::Bias | 原文件第120-123行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.cpp
以下为原始源码，不是截图OCR。
```
120: int ActionGroupItem::Bias(){
121:     return bias;
122: }
123: 
```

## actiongroupitem.cpp | ActionGroupItem::setBias | 原文件第124-127行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.cpp
以下为原始源码，不是截图OCR。
```
124: void ActionGroupItem::setBias(int itemBias){
125:     bias = itemBias;
126: }
127: 
```

## actiongroupitem.cpp | ActionGroupItem::setChanged | 原文件第128-131行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.cpp
以下为原始源码，不是截图OCR。
```
128: void ActionGroupItem::setChanged(bool itemChanged) {
129:     changed = itemChanged;
130: }
131: 
```

## actiongroupitem.cpp | ActionGroupItem::Changed | 原文件第132-134行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.cpp
以下为原始源码，不是截图OCR。
```
132: bool ActionGroupItem::Changed() {
133:     return changed;
134: }
```

## actiongroupitem.h | 文件开头/全局定义 | 原文件第1-19行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.h
以下为原始源码，不是截图OCR。
```
1: #ifndef ACTIONGROUPITEM_H
2: #define ACTIONGROUPITEM_H
3: 
4: #include <QDebug>
5: 
6: class QString;
7: 
8: 
9: class ActionGroupItem
10: {
11: public:
12:     ActionGroupItem();
13:     ActionGroupItem(int index_s, int id_s, int ipwm=1500,int itime=200,int ibias=0, bool changed=false);
14:     ActionGroupItem(const char *str);
15:     ~ActionGroupItem();
16: 
17:     void reset();
18: 
19:     void setIndex(int itemIndex);
```

## actiongroupitem.h | 文件开头/全局定义 | 原文件第20-39行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.h
以下为原始源码，不是截图OCR。
```
20:     int getIndex();
21: 
22:     void setId(int itemId);
23:     int Id();
24: 
25:     void setPwm(int itemPwm);
26:     int Pwm();
27: 
28:     void setTime(int itemTime);
29:     int Time();
30: 
31:     void setEnable(bool itemEnable);
32:     bool Enable();
33: 
34:     void setBias(int itemBias);
35:     int Bias();
36: 
37:     void setChanged(bool itemChanged);
38:     bool Changed();
39: 
```

## actiongroupitem.h | 文件开头/全局定义 | 原文件第40-58行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/actiongroupitem.h
以下为原始源码，不是截图OCR。
```
40:     QString toBiasString(int bias);
41:     //QString toBiasStringT(int bias[]);
42:     QString toNoBiasString();
43: 
44:     QString toDsiString();
45:     QString toDsiBiasString(int bias[]);
46: 
47: 
48: private:
49:     int index;
50:     int id;
51:     int pwm;
52:     int time;
53:     int bias;
54:     bool enable;
55:     bool changed;
56: };
57: 
58: #endif // ACTIONGROUPITEM_H
```

## dragwidget.cpp | 文件开头/全局定义 | 原文件第1-20行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/dragwidget.cpp
以下为原始源码，不是截图OCR。
```
1: #include "dragwidget.h"
2: 
3: #include <QWidget>
4: #include <QDragEnterEvent>
5: #include <QDropEvent>
6: #include <QDrag>
7: #include <QDebug>
8: #include <QMimeData>
9: #include "formsteerctl.h"
10: 
11: DragWidget::DragWidget(QWidget *parent) : QWidget(parent)
12: {
13:     setAcceptDrops(true);
14: }
15: 
16: DragWidget::~DragWidget()
17: {
18: 
19: }
20: 
```

## dragwidget.cpp | DragWidget::dragEnterEvent | 原文件第21-24行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/dragwidget.cpp
以下为原始源码，不是截图OCR。
```
21: void DragWidget::dragEnterEvent(QDragEnterEvent *e){
22:     e->acceptProposedAction();
23: }
24: 
```

## dragwidget.cpp | DragWidget::dropEvent | 原文件第25-33行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/dragwidget.cpp
以下为原始源码，不是截图OCR。
```
25: void DragWidget::dropEvent(QDropEvent *e){
26:     if(e->mimeData()->hasFormat("Drag-Steer")){
27:         QByteArray data = e->mimeData()->data("Drag-Steer");
28:         QDataStream stream(&data,QIODevice::ReadOnly);
29:         bool isenable;
30:         int myid,mypwm,mytime;
31:         QPoint offset;
32:         stream >> isenable >> myid >> mypwm >> mytime >> offset;
33: #if 0
```

## dragwidget.cpp | DragWidget::dropEvent | 原文件第34-43行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/dragwidget.cpp
以下为原始源码，不是截图OCR。
```
34:         qDebug() << "drag id " << myid <<endl;
35:         FormSteerCtl *steer = new FormSteerCtl(myid,this);
36:         steer->setEnabled(isenable);
37:         steer->setPwm(mypwm);
38:         steer->setTime(mytime);
39:         steer->move(e->pos() - offset);
40:         steer->show();
41:         steer->setAttribute(Qt::WA_DeleteOnClose);
42: #endif
43:         FormSteerCtl *s = static_cast <FormSteerCtl*>(e->source());
```

## dragwidget.cpp | DragWidget::dropEvent | 原文件第44-54行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/dragwidget.cpp
以下为原始源码，不是截图OCR。
```
44:         s->move(e->pos() - offset);
45:         s->show();
46:         if (children().contains(e->source())) {
47:             e->setDropAction(Qt::MoveAction);
48:             e->accept();
49:         }
50:         else  e->acceptProposedAction();
51:     }
52:     else e->ignore();
53:     emit clicked(this);
54: }
```

## dragwidget.h | 文件开头/全局定义 | 原文件第1-21行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/dragwidget.h
以下为原始源码，不是截图OCR。
```
1: #ifndef DRAGWIDGET_H
2: #define DRAGWIDGET_H
3: 
4: #include <QWidget>
5: 
6: class DragWidget : public QWidget
7: {
8:     Q_OBJECT
9: public:
10:     explicit DragWidget(QWidget *parent = 0);
11:     ~DragWidget();
12: 
13: signals:
14:     void clicked(DragWidget *dra);
15: 
16: protected:
17:     void dragEnterEvent(QDragEnterEvent *e);
18:     void dropEvent(QDropEvent *e);
19: };
20: 
21: #endif // DRAGWIDGET_H
```

## formsteerctl.cpp | 文件开头/全局定义 | 原文件第1-19行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
1: #include <QString>
2: #include "formsteerctl.h"
3: #include "ui_formsteerctl.h"
4: #include <QDataStream>
5: #include <QMouseEvent>
6: #include <QByteArray>
7: #include <QMimeData>
8: #include <QDrag>
9: #include <QDebug>
10: 
11: 
12: FormSteerCtl::FormSteerCtl(QWidget *parent) :
13:     QWidget(parent),
14:     ui(new Ui::FormSteerCtl)
15: {
16:     ui->setupUi(this);
17:     ui_init();
18: }
19: 
```

## formsteerctl.cpp | 文件开头/全局定义 | 原文件第20-36行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
20: FormSteerCtl::FormSteerCtl(int index_s, int id_s,QWidget *parent) :
21:     QWidget(parent),
22:     ui(new Ui::FormSteerCtl),
23:     index(index_s),
24:     id(id_s)
25: {
26:     menu = MENU_DEFAUL;
27:     pbtnSendClicked = true;
28:     id_old = 0;
29:     menu_old = menu;
30:     signalLose = false;
31:     emitStart = true;
32:     moveable = true;
33:     ui->setupUi(this);
34:     ui_init();
35: }
36: 
```

## formsteerctl.cpp | 文件开头/全局定义 | 原文件第37-41行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
37: FormSteerCtl::~FormSteerCtl()
38: {
39:     delete ui;
40: }
41: 
```

## formsteerctl.cpp | FormSteerCtl::ui_init | 原文件第42-56行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
42: void FormSteerCtl::ui_init(){
43:     //初始化界面
44:     //ui->labDjIndex->hide();
45: 
46:     pmin_click = false;
47:     pmax_click = false;
48:     pwm_changed = false;
49:     time_changed = false;
50:     bias_changed = false;
51: 
52:     ui->cmbMenu->clear();
53:     ui->cmbMenu->addItem("ID号");
54:     ui->cmbMenu->addItem("模式");
55:     //ui->cmbMenu->addItem("读角");
56:     ui->cmbMenu->addItem("释力");
```

## formsteerctl.cpp | FormSteerCtl::ui_init | 原文件第57-71行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
57:     ui->cmbMenu->addItem("中值");
58:     ui->cmbMenu->addItem("出厂");
59:     ui->cmbMenu->addItem("版本");
60:     ui->cmbMenu->addItem("测试");
61: 
62:     ui->cmbDjId->clear();
63:     for(int i=0;i<10;i++) {
64:         ui->cmbDjId->addItem("00" + QString::number(i));
65:     }
66: 
67:     for(int i=10;i<100;i++) {
68:         ui->cmbDjId->addItem("0" + QString::number(i));
69:     }
70: 
71:     for(int i=100;i<255;i++) {
```

## formsteerctl.cpp | FormSteerCtl::ui_init | 原文件第72-83行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
72:         ui->cmbDjId->addItem(QString::number(i));
73:     }
74: 
75:     if(id>255 || id < 0)id = 0;
76:     ui->cmbDjId->setCurrentIndex(id);
77:     ui->spbxTime->setValue(1000);
78:     ui->spbxPwm->setValue(1500);
79:     ui->spbxBias->setValue(0);
80:     ui->spbxPmin->setValue(500);
81:     ui->spbxPmax->setValue(2500);
82:     ui->hsdPwm->setRange(500,2500);
83:     ui->spbxPwm->setRange(500,2500);
```

## formsteerctl.cpp | FormSteerCtl::ui_init | 原文件第84-94行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
84:     ui->spbxTime->setRange(0,9999);
85:     ui->spbxBias->setRange(-100,100);
86:     ui->spbxPmin->setRange(500,1500);
87:     ui->spbxPmax->setRange(1500,2500);
88: 
89:     ui->pbtnPwm->setEnabled(true);
90:     ui->pbtnTime->setEnabled(true);
91:     ui->pbtnBias->setEnabled(true);
92:     ui->pbtnPmin->setEnabled(true);
93:     ui->pbtnPmax->setEnabled(true);
94:     ui->hsdPwm->setEnabled(true);
```

## formsteerctl.cpp | FormSteerCtl::ui_init | 原文件第95-105行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
95:     ui->spbxPwm->setEnabled(true);
96:     ui->spbxTime->setEnabled(true);
97:     ui->spbxBias->setEnabled(true);
98:     ui->spbxPmin->setEnabled(true);
99:     ui->spbxPmax->setEnabled(true);
100:     ui->edtDjTitle->setEnabled(false);
101: 
102:     connect(ui->pbtnSend,SIGNAL(clicked()),this,SLOT(pbtnSend_clicked()));
103: 
104:     //绑定事件
105:     connect(ui->pbtnTime,SIGNAL(clicked()),this,SLOT(pbtnTime_clicked()));
```

## formsteerctl.cpp | FormSteerCtl::ui_init | 原文件第106-110行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
106:     connect(ui->pbtnBias,SIGNAL(clicked()),this,SLOT(pbtnBias_clicked()));
107:     connect(ui->pbtnPwm,SIGNAL(clicked()),this,SLOT(pbtnPwm_clicked()));
108:     connect(ui->pbtnPmin,SIGNAL(clicked()),this,SLOT(pbtnPmin_clicked()));
109:     connect(ui->pbtnPmax,SIGNAL(clicked()),this,SLOT(pbtnPmax_clicked()));
110:     connect(ui->hsdPwm,SIGNAL(valueChanged(int)),this,SLOT(hsdPwm_valueChanged()));
```

## formsteerctl.cpp | FormSteerCtl::ui_init | 原文件第111-114行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
111:     connect(ui->spbxPwm,SIGNAL(valueChanged(int)),this,SLOT(spbxPwm_valueChanged()));
112:     connect(ui->spbxTime,SIGNAL(valueChanged(int)),this,SLOT(spbxTime_valueChanged()));
113:     connect(ui->spbxBias,SIGNAL(valueChanged(int)),this,SLOT(spbxBias_valueChanged()));
114:     connect(ui->spbxPmin,SIGNAL(valueChanged(int)),this,SLOT(spbxPmin_valueChanged()));
```

## formsteerctl.cpp | FormSteerCtl::ui_init | 原文件第115-121行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
115:     connect(ui->spbxPmax,SIGNAL(valueChanged(int)),this,SLOT(spbxPmax_valueChanged()));
116: 
117: 
118: 
119:     connect(ui->tobnClose,SIGNAL(clicked()),this,SLOT(tobnClose_clicked()));
120:     //connect(ui->djIndex,SIGNAL(doubleClicked()),this,SLOT(djIndex_doubleClicked()));
121:     connect(ui->cmbDjId, SIGNAL(currentIndexChanged(int)), this, SLOT(cmbDjId_currentIndexChanged()));
```

## formsteerctl.cpp | FormSteerCtl::ui_init | 原文件第122-131行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
122:     connect(ui->cmbMenu, SIGNAL(currentIndexChanged(int)), this, SLOT(cmbMenu_currentIndexChanged()));
123: 
124:     setTitleEnable(false);
125:     setcmbDjIdEnable(false);
126:     setcmbMenuEnable(false);
127: 
128: }
129: 
130: //slots
131: 
```

## formsteerctl.cpp | FormSteerCtl::tobnClose_clicked | 原文件第132-135行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
132: void FormSteerCtl::tobnClose_clicked(){
133:     setSeed(false);
134: }
135: 
```

## formsteerctl.cpp | FormSteerCtl::cmbDjId_currentIndexChanged | 原文件第136-142行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
136: void FormSteerCtl::cmbDjId_currentIndexChanged() {
137:     if(signalLose)return;
138:     qDebug() <<  "function:cmbDjId_currentIndexChanged";
139:     id = ui->cmbDjId->currentIndex();
140:     emit currentIndexChanged(this);
141: }
142: 
```

## formsteerctl.cpp | FormSteerCtl::setCmbDjIdIndex | 原文件第143-146行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
143: void FormSteerCtl::setCmbDjIdIndex(int val) {
144:     ui->cmbDjId->setCurrentIndex(val);
145: }
146: 
```

## formsteerctl.cpp | spbxClearFocus | 原文件第147-153行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
147: void FormSteerCtl:: spbxClearFocus() {
148: //    ui->spbxPwm->setStyleSheet("background-color: rgb(0, 139, 255);"
149: //                               "border-radius:5px;"
150: //                               "color: rgb(255, 255, 255);"
151: //                               "selection-background-color: rgb(0, 139, 255);");
152: //    ui->spbxPwm->setValue(ui->spbxPwm->value());
153: //    ui->spbxPwm->clearFocus();
```

## formsteerctl.cpp | spbxClearFocus | 原文件第154-157行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
154: //    ui->spbxTime->lineEdit()->deselect();
155: //    ui->spbxBias->lineEdit()->deselect();
156: }
157: 
```

## formsteerctl.cpp | FormSteerCtl::setBiasEnable | 原文件第158-166行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
158: void FormSteerCtl::setBiasEnable(bool enable) {
159:     ui->spbxBias->setEnabled(enable);
160:     ui->pbtnBias->setEnabled(enable);
161:     ui->pbtnPwm->setEnabled(!enable);
162:     ui->spbxPwm->setEnabled(!enable);
163:     ui->hsdPwm->setEnabled(!enable);
164:     ui->pbtnTime->setEnabled(!enable);
165:     ui->spbxTime->setEnabled(!enable);
166:     ui->pbtnPmin->setEnabled(!enable);
```

## formsteerctl.cpp | FormSteerCtl::setBiasEnable | 原文件第167-175行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
167:     ui->pbtnPmax->setEnabled(!enable);
168:     ui->spbxPmin->setEnabled(!enable);
169:     ui->spbxPmax->setEnabled(!enable);
170: 
171:     if(enable) {
172:         ui->spbxBias->setStyleSheet(
173:                                     "background-color: rgb(0, 139, 255);"
174:                                     "border-radius:5px;"
175:                                     "color: rgb(255, 255, 255);"
```

## formsteerctl.cpp | FormSteerCtl::setBiasEnable | 原文件第176-182行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
176:                                    );
177:         ui->spbxPwm->setStyleSheet(
178:                                     "background-color: rgb(226, 226, 231);"
179:                                     "border-radius:5px;"
180:                                     "color: rgb(255, 255, 255);"
181:                                    );
182:         ui->spbxTime->setStyleSheet(
```

## formsteerctl.cpp | FormSteerCtl::setBiasEnable | 原文件第183-189行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
183:                                     "background-color: rgb(226, 226, 231);"
184:                                     "border-radius:5px;"
185:                                     "color: rgb(255, 255, 255);"
186:                                    );
187:     } else {
188:         ui->spbxBias->setStyleSheet(
189:                                     "background-color: rgb(226, 226, 231);"
```

## formsteerctl.cpp | FormSteerCtl::setBiasEnable | 原文件第190-196行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
190:                                     "border-radius:5px;"
191:                                     "color: rgb(255, 255, 255);"
192:                                     );
193:         ui->spbxPwm->setStyleSheet(
194:                                     "background-color: rgb(0, 139, 255);"
195:                                     "border-radius:5px;"
196:                                     "color: rgb(255, 255, 255);"
```

## formsteerctl.cpp | FormSteerCtl::setBiasEnable | 原文件第197-205行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
197:                                    );
198:         ui->spbxTime->setStyleSheet(
199:                                     "background-color: rgb(0, 139, 255);"
200:                                     "border-radius:5px;"
201:                                     "color: rgb(255, 255, 255);"
202:                                    );
203:     }
204: }
205: 
```

## formsteerctl.cpp | FormSteerCtl::setPwmStyle | 原文件第206-209行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
206: void FormSteerCtl::setPwmStyle(QString str) {
207:     ui->spbxPwm->setStyleSheet(ui->spbxPwm->styleSheet()+str);
208: }
209: 
```

## formsteerctl.cpp | FormSteerCtl::setTimeStyle | 原文件第210-213行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
210: void FormSteerCtl::setTimeStyle(QString str) {
211:     ui->spbxTime->setStyleSheet(ui->spbxTime->styleSheet()+str);
212: }
213: 
```

## formsteerctl.cpp | FormSteerCtl::setBiasStyle | 原文件第214-217行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
214: void FormSteerCtl::setBiasStyle(QString str) {
215:     ui->spbxBias->setStyleSheet(ui->spbxBias->styleSheet()+str);
216: }
217: 
```

## formsteerctl.cpp | FormSteerCtl::createCmbDjIdIndexPid | 原文件第218-227行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
218: void FormSteerCtl::createCmbDjIdIndexPid(int index) {
219:     ui->pbtnSend->setText("R");
220:     ui->cmbDjId->show();
221:     ui->cmbDjId->setStyleSheet("font: 75 12pt 楷体;color: rgb(255, 255, 255);");
222:     ui->cmbDjId->clear();
223:     for(int i=0;i<10;i++) {
224:         ui->cmbDjId->addItem("00" + QString::number(i));
225:     }
226: 
227:     for(int i=10;i<100;i++) {
```

## formsteerctl.cpp | FormSteerCtl::createCmbDjIdIndexPid | 原文件第228-236行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
228:         ui->cmbDjId->addItem("0" + QString::number(i));
229:     }
230: 
231:     for(int i=100;i<=255;i++) {
232:         ui->cmbDjId->addItem(QString::number(i));
233:     }
234:     ui->cmbDjId->setCurrentIndex(index);
235: }
236: 
```

## formsteerctl.cpp | FormSteerCtl::setCmbMenuIndex | 原文件第237-241行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
237: void FormSteerCtl::setCmbMenuIndex(int val) {
238:     ui->cmbMenu->setCurrentIndex(val);
239: }
240: 
241: 
```

## formsteerctl.cpp | FormSteerCtl::cmbMenu_currentIndexChanged | 原文件第242-252行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
242: void FormSteerCtl::cmbMenu_currentIndexChanged() {
243:     menu = ui->cmbMenu->currentIndex();
244:     if(signalLose)return;
245: 
246:     qDebug() <<  "cmbMenu_currentIndexChanged";
247:     signalLose = true;
248: 
249:     if(menu == MENU_PID) {
250:         menu_old = menu;
251:         ui->pbtnSend->setText("R");
252:         ui->cmbDjId->show();
```

## formsteerctl.cpp | FormSteerCtl::cmbMenu_currentIndexChanged | 原文件第253-263行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
253:         ui->cmbDjId->setStyleSheet("font: 75 12pt 楷体;color: rgb(255, 255, 255);");
254:         ui->cmbDjId->clear();
255:         for(int i=0;i<10;i++) {
256:             ui->cmbDjId->addItem("00" + QString::number(i));
257:         }
258: 
259:         for(int i=10;i<100;i++) {
260:             ui->cmbDjId->addItem("0" + QString::number(i));
261:         }
262: 
263:         for(int i=100;i<=255;i++) {
```

## formsteerctl.cpp | FormSteerCtl::cmbMenu_currentIndexChanged | 原文件第264-272行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
264:             ui->cmbDjId->addItem(QString::number(i));
265:         }
266:         ui->cmbDjId->setCurrentIndex(id_old);
267:     /*} else if(menu == MENU_PBD) {
268:         ui->pbtnSend->setText("W");
269:         ui->cmbDjId->show();
270:         ui->cmbDjId->clear();
271:         ui->cmbDjId->setStyleSheet("font: 75 8pt 楷体;color: rgb(255, 255, 255);");
272:         ui->cmbDjId->addItem("9600");
```

## formsteerctl.cpp | FormSteerCtl::cmbMenu_currentIndexChanged | 原文件第273-282行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
273:         ui->cmbDjId->addItem("19200");
274:         ui->cmbDjId->addItem("38400");
275:         ui->cmbDjId->addItem("57600");
276:         ui->cmbDjId->addItem("115200");
277:         ui->cmbDjId->addItem("128000");*/
278:     } else if(menu == MENU_PMOD) {
279:         if(menu_old == MENU_PID)id_old = id;
280:         menu_old = menu;
281:         ui->pbtnSend->setText("W");
282:         ui->cmbDjId->show();
```

## formsteerctl.cpp | FormSteerCtl::cmbMenu_currentIndexChanged | 原文件第283-291行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
283:         ui->cmbDjId->clear();
284:         ui->cmbDjId->setStyleSheet("font: 75 8pt 楷体;color: rgb(255, 255, 255);");
285:         ui->cmbDjId->addItem("270度");
286:         ui->cmbDjId->addItem("180度");
287:         ui->cmbDjId->addItem("360定圈");
288:         ui->cmbDjId->addItem("360定时");
289: //    } else if(menu == MENU_PRAD) {
290: //        ui->pbtnSend->setText("R");
291: //        ui->cmbDjId->clear();
```

## formsteerctl.cpp | FormSteerCtl::cmbMenu_currentIndexChanged | 原文件第292-299行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
292: //        ui->cmbDjId->setStyleSheet("font: 75 8pt 楷体;color: rgb(255, 255, 255);");
293: //        ui->cmbDjId->addItem("读角度");
294: //        ui->cmbDjId->hide();
295:     } else if(menu == MENU_PULK) {
296:         if(menu_old == MENU_PID)id_old = id;
297:         menu_old = menu;
298:         ui->pbtnSend->setText("W");
299:         ui->cmbDjId->clear();
```

## formsteerctl.cpp | FormSteerCtl::cmbMenu_currentIndexChanged | 原文件第300-307行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
300:         ui->cmbDjId->setStyleSheet("font: 75 8pt 楷体;color: rgb(255, 255, 255);");
301:         ui->cmbDjId->addItem("释放扭力");
302:         ui->cmbDjId->hide();
303:     } else if(menu == MENU_PCSD) {
304:         if(menu_old == MENU_PID)id_old = id;
305:         menu_old = menu;
306:         ui->pbtnSend->setText("W");
307:         ui->cmbDjId->clear();
```

## formsteerctl.cpp | FormSteerCtl::cmbMenu_currentIndexChanged | 原文件第308-315行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
308:         ui->cmbDjId->setStyleSheet("font: 75 8pt 楷体;color: rgb(255, 255, 255);");
309:         ui->cmbDjId->addItem("设置中值");
310:         ui->cmbDjId->hide();
311:     } else if(menu == MENU_PCLE) {
312:         if(menu_old == MENU_PID)id_old = id;
313:         menu_old = menu;
314:         ui->pbtnSend->setText("W");
315:         ui->cmbDjId->clear();
```

## formsteerctl.cpp | FormSteerCtl::cmbMenu_currentIndexChanged | 原文件第316-323行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
316:         ui->cmbDjId->setStyleSheet("font: 75 8pt 楷体;color: rgb(255, 255, 255);");
317:         ui->cmbDjId->addItem("恢复出厂");
318:         ui->cmbDjId->hide();
319:     } else if(menu == MENU_PVER) {
320:         if(menu_old == MENU_PID)id_old = id;
321:         menu_old = menu;
322:         ui->pbtnSend->setText("R");
323:         ui->cmbDjId->clear();
```

## formsteerctl.cpp | FormSteerCtl::cmbMenu_currentIndexChanged | 原文件第324-331行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
324:         ui->cmbDjId->setStyleSheet("font: 75 8pt 楷体;color: rgb(255, 255, 255);");
325:         ui->cmbDjId->addItem("读取版本");
326:         ui->cmbDjId->hide();
327:     } else if(menu == MENU_PAT) {
328:         if(menu_old == MENU_PID)id_old = id;
329:         menu_old = menu;
330:         ui->pbtnSend->setText("W");
331:         ui->cmbDjId->clear();
```

## formsteerctl.cpp | FormSteerCtl::cmbMenu_currentIndexChanged | 原文件第332-339行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
332:         ui->cmbDjId->setStyleSheet("font: 75 8pt 楷体;color: rgb(255, 255, 255);");
333:         ui->cmbDjId->addItem("读取版本");
334:         ui->cmbDjId->hide();
335:     }
336:     signalLose = false;
337:     //emit currentIndexChanged(this);
338: }
339: 
```

## formsteerctl.cpp | FormSteerCtl::pbtnPwm_clicked | 原文件第340-346行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
340: void FormSteerCtl::pbtnPwm_clicked(){
341:     ui->spbxPwm->setValue(1500);
342:     ui->hsdPwm->setValue(1500);
343:     //ui->spbxPwm->setValue(1500 - ui->spbxBias->value());
344:     //ui->hsdPwm->setValue(1500 - ui->spbxBias->value());
345: }
346: 
```

## formsteerctl.cpp | FormSteerCtl::pbtnTime_clicked | 原文件第347-350行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
347: void FormSteerCtl::pbtnTime_clicked(){
348:     ui->spbxTime->setValue(1000);
349: }
350: 
```

## formsteerctl.cpp | FormSteerCtl::pbtnBias_clicked | 原文件第351-354行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
351: void FormSteerCtl::pbtnBias_clicked(){
352:     ui->spbxBias->setValue(0);
353: }
354: 
```

## formsteerctl.cpp | FormSteerCtl::pbtnPmin_clicked | 原文件第355-364行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
355: void FormSteerCtl::pbtnPmin_clicked() {
356:     pmin_click = true;
357:     ui->spbxPmin->setValue(ui->hsdPwm->value());
358:     emit clicked(this);
359:    //ui->spbxPmin->setValue(500);
360:    //ui->spbxPwm->setRange(ui->spbxPmin->value(), ui->spbxPmax->value());
361:    //ui->hsdPwm->setRange(ui->spbxPmin->value(), ui->spbxPmax->value());
362: 
363: 
364: }
```

## formsteerctl.cpp | FormSteerCtl::pbtnPmax_clicked | 原文件第365-373行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
365: void FormSteerCtl::pbtnPmax_clicked() {
366:     pmax_click = true;
367:     ui->spbxPmax->setValue(ui->hsdPwm->value());
368:     emit clicked(this);
369:     //ui->spbxPmax->setValue(2500);
370:     //ui->spbxPwm->setRange(ui->spbxPmin->value(), ui->spbxPmax->value());
371:     //ui->hsdPwm->setRange(ui->spbxPmin->value(), ui->spbxPmax->value());
372: }
373: 
```

## formsteerctl.cpp | FormSteerCtl::hsdPwm_valueChanged | 原文件第374-381行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
374: void FormSteerCtl::hsdPwm_valueChanged() {
375:     //qDebug() << "FormSteerCtl::spbxPwm_valueChanged";
376:     if(ui->hsdPwm->value()+ui->spbxBias->value() > 2500){
377:         ui->hsdPwm->setValue(2500 - ui->spbxBias->value());
378:     } else if(ui->hsdPwm->value()+ui->spbxBias->value() < 500){
379:         ui->hsdPwm->setValue(500 - ui->spbxBias->value());
380:     }
381:     ui->spbxPwm->setValue(ui->hsdPwm->value());
```

## formsteerctl.cpp | FormSteerCtl::hsdPwm_valueChanged | 原文件第382-386行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
382:     ui->spbxPwm->selectAll();
383:     pwm_changed = true;
384:     if(emitStart)emit valueChanged(this);
385: }
386: 
```

## formsteerctl.cpp | FormSteerCtl::spbxPwm_valueChanged | 原文件第387-394行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
387: void FormSteerCtl::spbxPwm_valueChanged(){
388:     //qDebug() << "FormSteerCtl::spbxPwm_valueChanged";
389:     if(ui->spbxPwm->value()+ui->spbxBias->value() > 2500){
390:         ui->spbxPwm->setValue(2500 - ui->spbxBias->value());
391:     } else if(ui->spbxPwm->value()+ui->spbxBias->value() < 500){
392:         ui->spbxPwm->setValue(500 - ui->spbxBias->value());
393:     }
394:     ui->hsdPwm->setValue(ui->spbxPwm->value());
```

## formsteerctl.cpp | FormSteerCtl::spbxPwm_valueChanged | 原文件第395-399行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
395:     ui->spbxPwm->selectAll();
396:     pwm_changed = true;
397:     if(emitStart)emit valueChanged(this);
398: }
399: 
```

## formsteerctl.cpp | FormSteerCtl::spbxTime_valueChanged | 原文件第400-405行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
400: void FormSteerCtl::spbxTime_valueChanged(){
401:     //qDebug() << "FormSteerCtl::spbxTime_valueChanged";
402:     time_changed = true;
403:     if(emitStart)emit valueChanged(this);
404: }
405: 
```

## formsteerctl.cpp | FormSteerCtl::spbxBias_valueChanged | 原文件第406-411行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
406: void FormSteerCtl::spbxBias_valueChanged(){
407:     //qDebug() << "FormSteerCtl::spbxBias_valueChanged";
408:     bias_changed = true;
409:     if(emitStart)emit valueChanged(this);
410: }
411: 
```

## formsteerctl.cpp | FormSteerCtl::spbxPmin_valueChanged | 原文件第412-421行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
412: void FormSteerCtl::spbxPmin_valueChanged() {
413:     if(ui->spbxPmin->value() > ui->spbxPmax->value()) {
414:         ui->spbxPmin->setValue(ui->spbxPmax->value());
415:         return;
416:     }
417:     ui->spbxPwm->setRange(ui->spbxPmin->value(), ui->spbxPmax->value());
418:     ui->hsdPwm->setRange(ui->spbxPmin->value(), ui->spbxPmax->value());
419:     //qDebug() << "Pmin BOX";
420:     //emit valueChanged(this);
421: 
```

## formsteerctl.cpp | FormSteerCtl::spbxPmin_valueChanged | 原文件第422-422行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
422: }
```

## formsteerctl.cpp | FormSteerCtl::spbxPmax_valueChanged | 原文件第423-432行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
423: void FormSteerCtl::spbxPmax_valueChanged() {
424:     if(ui->spbxPmin->value() > ui->spbxPmax->value()) {
425:         ui->spbxPmax->setValue(ui->spbxPmin->value());
426:         return;
427:     }
428:     ui->spbxPwm->setRange(ui->spbxPmin->value(), ui->spbxPmax->value());
429:     ui->hsdPwm->setRange(ui->spbxPmin->value(), ui->spbxPmax->value());
430:     //qDebug() << "Pmax BOX";
431:     //emit valueChanged(this);
432: }
```

## formsteerctl.cpp | FormSteerCtl::spbxPmax_valueChanged | 原文件第433-434行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
433: 
434: //方法
```

## formsteerctl.cpp | FormSteerCtl::getPwm | 原文件第435-438行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
435: int FormSteerCtl::getPwm(){
436:     return ui->spbxPwm->value();
437: }
438: 
```

## formsteerctl.cpp | FormSteerCtl::getTime | 原文件第439-442行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
439: int FormSteerCtl::getTime(){
440:     return ui->spbxTime->value();
441: }
442: 
```

## formsteerctl.cpp | FormSteerCtl::getBias | 原文件第443-446行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
443: int FormSteerCtl::getBias(){
444:     return ui->spbxBias->value();
445: }
446: 
```

## formsteerctl.cpp | FormSteerCtl::getPmin | 原文件第447-450行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
447: int FormSteerCtl::getPmin() {
448: 
449:     return ui->spbxPmin->value();
450: }
```

## formsteerctl.cpp | FormSteerCtl::getPmax | 原文件第451-454行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
451: int FormSteerCtl::getPmax() {
452:     return ui->spbxPmax->value();
453: }
454: 
```

## formsteerctl.cpp | FormSteerCtl::setId | 原文件第455-459行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
455: void FormSteerCtl::setId(int id_s){
456:     id = id_s;
457:     ui->cmbDjId->setCurrentIndex(id);
458: }
459: 
```

## formsteerctl.cpp | FormSteerCtl::getId | 原文件第460-464行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
460: int FormSteerCtl::getId(){
461:     id = ui->cmbDjId->currentIndex();
462:     return id;
463: }
464: 
```

## formsteerctl.cpp | FormSteerCtl::setIndex | 原文件第465-469行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
465: void FormSteerCtl::setIndex(int index_s) {
466:     index = index_s;
467:     ui->labIndex->setText(QString::number(index) + "号");
468: }
469: 
```

## formsteerctl.cpp | FormSteerCtl::getIndex | 原文件第470-473行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
470: int FormSteerCtl::getIndex() {
471:     return index;
472: }
473: 
```

## formsteerctl.cpp | FormSteerCtl::setTime | 原文件第474-477行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
474: void FormSteerCtl::setTime(int itime){
475:     ui->spbxTime->setValue(itime);
476: }
477: 
```

## formsteerctl.cpp | FormSteerCtl::setPwm | 原文件第478-482行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
478: void FormSteerCtl::setPwm(int ipwm){
479:     ui->spbxPwm->setValue(ipwm);
480:     ui->hsdPwm->setValue(ipwm);
481: }
482: 
```

## formsteerctl.cpp | FormSteerCtl::setPwmRange | 原文件第483-489行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
483: void FormSteerCtl::setPwmRange(int min, int max){
484:     ui->spbxPwm->setMinimum(min);
485:     ui->spbxPwm->setMaximum(max);
486:     ui->hsdPwm->setMinimum(min);
487:     ui->hsdPwm->setMaximum(max);
488: }
489: 
```

## formsteerctl.cpp | FormSteerCtl::setBias | 原文件第490-493行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
490: void FormSteerCtl::setBias(int ibias){
491:     ui->spbxBias->setValue(ibias);
492: }
493: 
```

## formsteerctl.cpp | FormSteerCtl::setPmin | 原文件第494-499行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
494: void FormSteerCtl::setPmin(int ipmin) {
495:     ui->spbxPmin->setValue(ipmin);
496:     ui->spbxPwm->setRange(ui->spbxPmin->value(), ui->spbxPmax->value());
497:     ui->hsdPwm->setRange(ui->spbxPmin->value(), ui->spbxPmax->value());
498: }
499: 
```

## formsteerctl.cpp | FormSteerCtl::setPmax | 原文件第500-505行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
500: void FormSteerCtl::setPmax(int ipmax) {
501:     ui->spbxPmax->setValue(ipmax);
502:     ui->spbxPwm->setRange(ui->spbxPmin->value(), ui->spbxPmax->value());
503:     ui->hsdPwm->setRange(ui->spbxPmin->value(), ui->spbxPmax->value());
504: }
505: 
```

## formsteerctl.cpp | FormSteerCtl::labLeft | 原文件第506-509行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
506: QString FormSteerCtl::labLeft() {
507:     return ui->labLeft->text();
508: }
509: 
```

## formsteerctl.cpp | FormSteerCtl::setlabLeft | 原文件第510-513行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
510: void FormSteerCtl::setlabLeft(QString str) {
511:     ui->labLeft->setText(str);
512: }
513: 
```

## formsteerctl.cpp | FormSteerCtl::labRight | 原文件第514-517行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
514: QString FormSteerCtl::labRight() {
515:     return ui->labRight->text();
516: }
517: 
```

## formsteerctl.cpp | FormSteerCtl::setlabRight | 原文件第518-521行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
518: void FormSteerCtl::setlabRight(QString str) {
519:     ui->labRight->setText(str);
520: }
521: 
```

## formsteerctl.cpp | FormSteerCtl::getTitle | 原文件第522-525行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
522: QString FormSteerCtl::getTitle() {
523:     return ui->edtDjTitle->text();
524: 
525: }
```

## formsteerctl.cpp | FormSteerCtl::setTitle | 原文件第526-529行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
526: void FormSteerCtl::setTitle(QString str) {
527:     ui->edtDjTitle->setText(str);
528: }
529: 
```

## formsteerctl.cpp | FormSteerCtl::setLableIndex | 原文件第530-533行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
530: void FormSteerCtl::setLableIndex(QString str) {
531:     ui->labIndex->setText(str);
532: }
533: 
```

## formsteerctl.cpp | FormSteerCtl::setTitleEnable | 原文件第534-537行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
534: void FormSteerCtl::setTitleEnable(bool enable) {
535:     ui->edtDjTitle->setEnabled(enable);
536: }
537: 
```

## formsteerctl.cpp | FormSteerCtl::setcmbDjIdEnable | 原文件第538-541行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
538: void FormSteerCtl::setcmbDjIdEnable(bool enable) {
539:     ui->cmbDjId->setEnabled(enable);
540: }
541: 
```

## formsteerctl.cpp | FormSteerCtl::setcmbMenuEnable | 原文件第542-545行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
542: void FormSteerCtl::setcmbMenuEnable(bool enable) {
543:     ui->cmbMenu->setEnabled(enable);
544: }
545: 
```

## formsteerctl.cpp | FormSteerCtl::setSeed | 原文件第546-553行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
546: void FormSteerCtl::setSeed(bool val) {
547:     isSeed = val;
548:     if(isSeed) {
549:         this->show();
550:     } else {
551:         this->hide();
552:     }
553: }
```

## formsteerctl.cpp | FormSteerCtl::getSeed | 原文件第554-557行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
554: bool FormSteerCtl::getSeed() {
555:     return isSeed;
556: }
557: 
```

## formsteerctl.cpp | FormSteerCtl::setJustClick | 原文件第558-560行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
558: void FormSteerCtl::setJustClick(bool iClick) {
559:     justClick = iClick;
560: }
```

## formsteerctl.cpp | FormSteerCtl::getJustClick | 原文件第561-564行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
561: bool FormSteerCtl::getJustClick() {
562:     return justClick;
563: }
564: 
```

## formsteerctl.cpp | FormSteerCtl::mousePressEvent | 原文件第565-578行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
565: void FormSteerCtl::mousePressEvent(QMouseEvent *e){
566: 
567:     if(!moveable)return;
568: 
569:     QPixmap pix;
570:     pix = pix.grabWidget(this);
571: 
572:     bool isenable = getSeed();
573:     int myid = getId();
574:     int mypwm = getPwm();
575:     int mytime = getTime();
576:     //int mybias = getBias();
577:     QByteArray data;
578:     QDataStream stream(&data,QIODevice::WriteOnly);
```

## formsteerctl.cpp | FormSteerCtl::mousePressEvent | 原文件第579-589行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
579:     stream << isenable << myid << mypwm << mytime << QPoint(e->pos()-rect().topLeft());
580:     QMimeData *mimeData = new QMimeData;
581:     mimeData->setData("Drag-Steer",data);
582: 
583:     QDrag *drag = new QDrag(this);
584:     drag->setMimeData(mimeData);
585:     drag->setHotSpot(QPoint(e->pos() - rect().topLeft()));
586:     drag->setPixmap(pix);
587: 
588:     hide();
589: 
```

## formsteerctl.cpp | FormSteerCtl::mousePressEvent | 原文件第590-600行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
590:     Qt::DropAction dropAction = drag->exec(Qt::CopyAction | Qt::MoveAction);
591: 
592:     if (dropAction == Qt::MoveAction){
593:         qDebug() <<"close " << endl;
594:         //close();
595:     }
596:     else
597:         show();
598: }
599: 
600: 
```

## formsteerctl.cpp | FormSteerCtl::getMenu | 原文件第601-605行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
601: int FormSteerCtl::getMenu(){
602:     menu = ui->cmbMenu->currentIndex();
603:     return menu;
604: }
605: 
```

## formsteerctl.cpp | FormSteerCtl::setMenu | 原文件第606-610行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
606: void FormSteerCtl::setMenu(int val){
607:     menu = val;
608:     ui->cmbMenu->setCurrentIndex(val);
609: }
610: 
```

## formsteerctl.cpp | FormSteerCtl::pbtnSend_clicked | 原文件第611-615行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
611: void FormSteerCtl::pbtnSend_clicked() {
612:     pbtnSendClicked = true;
613:     emit clicked(this);
614: }
615: 
```

## formsteerctl.cpp | FormSteerCtl::getPbtnSendClickedState | 原文件第616-619行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
616: bool FormSteerCtl::getPbtnSendClickedState() {
617:     return pbtnSendClicked;
618: }
619: 
```

## formsteerctl.cpp | FormSteerCtl::setPbtnSendClickedState | 原文件第620-624行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.cpp
以下为原始源码，不是截图OCR。
```
620: void FormSteerCtl::setPbtnSendClickedState(bool val) {
621:     pbtnSendClicked = val;
622: }
623: 
624: 
```

## formsteerctl.h | 文件开头/全局定义 | 原文件第1-10行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.h
以下为原始源码，不是截图OCR。
```
1: #ifndef FORMSTEERCTL_H
2: #define FORMSTEERCTL_H
3: 
4: #include <QWidget>
5: #include <QDebug>
6: 
7: #define MENU_PID    0   //ID设置                显示ID     命令：#1PID001!
8: //#define MENU_PBD    1   //波特率设置             显示BD     命令：#1PBD1!
9: #define MENU_PMOD   1   //模式设置               显示MO    命令：#1PMOD1!
10: //#define MENU_PRAD   2   //角度读取               显示AD    命令：#1PRAD!
```

## formsteerctl.h | 文件开头/全局定义 | 原文件第11-20行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.h
以下为原始源码，不是截图OCR。
```
11: #define MENU_PULK   2   //释放扭力               显示UK    命令：#1PULK!
12: #define MENU_PCSD   3   //设置当前值为中间位置     显示CS    命令：#1PCSD!
13: #define MENU_PCLE   4   //恢复出厂设置            显示LE     命令：#1PCLE!
14: #define MENU_PVER   5   //版本号读取              显示VR     命令：#1PVER!
15: #define MENU_PAT    6   //AT测试              显示AT     命令：#1PVER!
16: 
17: #define MENU_END    7
18: 
19: 
20: #define MENU_DEFAUL MENU_PID
```

## formsteerctl.h | 文件开头/全局定义 | 原文件第21-39行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.h
以下为原始源码，不是截图OCR。
```
21: #define MENU_START  MENU_PID
22: #define MENU_MAX    MENU_END
23: 
24: namespace Ui {
25: class FormSteerCtl;
26: }
27: 
28: class FormSteerCtl : public QWidget
29: {
30:     Q_OBJECT
31: 
32: public:
33:     explicit FormSteerCtl(QWidget *parent = 0);
34:     FormSteerCtl(int index_s, int id_s, QWidget *parent = 0);
35:     ~FormSteerCtl();
36: 
37:     void setIndex(int index_s);
38:     int getIndex();
39: 
```

## formsteerctl.h | 文件开头/全局定义 | 原文件第40-53行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.h
以下为原始源码，不是截图OCR。
```
40:     void setId(int id_s);
41:     int getId();
42:     void setPwm(int ipwm);
43:     void setPwmRange(int min, int max);
44:     int getPwm();
45:     void setTime(int itime);
46:     int getTime();
47:     void setBias(int ibias);
48:     int getBias();
49: 
50: //    void setSpbPwmStyle(QString str);
51: //    void setSpbBiasStyle(QString str);
52: //    void setSpbTimeStyle(QString str);
53: 
```

## formsteerctl.h | 文件开头/全局定义 | 原文件第54-70行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.h
以下为原始源码，不是截图OCR。
```
54:     void setJustClick(bool iClick);
55:     bool getJustClick();
56: 
57:     void setSeed(bool val);
58:     bool getSeed();
59: 
60:     QString labLeft();
61:     void setlabLeft(QString str);
62:     QString labRight();
63:     void setlabRight(QString str);
64: 
65: 
66:     QString getTitle();
67:     void setTitle(QString str);
68:     void setTitleEnable(bool enable);
69:     void setLableIndex(QString str);
70: 
```

## formsteerctl.h | 文件开头/全局定义 | 原文件第71-86行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.h
以下为原始源码，不是截图OCR。
```
71:     int getPmin();
72:     void setPmin(int ipmin);
73: 
74:     int getPmax();
75:     void setPmax(int ipmax);
76: 
77:     int getMenu();
78:     void setMenu(int val);
79: 
80:     bool getPbtnSendClickedState();
81:     void setPbtnSendClickedState(bool val);
82: 
83:     void setcmbDjIdEnable(bool enable);
84:     void setcmbMenuEnable(bool enable);
85: 
86:     void setCmbDjIdIndex(int val);
```

## formsteerctl.h | 文件开头/全局定义 | 原文件第87-102行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.h
以下为原始源码，不是截图OCR。
```
87:     void setCmbMenuIndex(int val);
88:     void createCmbDjIdIndexPid(int index);
89: 
90:     void setBiasEnable(bool enable);
91: 
92:     void spbxClearFocus();
93: 
94:     void setPwmStyle(QString str);
95:     void setTimeStyle(QString str);
96:     void setBiasStyle(QString str);
97: 
98: private:
99:     void ui_init();
100: 
101: signals:
102:     void clicked(FormSteerCtl *stc);
```

## formsteerctl.h | 文件开头/全局定义 | 原文件第103-120行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.h
以下为原始源码，不是截图OCR。
```
103:     void valueChanged(FormSteerCtl *stc);
104:     void currentIndexChanged(FormSteerCtl *stc);
105: 
106: protected:
107:     void mousePressEvent(QMouseEvent *e);
108: 
109: private:
110:     Ui::FormSteerCtl *ui;
111:     //QString title;
112:     int index;
113:     int id, id_old;
114:     int menu, menu_old;
115: 
116:     bool isSeed;
117:     bool justClick;
118:     bool pbtnSendClicked;
119: 
120:     bool menu_click;
```

## formsteerctl.h | 文件开头/全局定义 | 原文件第121-134行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.h
以下为原始源码，不是截图OCR。
```
121: 
122: public:
123:     bool signalLose;
124:     bool pmin_click, pmax_click;
125:     bool pwm_changed, time_changed, bias_changed;
126:     bool emitStart;
127:     bool moveable;
128:     //int  pwm_min, pwm_max;
129: 
130: private slots:
131:     void spbxPwm_valueChanged();
132:     void spbxTime_valueChanged();
133:     void spbxBias_valueChanged();
134:     void spbxPmin_valueChanged();
```

## formsteerctl.h | 文件开头/全局定义 | 原文件第135-147行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.h
以下为原始源码，不是截图OCR。
```
135:     void spbxPmax_valueChanged();
136:     void pbtnPwm_clicked();
137:     void pbtnTime_clicked();
138:     void pbtnBias_clicked();
139:     void pbtnPmin_clicked();
140:     void pbtnPmax_clicked();
141:     void pbtnSend_clicked();
142:     void tobnClose_clicked();
143:     void cmbDjId_currentIndexChanged();
144:     void cmbMenu_currentIndexChanged();
145:     void hsdPwm_valueChanged();
146: };
147: 
```

## formsteerctl.h | 文件开头/全局定义 | 原文件第148-148行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.h
以下为原始源码，不是截图OCR。
```
148: #endif // FORMSTEERCTL_H
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第1-16行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
1: <?xml version="1.0" encoding="UTF-8"?>
2: <ui version="4.0">
3:  <class>FormSteerCtl</class>
4:  <widget class="QWidget" name="FormSteerCtl">
5:   <property name="enabled">
6:    <bool>true</bool>
7:   </property>
8:   <property name="geometry">
9:    <rect>
10:     <x>0</x>
11:     <y>0</y>
12:     <width>180</width>
13:     <height>95</height>
14:    </rect>
15:   </property>
16:   <property name="windowTitle">
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第17-30行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
17:    <string>Form</string>
18:   </property>
19:   <property name="styleSheet">
20:    <string notr="true">background-color: rgba(255, 255, 255, 0);</string>
21:   </property>
22:   <widget class="QFrame" name="frame">
23:    <property name="enabled">
24:     <bool>true</bool>
25:    </property>
26:    <property name="geometry">
27:     <rect>
28:      <x>0</x>
29:      <y>0</y>
30:      <width>180</width>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第31-45行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
31:      <height>95</height>
32:     </rect>
33:    </property>
34:    <property name="styleSheet">
35:     <string notr="true">border-radius:5px;
36: background-color: rgb(255, 255, 255);</string>
37:    </property>
38:    <widget class="QSpinBox" name="spbxPwm">
39:     <property name="enabled">
40:      <bool>false</bool>
41:     </property>
42:     <property name="geometry">
43:      <rect>
44:       <x>125</x>
45:       <y>37</y>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第46-60行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
46:       <width>50</width>
47:       <height>20</height>
48:      </rect>
49:     </property>
50:     <property name="font">
51:      <font>
52:       <family>微软雅黑</family>
53:       <pointsize>8</pointsize>
54:       <weight>75</weight>
55:       <bold>true</bold>
56:      </font>
57:     </property>
58:     <property name="styleSheet">
59:      <string notr="true">background-color: rgb(0, 139, 255);
60: border-radius:5px;
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第61-76行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
61: color: rgb(255, 255, 255);
62: 
63: </string>
64:     </property>
65:     <property name="minimum">
66:      <number>500</number>
67:     </property>
68:     <property name="maximum">
69:      <number>2500</number>
70:     </property>
71:     <property name="value">
72:      <number>1500</number>
73:     </property>
74:    </widget>
75:    <widget class="QSpinBox" name="spbxTime">
76:     <property name="enabled">
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第77-93行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
77:      <bool>false</bool>
78:     </property>
79:     <property name="geometry">
80:      <rect>
81:       <x>125</x>
82:       <y>69</y>
83:       <width>50</width>
84:       <height>20</height>
85:      </rect>
86:     </property>
87:     <property name="font">
88:      <font>
89:       <family>微软雅黑</family>
90:       <pointsize>8</pointsize>
91:       <weight>75</weight>
92:       <bold>true</bold>
93:      </font>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第94-106行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
94:     </property>
95:     <property name="styleSheet">
96:      <string notr="true">background-color: rgb(0, 139, 255);
97: border-radius:5px;
98: color: rgb(255, 255, 255);</string>
99:     </property>
100:     <property name="maximum">
101:      <number>9999</number>
102:     </property>
103:     <property name="value">
104:      <number>500</number>
105:     </property>
106:    </widget>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第107-121行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
107:    <widget class="QPushButton" name="pbtnTime">
108:     <property name="enabled">
109:      <bool>false</bool>
110:     </property>
111:     <property name="geometry">
112:      <rect>
113:       <x>92</x>
114:       <y>69</y>
115:       <width>30</width>
116:       <height>20</height>
117:      </rect>
118:     </property>
119:     <property name="font">
120:      <font>
121:       <family>微软雅黑</family>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第122-134行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
122:       <pointsize>8</pointsize>
123:       <weight>75</weight>
124:       <italic>false</italic>
125:       <bold>true</bold>
126:      </font>
127:     </property>
128:     <property name="styleSheet">
129:      <string notr="true">background-color: rgb(227, 0, 122);
130: border-radius:5px;
131: color: rgb(255, 255, 255);</string>
132:     </property>
133:     <property name="text">
134:      <string>Time</string>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第135-150行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
135:     </property>
136:    </widget>
137:    <widget class="QPushButton" name="pbtnPwm">
138:     <property name="enabled">
139:      <bool>false</bool>
140:     </property>
141:     <property name="geometry">
142:      <rect>
143:       <x>4</x>
144:       <y>37</y>
145:       <width>30</width>
146:       <height>20</height>
147:      </rect>
148:     </property>
149:     <property name="font">
150:      <font>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第151-163行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
151:       <family>微软雅黑</family>
152:       <pointsize>7</pointsize>
153:       <weight>75</weight>
154:       <italic>false</italic>
155:       <bold>true</bold>
156:      </font>
157:     </property>
158:     <property name="styleSheet">
159:      <string notr="true">background-color: rgb(227, 0, 122);
160: border-radius:5px;
161: color: rgb(255, 255, 255);</string>
162:     </property>
163:     <property name="text">
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第164-179行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
164:      <string>PWM</string>
165:     </property>
166:    </widget>
167:    <widget class="QLabel" name="labIndex">
168:     <property name="geometry">
169:      <rect>
170:       <x>2</x>
171:       <y>2</y>
172:       <width>176</width>
173:       <height>28</height>
174:      </rect>
175:     </property>
176:     <property name="font">
177:      <font>
178:       <family>楷体</family>
179:       <pointsize>14</pointsize>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第180-192行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
180:       <weight>9</weight>
181:       <italic>false</italic>
182:       <bold>false</bold>
183:      </font>
184:     </property>
185:     <property name="styleSheet">
186:      <string notr="true">font: 75 14pt &quot;楷体&quot;;
187: color: rgb(255, 255, 255);
188: background-image: url(:/images/btn_bg2.png);</string>
189:     </property>
190:     <property name="text">
191:      <string>0号</string>
192:     </property>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第193-206行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
193:     <property name="alignment">
194:      <set>Qt::AlignCenter</set>
195:     </property>
196:    </widget>
197:    <widget class="QToolButton" name="tobnClose">
198:     <property name="geometry">
199:      <rect>
200:       <x>40</x>
201:       <y>9</y>
202:       <width>15</width>
203:       <height>15</height>
204:      </rect>
205:     </property>
206:     <property name="styleSheet">
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第207-220行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
207:      <string notr="true">image: url(:/images/close.png);</string>
208:     </property>
209:     <property name="text">
210:      <string/>
211:     </property>
212:    </widget>
213:    <widget class="QPushButton" name="pbtnBias">
214:     <property name="enabled">
215:      <bool>false</bool>
216:     </property>
217:     <property name="geometry">
218:      <rect>
219:       <x>4</x>
220:       <y>69</y>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第221-234行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
221:       <width>30</width>
222:       <height>20</height>
223:      </rect>
224:     </property>
225:     <property name="font">
226:      <font>
227:       <family>微软雅黑</family>
228:       <pointsize>8</pointsize>
229:       <weight>75</weight>
230:       <bold>true</bold>
231:      </font>
232:     </property>
233:     <property name="styleSheet">
234:      <string notr="true">background-color: rgb(227, 0, 122);
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第235-249行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
235: border-radius:5px;
236: color: rgb(255, 255, 255);</string>
237:     </property>
238:     <property name="text">
239:      <string>Bias</string>
240:     </property>
241:    </widget>
242:    <widget class="QPushButton" name="pbtnPmin">
243:     <property name="enabled">
244:      <bool>false</bool>
245:     </property>
246:     <property name="geometry">
247:      <rect>
248:       <x>42</x>
249:       <y>7</y>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第250-263行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
250:       <width>30</width>
251:       <height>18</height>
252:      </rect>
253:     </property>
254:     <property name="font">
255:      <font>
256:       <family>微软雅黑</family>
257:       <pointsize>8</pointsize>
258:       <weight>50</weight>
259:       <bold>false</bold>
260:      </font>
261:     </property>
262:     <property name="styleSheet">
263:      <string notr="true">background-color: rgb(248, 231, 28);
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第264-278行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
264: border-radius:5px;</string>
265:     </property>
266:     <property name="text">
267:      <string>Pmin</string>
268:     </property>
269:    </widget>
270:    <widget class="QPushButton" name="pbtnPmax">
271:     <property name="enabled">
272:      <bool>false</bool>
273:     </property>
274:     <property name="geometry">
275:      <rect>
276:       <x>70</x>
277:       <y>6</y>
278:       <width>30</width>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第279-292行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
279:       <height>18</height>
280:      </rect>
281:     </property>
282:     <property name="font">
283:      <font>
284:       <family>微软雅黑</family>
285:       <pointsize>7</pointsize>
286:       <weight>50</weight>
287:       <bold>false</bold>
288:      </font>
289:     </property>
290:     <property name="styleSheet">
291:      <string notr="true">background-color: rgb(248, 231, 28);
292: border-radius:5px;</string>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第293-308行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
293:     </property>
294:     <property name="text">
295:      <string>Pmax</string>
296:     </property>
297:    </widget>
298:    <widget class="QSpinBox" name="spbxPmin">
299:     <property name="enabled">
300:      <bool>false</bool>
301:     </property>
302:     <property name="geometry">
303:      <rect>
304:       <x>40</x>
305:       <y>7</y>
306:       <width>40</width>
307:       <height>18</height>
308:      </rect>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第309-322行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
309:     </property>
310:     <property name="font">
311:      <font>
312:       <family>微软雅黑</family>
313:       <pointsize>7</pointsize>
314:      </font>
315:     </property>
316:     <property name="styleSheet">
317:      <string notr="true">background-color: rgb(126, 211, 33);
318: border-radius:5px;</string>
319:     </property>
320:     <property name="maximum">
321:      <number>2500</number>
322:     </property>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第323-338行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
323:    </widget>
324:    <widget class="QSpinBox" name="spbxPmax">
325:     <property name="enabled">
326:      <bool>false</bool>
327:     </property>
328:     <property name="geometry">
329:      <rect>
330:       <x>80</x>
331:       <y>6</y>
332:       <width>50</width>
333:       <height>18</height>
334:      </rect>
335:     </property>
336:     <property name="font">
337:      <font>
338:       <family>微软雅黑</family>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第339-352行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
339:       <pointsize>7</pointsize>
340:      </font>
341:     </property>
342:     <property name="styleSheet">
343:      <string notr="true">background-color: rgb(126, 211, 33);
344: border-radius:5px;</string>
345:     </property>
346:     <property name="maximum">
347:      <number>9999</number>
348:     </property>
349:     <property name="value">
350:      <number>500</number>
351:     </property>
352:    </widget>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第353-367行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
353:    <widget class="QLineEdit" name="labLeft">
354:     <property name="geometry">
355:      <rect>
356:       <x>35</x>
357:       <y>10</y>
358:       <width>15</width>
359:       <height>18</height>
360:      </rect>
361:     </property>
362:     <property name="font">
363:      <font>
364:       <family>黑体</family>
365:       <pointsize>9</pointsize>
366:       <weight>9</weight>
367:       <italic>false</italic>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第368-381行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
368:       <bold>false</bold>
369:      </font>
370:     </property>
371:     <property name="styleSheet">
372:      <string notr="true">font: 75 9pt &quot;黑体&quot;;
373: color: rgb(255, 255, 255);</string>
374:     </property>
375:     <property name="text">
376:      <string>小</string>
377:     </property>
378:     <property name="alignment">
379:      <set>Qt::AlignCenter</set>
380:     </property>
381:    </widget>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第382-396行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
382:    <widget class="QLineEdit" name="labRight">
383:     <property name="geometry">
384:      <rect>
385:       <x>115</x>
386:       <y>8</y>
387:       <width>15</width>
388:       <height>18</height>
389:      </rect>
390:     </property>
391:     <property name="font">
392:      <font>
393:       <family>黑体</family>
394:       <pointsize>9</pointsize>
395:       <weight>9</weight>
396:       <italic>false</italic>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第397-410行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
397:       <bold>false</bold>
398:      </font>
399:     </property>
400:     <property name="styleSheet">
401:      <string notr="true">font: 75 9pt &quot;黑体&quot;;
402: color: rgb(255, 255, 255);</string>
403:     </property>
404:     <property name="text">
405:      <string>大</string>
406:     </property>
407:     <property name="alignment">
408:      <set>Qt::AlignCenter</set>
409:     </property>
410:    </widget>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第411-425行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
411:    <widget class="QLineEdit" name="edtDjTitle">
412:     <property name="geometry">
413:      <rect>
414:       <x>40</x>
415:       <y>10</y>
416:       <width>41</width>
417:       <height>20</height>
418:      </rect>
419:     </property>
420:     <property name="font">
421:      <font>
422:       <family>楷体</family>
423:       <pointsize>12</pointsize>
424:       <weight>9</weight>
425:       <italic>false</italic>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第426-438行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
426:       <bold>false</bold>
427:      </font>
428:     </property>
429:     <property name="styleSheet">
430:      <string notr="true">font: 75 12pt &quot;楷体&quot;;
431: color: rgb(255, 255, 255);
432: background-image: url(:/images/btn_bg2.png);
433: </string>
434:     </property>
435:     <property name="text">
436:      <string>0号</string>
437:     </property>
438:     <property name="alignment">
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第439-452行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
439:      <set>Qt::AlignCenter</set>
440:     </property>
441:    </widget>
442:    <widget class="QComboBox" name="cmbDjId">
443:     <property name="geometry">
444:      <rect>
445:       <x>60</x>
446:       <y>6</y>
447:       <width>51</width>
448:       <height>20</height>
449:      </rect>
450:     </property>
451:     <property name="styleSheet">
452:      <string notr="true">color: rgb(0, 0, 0);
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第453-469行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
453: font: 75 12pt &quot;楷体&quot;;
454: border-radius:10px;</string>
455:     </property>
456:     <item>
457:      <property name="text">
458:       <string>255</string>
459:      </property>
460:     </item>
461:     <item>
462:      <property name="text">
463:       <string>001</string>
464:      </property>
465:     </item>
466:     <item>
467:      <property name="text">
468:       <string>002</string>
469:      </property>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第470-486行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
470:     </item>
471:     <item>
472:      <property name="text">
473:       <string>003</string>
474:      </property>
475:     </item>
476:     <item>
477:      <property name="text">
478:       <string>004</string>
479:      </property>
480:     </item>
481:     <item>
482:      <property name="text">
483:       <string>005</string>
484:      </property>
485:     </item>
486:    </widget>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第487-500行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
487:    <widget class="QPushButton" name="pbtnSend">
488:     <property name="geometry">
489:      <rect>
490:       <x>160</x>
491:       <y>0</y>
492:       <width>21</width>
493:       <height>20</height>
494:      </rect>
495:     </property>
496:     <property name="styleSheet">
497:      <string notr="true">color: rgb(0, 0, 0);
498: font: 75 12pt &quot;楷体&quot;;
499: color: rgb(255, 255, 255);
500: border-radius:10px;</string>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第501-515行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
501:     </property>
502:     <property name="text">
503:      <string>R</string>
504:     </property>
505:    </widget>
506:    <widget class="QComboBox" name="cmbMenu">
507:     <property name="geometry">
508:      <rect>
509:       <x>50</x>
510:       <y>3</y>
511:       <width>81</width>
512:       <height>20</height>
513:      </rect>
514:     </property>
515:     <property name="styleSheet">
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第516-531行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
516:      <string notr="true">color: rgb(0, 0, 0);
517: font: 75 12pt &quot;楷体&quot;;
518: border-radius:10px;</string>
519:     </property>
520:     <item>
521:      <property name="text">
522:       <string>ID号</string>
523:      </property>
524:     </item>
525:     <item>
526:      <property name="text">
527:       <string>波率</string>
528:      </property>
529:     </item>
530:     <item>
531:      <property name="text">
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第532-549行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
532:       <string>模式</string>
533:      </property>
534:     </item>
535:     <item>
536:      <property name="text">
537:       <string>读角</string>
538:      </property>
539:     </item>
540:     <item>
541:      <property name="text">
542:       <string>释力</string>
543:      </property>
544:     </item>
545:     <item>
546:      <property name="text">
547:       <string>中值</string>
548:      </property>
549:     </item>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第550-566行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
550:     <item>
551:      <property name="text">
552:       <string>出厂</string>
553:      </property>
554:     </item>
555:     <item>
556:      <property name="text">
557:       <string>版本</string>
558:      </property>
559:     </item>
560:    </widget>
561:    <widget class="QFrame" name="frame_2">
562:     <property name="geometry">
563:      <rect>
564:       <x>2</x>
565:       <y>63</y>
566:       <width>176</width>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第567-578行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
567:       <height>30</height>
568:      </rect>
569:     </property>
570:     <property name="styleSheet">
571:      <string notr="true">color: rgb(255, 255, 255);
572: background-image: url(:/images/btn_bg2.png);</string>
573:     </property>
574:     <property name="frameShape">
575:      <enum>QFrame::StyledPanel</enum>
576:     </property>
577:     <property name="frameShadow">
578:      <enum>QFrame::Raised</enum>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第579-593行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
579:     </property>
580:    </widget>
581:    <widget class="QSlider" name="hsdPwm">
582:     <property name="enabled">
583:      <bool>false</bool>
584:     </property>
585:     <property name="geometry">
586:      <rect>
587:       <x>36</x>
588:       <y>32</y>
589:       <width>88</width>
590:       <height>30</height>
591:      </rect>
592:     </property>
593:     <property name="styleSheet">
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第594-604行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
594:      <string notr="true">QSlider::groove:horizontal {
595:         height: 8px;
596:         background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 rgb(124, 124, 124), stop: 1.0 rgb(72, 71, 71));
597: }
598: QSlider::handle:horizontal {
599:         width: 10px;
600:         background: rgb(0, 160, 230);
601:         margin: -6px 0px -6px 0px;
602:         border-radius: 9px;
603: }</string>
604:     </property>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第605-618行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
605:     <property name="minimum">
606:      <number>500</number>
607:     </property>
608:     <property name="maximum">
609:      <number>2500</number>
610:     </property>
611:     <property name="value">
612:      <number>1500</number>
613:     </property>
614:     <property name="orientation">
615:      <enum>Qt::Horizontal</enum>
616:     </property>
617:    </widget>
618:    <widget class="QSpinBox" name="spbxBias">
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第619-634行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
619:     <property name="enabled">
620:      <bool>false</bool>
621:     </property>
622:     <property name="geometry">
623:      <rect>
624:       <x>38</x>
625:       <y>69</y>
626:       <width>50</width>
627:       <height>20</height>
628:      </rect>
629:     </property>
630:     <property name="font">
631:      <font>
632:       <family>微软雅黑</family>
633:       <pointsize>8</pointsize>
634:       <weight>75</weight>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第635-648行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
635:       <bold>true</bold>
636:      </font>
637:     </property>
638:     <property name="styleSheet">
639:      <string notr="true">background-color: rgb(0, 139, 255);
640: border-radius:5px;
641: color: rgb(255, 255, 255);</string>
642:     </property>
643:     <property name="maximum">
644:      <number>2500</number>
645:     </property>
646:    </widget>
647:    <zorder>pbtnSend</zorder>
648:    <zorder>tobnClose</zorder>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第649-661行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
649:    <zorder>cmbMenu</zorder>
650:    <zorder>pbtnPmin</zorder>
651:    <zorder>pbtnPmax</zorder>
652:    <zorder>spbxPmin</zorder>
653:    <zorder>spbxPmax</zorder>
654:    <zorder>labLeft</zorder>
655:    <zorder>labRight</zorder>
656:    <zorder>cmbDjId</zorder>
657:    <zorder>edtDjTitle</zorder>
658:    <zorder>frame_2</zorder>
659:    <zorder>pbtnPwm</zorder>
660:    <zorder>spbxPwm</zorder>
661:    <zorder>pbtnTime</zorder>
```

## formsteerctl.ui | 文件开头/全局定义 | 原文件第662-671行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/formsteerctl.ui
以下为原始源码，不是截图OCR。
```
662:    <zorder>spbxTime</zorder>
663:    <zorder>hsdPwm</zorder>
664:    <zorder>labIndex</zorder>
665:    <zorder>spbxBias</zorder>
666:    <zorder>pbtnBias</zorder>
667:   </widget>
668:  </widget>
669:  <resources/>
670:  <connections/>
671: </ui>
```

## main.cpp | 文件开头/全局定义 | 原文件第1-3行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/main.cpp
以下为原始源码，不是截图OCR。
```
1: #include "mainwindow.h"
2: #include <QApplication>
3: 
```

## main.cpp | main | 原文件第4-14行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/main.cpp
以下为原始源码，不是截图OCR。
```
4: int main(int argc, char *argv[])
5: {
6:     QApplication a(argc, argv);
7:     MainWindow w;
8:     //w.setStyleSheet("background-color: rgb(66, 76, 88);");
9:     w.show();
10:     w.showMaximized();
11: 
12: 
13:     return a.exec();
14: }
```

## mainwindow.cpp | 文件开头/全局定义 | 原文件第1-17行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1: #include "ui_mainwindow.h"
2: #include <QtGui>
3: #include "mainwindow.h"
4: #include <QStringList>
5: #include <QIcon>
6: #include <QAction>
7: #include <QMenu>
8: #include <QFileDialog>
9: #include <QMessageBox>
10: #include <QMenuBar>
11: #include <QGroupBox>
12: #include <QCheckBox>
13: #include <QLabel>
14: #include <QComboBox>
15: #include <QHBoxLayout>
16: #include <QVBoxLayout>
17: #include <QGridLayout>
```

## mainwindow.cpp | 文件开头/全局定义 | 原文件第18-32行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
18: #include <QLineEdit>
19: #include <QTextEdit>
20: #include <QPushButton>
21: #include <QScrollArea>
22: #include <QScrollBar>
23: #include <QtSerialPort/qserialport.h>
24: #include <QtSerialPort/qserialportinfo.h>
25: #include <QDebug>
26: #include <QList>
27: #include <QSlider>
28: #include <QSpinBox>
29: #include <qregexp.h>
30: #include <QRadioButton>
31: #include <qlistwidget.h>
32: #include <QTextStream>
```

## mainwindow.cpp | 文件开头/全局定义 | 原文件第33-43行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
33: #include <QButtonGroup>
34: #include "actiongroup.h"
35: #include "actiongroupitem.h"
36: #include "formsteerctl.h"
37: #include "dragwidget.h"
38: #include <QSettings>
39: 
40: #define SAVE_FILE_NAME      "config.ini"
41: #define TITLE               "Zide_MINI V0"
42: #define BG_ROBOT_LOAD       "image: url(:/user_images/bg_load.png);"
43: #define BG_ROBOT_DIY        BG_ROBOT_LOAD
```

## mainwindow.cpp | 文件开头/全局定义 | 原文件第44-55行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
44: #define BG_ROBOT_RESET      "image: url(:/images/bg_reset.png);"
45: #define BG_ROBOT_MY        "image: url(:/images/bg_jxb.png);"
46: #define BG_ROBOT_XSZ        "image: url(:/images/bg_xfoot.png);"
47: #define BG_ROBOT_DEFAULT    BG_ROBOT_LOAD
48: 
49: #define MODE_ROBOT_DIY 1
50: #define MODE_ROBOT_JXB 2
51: 
52: #define BG_WIDTH            1440
53: #define BG_HEIGHT           900
54: 
55: int  last_select = 0;
```

## mainwindow.cpp | 文件开头/全局定义 | 原文件第56-71行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
56: bool list_click = false;
57: bool zxReleaseFlag = false;
58: 
59: int dj_bias[MAX_STEER_NUM] = {0};
60: int dj_bias_bak[MAX_STEER_NUM] = {0};
61: bool chkBoxDjFlag=true;
62: bool toReadPwm = false;
63: int toReadPwmIndex;
64: 
65: long long ackDownTime = 0;
66: //bool zxCorrectFlag = false;
67: 
68: #define WIDTH_NAME_LAYOUT             60
69: #define DJ_PRE_NUM                  20
70: 
71: int gird_index1 = 0, gird_index2 = 0;
```

## mainwindow.cpp | 文件开头/全局定义 | 原文件第72-85行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
72: 
73: QString updateFileName = "";
74: 
75: bool comOpened = false;
76: bool zxWRead = false;
77: bool data_send_flag = true;
78: bool actionList_double_clicked = false, actionList_double_clicked_fisrt = true;
79: bool initOk = false;
80: int  comIndex = 0;
81: int modeRobot = 0;
82: QString comText="com1";
83: 
84: QString pushButtonStyle1_1 =
85:         "QPushButton{background-color: rgb(66, 76, 88);\
```

## mainwindow.cpp | 文件开头/全局定义 | 原文件第86-92行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
86:                     color: rgb(255, 84, 25); \
87:                     font: 75 18pt; \
88:                     border-radius: 10px; border: 2px groove gray; border-style: outset;}\
89:         QPushButton:hover{background-color:white; color: black;} \
90:         QPushButton:pressed{background-color:rgb(85, 170, 255);border-style: inset; }";
91: 
92: QString pushButtonStyle1_2 =
```

## mainwindow.cpp | 文件开头/全局定义 | 原文件第93-99行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
93:         "QPushButton{background-color: rgb(66, 76, 8388\
94:                     color: rgb(255, 255, 0); \
95:                     font: 75 16pt; \
96:                     border-radius: 10px; border: 2px groove gray; border-style: outset;}\
97:         QPushButton:hover{background-color:white; color: black;} \
98:         QPushButton:pressed{background-color:rgb(85, 170, 255);border-style: inset; }";
99: 
```

## mainwindow.cpp | 文件开头/全局定义 | 原文件第100-105行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
100: QString pushButtonStyle1_3 =
101:         "QPushButton{background-color: rgb(66, 76, 88);\
102:                     color: rgb(0, 255, 0); \
103:                     font: 75 18pt; \
104:                     border-radius: 10px; border: 2px groove gray; border-style: outset;}\
105:         QPushButton:hover{background-color:white; color: black;} \
```

## mainwindow.cpp | 文件开头/全局定义 | 原文件第106-112行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
106:         QPushButton:pressed{background-color:rgb(85, 170, 255);border-style: inset; }";
107: 
108: 
109: 
110: QString pbtnStyle_normal =
111:         "QPushButton{background-color: rgb(66, 76, 88); color: white; border-radius: 3px; border: 2px groove gray; border-style: outset;}\
112:         QPushButton:hover{background-color:white; color: black;} \
```

## mainwindow.cpp | 文件开头/全局定义 | 原文件第113-118行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
113:         QPushButton:pressed{background-color:rgb(85, 170, 255);border-style: inset; }";
114: 
115: QString pbtnStyle_xxxxx =
116:         "QPushButton{background-color: rgb(66, 76, 88);color: white; border-radius: 3px; border: 2px groove gray; border-style: outset;}\
117:         QPushButton:hover{background-color:white; color: blue;} \
118:         QPushButton:pressed{background-color:rgb(85, 170, 255);border-style: inset; }";
```

## mainwindow.cpp | 文件开头/全局定义 | 原文件第119-127行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
119: 
120: QString pbtnStyle_actived =
121:         "QPushButton{background-color: rgb(46,190,251);color: white; border-radius: 3px; border: 2px groove gray; border-style: outset;}\
122:         QPushButton:hover{background-color:white; color: blue;} \
123:         QPushButton:pressed{background-color:rgb(85, 170, 255);border-style: inset; }";
124: 
125: //
126: MainWindow::MainWindow(QWidget *parent) :
127:     QMainWindow(parent),
```

## mainwindow.cpp | 文件开头/全局定义 | 原文件第128-142行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
128:     ui(new Ui::MainWindow)
129: {
130:     ui->setupUi(this);
131: 
132:     serialOpened = false;
133:     doGroupActionsOnline = false;
134:     doGroupActionsOffline = false;
135:     doGroupActionsFlag = true;
136:     doGroupActionsStop = false;
137:     saveActionsFlag = false;
138: 
139:     timesToDo = 1;
140: 
141:     //创建列表
142:     actionGroupListMng.actionGroupList.clear();
```

## mainwindow.cpp | 文件开头/全局定义 | 原文件第143-155行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
143:     actionGroupListMng.currentSelected = -1;
144: 
145:     //setGeometry(100,100,500,300);
146:     setWindowTitle(TITLE);
147:     createActions();
148:     createMenus();
149: 
150:     ui_init();
151: 
152:     threadA = new MyThread();
153:     connect(threadA,SIGNAL(comRecive()), this, SLOT(handleSerialRxData()));
154:     connect(threadA,SIGNAL(error(QString)),this,SLOT(hanlderSerialError(QString)));
155: 
```

## mainwindow.cpp | 文件开头/全局定义 | 原文件第156-164行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
156: //    QTimer *serialScanTimer = new QTimer();
157: //    connect(serialScanTimer,SIGNAL(timeout()),this,SLOT(updateSerialPortList()));
158: //    serialScanTimer->start(500);
159: 
160:     actionTimer = new QTimer(this);
161:     actionTimer->start(1000);
162:     connect(actionTimer,SIGNAL(timeout()),this,SLOT(actionTimer_timeout()));
163: 
164:     saveDefaultFileName = "./" + QString(SAVE_FILE_NAME);
```

## mainwindow.cpp | 文件开头/全局定义 | 原文件第165-177行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
165:     autoSaveTimer = new QTimer(this);
166:     autoSaveTimer->start(5000);
167:     connect(autoSaveTimer,SIGNAL(timeout()),this,SLOT(autosave_timeout()));
168: 
169:     ackDownCheckTimer = new QTimer(this);
170:     connect(ackDownCheckTimer,SIGNAL(timeout()),this,SLOT(ackDownCheckTimer_timeout()));
171:     ackDownCheckTimer->start(1000);
172: 
173: 
174: 
175: 
176:     timeDownload = 300;
177:     //打开工程文件
```

## mainwindow.cpp | 文件开头/全局定义 | 原文件第178-191行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
178:     if(QFile(saveDefaultFileName).exists()){
179:         openProjectFile(saveDefaultFileName);
180:     } else {
181:         //actionGroupListMng.actionGroupList.clear();
182:         //addActionGroup_clicked();
183:         //updateTableList();
184:     }
185: 
186: 
187: 
188: 
189:     actionGroupListMng.currentSelected = 0;
190:     //更新控件
191:     for(int i = 0;i < MAX_STEER_NUM;i++){
```

## mainwindow.cpp | 文件开头/全局定义 | 原文件第192-209行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
192:         sc[i]->setBiasEnable(true);
193:         dis_arr[i] = true;
194:         dis_arr_diy[i] = true;
195:         //updateWindowItem(0);
196:     }
197: 
198: 
199:     justComboBoxSteerNumber = false;
200:     timeBiasDownload = false;
201: 
202: 
203:     timeLdDownloadIndex = 0;
204:     timeLdDownloadFlag = false;
205: 
206:     timeCyDownloadIndex = 0;
207:     timeCyDownloadFlag = false;
208: 
209: 
```

## mainwindow.cpp | 文件开头/全局定义 | 原文件第210-228行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
210:     timeZxReadAdcFlag = false;
211:     dataSendEdit->clear();
212:     initOk = true;
213: 
214: }
215: 
216: 
217: 
218: 
219: MainWindow::~MainWindow()
220: {
221:     delete ui;
222: }
223: 
224: 
225: 
226: /*
227: *操作记录日志显示
228: */
```

## mainwindow.cpp | MainWindow::sendToLogDisplay | 原文件第229-236行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
229: void MainWindow::sendToLogDisplay(QString str)
230: {
231:     dataRecvEdit->moveCursor(QTextCursor::End);
232:     dataRecvEdit->setTextColor(QColor(255,0,0));
233:     dataRecvEdit->append(QTime::currentTime().toString("hh:mm:ss:zzz"));
234:     dataRecvEdit->setTextColor(QColor(0,255,0));
235:     dataRecvEdit->insertPlainText("-->");
236:     dataRecvEdit->setTextColor(QColor(0,0,0));
```

## mainwindow.cpp | MainWindow::sendToLogDisplay | 原文件第237-242行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
237:     dataRecvEdit->insertPlainText(str);
238:     dataRecvEdit->moveCursor(QTextCursor::End);
239:     QApplication::processEvents();
240: }
241: 
242: 
```

## mainwindow.cpp | MainWindow::on_actionHelp_triggered | 原文件第243-251行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
243: void MainWindow::on_actionHelp_triggered()
244: {
245: //    QString AboutStr;
246: //    AboutStr.append(QStringLiteral("官方网站<span style=\"font-size:12px;\"></span>：<a href=\"http://www.usbxyz.com\">www.usbxyz.com</a><br>"));
247: //    AboutStr.append(QStringLiteral("技术支持：188298598<br>"));
248: //    AboutStr.append(QStringLiteral("版本信息：v1.0.0"));
249: //    QMessageBox::about(this,QStringLiteral("帮助"),AboutStr);
250: }
251: 
```

## mainwindow.cpp | MainWindow::pushButton_sendData_clicked | 原文件第252-258行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
252: void MainWindow::pushButton_sendData_clicked() {
253:     qDebug() << "pushButton_sendData_clicked";
254:     //if(myHandle && myLoader)
255:     //myLoader->BT_WriteData2(myHandle,0,(unsigned char *)(ui->textEdit_sendData->toPlainText().toLatin1().data()),strlen(ui->textEdit_sendData->toPlainText().toLatin1().data()),1);
256: }
257: 
258: 
```

## mainwindow.cpp | MainWindow::uart_send_str | 原文件第259-271行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
259: void MainWindow::uart_send_str(QString str) {
260: 
261:     if(!initOk)return;
262: 
263:     if(!comOpened) {
264:         QMessageBox::warning(this,tr("温馨提示"),tr("串口没打开,请先打开串口"));
265:     }
266: 
267:     if(!data_send_flag)return;
268: 
269:     if(comOpened && this->threadA->comOpened()) {
270:         this->threadA->TxData.clear();
271:         this->threadA->TxData.append(str);
```

## mainwindow.cpp | MainWindow::uart_send_str | 原文件第272-278行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
272:         this->threadA->changeTxState(true);
273:         qDebug() << "uart_send:" << str;
274:         dataSendEdit->setText(str);
275:     }
276: }
277: 
278: 
```

## mainwindow.cpp | MainWindow::updateSerialPortList | 原文件第279-287行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
279: void MainWindow::updateSerialPortList(){
280:     static int currentPortCount = 0, portChangeCount = 0;
281:     int indexSum = 0;
282:     bool comRemoved = true;
283:     QString curComText = cbSerialCom->currentText();
284:     QList<QSerialPortInfo> list = QSerialPortInfo::availablePorts();
285:     if(currentPortCount != list.count()){
286:         portChangeCount ++;
287:         currentPortCount =  list.count();
```

## mainwindow.cpp | MainWindow::updateSerialPortList | 原文件第288-296行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
288:         QString currText = cbSerialCom->currentText();
289: 
290:         cbSerialCom->clear();
291:         foreach(const QSerialPortInfo &info, list){
292:            //qDebug() << "Name:" + info.portName();
293:            QChar ch = info.portName().at(info.portName().length() - 1);
294:            if( (ch > '9') || (ch < '0')) {
295:                //qDebug() << "get===:" + info.portName();
296:                continue;
```

## mainwindow.cpp | MainWindow::updateSerialPortList | 原文件第297-309行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
297:            }
298:            cbSerialCom->addItem(info.portName());
299:            if(curComText.compare(info.portName()) == 0) {
300:                comRemoved = false;
301:            }
302:            indexSum ++;
303:         }
304: 
305: 
306:         int lastSelectIndex = cbSerialCom->findText(currText);
307: 
308:         if(lastSelectIndex >= list.count() || lastSelectIndex < 0){
309:             lastSelectIndex = 0;
```

## mainwindow.cpp | MainWindow::updateSerialPortList | 原文件第310-320行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
310:         }
311: 
312:         if(comRemoved) {
313:             if(comOpened) {
314:                 threadA->stopCom();
315:                 pbtnConnect->setStyleSheet(pushButtonStyle1_1);
316:                 serialOpened = false;
317:                 pbtnConnect->setText("设备未连接");
318:                 labSerialLed->setStyleSheet("image: url(:/images/light_off.png);");
319:                 comOpened = false;
320:             }
```

## mainwindow.cpp | MainWindow::updateSerialPortList | 原文件第321-338行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
321:         }
322: 
323: 
324:          cbSerialCom->setCurrentIndex(lastSelectIndex);
325: 
326: 
327:     }
328:     pbtnConnectUpdate();
329: 
330:     //更新舵机checkBox
331:     if(chkBoxDjFlag) {
332:         for(int i=0;i<MAX_STEER_NUM; i++) {
333:             chkBoxDj[i]->setChecked(sc[i]->getSeed());
334:             dis_arr[i] = chkBoxDj[i]->isChecked();
335:         }
336:     }
337: }
338: 
```

## mainwindow.cpp | MainWindow::closeEvent | 原文件第339-348行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
339: void MainWindow::closeEvent(QCloseEvent *e){
340:     Q_UNUSED(e);
341: 
342:     if(QFile(saveDefaultFileName).exists()){
343: //        if(QMessageBox::Yes == QMessageBox::question(this,"要保存吗？","关闭之前要保存对舵机动作组的修改吗?",QMessageBox::Yes,QMessageBox::No)){
344: //            saveProjectFile();
345: //        }
346:     }
347: }
348: 
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第349-362行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
349: void MainWindow::ui_init(){
350: 
351:     QIcon myAppIcon(":/images/pc_logo.ico");
352:     setWindowIcon(myAppIcon);
353:     QWidget *pWidget = new QWidget;
354: 
355:     QVBoxLayout *rightContent_11 = new QVBoxLayout();
356:     QVBoxLayout *rightContent_23 = new QVBoxLayout();
357: 
358: 
359:     QVBoxLayout *tmpVBoxLayout;
360:     QHBoxLayout *tmpHBoxLayout;
361:     QGridLayout *tmpGridLayout;
362:     QFrame *tmpFrame;
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第363-377行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
363:     QLabel *tmpLabel;
364: 
365:     /////////////////////////////////////状态栏
366:     statusLabel = new QLabel();
367:     statusBar()->addWidget(statusLabel);
368: 
369: 
370: 
371:     //-------------------左边区域
372:     QVBoxLayout *leftContent = new QVBoxLayout();
373: 
374:     dj_sca = new QScrollArea();
375:     dj_sca->setVerticalScrollBarPolicy(Qt::ScrollBarAsNeeded);
376:     dj_sca->setStyleSheet(
377: 
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第378-394行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
378:     " QScrollBar:horizon {"
379:     " border:0px black;"
380:     " width: 20px"
381:     "}"
382: 
383:     " QScrollBar::handle:horizon {"
384:     " background: #E2E2E7;"
385:     " border: 3px black;"
386:     " border-radius:3px;"
387:     " }"
388: 
389:     " QScrollBar::add-page:horizon, QScrollBar::sub-page:horizon {"
390:     " background: none;"
391:     "}"
392: 
393:     );
394: 
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第395-406行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
395:     dj_pannel = new DragWidget(this);
396:     dj_pannel->setGeometry(QRect(0,0,BG_WIDTH,BG_HEIGHT));
397:     //dj_pannel->setBackgroundRole(QPalette::Dark);
398: 
399:     //设置背景图片
400:     dj_bg = new QLabel(dj_pannel);
401:     dj_bg->setFixedWidth(BG_WIDTH);
402:     dj_bg->setFixedHeight(BG_HEIGHT);
403: 
404:     //初始化舵机位置
405:     int pos_x_inc = 190;
406:     int pos_y_inc = 98;
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第407-413行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
407:     for(int index = 0; index < MAX_STEER_NUM; index ++){
408:         adc_arr[index] = false;
409:         djLstId[index] = index;
410:         sc[index] = new FormSteerCtl(index, index, dj_pannel);
411:         sc[index]->setTitle("S" + QString::number(index));
412:         sc[index]->setLableIndex(QString::number(index) + "号");
413:         sc[index]->move(pos_x_inc*(index%5),pos_y_inc*(index/5));
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第414-420行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
414:         sc[index]->setSeed(true);
415:         sc[index]->setEnabled(true);
416:         sc[index]->setAttribute(Qt::WA_DeleteOnClose);
417:         sc[index]->setBiasEnable(false);
418: 
419:         connect(sc[index],SIGNAL(clicked(FormSteerCtl*)),this,SLOT(steerCtl_clicked(FormSteerCtl*)));
420:         connect(sc[index],SIGNAL(valueChanged(FormSteerCtl*)),this,SLOT(steerCtl_valueChanged(FormSteerCtl*)));
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第421-429行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
421:         connect(sc[index],SIGNAL(currentIndexChanged(FormSteerCtl*)),this,SLOT(steerCtl_currentIndexChanged(FormSteerCtl*)));
422:         //connect(sc[index],SIGNAL(returnPressed()),this,SLOT(steerCtl_valueChanged(FormSteerCtl*)));
423:     }
424: 
425: 
426: 
427:     dj_sca->setWidget(dj_pannel);
428:     leftContent->addWidget(dj_sca);
429:     dj_pannel->setContextMenuPolicy(Qt::CustomContextMenu);
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第430-436行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
430:     connect(dj_pannel,SIGNAL(clicked(DragWidget*)),this,SLOT(dj_pannel_clicked(DragWidget*)));
431:     connect(dj_pannel, SIGNAL(customContextMenuRequested(const QPoint&)),
432:             this, SLOT(show_dj_pannelMenu(const QPoint&)));//this是datatable所在窗口
433: 
434:     QHBoxLayout *mainLayout = new QHBoxLayout();
435:     mainLayout->addLayout(leftContent,1);
436:     pWidget->setLayout(mainLayout);
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第437-445行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
437:     pWidget->setStyleSheet("background-color: rgb(66, 76, 88);");
438:     setCentralWidget(pWidget);
439: 
440: 
441:     //////////////////////////////////////////////////////////////右边的dock窗口
442:     /// /////////////////////////////////////串口设置
443:     tmpFrame = new QFrame();
444:     tmpFrame->setStyleSheet("background-color: rgb(226, 226, 231);");
445:     //tmpFrame->setFixedWidth(RIGHT_CONTENT_FIX_WIDTH);
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第446-454行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
446:     tmpVBoxLayout = new QVBoxLayout();
447: 
448:     tmpGridLayout = new QGridLayout();
449:     tmpGridLayout->setAlignment(Qt::AlignTop);
450:     tmpLabel = new QLabel(tr("串口号"));
451:     tmpLabel->setFixedWidth(50);
452:     cbSerialCom = new QComboBox();
453:     //cbSerialCom->setFixedWidth(WIDTH_NAME_LAYOUT*2);
454:     cbSerialCom->setStyleSheet("background-color: rgb(255, 255, 255);border-radius:3px;");
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第455-462行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
455:     //cbSerialCom->setFixedWidth(WIDTH_SPINBOX_LAYOUT+10);
456:     QList<QSerialPortInfo> list = QSerialPortInfo::availablePorts();
457:     int com_index=0;
458:     foreach(const QSerialPortInfo &info, list){
459:            cbSerialCom->addItem(info.portName());
460:            com_index++;
461:     }
462:     cbBaudRate = new QComboBox();
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第463-468行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
463:     cbBaudRate->setStyleSheet("background-color: rgb(255, 255, 255);border-radius:3px;");
464:     QStringList baudRateList;
465:     baudRateList << "600" <<"1200" << "2400" << "4800" << "9600"
466:                 << "14400" << "19200" << "28800" << "38400"
467:                    << "57600" << "115200" << "128000" << "230400" << "460800" << "1000000";
468:     cbBaudRate->addItems(baudRateList);
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第469-475行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
469:     cbBaudRate->setCurrentIndex(10);
470:     pbtnConnect = new QPushButton(tr("设备未连接"));
471:     pbtnConnect->setStyleSheet("background-color: rgb(216, 216, 216);border-radius:5px;color: rgb(255, 84, 25);font: 75 18pt 微软雅黑;");
472: 
473:     pbtnConnect->setStyleSheet(pushButtonStyle1_1);
474:     //pbtnConnect->setFixedWidth(RIGHT_CONTENT_FIX_WIDTH-20);
475:     pbtnConnect->setFixedHeight(50);
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第476-483行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
476:     //pbtnConnect->setFixedWidth(WIDTH_NAME_LAYOUT*4);
477:     connect(pbtnConnect,SIGNAL(clicked()),this,SLOT(pbtnConnect_clicked()));
478: 
479: 
480:     pbtnSerialLed = new QPushButton("");
481:     pbtnSerialLed->setFixedHeight(40);
482:     pbtnSerialLed->setFixedWidth(40);
483:     pbtnSerialLed->setStyleSheet("image: url(:/images/light_off.png);");
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第484-490行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
484:     connect(pbtnSerialLed,SIGNAL(clicked()),this,SLOT(pbtnSerialLed_clicked()));
485:     //pbtnSerialLed->viewport()->installEventFilter(this);
486: 
487:     labSerialLed = new QLabel("");
488:     labSerialLed->setFixedHeight(40);
489:     labSerialLed->setFixedWidth(40);
490:     labSerialLed->setStyleSheet("image: url(:/images/light_off.png);");
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第491-501行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
491:     connect(labSerialLed,SIGNAL(clicked()),this,SLOT(pbtnSerialLed_clicked()));
492: 
493:     tmpGridLayout->addWidget(tmpLabel,1,0);
494:     tmpGridLayout->addWidget(cbSerialCom,1,1);
495: 
496:     tmpLabel = new QLabel(tr("波特率"));
497:     tmpLabel->setFixedWidth(50);
498: 
499:     tmpGridLayout->addWidget(tmpLabel,1,2);
500:     tmpGridLayout->addWidget(cbBaudRate,1,3);
501: 
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第502-510行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
502:     QHBoxLayout *serialVbox2 = new QHBoxLayout();
503:     serialVbox2->addWidget(pbtnConnect);
504:     serialVbox2->addWidget(pbtnSerialLed);
505: 
506:     QHBoxLayout *dataSendLayout = new QHBoxLayout();
507: 
508:     dataSendEdit = new QTextEdit();
509:     dataSendEdit->setFixedHeight(40);
510:     dataSendEdit->setStyleSheet("background-color: rgb(255, 255, 255);border-radius:3px;");
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第511-518行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
511:     dataSendEdit->viewport()->installEventFilter(this);
512: 
513:     pushButtonDataSend = new QPushButton(tr("发送"));
514:     pushButtonDataSend->setStyleSheet("background-color: rgb(216, 216, 216);border-radius:3px;");
515:     pushButtonDataSend->setStyleSheet(pbtnStyle_normal);
516: 
517:     connect(pushButtonDataSend,SIGNAL(clicked()),this,SLOT(pushButtonDataSend_clicked()));
518: 
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第519-527行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
519:     pushButtonDataSend->setFixedWidth(40);
520:     pushButtonDataSend->setFixedHeight(40);
521:     dataSendLayout->addWidget(dataSendEdit);
522:     dataSendLayout->addWidget(pushButtonDataSend);
523: 
524: 
525:     QVBoxLayout *dataRecvLayout = new QVBoxLayout();
526:     dataRecvEdit = new QTextEdit();
527:     dataRecvEdit->setStyleSheet("background-color: rgb(255, 255, 255);border-radius:3px;");
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第528-536行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
528:     dataRecvEdit->viewport()->installEventFilter(this);
529:     connect(dataRecvEdit, SIGNAL(textChanged()), this, SLOT(autoScroll()));
530:     dataRecvLayout->addWidget(dataRecvEdit);
531: 
532: 
533:     tmpVBoxLayout->addLayout(tmpGridLayout);
534:     tmpVBoxLayout->addLayout(serialVbox2);
535:     tmpVBoxLayout->addLayout(dataSendLayout);
536:     tmpVBoxLayout->addLayout(dataRecvLayout);
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第537-546行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
537:     tmpFrame->setLayout(tmpVBoxLayout);
538:     rightContent_11->addWidget(tmpFrame);
539:     rightContent_11->setSpacing(0);
540: 
541: 
542:     tmpFrame = new QFrame();
543:     tmpFrame->setStyleSheet("background-color: rgb(226, 226, 231);");
544:     //tmpFrame->setFixedWidth(RIGHT_CONTENT_FIX_WIDTH);
545:     tmpVBoxLayout = new QVBoxLayout();
546:     ///////////////////////////////////////列表
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第547-551行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
547:     tmpHBoxLayout = new QHBoxLayout();
548:     QHBoxLayout *actionListLayout = new QHBoxLayout();
549:     actionList = new QListWidget();
550:     actionList->setStyleSheet("background-color: rgb(255, 255, 255);border-radius:3px;");
551:     connect(actionList,SIGNAL(clicked(QModelIndex)),this,SLOT(actionList_clicked(QModelIndex)));
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第552-556行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
552:     connect(actionList,SIGNAL(activated(QModelIndex)),this,SLOT(actionList_activated(QModelIndex)));
553:     connect(actionList,SIGNAL(doubleClicked(QModelIndex)),this,SLOT(actionList_doubleClick(QModelIndex)));
554:     connect(actionList,SIGNAL(currentRowChanged(int)),this,SLOT(actionList_rowChanged(int)));
555:     //connect(actionList,SIGNAL(doubleClicked(QModelIndex)),this,SLOT(actionList_clicked(QModelIndex)));
556: 
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第557-564行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
557:     actionList->setContextMenuPolicy(Qt::CustomContextMenu);
558:     connect(actionList, SIGNAL(customContextMenuRequested(const QPoint&)),
559:             this, SLOT(show_actionListMenu(const QPoint&)));//this是datatable所在窗口
560: 
561:     actionListLayout->addWidget(actionList);
562: 
563:     QVBoxLayout *actionListCtlButtonsLayout = new QVBoxLayout();
564:     addActionGroup = new QPushButton(tr("增加组"));
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第565-573行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
565:     insertActionGroup = new QPushButton(tr("插入组"));
566:     delActionGroup = new QPushButton(tr("删除组"));
567:     clearActionGroup = new QPushButton(tr("清空列表"));
568:     pbtnActionSave = new QPushButton(tr("下载动作组"));
569: 
570:     addActionGroup->setFixedHeight(30);
571:     insertActionGroup->setFixedHeight(30);
572:     delActionGroup->setFixedHeight(30);
573:     clearActionGroup->setFixedHeight(30);
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第574-579行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
574:     pbtnActionSave->setFixedHeight(30);
575: 
576:     connect(addActionGroup,SIGNAL(clicked()),this,SLOT(addActionGroup_clicked()));
577:     connect(insertActionGroup,SIGNAL(clicked()),this,SLOT(insertActionGroup_clicked()));
578:     connect(delActionGroup,SIGNAL(clicked()),this,SLOT(delActionGroup_clicked()));
579:     connect(clearActionGroup,SIGNAL(clicked()),this,SLOT(clearActionGroup_clicked()));
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第580-587行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
580:     connect(pbtnActionSave,SIGNAL(clicked()),this,SLOT(pbtnActionSave_clicked()));
581: 
582:     addActionGroup->setStyleSheet(pbtnStyle_normal);
583:     insertActionGroup->setStyleSheet(pbtnStyle_normal);
584:     delActionGroup->setStyleSheet(pbtnStyle_normal);
585:     clearActionGroup->setStyleSheet(pbtnStyle_normal);
586:     pbtnActionSave->setStyleSheet(pbtnStyle_xxxxx);
587: 
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第588-594行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
588:     actionListCtlButtonsLayout->addWidget(addActionGroup);
589:     actionListCtlButtonsLayout->addWidget(insertActionGroup);
590:     actionListCtlButtonsLayout->addWidget(delActionGroup);
591:     actionListCtlButtonsLayout->addWidget(clearActionGroup);
592:     actionListCtlButtonsLayout->addWidget(pbtnActionSave);
593: 
594:     tmpHBoxLayout->addLayout(actionListLayout);
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第595-605行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
595:     tmpHBoxLayout->addLayout(actionListCtlButtonsLayout);
596: 
597:     tmpVBoxLayout->addLayout(tmpHBoxLayout,1);
598: 
599:     tmpGridLayout = new QGridLayout();
600:     tmpGridLayout->setAlignment(Qt::AlignTop);
601:     pbtnDEG = new QPushButton(tr("擦除动作组"));
602:     connect(pbtnDEG,SIGNAL(clicked()),this,SLOT(pbtnDEG_clicked()));
603:     pbtnDEG->setFixedHeight(20);
604: 
605:     pbtnCGP = new QPushButton(tr("检查动作组"));
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第606-614行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
606:     connect(pbtnCGP,SIGNAL(clicked()),this,SLOT(pbtnCGP_clicked()));
607:     pbtnCGP->setFixedHeight(20);
608:     pbtnCGP->setStyleSheet(pbtnStyle_normal);
609: 
610:     pbtnDRS = new QPushButton(tr("读取下位机"));
611:     connect(pbtnDRS,SIGNAL(clicked()),this,SLOT(pbtnDRS_clicked()));
612:     pbtnDRS->setFixedHeight(20);
613: 
614:     pbtnDEA = new QPushButton(tr("擦除下位机"));
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第615-624行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
615:     connect(pbtnDEA,SIGNAL(clicked()),this,SLOT(pbtnDEA_clicked()));
616:     pbtnDEA->setFixedHeight(20);
617: 
618:     pbtnDEG->setStyleSheet(pbtnStyle_normal);
619:     pbtnActionSave->setStyleSheet(pbtnStyle_xxxxx);
620:     pbtnDRS->setStyleSheet(pbtnStyle_normal);
621:     pbtnDEA->setStyleSheet(pbtnStyle_normal);
622: 
623:     tmpGridLayout->addWidget(pbtnDEG,0,0);
624:     tmpGridLayout->addWidget(pbtnCGP,0,1);
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第625-633行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
625:     tmpGridLayout->addWidget(pbtnDRS,0,2);
626:     tmpGridLayout->addWidget(pbtnDEA,0,3);
627:     //tmpVBoxLayout->addLayout(tmpGridLayout);
628: 
629:     ///////////////////////////////////////////////
630:     tmpHBoxLayout = new QHBoxLayout();
631:     tmpLabel = new QLabel(tr("起始动作"));
632:     tmpLabel->setAlignment(Qt::AlignCenter);
633:     tmpLabel->setFixedHeight(40);
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第634-640行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
634:     //tmpLabel->setFixedWidth(WIDTH_NAME_LAYOUT/2);
635:     spinBoxStartGroup = new QSpinBox(this);
636:     spinBoxStartGroup->setStyleSheet("background-color: rgb(255, 255, 255);border-radius:3px;");
637:     spinBoxStartGroup->setFixedHeight(20);
638:     spinBoxStartGroup->setRange(0,9999);
639:     spinBoxStartGroup->setValue(0);
640:     tmpHBoxLayout->addWidget(tmpLabel);
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第641-648行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
641:     tmpHBoxLayout->addWidget(spinBoxStartGroup);
642:     tmpLabel = new QLabel(tr("终止动作"));
643:     tmpLabel->setAlignment(Qt::AlignCenter);
644:     tmpLabel->setFixedHeight(20);
645:     //tmpLabel->setFixedWidth(WIDTH_NAME_LAYOUT/2);
646:     spinBoxEndGroup = new QSpinBox(this);
647:     spinBoxEndGroup->setStyleSheet("background-color: rgb(255, 255, 255);border-radius:3px;");
648:     spinBoxEndGroup->setFixedHeight(20);
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第649-658行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
649:     spinBoxEndGroup->setRange(0,9999);
650:     spinBoxEndGroup->setValue(0);
651:     tmpHBoxLayout->addWidget(tmpLabel);
652:     tmpHBoxLayout->addWidget(spinBoxEndGroup);
653: 
654:     //////////////////////////////////////////////执行次数
655:     tmpLabel = new QLabel(tr("执行次数"));
656:     tmpLabel->setAlignment(Qt::AlignCenter);
657:     tmpLabel->setFixedHeight(20);
658:     //tmpLabel->setFixedWidth(WIDTH_NAME_LAYOUT/2);
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第659-669行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
659:     spinBoxDoTimes = new QSpinBox(this);
660:     spinBoxDoTimes->setStyleSheet("background-color: rgb(255, 255, 255);border-radius:3px;");
661:     spinBoxDoTimes->setFixedHeight(20);
662:     spinBoxDoTimes->setRange(0,9999);
663:     spinBoxDoTimes->setValue(0);
664: 
665:     tmpHBoxLayout->addWidget(tmpLabel);
666:     tmpHBoxLayout->addWidget(spinBoxDoTimes);
667: 
668:     tmpVBoxLayout->addLayout(tmpHBoxLayout,1);
669: 
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第670-676行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
670:     tmpHBoxLayout = new QHBoxLayout();
671:     pbtnDoActionOnline = new QPushButton(tr("在线执行"));
672:     pbtnDoActionOnline->setStyleSheet(pbtnStyle_normal);
673:     pbtnDoActionOnline->setFixedHeight(45);
674:     connect(pbtnDoActionOnline,SIGNAL(clicked()),this,SLOT(pbtnDoActionOnline_clicked()));
675:     tmpHBoxLayout->addWidget(pbtnDoActionOnline);
676:     pbtnDoActionOffline = new QPushButton(tr("脱机执行"));
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第677-683行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
677:     pbtnDoActionOffline->setStyleSheet(pbtnStyle_normal);
678:     pbtnDoActionOffline->setFixedHeight(45);
679:     connect(pbtnDoActionOffline,SIGNAL(clicked()),this,SLOT(pbtnDoActionOffline_clicked()));
680:     tmpHBoxLayout->addWidget(pbtnDoActionOffline);
681:     pbtnDoActionStop = new QPushButton(tr("停止"));
682:     pbtnDoActionStop->setStyleSheet(pbtnStyle_normal);
683:     pbtnDoActionStop->setFixedHeight(45);
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第684-695行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
684:     connect(pbtnDoActionStop,SIGNAL(clicked()),this,SLOT(pbtnDoActionStop_clicked()));
685:     tmpHBoxLayout->addWidget(pbtnDoActionStop);
686:     tmpVBoxLayout->addLayout(tmpHBoxLayout,1);
687: 
688: 
689:     tmpFrame->setLayout(tmpVBoxLayout);
690:     rightContent_23->addWidget(tmpFrame);
691: 
692: 
693:     QWidget *right_widget;
694:     //串口配置
695:     QDockWidget *dock1 = new QDockWidget(tr("串口配置"), this);
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第696-705行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
696:     dock1->setAllowedAreas(Qt::AllDockWidgetAreas);
697:     right_widget = new QWidget();
698:     right_widget->setLayout(rightContent_11);
699:     dock1->setWidget(right_widget);
700:     dock1->setAutoFillBackground(true);
701:     dock1->setStyleSheet("background-color: rgb(226, 226, 231);");
702: 
703:     addDockWidget(Qt::RightDockWidgetArea, dock1);
704:     viewMenu->addAction(dock1->toggleViewAction());
705: 
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第706-714行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
706:     //动作组调试
707:     QDockWidget *dock = new QDockWidget(tr("动作组调试"), this);
708:     dock->setAllowedAreas(Qt::AllDockWidgetAreas);
709:     right_widget = new QWidget();
710:     right_widget->setLayout(rightContent_23);
711:     right_widget->setSizePolicy(QSizePolicy::Minimum, QSizePolicy::Minimum);
712:     dock->setWidget(right_widget);
713: 
714:     dock->setStyleSheet("background-color: rgb(226, 226, 231);");
```

## mainwindow.cpp | MainWindow::ui_init | 原文件第715-720行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
715:     dock->setSizePolicy(QSizePolicy::Minimum, QSizePolicy::Minimum);
716:     addDockWidget(Qt::RightDockWidgetArea, dock);
717:     viewMenu->addAction(dock->toggleViewAction());
718: 
719: }
720: 
```

## mainwindow.cpp | MainWindow::createActions | 原文件第721-728行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
721: void MainWindow::createActions(){
722:     //
723:     openProjectAction = new QAction(tr("打开工程(&O)"),this);
724:     openProjectAction->setShortcut(tr("ctrl+o"));
725:     connect(openProjectAction,SIGNAL(triggered()),this,SLOT(openProjectFile()));
726: 
727:     saveProjectAction = new QAction(tr("保存工程(&S)"),this);
728:     saveProjectAction->setShortcut(tr("ctrl+s"));
```

## mainwindow.cpp | MainWindow::createActions | 原文件第729-735行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
729:     connect(saveProjectAction,SIGNAL(triggered()),this,SLOT(saveProjectFile()));
730: 
731:     openPlacementAction = new QAction(tr("打开位置(&P)"),this);
732:     openPlacementAction->setShortcut(tr("ctrl+p"));
733:     connect(openPlacementAction,SIGNAL(triggered()),this,SLOT(openPlacementAction_triggered()));
734: 
735:     savePlacementAction = new QAction(tr("保存位置"),this);
```

## mainwindow.cpp | MainWindow::createActions | 原文件第736-742行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
736:     connect(savePlacementAction,SIGNAL(triggered()),this,SLOT(savePlacementAction_triggered()));
737: 
738:     openOffsetAction = new QAction(tr("打开偏差(&B)"),this);
739:     openOffsetAction->setShortcut(tr("ctrl+b"));
740:     connect(openOffsetAction,SIGNAL(triggered()),this,SLOT(openOffsetAction_triggered()));
741: 
742:     saveOffsetAction = new QAction(tr("保存偏差"),this);
```

## mainwindow.cpp | MainWindow::createActions | 原文件第743-749行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
743:     connect(saveOffsetAction,SIGNAL(triggered()),this,SLOT(saveOffsetAction_triggered()));
744: 
745:     openTransactionGroupAction = new QAction(tr("打开动作组(&G)"),this);
746:     openTransactionGroupAction->setShortcut(tr("ctrl+g"));
747:     connect(openTransactionGroupAction,SIGNAL(triggered()),this,SLOT(openTransactionGroupAction_triggered()));
748: 
749:     saveTransactionGroupAction = new QAction(tr("保存动作组"),this);
```

## mainwindow.cpp | MainWindow::createActions | 原文件第750-758行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
750:     connect(saveTransactionGroupAction,SIGNAL(triggered()),this,SLOT(saveTransactionGroupAction_triggered()));
751: 
752:     manDoc = new QAction(tr("帮助文档"),this);
753:     manDoc->setShortcut(tr("F1"));
754:     connect(manDoc,SIGNAL(triggered()),this,SLOT(manDoc_triggered()));
755: 
756: 
757: }
758: 
```

## mainwindow.cpp | MainWindow::createMenus | 原文件第759-771行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
759: void MainWindow::createMenus(){
760: 
761:     menuBar()->clear();
762: 
763:     fileMenu = new QMenu(tr("文件(&F)"),this);
764: 
765:     fileMenu->addAction(openProjectAction);
766: //    fileMenu->addAction(openPlacementAction);
767: //    fileMenu->addAction(openOffsetAction);
768: //    fileMenu->addAction(openTransactionGroupAction);
769:     fileMenu->addSeparator();
770: 
771:     fileMenu->addAction(saveProjectAction);
```

## mainwindow.cpp | MainWindow::createMenus | 原文件第772-782行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
772: //    fileMenu->addAction(savePlacementAction);
773: //    fileMenu->addAction(saveOffsetAction);
774: //    fileMenu->addAction(saveTransactionGroupAction);
775:     menuBar()->addMenu(fileMenu);
776: 
777:     viewMenu = new QMenu(tr("窗口显示(&V)"),this);
778:     menuBar()->addMenu(viewMenu);
779: 
780: //    helpMenu = new QMenu(tr("帮助(&H)"),this);
781: //    helpMenu->addAction(manDoc);
782: //    menuBar()->addMenu(helpMenu);
```

## mainwindow.cpp | MainWindow::createMenus | 原文件第783-786行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
783: 
784: }
785: 
786: //更新动作组表
```

## mainwindow.cpp | MainWindow::updateWindowItem | 原文件第787-795行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
787: void MainWindow::updateWindowItem(int index){
788:     ActionGroup newGroup;
789:     newGroup.init();
790: 
791:     if(actionGroupListMng.actionGroupList.count() == 0) {
792:         actionGroupListMng.currentSelected = 0;
793:         newGroup.setIndex(actionGroupListMng.currentSelected);
794:         actionGroupListMng.actionGroupList.push_back(newGroup);
795:     } else {
```

## mainwindow.cpp | MainWindow::updateWindowItem | 原文件第796-804行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
796:         newGroup = actionGroupListMng.actionGroupList.at(actionGroupListMng.currentSelected);
797:         newGroup.setDisperse(!radioButtonGlobal->isChecked());
798:     }
799: 
800:     ActionGroupItem *item = newGroup.getItem(index);
801:     for (int i = 0;i < MAX_STEER_NUM;i ++){
802:         item->setEnable(dis_arr[i]);
803:         item->setChanged(dis_arr[i]);
804:         if(dis_arr[i]) {
```

## mainwindow.cpp | MainWindow::updateWindowItem | 原文件第805-814行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
805:             item->setId(sc[index]->getId());
806:             item->setPwm(sc[index]->getPwm());
807:             item->setTime(sc[index]->getTime());
808:             item->setBias(sc[index]->getBias());
809:         }
810:     }
811: 
812: 
813:     actionGroupListMng.actionGroupList.removeAt(actionGroupListMng.currentSelected);
814:     actionGroupListMng.actionGroupList.insert(actionGroupListMng.currentSelected,newGroup);
```

## mainwindow.cpp | MainWindow::updateWindowItem | 原文件第815-816行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
815: 
816: }
```

## mainwindow.cpp | MainWindow::updateWindowState | 原文件第817-832行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
817: void MainWindow::updateWindowState(){
818: 
819:     for(int i = 0;i < MAX_STEER_NUM;i ++) {
820:         if(dis_arr[i]) {
821:             sc[i]->setSeed(true);
822:         } else {
823:             sc[i]->setSeed(false);
824:         }
825:         chkBoxDj[i]->setChecked(dis_arr[i]);
826:         if(actionGroupListMng.currentSelected) {
827:             sc[i]->setBiasEnable(false);
828:         }
829:     }
830: 
831: 
832: 
```

## mainwindow.cpp | MainWindow::updateWindowState | 原文件第833-839行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
833: 
834:     if(!actionGroupListMng.actionGroupList.empty()) {
835:         if(last_select < actionGroupListMng.actionGroupList.count()) {
836:             actionList->item(last_select)->setBackgroundColor(Qt::white);
837:             actionList->item(last_select)->setTextColor(Qt::black);
838:         }
839:         actionList->currentItem()->setBackgroundColor(QColor(46,190,251));
```

## mainwindow.cpp | MainWindow::updateWindowState | 原文件第840-850行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
840:         actionList->currentItem()->setTextColor(Qt::white);
841: 
842:         last_select = actionGroupListMng.currentSelected;
843: 
844:         if(actionGroupListMng.currentSelected != 0){
845:             actionList->item(0)->setBackgroundColor(QColor(226,226,231));
846:         }
847:     }
848: 
849: 
850: }
```

## mainwindow.cpp | MainWindow::updateTableList | 原文件第851-859行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
851: void MainWindow::updateTableList(){
852:     actionList->clear();
853:     QList<ActionGroup>::iterator iter;
854:     int i;
855:     for(iter = actionGroupListMng.actionGroupList.begin(), i=0;iter != actionGroupListMng.actionGroupList.end(); iter ++, i++){
856:         QListWidgetItem *newItem = new QListWidgetItem();
857:         iter->setIndex(i);
858: 
859:         for(int j=0;j<MAX_STEER_NUM;j++) {
```

## mainwindow.cpp | MainWindow::updateTableList | 原文件第860-872行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
860:             iter->setItemEnable(j, dis_arr[j]);
861:         }
862: 
863:         if(iter->isGroup()) {
864:             newItem->setText(iter->toDisString());
865:         } else {
866:             newItem->setText(iter->combineCmdStr());
867:         }
868: 
869:         actionList->insertItem(i, newItem);
870:         //actionList->addItem(newItem);
871:     }
872: 
```

## mainwindow.cpp | MainWindow::updateTableList | 原文件第873-877行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
873:     actionList->setCurrentRow(actionGroupListMng.currentSelected);
874: 
875: }
876: 
877: 
```

## mainwindow.cpp | MainWindow::getGroupMaxTime | 原文件第878-888行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
878: int  MainWindow::getGroupMaxTime(ActionGroup &group){
879:     int maxTime = 0;
880:     for(int i = 0;i < MAX_STEER_NUM;i ++){
881:         if(dis_arr[i]) {
882:             int time = group.getItem(i)->Time();
883:             if(time > maxTime){
884:                 maxTime = time;
885:                 //qDebug() << QString::number(i) << ":" << QString::number(maxTime);
886:             }
887:         }
888:     }
```

## mainwindow.cpp | MainWindow::getGroupMaxTime | 原文件第889-891行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
889:     return maxTime;
890: }
891: 
```

## mainwindow.cpp | MainWindow::getGroupMaxTimeFromStr | 原文件第892-901行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
892: int  MainWindow::getGroupMaxTimeFromStr(QString str){
893:     int maxTime = 0;
894:     QRegExp rx("#(\\d+)P(\\d+)T(\\d+)!");
895:     int pos = 0, i = 0;
896:     while (((pos = rx.indexIn(str, pos)) != -1) && (i++ < MAX_STEER_NUM)) {
897:         if(rx.cap(3).toInt() > maxTime) {
898:             maxTime = rx.cap(3).toInt();
899:         }
900:         pos += rx.matchedLength();
901:     }
```

## mainwindow.cpp | MainWindow::getGroupMaxTimeFromStr | 原文件第902-905行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
902:     qDebug() << "getGroupMaxTimeFromStr-maxTime:" <<QString::number(maxTime);
903:     return maxTime;
904: }
905: 
```

## mainwindow.cpp | MainWindow::serialNotOpen | 原文件第906-922行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
906: bool MainWindow::serialNotOpen(){
907:     static bool open_ok = false;
908:     if(!serialOpened){
909:         if(!open_ok) {
910:             QMessageBox::warning(this,tr("温馨提示"),tr("串口没打开,请先打开串口"));
911:             open_ok = true;
912:         }
913:         return true;
914:     }
915:     return false;
916: }
917: 
918: 
919: /************************************************************/
920: //slots
921: 
922: 
```

## mainwindow.cpp | MainWindow::pushButtonDataSend_clicked | 原文件第923-929行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
923: void MainWindow::pushButtonDataSend_clicked(){
924:     if(serialNotOpen()){
925:         return;
926:     }
927:     uart_send_str(dataSendEdit->toPlainText());
928: }
929: 
```

## mainwindow.cpp | MainWindow::pbtnSerialLed_clicked | 原文件第930-934行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
930: void MainWindow::pbtnSerialLed_clicked() {
931:     static bool flag = false;
932:     qDebug() << "pbtnSerialLed_clicked";
933: }
934: 
```

## mainwindow.cpp | MainWindow::btn_ok_clicked | 原文件第935-939行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
935: void MainWindow::btn_ok_clicked(){
936: 
937:     qDebug() << "btn_ok click!";
938: }
939: 
```

## mainwindow.cpp | MainWindow::btn_setting_clicked | 原文件第940-945行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
940: void MainWindow::btn_setting_clicked(){
941: 
942:     qDebug() << "btn_stting click!";
943: 
944: }
945: 
```

## mainwindow.cpp | MainWindow::pbtnDoActionOnline_clicked | 原文件第946-958行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
946: void MainWindow::pbtnDoActionOnline_clicked() {
947:     //检查串口是否打开
948:     if(!comOpened) {
949:         QMessageBox::warning(this,tr("温馨提示"),tr("串口没打开,请先打开串口"));
950:         return;
951:     }
952: 
953:     //检查是否有动作组
954:     if((!radioButtonOnline->isChecked()) && (actionGroupListMng.actionGroupList.count() == 0)){
955:          QMessageBox::warning(this,tr("提示"),tr("请添加动作组"));
956:          return;
957:     }
958: 
```

## mainwindow.cpp | MainWindow::pbtnDoActionOnline_clicked | 原文件第959-970行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
959:     actionIndexDoOnceOk = false;
960:     startActionIndex = spinBoxStartGroup->value();
961:     endActionIndex = spinBoxEndGroup->value();
962:     timesToDo = spinBoxDoTimes->value();
963: 
964:     if(timesToDo == 0) {
965:         doForever = true;
966:     } else {
967:         doForever = false;
968:     }
969: 
970:     if((startActionIndex == 0) && (endActionIndex == 0)){
```

## mainwindow.cpp | MainWindow::pbtnDoActionOnline_clicked | 原文件第971-980行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
971:         //endActionIndex = actionGroupListMng.actionGroupList.count()-1;
972:         return;
973:     }
974: 
975: 
976:     if(startActionIndex >= actionGroupListMng.actionGroupList.count() ){
977:         startActionIndex = actionGroupListMng.actionGroupList.count()-1;
978:     }
979: 
980:     if(endActionIndex >= actionGroupListMng.actionGroupList.count()){
```

## mainwindow.cpp | MainWindow::pbtnDoActionOnline_clicked | 原文件第981-992行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
981:         endActionIndex = actionGroupListMng.actionGroupList.count()-1;
982:     }
983: 
984:     startActionIndexBak = startActionIndex;
985:     endActionIndexBak = endActionIndex;
986: 
987: 
988:     qDebug() << "Online Action";
989:     doGroupActionsOnline = true;
990:     if(doGroupActionsOnline){
991:         doGroupActionsOffline = false;
992:         musicTimeCount = 0;
```

## mainwindow.cpp | MainWindow::pbtnDoActionOnline_clicked | 原文件第993-1001行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
993:         //pbtnDoActionOnline->setText(tr("停止执行"));
994:         pbtnDoActionOffline->setText(tr("脱机执行"));
995:         uart_send_str("$DST!");
996:         actionTimer->start(1000);
997:         actionDisTimer->start(1000);
998:         pbtnDoActionOnline->setStyleSheet(pbtnStyle_actived);
999:         pbtnDoActionOffline->setStyleSheet(pbtnStyle_normal);
1000: //    } else {
1001: //        uart_send_str("$DST!");
```

## mainwindow.cpp | MainWindow::pbtnDoActionOnline_clicked | 原文件第1002-1008行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1002: //        pbtnDoActionOnline->setText(tr("在线执行"));
1003: //        pbtnDoActionOffline->setText(tr("脱机执行"));
1004: //        actionDisTimer->stop();
1005:     }
1006: 
1007: }
1008: 
```

## mainwindow.cpp | MainWindow::pbtnDoActionOffline_clicked | 原文件第1009-1020行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1009: void MainWindow::pbtnDoActionOffline_clicked() {
1010:     //检查串口是否打开
1011:     if(!comOpened) {
1012:         QMessageBox::warning(this,tr("温馨提示"),tr("串口没打开,请先打开串口"));
1013:         return;
1014:     }
1015: 
1016:     //检查是否有动作组
1017:     if((!radioButtonOnline->isChecked()) && (actionGroupListMng.actionGroupList.count() == 0)){
1018:          QMessageBox::warning(this,tr("提示"),tr("请添加动作组"));
1019:          return;
1020:     }
```

## mainwindow.cpp | MainWindow::pbtnDoActionOffline_clicked | 原文件第1021-1033行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1021: 
1022:     actionIndexDoOnceOk = false;
1023:     startActionIndex = spinBoxStartGroup->value();
1024:     endActionIndex = spinBoxEndGroup->value();
1025:     timesToDo = spinBoxDoTimes->value();
1026: 
1027:     if(timesToDo == 0) {
1028:         doForever = true;
1029:     } else {
1030:         doForever = false;
1031:     }
1032: 
1033:     if((startActionIndex == 0) && (endActionIndex == 0)){
```

## mainwindow.cpp | MainWindow::pbtnDoActionOffline_clicked | 原文件第1034-1043行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1034:         //endActionIndex = actionGroupListMng.actionGroupList.count()-1;
1035:         return;
1036:     }
1037: 
1038: 
1039:     if(startActionIndex >= actionGroupListMng.actionGroupList.count() ){
1040:         startActionIndex = actionGroupListMng.actionGroupList.count()-1;
1041:     }
1042: 
1043:     if(endActionIndex >= actionGroupListMng.actionGroupList.count()){
```

## mainwindow.cpp | MainWindow::pbtnDoActionOffline_clicked | 原文件第1044-1055行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1044:         endActionIndex = actionGroupListMng.actionGroupList.count()-1;
1045:     }
1046: 
1047:     startActionIndexBak = startActionIndex;
1048:     endActionIndexBak = endActionIndex;
1049: 
1050: 
1051:     qDebug() << "Offline Action";
1052: //    doGroupActionsOffline = !doGroupActionsOffline;
1053: //    if(doGroupActionsOffline){
1054:         doGroupActionsOffline = true;
1055:         doGroupActionsOnline = false;
```

## mainwindow.cpp | MainWindow::pbtnDoActionOffline_clicked | 原文件第1056-1064行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1056:         QString cmd;
1057:         int time = 0;
1058: //        if(spinBoxStartGroup->value() == spinBoxEndGroup->value()) {
1059: //            time = 1;
1060: //        } else {
1061:             time = spinBoxDoTimes->value();
1062: //        }
1063:         cmd = "$DGT:" + QString::number(spinBoxStartGroup->value()) + "-"
1064:                   + QString::number(spinBoxEndGroup->value()) + ","
```

## mainwindow.cpp | MainWindow::pbtnDoActionOffline_clicked | 原文件第1065-1073行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1065:                   + QString::number(time) + "!";
1066:         uart_send_str(cmd);
1067:         pbtnDoActionOnline->setText("在线执行");
1068:         //pbtnDoActionOffline->setText("停止执行");
1069:         actionDisTimer->start(1000);
1070:         musicTimeCount = 0;
1071:         pbtnDoActionOffline->setStyleSheet(pbtnStyle_actived);
1072:         pbtnDoActionOnline->setStyleSheet(pbtnStyle_normal);
1073: //    } else {
```

## mainwindow.cpp | MainWindow::pbtnDoActionOffline_clicked | 原文件第1074-1082行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1074: //        uart_send_str("$DST!");
1075: //        pbtnDoActionOnline->setText("在线执行");
1076: //        pbtnDoActionOffline->setText(tr("脱机执行"));
1077: //        actionDisTimer->stop();
1078: 
1079: //    }
1080: 
1081: }
1082: 
```

## mainwindow.cpp | MainWindow::pbtnDoActionStop_clicked | 原文件第1083-1092行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1083: void MainWindow::pbtnDoActionStop_clicked() {
1084:     doGroupActionsOnline = false;
1085:     doGroupActionsOffline = false;
1086:     uart_send_str("$DST!");
1087:     pbtnDoActionOnline->setText(tr("在线执行"));
1088:     pbtnDoActionOffline->setText(tr("脱机执行"));
1089:     pbtnDoActionOffline->setStyleSheet(pbtnStyle_normal);
1090:     pbtnDoActionOnline->setStyleSheet(pbtnStyle_normal);
1091:     actionDisTimer->stop();
1092: }
```

## mainwindow.cpp | MainWindow::pbtnDoActionStop_clicked | 原文件第1093-1093行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1093: 
```

## mainwindow.cpp | MainWindow::pbtnDoAction_reset_clicked | 原文件第1094-1102行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1094: void MainWindow::pbtnDoAction_reset_clicked() {
1095:     doGroupActionsOnline = false;
1096:     doGroupActionsOffline = false;
1097:     uart_send_str("$RST!");
1098:     pbtnDoActionOnline->setText(tr("在线执行"));
1099:     pbtnDoActionOffline->setText(tr("脱机执行"));
1100:     pbtnDoActionOffline->setStyleSheet(pbtnStyle_normal);
1101:     pbtnDoActionOnline->setStyleSheet(pbtnStyle_normal);
1102:     actionDisTimer->stop();
```

## mainwindow.cpp | MainWindow::pbtnDoAction_reset_clicked | 原文件第1103-1104行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1103: }
1104: 
```

## mainwindow.cpp | MainWindow::pbtnDoAction_read_clicked | 原文件第1105-1108行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1105: void MainWindow::pbtnDoAction_read_clicked() {
1106:     uart_send_str("$DRS!");
1107: }
1108: 
```

## mainwindow.cpp | MainWindow::pbtnDoAction_clear_clicked | 原文件第1109-1114行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1109: void MainWindow::pbtnDoAction_clear_clicked() {
1110:     uart_send_str("<$!>");
1111: }
1112: 
1113: 
1114: 
```

## mainwindow.cpp | MainWindow::pbtnDoActionSave_clicked | 原文件第1115-1126行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1115: void MainWindow::pbtnDoActionSave_clicked() {
1116:     QString cmd;
1117:     int times = 0;
1118:     times = spinBoxDoTimes->value();
1119:     cmd = "<$DGT:" + QString::number(spinBoxStartGroup->value()) + "-"
1120:               + QString::number(spinBoxEndGroup->value()) + ","
1121:               + QString::number(times) + "!>";
1122:     uart_send_str(cmd);
1123: }
1124: 
1125: 
1126: 
```

## mainwindow.cpp | MainWindow::autosave_timeout | 原文件第1127-1131行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1127: void MainWindow::autosave_timeout(){
1128:     saveProjectFile(saveDefaultFileName);
1129:     autoSaveTimer->start(5000);
1130: }
1131: 
```

## mainwindow.cpp | MainWindow::ackDownCheckTimer_timeout | 原文件第1132-1137行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1132: void MainWindow::ackDownCheckTimer_timeout(){
1133: 
1134:     return;
1135: }
1136: 
1137: 
```

## mainwindow.cpp | MainWindow::actionTimer_timeout | 原文件第1138-1146行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1138: void MainWindow::actionTimer_timeout(){
1139:     int maxTime = 1000;
1140: 
1141:     //执行动作组
1142:     if( doGroupActionsOnline) {//执行动作组
1143: 
1144:         actionList->setCurrentRow(startActionIndex);
1145:         if(last_select < actionGroupListMng.actionGroupList.count()) {
1146:             actionList->item(last_select)->setBackgroundColor(Qt::white);
```

## mainwindow.cpp | MainWindow::actionTimer_timeout | 原文件第1147-1155行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1147:             actionList->item(last_select)->setTextColor(Qt::black);
1148:         }
1149:         actionList->currentItem()->setBackgroundColor(QColor(46,190,251));
1150:         actionList->currentItem()->setTextColor(Qt::white);
1151: 
1152:         last_select = startActionIndex;
1153:         actionGroupListMng.currentSelected = last_select;
1154: 
1155:         if(actionGroupListMng.currentSelected != 0){
```

## mainwindow.cpp | MainWindow::actionTimer_timeout | 原文件第1156-1165行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1156:             actionList->item(0)->setBackgroundColor(QColor(226,226,231));
1157:         }
1158: 
1159:         if(doGroupActionsStop) {
1160:             doGroupActionsOnline = false;
1161:             doGroupActionsStop = false;
1162:             musicTimeCount = 0;
1163:             actionDisTimer->stop();
1164:             uart_send_str("$DST!");
1165:             pbtnDoActionOnline->setStyleSheet(pbtnStyle_normal);
```

## mainwindow.cpp | MainWindow::actionTimer_timeout | 原文件第1166-1174行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1166:         } else {
1167:             if(startActionIndex != endActionIndex) {
1168: 
1169:                 QString cmd = actionList->item(startActionIndex)->text();
1170:                 uart_send_str(cmd);
1171:                 maxTime = getGroupMaxTimeFromStr(cmd);// + spinBoxDelayTimes->value();
1172:                 qDebug() << "GETMAXTIME:" << QString::number(maxTime);
1173: 
1174:                 if(maxTime<100) {
```

## mainwindow.cpp | MainWindow::actionTimer_timeout | 原文件第1175-1183行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1175:                     maxTime = 100;
1176:                 }
1177: 
1178:                 uart_get_show("在线执行第"+QString::number(startActionIndex)+"组");
1179:                 if(startActionIndex < endActionIndex) {
1180:                     startActionIndex++;
1181:                 } else {
1182:                     startActionIndex--;
1183:                 }
```

## mainwindow.cpp | MainWindow::actionTimer_timeout | 原文件第1184-1191行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1184:                 if(startActionIndex == endActionIndex)actionIndexDoOnceOk=true;
1185: 
1186:             } else {
1187:                 if(actionIndexDoOnceOk) {
1188:                     actionIndexDoOnceOk = false;
1189:                     QString cmd = actionList->item(startActionIndex)->text();
1190:                     uart_send_str(cmd);
1191: 
```

## mainwindow.cpp | MainWindow::actionTimer_timeout | 原文件第1192-1197行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1192:                     maxTime = getGroupMaxTimeFromStr(cmd);// + spinBoxDelayTimes->value();
1193:                     //qDebug() << "GETMAXTIME:" << QString::number(maxTime)<< "-" << QString::number(spinBoxDelayTimes->value());
1194:                     if(maxTime<100) {
1195:                         maxTime = 100;
1196:                     }
1197:                     uart_get_show("正在执行第"+QString::number(startActionIndex)+"组");
```

## mainwindow.cpp | MainWindow::actionTimer_timeout | 原文件第1198-1205行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1198:                     uart_get_show("======>第"+QString::number(timesToDo)+"次执行完毕");
1199:                 } else {
1200:                     if(doForever) {
1201:                         maxTime = 100;
1202:                     } else {
1203:                         timesToDo --;
1204:                         if(timesToDo == 0) {
1205:                             if(doGroupActionsOnline) {
```

## mainwindow.cpp | MainWindow::actionTimer_timeout | 原文件第1206-1212行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1206:                                 doGroupActionsOnline = false;
1207:                                 pbtnDoActionOnline->setStyleSheet(pbtnStyle_normal);
1208:                                 pbtnDoActionOnline->setText(tr("在线执行"));
1209:                             }
1210:                             doForever = false;
1211:                             actionDisTimer->stop();
1212:                         } else {
```

## mainwindow.cpp | MainWindow::actionTimer_timeout | 原文件第1213-1219行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1213:                             uart_get_show("还剩"+QString::number(timesToDo)+"次");
1214:                         }
1215:                         maxTime = 100;
1216:                     }
1217:                     startActionIndex = startActionIndexBak;
1218:                     endActionIndex = endActionIndexBak;
1219:                     if((startActionIndex == 0) && (endActionIndex == 0)){
```

## mainwindow.cpp | MainWindow::actionTimer_timeout | 原文件第1220-1227行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1220:                         endActionIndex = actionGroupListMng.actionGroupList.count()-1;
1221:                     }
1222: 
1223: 
1224:                     if(startActionIndex >= actionGroupListMng.actionGroupList.count() ){
1225:                         startActionIndex = actionGroupListMng.actionGroupList.count()-1;
1226:                     }
1227: 
```

## mainwindow.cpp | MainWindow::actionTimer_timeout | 原文件第1228-1241行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1228:                     if(endActionIndex >= actionGroupListMng.actionGroupList.count()){
1229:                         endActionIndex = actionGroupListMng.actionGroupList.count()-1;
1230:                     }
1231:                 }
1232:             }
1233:         }
1234:     } else {
1235:         maxTime = 1000;
1236:     }
1237: 
1238:     actionTimer->start(maxTime);
1239:     //qDebug() << "dj time do";
1240: }
1241: 
```

## mainwindow.cpp | MainWindow::pbtnResetPwm_clicked | 原文件第1242-1251行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1242: void MainWindow::pbtnResetPwm_clicked(){
1243:     data_send_flag = false;
1244:     for(int i = 0;i < MAX_STEER_NUM;i ++){
1245:         sc[i]->setPwm(1500);
1246:     }
1247: 
1248:     spinBoxPwmControl->setValue(1500);
1249:     data_send_flag = true;
1250: }
1251: 
```

## mainwindow.cpp | MainWindow::pbtnPwmReset_clicked | 原文件第1252-1262行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1252: void MainWindow::pbtnPwmReset_clicked(){
1253:     qDebug() << "pbtnPwmReset_clicked";
1254:     data_send_flag = false;
1255:     for(int i = 0;i < MAX_STEER_NUM;i ++){
1256:         sc[i]->setPwm(1500);
1257:         updateWindowItem(i);
1258:     }
1259:     updateTableList();
1260:     data_send_flag = true;
1261: 
1262:     actionList->currentItem()->setBackgroundColor(QColor(46,190,251));
```

## mainwindow.cpp | MainWindow::pbtnPwmReset_clicked | 原文件第1263-1267行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1263:     actionList->currentItem()->setTextColor(Qt::green);
1264: 
1265:     uart_send_str(actionList->currentItem()->text());
1266: }
1267: 
```

## mainwindow.cpp | MainWindow::pbtnTimeReset_clicked | 原文件第1268-1279行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1268: void MainWindow::pbtnTimeReset_clicked()
1269: {
1270:     qDebug() << "pbtnTimeReset_clicked";
1271:     data_send_flag = false;
1272:     for(int i = 0;i < MAX_STEER_NUM;i ++){
1273:         sc[i]->setTime(1000);
1274:         updateWindowItem(i);
1275:     }
1276:     updateTableList();
1277:     data_send_flag = true;
1278:     //spinBoxTimeControl->setValue(1000);
1279: 
```

## mainwindow.cpp | MainWindow::pbtnTimeReset_clicked | 原文件第1280-1288行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1280:     actionList->currentItem()->setBackgroundColor(QColor(46,190,251));
1281:     actionList->currentItem()->setTextColor(Qt::white);
1282: 
1283:     //uart_send_str(actionList->currentItem()->text());
1284: }
1285: 
1286: 
1287: 
1288: 
```

## mainwindow.cpp | MainWindow::pbtnResetBias_clicked | 原文件第1289-1299行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1289: void MainWindow::pbtnResetBias_clicked(){
1290:     data_send_flag = false;
1291:     if(actionGroupListMng.currentSelected == 0) {
1292:         for(int i = 0;i < MAX_STEER_NUM;i ++){
1293:             sc[i]->setBias(0);
1294:         }
1295:         spinBoxBiasControl->setValue(0);
1296:     }
1297:     data_send_flag = true;
1298: }
1299: 
```

## mainwindow.cpp | MainWindow::pbtnResetTime_clicked | 原文件第1300-1312行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1300: void MainWindow::pbtnResetTime_clicked()
1301: {
1302:     data_send_flag = false;
1303:     for(int i = 0;i < MAX_STEER_NUM;i ++){
1304:         sc[i]->setTime(spinBoxTimeControl->value());
1305:     }
1306:     data_send_flag = true;
1307:     //spinBoxTimeControl->setValue(1000);
1308: }
1309: 
1310: 
1311: 
1312: 
```

## mainwindow.cpp | MainWindow::hsliderTimeControl_valueChanged | 原文件第1313-1324行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1313: void MainWindow::hsliderTimeControl_valueChanged(int val){
1314:     spinBoxTimeControl->setValue(val);
1315:     for(int i = 0;i < MAX_STEER_NUM;i ++){
1316:         sc[i]->setTime(val);
1317:     }
1318: }
1319: 
1320: //void MainWindow::pushButtonSelectSteers_clicked(){
1321: //    QString idString = lineEditSteerIds->text();
1322: //    if(0 == idString.length()){
1323: //        return ;
1324: //    }
```

## mainwindow.cpp | MainWindow::hsliderTimeControl_valueChanged | 原文件第1325-1333行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1325: //    bool isSelect[MAX_STEER_NUM] = {false};
1326: //    QStringList list1 = idString.split(',');
1327: //    QStringList::iterator iter =  list1.begin();
1328: //    while(iter != list1.end()){
1329: //        QString idForm = *iter;
1330: //        //qDebug() << idForm << endl;
1331: //        QStringList idlist = idForm.split('-');
1332: //        if(idlist.count() == 1){
1333: //            int index = idlist.at(0).toInt();
```

## mainwindow.cpp | MainWindow::hsliderTimeControl_valueChanged | 原文件第1334-1342行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1334: //            if(index > 31)
1335: //                index = 31;
1336: //            isSelect[index] = true;
1337: //        }
1338: //        else if(idlist.count() == 2) {
1339: //            //qDebug() << idlist.at(0) << "-" << idlist.at(1);
1340: //            int firstindex = idlist.at(0).toInt();
1341: //            int lastindex = idlist.at(1).toInt();
1342: //            if(lastindex > 31)
```

## mainwindow.cpp | MainWindow::hsliderTimeControl_valueChanged | 原文件第1343-1353行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1343: //                lastindex = 31;
1344: //            if(firstindex > lastindex){
1345: //                int temp = firstindex;
1346: //                firstindex = lastindex;
1347: //                lastindex = temp;
1348: //            }
1349: //            for(int j = firstindex;j <= lastindex;j ++){
1350: //                isSelect[j] = true;
1351: //            }
1352: //        }
1353: //        else {
```

## mainwindow.cpp | MainWindow::hsliderTimeControl_valueChanged | 原文件第1354-1367行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1354: //            //there must be something error
1355: //        }
1356: //        iter ++;
1357: //    }
1358: 
1359: //    for(int i = 0;i < MAX_STEER_NUM;i ++){
1360: //        if(isSelect[i]){
1361: //            sc[i]->setVisible(true);
1362: //            add_steer_enable(i, true);
1363: //            dis_arr[i] = true;
1364: //        }
1365: ////        else {
1366: ////            sc[i]->unVisible();
1367: ////        }
```

## mainwindow.cpp | MainWindow::hsliderTimeControl_valueChanged | 原文件第1368-1371行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1368: //    }
1369: 
1370: //}
1371: 
```

## mainwindow.cpp | MainWindow::addBiasStr | 原文件第1372-1380行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1372: QString MainWindow::addBiasStr(QString str) {
1373:     int i, index[MAX_STEER_NUM], pwm[MAX_STEER_NUM], time[MAX_STEER_NUM], cur_index = 0;
1374:     int len = str.length(), group_num = 0;
1375:     char *tchar_begin = str.toLatin1().data();
1376:     QString return_str;
1377:     for(i=0;i<len;i++) {
1378:         if(*(tchar_begin+i) == 'G') {
1379:             group_num = 0;
1380:             i++;
```

## mainwindow.cpp | MainWindow::addBiasStr | 原文件第1381-1388行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1381:             while((*(tchar_begin+i) != '#') && i<len) {
1382:                group_num = group_num*10 + *(tchar_begin+i) - '0';
1383:                i++;
1384:             }
1385:         } else if(*(tchar_begin+i) == '#') {
1386:             index[cur_index] = 0;
1387:             i++;
1388:             while((*(tchar_begin+i) != 'P') && i<len) {
```

## mainwindow.cpp | MainWindow::addBiasStr | 原文件第1389-1398行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1389:                index[cur_index] = index[cur_index]*10 + *(tchar_begin+i) - '0';
1390:                i++;
1391:             }
1392:             pwm[cur_index] = 0;
1393:             i++;
1394:             while((*(tchar_begin+i) != 'T') && i<len) {
1395:                pwm[cur_index] = pwm[cur_index]*10 + *(tchar_begin+i) - '0';
1396:                i++;
1397:             }
1398:             time[cur_index] = 0;
```

## mainwindow.cpp | MainWindow::addBiasStr | 原文件第1399-1410行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1399:             i++;
1400:             while((*(tchar_begin+i) != '!') && i<len) {
1401:                time[cur_index] = time[cur_index]*10 + *(tchar_begin+i) - '0';
1402:                i++;
1403:             }
1404:             cur_index++;
1405:         }
1406: 
1407:     }
1408:     return_str.clear();
1409:     if(*(tchar_begin+0) != '{') {
1410:         return_str = "{G" + QString::number(group_num);
```

## mainwindow.cpp | MainWindow::addBiasStr | 原文件第1411-1418行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1411:         for(i=0;i<cur_index;i++) {
1412:             return_str += "#" + QString::number(index[i]) +
1413:                         "P" + QString::number(pwm[i]+sc[index[i]]->getBias()) +
1414:                         "T" + QString::number(time[i]) + "!";
1415:         }
1416:         return_str += "}";
1417:     } else if(*(tchar_begin+0) != '<') {
1418:         return_str = "<G" + QString::number(group_num);
```

## mainwindow.cpp | MainWindow::addBiasStr | 原文件第1419-1429行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1419:         for(i=0;i<cur_index;i++) {
1420:             return_str += "#" + QString::number(index[i]) +
1421:                         "P" + QString::number(pwm[i]+sc[index[i]]->getBias()) +
1422:                         "T" + QString::number(time[i]) + "!";
1423:         }
1424:         return_str += ">";
1425:     }
1426: 
1427:     return return_str;
1428: }
1429: 
```

## mainwindow.cpp | MainWindow::actionList_clicked | 原文件第1430-1440行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1430: void MainWindow::actionList_clicked(QModelIndex index){
1431: 
1432: 
1433:     actionGroupListMng.currentSelected = index.row();
1434:     startDloadAction = actionGroupListMng.currentSelected;
1435:     ActionGroup group = actionGroupListMng.actionGroupList.at(actionGroupListMng.currentSelected);
1436: 
1437:     if(actionGroupListMng.currentSelected) {
1438:         actionList_double_clicked_fisrt = true;
1439:     }
1440: 
```

## mainwindow.cpp | MainWindow::actionList_clicked | 原文件第1441-1452行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1441:     qDebug() << "function start:actionList_clicked";
1442:     list_click = true;
1443: 
1444:     //更新控件
1445:     for(int i = 0;i < MAX_STEER_NUM;i++){
1446:         ActionGroupItem *item = group.getItem(i);
1447:         if(actionGroupListMng.currentSelected == 0) {
1448:             sc[i]->setBiasEnable(true);
1449:             sc[i]->setTime(1000);
1450:             sc[i]->setPwm(1500);
1451: 
1452:         } else {
```

## mainwindow.cpp | MainWindow::actionList_clicked | 原文件第1453-1462行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1453:             sc[i]->setTime(item->Time());
1454:             sc[i]->setPwm(item->Pwm());
1455:         }
1456: 
1457:     }
1458:     if(actionGroupListMng.currentSelected == 0) {
1459:         QString cmd = "", tempDjStr;
1460:         cmd = cmd.sprintf("{G%04d",index.row());
1461:         for(int i=0;i<MAX_STEER_NUM; i++) {
1462:             if(dis_arr[i]) {
```

## mainwindow.cpp | MainWindow::actionList_clicked | 原文件第1463-1475行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1463:                 tempDjStr.sprintf("#%03dP%04dT%04d!", sc[i]->getId(), sc[i]->getPwm() + sc[i]->getBias(), sc[i]->getTime());
1464:                 cmd = cmd+ tempDjStr;
1465:                 updateWindowItem(i);
1466:             }
1467: 
1468:         }
1469:         cmd = cmd+ "}";
1470:         uart_send_str(cmd);
1471: 
1472:         updateTableList();
1473:     }
1474:     updateWindowState();
1475:     list_click = false;
```

## mainwindow.cpp | MainWindow::actionList_clicked | 原文件第1476-1484行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1476: 
1477:     for(int i = 0;i < MAX_STEER_NUM;i++){
1478:         sc[i]->spbxClearFocus();
1479:     }
1480: 
1481:     qDebug() << "function end:actionList_clicked";
1482: }
1483: 
1484: 
```

## mainwindow.cpp | MainWindow::actionList_doubleClick | 原文件第1485-1495行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1485: void MainWindow::actionList_doubleClick(QModelIndex index){
1486:     qDebug() << "function start:actionList_doubleClick";
1487:     list_click = true;
1488:     actionList_double_clicked = true;
1489: 
1490:     QString tempDjStr;
1491:     QString cmd = "";
1492: 
1493:     cmd = cmd.sprintf("{G%04d",index.row());
1494:     for(int i=0;i<MAX_STEER_NUM; i++) {
1495:         if(dis_arr[i]) {
```

## mainwindow.cpp | MainWindow::actionList_doubleClick | 原文件第1496-1500行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1496:             //tempDjStr.sprintf("#%03dP%04dT%04d!", sc[i]->getId(), sc[i]->getPwm(), sc[i]->getTime());
1497:             tempDjStr.sprintf("#%03dP%04dT%04d!", sc[i]->getId(), sc[i]->getPwm() + sc[i]->getBias(), sc[i]->getTime());
1498:             if(index.row() == 0) {
1499:                 sc[i]->setBiasEnable(true);
1500:                 sc[i]->setPwm(1500);
```

## mainwindow.cpp | MainWindow::actionList_doubleClick | 原文件第1501-1514行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1501:                 //tempDjStr.sprintf("#%03dP%04dT%04d!", sc[i]->getId(), sc[i]->getPwm() + sc[i]->getBias(), sc[i]->getTime());
1502:             }
1503:             cmd = cmd+ tempDjStr;
1504:         }
1505: 
1506:     }
1507:     cmd = cmd+ "}";
1508:     uart_send_str(cmd);
1509: 
1510:     list_click = false;
1511:     qDebug() << "function end:actionList_doubleClick";
1512: }
1513: 
1514: //保存界面上舵机的位置
```

## mainwindow.cpp | MainWindow::savePlacementAction_triggered | 原文件第1515-1524行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1515: void MainWindow::savePlacementAction_triggered(){
1516:     QString filename = QFileDialog::getSaveFileName(this,tr("保存文件"),0,tr("INI文件(*.ini)\n所有文件(*.*)"));
1517:     if(!filename.length()) {
1518:         return;
1519:     }
1520: 
1521:     QSettings *configIni = new QSettings(filename, QSettings::IniFormat, 0);
1522:     configIni->setIniCodec("UTF-8");
1523: 
1524:     for(int i = 0;i < MAX_STEER_NUM;i ++){
```

## mainwindow.cpp | MainWindow::savePlacementAction_triggered | 原文件第1525-1537行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1525:         QString block = QString("steer%1").arg(i);
1526:         QString xkey = QString(block).append("/x");
1527:         configIni->setValue(xkey,sc[i]->x());
1528:         QString ykey = QString(block).append("/y");
1529:         configIni->setValue(ykey, sc[i]->y());
1530: 
1531:     }
1532:     delete configIni;
1533: 
1534:     return ;
1535: }
1536: 
1537: 
```

## mainwindow.cpp | MainWindow::openPlacementAction_triggered | 原文件第1538-1546行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1538: void MainWindow::openPlacementAction_triggered(){
1539:     QString filename = QFileDialog::getOpenFileName(this, tr("打开文件"), 0, tr("INI文件(*.ini)\n所有文件(*.*)"));  //添加更多的文件类型
1540:     if(!filename.length()){
1541:         return ;
1542:     }
1543: 
1544:     QSettings *configIniRead = new QSettings(filename, QSettings::IniFormat, 0);
1545:     configIniRead->setIniCodec("UTF-8");
1546: 
```

## mainwindow.cpp | MainWindow::openPlacementAction_triggered | 原文件第1547-1555行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1547:     for(int i = 0;i < MAX_STEER_NUM;i ++){
1548:         QString block = QString("steer%1").arg(i);
1549:         QString xkey = QString(block).append("/x");
1550:         QString ykey = QString(block).append("/y");
1551:         int x = configIniRead->value(xkey,"-1").toInt();
1552:         int y = configIniRead->value(ykey,"-1").toInt();
1553:         if(x == -1 && y == -1){
1554: 
1555:             //key不存在
```

## mainwindow.cpp | MainWindow::openPlacementAction_triggered | 原文件第1556-1567行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1556:             continue;
1557:         }
1558: 
1559:         sc[i]->move(x,y);
1560: 
1561:     }
1562:     delete configIniRead;
1563:     return ;
1564: }
1565: 
1566: 
1567: //保存舵机的偏差
```

## mainwindow.cpp | MainWindow::saveOffsetAction_triggered | 原文件第1568-1577行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1568: void MainWindow::saveOffsetAction_triggered(){
1569:     QString filename = QFileDialog::getSaveFileName(this,tr("保存偏差"),0,tr("INI文件(*.ini)\n所有文件(*.*)"));
1570:     if(!filename.length()) {
1571:         return;
1572:     }
1573: 
1574:     QSettings *configIni = new QSettings(filename, QSettings::IniFormat, 0);
1575:     configIni->setIniCodec("UTF-8");
1576: 
1577:     for(int i = 0;i < MAX_STEER_NUM;i ++){
```

## mainwindow.cpp | MainWindow::saveOffsetAction_triggered | 原文件第1578-1587行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1578:         QString block = QString("steer%1").arg(i);
1579:         QString offsetkey = QString(block).append("/bias");
1580:         configIni->setValue(offsetkey,sc[i]->getBias());
1581:     }
1582:     delete configIni;
1583: 
1584:     return ;
1585: }
1586: 
1587: 
```

## mainwindow.cpp | MainWindow::openOffsetAction_triggered | 原文件第1588-1596行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1588: void MainWindow::openOffsetAction_triggered(){
1589:     QString filename = QFileDialog::getOpenFileName(this, tr("打开文件"), 0, tr("INI文件(*.ini)\n所有文件(*.*)"));  //添加更多的文件类型
1590:     if(!filename.length()){
1591:         return ;
1592:     }
1593: 
1594:     QSettings *configIniRead = new QSettings(filename, QSettings::IniFormat, 0);
1595:     configIniRead->setIniCodec("UTF-8");
1596:     for(int i = 0;i < MAX_STEER_NUM;i ++){
```

## mainwindow.cpp | MainWindow::openOffsetAction_triggered | 原文件第1597-1612行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1597:         QString block = QString("steer%1").arg(i);
1598:         QString offsetkey = QString(block).append("/bias");
1599:         int bias = configIniRead->value(offsetkey,"-3000").toInt();
1600:         if(bias == -3000){
1601:             continue;
1602:         }
1603: 
1604: 
1605:         sc[i]->setBias(bias);
1606: 
1607:     }
1608:     delete configIniRead;
1609:     return ;
1610: }
1611: 
1612: 
```

## mainwindow.cpp | MainWindow::openTransactionGroupAction_triggered | 原文件第1613-1621行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1613: void MainWindow::openTransactionGroupAction_triggered(){
1614: 
1615:     QString filename = QFileDialog::getOpenFileName(this, tr("打开文件"), 0, tr("INI文件(*.ini)\n所有文件(*.*)"));  //添加更多的文件类型
1616:     if(!filename.length()){
1617:         return ;
1618:     }
1619: 
1620:     QSettings *configIniRead = new QSettings(filename, QSettings::IniFormat, 0);
1621:     configIniRead->setIniCodec("UTF-8");
```

## mainwindow.cpp | MainWindow::openTransactionGroupAction_triggered | 原文件第1622-1635行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1622:     QString block = QString("group");
1623:     int i = 0;
1624:     while(1){
1625:         QString key = QString(block).append("/G%1").arg(i); //
1626:         QString str = configIniRead->value(key,"").toString();
1627: 
1628:         if(str.length() == 0){
1629:             break;
1630:         }
1631: 
1632:         QRegExp rx("(\\d+)P(\\d+)T(\\d+)");
1633: 
1634:         ActionGroup group;
1635:         group.setIndex(i);
```

## mainwindow.cpp | MainWindow::openTransactionGroupAction_triggered | 原文件第1636-1645行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1636:         int pos = 0, j = 0;
1637:         while ((pos = rx.indexIn(str, pos)) != -1) {
1638:             ActionGroupItem item;
1639:             item.setEnable(true);
1640:             item.setId(rx.cap(1).toInt());
1641:             item.setPwm(rx.cap(2).toInt());
1642:             item.setTime(rx.cap(3).toInt());
1643:             group.addItem(item, j);
1644:             pos += rx.matchedLength();
1645:             j++;
```

## mainwindow.cpp | MainWindow::openTransactionGroupAction_triggered | 原文件第1646-1658行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1646:         }
1647:         actionGroupListMng.actionGroupList.push_back(group);
1648: 
1649:         i ++;
1650: 
1651:     }
1652:     actionGroupListMng.currentSelected = 0;
1653:     updateTableList();
1654:     updateWindowState();
1655: 
1656:     delete configIniRead;
1657: }
1658: 
```

## mainwindow.cpp | MainWindow::saveTransactionGroupAction_triggered | 原文件第1659-1670行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1659: void MainWindow::saveTransactionGroupAction_triggered(){
1660:     QString filename = QFileDialog::getSaveFileName(this,tr("保存偏差"),0,tr("INI文件(*.ini)\n所有文件(*.*)"));
1661:     if(!filename.length()) {
1662:         return;
1663:     }
1664: 
1665:     QSettings *configIni = new QSettings(filename, QSettings::IniFormat, 0);
1666:     configIni->setIniCodec("UTF-8");
1667: 
1668: 
1669: 
1670:     QString block = QString("group");
```

## mainwindow.cpp | MainWindow::saveTransactionGroupAction_triggered | 原文件第1671-1684行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1671:     QList<ActionGroup>::iterator iter;
1672:     int i = 0;
1673:     for(iter = actionGroupListMng.actionGroupList.begin();iter != actionGroupListMng.actionGroupList.end();iter ++){
1674:         QString key = QString(block).append("/G%1").arg(i); //
1675: 
1676:         configIni->setValue(key,(*iter).toDisString());
1677:         i ++;
1678:     }
1679: 
1680:     delete configIni;
1681: 
1682:     return ;
1683: }
1684: 
```

## mainwindow.cpp | MainWindow::saveTransactionGroupAction_triggered | 原文件第1685-1685行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1685: 
```

## mainwindow.cpp | MainWindow::addActionGroup_clicked | 原文件第1686-1693行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1686: void MainWindow::addActionGroup_clicked(){
1687:     ActionGroup newGroup;
1688:     newGroup.init();
1689: 
1690:     if(actionGroupListMng.actionGroupList.count() == 0) {
1691:         actionGroupListMng.currentSelected = 0;
1692:     } else {
1693:         newGroup = actionGroupListMng.actionGroupList.at(actionGroupListMng.currentSelected);
```

## mainwindow.cpp | MainWindow::addActionGroup_clicked | 原文件第1694-1703行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1694:         actionGroupListMng.currentSelected = actionGroupListMng.actionGroupList.count();
1695:     }
1696: 
1697:     newGroup.setIndex(actionGroupListMng.currentSelected);
1698:     actionGroupListMng.actionGroupList.push_back(newGroup);
1699: 
1700:     if(zxReleaseFlag) {
1701:         for(int i=0;i<MAX_STEER_NUM;i++) {
1702:             if(dis_arr[i]) {
1703:                 sc[i]->setPwm(1500);
```

## mainwindow.cpp | MainWindow::addActionGroup_clicked | 原文件第1704-1713行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1704:                 sc[i]->setTime(1000);
1705:             }
1706:         }
1707:     }
1708: 
1709: 
1710:     updateTableList();
1711:     updateWindowState();
1712: }
1713: 
```

## mainwindow.cpp | MainWindow::insertActionGroup_clicked | 原文件第1714-1722行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1714: void MainWindow::insertActionGroup_clicked(){
1715:     ActionGroup newGroup;
1716:     if(actionGroupListMng.actionGroupList.count() == 0){
1717:         addActionGroup_clicked();
1718:         return;
1719:     }
1720:     newGroup.init();
1721:     newGroup = actionGroupListMng.actionGroupList.at(actionGroupListMng.currentSelected);
1722:     actionGroupListMng.currentSelected++;
```

## mainwindow.cpp | MainWindow::insertActionGroup_clicked | 原文件第1723-1729行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1723:     //newGroup.setDisperse(radioButtonDisperse->isChecked());
1724:     actionGroupListMng.actionGroupList.insert(actionGroupListMng.currentSelected,newGroup);
1725:     newGroup.setIndex(actionGroupListMng.currentSelected);
1726:     //actionGroupListMng.currentSelected++;
1727:     updateTableList();
1728:     updateWindowState();
1729:     actionList->currentItem()->setBackgroundColor(QColor(255,0,0));
```

## mainwindow.cpp | MainWindow::insertActionGroup_clicked | 原文件第1730-1732行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1730:     actionList->currentItem()->setTextColor(Qt::white);
1731: }
1732: 
```

## mainwindow.cpp | MainWindow::delActionGroup_clicked | 原文件第1733-1740行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1733: void MainWindow::delActionGroup_clicked(){
1734:     if(actionGroupListMng.currentSelected == 0) {
1735:         QMessageBox::information(NULL, "提示", "此组无法删除！", QMessageBox::Ok);
1736:     } else {
1737:         actionGroupListMng.actionGroupList.removeAt(actionGroupListMng.currentSelected);
1738:         if(actionGroupListMng.currentSelected >= 0){
1739:             //actionGroupListMng.currentSelected -= 1;
1740:         }
```

## mainwindow.cpp | MainWindow::delActionGroup_clicked | 原文件第1741-1750行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1741:         if(actionGroupListMng.currentSelected==actionGroupListMng.actionGroupList.count()) {
1742:             actionGroupListMng.currentSelected -= 1;
1743:         }
1744: 
1745:         if(actionGroupListMng.currentSelected < 0 && actionGroupListMng.actionGroupList.count()){
1746:             actionGroupListMng.currentSelected = 0;
1747:         }
1748:         updateTableList();
1749:         updateWindowState();
1750:     }
```

## mainwindow.cpp | MainWindow::delActionGroup_clicked | 原文件第1751-1753行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1751: }
1752: 
1753: 
```

## mainwindow.cpp | MainWindow::steerCtl_clicked | 原文件第1754-1764行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1754: void MainWindow::steerCtl_clicked(FormSteerCtl *stc) {
1755:     QString toSendStr;
1756: 
1757:     qDebug() << "function:steerCtl_clicked";
1758: 
1759:     QString lstIdStr;
1760:     lstIdStr = lstIdStr.sprintf("%03d", djLstId[stc->getIndex()]);
1761: 
1762:     if(stc->getPbtnSendClickedState()) {
1763:         if(stc->getMenu() == MENU_PID) {
1764:             stc->setId(djLstId[stc->getIndex()]);
```

## mainwindow.cpp | MainWindow::steerCtl_clicked | 原文件第1765-1771行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1765:             toSendStr = "#"+ lstIdStr +"PRAD!";
1766:             toReadPwm = true;
1767:             toReadPwmIndex = stc->getIndex();
1768:         } else if(stc->getMenu() == MENU_PMOD) {
1769:             toSendStr = "#"+ lstIdStr +"PMOD" + QString::number(stc->getId()*2) + "!";
1770:         } else if(stc->getMenu() == MENU_PULK) {
1771:             toSendStr = "#"+ lstIdStr +"PULK!";
```

## mainwindow.cpp | MainWindow::steerCtl_clicked | 原文件第1772-1779行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1772:         } else if(stc->getMenu() == MENU_PCSD) {
1773:             toSendStr = "#"+ lstIdStr +"PCSD!";
1774:         } else if(stc->getMenu() == MENU_PCLE) {
1775:             toSendStr = "#"+ lstIdStr +"PCLE!";
1776:         } else if(stc->getMenu() == MENU_PVER) {
1777:             toSendStr = "#"+ lstIdStr +"PVER!";
1778:         } else if(stc->getMenu() == MENU_PAT) {
1779:             toSendStr = "#"+ lstIdStr +"PAT!";
```

## mainwindow.cpp | MainWindow::steerCtl_clicked | 原文件第1780-1793行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1780:         }
1781:         uart_send_str( toSendStr);
1782:         stc->setPbtnSendClickedState(false);
1783:     }
1784: 
1785:     QString clickTemp;
1786:     if(stc->pmin_click) {
1787:         stc->pmin_click = false;
1788:         clickTemp.sprintf("#%03dPSMI!", stc->getId());
1789:         uart_send_str(clickTemp);
1790:     }
1791: 
1792:     if(stc->pmax_click) {
1793:         stc->pmax_click = false;
```

## mainwindow.cpp | MainWindow::steerCtl_clicked | 原文件第1794-1801行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1794:         clickTemp.sprintf("#%03dPSMX!", stc->getId());
1795:         uart_send_str(clickTemp);
1796:     }
1797: 
1798: 
1799: }
1800: 
1801: 
```

## mainwindow.cpp | MainWindow::steerCtl_currentIndexChanged | 原文件第1802-1809行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1802: void MainWindow::steerCtl_currentIndexChanged(FormSteerCtl *stc) {
1803: 
1804:     qDebug() << "function:steerCtl_currentIndexChanged";
1805: 
1806:     if(stc->getMenu() != MENU_PID)return;
1807: //    QString toSendStr;
1808: //    toSendStr.sprintf("#%03dPID%03d!", djLstId[stc->getIndex()], stc->getId());
1809: //    if(djLstId[stc->getIndex()] != 255) uart_send_str( toSendStr);
```

## mainwindow.cpp | MainWindow::steerCtl_currentIndexChanged | 原文件第1810-1817行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1810: //    djLstId[stc->getIndex()] = stc->getId();
1811: 
1812:     ActionGroup newGroup;
1813:     for(int i=0;i<actionGroupListMng.actionGroupList.count();i++) {
1814:         newGroup = actionGroupListMng.actionGroupList.at(i);
1815:         newGroup.getItem(stc->getIndex())->setId(stc->getId());
1816: 
1817:         actionGroupListMng.actionGroupList.removeAt(i);
```

## mainwindow.cpp | MainWindow::steerCtl_currentIndexChanged | 原文件第1818-1824行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1818:         actionGroupListMng.actionGroupList.insert(i,newGroup);
1819:     }
1820: 
1821:     updateTableList();
1822:     updateWindowState();
1823: }
1824: 
```

## mainwindow.cpp | MainWindow::steerCtl_valueChanged | 原文件第1825-1835行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1825: void MainWindow::steerCtl_valueChanged(FormSteerCtl *stc){
1826:     if(list_click)return;
1827:     if(!data_send_flag)return;
1828: 
1829:     qDebug() << "MainWindow::steerCtl_valueChanged";
1830: 
1831:     if(stc->getMenu() != MENU_PID) {
1832:         int idTemp = djLstId[stc->getIndex()];
1833:         stc->signalLose = true;
1834:         stc->setMenu(MENU_PID);
1835:         stc->setCmbMenuIndex(MENU_PID);
```

## mainwindow.cpp | MainWindow::steerCtl_valueChanged | 原文件第1836-1847行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1836:         stc->setId(idTemp);
1837:         stc->createCmbDjIdIndexPid(idTemp);
1838:         stc->signalLose = false;
1839:         djLstId[stc->getIndex()] = idTemp;
1840:     }
1841: 
1842:     int curId = stc->getId();
1843:     int curTime = stc->getTime();
1844:     int curPwm = stc->getPwm();
1845:     int curBias = stc->getBias();
1846:     int curIndex = stc->getIndex();
1847:     bool changed = true;
```

## mainwindow.cpp | MainWindow::steerCtl_valueChanged | 原文件第1848-1860行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1848:     dj_bias[curIndex] = curBias;
1849: 
1850:     if(list_click) {
1851:         list_click = false;
1852:         qDebug() << "list_click return";
1853:         return;
1854:     }
1855: 
1856:     ActionGroupItem item(curIndex, curId, curPwm, curTime, curBias, changed);
1857:     QString temp_str = "";
1858:     //pwm 发送
1859:     if(stc->pwm_changed || stc->bias_changed) {
1860:         updateWindowItem(curIndex);
```

## mainwindow.cpp | MainWindow::steerCtl_valueChanged | 原文件第1861-1875行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1861:         updateTableList();
1862:         updateWindowState();
1863: 
1864:         temp_str = item.toBiasString(curBias);
1865:         uart_send_str(temp_str);
1866:     }
1867: 
1868:     //time 更新
1869:     if(stc->time_changed) {
1870:         data_send_flag = false;
1871:         updateWindowItem(curIndex);
1872:         updateTableList();
1873:         updateWindowState();
1874:         data_send_flag = true;
1875:     }
```

## mainwindow.cpp | MainWindow::steerCtl_valueChanged | 原文件第1876-1890行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1876: 
1877:     QString addChangeStyle = "selection-background-color: rgb(253, 62, 62);";
1878:     if(stc->bias_changed) {
1879:         stc->setBiasStyle(addChangeStyle);
1880:     }
1881: 
1882:     if(stc->pwm_changed) {
1883:         stc->setPwmStyle(addChangeStyle);
1884:     }
1885: 
1886:     if(stc->time_changed) {
1887:         stc->setTimeStyle(addChangeStyle);
1888:     }
1889: 
1890:     stc->pwm_changed = false;
```

## mainwindow.cpp | MainWindow::steerCtl_valueChanged | 原文件第1891-1894行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1891:     stc->time_changed = false;
1892:     stc->bias_changed = false;
1893: }
1894: 
```

## mainwindow.cpp | MainWindow::autoScroll | 原文件第1895-1900行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1895: void MainWindow::autoScroll() {
1896:     QTextCursor cursor =  dataRecvEdit->textCursor();
1897:     cursor.movePosition(QTextCursor::End);
1898:     dataRecvEdit->setTextCursor(cursor);
1899: }
1900: 
```

## mainwindow.cpp | MainWindow::pbtnConnectUpdate | 原文件第1901-1910行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1901: void MainWindow::pbtnConnectUpdate(){
1902:     if((!threadA->comOpened())){
1903:         pbtnConnect->setStyleSheet(pushButtonStyle1_1);
1904:         serialOpened = false;
1905:         pbtnConnect->setText("设备未连接");
1906:         labSerialLed->setStyleSheet("image: url(:/images/light_off.png);");
1907:         comOpened = false;
1908: 
1909:     } else {
1910:         pbtnConnect->setStyleSheet(pushButtonStyle1_3);
```

## mainwindow.cpp | MainWindow::pbtnConnectUpdate | 原文件第1911-1917行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1911:         serialOpened = true;
1912:         comOpened = true;
1913:         pbtnConnect->setText("设备已连接");
1914:         labSerialLed->setStyleSheet("image: url(:/images/light_on.png);");
1915:     }
1916: }
1917: 
```

## mainwindow.cpp | MainWindow::pbtnConnect_clicked | 原文件第1918-1926行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1918: void MainWindow::pbtnConnect_clicked(){
1919:     qDebug() << "pushButtonConnect_clicked";
1920: 
1921:     if(!serialOpened) {
1922:         threadA->start();
1923:         threadA->setPortnum(cbSerialCom->currentText());
1924:         threadA->setPortrate(cbBaudRate->currentText());
1925:         threadA->startCom();
1926:         //QTimer::singleShot(100, Qt::PreciseTimer,this,SLOT(pbtnConnectUpdate()));
```

## mainwindow.cpp | MainWindow::pbtnConnect_clicked | 原文件第1927-1935行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1927:         qDebug() << "opening....";
1928:         pbtnConnect->setText("正在打开...");
1929:         //cbSerialCom->setEnabled(false);
1930:         //cbBaudRate->setEnabled(false);
1931:     } else {
1932:         threadA->stopCom();
1933:         //QTimer::singleShot(100, Qt::PreciseTimer,this,SLOT(pbtnConnectUpdate()));
1934:         qDebug() << "closing....";
1935:         pbtnConnect->setText("正在关闭...");
```

## mainwindow.cpp | MainWindow::pbtnConnect_clicked | 原文件第1936-1940行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1936:         //cbSerialCom->setEnabled(true);
1937:         //cbBaudRate->setEnabled(true);
1938:     }
1939: }
1940: 
```

## mainwindow.cpp | MainWindow::pushButtonClearDataOut_clicked | 原文件第1941-1945行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1941: void MainWindow::pushButtonClearDataOut_clicked(){
1942:     dataRecvEdit->clear();
1943: }
1944: 
1945: //串口控制
```

## mainwindow.cpp | MainWindow::handleSerialRxData | 原文件第1946-1955行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1946: void MainWindow::handleSerialRxData(){
1947: 
1948:     QString str_get ;
1949:     str_get = uart_get_str();
1950:     qDebug() << "Get " << str_get;
1951:     uart_get_show(str_get);
1952:     parse_rx_data(str_get);
1953: 
1954: }
1955: 
```

## mainwindow.cpp | MainWindow::parse_rx_data | 原文件第1956-1963行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1956: void MainWindow::parse_rx_data(QString str_get) {
1957:     static bool fontFlag = false;
1958: //    //总线读取角度
1959: //    if(toReadPwm) {
1960: //        toReadPwm = false;
1961: //        QString id_str = str_get.split("#").last().split("P").first();
1962: //        QString pwm_str = str_get.split("P").last().split("!").first();
1963: //        //dataSendEdit->setText(index_str + "+" + pwm_str);
```

## mainwindow.cpp | MainWindow::parse_rx_data | 原文件第1964-1969行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1964: //        qDebug() << id_str + "+" + pwm_str;
1965: //        comOpened = false;
1966: //        if(id_str.length() == 3 && pwm_str.length()==4 && id_str.toInt() >= 0 && id_str.toInt() <= 254 && pwm_str.toInt()>=500 && pwm_str.toInt()<=2500) {
1967: //            for(int i=0;i<MAX_STEER_NUM;i++) {
1968: //                if(sc[i]->getId() == id_str.toInt()) {
1969: //                    //adc_arr[i] = true;
```

## mainwindow.cpp | MainWindow::parse_rx_data | 原文件第1970-1982行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1970: //                    sc[i]->setPwm(pwm_str.toInt());
1971: //                    qDebug() << "ID:" + id_str << endl;
1972: //                    break;
1973: //                }
1974: //            }
1975: //        }
1976: //        comOpened = true;
1977: //    }
1978: 
1979: //    if(zxWRead) {
1980: //        zxWRead = false;
1981: //        zxPbtnGetData->setText(str_get);
1982: //        if(fontFlag) {
```

## mainwindow.cpp | MainWindow::parse_rx_data | 原文件第1983-1989行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1983: //            zxPbtnGetData->setStyleSheet("background-color: rgb(255, 255, 255);border-radius:1px;");
1984: //        } else {
1985: //            zxPbtnGetData->setStyleSheet("background-color: rgb(0, 240, 214);border-radius:1px;");
1986: //        }
1987: //        fontFlag = !fontFlag;
1988: 
1989: //        QString id_str = str_get.split("#").last().split("P").first();
```

## mainwindow.cpp | MainWindow::parse_rx_data | 原文件第1990-1994行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1990: //        QString pwm_str = str_get.split("P").last().split("!").first();
1991: //        //dataSendEdit->setText(index_str + "+" + pwm_str);
1992: //        qDebug() << id_str + "+" + pwm_str;
1993: //        comOpened = false;
1994: //        if(id_str.length() == 3 && pwm_str.length()==4 && id_str.toInt() >= 0 && id_str.toInt() <= 254 && pwm_str.toInt()>=500 && pwm_str.toInt()<=2500) {
```

## mainwindow.cpp | MainWindow::parse_rx_data | 原文件第1995-2008行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
1995: //            zxSldPos->setValue(pwm_str.toInt());
1996: //        } else if(str_get.contains("PV")) {
1997: //            zxLableVersion->setText(pwm_str);
1998: //        }
1999: //        comOpened = true;
2000: 
2001: //    }
2002: 
2003:     //应答下载
2004:     QString cmd, tempDjStr;
2005:     ActionGroup groupTemp;
2006: 
2007:     //下载处理
2008:     if(saveActionsFlag && (str_get.contains("A"))) {
```

## mainwindow.cpp | MainWindow::parse_rx_data | 原文件第2009-2013行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2009:         //ackDownTime = QDateTime::currentMSecsSinceEpoch();
2010:         qDebug() << "startDloadAction ok! time:" + QString::number(ackDownTime);
2011:         if(startDloadAction < actionGroupListMng.actionGroupList.count()) {
2012:             groupTemp = actionGroupListMng.actionGroupList.at(startDloadAction);
2013:             cmd = cmd.sprintf("<G%04d",startDloadAction);
```

## mainwindow.cpp | MainWindow::parse_rx_data | 原文件第2014-2024行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2014:             for(int i=0;i<MAX_STEER_NUM; i++) {
2015:                 if(dis_arr[i]) {
2016:                     tempDjStr = groupTemp.getItem(i)->toBiasString(dj_bias[i]);
2017:                     cmd = cmd+ tempDjStr;
2018:                 }
2019: 
2020:             }
2021:             cmd = cmd+ "B000!>";
2022:             uart_send_str(cmd);
2023: 
2024:             actionList->setCurrentRow(startDloadAction);
```

## mainwindow.cpp | MainWindow::parse_rx_data | 原文件第2025-2031行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2025:             if(last_select < actionGroupListMng.actionGroupList.count()) {
2026:                 actionList->item(last_select)->setBackgroundColor(Qt::white);
2027:                 actionList->item(last_select)->setTextColor(Qt::black);
2028:             }
2029:             actionList->currentItem()->setBackgroundColor(QColor(46,190,251));
2030:             actionList->currentItem()->setTextColor(Qt::white);
2031: 
```

## mainwindow.cpp | MainWindow::parse_rx_data | 原文件第2032-2038行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2032:             last_select = startDloadAction;
2033:             actionGroupListMng.currentSelected = last_select;
2034: 
2035:             uart_get_show(tr("正在下载第%1个动作").arg(startDloadAction));
2036:             startDloadAction ++;
2037:         } else {
2038:             startDloadAction = actionGroupListMng.currentSelected;
```

## mainwindow.cpp | MainWindow::parse_rx_data | 原文件第2039-2047行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2039:             uart_get_show(tr("共保存%1个动作").arg(actionGroupListMng.actionGroupList.count()-startDloadActionBak));
2040:             pbtnActionSave->setText("下载动作组");
2041:             saveActionsFlag = false;
2042:             actionTimer->start(1);
2043:         }
2044:         qDebug() << "startDloadAction ok! end!!!";
2045:     }
2046: 
2047:     //脱机执行返回 @DoGroup 2 OK!
```

## mainwindow.cpp | MainWindow::parse_rx_data | 原文件第2048-2055行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2048:     if(doGroupActionsOffline && str_get.contains("DoGroup")) {
2049:         int indexEnd = str_get.indexOf("OK");
2050:         QString tmpStr11 = str_get.left(indexEnd-1);
2051:         int indexStart = tmpStr11.indexOf("DoGroup");
2052: 
2053:         int groupIndex = tmpStr11.right(indexStart).toInt();
2054: 
2055:         if(groupIndex < actionGroupListMng.actionGroupList.count()) {
```

## mainwindow.cpp | MainWindow::parse_rx_data | 原文件第2056-2061行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2056:             actionList->setCurrentRow(groupIndex);
2057:             if(last_select < actionGroupListMng.actionGroupList.count()) {
2058:                 actionList->item(last_select)->setBackgroundColor(Qt::white);
2059:                 actionList->item(last_select)->setTextColor(Qt::black);
2060:             }
2061:             actionList->currentItem()->setBackgroundColor(QColor(46,190,251));
```

## mainwindow.cpp | MainWindow::parse_rx_data | 原文件第2062-2072行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2062:             actionList->currentItem()->setTextColor(Qt::white);
2063: 
2064:             last_select = groupIndex;
2065:             actionGroupListMng.currentSelected = last_select;
2066:         }
2067: 
2068:         //qDebug() << "number:" + QString::number(groupIndex);
2069:     }
2070: 
2071:     //脱机执行完毕 @GroupDone!
2072:     if(doGroupActionsOffline && str_get.contains("GroupDone")) {
```

## mainwindow.cpp | MainWindow::parse_rx_data | 原文件第2073-2079行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2073:         doGroupActionsOffline = false;
2074:         pbtnDoActionOffline->setStyleSheet(pbtnStyle_normal);
2075:     }
2076: }
2077: 
2078: 
2079: 
```

## mainwindow.cpp | MainWindow::handlerSerialTimeout | 原文件第2080-2087行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2080: void MainWindow::handlerSerialTimeout(QString msg){
2081:     uart_get_show(msg);
2082: }
2083: 
2084: //void MainWindow::handlerSerialError(QString error){
2085: //    uart_get_show(error);
2086: //}
2087: 
```

## mainwindow.cpp | MainWindow::hanlderSerialError | 原文件第2088-2098行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2088: void MainWindow::hanlderSerialError(QString msg){
2089:     if(msg.toInt() == QSerialPort::PermissionError){
2090:         threadA->stopCom();
2091:         QMessageBox::critical(this,tr("错误"),
2092:                               tr("串口打开失败，串口被占用"),
2093:                               QMessageBox::Ok);
2094:     }
2095: 
2096: }
2097: 
2098: 
```

## mainwindow.cpp | MainWindow::pbtnActionSave_clicked | 原文件第2099-2111行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2099: void MainWindow::pbtnActionSave_clicked(){
2100:    //int i=0;
2101:    if(serialNotOpen() ){
2102:        qDebug() << "Please Open Serial!";
2103:        return;
2104:    }
2105: 
2106: 
2107:    if(!saveActionsFlag){
2108:        pbtnActionSave->setText("停止下载");
2109:        startDloadAction = actionGroupListMng.currentSelected;
2110:        startDloadActionBak = startDloadAction;
2111:        saveActionsFlag = true;
```

## mainwindow.cpp | MainWindow::pbtnActionSave_clicked | 原文件第2112-2124行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2112:        if(radioButtonAckDone->isChecked()) {
2113:          actionTimer->stop();
2114:          uart_send_str( "$GETA!");
2115:        } else {
2116:          actionTimer->start(1);
2117:        }
2118:    } else {
2119:        pbtnActionSave->setText("下载动作组");
2120:        saveActionsFlag = false;
2121:    }
2122: 
2123: }
2124: 
```

## mainwindow.cpp | MainWindow::pbtnDRS_clicked | 原文件第2125-2129行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2125: void MainWindow::pbtnDRS_clicked(){
2126:     uart_send_str("$DRS!");
2127: }
2128: 
2129: 
```

## mainwindow.cpp | MainWindow::pbtnDEA_clicked | 原文件第2130-2133行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2130: void MainWindow::pbtnDEA_clicked(){
2131:     uart_send_str("$DEA!");
2132: }
2133: 
```

## mainwindow.cpp | MainWindow::pushButtonReadSlaveActionGroups_clicked | 原文件第2134-2137行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2134: void MainWindow::pushButtonReadSlaveActionGroups_clicked(){
2135:     uart_send_str("$DEA!");
2136: }
2137: 
```

## mainwindow.cpp | MainWindow::pbtnCGP_clicked | 原文件第2138-2147行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2138: void MainWindow::pbtnCGP_clicked(){
2139:     QString cmd = "$CGP:"
2140:             + QString::number(spinBoxStartGroup->value())
2141:             + "-"
2142:             + QString::number(spinBoxEndGroup->value())
2143:             //+ QString::number(actionGroupListMng.actionGroupList.count()-1)
2144:             + "!";
2145:     uart_send_str(cmd);
2146: }
2147: 
```

## mainwindow.cpp | MainWindow::pbtnDEG_clicked | 原文件第2148-2157行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2148: void MainWindow::pbtnDEG_clicked(){
2149:     QString cmd = "$DEG:"
2150:             + QString::number(spinBoxStartGroup->value())
2151:             + "-"
2152:             + QString::number(spinBoxEndGroup->value())
2153:             //+ QString::number(actionGroupListMng.actionGroupList.count()-1)
2154:             + "!";
2155:     uart_send_str(cmd);
2156: }
2157: 
```

## mainwindow.cpp | MainWindow::pbtnOpenFile_clicked | 原文件第2158-2167行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2158: void MainWindow::pbtnOpenFile_clicked(){
2159: 
2160: 
2161:     updateFileName=QFileDialog::getOpenFileName(this,
2162:                                           tr("Open files"),
2163:                                           "",
2164:                                           "Binary Files (*.bin);;All Files (*.*)");
2165:     if(updateFileName.isNull()){
2166:         return;
2167:     }
```

## mainwindow.cpp | MainWindow::pbtnOpenFile_clicked | 原文件第2168-2174行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2168:     //pbtnOpenFile->setText(updateFileName.section('/', -1));
2169: 
2170:     //ui->firmwareFileLineEdit->setText(fileName);
2171:     //sendToLogDisplay(QStringLiteral("选择文件：")+fileName);
2172: }
2173: 
2174: 
```

## mainwindow.cpp | MainWindow::actionList_activated | 原文件第2175-2186行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2175: void MainWindow::actionList_activated(QModelIndex index){
2176:     if(actionList_double_clicked) {
2177:         actionList_double_clicked = false;
2178:         return;
2179:     }
2180:     qDebug() << "function start:actionList_doubleClick";
2181:     list_click = true;
2182:     actionList_double_clicked = true;
2183: 
2184:     QString tempDjStr;
2185:     QString cmd = "";
2186: 
```

## mainwindow.cpp | MainWindow::actionList_activated | 原文件第2187-2192行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2187:     cmd = cmd.sprintf("{G%04d",index.row());
2188:     for(int i=0;i<MAX_STEER_NUM; i++) {
2189:         if(dis_arr[i]) {
2190:             //tempDjStr.sprintf("#%03dP%04dT%04d!", sc[i]->getId(), sc[i]->getPwm(), sc[i]->getTime());
2191:             tempDjStr.sprintf("#%03dP%04dT%04d!", sc[i]->getId(), sc[i]->getPwm() + sc[i]->getBias(), sc[i]->getTime());
2192:             if(index.row() == 0) {
```

## mainwindow.cpp | MainWindow::actionList_activated | 原文件第2193-2204行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2193:                 sc[i]->setBiasEnable(true);
2194:                 sc[i]->setPwm(1500);
2195:                 //tempDjStr.sprintf("#%03dP%04dT%04d!", sc[i]->getId(), sc[i]->getPwm() + sc[i]->getBias(), sc[i]->getTime());
2196:             }
2197:             cmd = cmd+ tempDjStr;
2198:         }
2199: 
2200:     }
2201:     cmd = cmd+ "}";
2202:     uart_send_str(cmd);
2203: 
2204:     list_click = false;
```

## mainwindow.cpp | MainWindow::actionList_activated | 原文件第2205-2208行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2205:     qDebug() << "function end:actionList_doubleClick";
2206:     qDebug() << "function end:actionList_activated";
2207: }
2208: 
```

## mainwindow.cpp | MainWindow::clearBias_clicked | 原文件第2209-2218行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2209: void MainWindow::clearBias_clicked() {
2210:     QMessageBox::StandardButton rb = QMessageBox::question(NULL, "清除偏差", "你确定要清除偏差吗？", QMessageBox::Yes | QMessageBox::No, QMessageBox::Yes);
2211:     if(rb == QMessageBox::Yes) {
2212:         uart_send_str("#255PDEB!");
2213:     }
2214: 
2215: }
2216: 
2217: 
2218: 
```

## mainwindow.cpp | MainWindow::clearActionGroup_clicked | 原文件第2219-2223行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2219: void MainWindow::clearActionGroup_clicked(){
2220:     QMessageBox::StandardButton rb = QMessageBox::question(NULL, "清除列表", "你确定要清除列表吗？", QMessageBox::Yes | QMessageBox::No, QMessageBox::Yes);
2221:     if(rb == QMessageBox::Yes) {
2222:         ActionGroup newGroup = actionGroupListMng.actionGroupList.at(0);
2223:         actionGroupListMng.actionGroupList.clear();
```

## mainwindow.cpp | MainWindow::clearActionGroup_clicked | 原文件第2224-2231行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2224:         actionGroupListMng.actionGroupList.push_back(newGroup);
2225:         actionGroupListMng.currentSelected = 0;
2226:         updateTableList();
2227:         updateWindowState();
2228:     }
2229: }
2230: 
2231: 
```

## mainwindow.cpp | MainWindow::actionList_rowChanged | 原文件第2232-2241行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2232: void MainWindow::actionList_rowChanged(int row){
2233:     (void)row;
2234: /*    if(serialNotOpen()){
2235:         return ;
2236:     }
2237:     actionGroupListMng.currentSelected = row;
2238:     ActionGroup group = actionGroupListMng.actionGroupList.at(actionGroupListMng.currentSelected);
2239: 
2240:     for(int i = 0;i < MAX_STEER_NUM;i++){
2241:         ActionGroupItem *item = group.getItem(i);
```

## mainwindow.cpp | MainWindow::actionList_rowChanged | 原文件第2242-2255行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2242:         sc[i]->setEnabled(item->Enable());
2243:         sc[i]->setTime(item->Time());
2244:         sc[i]->setPwm(item->Pwm());
2245:     }
2246: 
2247:     dataSendEdit->setText(group.toString());
2248:     uart_send_str(5,group.toString());
2249:     //发送动作组
2250:     updateWindowState();*/
2251: }
2252: 
2253: 
2254: //void MainWindow::comboBoxSteerNumber_indexChanged(int index){
2255: //    if(justComboBoxSteerNumber){
```

## mainwindow.cpp | MainWindow::actionList_rowChanged | 原文件第2256-2269行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2256: //        justComboBoxSteerNumber = false;
2257: //        return;
2258: //    }
2259: //    drawdj_pannel(index);
2260: //    for(int i=0;i<index; i++) {
2261: //        dis_arr[i] = true;
2262: //        add_steer_enable(i, true);
2263: //    }
2264: //    for(int i=index; i<MAX_STEER_NUM;i++) {
2265: //        dis_arr[i] = false;
2266: //        add_steer_enable(i, false);
2267: //    }
2268: //}
2269: 
```

## mainwindow.cpp | MainWindow::actionList_rowChanged | 原文件第2270-2284行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2270: //void MainWindow::drawdj_pannel(int steerNum){
2271: //    int id = 0;
2272: //    while(id < steerNum){
2273: //        sc[id]->setVisible(true);
2274: //        add_steer_enable(id, true);
2275: //        id ++;
2276: //    }
2277: 
2278: //    while(id < MAX_STEER_NUM){
2279: //        sc[id]->setVisible(false);
2280: //        add_steer_enable(id, false);
2281: //        id ++;
2282: //    }
2283: //    update();
2284: //}
```

## mainwindow.cpp | MainWindow::actionList_rowChanged | 原文件第2285-2286行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2285: 
2286: 
```

## mainwindow.cpp | MainWindow::spinBoxTimeControl_valueChanged | 原文件第2287-2297行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2287: void MainWindow::spinBoxTimeControl_valueChanged(int val){
2288:     data_send_flag = false;
2289:     for(int i = 0;i < MAX_STEER_NUM;i ++){
2290:         sc[i]->setTime(val);
2291:         updateWindowItem(i);
2292:     }
2293:     updateTableList();
2294:     updateWindowState();
2295:     data_send_flag = true;
2296: }
2297: 
```

## mainwindow.cpp | MainWindow::spinBoxPwmControl_valueChanged | 原文件第2298-2303行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2298: void MainWindow::spinBoxPwmControl_valueChanged(int val){
2299:     for(int i = 0;i < MAX_STEER_NUM;i ++){
2300:         sc[i]->setPwm(val);
2301:     }
2302: }
2303: 
```

## mainwindow.cpp | MainWindow::spinBoxBiasControl_valueChanged | 原文件第2304-2310行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2304: void MainWindow::spinBoxBiasControl_valueChanged(int val){
2305:     for(int i = 0;i < MAX_STEER_NUM;i ++){
2306:         sc[i]->setBias(val);
2307:     }
2308: }
2309: 
2310: 
```

## mainwindow.cpp | MainWindow::manDoc_triggered | 原文件第2311-2320行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2311: void MainWindow::manDoc_triggered(){
2312: 
2313: //    QString fileName = "updateFile.txt";
2314: //    QFile updateFile(fileName);
2315: //    if(!updateFile.open(QIODevice::ReadOnly | QIODevice::Text)) {
2316: //        qDebug() << "open file fail!";
2317: //        return;
2318: //    }
2319: //    QTextStream fileContent(&updateFile);
2320: //    while(!fileContent.atEnd()) {
```

## mainwindow.cpp | MainWindow::manDoc_triggered | 原文件第2321-2333行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2321: //        QString line = fileContent.readLine();
2322: //        dataRecvEdit->append(line);
2323: //    }
2324: //    qDebug() << "come manDoc_triggered";
2325: 
2326: //    QMessageBox::information(this, tr("更新信息"), QFileInfo(updateFile));
2327: 
2328:     QString helpfile = "help.pdf";
2329:     QDesktopServices::openUrl(QUrl::fromLocalFile(QFileInfo(helpfile).absoluteFilePath()));
2330: 
2331: }
2332: 
2333: 
```

## mainwindow.cpp | MainWindow::pushButtonAddMusic_clicked | 原文件第2334-2341行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2334: void MainWindow::pushButtonAddMusic_clicked(){
2335:     QString filename  = QFileDialog::getOpenFileName(this, tr("打开文件"), 0, tr("mp3文件(*.mp3)\n所有文件(*.*)"));  //添加更多的文件类型
2336:     if(!filename.length()){
2337:         return ;
2338:     } else {
2339:         pushButtonAddMusic->setText(filename.split('/').last().left(5));
2340:         playList->clear();
2341:         playList->addMedia(QUrl::fromLocalFile(filename));
```

## mainwindow.cpp | MainWindow::pushButtonAddMusic_clicked | 原文件第2342-2345行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2342:         //qDebug() << filename;
2343:     }
2344: }
2345: 
```

## mainwindow.cpp | MainWindow::pbtnDoActionByPlayMusic_clicked | 原文件第2346-2359行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2346: void MainWindow::pbtnDoActionByPlayMusic_clicked(){
2347:     static bool flag = false;
2348:     //提示添加音乐
2349:     if(playList->isEmpty()) {
2350:         QMessageBox::warning(this,tr("提示"),tr("请先添加音乐"));
2351:         return;
2352:     }
2353: 
2354:     //串口没打开
2355:     if(serialNotOpen()){
2356:         return ;
2357:     }
2358: 
2359:     startActionIndex = spinBoxStartGroup->value();
```

## mainwindow.cpp | MainWindow::pbtnDoActionByPlayMusic_clicked | 原文件第2360-2372行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2360:     endActionIndex = spinBoxEndGroup->value();
2361:     timesToDo = spinBoxDoTimes->value();
2362: 
2363:     if(timesToDo == 0) {
2364:         doForever = true;
2365:     } else {
2366:         doForever = false;
2367:     }
2368: 
2369:     if(startActionIndex == 0 && endActionIndex == 0){
2370:         endActionIndex = actionGroupListMng.actionGroupList.count()-1;
2371:     }
2372: 
```

## mainwindow.cpp | MainWindow::pbtnDoActionByPlayMusic_clicked | 原文件第2373-2382行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2373:     if(startActionIndex > endActionIndex){
2374:         int tmp = startActionIndex;
2375:         startActionIndex =  endActionIndex;
2376:         endActionIndex = tmp;
2377:     }
2378: 
2379:     if(startActionIndex >= actionGroupListMng.actionGroupList.count() ){
2380:         startActionIndex = actionGroupListMng.actionGroupList.count()-1;
2381:     }
2382: 
```

## mainwindow.cpp | MainWindow::pbtnDoActionByPlayMusic_clicked | 原文件第2383-2392行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2383:     if(endActionIndex >= actionGroupListMng.actionGroupList.count()){
2384:         endActionIndex = actionGroupListMng.actionGroupList.count()-1;
2385:     }
2386: 
2387:     startActionIndexBak = startActionIndex;
2388:     endActionIndexBak = endActionIndex;
2389: 
2390:     if(radioButtonOnline->isChecked()) {
2391: 
2392:         if(actionGroupListMng.actionGroupList.count() == 0){
```

## mainwindow.cpp | MainWindow::pbtnDoActionByPlayMusic_clicked | 原文件第2393-2404行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2393:              QMessageBox::warning(this,tr("提示"),tr("请添加动作组"));
2394:              return;
2395:         }
2396: 
2397:         if(!flag){
2398:             //doGroupActions = !flag;
2399:             pbtnDoActionByPlayMusic->setText("停止执行");
2400:             player->play();
2401:             actionDisTimer->start(1000);
2402:             musicTimeCount = 0;
2403:             actionTimer->start(1);
2404:         } else {
```

## mainwindow.cpp | MainWindow::pbtnDoActionByPlayMusic_clicked | 原文件第2405-2417行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2405:             //doGroupActions = !flag;
2406:             pbtnDoActionByPlayMusic->setText("音乐同步执行");
2407:             uart_send_str("$DST!");//停止按钮
2408:             player->stop();
2409:             actionDisTimer->stop();
2410: 
2411:         }
2412: 
2413:     } else {
2414:         if(!flag){
2415:             QString cmd;
2416:             //doGroupActions = !flag;
2417:             pbtnDoActionByPlayMusic->setText("停止执行");
```

## mainwindow.cpp | MainWindow::pbtnDoActionByPlayMusic_clicked | 原文件第2418-2425行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2418:             cmd = "$DGT:" + QString::number(spinBoxStartGroup->value()) + "-"
2419:                       + QString::number(spinBoxEndGroup->value()) + ","
2420:                       + QString::number(spinBoxDoTimes->value()) + "!";
2421:             uart_send_str(cmd);
2422:             player->play();
2423:             actionDisTimer->start(1000);
2424:             musicTimeCount = 0;
2425:         } else {
```

## mainwindow.cpp | MainWindow::pbtnDoActionByPlayMusic_clicked | 原文件第2426-2436行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2426:             //doGroupActions = !flag;
2427:             pbtnDoActionByPlayMusic->setText("音乐同步执行");
2428:             player->stop();
2429:             uart_send_str("$DST!");//停止按钮
2430:             actionDisTimer->stop();
2431:         }
2432:     }
2433: 
2434:     flag = !flag;
2435: }
2436: 
```

## mainwindow.cpp | MainWindow::title_lock_click | 原文件第2437-2449行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2437: void MainWindow::title_lock_click() {
2438:     //qDebug() << "come title_lock_click";
2439:     for(int i=0;i<MAX_STEER_NUM; i++) {
2440:         if(title_lock->isChecked()) {
2441:             sc[i]->setTitleEnable(false);
2442:             title_lock->setText("标题已锁定");
2443:         } else {
2444:             sc[i]->setTitleEnable(true);
2445:             title_lock->setText("标题未锁定");
2446:         }
2447:     }
2448: }
2449: 
```

## mainwindow.cpp | MainWindow::title_lock_click | 原文件第2450-2451行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2450: 
2451: 
```

## mainwindow.cpp | MainWindow::listToCmd_clicked | 原文件第2452-2458行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2452: void MainWindow::listToCmd_clicked() {
2453: 
2454: //qDebug() << "come listToCmd_clicked";
2455: //    if(actionGroupListMng.actionGroupList.at(actionGroupListMng.currentSelected).isGroup()) {
2456: //        actionGroupListMng.actionGroupList.at(actionGroupListMng.currentSelected).setIsGroup(false);
2457: //    } else {
2458: //        actionGroupListMng.actionGroupList.at(actionGroupListMng.currentSelected).setIsGroup(true);
```

## mainwindow.cpp | MainWindow::listToCmd_clicked | 原文件第2459-2466行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2459: //    }
2460: 
2461:     //ActionGroup *tempActionGroup = &(actionGroupListMng.actionGroupList.at(actionGroupListMng.currentSelected));
2462:     ActionGroup tempGroup = actionGroupListMng.actionGroupList.at(actionGroupListMng.currentSelected);
2463:     if(tempGroup.isGroup()) {
2464:         tempGroup.setIsGroup(false);
2465:         listToCmd->setText("转换为动作");
2466:         listToCmd->setStyleSheet(pbtnStyle_xxxxx);
```

## mainwindow.cpp | MainWindow::listToCmd_clicked | 原文件第2467-2476行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2467:     }
2468:     else {
2469:         tempGroup.setIsGroup(true);
2470:         listToCmd->setText("转换为命令");
2471:         listToCmd->setStyleSheet(pbtnStyle_normal);
2472:     }
2473:     tempGroup.setCmdStr("$!");
2474:     actionGroupListMng.actionGroupList.removeAt(actionGroupListMng.currentSelected);
2475:     actionGroupListMng.actionGroupList.insert(actionGroupListMng.currentSelected,tempGroup);
2476:     updateTableList();
```

## mainwindow.cpp | MainWindow::listToCmd_clicked | 原文件第2477-2493行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2477: 
2478:     return;
2479: }
2480: 
2481: 
2482: //void MainWindow::pbtnBiasSave_clicked() {
2483: //    if(!pwmBiasDownload) {
2484: //        pwmBiasDownload = true;
2485: //        pbtnBiasSave->setText("停止下载");
2486: //    } else {
2487: //        pwmBiasDownload = false;
2488: //        pbtnBiasSave->setText("偏差下载");
2489: //    }
2490: //    return;
2491: //}
2492: 
2493: 
```

## mainwindow.cpp | MainWindow::ptbDnTimeBias_clicked | 原文件第2494-2505行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2494: void MainWindow::ptbDnTimeBias_clicked() {
2495:     if(!timeBiasDownload) {
2496:         timeBiasDownload = true;
2497:         ptbDnTimeBias->setText("停止下载");
2498:     } else {
2499:         timeBiasDownload = false;
2500:         ptbDnTimeBias->setText("时差下载");
2501:     }
2502:     return;
2503: }
2504: 
2505: //串口接收数据
```

## mainwindow.cpp | MainWindow::uart_get_str | 原文件第2506-2518行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2506: QString MainWindow::uart_get_str(void) {
2507:     char *buf;
2508:     QString seria_str;
2509:     if(threadA->requestData.size()>0) {
2510:         seria_str.clear();
2511:         buf=threadA->requestData.data();
2512:         seria_str = QString(QLatin1String(buf));
2513:         threadA->requestData.clear();
2514:         return seria_str;
2515:     }
2516:     return NULL;
2517: }
2518: 
```

## mainwindow.cpp | MainWindow::uart_get_show | 原文件第2519-2522行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2519: void MainWindow::uart_get_show(QString str) {
2520:     dataRecvEdit->append(str);
2521: }
2522: 
```

## mainwindow.cpp | MainWindow::uart_send_show | 原文件第2523-2526行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2523: void MainWindow::uart_send_show(QString str) {
2524:     dataSendEdit->setText(str);
2525: }
2526: 
```

## mainwindow.cpp | MainWindow::chkBoxDj_click | 原文件第2527-2539行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2527: void MainWindow::chkBoxDj_click() {
2528:     //qDebug() << "come chkBoxDj_click";
2529:     chkBoxDjFlag = false;
2530: 
2531:     for(int i=0;i<MAX_STEER_NUM;i++) {
2532:         if(dis_arr[i] != chkBoxDj[i]->isChecked()) {
2533:             dis_arr[i] = chkBoxDj[i]->isChecked();
2534:             sc[i]->setSeed(dis_arr[i]);
2535:         }
2536:     }
2537:     updateTableList();
2538:     dj_pannel_clicked(NULL);
2539: }
```

## mainwindow.cpp | MainWindow::chkBoxDj_click | 原文件第2540-2540行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2540: 
```

## mainwindow.cpp | MainWindow::chkBoxDjAll_click | 原文件第2541-2550行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2541: void MainWindow::chkBoxDjAll_click() {
2542:     chkBoxDjFlag = false;
2543:     for(int i=0;i<MAX_STEER_NUM;i++) {
2544:         dis_arr[i] = chkBoxDjAll->isChecked();
2545:         chkBoxDj[i]->setChecked(dis_arr[i]);
2546:         sc[i]->setSeed(dis_arr[i]);
2547:     }
2548:     if(chkBoxDjAll->isChecked())chkBoxDjAll->setText("全选");
2549:     else chkBoxDjAll->setText("全不选");
2550:     chkBoxDjFlag = true;
```

## mainwindow.cpp | MainWindow::chkBoxDjAll_click | 原文件第2551-2553行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2551:     updateTableList();
2552: }
2553: 
```

## mainwindow.cpp | MainWindow::chkBoxDjTitle_click | 原文件第2554-2563行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2554: void MainWindow::chkBoxDjTitle_click() {
2555:     if(chkBoxDjTitle->isChecked()) {
2556:         for(int i=0;i<32;i++) {
2557:             sc[i]->setTitleEnable(true);
2558:             sc[i]->setcmbDjIdEnable(true);
2559:             //sc[i]->setcmbMenuEnable(true);
2560:         }
2561:     } else {
2562:         for(int i=0;i<32;i++) {
2563:             sc[i]->setTitleEnable(false);
```

## mainwindow.cpp | MainWindow::chkBoxDjTitle_click | 原文件第2564-2571行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2564:             sc[i]->setcmbDjIdEnable(false);
2565:             //sc[i]->setcmbMenuEnable(false);
2566:         }
2567:     }
2568: }
2569: 
2570: 
2571: 
```

## mainwindow.cpp | MainWindow::mediaStateChanged | 原文件第2572-2581行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2572: void MainWindow::mediaStateChanged(QMediaPlayer::State state) {
2573:     if(state == QMediaPlayer::StoppedState) {
2574:         //doGroupActions = false;
2575:         pbtnDoActionByPlayMusic->setText("音乐同步执行");
2576:         player->stop();
2577:         uart_send_str("$DST!");//停止按钮
2578:         actionDisTimer->stop();
2579:     }
2580: }
2581: 
```

## mainwindow.cpp | MainWindow::handleError | 原文件第2582-2590行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2582: void MainWindow::handleError(QSerialPort::SerialPortError error)
2583: {
2584:     if (error == QSerialPort::ResourceError) {
2585:         QMessageBox::critical(this, tr("Critical Error"), serial->errorString());
2586:         //closeSerialPort();
2587:         serial->close();
2588: //        console->setEnabled(false);
2589: //        ui->actionConnect->setEnabled(true);
2590: //        ui->actionDisconnect->setEnabled(false);
```

## mainwindow.cpp | MainWindow::handleError | 原文件第2591-2595行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2591: //        ui->actionConfigure->setEnabled(true);
2592: //        ui->statusBar->showMessage(tr("Disconnected"));
2593:     }
2594: }
2595: 
```

## mainwindow.cpp | MainWindow::readData | 原文件第2596-2605行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2596: void MainWindow::readData()
2597: {
2598:     QByteArray data = serial->readAll();
2599:     QString str_to_show;
2600:     str_to_show.prepend(data);
2601:     //console->putData(data);
2602:     uart_get_show(str_to_show);
2603: 
2604: }
2605: 
```

## mainwindow.cpp | MainWindow::eventFilter | 原文件第2606-2614行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2606: bool MainWindow::eventFilter(QObject *obj, QEvent *event) {
2607:     if (obj == dataRecvEdit) {
2608:         if (event->type() == QEvent::MouseButtonDblClick) {
2609:             //QKeyEvent *keyEvent = static_cast<QKeyEvent*>(event);
2610:             qDebug() << "Ate key press";
2611:             //return true;
2612:         } else {
2613:             //return false;
2614:         }
```

## mainwindow.cpp | MainWindow::eventFilter | 原文件第2615-2625行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2615:     } else if (obj == dataRecvEdit->viewport()) {
2616:     // To do.....
2617:         if (event->type() == QEvent::MouseButtonDblClick) {
2618:             qDebug() << "MouseButtonDblClick";
2619:             dataRecvEdit->clear();
2620:             //return true;
2621:         }
2622: //    } else {
2623: //    // pass the event on to the parent class
2624: //        return QMainWindow::eventFilter(obj, event);
2625:     }
```

## mainwindow.cpp | MainWindow::eventFilter | 原文件第2626-2636行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2626: 
2627:     if (obj == dataSendEdit) {
2628:         if (event->type() == QEvent::MouseButtonDblClick) {
2629:             //QKeyEvent *keyEvent = static_cast<QKeyEvent*>(event);
2630:             qDebug() << "Ate key press";
2631:             //return true;
2632:         } else {
2633:             //return false;
2634:         }
2635:     } else if (obj == dataSendEdit->viewport()) {
2636:     // To do.....
```

## mainwindow.cpp | MainWindow::eventFilter | 原文件第2637-2647行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2637:         if (event->type() == QEvent::MouseButtonDblClick) {
2638:             qDebug() << "MouseButtonDblClick";
2639:             dataSendEdit->clear();
2640:             //return true;
2641:         }
2642: //    } else {
2643: //    // pass the event on to the parent class
2644: //        return QMainWindow::eventFilter(obj, event);
2645:     }
2646: 
2647:     if (obj == dj_pannel) {
```

## mainwindow.cpp | MainWindow::eventFilter | 原文件第2648-2659行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2648:         if (event->type() == QEvent::MouseButtonDblClick) {
2649:             qDebug() << "Ate key press";
2650:         } else {
2651:         }
2652:     }
2653: 
2654: 
2655:     return QMainWindow::eventFilter(obj, event);
2656:     //return true;
2657:  }
2658: 
2659: 
```

## mainwindow.cpp | MainWindow::openProjectFile | 原文件第2660-2674行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2660: void MainWindow::openProjectFile(QString name){
2661:     QString filename = name;
2662: 
2663:     //文件名判断
2664:     if(filename == "") {
2665:         filename = QFileDialog::getOpenFileName(this, tr("打开文件"), 0, tr("ini文件(*.ini)\n所有文件(*.*)"));  //添加更多的文件类型
2666:     }
2667: 
2668:     //文件长度判断
2669:     if(!filename.length()){
2670:         return ;
2671:     }
2672: 
2673:     QFile file(filename);
2674:     //如果打开失败则提示并退出函数
```

## mainwindow.cpp | MainWindow::openProjectFile | 原文件第2675-2682行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2675:     if(!file.open(QIODevice::ReadOnly | QIODevice::Text)){
2676:         QMessageBox::warning(this, tr("打开失败"),
2677:                              tr("抱歉! 未能打开此文件, 这可能是由于没有足够的权限造成的. 您可以尝试使用chmod按钮修改文件权限."),
2678:                              QMessageBox::Ok);
2679:         return;
2680:     }
2681: 
2682:     ////////////////////////////////////设置ini句柄
```

## mainwindow.cpp | MainWindow::openProjectFile | 原文件第2683-2690行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2683:     QSettings *configIni = new QSettings(filename, QSettings::IniFormat, 0);
2684:     configIni->setIniCodec("UTF-8");
2685: 
2686:     ////////////////////////////////////全局变量
2687:     QString block_global("global");
2688:     QString timeDownloadStr = QString(block_global).append("/timeDownload");
2689:     int timeDownload_temp  = configIni->value(timeDownloadStr,"-1000").toInt();
2690:     if(timeDownload_temp != -1000){
```

## mainwindow.cpp | MainWindow::openProjectFile | 原文件第2691-2702行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2691:         timeDownload = timeDownload_temp;
2692:     }
2693: 
2694:     QString modeRobotStr = QString(block_global).append("/modeRobot");
2695:     int modeRobot_temp  = configIni->value(modeRobotStr,"-1000").toInt();
2696:     if(modeRobot_temp != -1000){
2697:         modeRobot = modeRobot_temp;
2698:     }
2699: 
2700: qDebug() << "555555555555555555";
2701: 
2702:     ////////////////////////////////////坐标解析
```

## mainwindow.cpp | MainWindow::openProjectFile | 原文件第2703-2709行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2703:     int i = 0;//, dj_num = 0;
2704:     for(i = 0;i < MAX_STEER_NUM;i ++){
2705:         QString block = QString("steer%1").arg(i);
2706:         QString titlekey = QString(block).append("/title");
2707:         QString idkey = QString(block).append("/id");
2708:         QString xkey = QString(block).append("/x");
2709:         QString ykey = QString(block).append("/y");
```

## mainwindow.cpp | MainWindow::openProjectFile | 原文件第2710-2717行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2710:         QString biaskey = QString(block).append("/bias");
2711:         QString visiblekey = QString(block).append("/enable");
2712:         QString pminkey = QString(block).append("/pmin");
2713:         QString pmaxkey = QString(block).append("/pmax");
2714:         QString labLeftkey = QString(block).append("/labLeft");
2715:         QString labRightkey = QString(block).append("/labRight");
2716: 
2717:         //抬头
```

## mainwindow.cpp | MainWindow::openProjectFile | 原文件第2718-2728行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2718:         QString djTitle = configIni->value(titlekey,"").toString();
2719:         if(djTitle == "") {
2720:             djTitle = "S"+QString::number(i);
2721:         }
2722:         sc[i]->setTitle(djTitle);
2723:         sc[i]->setLableIndex(QString::number(i) + "号");
2724: 
2725:         //ID号
2726:         int id = configIni->value(idkey,"-1000").toInt();
2727:         if(id == -1000){
2728:             id = i;
```

## mainwindow.cpp | MainWindow::openProjectFile | 原文件第2729-2741行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2729:         }
2730:         sc[i]->setId(id);
2731:         djLstId[i] = id;
2732: 
2733:         int x = configIni->value(xkey,"-1000").toInt();
2734:         int y = configIni->value(ykey,"-1000").toInt();
2735:         if(x == -1000 || y == -1000){
2736:             continue;
2737:         } else {
2738:             sc[i]->move(x,y);
2739:         }
2740: 
2741:         int bias = configIni->value(biaskey,"").toInt();
```

## mainwindow.cpp | MainWindow::openProjectFile | 原文件第2742-2753行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2742:         if(bias == -1000){
2743:             bias = 0;
2744:         }
2745:         sc[i]->setBias(bias);
2746:         dj_bias[i] = bias;
2747: 
2748:         int pmin = configIni->value(pminkey,"").toInt();
2749:         if(pmin<500 || pmin>2500)pmin=500;
2750:         sc[i]->setPmin(pmin);
2751: 
2752:         int pmax = configIni->value(pmaxkey,"").toInt();
2753:         if(pmax<500 || pmax>2500)pmax=2500;
```

## mainwindow.cpp | MainWindow::openProjectFile | 原文件第2754-2765行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2754:         sc[i]->setPmax(pmax);
2755: 
2756:         QString labLeft = configIni->value(labLeftkey,"").toString();
2757:         if(labLeft == "") {
2758:             labLeft = "小";
2759:         }
2760:         sc[i]->setlabLeft(labLeft);
2761: 
2762:         QString labRight = configIni->value(labRightkey,"").toString();
2763:         if(labRight == "") {
2764:             labRight = "大";
2765:         }
```

## mainwindow.cpp | MainWindow::openProjectFile | 原文件第2766-2780行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2766:         sc[i]->setlabRight(labRight);
2767: 
2768:         bool beSeed = configIni->value(visiblekey,"").toBool();
2769:         dis_arr[i] = beSeed;
2770:         dis_arr_load[i] = dis_arr[i];
2771:         dis_arr_diy[i] = dis_arr[i];
2772: 
2773: 
2774:         //sc[i]->setSeed(beSeed);
2775:        // chkBoxDj[i]->setChecked(beSeed);
2776:     }
2777: 
2778: 
2779:     //chkBoxDjBias->setChecked(false);
2780: 
```

## mainwindow.cpp | MainWindow::openProjectFile | 原文件第2781-2792行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2781:     justComboBoxSteerNumber = true;
2782: 
2783:     ////////////////////////////////////动作组解析
2784:     QString block_group("group");
2785:     int groupIndex = 0;
2786:     actionGroupListMng.actionGroupList.clear();
2787:     while(1){
2788: 
2789:         ActionGroup group;
2790:         group.init();
2791:         QString key;
2792:         key.sprintf("/G%04d", groupIndex);
```

## mainwindow.cpp | MainWindow::openProjectFile | 原文件第2793-2804行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2793:         key = QString(block_group).append(key);
2794:         QString str = configIni->value(key,"").toString();
2795: 
2796:         if(str == ""){
2797:             break;
2798:         }
2799: 
2800:         qDebug() << "Get:" <<str;
2801: 
2802:         //statusLabel->setText("Get:" + str);
2803:         if(str.contains("$")) {
2804:             QString temp = "$" + (str.split('$').at(1)).split('!').at(0) + "!";
```

## mainwindow.cpp | MainWindow::openProjectFile | 原文件第2805-2816行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2805:             group.setCmdStr(temp);
2806:             group.setIsGroup(false);
2807:         } else {
2808:             group.setIsGroup(true);
2809:         }
2810: 
2811:         QRegExp rx("#(\\d+)P(\\d+)T(\\d+)!");
2812:         group.setIndex(groupIndex);
2813:         int pos = 0, itemIndex = 0, itemIndexBak = 0;
2814:         while ((pos = rx.indexIn(str, pos)) != -1) {
2815:             ActionGroupItem item;
2816: 
```

## mainwindow.cpp | MainWindow::openProjectFile | 原文件第2817-2826行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2817:             item.setIndex(itemIndex);
2818:             item.setId(rx.cap(1).toInt());
2819:             if(groupIndex == 0) {
2820:                 item.setPwm(1500);
2821:             } else {
2822:                 item.setPwm(rx.cap(2).toInt());
2823:             }
2824:             item.setTime(rx.cap(3).toInt());
2825:             item.setEnable(dis_arr[itemIndex]);
2826:             group.setItem(itemIndex, item);
```

## mainwindow.cpp | MainWindow::openProjectFile | 原文件第2827-2840行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2827:             pos += rx.matchedLength();
2828: 
2829:             itemIndex ++;
2830:             if(itemIndex == MAX_STEER_NUM)break;
2831:         }
2832: 
2833:         actionGroupListMng.actionGroupList.push_back(group);
2834:         groupIndex ++;
2835:     }
2836:     actionGroupListMng.currentSelected = 0;
2837: 
2838: 
2839:     ////////////////////////////////////更新列表
2840:     updateTableList();
```

## mainwindow.cpp | MainWindow::openProjectFile | 原文件第2841-2843行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2841:     //updateWindowState();
2842: }
2843: 
```

## mainwindow.cpp | MainWindow::saveProjectFile | 原文件第2844-2853行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2844: void MainWindow::saveProjectFile(QString name){
2845:     QString filename = name;
2846:     if(filename == ""){
2847:         filename = QFileDialog::getSaveFileName(this,tr("保存文件"),saveDefaultFileName,tr("ini文件(*.ini)\n所有文件(*.*)"));
2848:         //QFile(saveDefaultFileName).remove();
2849:     }
2850:     if(!filename.length()) {
2851:         return;
2852:     }
2853: 
```

## mainwindow.cpp | MainWindow::saveProjectFile | 原文件第2854-2863行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2854:     QSettings *configIni = new QSettings(filename, QSettings::IniFormat, 0);
2855:     configIni->setIniCodec("UTF8");
2856:     configIni->clear();
2857: 
2858:     //保存全局变量
2859:     QString block_global("global");
2860: 
2861:     QString timeDownloadStr = QString(block_global).append("/timeDownload");
2862:     configIni->setValue(timeDownloadStr,QString::number(timeDownload));
2863: 
```

## mainwindow.cpp | MainWindow::saveProjectFile | 原文件第2864-2877行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2864:     QString modeRobotStr = QString(block_global).append("/modeRobot");
2865:     configIni->setValue(modeRobotStr,QString::number(modeRobot));
2866: 
2867: 
2868:     //-----动作组存储
2869:     QString block;
2870:     block = QString("group");
2871:     QList<ActionGroup>::iterator iter;
2872:     int i = 0;
2873: 
2874:     //写入新的键值对
2875:     i = 0;
2876:     QString group_s, group_temp_s;
2877:     group_s = "{ NUM ";
```

## mainwindow.cpp | MainWindow::saveProjectFile | 原文件第2878-2887行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2878:     for(i=0;i<MAX_STEER_NUM;i++) {
2879:         group_temp_s.sprintf("------S%02d------", i);
2880:         group_s = group_s + group_temp_s;
2881:     }
2882:     group_s = group_s + "}";
2883:     QString key = QString(block).append("/GROUP");
2884:     configIni->setValue(key,group_s);
2885: 
2886: 
2887:     i = 0;
```

## mainwindow.cpp | MainWindow::saveProjectFile | 原文件第2888-2895行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2888:     for(iter = actionGroupListMng.actionGroupList.begin();iter != actionGroupListMng.actionGroupList.end();iter ++){
2889:         group_s.sprintf("/G%04d", i);
2890:         key = QString(block).append(group_s); //
2891:         if((*iter).isGroup()) {
2892:             configIni->setValue(key,(*iter).toStoreString());
2893:         } else {
2894:             configIni->setValue(key,(*iter).combineCmdStr());
2895:         }
```

## mainwindow.cpp | MainWindow::saveProjectFile | 原文件第2896-2907行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2896:         i ++;
2897:         if(i==10000)break;
2898:     }
2899: 
2900:     //-----保存舵机位置
2901:     for(int i = 0;i < MAX_STEER_NUM;i ++){
2902:         block = QString("steer%1").arg(i);
2903: 
2904:         QString titlekey = QString(block).append("/title");
2905:         configIni->setValue(titlekey,QString::fromUtf8(sc[i]->getTitle().toUtf8()));
2906: 
2907:         QString idkey = QString(block).append("/id");
```

## mainwindow.cpp | MainWindow::saveProjectFile | 原文件第2908-2917行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2908:         configIni->setValue(idkey,QString::number(sc[i]->getId()));
2909: 
2910:         QString xkey = QString(block).append("/x");
2911:         QString ykey = QString(block).append("/y");
2912: 
2913:         configIni->setValue(xkey,sc[i]->x());
2914:         configIni->setValue(ykey,sc[i]->y());
2915: 
2916:         QString biaskey = QString(block).append("/bias");
2917:         configIni->setValue(biaskey,sc[i]->getBias());
```

## mainwindow.cpp | MainWindow::saveProjectFile | 原文件第2918-2927行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2918: 
2919:         QString pminkey = QString(block).append("/pmin");
2920:         configIni->setValue(pminkey,sc[i]->getPmin());
2921: 
2922:         QString pmaxkey = QString(block).append("/pmax");
2923:         configIni->setValue(pmaxkey,sc[i]->getPmax());
2924: 
2925:         QString labLeftkey = QString(block).append("/labLeft");
2926:         configIni->setValue(labLeftkey,QString::fromUtf8(sc[i]->labLeft().toUtf8()));
2927: 
```

## mainwindow.cpp | MainWindow::saveProjectFile | 原文件第2928-2940行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2928:         QString labRightkey = QString(block).append("/labRight");
2929:         configIni->setValue(labRightkey,QString::fromUtf8(sc[i]->labRight().toUtf8()));
2930: 
2931:         dis_arr[i] = sc[i]->getSeed();
2932:         QString enablekey = QString(block).append("/enable");
2933:         configIni->setValue(enablekey,dis_arr[i]);
2934:     }
2935: 
2936: 
2937:     delete configIni;
2938:     return ;
2939: }
2940: 
```

## mainwindow.cpp | MainWindow::zxSldPos_valueChanged | 原文件第2941-2947行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2941: void MainWindow::zxSldPos_valueChanged() {
2942:     QString tmpStr;
2943:     tmpStr.sprintf("#%03dP%04dT%04d!", zxCboxIdNew->currentIndex(), zxSldPos->value(), zxSldTime->value());
2944:     zxPbtnSendData->setText(tmpStr);
2945:     uart_send_str(tmpStr);
2946: }
2947: 
```

## mainwindow.cpp | MainWindow::zxSldTime_valueChanged | 原文件第2948-2951行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2948: void MainWindow::zxSldTime_valueChanged() {
2949:     zxSpbxTime->setValue(zxSldTime->value());
2950: }
2951: 
```

## mainwindow.cpp | MainWindow::zxButtonClicked | 原文件第2952-2960行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2952: void MainWindow::zxButtonClicked() {
2953:     QPushButton* btn = qobject_cast<QPushButton*>(sender());
2954:     QString tmpStr = "";
2955:     static bool zxPbtnPosUInitFlag = false;
2956:     if(btn == zxPbtnVersionRead) {
2957:         qDebug() << "zxPbtnVersionRead Clicked";
2958:         tmpStr.sprintf("#255PVER!");
2959:     } else if(btn == zxPbtnIdWrite) {
2960:         qDebug() << "zxPbtnIdWrite Clicked";
```

## mainwindow.cpp | MainWindow::zxButtonClicked | 原文件第2961-2966行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2961:         tmpStr.sprintf("#%03dPID%03d!", zxCboxIdOld->currentIndex(), zxCboxIdNew->currentIndex());
2962:     } else if(btn == zxPbtnIdRead) {
2963:         qDebug() << "zxPbtnIdRead Clicked";
2964:         tmpStr.sprintf("#255PID!");
2965:     } else if(btn == zxPbtnModeWrite) {
2966:         qDebug() << "zxPbtnModeWrite Clicked";
```

## mainwindow.cpp | MainWindow::zxButtonClicked | 原文件第2967-2973行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2967:         tmpStr.sprintf("#%03dPMOD%d!", zxCboxIdNew->currentIndex(), zxCboxMode->currentIndex()+1);
2968:     } else if(btn == zxPbtnModeRead) {
2969:         qDebug() << "zxPbtnModeRead Clicked";
2970:         tmpStr.sprintf("#%03dPMOD!", zxCboxIdNew->currentIndex());
2971:     } else if(btn == zxPbtnPmin) {
2972:         qDebug() << "zxPbtnPmin Clicked";
2973:         tmpStr.sprintf("#%03dPSMI!", zxCboxIdNew->currentIndex());
```

## mainwindow.cpp | MainWindow::zxButtonClicked | 原文件第2974-2981行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2974:     } else if(btn == zxPbtnPmax) {
2975:         qDebug() << "zxPbtnPmax Clicked";
2976:         tmpStr.sprintf("#%03dPSMX!", zxCboxIdNew->currentIndex());
2977:     } else if(btn == zxPbtnPosReset) {
2978:         qDebug() << "zxPbtnPosReset Clicked";
2979:         zxSldPos->setValue(1500);
2980:         tmpStr.sprintf("#%03dP1500T0000!", zxCboxIdNew->currentIndex());
2981:     } else if(btn == zxPbtnPosRead) {
```

## mainwindow.cpp | MainWindow::zxButtonClicked | 原文件第2982-2989行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2982:         qDebug() << "zxPbtnPosRead Clicked";
2983:         tmpStr.sprintf("#%03dPRAD!", zxCboxIdNew->currentIndex());
2984:     } else if(btn == zxPbtnPosInit) {
2985:         qDebug() << "zxPbtnPosInit Clicked";
2986:         tmpStr.sprintf("#%03dPCSD!", zxCboxIdNew->currentIndex());
2987:     } else if(btn == zxPbtnPosUInit) {
2988:         qDebug() << "zxPbtnPosUInit Clicked";
2989:         if(!zxPbtnPosUInitFlag) {
```

## mainwindow.cpp | MainWindow::zxButtonClicked | 原文件第2990-2998行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2990:             zxPbtnPosUInit->setText("开机复力");
2991:             tmpStr.sprintf("#%03dPCSM!", zxCboxIdNew->currentIndex());
2992:         } else {
2993:             zxPbtnPosUInit->setText("开机释力");
2994:             tmpStr.sprintf("#%03dPCSR!", zxCboxIdNew->currentIndex());
2995:         }
2996:         zxPbtnPosUInitFlag = !zxPbtnPosUInitFlag;
2997:     } else if(btn == zxPbtnPULK) {
2998:         qDebug() << "zxPbtnPULK Clicked";
```

## mainwindow.cpp | MainWindow::zxButtonClicked | 原文件第2999-3006行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
2999:         tmpStr.sprintf("#%03dPULK!", zxCboxIdNew->currentIndex());
3000:     } else if(btn == zxPbtnPULR) {
3001:         qDebug() << "zxPbtnPULR Clicked";
3002:         tmpStr.sprintf("#%03dPULR!", zxCboxIdNew->currentIndex());
3003:     } else if(btn == zxPbtnPSCK) {
3004:         qDebug() << "zxPbtnPSCK Clicked";
3005:         tmpStr.sprintf("#%03dPSCK!", zxCboxIdNew->currentIndex());
3006:     } else if(btn == zxPbtnPCLE0) {
```

## mainwindow.cpp | MainWindow::zxButtonClicked | 原文件第3007-3015行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
3007:         qDebug() << "zxPbtnPCLE0 Clicked";
3008:         tmpStr.sprintf("#%03dPCLE0!", zxCboxIdNew->currentIndex());
3009:     } else if(btn == zxPbtnSendData) {
3010:         qDebug() << "zxPbtnSendData Clicked";
3011:         tmpStr = zxPbtnSendData->text();
3012:     } else if(btn == zxPbtnGetData) {
3013:         qDebug() << "zxPbtnGetData Clicked";
3014:         zxPbtnGetData->setText("");
3015:         return;
```

## mainwindow.cpp | MainWindow::zxButtonClicked | 原文件第3016-3027行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
3016:     } else if(btn == zxPbtnTimeReset) {
3017:         qDebug() << "zxPbtnTimeReset Clicked";
3018:         zxSldTime->setValue(1000);
3019:         return;
3020:     } else {
3021:     }
3022: 
3023:     zxWRead = true;
3024:     zxPbtnSendData->setText(tmpStr);
3025:     uart_send_str(tmpStr);
3026: }
3027: 
```

## mainwindow.cpp | MainWindow::zxSpbxTime_valueChanged | 原文件第3028-3032行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
3028: void MainWindow::zxSpbxTime_valueChanged() {
3029:     zxSldTime->setValue(zxSpbxTime->value());
3030: }
3031: 
3032: 
```

## mainwindow.cpp | MainWindow::show_actionListMenu | 原文件第3033-3044行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
3033: void MainWindow::show_actionListMenu(const QPoint& pos)
3034: {
3035:     QMenu *cmenu = NULL;
3036:     if(cmenu)//保证同时只存在一个menu，及时释放内存
3037:     {
3038:         delete cmenu;
3039:         cmenu = NULL;
3040:     }
3041:     cmenu = new QMenu(actionList);
3042: 
3043:     QAction *ascendSortAction = cmenu->addAction("编辑");
3044:     //QAction *descendSortAction = cmenu->addAction("降序");
```

## mainwindow.cpp | MainWindow::show_actionListMenu | 原文件第3045-3050行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
3045:     //QAction *filterAction = cmenu->addAction("过滤");
3046:     //QAction *reshowAction = cmenu->addAction("重载");
3047: 
3048:     //connect(ascendSortAction, SIGNAL(triggered(bool)), this, SLOT(sort_ascend()));
3049:     //connect(descendSortAction, SIGNAL(triggered(bool)), this, SLOT(sort_descend()));
3050:     //connect(filterAction, SIGNAL(triggered(bool)), this, SLOT(show_filter_dlg()));
```

## mainwindow.cpp | MainWindow::show_actionListMenu | 原文件第3051-3056行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
3051:     //connect(reshowAction, SIGNAL(triggered(bool)), this, SLOT(reshow_data()));
3052: 
3053:     cmenu->exec(QCursor::pos());//在当前鼠标位置显示
3054:     //cmenu->exec(pos)是在viewport显示
3055: }
3056: 
```

## mainwindow.cpp | MainWindow::show_dj_pannelMenu | 原文件第3057-3068行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
3057: void MainWindow::show_dj_pannelMenu(const QPoint& pos)
3058: {
3059:     QMenu *cmenu = NULL;
3060:     if(cmenu)//保证同时只存在一个menu，及时释放内存
3061:     {
3062:         delete cmenu;
3063:         cmenu = NULL;
3064:     }
3065:     cmenu = new QMenu(dj_pannel);
3066:     cmenu->setStyleSheet(" QMenu {"
3067:                          " background-color: white;"
3068:                         "  border: 1px solid white;"
```

## mainwindow.cpp | MainWindow::show_dj_pannelMenu | 原文件第3069-3078行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
3069:                      " }"
3070: 
3071:                      " QMenu::item {"
3072:                         " background-color: transparent;"
3073: 
3074:                         " font: 75 12pt;"
3075:                         " width: 120px;"
3076:                         " height: 40px;"
3077:                         " text-align: center; "
3078:                         "  border-bottom:1px solid #DBDBDB;"
```

## mainwindow.cpp | MainWindow::show_dj_pannelMenu | 原文件第3079-3088行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
3079:                      " }"
3080: 
3081:                     "  QMenu::item:selected { "
3082:                        "   background-color: #2dabf9;"
3083:                      " }");
3084: 
3085:     //QAction *robotLoad = cmenu->addAction(" 载入界面");
3086:     //QAction *robotReset = cmenu->addAction(" 窗口复位");
3087:     QAction *robotDiy = cmenu->addAction(" 自定义界面");
3088:     QAction *robotJxb = cmenu->addAction(" 6自由度机械臂");
```

## mainwindow.cpp | MainWindow::show_dj_pannelMenu | 原文件第3089-3095行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
3089:     //QAction *robotXFoot = cmenu->addAction(" 智能小双足");
3090:     //QAction *descendSortAction = cmenu->addAction("降序");
3091:     //QAction *filterAction = cmenu->addAction("过滤");
3092:     //QAction *reshowAction = cmenu->addAction("重载");
3093: 
3094: 
3095:     //connect(robotLoad, SIGNAL(triggered(bool)), this, SLOT(robotLoad_action()));
```

## mainwindow.cpp | MainWindow::show_dj_pannelMenu | 原文件第3096-3100行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
3096:     //connect(robotReset, SIGNAL(triggered(bool)), this, SLOT(robotReset_action()));
3097:     connect(robotDiy, SIGNAL(triggered(bool)), this, SLOT(robotDiy_action()));
3098:     connect(robotJxb, SIGNAL(triggered(bool)), this, SLOT(robotJxb_action()));
3099:     //connect(robotXFoot, SIGNAL(triggered(bool)), this, SLOT(robotXFoot_action()));
3100:     //connect(reshowAction, SIGNAL(triggered(bool)), this, SLOT(reshow_data()));
```

## mainwindow.cpp | MainWindow::show_dj_pannelMenu | 原文件第3101-3107行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
3101: 
3102:     cmenu->exec(QCursor::pos());//在当前鼠标位置显示
3103:     //cmenu->exec(pos)是在viewport显示
3104: }
3105: 
3106: 
3107: 
```

## mainwindow.cpp | MainWindow::sort_ascend | 原文件第3108-3111行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
3108: void MainWindow::sort_ascend() {
3109:     qDebug() << "sort_ascend Clicked";
3110: }
3111: 
```

## mainwindow.cpp | MainWindow::mdelay | 原文件第3112-3119行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
3112: void MainWindow::mdelay(int t) {
3113:     QMutex mutex;
3114:     QWaitCondition sleep;
3115:     mutex.lock();
3116:     sleep.wait(&mutex, t);
3117:     mutex.unlock();
3118: }
3119: 
```

## mainwindow.cpp | MainWindow::initFirstGroup | 原文件第3120-3127行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
3120: void MainWindow::initFirstGroup(){
3121:     if(actionGroupListMng.actionGroupList.count() == 0) {
3122:         ActionGroup newGroup;
3123:         newGroup.init();
3124:         actionGroupListMng.currentSelected = 0;
3125:         newGroup.setIndex(actionGroupListMng.currentSelected);
3126:         actionGroupListMng.actionGroupList.push_back(newGroup);
3127:         for(int i=0;i<MAX_STEER_NUM;i++) {
```

## mainwindow.cpp | MainWindow::initFirstGroup | 原文件第3128-3136行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
3128:             if(dis_arr[i]) {
3129:                 sc[i]->setPwm(1500);
3130:             }
3131:         }
3132:         updateTableList();
3133:         updateWindowState();
3134:     }
3135: }
3136: 
```

## mainwindow.cpp | MainWindow::dj_pannel_clicked | 原文件第3137-3142行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.cpp
以下为原始源码，不是截图OCR。
```
3137: void MainWindow::dj_pannel_clicked(DragWidget* dra) {
3138:     qDebug() << "dj_pannel_clicked";
3139:     for(int i=0;i<MAX_STEER_NUM;i++) {
3140:         dis_arr_diy[i] = dis_arr[i];
3141:     }
3142: }
```

## mainwindow.h | 文件开头/全局定义 | 原文件第1-19行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
1: #ifndef MAINWINDOW_H
2: #define MAINWINDOW_H
3: 
4: #include <QMainWindow>
5: #include <QProgressBar>
6: 
7: #include <qlist.h>
8: #include <QModelIndex>
9: #include <QMediaPlayer>
10: #include <QMediaPlaylist>
11: #include <QAction>
12: #include <QUndoStack>
13: #include <QtWidgets>
14: #include <QTabWidget>
15: #include <QMediaObject>
16: #include <QPixmap>
17: #include "actiongroup.h"
18: #include "mythread.h"
19: 
```

## mainwindow.h | 文件开头/全局定义 | 原文件第20-40行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
20: #include <QtSerialPort/QSerialPort>
21: 
22: class QUndoStack;
23: class QAction;
24: class QMenu;
25: class QComboBox;
26: class QPushButton;
27: class QLabel;
28: class QLineEdit;
29: class FormSteerCtl;
30: class QTextEdit;
31: class QListWidget;
32: class ActionGroup;
33: class QSpinBox;
34: class QCheckBox;
35: class QListWidgetItem;
36: class QSlider;
37: class QRadioButton;
38: class QTimer;
39: 
40: class DragWidget;
```

## mainwindow.h | 文件开头/全局定义 | 原文件第41-59行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
41: class QMediaPlayer;
42: class QMediaPlaylist;
43: class QSystemTrayIcon;
44: 
45: 
46: 
47: //延时，TIME_OUT是串口读写的延时
48: #define TIME_OUT 10
49: 
50: //连续发送定时器计时间隔,200ms
51: #define OBO_TIMER_INTERVAL 200
52: 
53: //载入文件时，如果文件大小超过TIP_FILE_SIZE字节则提示文件过大是否继续打开
54: #define TIP_FILE_SIZE 10240
55: //载入文件最大长度限制在MAX_FILE_SIZE字节内
56: #define MAX_FILE_SIZE 102400
57: 
58: //舵机个数
59: //#define MAX_STEER_NUM       64
```

## mainwindow.h | 文件开头/全局定义 | 原文件第60-80行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
60: #define ZDY_BUTTON_MAX      16
61: #define LD_ITEM_MAX      64             //联动配置
62: #define CY_ITEM_MAX      16             //常用配置
63: 
64: 
65: #define ZDY_DEFAULT_HANG    3
66: #define ZDY_DEFAULT_LIE     3
67: #define IR_PAGE_MAX         3
68: #define IR_BUTTON_MAX       21
69: 
70: 
71: namespace Ui {
72: class MainWindow;
73: }
74: 
75: 
76: class MainWindow : public QMainWindow
77: {
78:     Q_OBJECT
79: 
80: public:
```

## mainwindow.h | 文件开头/全局定义 | 原文件第81-94行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
81:     explicit MainWindow(QWidget *parent = 0);
82:     ~MainWindow();
83:     void createActions();
84:     void createMenus();
85:     void ui_init();
86:     void sendToLogDisplay(QString str);
87:     QString mytr(const char* chars);
88: 
89: private:
90:     void updateWindowItem(int index); //更新动作组
91:     void updateSingleMotion(int index);
92:     void updateTableList();  //
93:     void updateWindowState();
94: 
```

## mainwindow.h | 文件开头/全局定义 | 原文件第95-105行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
95:     int getGroupMaxTime(ActionGroup &group);
96:     int getGroupMaxTimeFromStr(QString str);
97: 
98:     bool serialNotOpen();
99:     void drawdj_pannel(int steerNum);
100:     void add_steer_enable(int index, bool enable);
101:     QString addBiasStr(QString str);
102:     void first_file_save();
103:     QString uart_get_str();
104:     void uart_send_str(QString str);
105:     void uart_get_show(QString str);
```

## mainwindow.h | 文件开头/全局定义 | 原文件第106-119行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
106:     void uart_send_show(QString str);
107:     void parse_rx_data(QString str_get);
108:     int musicTimeCount;
109:     void mdelay(int t);
110:     void initFirstGroup();
111: 
112: private:
113:     Ui::MainWindow *ui;
114:     QTimer *rxTimer;
115: 
116:     QAction *openProjectAction;
117:     QAction *saveProjectAction;
118:     QAction *openPlacementAction;
119:     QAction *savePlacementAction;
```

## mainwindow.h | 文件开头/全局定义 | 原文件第120-133行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
120:     QAction *openOffsetAction;
121:     QAction *saveOffsetAction;
122:     QAction *openTransactionGroupAction;
123:     QAction *saveTransactionGroupAction;
124: 
125:     QAction *manDoc;
126:     QMenu *fileMenu;
127:     QMenu *helpMenu;
128:     QMenu *viewMenu;
129: 
130:     QComboBox *cbSerialCom;
131:     QComboBox *cbBaudRate;
132:     QPushButton *pbtnConnect;
133:     QPushButton *pbtnSerialLed;
```

## mainwindow.h | 文件开头/全局定义 | 原文件第134-147行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
134:     QLabel *labSerialLed;
135: 
136:     QSpinBox *btnHang, *btnLie;
137:     QPushButton *btn_ok, *btn_setting;
138: 
139:     QTextEdit *dataSendEdit;
140:     QPushButton *pushButtonDataSend;
141: 
142:     QTextEdit *dataRecvEdit;
143:     QPushButton *pushButtonClearDataOut;
144:     //QCheckBox *checkBoxAsHex;
145: 
146:     FormSteerCtl *sc[MAX_STEER_NUM];
147:     QCheckBox *chkBoxDj[MAX_STEER_NUM];
```

## mainwindow.h | 文件开头/全局定义 | 原文件第148-161行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
148:     QCheckBox *chkBoxDjAll, *chkBoxDjTitle;
149: 
150:     struct {
151:         int currentSelected;
152:         QList<ActionGroup> actionGroupList;
153:     }actionGroupListMng;
154: 
155:     QListWidget *actionList;
156:     QPushButton *addActionGroup;
157:     QPushButton *insertActionGroup;
158:     QPushButton *delActionGroup;
159:     QPushButton *preSaveActionCmd;
160:     QPushButton *clearActionGroup;
161: 
```

## mainwindow.h | 文件开头/全局定义 | 原文件第162-175行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
162:     //控制区控件
163: 
164:     //QComboBox *comboBoxSteerNumber;
165:     QLineEdit *lineEditSteerIds;
166:     QPushButton *pushButtonSelectSteers;
167: 
168:     QRadioButton *radioButtonGlobal;
169:     QRadioButton *radioButtonDisperse;
170: 
171:     //QRadioButton *radioButtonOnlineBias;
172:     //QRadioButton *radioButtonOfflineBias;
173: 
174:     QSpinBox *spinBoxStartSteer;
175:     QSpinBox *spinBoxEndSteer;
```

## mainwindow.h | 文件开头/全局定义 | 原文件第176-190行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
176:     QPushButton *pushButtonSelectSteer;
177:     QCheckBox *checkBoxSelectAll;
178: 
179:     QSlider *hsliderTimeControl;
180:     QSpinBox *spinBoxTimeControl;
181:     QPushButton *pbtnResetTime;
182:     QCheckBox *checkBoxDisperseGroup;
183: 
184:     QPushButton *pbtnResetPwm;
185:     QSpinBox *spinBoxPwmControl;
186: 
187:     QPushButton *pbtnResetBias;
188:     QSpinBox *spinBoxBiasControl;
189: 
190: 
```

## mainwindow.h | 文件开头/全局定义 | 原文件第191-203行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
191:     QPushButton *ptbDnTimeBias;
192:     QSpinBox    *spBTimeBias;
193: 
194: 
195:     QPushButton *pbtnActionSave;
196:     QPushButton *pbtnDEG;           //擦除动作组
197:     QPushButton *pbtnDRS;           //获取下位机
198:     QPushButton *pbtnCGP;           //检查动作组
199:     QPushButton *pbtnDEA;           //擦除下位机
200: 
201:     QSpinBox *spinBoxStartGroup;
202:     QSpinBox *spinBoxEndGroup;
203:     QRadioButton *radioButtonOnline;
```

## mainwindow.h | 文件开头/全局定义 | 原文件第204-214行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
204:     QRadioButton *radioButtonOffline;
205:     QRadioButton *radioButtonAckDone;
206:     QRadioButton *radioButtonNoAckDone;
207:     QSpinBox *spinBoxDoTimes;
208:     QSpinBox *spinBoxDelayTimes;
209: 
210:     QPushButton *pbtnDoActionOnline;
211:     QPushButton *pbtnDoActionOffline;
212:     QPushButton *pbtnDoActionSave;
213:     QPushButton *pbtnDoActionStop;
214:     QPushButton *pbtnDoAction_reset;
```

## mainwindow.h | 文件开头/全局定义 | 原文件第215-229行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
215:     QPushButton *pbtnDoAction_read;
216:     QPushButton *pbtnDoAction_clear;
217: 
218:     QPushButton *pbtnPwmReset;
219:     QPushButton *pbtnTimeReset;
220: 
221:     //
222:     QPushButton *pushButtonAddMusic;
223:     QPushButton *pbtnDoActionByPlayMusic;
224:     QLabel      *music_time_label;
225: 
226:     QSpinBox *downloadStart;
227:     QSpinBox *downloadEnd;
228:     //QComboBox *downloadBlock;
229: 
```

## mainwindow.h | 文件开头/全局定义 | 原文件第230-245行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
230:     QCheckBox *click_list_send;
231:     QCheckBox *title_lock;
232:     QPushButton *listToCmd;
233:     //QPushButton *pbtnBiasSave;
234:     MyThread *threadA;
235:     QSerialPort *serial;
236: 
237:     QTimer *ackDownCheckTimer;
238: 
239:     QTimer *actionTimer;
240:     QTimer *actionDisTimer;
241:     QTimer *autoSaveTimer;
242:     QTimer *zxReadAdcTimer;
243:     QTimer *ldSaveTimer;
244:     QTimer *cySaveTimer;
245: 
```

## mainwindow.h | 文件开头/全局定义 | 原文件第246-259行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
246: 
247:     QString saveDefaultFileName;
248:     QMediaPlayer *player;
249:     QMediaPlaylist *playList;
250:     //QSystemTrayIcon *trayIcon;
251: 
252:     //1
253:     QLabel *zxLableVersion;
254:     QPushButton *zxPbtnVersionRead;
255:     //2
256:     QComboBox *zxCboxIdOld, *zxCboxIdNew;
257:     QPushButton *zxPbtnIdWrite, *zxPbtnIdRead;
258:     //3
259:     QComboBox *zxCboxMode;
```

## mainwindow.h | 文件开头/全局定义 | 原文件第260-272行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
260:     QPushButton *zxPbtnModeWrite, *zxPbtnModeRead;
261:     //4
262:     QPushButton *zxPbtnPmin, *zxPbtnPmax, *zxPbtnPosReset;
263:     QSlider *zxSldPos;
264:     //4
265:     QSlider *zxSldTime;
266:     QSpinBox *zxSpbxTime;
267:     QPushButton *zxPbtnTimeReset;
268: 
269:     //5
270:     QPushButton *zxPbtnPosRead, *zxPbtnPosInit, *zxPbtnPosUInit;
271:     //6
272:     QPushButton *zxPbtnPULK, *zxPbtnPULR, *zxPbtnPSCK;
```

## mainwindow.h | 文件开头/全局定义 | 原文件第273-288行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
273:     //7
274:     QPushButton *zxPbtnPCLE0;
275:     //8
276:     QPushButton *zxPbtnSendData, *zxPbtnGetData;
277: 
278: 
279: 
280:     QPushButton *zxRelease, *zxURelease;
281:     QPushButton *zxCorrect, *zxReset, *zxInit;
282:     QPushButton *zxReadADC;
283:     QCheckBox *startZXMode;
284: 
285: 
286:     QLabel *statusLabel;
287: 
288:     QComboBox *kzq_cbSerialCom, *kzq_cbBaudRate, *kzq_BtcbSerialCom;
```

## mainwindow.h | 文件开头/全局定义 | 原文件第289-297行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
289:     QTextEdit *kzq_cmdDsi, *kzq_actionDsi, *kzq_btName;
290:     QPushButton *kzq_biasReset, *kzq_uartReset, *kzq_preReset,*kzq_btReset, *kzq_drsReset, *kzq_dsi;
291:     QPushButton *kzq_peizhi1,*kzq_peizhi2,*kzq_peizhi3,*kzq_peizhi4, *kzq_ctl_mode, *kzq_ctl_mode_P1, *kzq_ctl_mode_Z1;
292: 
293:     QPushButton *kzq_getConfig;
294:     QScrollArea *dj_sca;
295:     DragWidget *dj_pannel;
296:     QLabel *dj_bg;
297: 
```

## mainwindow.h | 文件开头/全局定义 | 原文件第298-309行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
298: //    QUndoStack *m_UndoStack;
299: //    QAction *undoAction;
300: //    QAction *redoAction;
301: 
302: private:
303:     bool isDisperseGroup;
304:     bool listclick[MAX_STEER_NUM];
305:     bool serialOpened;
306:     bool doGroupActionsStop, doGroupActionsOnline, doGroupActionsOffline;
307:     bool doGroupActionsFlag;
308:     int startActionIndex, startActionIndexBak;
309:     int endActionIndex, endActionIndexBak;
```

## mainwindow.h | 文件开头/全局定义 | 原文件第310-323行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
310:     bool actionIndexDoOnceOk;
311:     int startDloadAction;
312:     int startDloadActionBak;
313:     bool doForever;
314:     bool justListClick[MAX_STEER_NUM];
315:     bool dis_arr[MAX_STEER_NUM];
316:     bool dis_arr_load[MAX_STEER_NUM];
317:     bool dis_arr_diy[MAX_STEER_NUM];
318:     bool adc_arr[MAX_STEER_NUM];
319:     int  djLstId[MAX_STEER_NUM];
320: 
321: 
322:     int timesToDo;
323:     int timeDownload;
```

## mainwindow.h | 文件开头/全局定义 | 原文件第324-340行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
324:     bool pwmBiasDownload;
325:     bool timeBiasDownload;
326: 
327:     bool timeLdDownloadFlag;
328:     int timeLdDownloadIndex;
329: 
330:     bool timeCyDownloadFlag;
331:     int timeCyDownloadIndex;
332: 
333:     bool timeZxReadAdcFlag;
334:     bool timeLdDownLoadFlag;
335: 
336:     bool justComboBoxSteerNumber;
337:     bool saveActionsFlag;
338:     int musicTimeLen;
339: 
340: private slots:
```

## mainwindow.h | 文件开头/全局定义 | 原文件第341-350行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
341:     void autoScroll();
342:     void pbtnConnectUpdate();
343:     void actionTimer_timeout();
344:     void openProjectFile(QString name="");
345:     void autosave_timeout();
346:     void ackDownCheckTimer_timeout();
347:     void saveProjectFile(QString name="");
348:     void savePlacementAction_triggered();
349:     void openPlacementAction_triggered();
350:     void saveOffsetAction_triggered();
```

## mainwindow.h | 文件开头/全局定义 | 原文件第351-361行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
351:     void openOffsetAction_triggered();
352:     void openTransactionGroupAction_triggered();
353:     void saveTransactionGroupAction_triggered();
354: 
355:     void steerCtl_valueChanged(FormSteerCtl *stc);
356:     void steerCtl_currentIndexChanged(FormSteerCtl *stc);
357: 
358:     void steerCtl_clicked(FormSteerCtl *stc);
359: 
360:     void pbtnConnect_clicked();
361:     void pushButtonClearDataOut_clicked();
```

## mainwindow.h | 文件开头/全局定义 | 原文件第362-373行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
362:     void clearActionGroup_clicked();
363:     void clearBias_clicked();
364:     void pushButtonDataSend_clicked();
365:     void pbtnSerialLed_clicked();
366:     void btn_ok_clicked();
367:     void btn_setting_clicked();
368: 
369:     void addActionGroup_clicked();
370:     void insertActionGroup_clicked();
371:     void delActionGroup_clicked();
372: 
373:     void actionList_clicked(QModelIndex index);
```

## mainwindow.h | 文件开头/全局定义 | 原文件第374-386行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
374:     void actionList_doubleClick(QModelIndex index);
375: //    void pushButtonSelectSteers_clicked();
376: 
377:     void hsliderTimeControl_valueChanged(int val);
378:     void pbtnResetPwm_clicked();
379: 
380:     void pbtnPwmReset_clicked();
381:     void pbtnTimeReset_clicked();
382: 
383:     void handleSerialRxData();
384:     void handlerSerialTimeout(QString msg);
385:     void hanlderSerialError(QString error);
386: 
```

## mainwindow.h | 文件开头/全局定义 | 原文件第387-397行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
387:     void pbtnDEA_clicked();
388:     void pbtnActionSave_clicked();
389:     void pbtnCGP_clicked();
390:     void pbtnDRS_clicked();
391:     void pushButtonReadSlaveActionGroups_clicked();
392:     void pbtnDEG_clicked();
393:     void pbtnOpenFile_clicked();
394:     void pbtnDoActionOnline_clicked();
395:     void pbtnDoActionOffline_clicked();
396:     void pbtnDoActionSave_clicked();
397:     void pbtnDoActionStop_clicked();
```

## mainwindow.h | 文件开头/全局定义 | 原文件第398-408行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
398:     void pbtnDoAction_reset_clicked();
399:     void pbtnDoAction_read_clicked();
400:     void pbtnDoAction_clear_clicked();
401:     void actionList_activated(QModelIndex index);
402:     void actionList_rowChanged(int row);
403:     //
404:     //void handleRxData();
405:     //void comboBoxSteerNumber_indexChanged(int index);
406: 
407:     void pbtnResetTime_clicked();
408: 
```

## mainwindow.h | 文件开头/全局定义 | 原文件第409-420行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
409:     void spinBoxTimeControl_valueChanged(int val);
410:     void spinBoxPwmControl_valueChanged(int val);
411:     void manDoc_triggered();
412:     void updateSerialPortList();
413: 
414: 
415:     void pushButtonAddMusic_clicked();
416:     void pbtnDoActionByPlayMusic_clicked();
417: 
418:     void spinBoxBiasControl_valueChanged(int val);
419:     void pbtnResetBias_clicked();
420:     void title_lock_click();
```

## mainwindow.h | 文件开头/全局定义 | 原文件第421-434行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
421:     void listToCmd_clicked();
422:     //void pbtnBiasSave_clicked();
423:     void ptbDnTimeBias_clicked();
424:     void chkBoxDj_click();
425:     void chkBoxDjAll_click();
426:     void chkBoxDjTitle_click();
427:     void mediaStateChanged(QMediaPlayer::State state);
428: 
429:     void readData();
430:     void handleError(QSerialPort::SerialPortError error);
431: 
432: 
433: 
434:     void on_actionHelp_triggered();
```

## mainwindow.h | 文件开头/全局定义 | 原文件第435-449行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
435:     void pushButton_sendData_clicked();
436: 
437:     void zxSldPos_valueChanged();
438:     void zxSldTime_valueChanged();
439:     void zxSpbxTime_valueChanged();
440: 
441:     void zxButtonClicked();
442: 
443:     void show_actionListMenu(const QPoint& pos);
444:     void show_dj_pannelMenu(const QPoint& pos);
445:     void sort_ascend();
446: 
447:     void dj_pannel_clicked(DragWidget* dra);
448: 
449: protected:
```

## mainwindow.h | 文件开头/全局定义 | 原文件第450-457行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.h
以下为原始源码，不是截图OCR。
```
450:     void closeEvent(QCloseEvent *e);
451:     //void mouseDoubleClickEvent(QMouseEvent *event);
452:     bool eventFilter(QObject *obj, QEvent *event);
453: 
454: };
455: 
456: 
457: #endif // MAINWINDOW_H
```

## mainwindow.ui | 文件开头/全局定义 | 原文件第1-15行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.ui
以下为原始源码，不是截图OCR。
```
1: <?xml version="1.0" encoding="UTF-8"?>
2: <ui version="4.0">
3:  <class>MainWindow</class>
4:  <widget class="QMainWindow" name="MainWindow">
5:   <property name="geometry">
6:    <rect>
7:     <x>0</x>
8:     <y>0</y>
9:     <width>709</width>
10:     <height>816</height>
11:    </rect>
12:   </property>
13:   <property name="windowTitle">
14:    <string>HID Bootloader</string>
15:   </property>
```

## mainwindow.ui | 文件开头/全局定义 | 原文件第16-28行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.ui
以下为原始源码，不是截图OCR。
```
16:   <widget class="QWidget" name="centralWidget">
17:    <layout class="QGridLayout" name="gridLayout_3"/>
18:   </widget>
19:   <widget class="QStatusBar" name="statusBar"/>
20:   <widget class="QMenuBar" name="menuBar">
21:    <property name="geometry">
22:     <rect>
23:      <x>0</x>
24:      <y>0</y>
25:      <width>709</width>
26:      <height>23</height>
27:     </rect>
28:    </property>
```

## mainwindow.ui | 文件开头/全局定义 | 原文件第29-41行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.ui
以下为原始源码，不是截图OCR。
```
29:    <widget class="QMenu" name="menu">
30:     <property name="title">
31:      <string>操作</string>
32:     </property>
33:     <addaction name="actionOpenFirmwareFile"/>
34:     <addaction name="actionUpgradeFirmware"/>
35:    </widget>
36:    <widget class="QMenu" name="menu_2">
37:     <property name="title">
38:      <string>帮助</string>
39:     </property>
40:     <addaction name="actionHelp"/>
41:    </widget>
```

## mainwindow.ui | 文件开头/全局定义 | 原文件第42-53行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.ui
以下为原始源码，不是截图OCR。
```
42:    <addaction name="menu"/>
43:    <addaction name="menu_2"/>
44:   </widget>
45:   <action name="actionOpenFirmwareFile">
46:    <property name="icon">
47:     <iconset resource="myapp.qrc">
48:      <normaloff>:/ico/open_file.png</normaloff>:/ico/open_file.png</iconset>
49:    </property>
50:    <property name="text">
51:     <string>打开固件</string>
52:    </property>
53:    <property name="shortcut">
```

## mainwindow.ui | 文件开头/全局定义 | 原文件第54-67行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.ui
以下为原始源码，不是截图OCR。
```
54:     <string>Ctrl+O</string>
55:    </property>
56:   </action>
57:   <action name="actionUpgradeFirmware">
58:    <property name="icon">
59:     <iconset resource="myapp.qrc">
60:      <normaloff>:/ico/upgrade.png</normaloff>:/ico/upgrade.png</iconset>
61:    </property>
62:    <property name="text">
63:     <string>升级固件</string>
64:    </property>
65:    <property name="shortcut">
66:     <string>Ctrl+U</string>
67:    </property>
```

## mainwindow.ui | 文件开头/全局定义 | 原文件第68-81行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.ui
以下为原始源码，不是截图OCR。
```
68:   </action>
69:   <action name="actionHelp">
70:    <property name="icon">
71:     <iconset resource="myapp.qrc">
72:      <normaloff>:/ico/user_help.png</normaloff>:/ico/user_help.png</iconset>
73:    </property>
74:    <property name="text">
75:     <string>帮助</string>
76:    </property>
77:    <property name="shortcut">
78:     <string>Ctrl+H</string>
79:    </property>
80:   </action>
81:  </widget>
```

## mainwindow.ui | 文件开头/全局定义 | 原文件第82-87行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mainwindow.ui
以下为原始源码，不是截图OCR。
```
82:  <layoutdefault spacing="6" margin="11"/>
83:  <resources>
84:   <include location="myapp.qrc"/>
85:  </resources>
86:  <connections/>
87: </ui>
```

## mythread.cpp | 文件开头/全局定义 | 原文件第1-14行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mythread.cpp
以下为原始源码，不是截图OCR。
```
1: #include "mythread.h"
2: #include <QtDebug>
3: //FOR RS232
4: #include <QtSerialPort/QSerialPort>
5: #include <QtSerialPort/QSerialPortInfo>
6: //FOR RS232
7: 
8: 
9: MyThread::MyThread() {
10:    stopped = true;
11:    com_opened = false;
12:    tx_event = false;
13: }
14: 
```

## mythread.cpp | MyThread::run | 原文件第15-23行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mythread.cpp
以下为原始源码，不是截图OCR。
```
15: void MyThread::run() {
16:     QSerialPort my_serialport;
17:     while(!stopped){
18:         //open
19:         while((!stopped) && (!com_opened)) {
20:             //qDebug() << "open starting";
21:             my_serialport.setPortName(portnum);
22:             my_serialport.setBaudRate(portrate.toInt());
23:             my_serialport.setDataBits(QSerialPort::Data8);
```

## mythread.cpp | MyThread::run | 原文件第24-28行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mythread.cpp
以下为原始源码，不是截图OCR。
```
24:             my_serialport.setParity(QSerialPort::NoParity);
25:             my_serialport.setStopBits(QSerialPort::OneStop);
26:             my_serialport.setFlowControl(QSerialPort::NoFlowControl);
27: 
28:             //connect(my_serialport,SIGNAL(deviceD),this,SLOT(hasComDiscovered(const QextPortInfo&)));
```

## mythread.cpp | MyThread::run | 原文件第29-36行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mythread.cpp
以下为原始源码，不是截图OCR。
```
29:             //connect(my_serialport,SIGNAL(deviceRemoved(const QextPortInfo&)),this,SLOT(hasComRemoved(const QextPortInfo&)));
30: 
31:             if(!my_serialport.open(QIODevice::ReadWrite)) {
32:                 emit error(QString().setNum(my_serialport.error()));
33:                 sleep(1);
34:                 qDebug() << "open com err";
35:                 com_opened=false;
36:                 continue;
```

## mythread.cpp | MyThread::run | 原文件第37-47行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mythread.cpp
以下为原始源码，不是截图OCR。
```
37:             } else {
38:                 qDebug() << "open com ok";
39:                 com_opened=true;
40:             }            
41:         }
42: 
43:         //tx
44:         if(this->com_opened && this->tx_event) {
45:             this->tx_event=false;
46:             my_serialport.clear(QSerialPort::AllDirections);
47:             //qDebug() << "Brush:" <<"send data to com"<<this->TxData.length();
```

## mythread.cpp | MyThread::run | 原文件第48-58行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mythread.cpp
以下为原始源码，不是截图OCR。
```
48:             //qDebug() << "arr size:" <<this->TxData.length();
49:             my_serialport.write(this->TxData);
50:             if (my_serialport.waitForBytesWritten(50)) {
51:                 //qDebug() << "Brush:" <<"send data success";
52:                 emit(this->comSend());
53:             } else {
54:                // qDebug() << "Brush:" <<"send time out";
55:             }
56:         }
57: 
58:         //rx
```

## mythread.cpp | MyThread::run | 原文件第59-71行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mythread.cpp
以下为原始源码，不是截图OCR。
```
59:         if(this->com_opened) {
60:             if (my_serialport.waitForReadyRead(5)) {
61:                 while(my_serialport.waitForReadyRead(5));
62:                 requestData = my_serialport.readAll();
63:                 //signal
64:                 emit(this->comRecive());
65:             }
66:         }
67:     }
68: 
69:     if(stopped) {
70:         if(com_opened) {
71:             my_serialport.close();
```

## mythread.cpp | MyThread::run | 原文件第72-77行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mythread.cpp
以下为原始源码，不是截图OCR。
```
72:             com_opened = false;
73:         }
74:         //qDebug() << "serial stopped";
75:     }
76: }
77: 
```

## mythread.cpp | MyThread::stopCom | 原文件第78-82行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mythread.cpp
以下为原始源码，不是截图OCR。
```
78: void MyThread::stopCom()
79: {
80:    stopped=true;
81: 
82: }
```

## mythread.cpp | MyThread::startCom | 原文件第83-88行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mythread.cpp
以下为原始源码，不是截图OCR。
```
83: void MyThread::startCom()
84: {
85:    stopped=false;
86: 
87: }
88: 
```

## mythread.cpp | MyThread::setPortnum | 原文件第89-92行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mythread.cpp
以下为原始源码，不是截图OCR。
```
89: void MyThread::setPortnum(const QString &num) {
90:     portnum=num;
91: }
92: 
```

## mythread.cpp | MyThread::setPortrate | 原文件第93-97行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mythread.cpp
以下为原始源码，不是截图OCR。
```
93: void MyThread::setPortrate(const QString &rate) {
94:     portrate=rate;
95: 
96: }
97: 
```

## mythread.cpp | comOpened | 原文件第98-101行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mythread.cpp
以下为原始源码，不是截图OCR。
```
98: bool MyThread:: comOpened(void) {
99:     return com_opened;
100: }
101: 
```

## mythread.cpp | comStoped | 原文件第102-105行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mythread.cpp
以下为原始源码，不是截图OCR。
```
102: bool MyThread:: comStoped(void) {
103:     return stopped;
104: }
105: 
```

## mythread.cpp | MyThread::changeTxState | 原文件第106-109行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mythread.cpp
以下为原始源码，不是截图OCR。
```
106: void MyThread::changeTxState(bool stat) {
107:     tx_event=stat;
108: }
109: 
```

## mythread.cpp | MyThread::changeComState | 原文件第110-116行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mythread.cpp
以下为原始源码，不是截图OCR。
```
110: void MyThread::changeComState(bool stat) {
111:    com_opened=stat;
112: }
113: 
114: 
115: /////////////////////////////////////////////////////
116: 
```

## mythread.cpp | MyThread::changeRxState | 原文件第117-120行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mythread.cpp
以下为原始源码，不是截图OCR。
```
117: void MyThread::changeRxState(bool stat) {
118:     rx_event=stat;
119: }
120: 
```

## mythread.cpp | MyThread::setMessage | 原文件第121-131行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mythread.cpp
以下为原始源码，不是截图OCR。
```
121: void MyThread::setMessage(const QString &message) {
122:    messageStr = message;
123: }
124: 
125: //void MyThread::hasComDiscovered(const QextPortInfo&) {
126: 
127: //}
128: 
129: //void MyThread::hasComRemoved(const QextPortInfo&) {
130: //    stopped = true;
131: //}
```

## mythread.h | 文件开头/全局定义 | 原文件第1-19行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mythread.h
以下为原始源码，不是截图OCR。
```
1: #ifndef MYTHREAD_H
2: #define MYTHREAD_H
3: 
4: #include <QThread>
5: #include <stdio.h>
6: #include <QtGlobal>
7: #include <QtSerialPort/QSerialPort>
8: #include <QtSerialPort/QSerialPortInfo>
9: 
10: class MyThread : public QThread
11: {
12:     Q_OBJECT
13: public:
14:     QByteArray requestData;
15:     QByteArray TxData;
16:     MyThread();
17: 
18: 
19:     void setPortnum(const QString &num);
```

## mythread.h | 文件开头/全局定义 | 原文件第20-35行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mythread.h
以下为原始源码，不是截图OCR。
```
20:     void setPortrate(const QString &rate);
21:     void stopCom();
22:     void startCom();
23:     bool comOpened(void);
24:     bool comStoped(void);
25: 
26:     void setMessage(const QString &message);
27:     void changeTxState(bool stat);
28:     void changeRxState(bool stat);
29:     void changeComState(bool stat);
30: 
31: 
32: signals:
33: 
34:     void comRecive();
35:     void comSend();
```

## mythread.h | 文件开头/全局定义 | 原文件第36-52行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mythread.h
以下为原始源码，不是截图OCR。
```
36:     void request(const QString &s);
37:     void error(const QString &s);
38: 
39: protected:
40:     void run();
41: 
42: private:
43:     QString messageStr;
44:     QString portnum;
45:     QString portrate;
46:     volatile bool com_opened;
47:     volatile bool stopped;
48:     volatile bool tx_event;
49:     volatile bool rx_event;
50: 
51: private slots:
52:     //void hasComDiscovered(const QextPortInfo&);
```

## mythread.h | 文件开头/全局定义 | 原文件第53-57行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/mythread.h
以下为原始源码，不是截图OCR。
```
53:     //void hasComRemoved(const QextPortInfo&);
54: 
55: };
56: 
57: #endif // MYTHREAD_H
```

## ZideMini.pro | 文件开头/全局定义 | 原文件第1-19行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/ZideMini.pro
以下为原始源码，不是截图OCR。
```
1: #-------------------------------------------------
2: #
3: # Project created by QtCreator 2016-05-04T12:10:09
4: #
5: #-------------------------------------------------
6: 
7: QT       += core gui serialport\
8:     multimediawidgets
9: 
10: greaterThan(QT_MAJOR_VERSION, 4): QT += widgets
11: 
12: TARGET = Zide_MINI
13: TEMPLATE = app
14: 
15: FORMS += \
16:     formsteerctl.ui \
17:     mainwindow.ui
18: 
19: HEADERS += \
```

## ZideMini.pro | 文件开头/全局定义 | 原文件第20-41行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/ZideMini.pro
以下为原始源码，不是截图OCR。
```
20:     actiongroup.h \
21:     actiongroupitem.h \
22:     dragwidget.h \
23:     formsteerctl.h \
24:     mainwindow.h \
25:     mythread.h
26: 
27: SOURCES += \
28:     actiongroup.cpp \
29:     actiongroupitem.cpp \
30:     dragwidget.cpp \
31:     formsteerctl.cpp \
32:     main.cpp \
33:     mainwindow.cpp \
34:     mythread.cpp
35: 
36: RC_FILE += \
37:     myapp.rc
38: 
39: RESOURCES += \
40:     myapp.qrc
41: 
```

## ZideMini.pro | 文件开头/全局定义 | 原文件第42-44行
来源：005-拓展资料\03-开源上位机代码\开源上位机代码.zip!/开源上位机代码/001-QT源代码/ZideMini源码QT.zip!/coding/ZideMini.pro
以下为原始源码，不是截图OCR。
```
42: OTHER_FILES += \
43:     升级说明.txt \
44:     images/bg_general.png
```
