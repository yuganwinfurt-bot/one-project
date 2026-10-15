## application.cc | 文件开头/全局定义 | 原文件第1-15行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
1: #include "application.h"
2: #include "board.h"
3: #include "display.h"
4: #include "system_info.h"
5: #include "ml307_ssl_transport.h"
6: #include "audio_codec.h"
7: #include "mqtt_protocol.h"
8: #include "websocket_protocol.h"
9: #include "font_awesome_symbols.h"
10: #include "iot/thing_manager.h"
11: #include "assets/lang_config.h"
12: 
13: #include <cstring>
14: #include <esp_log.h>
15: #include <cJSON.h>
```

## application.cc | 文件开头/全局定义 | 原文件第16-36行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
16: #include <driver/gpio.h>
17: #include <arpa/inet.h>
18: #include <esp_app_desc.h>
19: 
20: #define TAG "Application"
21: 
22: 
23: static const char* const STATE_STRINGS[] = {
24:     "unknown",
25:     "starting",
26:     "configuring",
27:     "idle",
28:     "connecting",
29:     "listening",
30:     "speaking",
31:     "upgrading",
32:     "activating",
33:     "fatal_error",
34:     "invalid_state"
35: };
36: 
```

## application.cc | 文件开头/全局定义 | 原文件第37-47行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
37: Application::Application() {
38:     event_group_ = xEventGroupCreate();
39:     background_task_ = new BackgroundTask(4096 * 8);
40: 
41:     esp_timer_create_args_t clock_timer_args = {
42:         .callback = [](void* arg) {
43:             Application* app = (Application*)arg;
44:             app->OnClockTimer();
45:         },
46:         .arg = this,
47:         .dispatch_method = ESP_TIMER_TASK,
```

## application.cc | 文件开头/全局定义 | 原文件第48-60行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
48:         .name = "clock_timer",
49:         .skip_unhandled_events = true
50:     };
51:     esp_timer_create(&clock_timer_args, &clock_timer_handle_);
52: }
53: 
54: Application::~Application() {
55:     if (clock_timer_handle_ != nullptr) {
56:         esp_timer_stop(clock_timer_handle_);
57:         esp_timer_delete(clock_timer_handle_);
58:     }
59:     if (background_task_ != nullptr) {
60:         delete background_task_;
```

## application.cc | 文件开头/全局定义 | 原文件第61-64行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
61:     }
62:     vEventGroupDelete(event_group_);
63: }
64: 
```

## application.cc | Application::CheckNewVersion | 原文件第65-76行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
65: void Application::CheckNewVersion() {
66:     auto& board = Board::GetInstance();
67:     auto display = board.GetDisplay();
68:     // Check if there is a new firmware version available
69:     ota_.SetPostData(board.GetJson());
70: 
71:     const int MAX_RETRY = 10;
72:     int retry_count = 0;
73: 
74:     while (true) {
75:         if (!ota_.CheckVersion()) {
76:             retry_count++;
```

## application.cc | Application::CheckNewVersion | 原文件第77-86行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
77:             if (retry_count >= MAX_RETRY) {
78:                 ESP_LOGE(TAG, "Too many retries, exit version check");
79:                 return;
80:             }
81:             ESP_LOGW(TAG, "Check new version failed, retry in %d seconds (%d/%d)", 60, retry_count, MAX_RETRY);
82:             vTaskDelay(pdMS_TO_TICKS(60000));
83:             continue;
84:         }
85:         retry_count = 0;
86: 
```

## application.cc | Application::CheckNewVersion | 原文件第87-94行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
87:         if (ota_.HasNewVersion()) {
88:             Alert(Lang::Strings::OTA_UPGRADE, Lang::Strings::UPGRADING, "happy", Lang::Sounds::P3_UPGRADE);
89:             // Wait for the chat state to be idle
90:             do {
91:                 vTaskDelay(pdMS_TO_TICKS(3000));
92:             } while (GetDeviceState() != kDeviceStateIdle);
93: 
94:             // Use main task to do the upgrade, not cancelable
```

## application.cc | Application::CheckNewVersion | 原文件第95-102行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
95:             Schedule([this, display]() {
96:                 SetDeviceState(kDeviceStateUpgrading);
97:                 
98:                 display->SetIcon(FONT_AWESOME_DOWNLOAD);
99:                 std::string message = std::string(Lang::Strings::NEW_VERSION) + ota_.GetFirmwareVersion();
100:                 display->SetChatMessage("system", message.c_str());
101: 
102:                 auto& board = Board::GetInstance();
```

## application.cc | Application::CheckNewVersion | 原文件第103-111行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
103:                 board.SetPowerSaveMode(false);
104: #if CONFIG_USE_WAKE_WORD_DETECT
105:                 wake_word_detect_.StopDetection();
106: #endif
107:                 // 预先关闭音频输出，避免升级过程有音频操作
108:                 auto codec = board.GetAudioCodec();
109:                 codec->EnableInput(false);
110:                 codec->EnableOutput(false);
111:                 {
```

## application.cc | Application::CheckNewVersion | 原文件第112-120行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
112:                     std::lock_guard<std::mutex> lock(mutex_);
113:                     audio_decode_queue_.clear();
114:                 }
115:                 background_task_->WaitForCompletion();
116:                 delete background_task_;
117:                 background_task_ = nullptr;
118:                 vTaskDelay(pdMS_TO_TICKS(1000));
119: 
120:                 ota_.StartUpgrade([display](int progress, size_t speed) {
```

## application.cc | Application::CheckNewVersion | 原文件第121-127行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
121:                     char buffer[64];
122:                     snprintf(buffer, sizeof(buffer), "%d%% %zuKB/s", progress, speed / 1024);
123:                     display->SetChatMessage("system", buffer);
124:                 });
125: 
126:                 // If upgrade success, the device will reboot and never reach here
127:                 display->SetStatus(Lang::Strings::UPGRADE_FAILED);
```

## application.cc | Application::CheckNewVersion | 原文件第128-138行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
128:                 ESP_LOGI(TAG, "Firmware upgrade failed...");
129:                 vTaskDelay(pdMS_TO_TICKS(3000));
130:                 Reboot();
131:             });
132: 
133:             return;
134:         }
135: 
136:         // No new version, mark the current version as valid
137:         ota_.MarkCurrentVersionValid();
138:         std::string message = std::string(Lang::Strings::VERSION) + ota_.GetCurrentVersion();
```

## application.cc | Application::CheckNewVersion | 原文件第139-147行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
139:         display->ShowNotification(message.c_str());
140:     
141:         if (ota_.HasActivationCode()) {
142:             // Activation code is valid
143:             SetDeviceState(kDeviceStateActivating);
144:             ShowActivationCode();
145: 
146:             // Check again in 60 seconds or until the device is idle
147:             for (int i = 0; i < 60; ++i) {
```

## application.cc | Application::CheckNewVersion | 原文件第148-159行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
148:                 if (device_state_ == kDeviceStateIdle) {
149:                     break;
150:                 }
151:                 vTaskDelay(pdMS_TO_TICKS(1000));
152:             }
153:             continue;
154:         }
155: 
156:         SetDeviceState(kDeviceStateIdle);
157:         display->SetChatMessage("system", "");
158:         PlaySound(Lang::Sounds::P3_SUCCESS);
159:         // Exit the loop if upgrade or idle
```

## application.cc | Application::CheckNewVersion | 原文件第160-163行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
160:         break;
161:     }
162: }
163: 
```

## application.cc | Application::ShowActivationCode | 原文件第164-174行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
164: void Application::ShowActivationCode() {
165:     auto& message = ota_.GetActivationMessage();
166:     auto& code = ota_.GetActivationCode();
167: 
168:     struct digit_sound {
169:         char digit;
170:         const std::string_view& sound;
171:     };
172:     static const std::array<digit_sound, 10> digit_sounds{{
173:         digit_sound{'0', Lang::Sounds::P3_0},
174:         digit_sound{'1', Lang::Sounds::P3_1}, 
```

## application.cc | Application::ShowActivationCode | 原文件第175-184行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
175:         digit_sound{'2', Lang::Sounds::P3_2},
176:         digit_sound{'3', Lang::Sounds::P3_3},
177:         digit_sound{'4', Lang::Sounds::P3_4},
178:         digit_sound{'5', Lang::Sounds::P3_5},
179:         digit_sound{'6', Lang::Sounds::P3_6},
180:         digit_sound{'7', Lang::Sounds::P3_7},
181:         digit_sound{'8', Lang::Sounds::P3_8},
182:         digit_sound{'9', Lang::Sounds::P3_9}
183:     }};
184: 
```

## application.cc | Application::ShowActivationCode | 原文件第185-191行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
185:     // This sentence uses 9KB of SRAM, so we need to wait for it to finish
186:     Alert(Lang::Strings::ACTIVATION, message.c_str(), "happy", Lang::Sounds::P3_ACTIVATION);
187:     vTaskDelay(pdMS_TO_TICKS(1000));
188:     background_task_->WaitForCompletion();
189: 
190:     for (const auto& digit : code) {
191:         auto it = std::find_if(digit_sounds.begin(), digit_sounds.end(),
```

## application.cc | Application::ShowActivationCode | 原文件第192-198行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
192:             [digit](const digit_sound& ds) { return ds.digit == digit; });
193:         if (it != digit_sounds.end()) {
194:             PlaySound(it->sound);
195:         }
196:     }
197: }
198: 
```

## application.cc | Application::Alert | 原文件第199-205行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
199: void Application::Alert(const char* status, const char* message, const char* emotion, const std::string_view& sound) {
200:     ESP_LOGW(TAG, "Alert %s: %s [%s]", status, message, emotion);
201:     auto display = Board::GetInstance().GetDisplay();
202:     display->SetStatus(status);
203:     display->SetEmotion(emotion);
204:     display->SetChatMessage("system", message);
205:     if (!sound.empty()) {
```

## application.cc | Application::Alert | 原文件第206-209行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
206:         PlaySound(sound);
207:     }
208: }
209: 
```

## application.cc | Application::DismissAlert | 原文件第210-218行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
210: void Application::DismissAlert() {
211:     if (device_state_ == kDeviceStateIdle) {
212:         auto display = Board::GetInstance().GetDisplay();
213:         display->SetStatus(Lang::Strings::STANDBY);
214:         display->SetEmotion("neutral");
215:         display->SetChatMessage("system", "");
216:     }
217: }
218: 
```

## application.cc | Application::PlaySound | 原文件第219-228行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
219: void Application::PlaySound(const std::string_view& sound) {
220:     auto codec = Board::GetInstance().GetAudioCodec();
221:     codec->EnableOutput(true);
222:     SetDecodeSampleRate(16000);
223:     const char* data = sound.data();
224:     size_t size = sound.size();
225:     for (const char* p = data; p < data + size; ) {
226:         auto p3 = (BinaryProtocol3*)p;
227:         p += sizeof(BinaryProtocol3);
228: 
```

## application.cc | Application::PlaySound | 原文件第229-239行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
229:         auto payload_size = ntohs(p3->payload_size);
230:         std::vector<uint8_t> opus;
231:         opus.resize(payload_size);
232:         memcpy(opus.data(), p3->payload, payload_size);
233:         p += payload_size;
234: 
235:         std::lock_guard<std::mutex> lock(mutex_);
236:         audio_decode_queue_.emplace_back(std::move(opus));
237:     }
238: }
239: 
```

## application.cc | Application::ToggleChatState | 原文件第240-252行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
240: void Application::ToggleChatState() {
241:     if (device_state_ == kDeviceStateActivating) {
242:         SetDeviceState(kDeviceStateIdle);
243:         return;
244:     }
245: 
246:     if (!protocol_) {
247:         ESP_LOGE(TAG, "Protocol not initialized");
248:         return;
249:     }
250: 
251:     if (device_state_ == kDeviceStateIdle) {
252:         Schedule([this]() {
```

## application.cc | Application::ToggleChatState | 原文件第253-262行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
253:             SetDeviceState(kDeviceStateConnecting);
254:             if (!protocol_->OpenAudioChannel()) {
255:                 return;
256:             }
257: 
258:             keep_listening_ = true;
259:             protocol_->SendStartListening(kListeningModeAutoStop);
260:             SetDeviceState(kDeviceStateListening);
261:         });
262:     } else if (device_state_ == kDeviceStateSpeaking) {
```

## application.cc | Application::ToggleChatState | 原文件第263-272行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
263:         Schedule([this]() {
264:             AbortSpeaking(kAbortReasonNone);
265:         });
266:     } else if (device_state_ == kDeviceStateListening) {
267:         Schedule([this]() {
268:             protocol_->CloseAudioChannel();
269:         });
270:     }
271: }
272: 
```

## application.cc | Application::StartListening | 原文件第273-286行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
273: void Application::StartListening() {
274:     if (device_state_ == kDeviceStateActivating) {
275:         SetDeviceState(kDeviceStateIdle);
276:         return;
277:     }
278: 
279:     if (!protocol_) {
280:         ESP_LOGE(TAG, "Protocol not initialized");
281:         return;
282:     }
283:     
284:     keep_listening_ = false;
285:     if (device_state_ == kDeviceStateIdle) {
286:         Schedule([this]() {
```

## application.cc | Application::StartListening | 原文件第287-295行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
287:             if (!protocol_->IsAudioChannelOpened()) {
288:                 SetDeviceState(kDeviceStateConnecting);
289:                 if (!protocol_->OpenAudioChannel()) {
290:                     return;
291:                 }
292:             }
293:             protocol_->SendStartListening(kListeningModeManualStop);
294:             SetDeviceState(kDeviceStateListening);
295:         });
```

## application.cc | Application::StartListening | 原文件第296-304行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
296:     } else if (device_state_ == kDeviceStateSpeaking) {
297:         Schedule([this]() {
298:             AbortSpeaking(kAbortReasonNone);
299:             protocol_->SendStartListening(kListeningModeManualStop);
300:             SetDeviceState(kDeviceStateListening);
301:         });
302:     }
303: }
304: 
```

## application.cc | Application::StopListening | 原文件第305-313行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
305: void Application::StopListening() {
306:     Schedule([this]() {
307:         if (device_state_ == kDeviceStateListening) {
308:             protocol_->SendStopListening();
309:             SetDeviceState(kDeviceStateIdle);
310:         }
311:     });
312: }
313: 
```

## application.cc | Application::Start | 原文件第314-323行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
314: void Application::Start() {
315:     auto& board = Board::GetInstance();
316:     SetDeviceState(kDeviceStateStarting);
317: 
318:     /* Setup the display */
319:     auto display = board.GetDisplay();
320: 
321:     /* Setup the audio codec */
322:     auto codec = board.GetAudioCodec();
323:     opus_decode_sample_rate_ = codec->output_sample_rate();
```

## application.cc | Application::Start | 原文件第324-328行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
324:     opus_decoder_ = std::make_unique<OpusDecoderWrapper>(opus_decode_sample_rate_, 1);
325:     opus_encoder_ = std::make_unique<OpusEncoderWrapper>(16000, 1, OPUS_FRAME_DURATION_MS);
326:     // For ML307 boards, we use complexity 5 to save bandwidth
327:     // For other boards, we use complexity 3 to save CPU
328:     if (board.GetBoardType() == "ml307") {
```

## application.cc | Application::Start | 原文件第329-337行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
329:         ESP_LOGI(TAG, "ML307 board detected, setting opus encoder complexity to 5");
330:         opus_encoder_->SetComplexity(5);
331:     } else {
332:         ESP_LOGI(TAG, "WiFi board detected, setting opus encoder complexity to 3");
333:         opus_encoder_->SetComplexity(3);
334:     }
335: 
336:     if (codec->input_sample_rate() != 16000) {
337:         input_resampler_.Configure(codec->input_sample_rate(), 16000);
```

## application.cc | Application::Start | 原文件第338-345行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
338:         reference_resampler_.Configure(codec->input_sample_rate(), 16000);
339:     }
340:     codec->OnInputReady([this, codec]() {
341:         BaseType_t higher_priority_task_woken = pdFALSE;
342:         xEventGroupSetBitsFromISR(event_group_, AUDIO_INPUT_READY_EVENT, &higher_priority_task_woken);
343:         return higher_priority_task_woken == pdTRUE;
344:     });
345:     codec->OnOutputReady([this]() {
```

## application.cc | Application::Start | 原文件第346-355行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
346:         BaseType_t higher_priority_task_woken = pdFALSE;
347:         xEventGroupSetBitsFromISR(event_group_, AUDIO_OUTPUT_READY_EVENT, &higher_priority_task_woken);
348:         return higher_priority_task_woken == pdTRUE;
349:     });
350:     codec->Start();
351: 
352:     /* Start the main loop */
353:     xTaskCreate([](void* arg) {
354:         Application* app = (Application*)arg;
355:         app->MainLoop();
```

## application.cc | Application::Start | 原文件第356-366行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
356:         vTaskDelete(NULL);
357:     }, "main_loop", 4096 * 2, this, 3, nullptr);
358: 
359:     /* Wait for the network to be ready */
360:     board.StartNetwork();
361: 
362:     // Initialize the protocol
363:     display->SetStatus(Lang::Strings::LOADING_PROTOCOL);
364: #ifdef CONFIG_CONNECTION_TYPE_WEBSOCKET
365:     protocol_ = std::make_unique<WebsocketProtocol>();
366: #else
```

## application.cc | Application::Start | 原文件第367-374行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
367:     protocol_ = std::make_unique<MqttProtocol>();
368: #endif
369:     protocol_->OnNetworkError([this](const std::string& message) {
370:         SetDeviceState(kDeviceStateIdle);
371:         Alert(Lang::Strings::ERROR, message.c_str(), "sad", Lang::Sounds::P3_EXCLAMATION);
372:     });
373:     protocol_->OnIncomingAudio([this](std::vector<uint8_t>&& data) {
374:         std::lock_guard<std::mutex> lock(mutex_);
```

## application.cc | Application::Start | 原文件第375-381行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
375:         if (device_state_ == kDeviceStateSpeaking) {
376:             audio_decode_queue_.emplace_back(std::move(data));
377:         }
378:     });
379:     protocol_->OnAudioChannelOpened([this, codec, &board]() {
380:         board.SetPowerSaveMode(false);
381:         if (protocol_->server_sample_rate() != codec->output_sample_rate()) {
```

## application.cc | Application::Start | 原文件第382-386行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
382:             ESP_LOGW(TAG, "Server sample rate %d does not match device output sample rate %d, resampling may cause distortion",
383:                 protocol_->server_sample_rate(), codec->output_sample_rate());
384:         }
385:         SetDecodeSampleRate(protocol_->server_sample_rate());
386:         auto& thing_manager = iot::ThingManager::GetInstance();
```

## application.cc | Application::Start | 原文件第387-395行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
387:         protocol_->SendIotDescriptors(thing_manager.GetDescriptorsJson());
388:         std::string states;
389:         if (thing_manager.GetStatesJson(states, false)) {
390:             protocol_->SendIotStates(states);
391:         }
392:     });
393:     protocol_->OnAudioChannelClosed([this, &board]() {
394:         board.SetPowerSaveMode(true);
395:         Schedule([this]() {
```

## application.cc | Application::Start | 原文件第396-404行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
396:             auto display = Board::GetInstance().GetDisplay();
397:             display->SetChatMessage("system", "");
398:             SetDeviceState(kDeviceStateIdle);
399:         });
400:     });
401:     protocol_->OnIncomingJson([this, display](const cJSON* root) {
402:         // Parse JSON data
403:         auto type = cJSON_GetObjectItem(root, "type");
404:         if (strcmp(type->valuestring, "tts") == 0) {
```

## application.cc | Application::Start | 原文件第405-411行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
405:             auto state = cJSON_GetObjectItem(root, "state");
406:             if (strcmp(state->valuestring, "start") == 0) {
407:                 Schedule([this]() {
408:                     aborted_ = false;
409:                     if (device_state_ == kDeviceStateIdle || device_state_ == kDeviceStateListening) {
410:                         SetDeviceState(kDeviceStateSpeaking);
411:                     }
```

## application.cc | Application::Start | 原文件第412-418行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
412:                 });
413:             } else if (strcmp(state->valuestring, "stop") == 0) {
414:                 Schedule([this]() {
415:                     if (device_state_ == kDeviceStateSpeaking) {
416:                         background_task_->WaitForCompletion();
417:                         if (keep_listening_) {
418:                             protocol_->SendStartListening(kListeningModeAutoStop);
```

## application.cc | Application::Start | 原文件第419-426行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
419:                             SetDeviceState(kDeviceStateListening);
420:                         } else {
421:                             SetDeviceState(kDeviceStateIdle);
422:                         }
423:                     }
424:                 });
425:             } else if (strcmp(state->valuestring, "sentence_start") == 0) {
426:                 auto text = cJSON_GetObjectItem(root, "text");
```

## application.cc | Application::Start | 原文件第427-434行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
427:                 if (text != NULL) {
428:                     ESP_LOGI(TAG, "<< %s", text->valuestring);
429:                     Schedule([this, display, message = std::string(text->valuestring)]() {
430:                         display->SetChatMessage("assistant", message.c_str());
431:                     });
432:                 }
433:             }
434:         } else if (strcmp(type->valuestring, "stt") == 0) {
```

## application.cc | Application::Start | 原文件第435-441行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
435:             auto text = cJSON_GetObjectItem(root, "text");
436:             if (text != NULL) {
437:                 ESP_LOGI(TAG, ">> %s", text->valuestring);
438:                 Schedule([this, display, message = std::string(text->valuestring)]() {
439:                     display->SetChatMessage("user", message.c_str());
440:                 });
441:             }
```

## application.cc | Application::Start | 原文件第442-448行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
442:         } else if (strcmp(type->valuestring, "llm") == 0) {
443:             auto emotion = cJSON_GetObjectItem(root, "emotion");
444:             if (emotion != NULL) {
445:                 Schedule([this, display, emotion_str = std::string(emotion->valuestring)]() {
446:                     display->SetEmotion(emotion_str.c_str());
447:                 });
448:             }
```

## application.cc | Application::Start | 原文件第449-454行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
449:         } else if (strcmp(type->valuestring, "iot") == 0) {
450:             auto commands = cJSON_GetObjectItem(root, "commands");
451:             if (commands != NULL) {
452:                 auto& thing_manager = iot::ThingManager::GetInstance();
453:                 for (int i = 0; i < cJSON_GetArraySize(commands); ++i) {
454:                     auto command = cJSON_GetArrayItem(commands, i);
```

## application.cc | Application::Start | 原文件第455-465行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
455:                     thing_manager.Invoke(command);
456:                 }
457:             }
458:         }
459:     });
460:     protocol_->Start();
461: 
462:     // Check for new firmware version or get the MQTT broker address
463:     ota_.SetCheckVersionUrl(CONFIG_OTA_VERSION_URL);
464:     ota_.SetHeader("Device-Id", SystemInfo::GetMacAddress().c_str());
465:     ota_.SetHeader("Client-Id", board.GetUuid());
```

## application.cc | Application::Start | 原文件第466-475行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
466:     ota_.SetHeader("Accept-Language", Lang::CODE);
467:     auto app_desc = esp_app_get_description();
468:     ota_.SetHeader("User-Agent", std::string(BOARD_NAME "/") + app_desc->version);
469: 
470:     xTaskCreate([](void* arg) {
471:         Application* app = (Application*)arg;
472:         app->CheckNewVersion();
473:         vTaskDelete(NULL);
474:     }, "check_new_version", 4096 * 2, this, 2, nullptr);
475: 
```

## application.cc | Application::Start | 原文件第476-481行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
476: #if CONFIG_USE_AUDIO_PROCESSOR
477:     audio_processor_.Initialize(codec->input_channels(), codec->input_reference());
478:     audio_processor_.OnOutput([this](std::vector<int16_t>&& data) {
479:         background_task_->Schedule([this, data = std::move(data)]() mutable {
480:             opus_encoder_->Encode(std::move(data), [this](std::vector<uint8_t>&& opus) {
481:                 Schedule([this, opus = std::move(opus)]() {
```

## application.cc | Application::Start | 原文件第482-492行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
482:                     protocol_->SendAudio(opus);
483:                 });
484:             });
485:         });
486:     });
487: #endif
488: 
489: #if CONFIG_USE_WAKE_WORD_DETECT
490:     wake_word_detect_.Initialize(codec->input_channels(), codec->input_reference());
491:     wake_word_detect_.OnVadStateChange([this](bool speaking) {
492:         Schedule([this, speaking]() {
```

## application.cc | Application::Start | 原文件第493-504行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
493:             if (device_state_ == kDeviceStateListening) {
494:                 if (speaking) {
495:                     voice_detected_ = true;
496:                 } else {
497:                     voice_detected_ = false;
498:                 }
499:                 auto led = Board::GetInstance().GetLed();
500:                 led->OnStateChanged();
501:             }
502:         });
503:     });
504: 
```

## application.cc | Application::Start | 原文件第505-512行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
505:     wake_word_detect_.OnWakeWordDetected([this](const std::string& wake_word) {
506:         Schedule([this, &wake_word]() {
507:             if (device_state_ == kDeviceStateIdle) {
508:                 SetDeviceState(kDeviceStateConnecting);
509:                 wake_word_detect_.EncodeWakeWordData();
510: 
511:                 if (!protocol_->OpenAudioChannel()) {
512:                     wake_word_detect_.StartDetection();
```

## application.cc | Application::Start | 原文件第513-521行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
513:                     return;
514:                 }
515:                 
516:                 std::vector<uint8_t> opus;
517:                 // Encode and send the wake word data to the server
518:                 while (wake_word_detect_.GetWakeWordOpus(opus)) {
519:                     protocol_->SendAudio(opus);
520:                 }
521:                 // Set the chat state to wake word detected
```

## application.cc | Application::Start | 原文件第522-527行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
522:                 protocol_->SendWakeWordDetected(wake_word);
523:                 ESP_LOGI(TAG, "Wake word detected: %s", wake_word.c_str());
524:                 keep_listening_ = true;
525:                 SetDeviceState(kDeviceStateIdle);
526:             } else if (device_state_ == kDeviceStateSpeaking) {
527:                 AbortSpeaking(kAbortReasonWakeWordDetected);
```

## application.cc | Application::Start | 原文件第528-539行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
528:             } else if (device_state_ == kDeviceStateActivating) {
529:                 SetDeviceState(kDeviceStateIdle);
530:             }
531: 
532:             // Resume detection
533:             wake_word_detect_.StartDetection();
534:         });
535:     });
536:     wake_word_detect_.StartDetection();
537: #endif
538: 
539:     SetDeviceState(kDeviceStateIdle);
```

## application.cc | Application::Start | 原文件第540-542行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
540:     esp_timer_start_periodic(clock_timer_handle_, 1000000);
541: }
542: 
```

## application.cc | Application::OnClockTimer | 原文件第543-550行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
543: void Application::OnClockTimer() {
544:     clock_ticks_++;
545: 
546:     // Print the debug info every 10 seconds
547:     if (clock_ticks_ % 10 == 0) {
548:         // SystemInfo::PrintRealTimeStats(pdMS_TO_TICKS(1000));
549:         int free_sram = heap_caps_get_free_size(MALLOC_CAP_INTERNAL);
550:         int min_free_sram = heap_caps_get_minimum_free_size(MALLOC_CAP_INTERNAL);
```

## application.cc | Application::OnClockTimer | 原文件第551-557行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
551:         ESP_LOGI(TAG, "Free internal: %u minimal internal: %u", free_sram, min_free_sram);
552: 
553:         // If we have synchronized server time, set the status to clock "HH:MM" if the device is idle
554:         if (ota_.HasServerTime()) {
555:             if (device_state_ == kDeviceStateIdle) {
556:                 Schedule([this]() {
557:                     // Set status to clock "HH:MM"
```

## application.cc | Application::OnClockTimer | 原文件第558-567行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
558:                     time_t now = time(NULL);
559:                     char time_str[64];
560:                     strftime(time_str, sizeof(time_str), "%H:%M  ", localtime(&now));
561:                     Board::GetInstance().GetDisplay()->SetStatus(time_str);
562:                 });
563:             }
564:         }
565:     }
566: }
567: 
```

## application.cc | Application::Schedule | 原文件第568-577行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
568: void Application::Schedule(std::function<void()> callback) {
569:     {
570:         std::lock_guard<std::mutex> lock(mutex_);
571:         main_tasks_.push_back(std::move(callback));
572:     }
573:     xEventGroupSetBits(event_group_, SCHEDULE_EVENT);
574: }
575: 
576: // The Main Loop controls the chat state and websocket connection
577: // If other tasks need to access the websocket or chat state,
```

## application.cc | Application::Schedule | 原文件第578-578行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
578: // they should use Schedule to call this function
```

## application.cc | Application::MainLoop | 原文件第579-588行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
579: void Application::MainLoop() {
580:     while (true) {
581:         auto bits = xEventGroupWaitBits(event_group_,
582:             SCHEDULE_EVENT | AUDIO_INPUT_READY_EVENT | AUDIO_OUTPUT_READY_EVENT,
583:             pdTRUE, pdFALSE, portMAX_DELAY);
584: 
585:         if (bits & AUDIO_INPUT_READY_EVENT) {
586:             InputAudio();
587:         }
588:         if (bits & AUDIO_OUTPUT_READY_EVENT) {
```

## application.cc | Application::MainLoop | 原文件第589-601行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
589:             OutputAudio();
590:         }
591:         if (bits & SCHEDULE_EVENT) {
592:             std::unique_lock<std::mutex> lock(mutex_);
593:             std::list<std::function<void()>> tasks = std::move(main_tasks_);
594:             lock.unlock();
595:             for (auto& task : tasks) {
596:                 task();
597:             }
598:         }
599:     }
600: }
601: 
```

## application.cc | Application::ResetDecoder | 原文件第602-608行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
602: void Application::ResetDecoder() {
603:     std::lock_guard<std::mutex> lock(mutex_);
604:     opus_decoder_->ResetState();
605:     audio_decode_queue_.clear();
606:     last_output_time_ = std::chrono::steady_clock::now();
607: }
608: 
```

## application.cc | Application::OutputAudio | 原文件第609-617行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
609: void Application::OutputAudio() {
610:     auto now = std::chrono::steady_clock::now();
611:     auto codec = Board::GetInstance().GetAudioCodec();
612:     const int max_silence_seconds = 10;
613: 
614:     std::unique_lock<std::mutex> lock(mutex_);
615:     if (audio_decode_queue_.empty()) {
616:         // Disable the output if there is no audio data for a long time
617:         if (device_state_ == kDeviceStateIdle) {
```

## application.cc | Application::OutputAudio | 原文件第618-630行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
618:             auto duration = std::chrono::duration_cast<std::chrono::seconds>(now - last_output_time_).count();
619:             if (duration > max_silence_seconds) {
620:                 codec->EnableOutput(false);
621:             }
622:         }
623:         return;
624:     }
625: 
626:     if (device_state_ == kDeviceStateListening) {
627:         audio_decode_queue_.clear();
628:         return;
629:     }
630: 
```

## application.cc | Application::OutputAudio | 原文件第631-642行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
631:     last_output_time_ = now;
632:     auto opus = std::move(audio_decode_queue_.front());
633:     audio_decode_queue_.pop_front();
634:     lock.unlock();
635: 
636:     background_task_->Schedule([this, codec, opus = std::move(opus)]() mutable {
637:         if (aborted_) {
638:             return;
639:         }
640: 
641:         std::vector<int16_t> pcm;
642:         if (!opus_decoder_->Decode(std::move(opus), pcm)) {
```

## application.cc | Application::OutputAudio | 原文件第643-650行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
643:             return;
644:         }
645: 
646:         // Resample if the sample rate is different
647:         if (opus_decode_sample_rate_ != codec->output_sample_rate()) {
648:             int target_size = output_resampler_.GetOutputSamples(pcm.size());
649:             std::vector<int16_t> resampled(target_size);
650:             output_resampler_.Process(pcm.data(), pcm.size(), resampled.data());
```

## application.cc | Application::OutputAudio | 原文件第651-657行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
651:             pcm = std::move(resampled);
652:         }
653:         
654:         codec->OutputData(pcm);
655:     });
656: }
657: 
```

## application.cc | Application::InputAudio | 原文件第658-667行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
658: void Application::InputAudio() {
659:     auto codec = Board::GetInstance().GetAudioCodec();
660:     std::vector<int16_t> data;
661:     if (!codec->InputData(data)) {
662:         return;
663:     }
664: 
665:     if (codec->input_sample_rate() != 16000) {
666:         if (codec->input_channels() == 2) {
667:             auto mic_channel = std::vector<int16_t>(data.size() / 2);
```

## application.cc | Application::InputAudio | 原文件第668-673行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
668:             auto reference_channel = std::vector<int16_t>(data.size() / 2);
669:             for (size_t i = 0, j = 0; i < mic_channel.size(); ++i, j += 2) {
670:                 mic_channel[i] = data[j];
671:                 reference_channel[i] = data[j + 1];
672:             }
673:             auto resampled_mic = std::vector<int16_t>(input_resampler_.GetOutputSamples(mic_channel.size()));
```

## application.cc | Application::InputAudio | 原文件第674-676行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
674:             auto resampled_reference = std::vector<int16_t>(reference_resampler_.GetOutputSamples(reference_channel.size()));
675:             input_resampler_.Process(mic_channel.data(), mic_channel.size(), resampled_mic.data());
676:             reference_resampler_.Process(reference_channel.data(), reference_channel.size(), resampled_reference.data());
```

## application.cc | Application::InputAudio | 原文件第677-683行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
677:             data.resize(resampled_mic.size() + resampled_reference.size());
678:             for (size_t i = 0, j = 0; i < resampled_mic.size(); ++i, j += 2) {
679:                 data[j] = resampled_mic[i];
680:                 data[j + 1] = resampled_reference[i];
681:             }
682:         } else {
683:             auto resampled = std::vector<int16_t>(input_resampler_.GetOutputSamples(data.size()));
```

## application.cc | Application::InputAudio | 原文件第684-695行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
684:             input_resampler_.Process(data.data(), data.size(), resampled.data());
685:             data = std::move(resampled);
686:         }
687:     }
688: 
689: #if CONFIG_USE_WAKE_WORD_DETECT
690:     if (wake_word_detect_.IsDetectionRunning()) {
691:         wake_word_detect_.Feed(data);
692:     }
693: #endif
694: #if CONFIG_USE_AUDIO_PROCESSOR
695:     if (audio_processor_.IsRunning()) {
```

## application.cc | Application::InputAudio | 原文件第696-704行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
696:         audio_processor_.Input(data);
697:     }
698: #else
699:     if (device_state_ == kDeviceStateListening) {
700:         background_task_->Schedule([this, data = std::move(data)]() mutable {
701:             opus_encoder_->Encode(std::move(data), [this](std::vector<uint8_t>&& opus) {
702:                 Schedule([this, opus = std::move(opus)]() {
703:                     protocol_->SendAudio(opus);
704:                 });
```

## application.cc | Application::InputAudio | 原文件第705-710行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
705:             });
706:         });
707:     }
708: #endif
709: }
710: 
```

## application.cc | Application::AbortSpeaking | 原文件第711-716行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
711: void Application::AbortSpeaking(AbortReason reason) {
712:     ESP_LOGI(TAG, "Abort speaking");
713:     aborted_ = true;
714:     protocol_->SendAbortSpeaking(reason);
715: }
716: 
```

## application.cc | Application::SetDeviceState | 原文件第717-728行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
717: void Application::SetDeviceState(DeviceState state) {
718:     if (device_state_ == state) {
719:         return;
720:     }
721:     
722:     clock_ticks_ = 0;
723:     auto previous_state = device_state_;
724:     device_state_ = state;
725:     ESP_LOGI(TAG, "STATE: %s", STATE_STRINGS[device_state_]);
726:     // The state is changed, wait for all background tasks to finish
727:     background_task_->WaitForCompletion();
728: 
```

## application.cc | Application::SetDeviceState | 原文件第729-738行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
729:     auto& board = Board::GetInstance();
730:     auto codec = board.GetAudioCodec();
731:     auto display = board.GetDisplay();
732:     auto led = board.GetLed();
733:     led->OnStateChanged();
734:     switch (state) {
735:         case kDeviceStateUnknown:
736:         case kDeviceStateIdle:
737:             display->SetStatus(Lang::Strings::STANDBY);
738:             display->SetEmotion("neutral");
```

## application.cc | Application::SetDeviceState | 原文件第739-748行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
739: #if CONFIG_USE_AUDIO_PROCESSOR
740:             audio_processor_.Stop();
741: #endif
742:             break;
743:         case kDeviceStateConnecting:
744:             display->SetStatus(Lang::Strings::CONNECTING);
745:             display->SetEmotion("neutral");
746:             display->SetChatMessage("system", "");
747:             break;
748:         case kDeviceStateListening:
```

## application.cc | Application::SetDeviceState | 原文件第749-757行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
749:             display->SetStatus(Lang::Strings::LISTENING);
750:             display->SetEmotion("neutral");
751:             ResetDecoder();
752:             opus_encoder_->ResetState();
753: #if CONFIG_USE_AUDIO_PROCESSOR
754:             audio_processor_.Start();
755: #endif
756:             UpdateIotStates();
757:             if (previous_state == kDeviceStateSpeaking) {
```

## application.cc | Application::SetDeviceState | 原文件第758-768行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
758:                 // FIXME: Wait for the speaker to empty the buffer
759:                 vTaskDelay(pdMS_TO_TICKS(120));
760:             }
761:             break;
762:         case kDeviceStateSpeaking:
763:             display->SetStatus(Lang::Strings::SPEAKING);
764:             ResetDecoder();
765:             codec->EnableOutput(true);
766: #if CONFIG_USE_AUDIO_PROCESSOR
767:             audio_processor_.Stop();
768: #endif
```

## application.cc | Application::SetDeviceState | 原文件第769-775行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
769:             break;
770:         default:
771:             // Do nothing
772:             break;
773:     }
774: }
775: 
```

## application.cc | Application::SetDecodeSampleRate | 原文件第776-785行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
776: void Application::SetDecodeSampleRate(int sample_rate) {
777:     if (opus_decode_sample_rate_ == sample_rate) {
778:         return;
779:     }
780: 
781:     opus_decode_sample_rate_ = sample_rate;
782:     opus_decoder_.reset();
783:     opus_decoder_ = std::make_unique<OpusDecoderWrapper>(opus_decode_sample_rate_, 1);
784: 
785:     auto codec = Board::GetInstance().GetAudioCodec();
```

## application.cc | Application::SetDecodeSampleRate | 原文件第786-791行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
786:     if (opus_decode_sample_rate_ != codec->output_sample_rate()) {
787:         ESP_LOGI(TAG, "Resampling audio from %d to %d", opus_decode_sample_rate_, codec->output_sample_rate());
788:         output_resampler_.Configure(opus_decode_sample_rate_, codec->output_sample_rate());
789:     }
790: }
791: 
```

## application.cc | Application::UpdateIotStates | 原文件第792-799行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
792: void Application::UpdateIotStates() {
793:     auto& thing_manager = iot::ThingManager::GetInstance();
794:     std::string states;
795:     if (thing_manager.GetStatesJson(states, true)) {
796:         protocol_->SendIotStates(states);
797:     }
798: }
799: 
```

## application.cc | Application::Reboot | 原文件第800-804行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
800: void Application::Reboot() {
801:     ESP_LOGI(TAG, "Rebooting...");
802:     esp_restart();
803: }
804: 
```

## application.cc | Application::WakeWordInvoke | 原文件第805-814行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
805: void Application::WakeWordInvoke(const std::string& wake_word) {
806:     if (device_state_ == kDeviceStateIdle) {
807:         ToggleChatState();
808:         Schedule([this, wake_word]() {
809:             if (protocol_) {
810:                 protocol_->SendWakeWordDetected(wake_word); 
811:             }
812:         }); 
813:     } else if (device_state_ == kDeviceStateSpeaking) {
814:         Schedule([this]() {
```

## application.cc | Application::WakeWordInvoke | 原文件第815-825行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
815:             AbortSpeaking(kAbortReasonNone);
816:         });
817:     } else if (device_state_ == kDeviceStateListening) {   
818:         Schedule([this]() {
819:             if (protocol_) {
820:                 protocol_->CloseAudioChannel();
821:             }
822:         });
823:     }
824: }
825: 
```

## application.cc | Application::CanEnterSleepMode | 原文件第826-837行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.cc
以下为原始源码，不是截图OCR。
```
826: bool Application::CanEnterSleepMode() {
827:     if (device_state_ != kDeviceStateIdle) {
828:         return false;
829:     }
830: 
831:     if (protocol_ && protocol_->IsAudioChannelOpened()) {
832:         return false;
833:     }
834: 
835:     // Now it is safe to enter sleep mode
836:     return true;
837: }
```

## application.h | 文件开头/全局定义 | 原文件第1-20行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.h
以下为原始源码，不是截图OCR。
```
1: #ifndef _APPLICATION_H_
2: #define _APPLICATION_H_
3: 
4: #include <freertos/FreeRTOS.h>
5: #include <freertos/event_groups.h>
6: #include <freertos/task.h>
7: #include <esp_timer.h>
8: 
9: #include <string>
10: #include <mutex>
11: #include <list>
12: 
13: #include <opus_encoder.h>
14: #include <opus_decoder.h>
15: #include <opus_resampler.h>
16: 
17: #include "protocol.h"
18: #include "ota.h"
19: #include "background_task.h"
20: 
```

## application.h | 文件开头/全局定义 | 原文件第21-35行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.h
以下为原始源码，不是截图OCR。
```
21: #if CONFIG_USE_WAKE_WORD_DETECT
22: #include "wake_word_detect.h"
23: #endif
24: #if CONFIG_USE_AUDIO_PROCESSOR
25: #include "audio_processor.h"
26: #endif
27: 
28: #define SCHEDULE_EVENT (1 << 0)
29: #define AUDIO_INPUT_READY_EVENT (1 << 1)
30: #define AUDIO_OUTPUT_READY_EVENT (1 << 2)
31: 
32: enum DeviceState {
33:     kDeviceStateUnknown,
34:     kDeviceStateStarting,
35:     kDeviceStateWifiConfiguring,
```

## application.h | 文件开头/全局定义 | 原文件第36-52行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.h
以下为原始源码，不是截图OCR。
```
36:     kDeviceStateIdle,
37:     kDeviceStateConnecting,
38:     kDeviceStateListening,
39:     kDeviceStateSpeaking,
40:     kDeviceStateUpgrading,
41:     kDeviceStateActivating,
42:     kDeviceStateFatalError
43: };
44: 
45: #define OPUS_FRAME_DURATION_MS 60
46: 
47: class Application {
48: public:
49:     static Application& GetInstance() {
50:         static Application instance;
51:         return instance;
52:     }
```

## application.h | 文件开头/全局定义 | 原文件第53-61行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.h
以下为原始源码，不是截图OCR。
```
53:     // 删除拷贝构造函数和赋值运算符
54:     Application(const Application&) = delete;
55:     Application& operator=(const Application&) = delete;
56: 
57:     void Start();
58:     DeviceState GetDeviceState() const { return device_state_; }
59:     bool IsVoiceDetected() const { return voice_detected_; }
60:     void Schedule(std::function<void()> callback);
61:     void SetDeviceState(DeviceState state);
```

## application.h | 文件开头/全局定义 | 原文件第62-70行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.h
以下为原始源码，不是截图OCR。
```
62:     void Alert(const char* status, const char* message, const char* emotion = "", const std::string_view& sound = "");
63:     void DismissAlert();
64:     void AbortSpeaking(AbortReason reason);
65:     void ToggleChatState();
66:     void StartListening();
67:     void StopListening();
68:     void UpdateIotStates();
69:     void Reboot();
70:     void WakeWordInvoke(const std::string& wake_word);
```

## application.h | 文件开头/全局定义 | 原文件第71-86行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.h
以下为原始源码，不是截图OCR。
```
71:     void PlaySound(const std::string_view& sound);
72:     bool CanEnterSleepMode();
73: 
74: private:
75:     Application();
76:     ~Application();
77: 
78: #if CONFIG_USE_WAKE_WORD_DETECT
79:     WakeWordDetect wake_word_detect_;
80: #endif
81: #if CONFIG_USE_AUDIO_PROCESSOR
82:     AudioProcessor audio_processor_;
83: #endif
84:     Ota ota_;
85:     std::mutex mutex_;
86:     std::list<std::function<void()>> main_tasks_;
```

## application.h | 文件开头/全局定义 | 原文件第87-96行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.h
以下为原始源码，不是截图OCR。
```
87:     std::unique_ptr<Protocol> protocol_;
88:     EventGroupHandle_t event_group_ = nullptr;
89:     esp_timer_handle_t clock_timer_handle_ = nullptr;
90:     volatile DeviceState device_state_ = kDeviceStateUnknown;
91:     bool keep_listening_ = false;
92:     bool aborted_ = false;
93:     bool voice_detected_ = false;
94:     int clock_ticks_ = 0;
95: 
96:     // Audio encode / decode
```

## application.h | 文件开头/全局定义 | 原文件第97-106行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.h
以下为原始源码，不是截图OCR。
```
97:     BackgroundTask* background_task_ = nullptr;
98:     std::chrono::steady_clock::time_point last_output_time_;
99:     std::list<std::vector<uint8_t>> audio_decode_queue_;
100: 
101:     std::unique_ptr<OpusEncoderWrapper> opus_encoder_;
102:     std::unique_ptr<OpusDecoderWrapper> opus_decoder_;
103: 
104:     int opus_decode_sample_rate_ = -1;
105:     OpusResampler input_resampler_;
106:     OpusResampler reference_resampler_;
```

## application.h | 文件开头/全局定义 | 原文件第107-119行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/application.h
以下为原始源码，不是截图OCR。
```
107:     OpusResampler output_resampler_;
108: 
109:     void MainLoop();
110:     void InputAudio();
111:     void OutputAudio();
112:     void ResetDecoder();
113:     void SetDecodeSampleRate(int sample_rate);
114:     void CheckNewVersion();
115:     void ShowActivationCode();
116:     void OnClockTimer();
117: };
118: 
119: #endif // _APPLICATION_H_
```

## lang_config.h | 文件开头/全局定义 | 原文件第1-17行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
1: // Auto-generated language config
2: #pragma once
3: 
4: #include <string_view>
5: 
6: #ifndef zh_cn
7:     #define zh_cn  // 預設語言
8: #endif
9: 
10: namespace Lang {
11:     // 语言元数据
12:     constexpr const char* CODE = "zh-CN";
13: 
14:     // 字符串资源
15:     namespace Strings {
16:         constexpr const char* ACCESS_VIA_BROWSER = "，浏览器访问 ";
17:         constexpr const char* ACTIVATION = "激活设备";
```

## lang_config.h | 文件开头/全局定义 | 原文件第18-24行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
18:         constexpr const char* BATTERY_CHARGING = "正在充电";
19:         constexpr const char* BATTERY_FULL = "电量已满";
20:         constexpr const char* BATTERY_LOW = "电量不足";
21:         constexpr const char* BATTERY_NEED_CHARGE = "电量低，请充电";
22:         constexpr const char* CONNECTED_TO = "已连接 ";
23:         constexpr const char* CONNECTING = "连接中...";
24:         constexpr const char* CONNECT_TO = "连接 ";
```

## lang_config.h | 文件开头/全局定义 | 原文件第25-31行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
25:         constexpr const char* CONNECT_TO_HOTSPOT = "手机连接热点 ";
26:         constexpr const char* DETECTING_MODULE = "检测模组...";
27:         constexpr const char* ENTERING_WIFI_CONFIG_MODE = "进入配网模式...";
28:         constexpr const char* ERROR = "错误";
29:         constexpr const char* INFO = "信息";
30:         constexpr const char* INITIALIZING = "正在初始化...";
31:         constexpr const char* LISTENING = "聆听中...";
```

## lang_config.h | 文件开头/全局定义 | 原文件第32-38行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
32:         constexpr const char* LOADING_PROTOCOL = "加载协议...";
33:         constexpr const char* MAX_VOLUME = "最大音量";
34:         constexpr const char* MUTED = "已静音";
35:         constexpr const char* NEW_VERSION = "新版本 ";
36:         constexpr const char* OTA_UPGRADE = "OTA 升级";
37:         constexpr const char* PIN_ERROR = "请插入 SIM 卡";
38:         constexpr const char* REGISTERING_NETWORK = "等待网络...";
```

## lang_config.h | 文件开头/全局定义 | 原文件第39-44行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
39:         constexpr const char* REG_ERROR = "无法接入网络，请检查流量卡状态";
40:         constexpr const char* SCANNING_WIFI = "扫描 Wi-Fi...";
41:         constexpr const char* SERVER_ERROR = "发送失败，请检查网络";
42:         constexpr const char* SERVER_NOT_CONNECTED = "无法连接服务，请稍后再试";
43:         constexpr const char* SERVER_NOT_FOUND = "正在寻找可用服务";
44:         constexpr const char* SERVER_TIMEOUT = "等待响应超时";
```

## lang_config.h | 文件开头/全局定义 | 原文件第45-52行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
45:         constexpr const char* SPEAKING = "说话中...";
46:         constexpr const char* STANDBY = "待命";
47:         constexpr const char* UPGRADE_FAILED = "升级失败";
48:         constexpr const char* UPGRADING = "正在升级系统...";
49:         constexpr const char* VERSION = "版本 ";
50:         constexpr const char* VOLUME = "音量 ";
51:         constexpr const char* WARNING = "警告";
52:         constexpr const char* WIFI_CONFIG_MODE = "配网模式";
```

## lang_config.h | 文件开头/全局定义 | 原文件第53-64行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
53:     }
54: 
55:     // 音效资源
56:     namespace Sounds {
57: 
58:         extern const char p3_0_start[] asm("_binary_0_p3_start");
59:         extern const char p3_0_end[] asm("_binary_0_p3_end");
60:         static const std::string_view P3_0 {
61:         static_cast<const char*>(p3_0_start),
62:         static_cast<size_t>(p3_0_end - p3_0_start)
63:         };
64: 
```

## lang_config.h | 文件开头/全局定义 | 原文件第65-72行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
65:         extern const char p3_1_start[] asm("_binary_1_p3_start");
66:         extern const char p3_1_end[] asm("_binary_1_p3_end");
67:         static const std::string_view P3_1 {
68:         static_cast<const char*>(p3_1_start),
69:         static_cast<size_t>(p3_1_end - p3_1_start)
70:         };
71: 
72:         extern const char p3_2_start[] asm("_binary_2_p3_start");
```

## lang_config.h | 文件开头/全局定义 | 原文件第73-81行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
73:         extern const char p3_2_end[] asm("_binary_2_p3_end");
74:         static const std::string_view P3_2 {
75:         static_cast<const char*>(p3_2_start),
76:         static_cast<size_t>(p3_2_end - p3_2_start)
77:         };
78: 
79:         extern const char p3_3_start[] asm("_binary_3_p3_start");
80:         extern const char p3_3_end[] asm("_binary_3_p3_end");
81:         static const std::string_view P3_3 {
```

## lang_config.h | 文件开头/全局定义 | 原文件第82-92行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
82:         static_cast<const char*>(p3_3_start),
83:         static_cast<size_t>(p3_3_end - p3_3_start)
84:         };
85: 
86:         extern const char p3_4_start[] asm("_binary_4_p3_start");
87:         extern const char p3_4_end[] asm("_binary_4_p3_end");
88:         static const std::string_view P3_4 {
89:         static_cast<const char*>(p3_4_start),
90:         static_cast<size_t>(p3_4_end - p3_4_start)
91:         };
92: 
```

## lang_config.h | 文件开头/全局定义 | 原文件第93-100行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
93:         extern const char p3_5_start[] asm("_binary_5_p3_start");
94:         extern const char p3_5_end[] asm("_binary_5_p3_end");
95:         static const std::string_view P3_5 {
96:         static_cast<const char*>(p3_5_start),
97:         static_cast<size_t>(p3_5_end - p3_5_start)
98:         };
99: 
100:         extern const char p3_6_start[] asm("_binary_6_p3_start");
```

## lang_config.h | 文件开头/全局定义 | 原文件第101-109行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
101:         extern const char p3_6_end[] asm("_binary_6_p3_end");
102:         static const std::string_view P3_6 {
103:         static_cast<const char*>(p3_6_start),
104:         static_cast<size_t>(p3_6_end - p3_6_start)
105:         };
106: 
107:         extern const char p3_7_start[] asm("_binary_7_p3_start");
108:         extern const char p3_7_end[] asm("_binary_7_p3_end");
109:         static const std::string_view P3_7 {
```

## lang_config.h | 文件开头/全局定义 | 原文件第110-119行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
110:         static_cast<const char*>(p3_7_start),
111:         static_cast<size_t>(p3_7_end - p3_7_start)
112:         };
113: 
114:         extern const char p3_8_start[] asm("_binary_8_p3_start");
115:         extern const char p3_8_end[] asm("_binary_8_p3_end");
116:         static const std::string_view P3_8 {
117:         static_cast<const char*>(p3_8_start),
118:         static_cast<size_t>(p3_8_end - p3_8_start)
119:         };
```

## lang_config.h | 文件开头/全局定义 | 原文件第120-128行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
120: 
121:         extern const char p3_9_start[] asm("_binary_9_p3_start");
122:         extern const char p3_9_end[] asm("_binary_9_p3_end");
123:         static const std::string_view P3_9 {
124:         static_cast<const char*>(p3_9_start),
125:         static_cast<size_t>(p3_9_end - p3_9_start)
126:         };
127: 
128:         extern const char p3_activation_start[] asm("_binary_activation_p3_start");
```

## lang_config.h | 文件开头/全局定义 | 原文件第129-135行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
129:         extern const char p3_activation_end[] asm("_binary_activation_p3_end");
130:         static const std::string_view P3_ACTIVATION {
131:         static_cast<const char*>(p3_activation_start),
132:         static_cast<size_t>(p3_activation_end - p3_activation_start)
133:         };
134: 
135:         extern const char p3_err_pin_start[] asm("_binary_err_pin_p3_start");
```

## lang_config.h | 文件开头/全局定义 | 原文件第136-142行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
136:         extern const char p3_err_pin_end[] asm("_binary_err_pin_p3_end");
137:         static const std::string_view P3_ERR_PIN {
138:         static_cast<const char*>(p3_err_pin_start),
139:         static_cast<size_t>(p3_err_pin_end - p3_err_pin_start)
140:         };
141: 
142:         extern const char p3_err_reg_start[] asm("_binary_err_reg_p3_start");
```

## lang_config.h | 文件开头/全局定义 | 原文件第143-149行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
143:         extern const char p3_err_reg_end[] asm("_binary_err_reg_p3_end");
144:         static const std::string_view P3_ERR_REG {
145:         static_cast<const char*>(p3_err_reg_start),
146:         static_cast<size_t>(p3_err_reg_end - p3_err_reg_start)
147:         };
148: 
149:         extern const char p3_exclamation_start[] asm("_binary_exclamation_p3_start");
```

## lang_config.h | 文件开头/全局定义 | 原文件第150-156行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
150:         extern const char p3_exclamation_end[] asm("_binary_exclamation_p3_end");
151:         static const std::string_view P3_EXCLAMATION {
152:         static_cast<const char*>(p3_exclamation_start),
153:         static_cast<size_t>(p3_exclamation_end - p3_exclamation_start)
154:         };
155: 
156:         extern const char p3_low_battery_start[] asm("_binary_low_battery_p3_start");
```

## lang_config.h | 文件开头/全局定义 | 原文件第157-163行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
157:         extern const char p3_low_battery_end[] asm("_binary_low_battery_p3_end");
158:         static const std::string_view P3_LOW_BATTERY {
159:         static_cast<const char*>(p3_low_battery_start),
160:         static_cast<size_t>(p3_low_battery_end - p3_low_battery_start)
161:         };
162: 
163:         extern const char p3_success_start[] asm("_binary_success_p3_start");
```

## lang_config.h | 文件开头/全局定义 | 原文件第164-170行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
164:         extern const char p3_success_end[] asm("_binary_success_p3_end");
165:         static const std::string_view P3_SUCCESS {
166:         static_cast<const char*>(p3_success_start),
167:         static_cast<size_t>(p3_success_end - p3_success_start)
168:         };
169: 
170:         extern const char p3_upgrade_start[] asm("_binary_upgrade_p3_start");
```

## lang_config.h | 文件开头/全局定义 | 原文件第171-177行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
171:         extern const char p3_upgrade_end[] asm("_binary_upgrade_p3_end");
172:         static const std::string_view P3_UPGRADE {
173:         static_cast<const char*>(p3_upgrade_start),
174:         static_cast<size_t>(p3_upgrade_end - p3_upgrade_start)
175:         };
176: 
177:         extern const char p3_vibration_start[] asm("_binary_vibration_p3_start");
```

## lang_config.h | 文件开头/全局定义 | 原文件第178-184行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
178:         extern const char p3_vibration_end[] asm("_binary_vibration_p3_end");
179:         static const std::string_view P3_VIBRATION {
180:         static_cast<const char*>(p3_vibration_start),
181:         static_cast<size_t>(p3_vibration_end - p3_vibration_start)
182:         };
183: 
184:         extern const char p3_welcome_start[] asm("_binary_welcome_p3_start");
```

## lang_config.h | 文件开头/全局定义 | 原文件第185-191行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
185:         extern const char p3_welcome_end[] asm("_binary_welcome_p3_end");
186:         static const std::string_view P3_WELCOME {
187:         static_cast<const char*>(p3_welcome_start),
188:         static_cast<size_t>(p3_welcome_end - p3_welcome_start)
189:         };
190: 
191:         extern const char p3_wificonfig_start[] asm("_binary_wificonfig_p3_start");
```

## lang_config.h | 文件开头/全局定义 | 原文件第192-198行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/assets/lang_config.h
以下为原始源码，不是截图OCR。
```
192:         extern const char p3_wificonfig_end[] asm("_binary_wificonfig_p3_end");
193:         static const std::string_view P3_WIFICONFIG {
194:         static_cast<const char*>(p3_wificonfig_start),
195:         static_cast<size_t>(p3_wificonfig_end - p3_wificonfig_start)
196:         };
197:     }
198: }
```

## audio_codec.cc | 文件开头/全局定义 | 原文件第1-16行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/audio_codec.cc
以下为原始源码，不是截图OCR。
```
1: #include "audio_codec.h"
2: #include "board.h"
3: #include "settings.h"
4: 
5: #include <esp_log.h>
6: #include <cstring>
7: #include <driver/i2s_common.h>
8: 
9: #define TAG "AudioCodec"
10: 
11: AudioCodec::AudioCodec() {
12: }
13: 
14: AudioCodec::~AudioCodec() {
15: }
16: 
```

## audio_codec.cc | AudioCodec::OnInputReady | 原文件第17-20行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/audio_codec.cc
以下为原始源码，不是截图OCR。
```
17: void AudioCodec::OnInputReady(std::function<bool()> callback) {
18:     on_input_ready_ = callback;
19: }
20: 
```

## audio_codec.cc | AudioCodec::OnOutputReady | 原文件第21-24行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/audio_codec.cc
以下为原始源码，不是截图OCR。
```
21: void AudioCodec::OnOutputReady(std::function<bool()> callback) {
22:     on_output_ready_ = callback;
23: }
24: 
```

## audio_codec.cc | AudioCodec::OutputData | 原文件第25-28行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/audio_codec.cc
以下为原始源码，不是截图OCR。
```
25: void AudioCodec::OutputData(std::vector<int16_t>& data) {
26:     Write(data.data(), data.size());
27: }
28: 
```

## audio_codec.cc | AudioCodec::InputData | 原文件第29-40行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/audio_codec.cc
以下为原始源码，不是截图OCR。
```
29: bool AudioCodec::InputData(std::vector<int16_t>& data) {
30:     int duration = 30;
31:     int input_frame_size = input_sample_rate_ / 1000 * duration * input_channels_;
32: 
33:     data.resize(input_frame_size);
34:     int samples = Read(data.data(), data.size());
35:     if (samples > 0) {
36:         return true;
37:     }
38:     return false;
39: }
40: 
```

## audio_codec.cc | AudioCodec::on_sent | 原文件第41-48行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/audio_codec.cc
以下为原始源码，不是截图OCR。
```
41: IRAM_ATTR bool AudioCodec::on_sent(i2s_chan_handle_t handle, i2s_event_data_t *event, void *user_ctx) {
42:     auto audio_codec = (AudioCodec*)user_ctx;
43:     if (audio_codec->output_enabled_ && audio_codec->on_output_ready_) {
44:         return audio_codec->on_output_ready_();
45:     }
46:     return false;
47: }
48: 
```

## audio_codec.cc | AudioCodec::on_recv | 原文件第49-56行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/audio_codec.cc
以下为原始源码，不是截图OCR。
```
49: IRAM_ATTR bool AudioCodec::on_recv(i2s_chan_handle_t handle, i2s_event_data_t *event, void *user_ctx) {
50:     auto audio_codec = (AudioCodec*)user_ctx;
51:     if (audio_codec->input_enabled_ && audio_codec->on_input_ready_) {
52:         return audio_codec->on_input_ready_();
53:     }
54:     return false;
55: }
56: 
```

## audio_codec.cc | AudioCodec::Start | 原文件第57-67行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/audio_codec.cc
以下为原始源码，不是截图OCR。
```
57: void AudioCodec::Start() {
58:     Settings settings("audio", false);
59:     output_volume_ = settings.GetInt("output_volume", output_volume_);
60: 
61:     // 注册音频数据回调
62:     i2s_event_callbacks_t rx_callbacks = {};
63:     rx_callbacks.on_recv = on_recv;
64:     i2s_channel_register_event_callback(rx_handle_, &rx_callbacks, this);
65: 
66:     i2s_event_callbacks_t tx_callbacks = {};
67:     tx_callbacks.on_sent = on_sent;
```

## audio_codec.cc | AudioCodec::Start | 原文件第68-76行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/audio_codec.cc
以下为原始源码，不是截图OCR。
```
68:     i2s_channel_register_event_callback(tx_handle_, &tx_callbacks, this);
69: 
70:     ESP_ERROR_CHECK(i2s_channel_enable(tx_handle_));
71:     ESP_ERROR_CHECK(i2s_channel_enable(rx_handle_));
72: 
73:     EnableInput(true);
74:     EnableOutput(true);
75: }
76: 
```

## audio_codec.cc | AudioCodec::SetOutputVolume | 原文件第77-84行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/audio_codec.cc
以下为原始源码，不是截图OCR。
```
77: void AudioCodec::SetOutputVolume(int volume) {
78:     output_volume_ = volume;
79:     ESP_LOGI(TAG, "Set output volume to %d", output_volume_);
80:     
81:     Settings settings("audio", true);
82:     settings.SetInt("output_volume", output_volume_);
83: }
84: 
```

## audio_codec.cc | AudioCodec::EnableInput | 原文件第85-92行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/audio_codec.cc
以下为原始源码，不是截图OCR。
```
85: void AudioCodec::EnableInput(bool enable) {
86:     if (enable == input_enabled_) {
87:         return;
88:     }
89:     input_enabled_ = enable;
90:     ESP_LOGI(TAG, "Set input enable to %s", enable ? "true" : "false");
91: }
92: 
```

## audio_codec.cc | AudioCodec::EnableOutput | 原文件第93-99行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/audio_codec.cc
以下为原始源码，不是截图OCR。
```
93: void AudioCodec::EnableOutput(bool enable) {
94:     if (enable == output_enabled_) {
95:         return;
96:     }
97:     output_enabled_ = enable;
98:     ESP_LOGI(TAG, "Set output enable to %s", enable ? "true" : "false");
99: }
```

## audio_codec.h | 文件开头/全局定义 | 原文件第1-19行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/audio_codec.h
以下为原始源码，不是截图OCR。
```
1: #ifndef _AUDIO_CODEC_H
2: #define _AUDIO_CODEC_H
3: 
4: #include <freertos/FreeRTOS.h>
5: #include <freertos/event_groups.h>
6: #include <driver/i2s_std.h>
7: 
8: #include <vector>
9: #include <string>
10: #include <functional>
11: 
12: #include "board.h"
13: 
14: class AudioCodec {
15: public:
16:     AudioCodec();
17:     virtual ~AudioCodec();
18:     
19:     virtual void SetOutputVolume(int volume);
```

## audio_codec.h | 文件开头/全局定义 | 原文件第20-29行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/audio_codec.h
以下为原始源码，不是截图OCR。
```
20:     virtual void EnableInput(bool enable);
21:     virtual void EnableOutput(bool enable);
22: 
23:     void Start();
24:     void OutputData(std::vector<int16_t>& data);
25:     bool InputData(std::vector<int16_t>& data);
26:     void OnOutputReady(std::function<bool()> callback);
27:     void OnInputReady(std::function<bool()> callback);
28: 
29:     inline bool duplex() const { return duplex_; }
```

## audio_codec.h | 文件开头/全局定义 | 原文件第30-35行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/audio_codec.h
以下为原始源码，不是截图OCR。
```
30:     inline bool input_reference() const { return input_reference_; }
31:     inline int input_sample_rate() const { return input_sample_rate_; }
32:     inline int output_sample_rate() const { return output_sample_rate_; }
33:     inline int input_channels() const { return input_channels_; }
34:     inline int output_channels() const { return output_channels_; }
35:     inline int output_volume() const { return output_volume_; }
```

## audio_codec.h | 文件开头/全局定义 | 原文件第36-45行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/audio_codec.h
以下为原始源码，不是截图OCR。
```
36: 
37: private:
38:     std::function<bool()> on_input_ready_;
39:     std::function<bool()> on_output_ready_;
40:     
41:     IRAM_ATTR static bool on_recv(i2s_chan_handle_t handle, i2s_event_data_t *event, void *user_ctx);
42:     IRAM_ATTR static bool on_sent(i2s_chan_handle_t handle, i2s_event_data_t *event, void *user_ctx);
43: 
44: protected:
45:     i2s_chan_handle_t tx_handle_ = nullptr;
```

## audio_codec.h | 文件开头/全局定义 | 原文件第46-58行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/audio_codec.h
以下为原始源码，不是截图OCR。
```
46:     i2s_chan_handle_t rx_handle_ = nullptr;
47: 
48:     bool duplex_ = false;
49:     bool input_reference_ = false;
50:     bool input_enabled_ = false;
51:     bool output_enabled_ = false;
52:     int input_sample_rate_ = 0;
53:     int output_sample_rate_ = 0;
54:     int input_channels_ = 1;
55:     int output_channels_ = 1;
56:     int output_volume_ = 70;
57: 
58:     virtual int Read(int16_t* dest, int samples) = 0;
```

## audio_codec.h | 文件开头/全局定义 | 原文件第59-62行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/audio_codec.h
以下为原始源码，不是截图OCR。
```
59:     virtual int Write(const int16_t* data, int samples) = 0;
60: };
61: 
62: #endif // _AUDIO_CODEC_H
```

## box_audio_codec.cc | 文件开头/全局定义 | 原文件第1-10行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
1: #include "box_audio_codec.h"
2: 
3: #include <esp_log.h>
4: #include <driver/i2c.h>
5: #include <driver/i2s_tdm.h>
6: 
7: static const char TAG[] = "BoxAudioCodec";
8: 
9: BoxAudioCodec::BoxAudioCodec(void* i2c_master_handle, int input_sample_rate, int output_sample_rate,
10:     gpio_num_t mclk, gpio_num_t bclk, gpio_num_t ws, gpio_num_t dout, gpio_num_t din,
```

## box_audio_codec.cc | 文件开头/全局定义 | 原文件第11-19行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
11:     gpio_num_t pa_pin, uint8_t es8311_addr, uint8_t es7210_addr, bool input_reference) {
12:     duplex_ = true; // 是否双工
13:     input_reference_ = input_reference; // 是否使用参考输入，实现回声消除
14:     input_channels_ = input_reference_ ? 2 : 1; // 输入通道数
15:     input_sample_rate_ = input_sample_rate;
16:     output_sample_rate_ = output_sample_rate;
17: 
18:     CreateDuplexChannels(mclk, bclk, ws, dout, din);
19: 
```

## box_audio_codec.cc | 文件开头/全局定义 | 原文件第20-31行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
20:     // Do initialize of related interface: data_if, ctrl_if and gpio_if
21:     audio_codec_i2s_cfg_t i2s_cfg = {
22:         .port = I2S_NUM_0,
23:         .rx_handle = rx_handle_,
24:         .tx_handle = tx_handle_,
25:     };
26:     data_if_ = audio_codec_new_i2s_data(&i2s_cfg);
27:     assert(data_if_ != NULL);
28: 
29:     // Output
30:     audio_codec_i2c_cfg_t i2c_cfg = {
31:         .port = (i2c_port_t)1,
```

## box_audio_codec.cc | 文件开头/全局定义 | 原文件第32-43行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
32:         .addr = es8311_addr,
33:         .bus_handle = i2c_master_handle,
34:     };
35:     out_ctrl_if_ = audio_codec_new_i2c_ctrl(&i2c_cfg);
36:     assert(out_ctrl_if_ != NULL);
37: 
38:     gpio_if_ = audio_codec_new_gpio();
39:     assert(gpio_if_ != NULL);
40: 
41:     es8311_codec_cfg_t es8311_cfg = {};
42:     es8311_cfg.ctrl_if = out_ctrl_if_;
43:     es8311_cfg.gpio_if = gpio_if_;
```

## box_audio_codec.cc | 文件开头/全局定义 | 原文件第44-53行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
44:     es8311_cfg.codec_mode = ESP_CODEC_DEV_WORK_MODE_DAC;
45:     es8311_cfg.pa_pin = pa_pin;
46:     es8311_cfg.use_mclk = true;
47:     es8311_cfg.hw_gain.pa_voltage = 5.0;
48:     es8311_cfg.hw_gain.codec_dac_voltage = 3.3;
49:     out_codec_if_ = es8311_codec_new(&es8311_cfg);
50:     assert(out_codec_if_ != NULL);
51: 
52:     esp_codec_dev_cfg_t dev_cfg = {
53:         .dev_type = ESP_CODEC_DEV_TYPE_OUT,
```

## box_audio_codec.cc | 文件开头/全局定义 | 原文件第54-66行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
54:         .codec_if = out_codec_if_,
55:         .data_if = data_if_,
56:     };
57:     output_dev_ = esp_codec_dev_new(&dev_cfg);
58:     assert(output_dev_ != NULL);
59: 
60:     // Input
61:     i2c_cfg.addr = es7210_addr;
62:     in_ctrl_if_ = audio_codec_new_i2c_ctrl(&i2c_cfg);
63:     assert(in_ctrl_if_ != NULL);
64: 
65:     es7210_codec_cfg_t es7210_cfg = {};
66:     es7210_cfg.ctrl_if = in_ctrl_if_;
```

## box_audio_codec.cc | 文件开头/全局定义 | 原文件第67-76行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
67:     es7210_cfg.mic_selected = ES7120_SEL_MIC1 | ES7120_SEL_MIC2 | ES7120_SEL_MIC3 | ES7120_SEL_MIC4;
68:     in_codec_if_ = es7210_codec_new(&es7210_cfg);
69:     assert(in_codec_if_ != NULL);
70: 
71:     dev_cfg.dev_type = ESP_CODEC_DEV_TYPE_IN;
72:     dev_cfg.codec_if = in_codec_if_;
73:     input_dev_ = esp_codec_dev_new(&dev_cfg);
74:     assert(input_dev_ != NULL);
75: 
76:     ESP_LOGI(TAG, "BoxAudioDevice initialized");
```

## box_audio_codec.cc | 文件开头/全局定义 | 原文件第77-87行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
77: }
78: 
79: BoxAudioCodec::~BoxAudioCodec() {
80:     ESP_ERROR_CHECK(esp_codec_dev_close(output_dev_));
81:     esp_codec_dev_delete(output_dev_);
82:     ESP_ERROR_CHECK(esp_codec_dev_close(input_dev_));
83:     esp_codec_dev_delete(input_dev_);
84: 
85:     audio_codec_delete_codec_if(in_codec_if_);
86:     audio_codec_delete_ctrl_if(in_ctrl_if_);
87:     audio_codec_delete_codec_if(out_codec_if_);
```

## box_audio_codec.cc | 文件开头/全局定义 | 原文件第88-92行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
88:     audio_codec_delete_ctrl_if(out_ctrl_if_);
89:     audio_codec_delete_gpio_if(gpio_if_);
90:     audio_codec_delete_data_if(data_if_);
91: }
92: 
```

## box_audio_codec.cc | BoxAudioCodec::CreateDuplexChannels | 原文件第93-101行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
93: void BoxAudioCodec::CreateDuplexChannels(gpio_num_t mclk, gpio_num_t bclk, gpio_num_t ws, gpio_num_t dout, gpio_num_t din) {
94:     assert(input_sample_rate_ == output_sample_rate_);
95: 
96:     i2s_chan_config_t chan_cfg = {
97:         .id = I2S_NUM_0,
98:         .role = I2S_ROLE_MASTER,
99:         .dma_desc_num = 6,
100:         .dma_frame_num = 240,
101:         .auto_clear_after_cb = true,
```

## box_audio_codec.cc | BoxAudioCodec::CreateDuplexChannels | 原文件第102-111行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
102:         .auto_clear_before_cb = false,
103:         .intr_priority = 0,
104:     };
105:     ESP_ERROR_CHECK(i2s_new_channel(&chan_cfg, &tx_handle_, &rx_handle_));
106: 
107:     i2s_std_config_t std_cfg = {
108:         .clk_cfg = {
109:             .sample_rate_hz = (uint32_t)output_sample_rate_,
110:             .clk_src = I2S_CLK_SRC_DEFAULT,
111:             .ext_clk_freq_hz = 0,
```

## box_audio_codec.cc | BoxAudioCodec::CreateDuplexChannels | 原文件第112-120行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
112:             .mclk_multiple = I2S_MCLK_MULTIPLE_256
113:         },
114:         .slot_cfg = {
115:             .data_bit_width = I2S_DATA_BIT_WIDTH_16BIT,
116:             .slot_bit_width = I2S_SLOT_BIT_WIDTH_AUTO,
117:             .slot_mode = I2S_SLOT_MODE_STEREO,
118:             .slot_mask = I2S_STD_SLOT_BOTH,
119:             .ws_width = I2S_DATA_BIT_WIDTH_16BIT,
120:             .ws_pol = false,
```

## box_audio_codec.cc | BoxAudioCodec::CreateDuplexChannels | 原文件第121-133行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
121:             .bit_shift = true,
122:             .left_align = true,
123:             .big_endian = false,
124:             .bit_order_lsb = false
125:         },
126:         .gpio_cfg = {
127:             .mclk = mclk,
128:             .bclk = bclk,
129:             .ws = ws,
130:             .dout = dout,
131:             .din = I2S_GPIO_UNUSED,
132:             .invert_flags = {
133:                 .mclk_inv = false,
```

## box_audio_codec.cc | BoxAudioCodec::CreateDuplexChannels | 原文件第134-146行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
134:                 .bclk_inv = false,
135:                 .ws_inv = false
136:             }
137:         }
138:     };
139: 
140:     i2s_tdm_config_t tdm_cfg = {
141:         .clk_cfg = {
142:             .sample_rate_hz = (uint32_t)input_sample_rate_,
143:             .clk_src = I2S_CLK_SRC_DEFAULT,
144:             .ext_clk_freq_hz = 0,
145:             .mclk_multiple = I2S_MCLK_MULTIPLE_256,
146:             .bclk_div = 8,
```

## box_audio_codec.cc | BoxAudioCodec::CreateDuplexChannels | 原文件第147-154行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
147:         },
148:         .slot_cfg = {
149:             .data_bit_width = I2S_DATA_BIT_WIDTH_16BIT,
150:             .slot_bit_width = I2S_SLOT_BIT_WIDTH_AUTO,
151:             .slot_mode = I2S_SLOT_MODE_STEREO,
152:             .slot_mask = i2s_tdm_slot_mask_t(I2S_TDM_SLOT0 | I2S_TDM_SLOT1 | I2S_TDM_SLOT2 | I2S_TDM_SLOT3),
153:             .ws_width = I2S_TDM_AUTO_WS_WIDTH,
154:             .ws_pol = false,
```

## box_audio_codec.cc | BoxAudioCodec::CreateDuplexChannels | 原文件第155-166行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
155:             .bit_shift = true,
156:             .left_align = false,
157:             .big_endian = false,
158:             .bit_order_lsb = false,
159:             .skip_mask = false,
160:             .total_slot = I2S_TDM_AUTO_SLOT_NUM
161:         },
162:         .gpio_cfg = {
163:             .mclk = mclk,
164:             .bclk = bclk,
165:             .ws = ws,
166:             .dout = I2S_GPIO_UNUSED,
```

## box_audio_codec.cc | BoxAudioCodec::CreateDuplexChannels | 原文件第167-178行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
167:             .din = din,
168:             .invert_flags = {
169:                 .mclk_inv = false,
170:                 .bclk_inv = false,
171:                 .ws_inv = false
172:             }
173:         }
174:     };
175: 
176:     ESP_ERROR_CHECK(i2s_channel_init_std_mode(tx_handle_, &std_cfg));
177:     ESP_ERROR_CHECK(i2s_channel_init_tdm_mode(rx_handle_, &tdm_cfg));
178:     ESP_LOGI(TAG, "Duplex channels created");
```

## box_audio_codec.cc | BoxAudioCodec::CreateDuplexChannels | 原文件第179-180行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
179: }
180: 
```

## box_audio_codec.cc | BoxAudioCodec::SetOutputVolume | 原文件第181-185行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
181: void BoxAudioCodec::SetOutputVolume(int volume) {
182:     ESP_ERROR_CHECK(esp_codec_dev_set_out_vol(output_dev_, volume));
183:     AudioCodec::SetOutputVolume(volume);
184: }
185: 
```

## box_audio_codec.cc | BoxAudioCodec::EnableInput | 原文件第186-196行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
186: void BoxAudioCodec::EnableInput(bool enable) {
187:     if (enable == input_enabled_) {
188:         return;
189:     }
190:     if (enable) {
191:         esp_codec_dev_sample_info_t fs = {
192:             .bits_per_sample = 16,
193:             .channel = 4,
194:             .channel_mask = ESP_CODEC_DEV_MAKE_CHANNEL_MASK(0),
195:             .sample_rate = (uint32_t)output_sample_rate_,
196:             .mclk_multiple = 0,
```

## box_audio_codec.cc | BoxAudioCodec::EnableInput | 原文件第197-205行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
197:         };
198:         if (input_reference_) {
199:             fs.channel_mask |= ESP_CODEC_DEV_MAKE_CHANNEL_MASK(1);
200:         }
201:         ESP_ERROR_CHECK(esp_codec_dev_open(input_dev_, &fs));
202:         ESP_ERROR_CHECK(esp_codec_dev_set_in_channel_gain(input_dev_, ESP_CODEC_DEV_MAKE_CHANNEL_MASK(0), 40.0));
203:     } else {
204:         ESP_ERROR_CHECK(esp_codec_dev_close(input_dev_));
205:     }
```

## box_audio_codec.cc | BoxAudioCodec::EnableInput | 原文件第206-208行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
206:     AudioCodec::EnableInput(enable);
207: }
208: 
```

## box_audio_codec.cc | BoxAudioCodec::EnableOutput | 原文件第209-219行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
209: void BoxAudioCodec::EnableOutput(bool enable) {
210:     if (enable == output_enabled_) {
211:         return;
212:     }
213:     if (enable) {
214:         // Play 16bit 1 channel
215:         esp_codec_dev_sample_info_t fs = {
216:             .bits_per_sample = 16,
217:             .channel = 1,
218:             .channel_mask = 0,
219:             .sample_rate = (uint32_t)output_sample_rate_,
```

## box_audio_codec.cc | BoxAudioCodec::EnableOutput | 原文件第220-229行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
220:             .mclk_multiple = 0,
221:         };
222:         ESP_ERROR_CHECK(esp_codec_dev_open(output_dev_, &fs));
223:         ESP_ERROR_CHECK(esp_codec_dev_set_out_vol(output_dev_, output_volume_));
224:     } else {
225:         ESP_ERROR_CHECK(esp_codec_dev_close(output_dev_));
226:     }
227:     AudioCodec::EnableOutput(enable);
228: }
229: 
```

## box_audio_codec.cc | BoxAudioCodec::Read | 原文件第230-236行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
230: int BoxAudioCodec::Read(int16_t* dest, int samples) {
231:     if (input_enabled_) {
232:         ESP_ERROR_CHECK_WITHOUT_ABORT(esp_codec_dev_read(input_dev_, (void*)dest, samples * sizeof(int16_t)));
233:     }
234:     return samples;
235: }
236: 
```

## box_audio_codec.cc | BoxAudioCodec::Write | 原文件第237-242行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.cc
以下为原始源码，不是截图OCR。
```
237: int BoxAudioCodec::Write(const int16_t* data, int samples) {
238:     if (output_enabled_) {
239:         ESP_ERROR_CHECK_WITHOUT_ABORT(esp_codec_dev_write(output_dev_, (void*)data, samples * sizeof(int16_t)));
240:     }
241:     return samples;
242: }
```

## box_audio_codec.h | 文件开头/全局定义 | 原文件第1-13行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.h
以下为原始源码，不是截图OCR。
```
1: #ifndef _BOX_AUDIO_CODEC_H
2: #define _BOX_AUDIO_CODEC_H
3: 
4: #include "audio_codec.h"
5: 
6: #include <esp_codec_dev.h>
7: #include <esp_codec_dev_defaults.h>
8: 
9: class BoxAudioCodec : public AudioCodec {
10: private:
11:     const audio_codec_data_if_t* data_if_ = nullptr;
12:     const audio_codec_ctrl_if_t* out_ctrl_if_ = nullptr;
13:     const audio_codec_if_t* out_codec_if_ = nullptr;
```

## box_audio_codec.h | 文件开头/全局定义 | 原文件第14-22行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.h
以下为原始源码，不是截图OCR。
```
14:     const audio_codec_ctrl_if_t* in_ctrl_if_ = nullptr;
15:     const audio_codec_if_t* in_codec_if_ = nullptr;
16:     const audio_codec_gpio_if_t* gpio_if_ = nullptr;
17: 
18:     esp_codec_dev_handle_t output_dev_ = nullptr;
19:     esp_codec_dev_handle_t input_dev_ = nullptr;
20: 
21:     void CreateDuplexChannels(gpio_num_t mclk, gpio_num_t bclk, gpio_num_t ws, gpio_num_t dout, gpio_num_t din);
22: 
```

## box_audio_codec.h | 文件开头/全局定义 | 原文件第23-29行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.h
以下为原始源码，不是截图OCR。
```
23:     virtual int Read(int16_t* dest, int samples) override;
24:     virtual int Write(const int16_t* data, int samples) override;
25: 
26: public:
27:     BoxAudioCodec(void* i2c_master_handle, int input_sample_rate, int output_sample_rate,
28:         gpio_num_t mclk, gpio_num_t bclk, gpio_num_t ws, gpio_num_t dout, gpio_num_t din,
29:         gpio_num_t pa_pin, uint8_t es8311_addr, uint8_t es7210_addr, bool input_reference);
```

## box_audio_codec.h | 文件开头/全局定义 | 原文件第30-37行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/box_audio_codec.h
以下为原始源码，不是截图OCR。
```
30:     virtual ~BoxAudioCodec();
31: 
32:     virtual void SetOutputVolume(int volume) override;
33:     virtual void EnableInput(bool enable) override;
34:     virtual void EnableOutput(bool enable) override;
35: };
36: 
37: #endif // _BOX_AUDIO_CODEC_H
```

## es8311_audio_codec.cc | 文件开头/全局定义 | 原文件第1-10行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.cc
以下为原始源码，不是截图OCR。
```
1: #include "es8311_audio_codec.h"
2: 
3: #include <esp_log.h>
4: 
5: static const char TAG[] = "Es8311AudioCodec";
6: 
7: Es8311AudioCodec::Es8311AudioCodec(void* i2c_master_handle, i2c_port_t i2c_port, int input_sample_rate, int output_sample_rate,
8:     gpio_num_t mclk, gpio_num_t bclk, gpio_num_t ws, gpio_num_t dout, gpio_num_t din,
9:     gpio_num_t pa_pin, uint8_t es8311_addr, bool use_mclk) {
10:     duplex_ = true; // 是否双工
```

## es8311_audio_codec.cc | 文件开头/全局定义 | 原文件第11-20行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.cc
以下为原始源码，不是截图OCR。
```
11:     input_reference_ = false; // 是否使用参考输入，实现回声消除
12:     input_channels_ = 1; // 输入通道数
13:     input_sample_rate_ = input_sample_rate;
14:     output_sample_rate_ = output_sample_rate;
15:     pa_pin_ = pa_pin;
16:     CreateDuplexChannels(mclk, bclk, ws, dout, din);
17: 
18:     // Do initialize of related interface: data_if, ctrl_if and gpio_if
19:     audio_codec_i2s_cfg_t i2s_cfg = {
20:         .port = I2S_NUM_0,
```

## es8311_audio_codec.cc | 文件开头/全局定义 | 原文件第21-33行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.cc
以下为原始源码，不是截图OCR。
```
21:         .rx_handle = rx_handle_,
22:         .tx_handle = tx_handle_,
23:     };
24:     data_if_ = audio_codec_new_i2s_data(&i2s_cfg);
25:     assert(data_if_ != NULL);
26: 
27:     // Output
28:     audio_codec_i2c_cfg_t i2c_cfg = {
29:         .port = i2c_port,
30:         .addr = es8311_addr,
31:         .bus_handle = i2c_master_handle,
32:     };
33:     ctrl_if_ = audio_codec_new_i2c_ctrl(&i2c_cfg);
```

## es8311_audio_codec.cc | 文件开头/全局定义 | 原文件第34-45行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.cc
以下为原始源码，不是截图OCR。
```
34:     assert(ctrl_if_ != NULL);
35: 
36:     gpio_if_ = audio_codec_new_gpio();
37:     assert(gpio_if_ != NULL);
38: 
39:     es8311_codec_cfg_t es8311_cfg = {};
40:     es8311_cfg.ctrl_if = ctrl_if_;
41:     es8311_cfg.gpio_if = gpio_if_;
42:     es8311_cfg.codec_mode = ESP_CODEC_DEV_WORK_MODE_BOTH;
43:     es8311_cfg.pa_pin = pa_pin;
44:     es8311_cfg.use_mclk = use_mclk;
45:     es8311_cfg.hw_gain.pa_voltage = 5.0;
```

## es8311_audio_codec.cc | 文件开头/全局定义 | 原文件第46-56行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.cc
以下为原始源码，不是截图OCR。
```
46:     es8311_cfg.hw_gain.codec_dac_voltage = 3.3;
47:     codec_if_ = es8311_codec_new(&es8311_cfg);
48:     assert(codec_if_ != NULL);
49: 
50:     esp_codec_dev_cfg_t dev_cfg = {
51:         .dev_type = ESP_CODEC_DEV_TYPE_OUT,
52:         .codec_if = codec_if_,
53:         .data_if = data_if_,
54:     };
55:     output_dev_ = esp_codec_dev_new(&dev_cfg);
56:     assert(output_dev_ != NULL);
```

## es8311_audio_codec.cc | 文件开头/全局定义 | 原文件第57-66行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.cc
以下为原始源码，不是截图OCR。
```
57:     dev_cfg.dev_type = ESP_CODEC_DEV_TYPE_IN;
58:     input_dev_ = esp_codec_dev_new(&dev_cfg);
59:     assert(input_dev_ != NULL);
60:     esp_codec_set_disable_when_closed(output_dev_, false);
61:     esp_codec_set_disable_when_closed(input_dev_, false);
62:     ESP_LOGI(TAG, "Es8311AudioCodec initialized");
63: }
64: 
65: Es8311AudioCodec::~Es8311AudioCodec() {
66:     ESP_ERROR_CHECK(esp_codec_dev_close(output_dev_));
```

## es8311_audio_codec.cc | 文件开头/全局定义 | 原文件第67-76行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.cc
以下为原始源码，不是截图OCR。
```
67:     esp_codec_dev_delete(output_dev_);
68:     ESP_ERROR_CHECK(esp_codec_dev_close(input_dev_));
69:     esp_codec_dev_delete(input_dev_);
70: 
71:     audio_codec_delete_codec_if(codec_if_);
72:     audio_codec_delete_ctrl_if(ctrl_if_);
73:     audio_codec_delete_gpio_if(gpio_if_);
74:     audio_codec_delete_data_if(data_if_);
75: }
76: 
```

## es8311_audio_codec.cc | Es8311AudioCodec::CreateDuplexChannels | 原文件第77-85行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.cc
以下为原始源码，不是截图OCR。
```
77: void Es8311AudioCodec::CreateDuplexChannels(gpio_num_t mclk, gpio_num_t bclk, gpio_num_t ws, gpio_num_t dout, gpio_num_t din) {
78:     assert(input_sample_rate_ == output_sample_rate_);
79: 
80:     i2s_chan_config_t chan_cfg = {
81:         .id = I2S_NUM_0,
82:         .role = I2S_ROLE_MASTER,
83:         .dma_desc_num = 6,
84:         .dma_frame_num = 240,
85:         .auto_clear_after_cb = true,
```

## es8311_audio_codec.cc | Es8311AudioCodec::CreateDuplexChannels | 原文件第86-96行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.cc
以下为原始源码，不是截图OCR。
```
86:         .auto_clear_before_cb = false,
87:         .intr_priority = 0,
88:     };
89:     ESP_ERROR_CHECK(i2s_new_channel(&chan_cfg, &tx_handle_, &rx_handle_));
90: 
91:     i2s_std_config_t std_cfg = {
92:         .clk_cfg = {
93:             .sample_rate_hz = (uint32_t)output_sample_rate_,
94:             .clk_src = I2S_CLK_SRC_DEFAULT,
95:             .mclk_multiple = I2S_MCLK_MULTIPLE_256,
96: 			#ifdef   I2S_HW_VERSION_2    
```

## es8311_audio_codec.cc | Es8311AudioCodec::CreateDuplexChannels | 原文件第97-107行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.cc
以下为原始源码，不是截图OCR。
```
97: 				.ext_clk_freq_hz = 0,
98: 			#endif
99:         },
100:         .slot_cfg = {
101:             .data_bit_width = I2S_DATA_BIT_WIDTH_16BIT,
102:             .slot_bit_width = I2S_SLOT_BIT_WIDTH_AUTO,
103:             .slot_mode = I2S_SLOT_MODE_STEREO,
104:             .slot_mask = I2S_STD_SLOT_BOTH,
105:             .ws_width = I2S_DATA_BIT_WIDTH_16BIT,
106:             .ws_pol = false,
107:             .bit_shift = true,
```

## es8311_audio_codec.cc | Es8311AudioCodec::CreateDuplexChannels | 原文件第108-120行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.cc
以下为原始源码，不是截图OCR。
```
108:             #ifdef   I2S_HW_VERSION_2   
109:                 .left_align = true,
110:                 .big_endian = false,
111:                 .bit_order_lsb = false
112:             #endif
113:         },
114:         .gpio_cfg = {
115:             .mclk = mclk,
116:             .bclk = bclk,
117:             .ws = ws,
118:             .dout = dout,
119:             .din = din,
120:             .invert_flags = {
```

## es8311_audio_codec.cc | Es8311AudioCodec::CreateDuplexChannels | 原文件第121-132行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.cc
以下为原始源码，不是截图OCR。
```
121:                 .mclk_inv = false,
122:                 .bclk_inv = false,
123:                 .ws_inv = false
124:             }
125:         }
126:     };
127: 
128:     ESP_ERROR_CHECK(i2s_channel_init_std_mode(tx_handle_, &std_cfg));
129:     ESP_ERROR_CHECK(i2s_channel_init_std_mode(rx_handle_, &std_cfg));
130:     ESP_LOGI(TAG, "Duplex channels created");
131: }
132: 
```

## es8311_audio_codec.cc | Es8311AudioCodec::SetOutputVolume | 原文件第133-137行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.cc
以下为原始源码，不是截图OCR。
```
133: void Es8311AudioCodec::SetOutputVolume(int volume) {
134:     ESP_ERROR_CHECK(esp_codec_dev_set_out_vol(output_dev_, volume));
135:     AudioCodec::SetOutputVolume(volume);
136: }
137: 
```

## es8311_audio_codec.cc | Es8311AudioCodec::EnableInput | 原文件第138-149行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.cc
以下为原始源码，不是截图OCR。
```
138: void Es8311AudioCodec::EnableInput(bool enable) {
139:     if (enable == input_enabled_) {
140:         return;
141:     }
142:     if (enable) {
143:         esp_codec_dev_sample_info_t fs = {
144:             .bits_per_sample = 16,
145:             .channel = 1,
146:             .channel_mask = 0,
147:             .sample_rate = (uint32_t)input_sample_rate_,
148:             .mclk_multiple = 0,
149:         };
```

## es8311_audio_codec.cc | Es8311AudioCodec::EnableInput | 原文件第150-157行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.cc
以下为原始源码，不是截图OCR。
```
150:         ESP_ERROR_CHECK(esp_codec_dev_open(input_dev_, &fs));
151:         ESP_ERROR_CHECK(esp_codec_dev_set_in_gain(input_dev_, 40.0));
152:     } else {
153:         ESP_ERROR_CHECK(esp_codec_dev_close(input_dev_));
154:     }
155:     AudioCodec::EnableInput(enable);
156: }
157: 
```

## es8311_audio_codec.cc | Es8311AudioCodec::EnableOutput | 原文件第158-168行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.cc
以下为原始源码，不是截图OCR。
```
158: void Es8311AudioCodec::EnableOutput(bool enable) {
159:     if (enable == output_enabled_) {
160:         return;
161:     }
162:     if (enable) {
163:         // Play 16bit 1 channel
164:         esp_codec_dev_sample_info_t fs = {
165:             .bits_per_sample = 16,
166:             .channel = 1,
167:             .channel_mask = 0,
168:             .sample_rate = (uint32_t)output_sample_rate_,
```

## es8311_audio_codec.cc | Es8311AudioCodec::EnableOutput | 原文件第169-178行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.cc
以下为原始源码，不是截图OCR。
```
169:             .mclk_multiple = 0,
170:         };
171:         ESP_ERROR_CHECK(esp_codec_dev_open(output_dev_, &fs));
172:         ESP_ERROR_CHECK(esp_codec_dev_set_out_vol(output_dev_, output_volume_));
173:         if (pa_pin_ != GPIO_NUM_NC) {
174:             gpio_set_level(pa_pin_, 1);
175:         }
176:     } else {
177:         ESP_ERROR_CHECK(esp_codec_dev_close(output_dev_));
178:         if (pa_pin_ != GPIO_NUM_NC) {
```

## es8311_audio_codec.cc | Es8311AudioCodec::EnableOutput | 原文件第179-184行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.cc
以下为原始源码，不是截图OCR。
```
179:             gpio_set_level(pa_pin_, 0);
180:         }
181:     }
182:     AudioCodec::EnableOutput(enable);
183: }
184: 
```

## es8311_audio_codec.cc | Es8311AudioCodec::Read | 原文件第185-191行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.cc
以下为原始源码，不是截图OCR。
```
185: int Es8311AudioCodec::Read(int16_t* dest, int samples) {
186:     if (input_enabled_) {
187:         ESP_ERROR_CHECK_WITHOUT_ABORT(esp_codec_dev_read(input_dev_, (void*)dest, samples * sizeof(int16_t)));
188:     }
189:     return samples;
190: }
191: 
```

## es8311_audio_codec.cc | Es8311AudioCodec::Write | 原文件第192-197行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.cc
以下为原始源码，不是截图OCR。
```
192: int Es8311AudioCodec::Write(const int16_t* data, int samples) {
193:     if (output_enabled_) {
194:         ESP_ERROR_CHECK_WITHOUT_ABORT(esp_codec_dev_write(output_dev_, (void*)data, samples * sizeof(int16_t)));
195:     }
196:     return samples;
197: }
```

## es8311_audio_codec.h | 文件开头/全局定义 | 原文件第1-14行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.h
以下为原始源码，不是截图OCR。
```
1: #ifndef _ES8311_AUDIO_CODEC_H
2: #define _ES8311_AUDIO_CODEC_H
3: 
4: #include "audio_codec.h"
5: 
6: #include <driver/i2c.h>
7: #include <driver/gpio.h>
8: #include <esp_codec_dev.h>
9: #include <esp_codec_dev_defaults.h>
10: 
11: class Es8311AudioCodec : public AudioCodec {
12: private:
13:     const audio_codec_data_if_t* data_if_ = nullptr;
14:     const audio_codec_ctrl_if_t* ctrl_if_ = nullptr;
```

## es8311_audio_codec.h | 文件开头/全局定义 | 原文件第15-23行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.h
以下为原始源码，不是截图OCR。
```
15:     const audio_codec_if_t* codec_if_ = nullptr;
16:     const audio_codec_gpio_if_t* gpio_if_ = nullptr;
17: 
18:     esp_codec_dev_handle_t output_dev_ = nullptr;
19:     esp_codec_dev_handle_t input_dev_ = nullptr;
20:     gpio_num_t pa_pin_ = GPIO_NUM_NC;
21: 
22:     void CreateDuplexChannels(gpio_num_t mclk, gpio_num_t bclk, gpio_num_t ws, gpio_num_t dout, gpio_num_t din);
23: 
```

## es8311_audio_codec.h | 文件开头/全局定义 | 原文件第24-30行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.h
以下为原始源码，不是截图OCR。
```
24:     virtual int Read(int16_t* dest, int samples) override;
25:     virtual int Write(const int16_t* data, int samples) override;
26: 
27: public:
28:     Es8311AudioCodec(void* i2c_master_handle, i2c_port_t i2c_port, int input_sample_rate, int output_sample_rate,
29:         gpio_num_t mclk, gpio_num_t bclk, gpio_num_t ws, gpio_num_t dout, gpio_num_t din,
30:         gpio_num_t pa_pin, uint8_t es8311_addr, bool use_mclk = true);
```

## es8311_audio_codec.h | 文件开头/全局定义 | 原文件第31-38行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8311_audio_codec.h
以下为原始源码，不是截图OCR。
```
31:     virtual ~Es8311AudioCodec();
32: 
33:     virtual void SetOutputVolume(int volume) override;
34:     virtual void EnableInput(bool enable) override;
35:     virtual void EnableOutput(bool enable) override;
36: };
37: 
38: #endif // _ES8311_AUDIO_CODEC_H
```

## es8388_audio_codec.cc | 文件开头/全局定义 | 原文件第1-10行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
1: #include "es8388_audio_codec.h"
2: 
3: #include <esp_log.h>
4: 
5: static const char TAG[] = "Es8388AudioCodec";
6: 
7: Es8388AudioCodec::Es8388AudioCodec(void* i2c_master_handle, i2c_port_t i2c_port, int input_sample_rate, int output_sample_rate,
8:     gpio_num_t mclk, gpio_num_t bclk, gpio_num_t ws, gpio_num_t dout, gpio_num_t din,
9:     gpio_num_t pa_pin, uint8_t es8388_addr) {
10:     duplex_ = true; // 是否双工
```

## es8388_audio_codec.cc | 文件开头/全局定义 | 原文件第11-14行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
11:     input_reference_ = false; // 是否使用参考输入，实现回声消除
12:     input_channels_ = 1; // 输入通道数
13:     input_sample_rate_ = input_sample_rate;
14:     output_sample_rate_ = output_sample_rate;
```

## es8388_audio_codec.cc | 文件开头/全局定义 | 原文件第15-19行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
15:     pa_pin_ = pa_pin;                                                                                                                                                                                     CreateDuplexChannels(mclk, bclk, ws, dout, din);
16: 
17:     // Do initialize of related interface: data_if, ctrl_if and gpio_if
18:     audio_codec_i2s_cfg_t i2s_cfg = {
19:         .port = I2S_NUM_0,
```

## es8388_audio_codec.cc | 文件开头/全局定义 | 原文件第20-32行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
20:         .rx_handle = rx_handle_,
21:         .tx_handle = tx_handle_,
22:     };
23:     data_if_ = audio_codec_new_i2s_data(&i2s_cfg);
24:     assert(data_if_ != NULL);
25: 
26:     // Output
27:     audio_codec_i2c_cfg_t i2c_cfg = {
28:         .port = i2c_port,
29:         .addr = es8388_addr,
30:         .bus_handle = i2c_master_handle,
31:     };
32:     ctrl_if_ = audio_codec_new_i2c_ctrl(&i2c_cfg);
```

## es8388_audio_codec.cc | 文件开头/全局定义 | 原文件第33-44行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
33:     assert(ctrl_if_ != NULL);
34: 
35:     gpio_if_ = audio_codec_new_gpio();
36:     assert(gpio_if_ != NULL);
37: 
38:     es8388_codec_cfg_t es8388_cfg = {};
39:     es8388_cfg.ctrl_if = ctrl_if_;
40:     es8388_cfg.gpio_if = gpio_if_;
41:     es8388_cfg.codec_mode = ESP_CODEC_DEV_WORK_MODE_BOTH;
42:     es8388_cfg.master_mode = true;
43:     es8388_cfg.pa_pin = pa_pin;
44:     es8388_cfg.pa_reverted = false;
```

## es8388_audio_codec.cc | 文件开头/全局定义 | 原文件第45-55行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
45:     es8388_cfg.hw_gain.pa_voltage = 5.0;
46:     es8388_cfg.hw_gain.codec_dac_voltage = 3.3;
47:     codec_if_ = es8388_codec_new(&es8388_cfg);
48:     assert(codec_if_ != NULL);
49: 
50:     esp_codec_dev_cfg_t outdev_cfg = {
51:         .dev_type = ESP_CODEC_DEV_TYPE_OUT,
52:         .codec_if = codec_if_,
53:         .data_if = data_if_,
54:     };
55:     output_dev_ = esp_codec_dev_new(&outdev_cfg);
```

## es8388_audio_codec.cc | 文件开头/全局定义 | 原文件第56-66行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
56:     assert(output_dev_ != NULL);
57: 
58:     esp_codec_dev_cfg_t indev_cfg = {
59:         .dev_type = ESP_CODEC_DEV_TYPE_IN,
60:         .codec_if = codec_if_,
61:         .data_if = data_if_,
62:     };
63:     input_dev_ = esp_codec_dev_new(&indev_cfg);
64:     assert(input_dev_ != NULL);
65:     esp_codec_set_disable_when_closed(output_dev_, false);
66:     esp_codec_set_disable_when_closed(input_dev_, false);
```

## es8388_audio_codec.cc | 文件开头/全局定义 | 原文件第67-77行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
67:     ESP_LOGI(TAG, "Es8388AudioCodec initialized");
68: }
69: 
70: Es8388AudioCodec::~Es8388AudioCodec() {
71:     ESP_ERROR_CHECK(esp_codec_dev_close(output_dev_));
72:     esp_codec_dev_delete(output_dev_);
73:     ESP_ERROR_CHECK(esp_codec_dev_close(input_dev_));
74:     esp_codec_dev_delete(input_dev_);
75: 
76:     audio_codec_delete_codec_if(codec_if_);
77:     audio_codec_delete_ctrl_if(ctrl_if_);
```

## es8388_audio_codec.cc | 文件开头/全局定义 | 原文件第78-81行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
78:     audio_codec_delete_gpio_if(gpio_if_);
79:     audio_codec_delete_data_if(data_if_);
80: }
81: 
```

## es8388_audio_codec.cc | Es8388AudioCodec::CreateDuplexChannels | 原文件第82-90行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
82: void Es8388AudioCodec::CreateDuplexChannels(gpio_num_t mclk, gpio_num_t bclk, gpio_num_t ws, gpio_num_t dout, gpio_num_t din){
83:     assert(input_sample_rate_ == output_sample_rate_);
84: 
85:     i2s_chan_config_t chan_cfg = {
86:         .id = I2S_NUM_0,
87:         .role = I2S_ROLE_MASTER,
88:         .dma_desc_num = 6,
89:         .dma_frame_num = 240,
90:         .auto_clear_after_cb = true,
```

## es8388_audio_codec.cc | Es8388AudioCodec::CreateDuplexChannels | 原文件第91-101行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
91:         .auto_clear_before_cb = false,
92:         .intr_priority = 0,
93:     };
94:     ESP_ERROR_CHECK(i2s_new_channel(&chan_cfg, &tx_handle_, &rx_handle_));
95: 
96:     i2s_std_config_t std_cfg = {
97:         .clk_cfg = {
98:             .sample_rate_hz = (uint32_t)output_sample_rate_,
99:             .clk_src = I2S_CLK_SRC_DEFAULT,
100:             .ext_clk_freq_hz = 0,
101:             .mclk_multiple = I2S_MCLK_MULTIPLE_256
```

## es8388_audio_codec.cc | Es8388AudioCodec::CreateDuplexChannels | 原文件第102-111行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
102:         },
103:         .slot_cfg = {
104:             .data_bit_width = I2S_DATA_BIT_WIDTH_16BIT,
105:             .slot_bit_width = I2S_SLOT_BIT_WIDTH_AUTO,
106:             .slot_mode = I2S_SLOT_MODE_STEREO,
107:             .slot_mask = I2S_STD_SLOT_BOTH,
108:             .ws_width = I2S_DATA_BIT_WIDTH_16BIT,
109:             .ws_pol = false,
110:             .bit_shift = true,
111:             .left_align = true,
```

## es8388_audio_codec.cc | Es8388AudioCodec::CreateDuplexChannels | 原文件第112-124行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
112:             .big_endian = false,
113:             .bit_order_lsb = false
114:         },
115:         .gpio_cfg = {
116:             .mclk = mclk,
117:             .bclk = bclk,
118:             .ws = ws,
119:             .dout = dout,
120:             .din = din,
121:             .invert_flags = {
122:                 .mclk_inv = false,
123:                 .bclk_inv = false,
124:                 .ws_inv = false
```

## es8388_audio_codec.cc | Es8388AudioCodec::CreateDuplexChannels | 原文件第125-133行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
125:             }
126:         }
127:     };
128: 
129:     ESP_ERROR_CHECK(i2s_channel_init_std_mode(tx_handle_, &std_cfg));
130:     ESP_ERROR_CHECK(i2s_channel_init_std_mode(rx_handle_, &std_cfg));
131:     ESP_LOGI(TAG, "Duplex channels created");
132: }
133: 
```

## es8388_audio_codec.cc | Es8388AudioCodec::SetOutputVolume | 原文件第134-138行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
134: void Es8388AudioCodec::SetOutputVolume(int volume) {
135:     ESP_ERROR_CHECK(esp_codec_dev_set_out_vol(output_dev_, volume));
136:     AudioCodec::SetOutputVolume(volume);
137: }
138: 
```

## es8388_audio_codec.cc | Es8388AudioCodec::EnableInput | 原文件第139-150行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
139: void Es8388AudioCodec::EnableInput(bool enable) {
140:     if (enable == input_enabled_) {
141:         return;
142:     }
143:     if (enable) {
144:         esp_codec_dev_sample_info_t fs = {
145:             .bits_per_sample = 16,
146:             .channel = 1,
147:             .channel_mask = 0,
148:             .sample_rate = (uint32_t)input_sample_rate_,
149:             .mclk_multiple = 0,
150:         };
```

## es8388_audio_codec.cc | Es8388AudioCodec::EnableInput | 原文件第151-158行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
151:         ESP_ERROR_CHECK(esp_codec_dev_open(input_dev_, &fs));
152:         ESP_ERROR_CHECK(esp_codec_dev_set_in_gain(input_dev_, 24.0));
153:     } else {
154:         ESP_ERROR_CHECK(esp_codec_dev_close(input_dev_));
155:     }
156:     AudioCodec::EnableInput(enable);
157: }
158: 
```

## es8388_audio_codec.cc | Es8388AudioCodec::EnableOutput | 原文件第159-170行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
159: void Es8388AudioCodec::EnableOutput(bool enable) {
160:     if (enable == output_enabled_) {
161:         return;
162:     }
163:     if (enable) {
164:         esp_codec_dev_sample_info_t fs = {
165:             .bits_per_sample = 16,
166:             .channel = 1,
167:             .channel_mask = 0,
168:             .sample_rate = (uint32_t)output_sample_rate_,
169:             .mclk_multiple = 0,
170:         };
```

## es8388_audio_codec.cc | Es8388AudioCodec::EnableOutput | 原文件第171-177行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
171:         ESP_ERROR_CHECK(esp_codec_dev_open(output_dev_, &fs));
172:         ESP_ERROR_CHECK(esp_codec_dev_set_out_vol(output_dev_, output_volume_));
173: 
174:         // Set analog output volume to 0dB, default is -45dB
175:         uint8_t reg_val = 30; // 0dB
176:         uint8_t regs[] = { 46, 47, 48, 49 }; // HP_LVOL, HP_RVOL, SPK_LVOL, SPK_RVOL
177:         for (uint8_t reg : regs) {
```

## es8388_audio_codec.cc | Es8388AudioCodec::EnableOutput | 原文件第178-191行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
178:             ctrl_if_->write_reg(ctrl_if_, reg, 1, &reg_val, 1);
179:         }
180: 
181:         if (pa_pin_ != GPIO_NUM_NC) {
182:             gpio_set_level(pa_pin_, 1);
183:         }
184:     } else {
185:         ESP_ERROR_CHECK(esp_codec_dev_close(output_dev_));
186:         if (pa_pin_ != GPIO_NUM_NC) {
187:             gpio_set_level(pa_pin_, 0);
188:         }
189:     }
190:     AudioCodec::EnableOutput(enable);
191: }
```

## es8388_audio_codec.cc | Es8388AudioCodec::EnableOutput | 原文件第192-192行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
192: 
```

## es8388_audio_codec.cc | Es8388AudioCodec::Read | 原文件第193-199行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
193: int Es8388AudioCodec::Read(int16_t* dest, int samples) {
194:     if (input_enabled_) {
195:         ESP_ERROR_CHECK_WITHOUT_ABORT(esp_codec_dev_read(input_dev_, (void*)dest, samples * sizeof(int16_t)));
196:     }
197:     return samples;
198: }
199: 
```

## es8388_audio_codec.cc | Es8388AudioCodec::Write | 原文件第200-205行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.cc
以下为原始源码，不是截图OCR。
```
200: int Es8388AudioCodec::Write(const int16_t* data, int samples) {
201:     if (output_enabled_) {
202:         ESP_ERROR_CHECK_WITHOUT_ABORT(esp_codec_dev_write(output_dev_, (void*)data, samples * sizeof(int16_t)));
203:     }
204:     return samples;
205: }
```

## es8388_audio_codec.h | 文件开头/全局定义 | 原文件第1-14行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.h
以下为原始源码，不是截图OCR。
```
1: #ifndef _ES8388_AUDIO_CODEC_H
2: #define _ES8388_AUDIO_CODEC_H
3: 
4: #include "audio_codec.h"
5: 
6: #include <driver/i2c.h>
7: #include <esp_codec_dev.h>
8: #include <esp_codec_dev_defaults.h>
9: 
10: class Es8388AudioCodec : public AudioCodec {
11: private:
12:     const audio_codec_data_if_t* data_if_ = nullptr;
13:     const audio_codec_ctrl_if_t* ctrl_if_ = nullptr;
14:     const audio_codec_if_t* codec_if_ = nullptr;
```

## es8388_audio_codec.h | 文件开头/全局定义 | 原文件第15-23行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.h
以下为原始源码，不是截图OCR。
```
15:     const audio_codec_gpio_if_t* gpio_if_ = nullptr;
16: 
17:     esp_codec_dev_handle_t output_dev_ = nullptr;
18:     esp_codec_dev_handle_t input_dev_ = nullptr;
19:     gpio_num_t pa_pin_ = GPIO_NUM_NC;
20: 
21:     void CreateDuplexChannels(gpio_num_t mclk, gpio_num_t bclk, gpio_num_t ws, gpio_num_t dout, gpio_num_t din);
22: 
23:     virtual int Read(int16_t* dest, int samples) override;
```

## es8388_audio_codec.h | 文件开头/全局定义 | 原文件第24-31行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.h
以下为原始源码，不是截图OCR。
```
24:     virtual int Write(const int16_t* data, int samples) override;
25: 
26: public:
27:     Es8388AudioCodec(void* i2c_master_handle, i2c_port_t i2c_port, int input_sample_rate, int output_sample_rate,
28:         gpio_num_t mclk, gpio_num_t bclk, gpio_num_t ws, gpio_num_t dout, gpio_num_t din,
29:         gpio_num_t pa_pin, uint8_t es8388_addr);
30:     virtual ~Es8388AudioCodec();
31: 
```

## es8388_audio_codec.h | 文件开头/全局定义 | 原文件第32-37行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/es8388_audio_codec.h
以下为原始源码，不是截图OCR。
```
32:     virtual void SetOutputVolume(int volume) override;
33:     virtual void EnableInput(bool enable) override;
34:     virtual void EnableOutput(bool enable) override;
35: };
36: 
37: #endif // _ES8388_AUDIO_CODEC_H
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第1-17行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
1: #include "no_audio_codec.h"
2: 
3: #include <esp_log.h>
4: #include <cmath>
5: #include <cstring>
6: 
7: #define TAG "NoAudioCodec"
8: 
9: NoAudioCodec::~NoAudioCodec() {
10:     if (rx_handle_ != nullptr) {
11:         ESP_ERROR_CHECK(i2s_channel_disable(rx_handle_));
12:     }
13:     if (tx_handle_ != nullptr) {
14:         ESP_ERROR_CHECK(i2s_channel_disable(tx_handle_));
15:     }
16: }
17: 
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第18-26行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
18: NoAudioCodecDuplex::NoAudioCodecDuplex(int input_sample_rate, int output_sample_rate, gpio_num_t bclk, gpio_num_t ws, gpio_num_t dout, gpio_num_t din) {
19:     duplex_ = true;
20:     input_sample_rate_ = input_sample_rate;
21:     output_sample_rate_ = output_sample_rate;
22: 
23:     i2s_chan_config_t chan_cfg = {
24:         .id = I2S_NUM_0,
25:         .role = I2S_ROLE_MASTER,
26:         .dma_desc_num = 6,
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第27-37行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
27:         .dma_frame_num = 240,
28:         .auto_clear_after_cb = true,
29:         .auto_clear_before_cb = false,
30:         .intr_priority = 0,
31:     };
32:     ESP_ERROR_CHECK(i2s_new_channel(&chan_cfg, &tx_handle_, &rx_handle_));
33: 
34:     i2s_std_config_t std_cfg = {
35:         .clk_cfg = {
36:             .sample_rate_hz = (uint32_t)output_sample_rate_,
37:             .clk_src = I2S_CLK_SRC_DEFAULT,
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第38-48行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
38:             .mclk_multiple = I2S_MCLK_MULTIPLE_256,
39: 			#ifdef   I2S_HW_VERSION_2
40: 				.ext_clk_freq_hz = 0,
41: 			#endif
42: 
43:         },
44:         .slot_cfg = {
45:             .data_bit_width = I2S_DATA_BIT_WIDTH_32BIT,
46:             .slot_bit_width = I2S_SLOT_BIT_WIDTH_AUTO,
47:             .slot_mode = I2S_SLOT_MODE_MONO,
48:             .slot_mask = I2S_STD_SLOT_LEFT,
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第49-61行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
49:             .ws_width = I2S_DATA_BIT_WIDTH_32BIT,
50:             .ws_pol = false,
51:             .bit_shift = true,
52:             #ifdef   I2S_HW_VERSION_2
53:                 .left_align = true,
54:                 .big_endian = false,
55:                 .bit_order_lsb = false
56:             #endif
57: 
58:         },
59:         .gpio_cfg = {
60:             .mclk = I2S_GPIO_UNUSED,
61:             .bclk = bclk,
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第62-73行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
62:             .ws = ws,
63:             .dout = dout,
64:             .din = din,
65:             .invert_flags = {
66:                 .mclk_inv = false,
67:                 .bclk_inv = false,
68:                 .ws_inv = false
69:             }
70:         }
71:     };
72:     ESP_ERROR_CHECK(i2s_channel_init_std_mode(tx_handle_, &std_cfg));
73:     ESP_ERROR_CHECK(i2s_channel_init_std_mode(rx_handle_, &std_cfg));
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第74-83行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
74:     ESP_LOGI(TAG, "Duplex channels created");
75: }
76: 
77: ATK_NoAudioCodecDuplex::ATK_NoAudioCodecDuplex(int input_sample_rate, int output_sample_rate, gpio_num_t bclk, gpio_num_t ws, gpio_num_t dout, gpio_num_t din) {
78:     duplex_ = true;
79:     input_sample_rate_ = input_sample_rate;
80:     output_sample_rate_ = output_sample_rate;
81: 
82:     i2s_chan_config_t chan_cfg = {
83:         .id = I2S_NUM_0,
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第84-95行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
84:         .role = I2S_ROLE_MASTER,
85:         .dma_desc_num = 6,
86:         .dma_frame_num = 240,
87:         .auto_clear_after_cb = true,
88:         .auto_clear_before_cb = false,
89:         .intr_priority = 0,
90:     };
91:     ESP_ERROR_CHECK(i2s_new_channel(&chan_cfg, &tx_handle_, &rx_handle_));
92: 
93:     i2s_std_config_t std_cfg = {
94:         .clk_cfg = {
95:             .sample_rate_hz = (uint32_t)output_sample_rate_,
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第96-105行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
96:             .clk_src = I2S_CLK_SRC_DEFAULT,
97:             .mclk_multiple = I2S_MCLK_MULTIPLE_256,
98: 			#ifdef   I2S_HW_VERSION_2
99: 				.ext_clk_freq_hz = 0,
100: 			#endif
101:         },
102:         .slot_cfg = {
103:             .data_bit_width = I2S_DATA_BIT_WIDTH_16BIT,
104:             .slot_bit_width = I2S_SLOT_BIT_WIDTH_AUTO,
105:             .slot_mode = I2S_SLOT_MODE_STEREO,
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第106-116行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
106:             .slot_mask = I2S_STD_SLOT_BOTH,
107:             .ws_width = I2S_DATA_BIT_WIDTH_16BIT,
108:             .ws_pol = false,
109:             .bit_shift = true,
110:             #ifdef   I2S_HW_VERSION_2
111:                 .left_align = true,
112:                 .big_endian = false,
113:                 .bit_order_lsb = false
114:             #endif
115:         },
116:         .gpio_cfg = {
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第117-129行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
117:             .mclk = I2S_GPIO_UNUSED,
118:             .bclk = bclk,
119:             .ws = ws,
120:             .dout = dout,
121:             .din = din,
122:             .invert_flags = {
123:                 .mclk_inv = false,
124:                 .bclk_inv = false,
125:                 .ws_inv = false
126:             }
127:         }
128:     };
129:     ESP_ERROR_CHECK(i2s_channel_init_std_mode(tx_handle_, &std_cfg));
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第130-137行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
130:     ESP_ERROR_CHECK(i2s_channel_init_std_mode(rx_handle_, &std_cfg));
131:     ESP_LOGI(TAG, "Duplex channels created");
132: }
133: 
134: 
135: NoAudioCodecSimplex::NoAudioCodecSimplex(int input_sample_rate, int output_sample_rate, gpio_num_t spk_bclk, gpio_num_t spk_ws, gpio_num_t spk_dout, gpio_num_t mic_sck, gpio_num_t mic_ws, gpio_num_t mic_din) {
136:     duplex_ = false;
137:     input_sample_rate_ = input_sample_rate;
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第138-149行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
138:     output_sample_rate_ = output_sample_rate;
139: 
140:     // Create a new channel for speaker
141:     i2s_chan_config_t chan_cfg = {
142:         .id = (i2s_port_t)0,
143:         .role = I2S_ROLE_MASTER,
144:         .dma_desc_num = 6,
145:         .dma_frame_num = 240,
146:         .auto_clear_after_cb = true,
147:         .auto_clear_before_cb = false,
148:         .intr_priority = 0,
149:     };
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第150-161行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
150:     ESP_ERROR_CHECK(i2s_new_channel(&chan_cfg, &tx_handle_, nullptr));
151: 
152:     i2s_std_config_t std_cfg = {
153:         .clk_cfg = {
154:             .sample_rate_hz = (uint32_t)output_sample_rate_,
155:             .clk_src = I2S_CLK_SRC_DEFAULT,
156:             .mclk_multiple = I2S_MCLK_MULTIPLE_256,
157: 			#ifdef   I2S_HW_VERSION_2
158: 				.ext_clk_freq_hz = 0,
159: 			#endif
160: 
161:         },
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第162-170行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
162:         .slot_cfg = {
163:             .data_bit_width = I2S_DATA_BIT_WIDTH_32BIT,
164:             .slot_bit_width = I2S_SLOT_BIT_WIDTH_AUTO,
165:             .slot_mode = I2S_SLOT_MODE_MONO,
166:             .slot_mask = I2S_STD_SLOT_LEFT,
167:             .ws_width = I2S_DATA_BIT_WIDTH_32BIT,
168:             .ws_pol = false,
169:             .bit_shift = true,
170:             #ifdef   I2S_HW_VERSION_2
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第171-183行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
171:                 .left_align = true,
172:                 .big_endian = false,
173:                 .bit_order_lsb = false
174:             #endif
175: 
176:         },
177:         .gpio_cfg = {
178:             .mclk = I2S_GPIO_UNUSED,
179:             .bclk = spk_bclk,
180:             .ws = spk_ws,
181:             .dout = spk_dout,
182:             .din = I2S_GPIO_UNUSED,
183:             .invert_flags = {
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第184-194行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
184:                 .mclk_inv = false,
185:                 .bclk_inv = false,
186:                 .ws_inv = false
187:             }
188:         }
189:     };
190:     ESP_ERROR_CHECK(i2s_channel_init_std_mode(tx_handle_, &std_cfg));
191: 
192:     // Create a new channel for MIC
193:     chan_cfg.id = (i2s_port_t)1;
194:     ESP_ERROR_CHECK(i2s_new_channel(&chan_cfg, nullptr, &rx_handle_));
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第195-203行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
195:     std_cfg.clk_cfg.sample_rate_hz = (uint32_t)input_sample_rate_;
196:     std_cfg.gpio_cfg.bclk = mic_sck;
197:     std_cfg.gpio_cfg.ws = mic_ws;
198:     std_cfg.gpio_cfg.dout = I2S_GPIO_UNUSED;
199:     std_cfg.gpio_cfg.din = mic_din;
200:     ESP_ERROR_CHECK(i2s_channel_init_std_mode(rx_handle_, &std_cfg));
201:     ESP_LOGI(TAG, "Simplex channels created");
202: }
203: 
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第204-208行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
204: NoAudioCodecSimplex::NoAudioCodecSimplex(int input_sample_rate, int output_sample_rate, gpio_num_t spk_bclk, gpio_num_t spk_ws, gpio_num_t spk_dout, i2s_std_slot_mask_t spk_slot_mask, gpio_num_t mic_sck, gpio_num_t mic_ws, gpio_num_t mic_din, i2s_std_slot_mask_t mic_slot_mask){
205:     duplex_ = false;
206:     input_sample_rate_ = input_sample_rate;
207:     output_sample_rate_ = output_sample_rate;
208: 
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第209-220行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
209:     // Create a new channel for speaker
210:     i2s_chan_config_t chan_cfg = {
211:         .id = (i2s_port_t)0,
212:         .role = I2S_ROLE_MASTER,
213:         .dma_desc_num = 6,
214:         .dma_frame_num = 240,
215:         .auto_clear_after_cb = true,
216:         .auto_clear_before_cb = false,
217:         .intr_priority = 0,
218:     };
219:     ESP_ERROR_CHECK(i2s_new_channel(&chan_cfg, &tx_handle_, nullptr));
220: 
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第221-232行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
221:     i2s_std_config_t std_cfg = {
222:         .clk_cfg = {
223:             .sample_rate_hz = (uint32_t)output_sample_rate_,
224:             .clk_src = I2S_CLK_SRC_DEFAULT,
225:             .mclk_multiple = I2S_MCLK_MULTIPLE_256,
226: 			#ifdef   I2S_HW_VERSION_2
227: 				.ext_clk_freq_hz = 0,
228: 			#endif
229: 
230:         },
231:         .slot_cfg = {
232:             .data_bit_width = I2S_DATA_BIT_WIDTH_32BIT,
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第233-241行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
233:             .slot_bit_width = I2S_SLOT_BIT_WIDTH_AUTO,
234:             .slot_mode = I2S_SLOT_MODE_MONO,
235:             .slot_mask = spk_slot_mask,
236:             .ws_width = I2S_DATA_BIT_WIDTH_32BIT,
237:             .ws_pol = false,
238:             .bit_shift = true,
239:             #ifdef   I2S_HW_VERSION_2
240:                 .left_align = true,
241:                 .big_endian = false,
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第242-254行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
242:                 .bit_order_lsb = false
243:             #endif
244: 
245:         },
246:         .gpio_cfg = {
247:             .mclk = I2S_GPIO_UNUSED,
248:             .bclk = spk_bclk,
249:             .ws = spk_ws,
250:             .dout = spk_dout,
251:             .din = I2S_GPIO_UNUSED,
252:             .invert_flags = {
253:                 .mclk_inv = false,
254:                 .bclk_inv = false,
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第255-264行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
255:                 .ws_inv = false
256:             }
257:         }
258:     };
259:     ESP_ERROR_CHECK(i2s_channel_init_std_mode(tx_handle_, &std_cfg));
260: 
261:     // Create a new channel for MIC
262:     chan_cfg.id = (i2s_port_t)1;
263:     ESP_ERROR_CHECK(i2s_new_channel(&chan_cfg, nullptr, &rx_handle_));
264:     std_cfg.clk_cfg.sample_rate_hz = (uint32_t)input_sample_rate_;
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第265-273行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
265:     std_cfg.slot_cfg.slot_mask = mic_slot_mask;
266:     std_cfg.gpio_cfg.bclk = mic_sck;
267:     std_cfg.gpio_cfg.ws = mic_ws;
268:     std_cfg.gpio_cfg.dout = I2S_GPIO_UNUSED;
269:     std_cfg.gpio_cfg.din = mic_din;
270:     ESP_ERROR_CHECK(i2s_channel_init_std_mode(rx_handle_, &std_cfg));
271:     ESP_LOGI(TAG, "Simplex channels created");
272: }
273: 
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第274-279行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
274: NoAudioCodecSimplexPdm::NoAudioCodecSimplexPdm(int input_sample_rate, int output_sample_rate, gpio_num_t spk_bclk, gpio_num_t spk_ws, gpio_num_t spk_dout, gpio_num_t mic_sck, gpio_num_t mic_din) {
275:     duplex_ = false;
276:     input_sample_rate_ = input_sample_rate;
277:     output_sample_rate_ = output_sample_rate;
278: 
279:     // Create a new channel for speaker
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第280-288行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
280:     i2s_chan_config_t tx_chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG((i2s_port_t)1, I2S_ROLE_MASTER);
281:     tx_chan_cfg.dma_desc_num = 6;
282:     tx_chan_cfg.dma_frame_num = 240;
283:     tx_chan_cfg.auto_clear_after_cb = true;
284:     tx_chan_cfg.auto_clear_before_cb = false;
285:     tx_chan_cfg.intr_priority = 0;
286:     ESP_ERROR_CHECK(i2s_new_channel(&tx_chan_cfg, &tx_handle_, NULL));
287: 
288: 
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第289-298行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
289:     i2s_std_config_t tx_std_cfg = {
290:         .clk_cfg = {
291:             .sample_rate_hz = (uint32_t)output_sample_rate_,
292:             .clk_src = I2S_CLK_SRC_DEFAULT,
293:             .mclk_multiple = I2S_MCLK_MULTIPLE_256,
294: 			#ifdef   I2S_HW_VERSION_2
295: 				.ext_clk_freq_hz = 0,
296: 			#endif
297: 
298:         },
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第299-308行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
299:         .slot_cfg = I2S_STD_MSB_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO),
300:         .gpio_cfg = {
301:             .mclk = I2S_GPIO_UNUSED,
302:             .bclk = spk_bclk,
303:             .ws = spk_ws,
304:             .dout = spk_dout,
305:             .din = I2S_GPIO_UNUSED,
306:             .invert_flags = {
307:                 .mclk_inv = false,
308:                 .bclk_inv = false,
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第309-317行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
309:                 .ws_inv   = false,
310:             },
311:         },
312:     };
313:     ESP_ERROR_CHECK(i2s_channel_init_std_mode(tx_handle_, &tx_std_cfg));
314: #if SOC_I2S_SUPPORTS_PDM_RX
315:     // Create a new channel for MIC in PDM mode
316:     i2s_chan_config_t rx_chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG((i2s_port_t)0, I2S_ROLE_MASTER);
317:     ESP_ERROR_CHECK(i2s_new_channel(&rx_chan_cfg, NULL, &rx_handle_));
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第318-326行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
318:     i2s_pdm_rx_config_t pdm_rx_cfg = {
319:         .clk_cfg = I2S_PDM_RX_CLK_DEFAULT_CONFIG((uint32_t)input_sample_rate_),
320:         /* The data bit-width of PDM mode is fixed to 16 */
321:         .slot_cfg = I2S_PDM_RX_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_MONO),
322:         .gpio_cfg = {
323:             .clk = mic_sck,
324:             .din = mic_din,
325: 
326:             .invert_flags = {
```

## no_audio_codec.cc | 文件开头/全局定义 | 原文件第327-337行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
327:                 .clk_inv = false,
328:             },
329:         },
330:     };
331:     ESP_ERROR_CHECK(i2s_channel_init_pdm_rx_mode(rx_handle_, &pdm_rx_cfg));
332: #else
333:     ESP_LOGE(TAG, "PDM is not supported");
334: #endif
335:     ESP_LOGI(TAG, "Simplex channels created");
336: }
337: 
```

## no_audio_codec.cc | NoAudioCodec::Write | 原文件第338-346行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
338: int NoAudioCodec::Write(const int16_t* data, int samples) {
339:     std::vector<int32_t> buffer(samples);
340: 
341:     // output_volume_: 0-100
342:     // volume_factor_: 0-65536
343:     int32_t volume_factor = pow(double(output_volume_) / 100.0, 2) * 65536;
344:     for (int i = 0; i < samples; i++) {
345:         int64_t temp = int64_t(data[i]) * volume_factor; // 使用 int64_t 进行乘法运算
346:         if (temp > INT32_MAX) {
```

## no_audio_codec.cc | NoAudioCodec::Write | 原文件第347-356行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
347:             buffer[i] = INT32_MAX;
348:         } else if (temp < INT32_MIN) {
349:             buffer[i] = INT32_MIN;
350:         } else {
351:             buffer[i] = static_cast<int32_t>(temp);
352:         }
353:     }
354: 
355:     size_t bytes_written;
356:     ESP_ERROR_CHECK(i2s_channel_write(tx_handle_, buffer.data(), samples * sizeof(int32_t), &bytes_written, portMAX_DELAY));
```

## no_audio_codec.cc | NoAudioCodec::Write | 原文件第357-359行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
357:     return bytes_written / sizeof(int32_t);
358: }
359: 
```

## no_audio_codec.cc | NoAudioCodec::Read | 原文件第360-369行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
360: int NoAudioCodec::Read(int16_t* dest, int samples) {
361:     size_t bytes_read;
362: 
363:     std::vector<int32_t> bit32_buffer(samples);
364:     if (i2s_channel_read(rx_handle_, bit32_buffer.data(), samples * sizeof(int32_t), &bytes_read, portMAX_DELAY) != ESP_OK) {
365:         ESP_LOGE(TAG, "Read Failed!");
366:         return 0;
367:     }
368: 
369:     samples = bytes_read / sizeof(int32_t);
```

## no_audio_codec.cc | NoAudioCodec::Read | 原文件第370-376行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
370:     for (int i = 0; i < samples; i++) {
371:         int32_t value = bit32_buffer[i] >> 12;
372:         dest[i] = (value > INT16_MAX) ? INT16_MAX : (value < -INT16_MAX) ? -INT16_MAX : (int16_t)value;
373:     }
374:     return samples;
375: }
376: 
```

## no_audio_codec.cc | NoAudioCodecSimplexPdm::Read | 原文件第377-387行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
377: int NoAudioCodecSimplexPdm::Read(int16_t* dest, int samples) {
378:     size_t bytes_read;
379: 
380:     // PDM 解调后的数据位宽为 16 位
381:     std::vector<int16_t> bit16_buffer(samples);
382:     if (i2s_channel_read(rx_handle_, bit16_buffer.data(), samples * sizeof(int16_t), &bytes_read, portMAX_DELAY) != ESP_OK) {
383:         ESP_LOGE(TAG, "Read Failed!");
384:         return 0;
385:     }
386: 
387:     // 计算实际读取的样本数
```

## no_audio_codec.cc | NoAudioCodecSimplexPdm::Read | 原文件第388-394行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.cc
以下为原始源码，不是截图OCR。
```
388:     samples = bytes_read / sizeof(int16_t);
389: 
390:     // 将 16 位数据直接复制到目标缓冲区
391:     memcpy(dest, bit16_buffer.data(), samples * sizeof(int16_t));
392: 
393:     return samples;
394: }
```

## no_audio_codec.h | 文件开头/全局定义 | 原文件第1-17行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.h
以下为原始源码，不是截图OCR。
```
1: #ifndef _NO_AUDIO_CODEC_H
2: #define _NO_AUDIO_CODEC_H
3: 
4: #include "audio_codec.h"
5: 
6: #include <driver/gpio.h>
7: #include <driver/i2s_pdm.h>
8: 
9: class NoAudioCodec : public AudioCodec {
10: private:
11:     virtual int Write(const int16_t* data, int samples) override;
12:     virtual int Read(int16_t* dest, int samples) override;
13: 
14: public:
15:     virtual ~NoAudioCodec();
16: };
17: 
```

## no_audio_codec.h | 文件开头/全局定义 | 原文件第18-26行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.h
以下为原始源码，不是截图OCR。
```
18: class NoAudioCodecDuplex : public NoAudioCodec {
19: public:
20:     NoAudioCodecDuplex(int input_sample_rate, int output_sample_rate, gpio_num_t bclk, gpio_num_t ws, gpio_num_t dout, gpio_num_t din);
21: };
22: 
23: class ATK_NoAudioCodecDuplex : public NoAudioCodec {
24: public:
25:     ATK_NoAudioCodecDuplex(int input_sample_rate, int output_sample_rate, gpio_num_t bclk, gpio_num_t ws, gpio_num_t dout, gpio_num_t din);
26: };
```

## no_audio_codec.h | 文件开头/全局定义 | 原文件第27-30行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.h
以下为原始源码，不是截图OCR。
```
27: 
28: class NoAudioCodecSimplex : public NoAudioCodec {
29: public:
30:     NoAudioCodecSimplex(int input_sample_rate, int output_sample_rate, gpio_num_t spk_bclk, gpio_num_t spk_ws, gpio_num_t spk_dout, gpio_num_t mic_sck, gpio_num_t mic_ws, gpio_num_t mic_din);
```

## no_audio_codec.h | 文件开头/全局定义 | 原文件第31-35行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.h
以下为原始源码，不是截图OCR。
```
31:     NoAudioCodecSimplex(int input_sample_rate, int output_sample_rate, gpio_num_t spk_bclk, gpio_num_t spk_ws, gpio_num_t spk_dout, i2s_std_slot_mask_t spk_slot_mask, gpio_num_t mic_sck, gpio_num_t mic_ws, gpio_num_t mic_din, i2s_std_slot_mask_t mic_slot_mask);
32: };
33: 
34: class NoAudioCodecSimplexPdm : public NoAudioCodec {
35: public:
```

## no_audio_codec.h | 文件开头/全局定义 | 原文件第36-40行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_codecs/no_audio_codec.h
以下为原始源码，不是截图OCR。
```
36:     NoAudioCodecSimplexPdm(int input_sample_rate, int output_sample_rate, gpio_num_t spk_bclk, gpio_num_t spk_ws, gpio_num_t spk_dout, gpio_num_t mic_sck,  gpio_num_t mic_din);
37:     int Read(int16_t* dest, int samples);
38: };
39: 
40: #endif // _NO_AUDIO_CODEC_H
```

## audio_processor.cc | 文件开头/全局定义 | 原文件第1-8行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/audio_processor.cc
以下为原始源码，不是截图OCR。
```
1: #include "audio_processor.h"
2: #include <esp_log.h>
3: 
4: #define PROCESSOR_RUNNING 0x01
5: 
6: static const char* TAG = "AudioProcessor";
7: 
8: AudioProcessor::AudioProcessor()
```

## audio_processor.cc | afe_communication_data_ | 原文件第9-12行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/audio_processor.cc
以下为原始源码，不是截图OCR。
```
9:     : afe_communication_data_(nullptr) {
10:     event_group_ = xEventGroupCreate();
11: }
12: 
```

## audio_processor.cc | AudioProcessor::Initialize | 原文件第13-24行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/audio_processor.cc
以下为原始源码，不是截图OCR。
```
13: void AudioProcessor::Initialize(int channels, bool reference) {
14:     channels_ = channels;
15:     reference_ = reference;
16:     int ref_num = reference_ ? 1 : 0;
17: 
18:     afe_config_t afe_config = {
19:         .aec_init = false,
20:         .se_init = true,
21:         .vad_init = false,
22:         .wakenet_init = false,
23:         .voice_communication_init = true,
24:         .voice_communication_agc_init = true,
```

## audio_processor.cc | AudioProcessor::Initialize | 原文件第25-34行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/audio_processor.cc
以下为原始源码，不是截图OCR。
```
25:         .voice_communication_agc_gain = 10,
26:         .vad_mode = VAD_MODE_3,
27:         .wakenet_model_name = NULL,
28:         .wakenet_model_name_2 = NULL,
29:         .wakenet_mode = DET_MODE_90,
30:         .afe_mode = SR_MODE_HIGH_PERF,
31:         .afe_perferred_core = 1,
32:         .afe_perferred_priority = 1,
33:         .afe_ringbuf_size = 50,
34:         .memory_alloc_mode = AFE_MEMORY_ALLOC_MORE_PSRAM,
```

## audio_processor.cc | AudioProcessor::Initialize | 原文件第35-44行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/audio_processor.cc
以下为原始源码，不是截图OCR。
```
35:         .afe_linear_gain = 1.0,
36:         .agc_mode = AFE_MN_PEAK_AGC_MODE_2,
37:         .pcm_config = {
38:             .total_ch_num = channels_,
39:             .mic_num = channels_ - ref_num,
40:             .ref_num = ref_num,
41:             .sample_rate = 16000,
42:         },
43:         .debug_init = false,
44:         .debug_hook = {{ AFE_DEBUG_HOOK_MASE_TASK_IN, NULL }, { AFE_DEBUG_HOOK_FETCH_TASK_IN, NULL }},
```

## audio_processor.cc | AudioProcessor::Initialize | 原文件第45-55行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/audio_processor.cc
以下为原始源码，不是截图OCR。
```
45:         .afe_ns_mode = NS_MODE_SSP,
46:         .afe_ns_model_name = NULL,
47:         .fixed_first_channel = true,
48:     };
49: 
50:     afe_communication_data_ = esp_afe_vc_v1.create_from_config(&afe_config);
51:     
52:     xTaskCreate([](void* arg) {
53:         auto this_ = (AudioProcessor*)arg;
54:         this_->AudioProcessorTask();
55:         vTaskDelete(NULL);
```

## audio_processor.cc | AudioProcessor::Initialize | 原文件第56-65行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/audio_processor.cc
以下为原始源码，不是截图OCR。
```
56:     }, "audio_communication", 4096 * 2, this, 2, NULL);
57: }
58: 
59: AudioProcessor::~AudioProcessor() {
60:     if (afe_communication_data_ != nullptr) {
61:         esp_afe_vc_v1.destroy(afe_communication_data_);
62:     }
63:     vEventGroupDelete(event_group_);
64: }
65: 
```

## audio_processor.cc | AudioProcessor::Input | 原文件第66-72行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/audio_processor.cc
以下为原始源码，不是截图OCR。
```
66: void AudioProcessor::Input(const std::vector<int16_t>& data) {
67:     input_buffer_.insert(input_buffer_.end(), data.begin(), data.end());
68: 
69:     auto feed_size = esp_afe_vc_v1.get_feed_chunksize(afe_communication_data_) * channels_;
70:     while (input_buffer_.size() >= feed_size) {
71:         auto chunk = input_buffer_.data();
72:         esp_afe_vc_v1.feed(afe_communication_data_, chunk);
```

## audio_processor.cc | AudioProcessor::Input | 原文件第73-76行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/audio_processor.cc
以下为原始源码，不是截图OCR。
```
73:         input_buffer_.erase(input_buffer_.begin(), input_buffer_.begin() + feed_size);
74:     }
75: }
76: 
```

## audio_processor.cc | AudioProcessor::Start | 原文件第77-80行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/audio_processor.cc
以下为原始源码，不是截图OCR。
```
77: void AudioProcessor::Start() {
78:     xEventGroupSetBits(event_group_, PROCESSOR_RUNNING);
79: }
80: 
```

## audio_processor.cc | AudioProcessor::Stop | 原文件第81-84行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/audio_processor.cc
以下为原始源码，不是截图OCR。
```
81: void AudioProcessor::Stop() {
82:     xEventGroupClearBits(event_group_, PROCESSOR_RUNNING);
83: }
84: 
```

## audio_processor.cc | AudioProcessor::IsRunning | 原文件第85-88行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/audio_processor.cc
以下为原始源码，不是截图OCR。
```
85: bool AudioProcessor::IsRunning() {
86:     return xEventGroupGetBits(event_group_) & PROCESSOR_RUNNING;
87: }
88: 
```

## audio_processor.cc | AudioProcessor::OnOutput | 原文件第89-92行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/audio_processor.cc
以下为原始源码，不是截图OCR。
```
89: void AudioProcessor::OnOutput(std::function<void(std::vector<int16_t>&& data)> callback) {
90:     output_callback_ = callback;
91: }
92: 
```

## audio_processor.cc | AudioProcessor::AudioProcessorTask | 原文件第93-99行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/audio_processor.cc
以下为原始源码，不是截图OCR。
```
93: void AudioProcessor::AudioProcessorTask() {
94:     auto fetch_size = esp_afe_sr_v1.get_fetch_chunksize(afe_communication_data_);
95:     auto feed_size = esp_afe_sr_v1.get_feed_chunksize(afe_communication_data_);
96:     ESP_LOGI(TAG, "Audio communication task started, feed size: %d fetch size: %d",
97:         feed_size, fetch_size);
98: 
99:     while (true) {
```

## audio_processor.cc | AudioProcessor::AudioProcessorTask | 原文件第100-107行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/audio_processor.cc
以下为原始源码，不是截图OCR。
```
100:         xEventGroupWaitBits(event_group_, PROCESSOR_RUNNING, pdFALSE, pdTRUE, portMAX_DELAY);
101: 
102:         auto res = esp_afe_vc_v1.fetch(afe_communication_data_);
103:         if ((xEventGroupGetBits(event_group_) & PROCESSOR_RUNNING) == 0) {
104:             continue;
105:         }
106:         if (res == nullptr || res->ret_value == ESP_FAIL) {
107:             if (res != nullptr) {
```

## audio_processor.cc | AudioProcessor::AudioProcessorTask | 原文件第108-117行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/audio_processor.cc
以下为原始源码，不是截图OCR。
```
108:                 ESP_LOGI(TAG, "Error code: %d", res->ret_value);
109:             }
110:             continue;
111:         }
112: 
113:         if (output_callback_) {
114:             output_callback_(std::vector<int16_t>(res->data, res->data + res->data_size / sizeof(int16_t)));
115:         }
116:     }
117: }
```

## audio_processor.h | 文件开头/全局定义 | 原文件第1-18行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/audio_processor.h
以下为原始源码，不是截图OCR。
```
1: #ifndef AUDIO_PROCESSOR_H
2: #define AUDIO_PROCESSOR_H
3: 
4: #include <esp_afe_sr_models.h>
5: #include <freertos/FreeRTOS.h>
6: #include <freertos/task.h>
7: #include <freertos/event_groups.h>
8: 
9: #include <string>
10: #include <vector>
11: #include <functional>
12: 
13: class AudioProcessor {
14: public:
15:     AudioProcessor();
16:     ~AudioProcessor();
17: 
18:     void Initialize(int channels, bool reference);
```

## audio_processor.h | 文件开头/全局定义 | 原文件第19-28行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/audio_processor.h
以下为原始源码，不是截图OCR。
```
19:     void Input(const std::vector<int16_t>& data);
20:     void Start();
21:     void Stop();
22:     bool IsRunning();
23:     void OnOutput(std::function<void(std::vector<int16_t>&& data)> callback);
24: 
25: private:
26:     EventGroupHandle_t event_group_ = nullptr;
27:     esp_afe_sr_data_t* afe_communication_data_ = nullptr;
28:     std::vector<int16_t> input_buffer_;
```

## audio_processor.h | 文件开头/全局定义 | 原文件第29-36行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/audio_processor.h
以下为原始源码，不是截图OCR。
```
29:     std::function<void(std::vector<int16_t>&& data)> output_callback_;
30:     int channels_;
31:     bool reference_;
32: 
33:     void AudioProcessorTask();
34: };
35: 
36: #endif
```

## wake_word_detect.cc | 文件开头/全局定义 | 原文件第1-17行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
1: #include "wake_word_detect.h"
2: #include "application.h"
3: 
4: #include <esp_log.h>
5: #include <model_path.h>
6: #include <arpa/inet.h>
7: #include <sstream>
8: 
9: #define DETECTION_RUNNING_EVENT 1
10: 
11: static const char* TAG = "WakeWordDetect";
12: 
13: WakeWordDetect::WakeWordDetect()
14:     : afe_detection_data_(nullptr),
15:       wake_word_pcm_(),
16:       wake_word_opus_() {
17: 
```

## wake_word_detect.cc | 文件开头/全局定义 | 原文件第18-32行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
18:     event_group_ = xEventGroupCreate();
19: }
20: 
21: WakeWordDetect::~WakeWordDetect() {
22:     if (afe_detection_data_ != nullptr) {
23:         esp_afe_sr_v1.destroy(afe_detection_data_);
24:     }
25: 
26:     if (wake_word_encode_task_stack_ != nullptr) {
27:         heap_caps_free(wake_word_encode_task_stack_);
28:     }
29: 
30:     vEventGroupDelete(event_group_);
31: }
32: 
```

## wake_word_detect.cc | WakeWordDetect::Initialize | 原文件第33-41行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
33: void WakeWordDetect::Initialize(int channels, bool reference) {
34:     channels_ = channels;
35:     reference_ = reference;
36:     int ref_num = reference_ ? 1 : 0;
37: 
38:     srmodel_list_t *models = esp_srmodel_init("model");
39:     for (int i = 0; i < models->num; i++) {
40:         ESP_LOGI(TAG, "Model %d: %s", i, models->model_name[i]);
41:         if (strstr(models->model_name[i], ESP_WN_PREFIX) != NULL) {
```

## wake_word_detect.cc | WakeWordDetect::Initialize | 原文件第42-52行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
42:             wakenet_model_ = models->model_name[i];
43:             auto words = esp_srmodel_get_wake_words(models, wakenet_model_);
44:             // split by ";" to get all wake words
45:             std::stringstream ss(words);
46:             std::string word;
47:             while (std::getline(ss, word, ';')) {
48:                 wake_words_.push_back(word);
49:             }
50:         }
51:     }
52: 
```

## wake_word_detect.cc | WakeWordDetect::Initialize | 原文件第53-63行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
53:     afe_config_t afe_config = {
54:         .aec_init = reference_,
55:         .se_init = true,
56:         .vad_init = true,
57:         .wakenet_init = true,
58:         .voice_communication_init = false,
59:         .voice_communication_agc_init = false,
60:         .voice_communication_agc_gain = 10,
61:         .vad_mode = VAD_MODE_3,
62:         .wakenet_model_name = wakenet_model_,
63:         .wakenet_model_name_2 = NULL,
```

## wake_word_detect.cc | WakeWordDetect::Initialize | 原文件第64-73行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
64:         .wakenet_mode = DET_MODE_90,
65:         .afe_mode = SR_MODE_HIGH_PERF,
66:         .afe_perferred_core = 1,
67:         .afe_perferred_priority = 1,
68:         .afe_ringbuf_size = 50,
69:         .memory_alloc_mode = AFE_MEMORY_ALLOC_MORE_PSRAM,
70:         .afe_linear_gain = 1.0,
71:         .agc_mode = AFE_MN_PEAK_AGC_MODE_2,
72:         .pcm_config = {
73:             .total_ch_num = channels_,
```

## wake_word_detect.cc | WakeWordDetect::Initialize | 原文件第74-84行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
74:             .mic_num = channels_ - ref_num,
75:             .ref_num = ref_num,
76:             .sample_rate = 16000
77:         },
78:         .debug_init = false,
79:         .debug_hook = {{ AFE_DEBUG_HOOK_MASE_TASK_IN, NULL }, { AFE_DEBUG_HOOK_FETCH_TASK_IN, NULL }},
80:         .afe_ns_mode = NS_MODE_SSP,
81:         .afe_ns_model_name = NULL,
82:         .fixed_first_channel = true,
83:     };
84: 
```

## wake_word_detect.cc | WakeWordDetect::Initialize | 原文件第85-93行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
85:     afe_detection_data_ = esp_afe_sr_v1.create_from_config(&afe_config);
86: 
87:     xTaskCreate([](void* arg) {
88:         auto this_ = (WakeWordDetect*)arg;
89:         this_->AudioDetectionTask();
90:         vTaskDelete(NULL);
91:     }, "audio_detection", 4096 * 2, this, 2, nullptr);
92: }
93: 
```

## wake_word_detect.cc | WakeWordDetect::OnWakeWordDetected | 原文件第94-97行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
94: void WakeWordDetect::OnWakeWordDetected(std::function<void(const std::string& wake_word)> callback) {
95:     wake_word_detected_callback_ = callback;
96: }
97: 
```

## wake_word_detect.cc | WakeWordDetect::OnVadStateChange | 原文件第98-101行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
98: void WakeWordDetect::OnVadStateChange(std::function<void(bool speaking)> callback) {
99:     vad_state_change_callback_ = callback;
100: }
101: 
```

## wake_word_detect.cc | WakeWordDetect::StartDetection | 原文件第102-105行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
102: void WakeWordDetect::StartDetection() {
103:     xEventGroupSetBits(event_group_, DETECTION_RUNNING_EVENT);
104: }
105: 
```

## wake_word_detect.cc | WakeWordDetect::StopDetection | 原文件第106-109行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
106: void WakeWordDetect::StopDetection() {
107:     xEventGroupClearBits(event_group_, DETECTION_RUNNING_EVENT);
108: }
109: 
```

## wake_word_detect.cc | WakeWordDetect::IsDetectionRunning | 原文件第110-113行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
110: bool WakeWordDetect::IsDetectionRunning() {
111:     return xEventGroupGetBits(event_group_) & DETECTION_RUNNING_EVENT;
112: }
113: 
```

## wake_word_detect.cc | WakeWordDetect::Feed | 原文件第114-119行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
114: void WakeWordDetect::Feed(const std::vector<int16_t>& data) {
115:     input_buffer_.insert(input_buffer_.end(), data.begin(), data.end());
116: 
117:     auto feed_size = esp_afe_sr_v1.get_feed_chunksize(afe_detection_data_) * channels_;
118:     while (input_buffer_.size() >= feed_size) {
119:         esp_afe_sr_v1.feed(afe_detection_data_, input_buffer_.data());
```

## wake_word_detect.cc | WakeWordDetect::Feed | 原文件第120-123行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
120:         input_buffer_.erase(input_buffer_.begin(), input_buffer_.begin() + feed_size);
121:     }
122: }
123: 
```

## wake_word_detect.cc | WakeWordDetect::AudioDetectionTask | 原文件第124-130行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
124: void WakeWordDetect::AudioDetectionTask() {
125:     auto fetch_size = esp_afe_sr_v1.get_fetch_chunksize(afe_detection_data_);
126:     auto feed_size = esp_afe_sr_v1.get_feed_chunksize(afe_detection_data_);
127:     ESP_LOGI(TAG, "Audio detection task started, feed size: %d fetch size: %d",
128:         feed_size, fetch_size);
129: 
130:     while (true) {
```

## wake_word_detect.cc | WakeWordDetect::AudioDetectionTask | 原文件第131-138行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
131:         xEventGroupWaitBits(event_group_, DETECTION_RUNNING_EVENT, pdFALSE, pdTRUE, portMAX_DELAY);
132: 
133:         auto res = esp_afe_sr_v1.fetch(afe_detection_data_);
134:         if (res == nullptr || res->ret_value == ESP_FAIL) {
135:             continue;;
136:         }
137: 
138:         // Store the wake word data for voice recognition, like who is speaking
```

## wake_word_detect.cc | WakeWordDetect::AudioDetectionTask | 原文件第139-146行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
139:         StoreWakeWordData((uint16_t*)res->data, res->data_size / sizeof(uint16_t));
140: 
141:         // VAD state change
142:         if (vad_state_change_callback_) {
143:             if (res->vad_state == AFE_VAD_SPEECH && !is_speaking_) {
144:                 is_speaking_ = true;
145:                 vad_state_change_callback_(true);
146:             } else if (res->vad_state == AFE_VAD_SILENCE && is_speaking_) {
```

## wake_word_detect.cc | WakeWordDetect::AudioDetectionTask | 原文件第147-156行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
147:                 is_speaking_ = false;
148:                 vad_state_change_callback_(false);
149:             }
150:         }
151: 
152:         if (res->wakeup_state == WAKENET_DETECTED) {
153:             StopDetection();
154:             last_detected_wake_word_ = wake_words_[res->wake_word_index - 1];
155: 
156:             if (wake_word_detected_callback_) {
```

## wake_word_detect.cc | WakeWordDetect::AudioDetectionTask | 原文件第157-162行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
157:                 wake_word_detected_callback_(last_detected_wake_word_);
158:             }
159:         }
160:     }
161: }
162: 
```

## wake_word_detect.cc | WakeWordDetect::StoreWakeWordData | 原文件第163-171行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
163: void WakeWordDetect::StoreWakeWordData(uint16_t* data, size_t samples) {
164:     // store audio data to wake_word_pcm_
165:     wake_word_pcm_.emplace_back(std::vector<int16_t>(data, data + samples));
166:     // keep about 2 seconds of data, detect duration is 32ms (sample_rate == 16000, chunksize == 512)
167:     while (wake_word_pcm_.size() > 2000 / 32) {
168:         wake_word_pcm_.pop_front();
169:     }
170: }
171: 
```

## wake_word_detect.cc | WakeWordDetect::EncodeWakeWordData | 原文件第172-179行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
172: void WakeWordDetect::EncodeWakeWordData() {
173:     wake_word_opus_.clear();
174:     if (wake_word_encode_task_stack_ == nullptr) {
175:         wake_word_encode_task_stack_ = (StackType_t*)heap_caps_malloc(4096 * 8, MALLOC_CAP_SPIRAM);
176:     }
177:     wake_word_encode_task_ = xTaskCreateStatic([](void* arg) {
178:         auto this_ = (WakeWordDetect*)arg;
179:         {
```

## wake_word_detect.cc | WakeWordDetect::EncodeWakeWordData | 原文件第180-185行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
180:             auto start_time = esp_timer_get_time();
181:             auto encoder = std::make_unique<OpusEncoderWrapper>(16000, 1, OPUS_FRAME_DURATION_MS);
182:             encoder->SetComplexity(0); // 0 is the fastest
183: 
184:             for (auto& pcm: this_->wake_word_pcm_) {
185:                 encoder->Encode(std::move(pcm), [this_](std::vector<uint8_t>&& opus) {
```

## wake_word_detect.cc | WakeWordDetect::EncodeWakeWordData | 原文件第186-193行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
186:                     std::lock_guard<std::mutex> lock(this_->wake_word_mutex_);
187:                     this_->wake_word_opus_.emplace_back(std::move(opus));
188:                     this_->wake_word_cv_.notify_all();
189:                 });
190:             }
191:             this_->wake_word_pcm_.clear();
192: 
193:             auto end_time = esp_timer_get_time();
```

## wake_word_detect.cc | WakeWordDetect::EncodeWakeWordData | 原文件第194-201行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
194:             ESP_LOGI(TAG, "Encode wake word opus %zu packets in %lld ms",
195:                 this_->wake_word_opus_.size(), (end_time - start_time) / 1000);
196: 
197:             std::lock_guard<std::mutex> lock(this_->wake_word_mutex_);
198:             this_->wake_word_opus_.push_back(std::vector<uint8_t>());
199:             this_->wake_word_cv_.notify_all();
200:         }
201:         vTaskDelete(NULL);
```

## wake_word_detect.cc | WakeWordDetect::EncodeWakeWordData | 原文件第202-204行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
202:     }, "encode_detect_packets", 4096 * 8, this, 2, wake_word_encode_task_stack_, &wake_word_encode_task_buffer_);
203: }
204: 
```

## wake_word_detect.cc | WakeWordDetect::GetWakeWordOpus | 原文件第205-213行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.cc
以下为原始源码，不是截图OCR。
```
205: bool WakeWordDetect::GetWakeWordOpus(std::vector<uint8_t>& opus) {
206:     std::unique_lock<std::mutex> lock(wake_word_mutex_);
207:     wake_word_cv_.wait(lock, [this]() {
208:         return !wake_word_opus_.empty();
209:     });
210:     opus.swap(wake_word_opus_.front());
211:     wake_word_opus_.pop_front();
212:     return !opus.empty();
213: }
```

## wake_word_detect.h | 文件开头/全局定义 | 原文件第1-20行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.h
以下为原始源码，不是截图OCR。
```
1: #ifndef WAKE_WORD_DETECT_H
2: #define WAKE_WORD_DETECT_H
3: 
4: #include <freertos/FreeRTOS.h>
5: #include <freertos/task.h>
6: #include <freertos/event_groups.h>
7: 
8: #include <esp_afe_sr_models.h>
9: #include <esp_nsn_models.h>
10: 
11: #include <list>
12: #include <string>
13: #include <vector>
14: #include <functional>
15: #include <mutex>
16: #include <condition_variable>
17: 
18: 
19: class WakeWordDetect {
20: public:
```

## wake_word_detect.h | 文件开头/全局定义 | 原文件第21-30行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.h
以下为原始源码，不是截图OCR。
```
21:     WakeWordDetect();
22:     ~WakeWordDetect();
23: 
24:     void Initialize(int channels, bool reference);
25:     void Feed(const std::vector<int16_t>& data);
26:     void OnWakeWordDetected(std::function<void(const std::string& wake_word)> callback);
27:     void OnVadStateChange(std::function<void(bool speaking)> callback);
28:     void StartDetection();
29:     void StopDetection();
30:     bool IsDetectionRunning();
```

## wake_word_detect.h | 文件开头/全局定义 | 原文件第31-40行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.h
以下为原始源码，不是截图OCR。
```
31:     void EncodeWakeWordData();
32:     bool GetWakeWordOpus(std::vector<uint8_t>& opus);
33:     const std::string& GetLastDetectedWakeWord() const { return last_detected_wake_word_; }
34: 
35: private:
36:     esp_afe_sr_data_t* afe_detection_data_ = nullptr;
37:     char* wakenet_model_ = NULL;
38:     std::vector<std::string> wake_words_;
39:     std::vector<int16_t> input_buffer_;
40:     EventGroupHandle_t event_group_;
```

## wake_word_detect.h | 文件开头/全局定义 | 原文件第41-49行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.h
以下为原始源码，不是截图OCR。
```
41:     std::function<void(const std::string& wake_word)> wake_word_detected_callback_;
42:     std::function<void(bool speaking)> vad_state_change_callback_;
43:     bool is_speaking_ = false;
44:     int channels_;
45:     bool reference_;
46:     std::string last_detected_wake_word_;
47: 
48:     TaskHandle_t wake_word_encode_task_ = nullptr;
49:     StaticTask_t wake_word_encode_task_buffer_;
```

## wake_word_detect.h | 文件开头/全局定义 | 原文件第50-60行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/audio_processing/wake_word_detect.h
以下为原始源码，不是截图OCR。
```
50:     StackType_t* wake_word_encode_task_stack_ = nullptr;
51:     std::list<std::vector<int16_t>> wake_word_pcm_;
52:     std::list<std::vector<uint8_t>> wake_word_opus_;
53:     std::mutex wake_word_mutex_;
54:     std::condition_variable wake_word_cv_;
55: 
56:     void StoreWakeWordData(uint16_t* data, size_t size);
57:     void AudioDetectionTask();
58: };
59: 
60: #endif
```

## background_task.cc | 文件开头/全局定义 | 原文件第1-14行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/background_task.cc
以下为原始源码，不是截图OCR。
```
1: #include "background_task.h"
2: 
3: #include <esp_log.h>
4: #include <esp_task_wdt.h>
5: 
6: #define TAG "BackgroundTask"
7: 
8: BackgroundTask::BackgroundTask(uint32_t stack_size) {
9:     xTaskCreate([](void* arg) {
10:         BackgroundTask* task = (BackgroundTask*)arg;
11:         task->BackgroundTaskLoop();
12:     }, "background_task", stack_size, this, 2, &background_task_handle_);
13: }
14: 
```

## background_task.cc | 文件开头/全局定义 | 原文件第15-20行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/background_task.cc
以下为原始源码，不是截图OCR。
```
15: BackgroundTask::~BackgroundTask() {
16:     if (background_task_handle_ != nullptr) {
17:         vTaskDelete(background_task_handle_);
18:     }
19: }
20: 
```

## background_task.cc | BackgroundTask::Schedule | 原文件第21-29行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/background_task.cc
以下为原始源码，不是截图OCR。
```
21: void BackgroundTask::Schedule(std::function<void()> callback) {
22:     std::lock_guard<std::mutex> lock(mutex_);
23:     if (active_tasks_ >= 30) {
24:         int free_sram = heap_caps_get_free_size(MALLOC_CAP_INTERNAL);
25:         if (free_sram < 10000) {
26:             ESP_LOGW(TAG, "active_tasks_ == %u, free_sram == %u", active_tasks_.load(), free_sram);
27:         }
28:     }
29:     active_tasks_++;
```

## background_task.cc | BackgroundTask::Schedule | 原文件第30-42行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/background_task.cc
以下为原始源码，不是截图OCR。
```
30:     main_tasks_.emplace_back([this, cb = std::move(callback)]() {
31:         cb();
32:         {
33:             std::lock_guard<std::mutex> lock(mutex_);
34:             active_tasks_--;
35:             if (main_tasks_.empty() && active_tasks_ == 0) {
36:                 condition_variable_.notify_all();
37:             }
38:         }
39:     });
40:     condition_variable_.notify_all();
41: }
42: 
```

## background_task.cc | BackgroundTask::WaitForCompletion | 原文件第43-49行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/background_task.cc
以下为原始源码，不是截图OCR。
```
43: void BackgroundTask::WaitForCompletion() {
44:     std::unique_lock<std::mutex> lock(mutex_);
45:     condition_variable_.wait(lock, [this]() {
46:         return main_tasks_.empty() && active_tasks_ == 0;
47:     });
48: }
49: 
```

## background_task.cc | BackgroundTask::BackgroundTaskLoop | 原文件第50-59行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/background_task.cc
以下为原始源码，不是截图OCR。
```
50: void BackgroundTask::BackgroundTaskLoop() {
51:     ESP_LOGI(TAG, "background_task started");
52:     while (true) {
53:         std::unique_lock<std::mutex> lock(mutex_);
54:         condition_variable_.wait(lock, [this]() { return !main_tasks_.empty(); });
55:         
56:         std::list<std::function<void()>> tasks = std::move(main_tasks_);
57:         lock.unlock();
58: 
59:         for (auto& task : tasks) {
```

## background_task.cc | BackgroundTask::BackgroundTaskLoop | 原文件第60-63行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/background_task.cc
以下为原始源码，不是截图OCR。
```
60:             task();
61:         }
62:     }
63: }
```

## background_task.h | 文件开头/全局定义 | 原文件第1-17行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/background_task.h
以下为原始源码，不是截图OCR。
```
1: #ifndef BACKGROUND_TASK_H
2: #define BACKGROUND_TASK_H
3: 
4: #include <freertos/FreeRTOS.h>
5: #include <freertos/task.h>
6: #include <mutex>
7: #include <list>
8: #include <condition_variable>
9: #include <atomic>
10: 
11: class BackgroundTask {
12: public:
13:     BackgroundTask(uint32_t stack_size = 4096 * 2);
14:     ~BackgroundTask();
15: 
16:     void Schedule(std::function<void()> callback);
17:     void WaitForCompletion();
```

## background_task.h | 文件开头/全局定义 | 原文件第18-29行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/background_task.h
以下为原始源码，不是截图OCR。
```
18: 
19: private:
20:     std::mutex mutex_;
21:     std::list<std::function<void()>> main_tasks_;
22:     std::condition_variable condition_variable_;
23:     TaskHandle_t background_task_handle_ = nullptr;
24:     std::atomic<size_t> active_tasks_{0};
25: 
26:     void BackgroundTaskLoop();
27: };
28: 
29: #endif
```

## axp2101.cc | 文件开头/全局定义 | 原文件第1-11行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/axp2101.cc
以下为原始源码，不是截图OCR。
```
1: #include "axp2101.h"
2: #include "board.h"
3: #include "display.h"
4: 
5: #include <esp_log.h>
6: 
7: #define TAG "Axp2101"
8: 
9: Axp2101::Axp2101(i2c_master_bus_handle_t i2c_bus, uint8_t addr) : I2cDevice(i2c_bus, addr) {
10: }
11: 
```

## axp2101.cc | Axp2101::GetBatteryCurrentDirection | 原文件第12-15行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/axp2101.cc
以下为原始源码，不是截图OCR。
```
12: int Axp2101::GetBatteryCurrentDirection() {
13:     return (ReadReg(0x01) & 0b01100000) >> 5;
14: }
15: 
```

## axp2101.cc | Axp2101::IsCharging | 原文件第16-19行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/axp2101.cc
以下为原始源码，不是截图OCR。
```
16: bool Axp2101::IsCharging() {
17:     return GetBatteryCurrentDirection() == 1;
18: }
19: 
```

## axp2101.cc | Axp2101::IsDischarging | 原文件第20-23行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/axp2101.cc
以下为原始源码，不是截图OCR。
```
20: bool Axp2101::IsDischarging() {
21:     return GetBatteryCurrentDirection() == 2;
22: }
23: 
```

## axp2101.cc | Axp2101::IsChargingDone | 原文件第24-28行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/axp2101.cc
以下为原始源码，不是截图OCR。
```
24: bool Axp2101::IsChargingDone() {
25:     uint8_t value = ReadReg(0x01);
26:     return (value & 0b00000111) == 0b00000100;
27: }
28: 
```

## axp2101.cc | Axp2101::GetBatteryLevel | 原文件第29-32行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/axp2101.cc
以下为原始源码，不是截图OCR。
```
29: int Axp2101::GetBatteryLevel() {
30:     return ReadReg(0xA4);
31: }
32: 
```

## axp2101.cc | Axp2101::PowerOff | 原文件第33-37行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/axp2101.cc
以下为原始源码，不是截图OCR。
```
33: void Axp2101::PowerOff() {
34:     uint8_t value = ReadReg(0x10);
35:     value = value | 0x01;
36:     WriteReg(0x10, value);
37: }
```

## axp2101.h | 文件开头/全局定义 | 原文件第1-19行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/axp2101.h
以下为原始源码，不是截图OCR。
```
1: #ifndef __AXP2101_H__
2: #define __AXP2101_H__
3: 
4: #include "i2c_device.h"
5: 
6: class Axp2101 : public I2cDevice {
7: public:
8:     Axp2101(i2c_master_bus_handle_t i2c_bus, uint8_t addr);
9:     bool IsCharging();
10:     bool IsDischarging();
11:     bool IsChargingDone();
12:     int GetBatteryLevel();
13:     void PowerOff();
14: 
15: private:
16:     int GetBatteryCurrentDirection();
17: };
18: 
19: #endif
```

## backlight.cc | 文件开头/全局定义 | 原文件第1-17行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/backlight.cc
以下为原始源码，不是截图OCR。
```
1: #include "backlight.h"
2: #include "settings.h"
3: 
4: #include <esp_log.h>
5: #include <driver/ledc.h>
6: 
7: #define TAG "Backlight"
8: 
9: 
10: Backlight::Backlight() {
11:     // 创建背光渐变定时器
12:     const esp_timer_create_args_t timer_args = {
13:         .callback = [](void* arg) {
14:             auto self = static_cast<Backlight*>(arg);
15:             self->OnTransitionTimer();
16:         },
17:         .arg = this,
```

## backlight.cc | 文件开头/全局定义 | 原文件第18-31行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/backlight.cc
以下为原始源码，不是截图OCR。
```
18:         .dispatch_method = ESP_TIMER_TASK,
19:         .name = "backlight_timer",
20:         .skip_unhandled_events = true,
21:     };
22:     ESP_ERROR_CHECK(esp_timer_create(&timer_args, &transition_timer_));
23: }
24: 
25: Backlight::~Backlight() {
26:     if (transition_timer_ != nullptr) {
27:         esp_timer_stop(transition_timer_);
28:         esp_timer_delete(transition_timer_);
29:     }
30: }
31: 
```

## backlight.cc | Backlight::RestoreBrightness | 原文件第32-37行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/backlight.cc
以下为原始源码，不是截图OCR。
```
32: void Backlight::RestoreBrightness() {
33:     // Load brightness from settings
34:     Settings settings("display");
35:     SetBrightness(settings.GetInt("brightness", 75));
36: }
37: 
```

## backlight.cc | Backlight::SetBrightness | 原文件第38-52行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/backlight.cc
以下为原始源码，不是截图OCR。
```
38: void Backlight::SetBrightness(uint8_t brightness, bool permanent) {
39:     if (brightness > 100) {
40:         brightness = 100;
41:     }
42: 
43:     if (brightness_ == brightness) {
44:         return;
45:     }
46: 
47:     if (permanent) {
48:         Settings settings("display", true);
49:         settings.SetInt("brightness", brightness);
50:     }
51: 
52:     target_brightness_ = brightness;
```

## backlight.cc | Backlight::SetBrightness | 原文件第53-61行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/backlight.cc
以下为原始源码，不是截图OCR。
```
53:     step_ = (target_brightness_ > brightness_) ? 1 : -1;
54: 
55:     if (transition_timer_ != nullptr) {
56:         // 启动定时器，每 5ms 更新一次
57:         esp_timer_start_periodic(transition_timer_, 5 * 1000);
58:     }
59:     ESP_LOGI(TAG, "Set brightness to %d", brightness);
60: }
61: 
```

## backlight.cc | Backlight::OnTransitionTimer | 原文件第62-75行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/backlight.cc
以下为原始源码，不是截图OCR。
```
62: void Backlight::OnTransitionTimer() {
63:     if (brightness_ == target_brightness_) {
64:         esp_timer_stop(transition_timer_);
65:         return;
66:     }
67: 
68:     brightness_ += step_;
69:     SetBrightnessImpl(brightness_);
70: 
71:     if (brightness_ == target_brightness_) {
72:         esp_timer_stop(transition_timer_);
73:     }
74: }
75: 
```

## backlight.cc | Backlight::OnTransitionTimer | 原文件第76-84行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/backlight.cc
以下为原始源码，不是截图OCR。
```
76: PwmBacklight::PwmBacklight(gpio_num_t pin, bool output_invert) : Backlight() {
77:     const ledc_timer_config_t backlight_timer = {
78:         .speed_mode = LEDC_LOW_SPEED_MODE,
79:         .duty_resolution = LEDC_TIMER_10_BIT,
80:         .timer_num = LEDC_TIMER_0,
81:         .freq_hz = 20000, //背光pwm频率需要高一点，防止电感啸叫
82:         .clk_cfg = LEDC_AUTO_CLK,
83:         .deconfigure = false
84:     };
```

## backlight.cc | Backlight::OnTransitionTimer | 原文件第85-95行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/backlight.cc
以下为原始源码，不是截图OCR。
```
85:     ESP_ERROR_CHECK(ledc_timer_config(&backlight_timer));
86: 
87:     // Setup LEDC peripheral for PWM backlight control
88:     const ledc_channel_config_t backlight_channel = {
89:         .gpio_num = pin,
90:         .speed_mode = LEDC_LOW_SPEED_MODE,
91:         .channel = LEDC_CHANNEL_0,
92:         .intr_type = LEDC_INTR_DISABLE,
93:         .timer_sel = LEDC_TIMER_0,
94:         .duty = 0,
95:         .hpoint = 0,
```

## backlight.cc | Backlight::OnTransitionTimer | 原文件第96-106行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/backlight.cc
以下为原始源码，不是截图OCR。
```
96:         .flags = {
97:             .output_invert = output_invert,
98:         }
99:     };
100:     ESP_ERROR_CHECK(ledc_channel_config(&backlight_channel));
101: }
102: 
103: PwmBacklight::~PwmBacklight() {
104:     ledc_stop(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 0);
105: }
106: 
```

## backlight.cc | PwmBacklight::SetBrightnessImpl | 原文件第107-113行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/backlight.cc
以下为原始源码，不是截图OCR。
```
107: void PwmBacklight::SetBrightnessImpl(uint8_t brightness) {
108:     // LEDC resolution set to 10bits, thus: 100% = 1023
109:     uint32_t duty_cycle = (1023 * brightness) / 100;
110:     ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, duty_cycle);
111:     ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
112: }
113: 
```

## backlight.h | 文件开头/全局定义 | 原文件第1-19行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/backlight.h
以下为原始源码，不是截图OCR。
```
1: #pragma once
2: 
3: #include <cstdint>
4: #include <functional>
5: 
6: #include <driver/gpio.h>
7: #include <esp_timer.h>
8: 
9: 
10: class Backlight {
11: public:
12:     Backlight();
13:     ~Backlight();
14: 
15:     void RestoreBrightness();
16:     void SetBrightness(uint8_t brightness, bool permanent = false);
17:     inline uint8_t brightness() const { return brightness_; }
18: 
19: protected:
```

## backlight.h | 文件开头/全局定义 | 原文件第20-34行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/backlight.h
以下为原始源码，不是截图OCR。
```
20:     void OnTransitionTimer();
21:     virtual void SetBrightnessImpl(uint8_t brightness) = 0;
22: 
23:     esp_timer_handle_t transition_timer_ = nullptr;
24:     uint8_t brightness_ = 0;
25:     uint8_t target_brightness_ = 0;
26:     uint8_t step_ = 1;
27: };
28: 
29: 
30: class PwmBacklight : public Backlight {
31: public:
32:     PwmBacklight(gpio_num_t pin, bool output_invert = false);
33:     ~PwmBacklight();
34: 
```

## backlight.h | 文件开头/全局定义 | 原文件第35-36行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/backlight.h
以下为原始源码，不是截图OCR。
```
35:     void SetBrightnessImpl(uint8_t brightness) override;
36: };
```

## board.cc | 文件开头/全局定义 | 原文件第1-17行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.cc
以下为原始源码，不是截图OCR。
```
1: #include "board.h"
2: #include "system_info.h"
3: #include "settings.h"
4: #include "display/display.h"
5: #include "assets/lang_config.h"
6: 
7: #include <esp_log.h>
8: #include <esp_ota_ops.h>
9: #include <esp_chip_info.h>
10: #include <esp_random.h>
11: 
12: #define TAG "Board"
13: 
14: Board::Board() {
15:     Settings settings("board", true);
16:     uuid_ = settings.GetString("uuid");
17:     if (uuid_.empty()) {
```

## board.cc | 文件开头/全局定义 | 原文件第18-23行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.cc
以下为原始源码，不是截图OCR。
```
18:         uuid_ = GenerateUuid();
19:         settings.SetString("uuid", uuid_);
20:     }
21:     ESP_LOGI(TAG, "UUID=%s SKU=%s", uuid_.c_str(), BOARD_NAME);
22: }
23: 
```

## board.cc | Board::GenerateUuid | 原文件第24-36行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.cc
以下为原始源码，不是截图OCR。
```
24: std::string Board::GenerateUuid() {
25:     // UUID v4 需要 16 字节的随机数据
26:     uint8_t uuid[16];
27:     
28:     // 使用 ESP32 的硬件随机数生成器
29:     esp_fill_random(uuid, sizeof(uuid));
30:     
31:     // 设置版本 (版本 4) 和变体位
32:     uuid[6] = (uuid[6] & 0x0F) | 0x40;    // 版本 4
33:     uuid[8] = (uuid[8] & 0x3F) | 0x80;    // 变体 1
34:     
35:     // 将字节转换为标准的 UUID 字符串格式
36:     char uuid_str[37];
```

## board.cc | Board::GenerateUuid | 原文件第37-46行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.cc
以下为原始源码，不是截图OCR。
```
37:     snprintf(uuid_str, sizeof(uuid_str),
38:         "%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x",
39:         uuid[0], uuid[1], uuid[2], uuid[3],
40:         uuid[4], uuid[5], uuid[6], uuid[7],
41:         uuid[8], uuid[9], uuid[10], uuid[11],
42:         uuid[12], uuid[13], uuid[14], uuid[15]);
43:     
44:     return std::string(uuid_str);
45: }
46: 
```

## board.cc | Board::GetBatteryLevel | 原文件第47-50行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.cc
以下为原始源码，不是截图OCR。
```
47: bool Board::GetBatteryLevel(int &level, bool& charging, bool& discharging) {
48:     return false;
49: }
50: 
```

## board.cc | Board::GetDisplay | 原文件第51-55行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.cc
以下为原始源码，不是截图OCR。
```
51: Display* Board::GetDisplay() {
52:     static NoDisplay display;
53:     return &display;
54: }
55: 
```

## board.cc | Board::GetLed | 原文件第56-60行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.cc
以下为原始源码，不是截图OCR。
```
56: Led* Board::GetLed() {
57:     static NoLed led;
58:     return &led;
59: }
60: 
```

## board.cc | Board::GetJson | 原文件第61-72行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.cc
以下为原始源码，不是截图OCR。
```
61: std::string Board::GetJson() {
62:     /* 
63:         {
64:             "version": 2,
65:             "flash_size": 4194304,
66:             "psram_size": 0,
67:             "minimum_free_heap_size": 123456,
68:             "mac_address": "00:00:00:00:00:00",
69:             "uuid": "00000000-0000-0000-0000-000000000000",
70:             "chip_model_name": "esp32s3",
71:             "chip_info": {
72:                 "model": 1,
```

## board.cc | Board::GetJson | 原文件第73-84行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.cc
以下为原始源码，不是截图OCR。
```
73:                 "cores": 2,
74:                 "revision": 0,
75:                 "features": 0
76:             },
77:             "application": {
78:                 "name": "my-app",
79:                 "version": "1.0.0",
80:                 "compile_time": "2021-01-01T00:00:00Z"
81:                 "idf_version": "4.2-dev"
82:                 "elf_sha256": ""
83:             },
84:             "partition_table": [
```

## board.cc | Board::GetJson | 原文件第85-99行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.cc
以下为原始源码，不是截图OCR。
```
85:                 "app": {
86:                     "label": "app",
87:                     "type": 1,
88:                     "subtype": 2,
89:                     "address": 0x10000,
90:                     "size": 0x100000
91:                 }
92:             ],
93:             "ota": {
94:                 "label": "ota_0"
95:             },
96:             "board": {
97:                 ...
98:             }
99:         }
```

## board.cc | Board::GetJson | 原文件第100-106行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.cc
以下为原始源码，不是截图OCR。
```
100:     */
101:     std::string json = "{";
102:     json += "\"version\":2,";
103:     json += "\"language\":\"" + std::string(Lang::CODE) + "\",";
104:     json += "\"flash_size\":" + std::to_string(SystemInfo::GetFlashSize()) + ",";
105:     json += "\"minimum_free_heap_size\":" + std::to_string(SystemInfo::GetMinimumFreeHeapSize()) + ",";
106:     json += "\"mac_address\":\"" + SystemInfo::GetMacAddress() + "\",";
```

## board.cc | Board::GetJson | 原文件第107-114行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.cc
以下为原始源码，不是截图OCR。
```
107:     json += "\"uuid\":\"" + uuid_ + "\",";
108:     json += "\"chip_model_name\":\"" + SystemInfo::GetChipModelName() + "\",";
109:     json += "\"chip_info\":{";
110: 
111:     esp_chip_info_t chip_info;
112:     esp_chip_info(&chip_info);
113:     json += "\"model\":" + std::to_string(chip_info.model) + ",";
114:     json += "\"cores\":" + std::to_string(chip_info.cores) + ",";
```

## board.cc | Board::GetJson | 原文件第115-122行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.cc
以下为原始源码，不是截图OCR。
```
115:     json += "\"revision\":" + std::to_string(chip_info.revision) + ",";
116:     json += "\"features\":" + std::to_string(chip_info.features);
117:     json += "},";
118: 
119:     json += "\"application\":{";
120:     auto app_desc = esp_app_get_description();
121:     json += "\"name\":\"" + std::string(app_desc->project_name) + "\",";
122:     json += "\"version\":\"" + std::string(app_desc->version) + "\",";
```

## board.cc | Board::GetJson | 原文件第123-129行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.cc
以下为原始源码，不是截图OCR。
```
123:     json += "\"compile_time\":\"" + std::string(app_desc->date) + "T" + std::string(app_desc->time) + "Z\",";
124:     json += "\"idf_version\":\"" + std::string(app_desc->idf_ver) + "\",";
125: 
126:     char sha256_str[65];
127:     for (int i = 0; i < 32; i++) {
128:         snprintf(sha256_str + i * 2, sizeof(sha256_str) - i * 2, "%02x", app_desc->app_elf_sha256[i]);
129:     }
```

## board.cc | Board::GetJson | 原文件第130-137行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.cc
以下为原始源码，不是截图OCR。
```
130:     json += "\"elf_sha256\":\"" + std::string(sha256_str) + "\"";
131:     json += "},";
132: 
133:     json += "\"partition_table\": [";
134:     esp_partition_iterator_t it = esp_partition_find(ESP_PARTITION_TYPE_ANY, ESP_PARTITION_SUBTYPE_ANY, NULL);
135:     while (it) {
136:         const esp_partition_t *partition = esp_partition_get(it);
137:         json += "{";
```

## board.cc | Board::GetJson | 原文件第138-143行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.cc
以下为原始源码，不是截图OCR。
```
138:         json += "\"label\":\"" + std::string(partition->label) + "\",";
139:         json += "\"type\":" + std::to_string(partition->type) + ",";
140:         json += "\"subtype\":" + std::to_string(partition->subtype) + ",";
141:         json += "\"address\":" + std::to_string(partition->address) + ",";
142:         json += "\"size\":" + std::to_string(partition->size);
143:         json += "},";
```

## board.cc | Board::GetJson | 原文件第144-156行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.cc
以下为原始源码，不是截图OCR。
```
144:         it = esp_partition_next(it);
145:     }
146:     json.pop_back(); // Remove the last comma
147:     json += "],";
148: 
149:     json += "\"ota\":{";
150:     auto ota_partition = esp_ota_get_running_partition();
151:     json += "\"label\":\"" + std::string(ota_partition->label) + "\"";
152:     json += "},";
153: 
154:     json += "\"board\":" + GetBoardJson();
155: 
156:     // Close the JSON object
```

## board.cc | Board::GetJson | 原文件第157-159行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.cc
以下为原始源码，不是截图OCR。
```
157:     json += "}";
158:     return json;
159: }
```

## board.h | 文件开头/全局定义 | 原文件第1-19行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.h
以下为原始源码，不是截图OCR。
```
1: #ifndef BOARD_H
2: #define BOARD_H
3: 
4: #include <http.h>
5: #include <web_socket.h>
6: #include <mqtt.h>
7: #include <udp.h>
8: #include <string>
9: 
10: #include "led/led.h"
11: #include "backlight.h"
12: 
13: void* create_board();
14: class AudioCodec;
15: class Display;
16: class Board {
17: private:
18:     Board(const Board&) = delete; // 禁用拷贝构造函数
19:     Board& operator=(const Board&) = delete; // 禁用赋值操作
```

## board.h | 文件开头/全局定义 | 原文件第20-36行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.h
以下为原始源码，不是截图OCR。
```
20:     virtual std::string GetBoardJson() = 0;
21: 
22: protected:
23:     Board();
24:     std::string GenerateUuid();
25: 
26:     // 软件生成的设备唯一标识
27:     std::string uuid_;
28: 
29: public:
30:     static Board& GetInstance() {
31:         static Board* instance = static_cast<Board*>(create_board());
32:         return *instance;
33:     }
34: 
35:     virtual ~Board() = default;
36:     virtual std::string GetBoardType() = 0;
```

## board.h | GetUuid | 原文件第37-37行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.h
以下为原始源码，不是截图OCR。
```
37:     virtual std::string GetUuid() { return uuid_; }
```

## board.h | GetBacklight | 原文件第38-46行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.h
以下为原始源码，不是截图OCR。
```
38:     virtual Backlight* GetBacklight() { return nullptr; }
39:     virtual Led* GetLed();
40:     virtual AudioCodec* GetAudioCodec() = 0;
41:     virtual Display* GetDisplay();
42:     virtual Http* CreateHttp() = 0;
43:     virtual WebSocket* CreateWebSocket() = 0;
44:     virtual Mqtt* CreateMqtt() = 0;
45:     virtual Udp* CreateUdp() = 0;
46:     virtual void StartNetwork() = 0;
```

## board.h | GetBacklight | 原文件第47-53行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.h
以下为原始源码，不是截图OCR。
```
47:     virtual const char* GetNetworkStateIcon() = 0;
48:     virtual bool GetBatteryLevel(int &level, bool& charging, bool& discharging);
49:     virtual std::string GetJson();
50:     virtual void SetPowerSaveMode(bool enabled) = 0;
51: };
52: 
53: #define DECLARE_BOARD(BOARD_CLASS_NAME) \
```

## board.h | create_board | 原文件第54-58行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/board.h
以下为原始源码，不是截图OCR。
```
54: void* create_board() { \
55:     return new BOARD_CLASS_NAME(); \
56: }
57: 
58: #endif // BOARD_H
```

## button.cc | 文件开头/全局定义 | 原文件第1-13行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/button.cc
以下为原始源码，不是截图OCR。
```
1: #include "button.h"
2: 
3: #include <esp_log.h>
4: 
5: static const char* TAG = "Button";
6: #if CONFIG_SOC_ADC_SUPPORTED
7: Button::Button(const button_adc_config_t& adc_cfg) {
8:     button_config_t button_config = {
9:         .type = BUTTON_TYPE_ADC,
10:         .long_press_time = 1000,
11:         .short_press_time = 50,
12:         .adc_button_config = adc_cfg
13:     };
```

## button.cc | 文件开头/全局定义 | 原文件第14-26行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/button.cc
以下为原始源码，不是截图OCR。
```
14:     button_handle_ = iot_button_create(&button_config);
15:     if (button_handle_ == NULL) {
16:         ESP_LOGE(TAG, "Failed to create button handle");
17:         return;
18:     }
19: }
20: #endif
21: 
22: Button::Button(gpio_num_t gpio_num, bool active_high) : gpio_num_(gpio_num) {
23:     if (gpio_num == GPIO_NUM_NC) {
24:         return;
25:     }
26:     button_config_t button_config = {
```

## button.cc | 文件开头/全局定义 | 原文件第27-36行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/button.cc
以下为原始源码，不是截图OCR。
```
27:         .type = BUTTON_TYPE_GPIO,
28:         .long_press_time = 1000,
29:         .short_press_time = 50,
30:         .gpio_button_config = {
31:             .gpio_num = gpio_num,
32:             .active_level = static_cast<uint8_t>(active_high ? 1 : 0)
33:         }
34:     };
35:     button_handle_ = iot_button_create(&button_config);
36:     if (button_handle_ == NULL) {
```

## button.cc | 文件开头/全局定义 | 原文件第37-47行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/button.cc
以下为原始源码，不是截图OCR。
```
37:         ESP_LOGE(TAG, "Failed to create button handle");
38:         return;
39:     }
40: }
41: 
42: Button::~Button() {
43:     if (button_handle_ != NULL) {
44:         iot_button_delete(button_handle_);
45:     }
46: }
47: 
```

## button.cc | Button::OnPressDown | 原文件第48-57行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/button.cc
以下为原始源码，不是截图OCR。
```
48: void Button::OnPressDown(std::function<void()> callback) {
49:     if (button_handle_ == nullptr) {
50:         return;
51:     }
52:     on_press_down_ = callback;
53:     iot_button_register_cb(button_handle_, BUTTON_PRESS_DOWN, [](void* handle, void* usr_data) {
54:         Button* button = static_cast<Button*>(usr_data);
55:         if (button->on_press_down_) {
56:             button->on_press_down_();
57:         }
```

## button.cc | Button::OnPressDown | 原文件第58-60行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/button.cc
以下为原始源码，不是截图OCR。
```
58:     }, this);
59: }
60: 
```

## button.cc | Button::OnPressUp | 原文件第61-71行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/button.cc
以下为原始源码，不是截图OCR。
```
61: void Button::OnPressUp(std::function<void()> callback) {
62:     if (button_handle_ == nullptr) {
63:         return;
64:     }
65:     on_press_up_ = callback;
66:     iot_button_register_cb(button_handle_, BUTTON_PRESS_UP, [](void* handle, void* usr_data) {
67:         Button* button = static_cast<Button*>(usr_data);
68:         if (button->on_press_up_) {
69:             button->on_press_up_();
70:         }
71:     }, this);
```

## button.cc | Button::OnPressUp | 原文件第72-73行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/button.cc
以下为原始源码，不是截图OCR。
```
72: }
73: 
```

## button.cc | Button::OnLongPress | 原文件第74-83行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/button.cc
以下为原始源码，不是截图OCR。
```
74: void Button::OnLongPress(std::function<void()> callback) {
75:     if (button_handle_ == nullptr) {
76:         return;
77:     }
78:     on_long_press_ = callback;
79:     iot_button_register_cb(button_handle_, BUTTON_LONG_PRESS_START, [](void* handle, void* usr_data) {
80:         Button* button = static_cast<Button*>(usr_data);
81:         if (button->on_long_press_) {
82:             button->on_long_press_();
83:         }
```

## button.cc | Button::OnLongPress | 原文件第84-86行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/button.cc
以下为原始源码，不是截图OCR。
```
84:     }, this);
85: }
86: 
```

## button.cc | Button::OnClick | 原文件第87-98行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/button.cc
以下为原始源码，不是截图OCR。
```
87: void Button::OnClick(std::function<void()> callback) {
88:     if (button_handle_ == nullptr) {
89:         return;
90:     }
91:     on_click_ = callback;
92:     iot_button_register_cb(button_handle_, BUTTON_SINGLE_CLICK, [](void* handle, void* usr_data) {
93:         Button* button = static_cast<Button*>(usr_data);
94:         if (button->on_click_) {
95:             button->on_click_();
96:         }
97:     }, this);
98: }
```

## button.cc | Button::OnClick | 原文件第99-99行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/button.cc
以下为原始源码，不是截图OCR。
```
99: 
```

## button.cc | Button::OnDoubleClick | 原文件第100-108行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/button.cc
以下为原始源码，不是截图OCR。
```
100: void Button::OnDoubleClick(std::function<void()> callback) {
101:     if (button_handle_ == nullptr) {
102:         return;
103:     }
104:     on_double_click_ = callback;
105:     iot_button_register_cb(button_handle_, BUTTON_DOUBLE_CLICK, [](void* handle, void* usr_data) {
106:         Button* button = static_cast<Button*>(usr_data);
107:         if (button->on_double_click_) {
108:             button->on_double_click_();
```

## button.cc | Button::OnDoubleClick | 原文件第109-111行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/button.cc
以下为原始源码，不是截图OCR。
```
109:         }
110:     }, this);
111: }
```

## button.h | 文件开头/全局定义 | 原文件第1-16行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/button.h
以下为原始源码，不是截图OCR。
```
1: #ifndef BUTTON_H_
2: #define BUTTON_H_
3: 
4: #include <driver/gpio.h>
5: #include <iot_button.h>
6: #include <functional>
7: 
8: class Button {
9: public:
10: #if CONFIG_SOC_ADC_SUPPORTED
11:     Button(const button_adc_config_t& cfg);
12: #endif
13:     Button(gpio_num_t gpio_num, bool active_high = false);
14:     ~Button();
15: 
16:     void OnPressDown(std::function<void()> callback);
```

## button.h | 文件开头/全局定义 | 原文件第17-27行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/button.h
以下为原始源码，不是截图OCR。
```
17:     void OnPressUp(std::function<void()> callback);
18:     void OnLongPress(std::function<void()> callback);
19:     void OnClick(std::function<void()> callback);
20:     void OnDoubleClick(std::function<void()> callback);
21: private:
22:     gpio_num_t gpio_num_;
23:     button_handle_t button_handle_ = nullptr;
24: 
25: 
26:     std::function<void()> on_press_down_;
27:     std::function<void()> on_press_up_;
```

## button.h | 文件开头/全局定义 | 原文件第28-33行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/button.h
以下为原始源码，不是截图OCR。
```
28:     std::function<void()> on_long_press_;
29:     std::function<void()> on_click_;
30:     std::function<void()> on_double_click_;
31: };
32: 
33: #endif // BUTTON_H_
```

## i2c_device.cc | 文件开头/全局定义 | 原文件第1-15行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/i2c_device.cc
以下为原始源码，不是截图OCR。
```
1: #include "i2c_device.h"
2: 
3: #include <esp_log.h>
4: 
5: #define TAG "I2cDevice"
6: 
7: 
8: I2cDevice::I2cDevice(i2c_master_bus_handle_t i2c_bus, uint8_t addr) {
9:     i2c_device_config_t i2c_device_cfg = {
10:         .dev_addr_length = I2C_ADDR_BIT_LEN_7,
11:         .device_address = addr,
12:         .scl_speed_hz = 400 * 1000,
13:         .scl_wait_us = 0,
14:         .flags = {
15:             .disable_ack_check = 0,
```

## i2c_device.cc | 文件开头/全局定义 | 原文件第16-21行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/i2c_device.cc
以下为原始源码，不是截图OCR。
```
16:         },
17:     };
18:     ESP_ERROR_CHECK(i2c_master_bus_add_device(i2c_bus, &i2c_device_cfg, &i2c_device_));
19:     assert(i2c_device_ != NULL);
20: }
21: 
```

## i2c_device.cc | I2cDevice::WriteReg | 原文件第22-26行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/i2c_device.cc
以下为原始源码，不是截图OCR。
```
22: void I2cDevice::WriteReg(uint8_t reg, uint8_t value) {
23:     uint8_t buffer[2] = {reg, value};
24:     ESP_ERROR_CHECK(i2c_master_transmit(i2c_device_, buffer, 2, 100));
25: }
26: 
```

## i2c_device.cc | I2cDevice::ReadReg | 原文件第27-32行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/i2c_device.cc
以下为原始源码，不是截图OCR。
```
27: uint8_t I2cDevice::ReadReg(uint8_t reg) {
28:     uint8_t buffer[1];
29:     ESP_ERROR_CHECK(i2c_master_transmit_receive(i2c_device_, &reg, 1, buffer, 1, 100));
30:     return buffer[0];
31: }
32: 
```

## i2c_device.cc | I2cDevice::ReadRegs | 原文件第33-35行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/i2c_device.cc
以下为原始源码，不是截图OCR。
```
33: void I2cDevice::ReadRegs(uint8_t reg, uint8_t* buffer, size_t length) {
34:     ESP_ERROR_CHECK(i2c_master_transmit_receive(i2c_device_, &reg, 1, buffer, length, 100));
35: }
```

## i2c_device.h | 文件开头/全局定义 | 原文件第1-17行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/i2c_device.h
以下为原始源码，不是截图OCR。
```
1: #ifndef I2C_DEVICE_H
2: #define I2C_DEVICE_H
3: 
4: #include <driver/i2c_master.h>
5: 
6: class I2cDevice {
7: public:
8:     I2cDevice(i2c_master_bus_handle_t i2c_bus, uint8_t addr);
9: 
10: protected:
11:     i2c_master_dev_handle_t i2c_device_;
12: 
13:     void WriteReg(uint8_t reg, uint8_t value);
14:     uint8_t ReadReg(uint8_t reg);
15:     void ReadRegs(uint8_t reg, uint8_t* buffer, size_t length);
16: };
17: 
```

## i2c_device.h | 文件开头/全局定义 | 原文件第18-18行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/i2c_device.h
以下为原始源码，不是截图OCR。
```
18: #endif // I2C_DEVICE_H
```

## ml307_board.cc | 文件开头/全局定义 | 原文件第1-17行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/ml307_board.cc
以下为原始源码，不是截图OCR。
```
1: #include "ml307_board.h"
2: 
3: #include "application.h"
4: #include "display.h"
5: #include "font_awesome_symbols.h"
6: #include "assets/lang_config.h"
7: 
8: #include <esp_log.h>
9: #include <esp_timer.h>
10: #include <ml307_http.h>
11: #include <ml307_ssl_transport.h>
12: #include <web_socket.h>
13: #include <ml307_mqtt.h>
14: #include <ml307_udp.h>
15: #include <opus_encoder.h>
16: 
17: static const char *TAG = "Ml307Board";
```

## ml307_board.cc | 文件开头/全局定义 | 原文件第18-21行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/ml307_board.cc
以下为原始源码，不是截图OCR。
```
18: 
19: Ml307Board::Ml307Board(gpio_num_t tx_pin, gpio_num_t rx_pin, size_t rx_buffer_size) : modem_(tx_pin, rx_pin, rx_buffer_size) {
20: }
21: 
```

## ml307_board.cc | Ml307Board::GetBoardType | 原文件第22-25行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/ml307_board.cc
以下为原始源码，不是截图OCR。
```
22: std::string Ml307Board::GetBoardType() {
23:     return "ml307";
24: }
25: 
```

## ml307_board.cc | Ml307Board::StartNetwork | 原文件第26-33行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/ml307_board.cc
以下为原始源码，不是截图OCR。
```
26: void Ml307Board::StartNetwork() {
27:     auto display = Board::GetInstance().GetDisplay();
28:     display->SetStatus(Lang::Strings::DETECTING_MODULE);
29:     modem_.SetDebug(false);
30:     modem_.SetBaudRate(921600);
31: 
32:     auto& application = Application::GetInstance();
33:     // If low power, the material ready event will be triggered by the modem because of a reset
```

## ml307_board.cc | Ml307Board::StartNetwork | 原文件第34-44行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/ml307_board.cc
以下为原始源码，不是截图OCR。
```
34:     modem_.OnMaterialReady([this, &application]() {
35:         ESP_LOGI(TAG, "ML307 material ready");
36:         application.Schedule([this, &application]() {
37:             application.SetDeviceState(kDeviceStateIdle);
38:             WaitForNetworkReady();
39:         });
40:     });
41: 
42:     WaitForNetworkReady();
43: }
44: 
```

## ml307_board.cc | Ml307Board::WaitForNetworkReady | 原文件第45-52行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/ml307_board.cc
以下为原始源码，不是截图OCR。
```
45: void Ml307Board::WaitForNetworkReady() {
46:     auto& application = Application::GetInstance();
47:     auto display = Board::GetInstance().GetDisplay();
48:     display->SetStatus(Lang::Strings::REGISTERING_NETWORK);
49:     int result = modem_.WaitForNetworkReady();
50:     if (result == -1) {
51:         application.Alert(Lang::Strings::ERROR, Lang::Strings::PIN_ERROR, "sad", Lang::Sounds::P3_ERR_PIN);
52:         return;
```

## ml307_board.cc | Ml307Board::WaitForNetworkReady | 原文件第53-61行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/ml307_board.cc
以下为原始源码，不是截图OCR。
```
53:     } else if (result == -2) {
54:         application.Alert(Lang::Strings::ERROR, Lang::Strings::REG_ERROR, "sad", Lang::Sounds::P3_ERR_REG);
55:         return;
56:     }
57: 
58:     // Print the ML307 modem information
59:     std::string module_name = modem_.GetModuleName();
60:     std::string imei = modem_.GetImei();
61:     std::string iccid = modem_.GetIccid();
```

## ml307_board.cc | Ml307Board::WaitForNetworkReady | 原文件第62-69行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/ml307_board.cc
以下为原始源码，不是截图OCR。
```
62:     ESP_LOGI(TAG, "ML307 Module: %s", module_name.c_str());
63:     ESP_LOGI(TAG, "ML307 IMEI: %s", imei.c_str());
64:     ESP_LOGI(TAG, "ML307 ICCID: %s", iccid.c_str());
65: 
66:     // Close all previous connections
67:     modem_.ResetConnections();
68: }
69: 
```

## ml307_board.cc | Ml307Board::CreateHttp | 原文件第70-73行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/ml307_board.cc
以下为原始源码，不是截图OCR。
```
70: Http* Ml307Board::CreateHttp() {
71:     return new Ml307Http(modem_);
72: }
73: 
```

## ml307_board.cc | Ml307Board::CreateWebSocket | 原文件第74-77行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/ml307_board.cc
以下为原始源码，不是截图OCR。
```
74: WebSocket* Ml307Board::CreateWebSocket() {
75:     return new WebSocket(new Ml307SslTransport(modem_, 0));
76: }
77: 
```

## ml307_board.cc | Ml307Board::CreateMqtt | 原文件第78-81行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/ml307_board.cc
以下为原始源码，不是截图OCR。
```
78: Mqtt* Ml307Board::CreateMqtt() {
79:     return new Ml307Mqtt(modem_, 0);
80: }
81: 
```

## ml307_board.cc | Ml307Board::CreateUdp | 原文件第82-85行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/ml307_board.cc
以下为原始源码，不是截图OCR。
```
82: Udp* Ml307Board::CreateUdp() {
83:     return new Ml307Udp(modem_, 0);
84: }
85: 
```

## ml307_board.cc | Ml307Board::GetNetworkStateIcon | 原文件第86-96行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/ml307_board.cc
以下为原始源码，不是截图OCR。
```
86: const char* Ml307Board::GetNetworkStateIcon() {
87:     if (!modem_.network_ready()) {
88:         return FONT_AWESOME_SIGNAL_OFF;
89:     }
90:     int csq = modem_.GetCsq();
91:     if (csq == -1) {
92:         return FONT_AWESOME_SIGNAL_OFF;
93:     } else if (csq >= 0 && csq <= 14) {
94:         return FONT_AWESOME_SIGNAL_1;
95:     } else if (csq >= 15 && csq <= 19) {
96:         return FONT_AWESOME_SIGNAL_2;
```

## ml307_board.cc | Ml307Board::GetNetworkStateIcon | 原文件第97-106行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/ml307_board.cc
以下为原始源码，不是截图OCR。
```
97:     } else if (csq >= 20 && csq <= 24) {
98:         return FONT_AWESOME_SIGNAL_3;
99:     } else if (csq >= 25 && csq <= 31) {
100:         return FONT_AWESOME_SIGNAL_4;
101:     }
102: 
103:     ESP_LOGW(TAG, "Invalid CSQ: %d", csq);
104:     return FONT_AWESOME_SIGNAL_OFF;
105: }
106: 
```

## ml307_board.cc | Ml307Board::GetBoardJson | 原文件第107-112行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/ml307_board.cc
以下为原始源码，不是截图OCR。
```
107: std::string Ml307Board::GetBoardJson() {
108:     // Set the board type for OTA
109:     std::string board_json = std::string("{\"type\":\"" BOARD_TYPE "\",");
110:     board_json += "\"name\":\"" BOARD_NAME "\",";
111:     board_json += "\"revision\":\"" + modem_.GetModuleName() + "\",";
112:     board_json += "\"carrier\":\"" + modem_.GetCarrierName() + "\",";
```

## ml307_board.cc | Ml307Board::GetBoardJson | 原文件第113-118行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/ml307_board.cc
以下为原始源码，不是截图OCR。
```
113:     board_json += "\"csq\":\"" + std::to_string(modem_.GetCsq()) + "\",";
114:     board_json += "\"imei\":\"" + modem_.GetImei() + "\",";
115:     board_json += "\"iccid\":\"" + modem_.GetIccid() + "\"}";
116:     return board_json;
117: }
118: 
```

## ml307_board.cc | Ml307Board::SetPowerSaveMode | 原文件第119-121行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/ml307_board.cc
以下为原始源码，不是截图OCR。
```
119: void Ml307Board::SetPowerSaveMode(bool enabled) {
120:     // TODO: Implement power save mode for ML307
121: }
```

## ml307_board.h | 文件开头/全局定义 | 原文件第1-15行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/ml307_board.h
以下为原始源码，不是截图OCR。
```
1: #ifndef ML307_BOARD_H
2: #define ML307_BOARD_H
3: 
4: #include "board.h"
5: #include <ml307_at_modem.h>
6: 
7: class Ml307Board : public Board {
8: protected:
9:     Ml307AtModem modem_;
10: 
11:     virtual std::string GetBoardJson() override;
12:     void WaitForNetworkReady();
13: 
14: public:
15:     Ml307Board(gpio_num_t tx_pin, gpio_num_t rx_pin, size_t rx_buffer_size = 4096);
```

## ml307_board.h | 文件开头/全局定义 | 原文件第16-25行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/ml307_board.h
以下为原始源码，不是截图OCR。
```
16:     virtual std::string GetBoardType() override;
17:     virtual void StartNetwork() override;
18:     virtual Http* CreateHttp() override;
19:     virtual WebSocket* CreateWebSocket() override;
20:     virtual Mqtt* CreateMqtt() override;
21:     virtual Udp* CreateUdp() override;
22:     virtual const char* GetNetworkStateIcon() override;
23:     virtual void SetPowerSaveMode(bool enabled) override;
24: };
25: 
```

## ml307_board.h | 文件开头/全局定义 | 原文件第26-26行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/ml307_board.h
以下为原始源码，不是截图OCR。
```
26: #endif // ML307_BOARD_H
```

## power_save_timer.cc | 文件开头/全局定义 | 原文件第1-9行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/power_save_timer.cc
以下为原始源码，不是截图OCR。
```
1: #include "power_save_timer.h"
2: #include "application.h"
3: 
4: #include <esp_log.h>
5: 
6: #define TAG "PowerSaveTimer"
7: 
8: 
9: PowerSaveTimer::PowerSaveTimer(int cpu_max_freq, int seconds_to_sleep, int seconds_to_shutdown)
```

## power_save_timer.cc | cpu_max_freq_ | 原文件第10-18行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/power_save_timer.cc
以下为原始源码，不是截图OCR。
```
10:     : cpu_max_freq_(cpu_max_freq), seconds_to_sleep_(seconds_to_sleep), seconds_to_shutdown_(seconds_to_shutdown) {
11:     esp_timer_create_args_t timer_args = {
12:         .callback = [](void* arg) {
13:             auto self = static_cast<PowerSaveTimer*>(arg);
14:             self->PowerSaveCheck();
15:         },
16:         .arg = this,
17:         .dispatch_method = ESP_TIMER_TASK,
18:         .name = "power_save_timer",
```

## power_save_timer.cc | cpu_max_freq_ | 原文件第19-28行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/power_save_timer.cc
以下为原始源码，不是截图OCR。
```
19:         .skip_unhandled_events = true,
20:     };
21:     ESP_ERROR_CHECK(esp_timer_create(&timer_args, &power_save_timer_));
22: }
23: 
24: PowerSaveTimer::~PowerSaveTimer() {
25:     esp_timer_stop(power_save_timer_);
26:     esp_timer_delete(power_save_timer_);
27: }
28: 
```

## power_save_timer.cc | PowerSaveTimer::SetEnabled | 原文件第29-37行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/power_save_timer.cc
以下为原始源码，不是截图OCR。
```
29: void PowerSaveTimer::SetEnabled(bool enabled) {
30:     if (enabled && !enabled_) {
31:         ticks_ = 0;
32:         enabled_ = enabled;
33:         ESP_ERROR_CHECK(esp_timer_start_periodic(power_save_timer_, 1000000));
34:         ESP_LOGI(TAG, "Power save timer enabled");
35:     } else if (!enabled && enabled_) {
36:         ESP_ERROR_CHECK(esp_timer_stop(power_save_timer_));
37:         enabled_ = enabled;
```

## power_save_timer.cc | PowerSaveTimer::SetEnabled | 原文件第38-42行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/power_save_timer.cc
以下为原始源码，不是截图OCR。
```
38:         WakeUp();
39:         ESP_LOGI(TAG, "Power save timer disabled");
40:     }
41: }
42: 
```

## power_save_timer.cc | PowerSaveTimer::OnEnterSleepMode | 原文件第43-46行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/power_save_timer.cc
以下为原始源码，不是截图OCR。
```
43: void PowerSaveTimer::OnEnterSleepMode(std::function<void()> callback) {
44:     on_enter_sleep_mode_ = callback;
45: }
46: 
```

## power_save_timer.cc | PowerSaveTimer::OnExitSleepMode | 原文件第47-50行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/power_save_timer.cc
以下为原始源码，不是截图OCR。
```
47: void PowerSaveTimer::OnExitSleepMode(std::function<void()> callback) {
48:     on_exit_sleep_mode_ = callback;
49: }
50: 
```

## power_save_timer.cc | PowerSaveTimer::OnShutdownRequest | 原文件第51-54行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/power_save_timer.cc
以下为原始源码，不是截图OCR。
```
51: void PowerSaveTimer::OnShutdownRequest(std::function<void()> callback) {
52:     on_shutdown_request_ = callback;
53: }
54: 
```

## power_save_timer.cc | PowerSaveTimer::PowerSaveCheck | 原文件第55-66行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/power_save_timer.cc
以下为原始源码，不是截图OCR。
```
55: void PowerSaveTimer::PowerSaveCheck() {
56:     auto& app = Application::GetInstance();
57:     if (!in_sleep_mode_ && !app.CanEnterSleepMode()) {
58:         ticks_ = 0;
59:         return;
60:     }
61: 
62:     ticks_++;
63:     if (seconds_to_sleep_ != -1 && ticks_ >= seconds_to_sleep_) {
64:         if (!in_sleep_mode_) {
65:             in_sleep_mode_ = true;
66:             if (on_enter_sleep_mode_) {
```

## power_save_timer.cc | PowerSaveTimer::PowerSaveCheck | 原文件第67-79行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/power_save_timer.cc
以下为原始源码，不是截图OCR。
```
67:                 on_enter_sleep_mode_();
68:             }
69: 
70:             if (cpu_max_freq_ != -1) {
71:                 esp_pm_config_t pm_config = {
72:                     .max_freq_mhz = cpu_max_freq_,
73:                     .min_freq_mhz = 40,
74:                     .light_sleep_enable = true,
75:                 };
76:                 esp_pm_configure(&pm_config);
77:             }
78:         }
79:     }
```

## power_save_timer.cc | PowerSaveTimer::PowerSaveCheck | 原文件第80-84行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/power_save_timer.cc
以下为原始源码，不是截图OCR。
```
80:     if (seconds_to_shutdown_ != -1 && ticks_ >= seconds_to_shutdown_ && on_shutdown_request_) {
81:         on_shutdown_request_();
82:     }
83: }
84: 
```

## power_save_timer.cc | PowerSaveTimer::WakeUp | 原文件第85-96行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/power_save_timer.cc
以下为原始源码，不是截图OCR。
```
85: void PowerSaveTimer::WakeUp() {
86:     ticks_ = 0;
87:     if (in_sleep_mode_) {
88:         in_sleep_mode_ = false;
89: 
90:         if (cpu_max_freq_ != -1) {
91:             esp_pm_config_t pm_config = {
92:                 .max_freq_mhz = cpu_max_freq_,
93:                 .min_freq_mhz = cpu_max_freq_,
94:                 .light_sleep_enable = false,
95:             };
96:             esp_pm_configure(&pm_config);
```

## power_save_timer.cc | PowerSaveTimer::WakeUp | 原文件第97-103行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/power_save_timer.cc
以下为原始源码，不是截图OCR。
```
97:         }
98: 
99:         if (on_exit_sleep_mode_) {
100:             on_exit_sleep_mode_();
101:         }
102:     }
103: }
```

## power_save_timer.h | 文件开头/全局定义 | 原文件第1-15行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/power_save_timer.h
以下为原始源码，不是截图OCR。
```
1: #pragma once
2: 
3: #include <functional>
4: 
5: #include <esp_timer.h>
6: #include <esp_pm.h>
7: 
8: class PowerSaveTimer {
9: public:
10:     PowerSaveTimer(int cpu_max_freq, int seconds_to_sleep = 20, int seconds_to_shutdown = -1);
11:     ~PowerSaveTimer();
12: 
13:     void SetEnabled(bool enabled);
14:     void OnEnterSleepMode(std::function<void()> callback);
15:     void OnExitSleepMode(std::function<void()> callback);
```

## power_save_timer.h | 文件开头/全局定义 | 原文件第16-30行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/power_save_timer.h
以下为原始源码，不是截图OCR。
```
16:     void OnShutdownRequest(std::function<void()> callback);
17:     void WakeUp();
18: 
19: private:
20:     void PowerSaveCheck();
21: 
22:     esp_timer_handle_t power_save_timer_ = nullptr;
23:     bool enabled_ = false;
24:     bool in_sleep_mode_ = false;
25:     int ticks_ = 0;
26:     int cpu_max_freq_;
27:     int seconds_to_sleep_;
28:     int seconds_to_shutdown_;
29: 
30:     std::function<void()> on_enter_sleep_mode_;
```

## power_save_timer.h | 文件开头/全局定义 | 原文件第31-33行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/power_save_timer.h
以下为原始源码，不是截图OCR。
```
31:     std::function<void()> on_exit_sleep_mode_;
32:     std::function<void()> on_shutdown_request_;
33: };
```

## system_reset.cc | 文件开头/全局定义 | 原文件第1-14行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/system_reset.cc
以下为原始源码，不是截图OCR。
```
1: #include "system_reset.h"
2: 
3: #include <esp_log.h>
4: #include <nvs_flash.h>
5: #include <driver/gpio.h>
6: #include <esp_partition.h>
7: #include <esp_system.h>
8: #include <freertos/FreeRTOS.h>
9: 
10: 
11: #define TAG "SystemReset"
12: 
13: 
14: SystemReset::SystemReset(gpio_num_t reset_nvs_pin, gpio_num_t reset_factory_pin) : reset_nvs_pin_(reset_nvs_pin), reset_factory_pin_(reset_factory_pin) {
```

## system_reset.cc | 文件开头/全局定义 | 原文件第15-24行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/system_reset.cc
以下为原始源码，不是截图OCR。
```
15:     // Configure GPIO1, GPIO2 as INPUT, reset NVS flash if the button is pressed
16:     gpio_config_t io_conf;
17:     io_conf.intr_type = GPIO_INTR_DISABLE;
18:     io_conf.mode = GPIO_MODE_INPUT;
19:     io_conf.pin_bit_mask = (1ULL << reset_nvs_pin_) | (1ULL << reset_factory_pin_);
20:     io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
21:     io_conf.pull_up_en = GPIO_PULLUP_ENABLE;
22:     gpio_config(&io_conf);
23: }
24: 
```

## system_reset.cc | 文件开头/全局定义 | 原文件第25-25行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/system_reset.cc
以下为原始源码，不是截图OCR。
```
25: 
```

## system_reset.cc | SystemReset::CheckButtons | 原文件第26-38行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/system_reset.cc
以下为原始源码，不是截图OCR。
```
26: void SystemReset::CheckButtons() {
27:     if (gpio_get_level(reset_factory_pin_) == 0) {
28:         ESP_LOGI(TAG, "Button is pressed, reset to factory");
29:         ResetNvsFlash();
30:         ResetToFactory();
31:     }
32: 
33:     if (gpio_get_level(reset_nvs_pin_) == 0) {
34:         ESP_LOGI(TAG, "Button is pressed, reset NVS flash");
35:         ResetNvsFlash();
36:     }
37: }
38: 
```

## system_reset.cc | SystemReset::ResetNvsFlash | 原文件第39-50行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/system_reset.cc
以下为原始源码，不是截图OCR。
```
39: void SystemReset::ResetNvsFlash() {
40:     ESP_LOGI(TAG, "Resetting NVS flash");
41:     esp_err_t ret = nvs_flash_erase();
42:     if (ret != ESP_OK) {
43:         ESP_LOGE(TAG, "Failed to erase NVS flash");
44:     }
45:     ret = nvs_flash_init();
46:     if (ret != ESP_OK) {
47:         ESP_LOGE(TAG, "Failed to initialize NVS flash");
48:     }
49: }
50: 
```

## system_reset.cc | SystemReset::ResetToFactory | 原文件第51-58行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/system_reset.cc
以下为原始源码，不是截图OCR。
```
51: void SystemReset::ResetToFactory() {
52:     ESP_LOGI(TAG, "Resetting to factory");
53:     // Erase otadata partition
54:     const esp_partition_t* partition = esp_partition_find_first(ESP_PARTITION_TYPE_DATA, ESP_PARTITION_SUBTYPE_DATA_OTA, NULL);
55:     if (partition == NULL) {
56:         ESP_LOGE(TAG, "Failed to find otadata partition");
57:         return;
58:     }
```

## system_reset.cc | SystemReset::ResetToFactory | 原文件第59-65行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/system_reset.cc
以下为原始源码，不是截图OCR。
```
59:     esp_partition_erase_range(partition, 0, partition->size);
60:     ESP_LOGI(TAG, "Erased otadata partition");
61: 
62:     // Reboot in 3 seconds
63:     RestartInSeconds(3);
64: }
65: 
```

## system_reset.cc | SystemReset::RestartInSeconds | 原文件第66-72行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/system_reset.cc
以下为原始源码，不是截图OCR。
```
66: void SystemReset::RestartInSeconds(int seconds) {
67:     for (int i = seconds; i > 0; i--) {
68:         ESP_LOGI(TAG, "Resetting in %d seconds", i);
69:         vTaskDelay(1000 / portTICK_PERIOD_MS);
70:     }
71:     esp_restart();
72: }
```

## system_reset.h | 文件开头/全局定义 | 原文件第1-16行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/system_reset.h
以下为原始源码，不是截图OCR。
```
1: #ifndef _SYSTEM_RESET_H
2: #define _SYSTEM_RESET_H
3: 
4: #include <driver/gpio.h>
5: 
6: class SystemReset {
7: public:
8:     SystemReset(gpio_num_t reset_nvs_pin, gpio_num_t reset_factory_pin); // 构造函数私有化
9:     void CheckButtons();
10: 
11: private:
12:     gpio_num_t reset_nvs_pin_;
13:     gpio_num_t reset_factory_pin_;
14: 
15:     void ResetNvsFlash();
16:     void ResetToFactory();
```

## system_reset.h | 文件开头/全局定义 | 原文件第17-21行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/system_reset.h
以下为原始源码，不是截图OCR。
```
17:     void RestartInSeconds(int seconds);
18: };
19: 
20: 
21: #endif
```

## wifi_board.cc | 文件开头/全局定义 | 原文件第1-16行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.cc
以下为原始源码，不是截图OCR。
```
1: #include "wifi_board.h"
2: 
3: #include "display.h"
4: #include "application.h"
5: #include "system_info.h"
6: #include "font_awesome_symbols.h"
7: #include "settings.h"
8: #include "assets/lang_config.h"
9: 
10: #include <freertos/FreeRTOS.h>
11: #include <freertos/task.h>
12: #include <esp_http.h>
13: #include <esp_mqtt.h>
14: #include <esp_udp.h>
15: #include <tcp_transport.h>
16: #include <tls_transport.h>
```

## wifi_board.cc | 文件开头/全局定义 | 原文件第17-30行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.cc
以下为原始源码，不是截图OCR。
```
17: #include <web_socket.h>
18: #include <esp_log.h>
19: 
20: #include <wifi_station.h>
21: #include <wifi_configuration_ap.h>
22: #include <ssid_manager.h>
23: 
24: static const char *TAG = "WifiBoard";
25: 
26: WifiBoard::WifiBoard() {
27:     Settings settings("wifi", true);
28:     wifi_config_mode_ = settings.GetInt("force_ap") == 1;
29:     if (wifi_config_mode_) {
30:         ESP_LOGI(TAG, "force_ap is set to 1, reset to 0");
```

## wifi_board.cc | 文件开头/全局定义 | 原文件第31-34行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.cc
以下为原始源码，不是截图OCR。
```
31:         settings.SetInt("force_ap", 0);
32:     }
33: }
34: 
```

## wifi_board.cc | WifiBoard::GetBoardType | 原文件第35-38行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.cc
以下为原始源码，不是截图OCR。
```
35: std::string WifiBoard::GetBoardType() {
36:     return "wifi";
37: }
38: 
```

## wifi_board.cc | WifiBoard::EnterWifiConfigMode | 原文件第39-48行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.cc
以下为原始源码，不是截图OCR。
```
39: void WifiBoard::EnterWifiConfigMode() {
40:     auto& application = Application::GetInstance();
41:     application.SetDeviceState(kDeviceStateWifiConfiguring);
42: 
43:     auto& wifi_ap = WifiConfigurationAp::GetInstance();
44:     wifi_ap.SetLanguage(Lang::CODE);
45:     wifi_ap.SetSsidPrefix("Xiaozhi");
46:     wifi_ap.Start();
47: 
48:     // 显示 WiFi 配置 AP 的 SSID 和 Web 服务器 URL
```

## wifi_board.cc | WifiBoard::EnterWifiConfigMode | 原文件第49-58行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.cc
以下为原始源码，不是截图OCR。
```
49:     std::string hint = Lang::Strings::CONNECT_TO_HOTSPOT;
50:     hint += wifi_ap.GetSsid();
51:     hint += Lang::Strings::ACCESS_VIA_BROWSER;
52:     hint += wifi_ap.GetWebServerUrl();
53:     hint += "\n\n";
54:     
55:     // 播报配置 WiFi 的提示
56:     application.Alert(Lang::Strings::WIFI_CONFIG_MODE, hint.c_str(), "", Lang::Sounds::P3_WIFICONFIG);
57:     
58:     // Wait forever until reset after configuration
```

## wifi_board.cc | WifiBoard::EnterWifiConfigMode | 原文件第59-66行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.cc
以下为原始源码，不是截图OCR。
```
59:     while (true) {
60:         int free_sram = heap_caps_get_free_size(MALLOC_CAP_INTERNAL);
61:         int min_free_sram = heap_caps_get_minimum_free_size(MALLOC_CAP_INTERNAL);
62:         ESP_LOGI(TAG, "Free internal: %u minimal internal: %u", free_sram, min_free_sram);
63:         vTaskDelay(pdMS_TO_TICKS(10000));
64:     }
65: }
66: 
```

## wifi_board.cc | WifiBoard::StartNetwork | 原文件第67-76行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.cc
以下为原始源码，不是截图OCR。
```
67: void WifiBoard::StartNetwork() {
68:     // User can press BOOT button while starting to enter WiFi configuration mode
69:     if (wifi_config_mode_) {
70:         EnterWifiConfigMode();
71:         return;
72:     }
73: 
74:     // If no WiFi SSID is configured, enter WiFi configuration mode
75:     auto& ssid_manager = SsidManager::GetInstance();
76:     auto ssid_list = ssid_manager.GetSsidList();
```

## wifi_board.cc | WifiBoard::StartNetwork | 原文件第77-87行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.cc
以下为原始源码，不是截图OCR。
```
77:     if (ssid_list.empty()) {
78:         wifi_config_mode_ = true;
79:         EnterWifiConfigMode();
80:         return;
81:     }
82: 
83:     auto& wifi_station = WifiStation::GetInstance();
84:     wifi_station.OnScanBegin([this]() {
85:         auto display = Board::GetInstance().GetDisplay();
86:         display->ShowNotification(Lang::Strings::SCANNING_WIFI, 30000);
87:     });
```

## wifi_board.cc | WifiBoard::StartNetwork | 原文件第88-95行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.cc
以下为原始源码，不是截图OCR。
```
88:     wifi_station.OnConnect([this](const std::string& ssid) {
89:         auto display = Board::GetInstance().GetDisplay();
90:         std::string notification = Lang::Strings::CONNECT_TO;
91:         notification += ssid;
92:         notification += "...";
93:         display->ShowNotification(notification.c_str(), 30000);
94:     });
95:     wifi_station.OnConnected([this](const std::string& ssid) {
```

## wifi_board.cc | WifiBoard::StartNetwork | 原文件第96-104行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.cc
以下为原始源码，不是截图OCR。
```
96:         auto display = Board::GetInstance().GetDisplay();
97:         std::string notification = Lang::Strings::CONNECTED_TO;
98:         notification += ssid;
99:         display->ShowNotification(notification.c_str(), 30000);
100:     });
101:     wifi_station.Start();
102: 
103:     // Try to connect to WiFi, if failed, launch the WiFi configuration AP
104:     if (!wifi_station.WaitForConnected(60 * 1000)) {
```

## wifi_board.cc | WifiBoard::StartNetwork | 原文件第105-111行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.cc
以下为原始源码，不是截图OCR。
```
105:         wifi_station.Stop();
106:         wifi_config_mode_ = true;
107:         EnterWifiConfigMode();
108:         return;
109:     }
110: }
111: 
```

## wifi_board.cc | WifiBoard::CreateHttp | 原文件第112-115行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.cc
以下为原始源码，不是截图OCR。
```
112: Http* WifiBoard::CreateHttp() {
113:     return new EspHttp();
114: }
115: 
```

## wifi_board.cc | WifiBoard::CreateWebSocket | 原文件第116-127行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.cc
以下为原始源码，不是截图OCR。
```
116: WebSocket* WifiBoard::CreateWebSocket() {
117: #ifdef CONFIG_CONNECTION_TYPE_WEBSOCKET
118:     std::string url = CONFIG_WEBSOCKET_URL;
119:     if (url.find("wss://") == 0) {
120:         return new WebSocket(new TlsTransport());
121:     } else {
122:         return new WebSocket(new TcpTransport());
123:     }
124: #endif
125:     return nullptr;
126: }
127: 
```

## wifi_board.cc | WifiBoard::CreateMqtt | 原文件第128-131行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.cc
以下为原始源码，不是截图OCR。
```
128: Mqtt* WifiBoard::CreateMqtt() {
129:     return new EspMqtt();
130: }
131: 
```

## wifi_board.cc | WifiBoard::CreateUdp | 原文件第132-135行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.cc
以下为原始源码，不是截图OCR。
```
132: Udp* WifiBoard::CreateUdp() {
133:     return new EspUdp();
134: }
135: 
```

## wifi_board.cc | WifiBoard::GetNetworkStateIcon | 原文件第136-146行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.cc
以下为原始源码，不是截图OCR。
```
136: const char* WifiBoard::GetNetworkStateIcon() {
137:     if (wifi_config_mode_) {
138:         return FONT_AWESOME_WIFI;
139:     }
140:     auto& wifi_station = WifiStation::GetInstance();
141:     if (!wifi_station.IsConnected()) {
142:         return FONT_AWESOME_WIFI_OFF;
143:     }
144:     int8_t rssi = wifi_station.GetRssi();
145:     if (rssi >= -60) {
146:         return FONT_AWESOME_WIFI;
```

## wifi_board.cc | WifiBoard::GetNetworkStateIcon | 原文件第147-153行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.cc
以下为原始源码，不是截图OCR。
```
147:     } else if (rssi >= -70) {
148:         return FONT_AWESOME_WIFI_FAIR;
149:     } else {
150:         return FONT_AWESOME_WIFI_WEAK;
151:     }
152: }
153: 
```

## wifi_board.cc | WifiBoard::GetBoardJson | 原文件第154-160行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.cc
以下为原始源码，不是截图OCR。
```
154: std::string WifiBoard::GetBoardJson() {
155:     // Set the board type for OTA
156:     auto& wifi_station = WifiStation::GetInstance();
157:     std::string board_json = std::string("{\"type\":\"" BOARD_TYPE "\",");
158:     board_json += "\"name\":\"" BOARD_NAME "\",";
159:     if (!wifi_config_mode_) {
160:         board_json += "\"ssid\":\"" + wifi_station.GetSsid() + "\",";
```

## wifi_board.cc | WifiBoard::GetBoardJson | 原文件第161-168行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.cc
以下为原始源码，不是截图OCR。
```
161:         board_json += "\"rssi\":" + std::to_string(wifi_station.GetRssi()) + ",";
162:         board_json += "\"channel\":" + std::to_string(wifi_station.GetChannel()) + ",";
163:         board_json += "\"ip\":\"" + wifi_station.GetIpAddress() + "\",";
164:     }
165:     board_json += "\"mac\":\"" + SystemInfo::GetMacAddress() + "\"}";
166:     return board_json;
167: }
168: 
```

## wifi_board.cc | WifiBoard::SetPowerSaveMode | 原文件第169-173行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.cc
以下为原始源码，不是截图OCR。
```
169: void WifiBoard::SetPowerSaveMode(bool enabled) {
170:     auto& wifi_station = WifiStation::GetInstance();
171:     wifi_station.SetPowerSaveMode(enabled);
172: }
173: 
```

## wifi_board.cc | WifiBoard::ResetWifiConfiguration | 原文件第174-184行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.cc
以下为原始源码，不是截图OCR。
```
174: void WifiBoard::ResetWifiConfiguration() {
175:     // Set a flag and reboot the device to enter the network configuration mode
176:     {
177:         Settings settings("wifi", true);
178:         settings.SetInt("force_ap", 1);
179:     }
180:     GetDisplay()->ShowNotification(Lang::Strings::ENTERING_WIFI_CONFIG_MODE);
181:     vTaskDelay(pdMS_TO_TICKS(1000));
182:     // Reboot the device
183:     esp_restart();
184: }
```

## wifi_board.h | 文件开头/全局定义 | 原文件第1-16行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.h
以下为原始源码，不是截图OCR。
```
1: #ifndef WIFI_BOARD_H
2: #define WIFI_BOARD_H
3: 
4: #include "board.h"
5: 
6: class WifiBoard : public Board {
7: protected:
8:     bool wifi_config_mode_ = false;
9: 
10:     WifiBoard();
11:     void EnterWifiConfigMode();
12:     virtual std::string GetBoardJson() override;
13: 
14: public:
15:     virtual std::string GetBoardType() override;
16:     virtual void StartNetwork() override;
```

## wifi_board.h | 文件开头/全局定义 | 原文件第17-26行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/common/wifi_board.h
以下为原始源码，不是截图OCR。
```
17:     virtual Http* CreateHttp() override;
18:     virtual WebSocket* CreateWebSocket() override;
19:     virtual Mqtt* CreateMqtt() override;
20:     virtual Udp* CreateUdp() override;
21:     virtual const char* GetNetworkStateIcon() override;
22:     virtual void SetPowerSaveMode(bool enabled) override;
23:     virtual void ResetWifiConfiguration();
24: };
25: 
26: #endif // WIFI_BOARD_H
```

## config.h | 文件开头/全局定义 | 原文件第1-16行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/config.h
以下为原始源码，不是截图OCR。
```
1: #ifndef _BOARD_CONFIG_H_
2: #define _BOARD_CONFIG_H_
3: 
4: #include <driver/gpio.h>
5: 
6: #define AUDIO_INPUT_SAMPLE_RATE  16000
7: #define AUDIO_OUTPUT_SAMPLE_RATE 24000
8: 
9: // 如果使用 Duplex I2S 模式，请注释下面一行
10: #define AUDIO_I2S_METHOD_SIMPLEX
11: 
12: #ifdef AUDIO_I2S_METHOD_SIMPLEX
13: 
14: #define AUDIO_I2S_MIC_GPIO_WS   GPIO_NUM_4
15: #define AUDIO_I2S_MIC_GPIO_SCK  GPIO_NUM_5
16: #define AUDIO_I2S_MIC_GPIO_DIN  GPIO_NUM_6
```

## config.h | 文件开头/全局定义 | 原文件第17-31行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/config.h
以下为原始源码，不是截图OCR。
```
17: #define AUDIO_I2S_SPK_GPIO_DOUT GPIO_NUM_7
18: #define AUDIO_I2S_SPK_GPIO_BCLK GPIO_NUM_15
19: #define AUDIO_I2S_SPK_GPIO_LRCK GPIO_NUM_16
20: 
21: #else
22: 
23: #define AUDIO_I2S_GPIO_WS GPIO_NUM_4
24: #define AUDIO_I2S_GPIO_BCLK GPIO_NUM_5
25: #define AUDIO_I2S_GPIO_DIN  GPIO_NUM_6
26: #define AUDIO_I2S_GPIO_DOUT GPIO_NUM_7
27: 
28: #endif
29: 
30: 
31: #define BUILTIN_LED_GPIO        GPIO_NUM_48
```

## config.h | 文件开头/全局定义 | 原文件第32-42行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/config.h
以下为原始源码，不是截图OCR。
```
32: #define BOOT_BUTTON_GPIO        GPIO_NUM_0
33: #define TOUCH_BUTTON_GPIO       GPIO_NUM_NC
34: #define VOLUME_UP_BUTTON_GPIO   GPIO_NUM_40
35: #define VOLUME_DOWN_BUTTON_GPIO GPIO_NUM_39
36: 
37: 
38: #define DISPLAY_BACKLIGHT_PIN GPIO_NUM_13
39: #define DISPLAY_MOSI_PIN      GPIO_NUM_10
40: #define DISPLAY_CLK_PIN       GPIO_NUM_9
41: #define DISPLAY_DC_PIN        GPIO_NUM_8
42: #define DISPLAY_RST_PIN       GPIO_NUM_18
```

## config.h | 文件开头/全局定义 | 原文件第43-56行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/config.h
以下为原始源码，不是截图OCR。
```
43: #define DISPLAY_CS_PIN        GPIO_NUM_14
44: 
45: #define ML307_RX_PIN GPIO_NUM_11
46: #define ML307_TX_PIN GPIO_NUM_12
47: 
48: 
49: #define DISPLAY_BACKLIGHT_PIN GPIO_NUM_13
50: #define DISPLAY_MOSI_PIN      GPIO_NUM_10
51: #define DISPLAY_CLK_PIN       GPIO_NUM_9
52: #define DISPLAY_DC_PIN        GPIO_NUM_8
53: #define DISPLAY_RST_PIN       GPIO_NUM_18
54: #define DISPLAY_CS_PIN        GPIO_NUM_14
55: 
56: 
```

## config.h | 文件开头/全局定义 | 原文件第57-69行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/config.h
以下为原始源码，不是截图OCR。
```
57: #define DISPLAY_WIDTH   240
58: #define DISPLAY_HEIGHT  240
59: #define DISPLAY_SWAP_XY  false
60: #define DISPLAY_MIRROR_X false
61: #define DISPLAY_MIRROR_Y false
62: #define BACKLIGHT_INVERT false
63: #define DISPLAY_OFFSET_X  0
64: #define DISPLAY_OFFSET_Y  0
65: #define DISPLAY_BACKLIGHT_OUTPUT_INVERT false
66: 
67: 
68: 
69: #endif // _BOARD_CONFIG_H_
```

## zl_ai_zhikong_4g.cc | 文件开头/全局定义 | 原文件第1-14行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/zl_ai_zhikong_4g.cc
以下为原始源码，不是截图OCR。
```
1: #include "ml307_board.h"
2: #include "audio_codecs/no_audio_codec.h"
3: #include "display/lcd_display.h"
4: #include "system_reset.h"
5: #include "application.h"
6: #include "button.h"
7: #include "config.h"
8: #include "iot/thing_manager.h"
9: #include "led/single_led.h"
10: 
11: #include <wifi_station.h>
12: #include <esp_log.h>
13: #include <driver/i2c_master.h>
14: #include <esp_lcd_panel_vendor.h>
```

## zl_ai_zhikong_4g.cc | 文件开头/全局定义 | 原文件第15-30行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/zl_ai_zhikong_4g.cc
以下为原始源码，不是截图OCR。
```
15: #include <driver/spi_common.h>
16: 
17:  
18: #define TAG "ZlAiZhiKong4g"
19: 
20: LV_FONT_DECLARE(font_puhui_20_4);
21: LV_FONT_DECLARE(font_awesome_20_4);
22: 
23: class ZlAiZhiKong4g : public Ml307Board {
24: private:
25:  
26:     Button boot_button_;
27:     Button volume_up_button_;
28:     Button volume_down_button_;
29:     LcdDisplay* display_;
30: 
```

## zl_ai_zhikong_4g.cc | InitializeSpi | 原文件第31-38行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/zl_ai_zhikong_4g.cc
以下为原始源码，不是截图OCR。
```
31:     void InitializeSpi() {
32:         spi_bus_config_t buscfg = {};
33:         buscfg.mosi_io_num = DISPLAY_MOSI_PIN;
34:         buscfg.miso_io_num = GPIO_NUM_NC;
35:         buscfg.sclk_io_num = DISPLAY_CLK_PIN;
36:         buscfg.quadwp_io_num = GPIO_NUM_NC;
37:         buscfg.quadhd_io_num = GPIO_NUM_NC;
38:         buscfg.max_transfer_sz = DISPLAY_WIDTH * DISPLAY_HEIGHT * sizeof(uint16_t);
```

## zl_ai_zhikong_4g.cc | InitializeSpi | 原文件第39-41行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/zl_ai_zhikong_4g.cc
以下为原始源码，不是截图OCR。
```
39:         ESP_ERROR_CHECK(spi_bus_initialize(SPI3_HOST, &buscfg, SPI_DMA_CH_AUTO));
40:     }
41: 
```

## zl_ai_zhikong_4g.cc | InitializeLcdDisplay | 原文件第42-49行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/zl_ai_zhikong_4g.cc
以下为原始源码，不是截图OCR。
```
42:     void InitializeLcdDisplay() {
43:         esp_lcd_panel_io_handle_t panel_io = nullptr;
44:         esp_lcd_panel_handle_t panel = nullptr;
45:         ESP_LOGD(TAG, "Install panel IO");
46:         esp_lcd_panel_io_spi_config_t io_config = {};
47:         io_config.cs_gpio_num = DISPLAY_CS_PIN;
48:         io_config.dc_gpio_num = DISPLAY_DC_PIN;
49:         io_config.spi_mode = 3;
```

## zl_ai_zhikong_4g.cc | InitializeLcdDisplay | 原文件第50-58行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/zl_ai_zhikong_4g.cc
以下为原始源码，不是截图OCR。
```
50:         io_config.pclk_hz = 80 * 1000 * 1000;
51:         io_config.trans_queue_depth = 10;
52:         io_config.lcd_cmd_bits = 8;
53:         io_config.lcd_param_bits = 8;
54:         ESP_ERROR_CHECK(esp_lcd_new_panel_io_spi(SPI3_HOST, &io_config, &panel_io));
55: 
56:         ESP_LOGD(TAG, "Install LCD driver");
57:         esp_lcd_panel_dev_config_t panel_config = {};
58:         panel_config.reset_gpio_num = DISPLAY_RST_PIN;
```

## zl_ai_zhikong_4g.cc | InitializeLcdDisplay | 原文件第59-64行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/zl_ai_zhikong_4g.cc
以下为原始源码，不是截图OCR。
```
59:         panel_config.rgb_ele_order = LCD_RGB_ELEMENT_ORDER_RGB;
60:         panel_config.bits_per_pixel = 16;
61:         ESP_ERROR_CHECK(esp_lcd_new_panel_st7789(panel_io, &panel_config, &panel));
62:         ESP_ERROR_CHECK(esp_lcd_panel_reset(panel));
63:         ESP_ERROR_CHECK(esp_lcd_panel_init(panel));
64:         ESP_ERROR_CHECK(esp_lcd_panel_swap_xy(panel, DISPLAY_SWAP_XY));
```

## zl_ai_zhikong_4g.cc | InitializeLcdDisplay | 原文件第65-71行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/zl_ai_zhikong_4g.cc
以下为原始源码，不是截图OCR。
```
65:         ESP_ERROR_CHECK(esp_lcd_panel_mirror(panel, DISPLAY_MIRROR_X, DISPLAY_MIRROR_Y));
66:         ESP_ERROR_CHECK(esp_lcd_panel_invert_color(panel, true));
67: 
68:         display_ = new SpiLcdDisplay(panel_io, panel, DISPLAY_WIDTH, DISPLAY_HEIGHT, DISPLAY_OFFSET_X, DISPLAY_OFFSET_Y, 
69:             DISPLAY_MIRROR_X, DISPLAY_MIRROR_Y, DISPLAY_SWAP_XY, 
70:         {
71:             .text_font = &font_puhui_20_4,
```

## zl_ai_zhikong_4g.cc | InitializeLcdDisplay | 原文件第72-78行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/zl_ai_zhikong_4g.cc
以下为原始源码，不是截图OCR。
```
72:             .icon_font = &font_awesome_20_4,
73:             .emoji_font = font_emoji_64_init(),
74:         });
75:     }
76: 
77: 
78:  
```

## zl_ai_zhikong_4g.cc | InitializeButtons | 原文件第79-90行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/zl_ai_zhikong_4g.cc
以下为原始源码，不是截图OCR。
```
79:     void InitializeButtons() {
80:         boot_button_.OnClick([this]() {
81:             Application::GetInstance().ToggleChatState();
82:         });
83: 
84:         
85:         volume_up_button_.OnClick([this]() {
86:             auto codec = GetAudioCodec();
87:             auto volume = codec->output_volume() + 10;
88:             if (volume > 100) {
89:                 volume = 100;
90:             }
```

## zl_ai_zhikong_4g.cc | InitializeButtons | 原文件第91-101行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/zl_ai_zhikong_4g.cc
以下为原始源码，不是截图OCR。
```
91:             codec->SetOutputVolume(volume);
92:             GetDisplay()->ShowNotification("音量 " + std::to_string(volume));
93:         });
94: 
95:         volume_up_button_.OnLongPress([this]() {
96:             GetAudioCodec()->SetOutputVolume(100);
97:             GetDisplay()->ShowNotification("最大音量");
98:         });
99: 
100:         volume_down_button_.OnClick([this]() {
101:             auto codec = GetAudioCodec();
```

## zl_ai_zhikong_4g.cc | InitializeButtons | 原文件第102-111行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/zl_ai_zhikong_4g.cc
以下为原始源码，不是截图OCR。
```
102:             auto volume = codec->output_volume() - 10;
103:             if (volume < 0) {
104:                 volume = 0;
105:             }
106:             codec->SetOutputVolume(volume);
107:             GetDisplay()->ShowNotification("音量 " + std::to_string(volume));
108:         });
109: 
110:         volume_down_button_.OnLongPress([this]() {
111:             GetAudioCodec()->SetOutputVolume(0);
```

## zl_ai_zhikong_4g.cc | InitializeButtons | 原文件第112-117行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/zl_ai_zhikong_4g.cc
以下为原始源码，不是截图OCR。
```
112:             GetDisplay()->ShowNotification("已静音");
113:         });
114: 
115:     }
116: 
117:     // 物联网初始化，添加对 AI 可见设备
```

## zl_ai_zhikong_4g.cc | InitializeIot | 原文件第118-126行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/zl_ai_zhikong_4g.cc
以下为原始源码，不是截图OCR。
```
118:     void InitializeIot() {
119:         auto& thing_manager = iot::ThingManager::GetInstance();
120:         thing_manager.AddThing(iot::CreateThing("Speaker"));
121:         thing_manager.AddThing(iot::CreateThing("Backlight"));
122:     }
123: 
124: public:
125:     ZlAiZhiKong4g() : Ml307Board(ML307_TX_PIN, ML307_RX_PIN, 4096),
126:         boot_button_(BOOT_BUTTON_GPIO),         
```

## zl_ai_zhikong_4g.cc | InitializeIot | 原文件第127-138行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/zl_ai_zhikong_4g.cc
以下为原始源码，不是截图OCR。
```
127:         volume_up_button_(VOLUME_UP_BUTTON_GPIO),
128:         volume_down_button_(VOLUME_DOWN_BUTTON_GPIO){
129:         InitializeSpi();
130:         InitializeLcdDisplay();
131:         InitializeButtons();
132:         InitializeIot();
133:         GetBacklight()->RestoreBrightness();
134:     }
135: 
136:     virtual Led* GetLed() override {
137:         static SingleLed led(BUILTIN_LED_GPIO);
138:         return &led;
```

## zl_ai_zhikong_4g.cc | InitializeIot | 原文件第139-145行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/zl_ai_zhikong_4g.cc
以下为原始源码，不是截图OCR。
```
139:     }
140: 
141:     virtual AudioCodec* GetAudioCodec() override {
142: #ifdef AUDIO_I2S_METHOD_SIMPLEX
143:         static NoAudioCodecSimplex audio_codec(AUDIO_INPUT_SAMPLE_RATE, AUDIO_OUTPUT_SAMPLE_RATE,
144:             AUDIO_I2S_SPK_GPIO_BCLK, AUDIO_I2S_SPK_GPIO_LRCK, AUDIO_I2S_SPK_GPIO_DOUT, AUDIO_I2S_MIC_GPIO_SCK, AUDIO_I2S_MIC_GPIO_WS, AUDIO_I2S_MIC_GPIO_DIN);
145: #else
```

## zl_ai_zhikong_4g.cc | InitializeIot | 原文件第146-155行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/zl_ai_zhikong_4g.cc
以下为原始源码，不是截图OCR。
```
146:         static NoAudioCodecDuplex audio_codec(AUDIO_INPUT_SAMPLE_RATE, AUDIO_OUTPUT_SAMPLE_RATE,
147:             AUDIO_I2S_GPIO_BCLK, AUDIO_I2S_GPIO_WS, AUDIO_I2S_GPIO_DOUT, AUDIO_I2S_GPIO_DIN);
148: #endif
149:         return &audio_codec;
150:     }
151: 
152:     virtual Display* GetDisplay() override {
153:         return display_;
154:     }
155:     virtual Backlight* GetBacklight() override {
```

## zl_ai_zhikong_4g.cc | InitializeIot | 原文件第156-164行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-4g/zl_ai_zhikong_4g.cc
以下为原始源码，不是截图OCR。
```
156:         if (DISPLAY_BACKLIGHT_PIN != GPIO_NUM_NC) {
157:             static PwmBacklight backlight(DISPLAY_BACKLIGHT_PIN, DISPLAY_BACKLIGHT_OUTPUT_INVERT);
158:             return &backlight;
159:         }
160:         return nullptr;
161:     }
162: };
163: 
164: DECLARE_BOARD(ZlAiZhiKong4g);
```

## config.h | 文件开头/全局定义 | 原文件第1-16行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-wifi/config.h
以下为原始源码，不是截图OCR。
```
1: #ifndef _BOARD_CONFIG_H_
2: #define _BOARD_CONFIG_H_
3: 
4: #include <driver/gpio.h>
5: 
6: #define AUDIO_INPUT_SAMPLE_RATE  16000
7: #define AUDIO_OUTPUT_SAMPLE_RATE 24000
8: 
9: // 如果使用 Duplex I2S 模式，请注释下面一行
10: #define AUDIO_I2S_METHOD_SIMPLEX
11: 
12: #ifdef AUDIO_I2S_METHOD_SIMPLEX
13: 
14: #define AUDIO_I2S_MIC_GPIO_WS   GPIO_NUM_4
15: #define AUDIO_I2S_MIC_GPIO_SCK  GPIO_NUM_5
16: #define AUDIO_I2S_MIC_GPIO_DIN  GPIO_NUM_6
```

## config.h | 文件开头/全局定义 | 原文件第17-31行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-wifi/config.h
以下为原始源码，不是截图OCR。
```
17: #define AUDIO_I2S_SPK_GPIO_DOUT GPIO_NUM_7
18: #define AUDIO_I2S_SPK_GPIO_BCLK GPIO_NUM_15
19: #define AUDIO_I2S_SPK_GPIO_LRCK GPIO_NUM_16
20: 
21: #else
22: 
23: #define AUDIO_I2S_GPIO_WS GPIO_NUM_4
24: #define AUDIO_I2S_GPIO_BCLK GPIO_NUM_5
25: #define AUDIO_I2S_GPIO_DIN  GPIO_NUM_6
26: #define AUDIO_I2S_GPIO_DOUT GPIO_NUM_7
27: 
28: #endif
29: 
30: 
31: #define BUILTIN_LED_GPIO        GPIO_NUM_48
```

## config.h | 文件开头/全局定义 | 原文件第32-42行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-wifi/config.h
以下为原始源码，不是截图OCR。
```
32: #define BOOT_BUTTON_GPIO        GPIO_NUM_0
33: #define TOUCH_BUTTON_GPIO       GPIO_NUM_NC
34: #define VOLUME_UP_BUTTON_GPIO   GPIO_NUM_40
35: #define VOLUME_DOWN_BUTTON_GPIO GPIO_NUM_39
36: 
37: 
38: #define DISPLAY_BACKLIGHT_PIN GPIO_NUM_13
39: #define DISPLAY_MOSI_PIN      GPIO_NUM_10
40: #define DISPLAY_CLK_PIN       GPIO_NUM_9
41: #define DISPLAY_DC_PIN        GPIO_NUM_8
42: #define DISPLAY_RST_PIN       GPIO_NUM_18
```

## config.h | 文件开头/全局定义 | 原文件第43-58行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-wifi/config.h
以下为原始源码，不是截图OCR。
```
43: #define DISPLAY_CS_PIN        GPIO_NUM_14
44: 
45: 
46: #define DISPLAY_WIDTH   240
47: #define DISPLAY_HEIGHT  240
48: #define DISPLAY_SWAP_XY  false
49: #define DISPLAY_MIRROR_X false
50: #define DISPLAY_MIRROR_Y false
51: #define BACKLIGHT_INVERT false
52: #define DISPLAY_OFFSET_X  0
53: #define DISPLAY_OFFSET_Y  0
54: #define DISPLAY_BACKLIGHT_OUTPUT_INVERT false
55: 
56: 
57: 
58: #endif // _BOARD_CONFIG_H_
```

## zl_ai_zhikong_wifi.cc | 文件开头/全局定义 | 原文件第1-14行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-wifi/zl_ai_zhikong_wifi.cc
以下为原始源码，不是截图OCR。
```
1: #include "wifi_board.h"
2: #include "audio_codecs/no_audio_codec.h"
3: #include "display/lcd_display.h"
4: #include "system_reset.h"
5: #include "application.h"
6: #include "button.h"
7: #include "config.h"
8: #include "iot/thing_manager.h"
9: #include "led/single_led.h"
10: 
11: #include <wifi_station.h>
12: #include <esp_log.h>
13: #include <driver/i2c_master.h>
14: #include <esp_lcd_panel_vendor.h>
```

## zl_ai_zhikong_wifi.cc | 文件开头/全局定义 | 原文件第15-30行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-wifi/zl_ai_zhikong_wifi.cc
以下为原始源码，不是截图OCR。
```
15: #include <driver/spi_common.h>
16: 
17:  
18: #define TAG "ZlAiZhiKongWifi"
19: 
20: LV_FONT_DECLARE(font_puhui_20_4);
21: LV_FONT_DECLARE(font_awesome_20_4);
22: 
23: class ZlAiZhiKongWifi : public WifiBoard {
24: private:
25:  
26:     Button boot_button_;
27:     Button volume_up_button_;
28:     Button volume_down_button_;
29:     LcdDisplay* display_;
30: 
```

## zl_ai_zhikong_wifi.cc | InitializeSpi | 原文件第31-38行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-wifi/zl_ai_zhikong_wifi.cc
以下为原始源码，不是截图OCR。
```
31:     void InitializeSpi() {
32:         spi_bus_config_t buscfg = {};
33:         buscfg.mosi_io_num = DISPLAY_MOSI_PIN;
34:         buscfg.miso_io_num = GPIO_NUM_NC;
35:         buscfg.sclk_io_num = DISPLAY_CLK_PIN;
36:         buscfg.quadwp_io_num = GPIO_NUM_NC;
37:         buscfg.quadhd_io_num = GPIO_NUM_NC;
38:         buscfg.max_transfer_sz = DISPLAY_WIDTH * DISPLAY_HEIGHT * sizeof(uint16_t);
```

## zl_ai_zhikong_wifi.cc | InitializeSpi | 原文件第39-41行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-wifi/zl_ai_zhikong_wifi.cc
以下为原始源码，不是截图OCR。
```
39:         ESP_ERROR_CHECK(spi_bus_initialize(SPI3_HOST, &buscfg, SPI_DMA_CH_AUTO));
40:     }
41: 
```

## zl_ai_zhikong_wifi.cc | InitializeLcdDisplay | 原文件第42-49行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-wifi/zl_ai_zhikong_wifi.cc
以下为原始源码，不是截图OCR。
```
42:     void InitializeLcdDisplay() {
43:         esp_lcd_panel_io_handle_t panel_io = nullptr;
44:         esp_lcd_panel_handle_t panel = nullptr;
45:         ESP_LOGD(TAG, "Install panel IO");
46:         esp_lcd_panel_io_spi_config_t io_config = {};
47:         io_config.cs_gpio_num = DISPLAY_CS_PIN;
48:         io_config.dc_gpio_num = DISPLAY_DC_PIN;
49:         io_config.spi_mode = 3;
```

## zl_ai_zhikong_wifi.cc | InitializeLcdDisplay | 原文件第50-58行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-wifi/zl_ai_zhikong_wifi.cc
以下为原始源码，不是截图OCR。
```
50:         io_config.pclk_hz = 80 * 1000 * 1000;
51:         io_config.trans_queue_depth = 10;
52:         io_config.lcd_cmd_bits = 8;
53:         io_config.lcd_param_bits = 8;
54:         ESP_ERROR_CHECK(esp_lcd_new_panel_io_spi(SPI3_HOST, &io_config, &panel_io));
55: 
56:         ESP_LOGD(TAG, "Install LCD driver");
57:         esp_lcd_panel_dev_config_t panel_config = {};
58:         panel_config.reset_gpio_num = DISPLAY_RST_PIN;
```

## zl_ai_zhikong_wifi.cc | InitializeLcdDisplay | 原文件第59-64行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-wifi/zl_ai_zhikong_wifi.cc
以下为原始源码，不是截图OCR。
```
59:         panel_config.rgb_ele_order = LCD_RGB_ELEMENT_ORDER_RGB;
60:         panel_config.bits_per_pixel = 16;
61:         ESP_ERROR_CHECK(esp_lcd_new_panel_st7789(panel_io, &panel_config, &panel));
62:         ESP_ERROR_CHECK(esp_lcd_panel_reset(panel));
63:         ESP_ERROR_CHECK(esp_lcd_panel_init(panel));
64:         ESP_ERROR_CHECK(esp_lcd_panel_swap_xy(panel, DISPLAY_SWAP_XY));
```

## zl_ai_zhikong_wifi.cc | InitializeLcdDisplay | 原文件第65-71行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-wifi/zl_ai_zhikong_wifi.cc
以下为原始源码，不是截图OCR。
```
65:         ESP_ERROR_CHECK(esp_lcd_panel_mirror(panel, DISPLAY_MIRROR_X, DISPLAY_MIRROR_Y));
66:         ESP_ERROR_CHECK(esp_lcd_panel_invert_color(panel, true));
67: 
68:         display_ = new SpiLcdDisplay(panel_io, panel, DISPLAY_WIDTH, DISPLAY_HEIGHT, DISPLAY_OFFSET_X, DISPLAY_OFFSET_Y, 
69:             DISPLAY_MIRROR_X, DISPLAY_MIRROR_Y, DISPLAY_SWAP_XY, 
70:         {
71:             .text_font = &font_puhui_20_4,
```

## zl_ai_zhikong_wifi.cc | InitializeLcdDisplay | 原文件第72-78行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-wifi/zl_ai_zhikong_wifi.cc
以下为原始源码，不是截图OCR。
```
72:             .icon_font = &font_awesome_20_4,
73:             .emoji_font = font_emoji_64_init(),
74:         });
75:     }
76: 
77: 
78:  
```

## zl_ai_zhikong_wifi.cc | InitializeButtons | 原文件第79-89行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-wifi/zl_ai_zhikong_wifi.cc
以下为原始源码，不是截图OCR。
```
79:     void InitializeButtons() {
80:         boot_button_.OnClick([this]() {
81:             auto& app = Application::GetInstance();
82:             if (app.GetDeviceState() == kDeviceStateStarting && !WifiStation::GetInstance().IsConnected()) {
83:                 ResetWifiConfiguration();
84:             }
85:             app.ToggleChatState();
86:         });
87: 
88:         
89:         volume_up_button_.OnClick([this]() {
```

## zl_ai_zhikong_wifi.cc | InitializeButtons | 原文件第90-99行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-wifi/zl_ai_zhikong_wifi.cc
以下为原始源码，不是截图OCR。
```
90:             auto codec = GetAudioCodec();
91:             auto volume = codec->output_volume() + 10;
92:             if (volume > 100) {
93:                 volume = 100;
94:             }
95:             codec->SetOutputVolume(volume);
96:             GetDisplay()->ShowNotification("音量 " + std::to_string(volume));
97:         });
98: 
99:         volume_up_button_.OnLongPress([this]() {
```

## zl_ai_zhikong_wifi.cc | InitializeButtons | 原文件第100-110行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-wifi/zl_ai_zhikong_wifi.cc
以下为原始源码，不是截图OCR。
```
100:             GetAudioCodec()->SetOutputVolume(100);
101:             GetDisplay()->ShowNotification("最大音量");
102:         });
103: 
104:         volume_down_button_.OnClick([this]() {
105:             auto codec = GetAudioCodec();
106:             auto volume = codec->output_volume() - 10;
107:             if (volume < 0) {
108:                 volume = 0;
109:             }
110:             codec->SetOutputVolume(volume);
```

## zl_ai_zhikong_wifi.cc | InitializeButtons | 原文件第111-121行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-wifi/zl_ai_zhikong_wifi.cc
以下为原始源码，不是截图OCR。
```
111:             GetDisplay()->ShowNotification("音量 " + std::to_string(volume));
112:         });
113: 
114:         volume_down_button_.OnLongPress([this]() {
115:             GetAudioCodec()->SetOutputVolume(0);
116:             GetDisplay()->ShowNotification("已静音");
117:         });
118: 
119:     }
120: 
121:     // 物联网初始化，添加对 AI 可见设备
```

## zl_ai_zhikong_wifi.cc | InitializeIot | 原文件第122-131行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-wifi/zl_ai_zhikong_wifi.cc
以下为原始源码，不是截图OCR。
```
122:     void InitializeIot() {
123:         auto& thing_manager = iot::ThingManager::GetInstance();
124:         thing_manager.AddThing(iot::CreateThing("Speaker"));
125:         thing_manager.AddThing(iot::CreateThing("Backlight"));
126:         thing_manager.AddThing(iot::CreateThing("RoboticArm"));
127:     }
128: 
129: public:
130:     ZlAiZhiKongWifi() :
131:         boot_button_(BOOT_BUTTON_GPIO),         
```

## zl_ai_zhikong_wifi.cc | InitializeIot | 原文件第132-144行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-wifi/zl_ai_zhikong_wifi.cc
以下为原始源码，不是截图OCR。
```
132:         volume_up_button_(VOLUME_UP_BUTTON_GPIO),
133:         volume_down_button_(VOLUME_DOWN_BUTTON_GPIO){
134:         InitializeSpi();
135:         InitializeLcdDisplay();
136:         InitializeButtons();
137:         InitializeIot();
138:         GetBacklight()->RestoreBrightness();
139: 
140:     }
141: 
142:     virtual Led* GetLed() override {
143:         static SingleLed led(BUILTIN_LED_GPIO);
144:         return &led;
```

## zl_ai_zhikong_wifi.cc | InitializeIot | 原文件第145-151行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-wifi/zl_ai_zhikong_wifi.cc
以下为原始源码，不是截图OCR。
```
145:     }
146: 
147:     virtual AudioCodec* GetAudioCodec() override {
148: #ifdef AUDIO_I2S_METHOD_SIMPLEX
149:         static NoAudioCodecSimplex audio_codec(AUDIO_INPUT_SAMPLE_RATE, AUDIO_OUTPUT_SAMPLE_RATE,
150:             AUDIO_I2S_SPK_GPIO_BCLK, AUDIO_I2S_SPK_GPIO_LRCK, AUDIO_I2S_SPK_GPIO_DOUT, AUDIO_I2S_MIC_GPIO_SCK, AUDIO_I2S_MIC_GPIO_WS, AUDIO_I2S_MIC_GPIO_DIN);
151: #else
```

## zl_ai_zhikong_wifi.cc | InitializeIot | 原文件第152-161行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-wifi/zl_ai_zhikong_wifi.cc
以下为原始源码，不是截图OCR。
```
152:         static NoAudioCodecDuplex audio_codec(AUDIO_INPUT_SAMPLE_RATE, AUDIO_OUTPUT_SAMPLE_RATE,
153:             AUDIO_I2S_GPIO_BCLK, AUDIO_I2S_GPIO_WS, AUDIO_I2S_GPIO_DOUT, AUDIO_I2S_GPIO_DIN);
154: #endif
155:         return &audio_codec;
156:     }
157: 
158:     virtual Display* GetDisplay() override {
159:         return display_;
160:     }
161:     virtual Backlight* GetBacklight() override {
```

## zl_ai_zhikong_wifi.cc | InitializeIot | 原文件第162-170行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/boards/zl-ai-zhikong-wifi/zl_ai_zhikong_wifi.cc
以下为原始源码，不是截图OCR。
```
162:         if (DISPLAY_BACKLIGHT_PIN != GPIO_NUM_NC) {
163:             static PwmBacklight backlight(DISPLAY_BACKLIGHT_PIN, DISPLAY_BACKLIGHT_OUTPUT_INVERT);
164:             return &backlight;
165:         }
166:         return nullptr;
167:     }
168: };
169: 
170: DECLARE_BOARD(ZlAiZhiKongWifi);
```

## display.cc | 文件开头/全局定义 | 原文件第1-18行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
1: #include <esp_log.h>
2: #include <esp_err.h>
3: #include <string>
4: #include <cstdlib>
5: #include <cstring>
6: 
7: #include "display.h"
8: #include "board.h"
9: #include "application.h"
10: #include "font_awesome_symbols.h"
11: #include "audio_codec.h"
12: #include "settings.h"
13: #include "assets/lang_config.h"
14: 
15: #define TAG "Display"
16: 
17: Display::Display() {
18:     // Notification timer
```

## display.cc | 文件开头/全局定义 | 原文件第19-26行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
19:     esp_timer_create_args_t notification_timer_args = {
20:         .callback = [](void *arg) {
21:             Display *display = static_cast<Display*>(arg);
22:             DisplayLockGuard lock(display);
23:             lv_obj_add_flag(display->notification_label_, LV_OBJ_FLAG_HIDDEN);
24:             lv_obj_clear_flag(display->status_label_, LV_OBJ_FLAG_HIDDEN);
25:         },
26:         .arg = this,
```

## display.cc | 文件开头/全局定义 | 原文件第27-36行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
27:         .dispatch_method = ESP_TIMER_TASK,
28:         .name = "notification_timer",
29:         .skip_unhandled_events = false,
30:     };
31:     ESP_ERROR_CHECK(esp_timer_create(&notification_timer_args, &notification_timer_));
32: 
33:     // Update display timer
34:     esp_timer_create_args_t update_display_timer_args = {
35:         .callback = [](void *arg) {
36:             Display *display = static_cast<Display*>(arg);
```

## display.cc | 文件开头/全局定义 | 原文件第37-47行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
37:             display->Update();
38:         },
39:         .arg = this,
40:         .dispatch_method = ESP_TIMER_TASK,
41:         .name = "display_update_timer",
42:         .skip_unhandled_events = true,
43:     };
44:     ESP_ERROR_CHECK(esp_timer_create(&update_display_timer_args, &update_timer_));
45:     ESP_ERROR_CHECK(esp_timer_start_periodic(update_timer_, 1000000));
46: 
47:     // Create a power management lock
```

## display.cc | 文件开头/全局定义 | 原文件第48-58行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
48:     auto ret = esp_pm_lock_create(ESP_PM_APB_FREQ_MAX, 0, "display_update", &pm_lock_);
49:     if (ret == ESP_ERR_NOT_SUPPORTED) {
50:         ESP_LOGI(TAG, "Power management not supported");
51:     } else {
52:         ESP_ERROR_CHECK(ret);
53:     }
54: }
55: 
56: Display::~Display() {
57:     if (notification_timer_ != nullptr) {
58:         esp_timer_stop(notification_timer_);
```

## display.cc | 文件开头/全局定义 | 原文件第59-70行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
59:         esp_timer_delete(notification_timer_);
60:     }
61:     if (update_timer_ != nullptr) {
62:         esp_timer_stop(update_timer_);
63:         esp_timer_delete(update_timer_);
64:     }
65: 
66:     if (network_label_ != nullptr) {
67:         lv_obj_del(network_label_);
68:         lv_obj_del(notification_label_);
69:         lv_obj_del(status_label_);
70:         lv_obj_del(mute_label_);
```

## display.cc | 文件开头/全局定义 | 原文件第71-79行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
71:         lv_obj_del(battery_label_);
72:         lv_obj_del(emotion_label_);
73:     }
74: 
75:     if (pm_lock_ != nullptr) {
76:         esp_pm_lock_delete(pm_lock_);
77:     }
78: }
79: 
```

## display.cc | Display::SetStatus | 原文件第80-89行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
80: void Display::SetStatus(const char* status) {
81:     DisplayLockGuard lock(this);
82:     if (status_label_ == nullptr) {
83:         return;
84:     }
85:     lv_label_set_text(status_label_, status);
86:     lv_obj_clear_flag(status_label_, LV_OBJ_FLAG_HIDDEN);
87:     lv_obj_add_flag(notification_label_, LV_OBJ_FLAG_HIDDEN);
88: }
89: 
```

## display.cc | Display::ShowNotification | 原文件第90-93行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
90: void Display::ShowNotification(const std::string &notification, int duration_ms) {
91:     ShowNotification(notification.c_str(), duration_ms);
92: }
93: 
```

## display.cc | Display::ShowNotification | 原文件第94-103行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
94: void Display::ShowNotification(const char* notification, int duration_ms) {
95:     DisplayLockGuard lock(this);
96:     if (notification_label_ == nullptr) {
97:         return;
98:     }
99:     lv_label_set_text(notification_label_, notification);
100:     lv_obj_clear_flag(notification_label_, LV_OBJ_FLAG_HIDDEN);
101:     lv_obj_add_flag(status_label_, LV_OBJ_FLAG_HIDDEN);
102: 
103:     esp_timer_stop(notification_timer_);
```

## display.cc | Display::ShowNotification | 原文件第104-106行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
104:     ESP_ERROR_CHECK(esp_timer_start_once(notification_timer_, duration_ms * 1000));
105: }
106: 
```

## display.cc | Display::Update | 原文件第107-119行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
107: void Display::Update() {
108:     auto& board = Board::GetInstance();
109:     auto codec = board.GetAudioCodec();
110: 
111:     {
112:         DisplayLockGuard lock(this);
113:         if (mute_label_ == nullptr) {
114:             return;
115:         }
116: 
117:         // 如果静音状态改变，则更新图标
118:         if (codec->output_volume() == 0 && !muted_) {
119:             muted_ = true;
```

## display.cc | Display::Update | 原文件第120-131行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
120:             lv_label_set_text(mute_label_, FONT_AWESOME_VOLUME_MUTE);
121:         } else if (codec->output_volume() > 0 && muted_) {
122:             muted_ = false;
123:             lv_label_set_text(mute_label_, "");
124:         }
125:     }
126: 
127:     esp_pm_lock_acquire(pm_lock_);
128:     // 更新电池图标
129:     int battery_level;
130:     bool charging, discharging;
131:     const char* icon = nullptr;
```

## display.cc | Display::Update | 原文件第132-139行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
132:     if (board.GetBatteryLevel(battery_level, charging, discharging)) {
133:         if (charging) {
134:             icon = FONT_AWESOME_BATTERY_CHARGING;
135:         } else {
136:             const char* levels[] = {
137:                 FONT_AWESOME_BATTERY_EMPTY, // 0-19%
138:                 FONT_AWESOME_BATTERY_1,    // 20-39%
139:                 FONT_AWESOME_BATTERY_2,    // 40-59%
```

## display.cc | Display::Update | 原文件第140-148行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
140:                 FONT_AWESOME_BATTERY_3,    // 60-79%
141:                 FONT_AWESOME_BATTERY_FULL, // 80-99%
142:                 FONT_AWESOME_BATTERY_FULL, // 100%
143:             };
144:             icon = levels[battery_level / 20];
145:         }
146:         DisplayLockGuard lock(this);
147:         if (battery_label_ != nullptr && battery_icon_ != icon) {
148:             battery_icon_ = icon;
```

## display.cc | Display::Update | 原文件第149-155行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
149:             lv_label_set_text(battery_label_, battery_icon_);
150:         }
151: 
152:         if (low_battery_popup_ != nullptr) {
153:             if (strcmp(icon, FONT_AWESOME_BATTERY_EMPTY) == 0 && discharging) {
154:                 if (lv_obj_has_flag(low_battery_popup_, LV_OBJ_FLAG_HIDDEN)) { // 如果低电量提示框隐藏，则显示
155:                     lv_obj_clear_flag(low_battery_popup_, LV_OBJ_FLAG_HIDDEN);
```

## display.cc | Display::Update | 原文件第156-161行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
156:                     auto& app = Application::GetInstance();
157:                     app.PlaySound(Lang::Sounds::P3_LOW_BATTERY);
158:                 }
159:             } else {
160:                 // Hide the low battery popup when the battery is not empty
161:                 if (!lv_obj_has_flag(low_battery_popup_, LV_OBJ_FLAG_HIDDEN)) { // 如果低电量提示框显示，则隐藏
```

## display.cc | Display::Update | 原文件第162-172行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
162:                     lv_obj_add_flag(low_battery_popup_, LV_OBJ_FLAG_HIDDEN);
163:                 }
164:             }
165:         }
166:     }
167: 
168:     // 升级固件时，不读取 4G 网络状态，避免占用 UART 资源
169:     auto device_state = Application::GetInstance().GetDeviceState();
170:     static const std::vector<DeviceState> allowed_states = {
171:         kDeviceStateIdle,
172:         kDeviceStateStarting,
```

## display.cc | Display::Update | 原文件第173-180行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
173:         kDeviceStateWifiConfiguring,
174:         kDeviceStateListening,
175:     };
176:     if (std::find(allowed_states.begin(), allowed_states.end(), device_state) != allowed_states.end()) {
177:         icon = board.GetNetworkStateIcon();
178:         if (network_label_ != nullptr && icon != nullptr && network_icon_ != icon) {
179:             DisplayLockGuard lock(this);
180:             network_icon_ = icon;
```

## display.cc | Display::Update | 原文件第181-188行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
181:             lv_label_set_text(network_label_, network_icon_);
182:         }
183:     }
184: 
185:     esp_pm_lock_release(pm_lock_);
186: }
187: 
188: 
```

## display.cc | Display::SetEmotion | 原文件第189-199行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
189: void Display::SetEmotion(const char* emotion) {
190:     struct Emotion {
191:         const char* icon;
192:         const char* text;
193:     };
194: 
195:     static const std::vector<Emotion> emotions = {
196:         {FONT_AWESOME_EMOJI_NEUTRAL, "neutral"},
197:         {FONT_AWESOME_EMOJI_HAPPY, "happy"},
198:         {FONT_AWESOME_EMOJI_LAUGHING, "laughing"},
199:         {FONT_AWESOME_EMOJI_FUNNY, "funny"},
```

## display.cc | Display::SetEmotion | 原文件第200-207行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
200:         {FONT_AWESOME_EMOJI_SAD, "sad"},
201:         {FONT_AWESOME_EMOJI_ANGRY, "angry"},
202:         {FONT_AWESOME_EMOJI_CRYING, "crying"},
203:         {FONT_AWESOME_EMOJI_LOVING, "loving"},
204:         {FONT_AWESOME_EMOJI_EMBARRASSED, "embarrassed"},
205:         {FONT_AWESOME_EMOJI_SURPRISED, "surprised"},
206:         {FONT_AWESOME_EMOJI_SHOCKED, "shocked"},
207:         {FONT_AWESOME_EMOJI_THINKING, "thinking"},
```

## display.cc | Display::SetEmotion | 原文件第208-215行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
208:         {FONT_AWESOME_EMOJI_WINKING, "winking"},
209:         {FONT_AWESOME_EMOJI_COOL, "cool"},
210:         {FONT_AWESOME_EMOJI_RELAXED, "relaxed"},
211:         {FONT_AWESOME_EMOJI_DELICIOUS, "delicious"},
212:         {FONT_AWESOME_EMOJI_KISSY, "kissy"},
213:         {FONT_AWESOME_EMOJI_CONFIDENT, "confident"},
214:         {FONT_AWESOME_EMOJI_SLEEPY, "sleepy"},
215:         {FONT_AWESOME_EMOJI_SILLY, "silly"},
```

## display.cc | Display::SetEmotion | 原文件第216-228行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
216:         {FONT_AWESOME_EMOJI_CONFUSED, "confused"}
217:     };
218:     
219:     // 查找匹配的表情
220:     std::string_view emotion_view(emotion);
221:     auto it = std::find_if(emotions.begin(), emotions.end(),
222:         [&emotion_view](const Emotion& e) { return e.text == emotion_view; });
223:     
224:     DisplayLockGuard lock(this);
225:     if (emotion_label_ == nullptr) {
226:         return;
227:     }
228: 
```

## display.cc | Display::SetEmotion | 原文件第229-236行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
229:     // 如果找到匹配的表情就显示对应图标，否则显示默认的neutral表情
230:     if (it != emotions.end()) {
231:         lv_label_set_text(emotion_label_, it->icon);
232:     } else {
233:         lv_label_set_text(emotion_label_, FONT_AWESOME_EMOJI_NEUTRAL);
234:     }
235: }
236: 
```

## display.cc | Display::SetIcon | 原文件第237-244行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
237: void Display::SetIcon(const char* icon) {
238:     DisplayLockGuard lock(this);
239:     if (emotion_label_ == nullptr) {
240:         return;
241:     }
242:     lv_label_set_text(emotion_label_, icon);
243: }
244: 
```

## display.cc | Display::SetChatMessage | 原文件第245-251行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.cc
以下为原始源码，不是截图OCR。
```
245: void Display::SetChatMessage(const char* role, const char* content) {
246:     DisplayLockGuard lock(this);
247:     if (chat_message_label_ == nullptr) {
248:         return;
249:     }
250:     lv_label_set_text(chat_message_label_, content);
251: }
```

## display.h | 文件开头/全局定义 | 原文件第1-21行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.h
以下为原始源码，不是截图OCR。
```
1: #ifndef DISPLAY_H
2: #define DISPLAY_H
3: 
4: #include <lvgl.h>
5: #include <esp_timer.h>
6: #include <esp_log.h>
7: #include <esp_pm.h>
8: 
9: #include <string>
10: 
11: struct DisplayFonts {
12:     const lv_font_t* text_font = nullptr;
13:     const lv_font_t* icon_font = nullptr;
14:     const lv_font_t* emoji_font = nullptr;
15: };
16: 
17: class Display {
18: public:
19:     Display();
20:     virtual ~Display();
21: 
```

## display.h | 文件开头/全局定义 | 原文件第22-28行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.h
以下为原始源码，不是截图OCR。
```
22:     virtual void SetStatus(const char* status);
23:     virtual void ShowNotification(const char* notification, int duration_ms = 3000);
24:     virtual void ShowNotification(const std::string &notification, int duration_ms = 3000);
25:     virtual void SetEmotion(const char* emotion);
26:     virtual void SetChatMessage(const char* role, const char* content);
27:     virtual void SetIcon(const char* icon);
28: 
```

## display.h | 文件开头/全局定义 | 原文件第29-41行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.h
以下为原始源码，不是截图OCR。
```
29:     inline int width() const { return width_; }
30:     inline int height() const { return height_; }
31: 
32: protected:
33:     int width_ = 0;
34:     int height_ = 0;
35:     
36:     esp_pm_lock_handle_t pm_lock_ = nullptr;
37:     lv_display_t *display_ = nullptr;
38: 
39:     lv_obj_t *emotion_label_ = nullptr;
40:     lv_obj_t *network_label_ = nullptr;
41:     lv_obj_t *status_label_ = nullptr;
```

## display.h | 文件开头/全局定义 | 原文件第42-52行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.h
以下为原始源码，不是截图OCR。
```
42:     lv_obj_t *notification_label_ = nullptr;
43:     lv_obj_t *mute_label_ = nullptr;
44:     lv_obj_t *battery_label_ = nullptr;
45:     lv_obj_t* chat_message_label_ = nullptr;
46:     lv_obj_t* low_battery_popup_ = nullptr;
47: 
48:     const char* battery_icon_ = nullptr;
49:     const char* network_icon_ = nullptr;
50:     bool muted_ = false;
51: 
52:     esp_timer_handle_t notification_timer_ = nullptr;
```

## display.h | 文件开头/全局定义 | 原文件第53-66行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.h
以下为原始源码，不是截图OCR。
```
53:     esp_timer_handle_t update_timer_ = nullptr;
54: 
55:     friend class DisplayLockGuard;
56:     virtual bool Lock(int timeout_ms = 0) = 0;
57:     virtual void Unlock() = 0;
58: 
59:     virtual void Update();
60: };
61: 
62: 
63: class DisplayLockGuard {
64: public:
65:     DisplayLockGuard(Display *display) : display_(display) {
66:         if (!display_->Lock(3000)) {
```

## display.h | 文件开头/全局定义 | 原文件第67-86行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/display.h
以下为原始源码，不是截图OCR。
```
67:             ESP_LOGE("Display", "Failed to lock display");
68:         }
69:     }
70:     ~DisplayLockGuard() {
71:         display_->Unlock();
72:     }
73: 
74: private:
75:     Display *display_;
76: };
77: 
78: class NoDisplay : public Display {
79: private:
80:     virtual bool Lock(int timeout_ms = 0) override {
81:         return true;
82:     }
83:     virtual void Unlock() override {}
84: };
85: 
86: #endif
```

## lcd_display.cc | 文件开头/全局定义 | 原文件第1-16行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
1: #include "lcd_display.h"
2: 
3: #include <vector>
4: #include <font_awesome_symbols.h>
5: #include <esp_log.h>
6: #include <esp_err.h>
7: #include <esp_lvgl_port.h>
8: #include "assets/lang_config.h"
9: 
10: #include "board.h"
11: 
12: #define TAG "LcdDisplay"
13: 
14: LV_FONT_DECLARE(font_awesome_30_4);
15: 
16: SpiLcdDisplay::SpiLcdDisplay(esp_lcd_panel_io_handle_t panel_io, esp_lcd_panel_handle_t panel,
```

## lcd_display.cc | 文件开头/全局定义 | 原文件第17-18行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
17:                            int width, int height, int offset_x, int offset_y, bool mirror_x, bool mirror_y, bool swap_xy,
18:                            DisplayFonts fonts)
```

## lcd_display.cc | LcdDisplay | 原文件第19-30行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
19:     : LcdDisplay(panel_io, panel, fonts) {
20:     width_ = width;
21:     height_ = height;
22: 
23:     // draw white
24:     std::vector<uint16_t> buffer(width_, 0xFFFF);
25:     for (int y = 0; y < height_; y++) {
26:         esp_lcd_panel_draw_bitmap(panel_, 0, y, width_, y + 1, buffer.data());
27:     }
28: 
29:     // Set the display to on
30:     ESP_LOGI(TAG, "Turning display on");
```

## lcd_display.cc | LcdDisplay | 原文件第31-42行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
31:     ESP_ERROR_CHECK(esp_lcd_panel_disp_on_off(panel_, true));
32: 
33:     ESP_LOGI(TAG, "Initialize LVGL library");
34:     lv_init();
35: 
36:     ESP_LOGI(TAG, "Initialize LVGL port");
37:     lvgl_port_cfg_t port_cfg = ESP_LVGL_PORT_INIT_CONFIG();
38:     port_cfg.task_priority = 1;
39:     lvgl_port_init(&port_cfg);
40: 
41:     ESP_LOGI(TAG, "Adding LCD screen");
42:     const lvgl_port_display_cfg_t display_cfg = {
```

## lcd_display.cc | LcdDisplay | 原文件第43-53行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
43:         .io_handle = panel_io_,
44:         .panel_handle = panel_,
45:         .control_handle = nullptr,
46:         .buffer_size = static_cast<uint32_t>(width_ * 10),
47:         .double_buffer = false,
48:         .trans_size = 0,
49:         .hres = static_cast<uint32_t>(width_),
50:         .vres = static_cast<uint32_t>(height_),
51:         .monochrome = false,
52:         .rotation = {
53:             .swap_xy = swap_xy,
```

## lcd_display.cc | LcdDisplay | 原文件第54-67行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
54:             .mirror_x = mirror_x,
55:             .mirror_y = mirror_y,
56:         },
57:         .color_format = LV_COLOR_FORMAT_RGB565,
58:         .flags = {
59:             .buff_dma = 1,
60:             .buff_spiram = 0,
61:             .sw_rotate = 0,
62:             .swap_bytes = 1,
63:             .full_refresh = 0,
64:             .direct_mode = 0,
65:         },
66:     };
67: 
```

## lcd_display.cc | LcdDisplay | 原文件第68-81行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
68:     display_ = lvgl_port_add_disp(&display_cfg);
69:     if (display_ == nullptr) {
70:         ESP_LOGE(TAG, "Failed to add display");
71:         return;
72:     }
73: 
74:     if (offset_x != 0 || offset_y != 0) {
75:         lv_display_set_offset(display_, offset_x, offset_y);
76:     }
77: 
78:     SetupUI();
79: }
80: 
81: // RGB LCD实现
```

## lcd_display.cc | LcdDisplay | 原文件第82-85行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
82: RgbLcdDisplay::RgbLcdDisplay(esp_lcd_panel_io_handle_t panel_io, esp_lcd_panel_handle_t panel,
83:                            int width, int height, int offset_x, int offset_y,
84:                            bool mirror_x, bool mirror_y, bool swap_xy,
85:                            DisplayFonts fonts)
```

## lcd_display.cc | LcdDisplay | 原文件第86-98行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
86:     : LcdDisplay(panel_io, panel, fonts) {
87:     width_ = width;
88:     height_ = height;
89:     
90:     // draw white
91:     std::vector<uint16_t> buffer(width_, 0xFFFF);
92:     for (int y = 0; y < height_; y++) {
93:         esp_lcd_panel_draw_bitmap(panel_, 0, y, width_, y + 1, buffer.data());
94:     }
95: 
96:     ESP_LOGI(TAG, "Initialize LVGL library");
97:     lv_init();
98: 
```

## lcd_display.cc | LcdDisplay | 原文件第99-108行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
99:     ESP_LOGI(TAG, "Initialize LVGL port");
100:     lvgl_port_cfg_t port_cfg = ESP_LVGL_PORT_INIT_CONFIG();
101:     port_cfg.task_priority = 1;
102:     lvgl_port_init(&port_cfg);
103: 
104:     ESP_LOGI(TAG, "Adding LCD screen");
105:     const lvgl_port_display_cfg_t display_cfg = {
106:         .io_handle = panel_io_,
107:         .panel_handle = panel_,
108:         .buffer_size = static_cast<uint32_t>(width_ * 10),
```

## lcd_display.cc | LcdDisplay | 原文件第109-120行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
109:         .double_buffer = true,
110:         .hres = static_cast<uint32_t>(width_),
111:         .vres = static_cast<uint32_t>(height_),
112:         .rotation = {
113:             .swap_xy = swap_xy,
114:             .mirror_x = mirror_x,
115:             .mirror_y = mirror_y,
116:         },
117:         .flags = {
118:             .buff_dma = 1,
119:             .swap_bytes = 0,
120:             .full_refresh = 1,
```

## lcd_display.cc | LcdDisplay | 原文件第121-134行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
121:             .direct_mode = 1,
122:         },
123:     };
124: 
125:     const lvgl_port_display_rgb_cfg_t rgb_cfg = {
126:         .flags = {
127:             .bb_mode = true,
128:             .avoid_tearing = true,
129:         }
130:     };
131:     
132:     display_ = lvgl_port_add_disp_rgb(&display_cfg, &rgb_cfg);
133:     if (display_ == nullptr) {
134:         ESP_LOGE(TAG, "Failed to add RGB display");
```

## lcd_display.cc | LcdDisplay | 原文件第135-152行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
135:         return;
136:     }
137:     
138:     if (offset_x != 0 || offset_y != 0) {
139:         lv_display_set_offset(display_, offset_x, offset_y);
140:     }
141: 
142:     SetupUI();
143: }
144: 
145: LcdDisplay::~LcdDisplay() {
146:     // 然后再清理 LVGL 对象
147:     if (content_ != nullptr) {
148:         lv_obj_del(content_);
149:     }
150:     if (status_bar_ != nullptr) {
151:         lv_obj_del(status_bar_);
152:     }
```

## lcd_display.cc | LcdDisplay | 原文件第153-167行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
153:     if (side_bar_ != nullptr) {
154:         lv_obj_del(side_bar_);
155:     }
156:     if (container_ != nullptr) {
157:         lv_obj_del(container_);
158:     }
159:     if (display_ != nullptr) {
160:         lv_display_delete(display_);
161:     }
162: 
163:     if (panel_ != nullptr) {
164:         esp_lcd_panel_del(panel_);
165:     }
166:     if (panel_io_ != nullptr) {
167:         esp_lcd_panel_io_del(panel_io_);
```

## lcd_display.cc | LcdDisplay | 原文件第168-170行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
168:     }
169: }
170: 
```

## lcd_display.cc | LcdDisplay::Lock | 原文件第171-174行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
171: bool LcdDisplay::Lock(int timeout_ms) {
172:     return lvgl_port_lock(timeout_ms);
173: }
174: 
```

## lcd_display.cc | LcdDisplay::Unlock | 原文件第175-178行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
175: void LcdDisplay::Unlock() {
176:     lvgl_port_unlock();
177: }
178: 
```

## lcd_display.cc | LcdDisplay::SetupUI | 原文件第179-188行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
179: void LcdDisplay::SetupUI() {
180:     DisplayLockGuard lock(this);
181: 
182:     auto screen = lv_screen_active();
183:     lv_obj_set_style_text_font(screen, fonts_.text_font, 0);
184:     lv_obj_set_style_text_color(screen, lv_color_black(), 0);
185: 
186:     /* Container */
187:     container_ = lv_obj_create(screen);
188:     lv_obj_set_size(container_, LV_HOR_RES, LV_VER_RES);
```

## lcd_display.cc | LcdDisplay::SetupUI | 原文件第189-196行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
189:     lv_obj_set_flex_flow(container_, LV_FLEX_FLOW_COLUMN);
190:     lv_obj_set_style_pad_all(container_, 0, 0);
191:     lv_obj_set_style_border_width(container_, 0, 0);
192:     lv_obj_set_style_pad_row(container_, 0, 0);
193: 
194:     /* Status bar */
195:     status_bar_ = lv_obj_create(container_);
196:     lv_obj_set_size(status_bar_, LV_HOR_RES, fonts_.text_font->line_height);
```

## lcd_display.cc | LcdDisplay::SetupUI | 原文件第197-206行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
197:     lv_obj_set_style_radius(status_bar_, 0, 0);
198:     
199:     /* Content */
200:     content_ = lv_obj_create(container_);
201:     lv_obj_set_scrollbar_mode(content_, LV_SCROLLBAR_MODE_OFF);
202:     lv_obj_set_style_radius(content_, 0, 0);
203:     lv_obj_set_width(content_, LV_HOR_RES);
204:     lv_obj_set_flex_grow(content_, 1);
205: 
206:     lv_obj_set_flex_flow(content_, LV_FLEX_FLOW_COLUMN); // 垂直布局（从上到下）
```

## lcd_display.cc | LcdDisplay::SetupUI | 原文件第207-213行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
207:     lv_obj_set_flex_align(content_, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_SPACE_EVENLY); // 子对象居中对齐，等距分布
208: 
209:     emotion_label_ = lv_label_create(content_);
210:     lv_obj_set_style_text_font(emotion_label_, &font_awesome_30_4, 0);
211:     lv_label_set_text(emotion_label_, FONT_AWESOME_AI_CHIP);
212: 
213:     chat_message_label_ = lv_label_create(content_);
```

## lcd_display.cc | LcdDisplay::SetupUI | 原文件第214-220行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
214:     lv_label_set_text(chat_message_label_, "");
215:     lv_obj_set_width(chat_message_label_, LV_HOR_RES * 0.9); // 限制宽度为屏幕宽度的 90%
216:     lv_label_set_long_mode(chat_message_label_, LV_LABEL_LONG_WRAP); // 设置为自动换行模式
217:     lv_obj_set_style_text_align(chat_message_label_, LV_TEXT_ALIGN_CENTER, 0); // 设置文本居中对齐
218: 
219:     /* Status bar */
220:     lv_obj_set_flex_flow(status_bar_, LV_FLEX_FLOW_ROW);
```

## lcd_display.cc | LcdDisplay::SetupUI | 原文件第221-228行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
221:     lv_obj_set_style_pad_all(status_bar_, 0, 0);
222:     lv_obj_set_style_border_width(status_bar_, 0, 0);
223:     lv_obj_set_style_pad_column(status_bar_, 0, 0);
224:     lv_obj_set_style_pad_left(status_bar_, 2, 0);
225:     lv_obj_set_style_pad_right(status_bar_, 2, 0);
226: 
227:     network_label_ = lv_label_create(status_bar_);
228:     lv_label_set_text(network_label_, "");
```

## lcd_display.cc | LcdDisplay::SetupUI | 原文件第229-236行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
229:     lv_obj_set_style_text_font(network_label_, fonts_.icon_font, 0);
230: 
231:     notification_label_ = lv_label_create(status_bar_);
232:     lv_obj_set_flex_grow(notification_label_, 1);
233:     lv_obj_set_style_text_align(notification_label_, LV_TEXT_ALIGN_CENTER, 0);
234:     lv_label_set_text(notification_label_, "");
235:     lv_obj_add_flag(notification_label_, LV_OBJ_FLAG_HIDDEN);
236: 
```

## lcd_display.cc | LcdDisplay::SetupUI | 原文件第237-243行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
237:     status_label_ = lv_label_create(status_bar_);
238:     lv_obj_set_flex_grow(status_label_, 1);
239:     lv_label_set_long_mode(status_label_, LV_LABEL_LONG_SCROLL_CIRCULAR);
240:     lv_obj_set_style_text_align(status_label_, LV_TEXT_ALIGN_CENTER, 0);
241:     lv_label_set_text(status_label_, Lang::Strings::INITIALIZING);
242:     mute_label_ = lv_label_create(status_bar_);
243:     lv_label_set_text(mute_label_, "");
```

## lcd_display.cc | LcdDisplay::SetupUI | 原文件第244-251行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
244:     lv_obj_set_style_text_font(mute_label_, fonts_.icon_font, 0);
245: 
246:     battery_label_ = lv_label_create(status_bar_);
247:     lv_label_set_text(battery_label_, "");
248:     lv_obj_set_style_text_font(battery_label_, fonts_.icon_font, 0);
249: 
250:     low_battery_popup_ = lv_obj_create(screen);
251:     lv_obj_set_scrollbar_mode(low_battery_popup_, LV_SCROLLBAR_MODE_OFF);
```

## lcd_display.cc | LcdDisplay::SetupUI | 原文件第252-256行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
252:     lv_obj_set_size(low_battery_popup_, LV_HOR_RES * 0.9, fonts_.text_font->line_height * 2);
253:     lv_obj_align(low_battery_popup_, LV_ALIGN_BOTTOM_MID, 0, 0);
254:     lv_obj_set_style_bg_color(low_battery_popup_, lv_color_black(), 0);
255:     lv_obj_set_style_radius(low_battery_popup_, 10, 0);
256:     lv_obj_t* low_battery_label = lv_label_create(low_battery_popup_);
```

## lcd_display.cc | LcdDisplay::SetupUI | 原文件第257-262行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
257:     lv_label_set_text(low_battery_label, Lang::Strings::BATTERY_NEED_CHARGE);
258:     lv_obj_set_style_text_color(low_battery_label, lv_color_white(), 0);
259:     lv_obj_center(low_battery_label);
260:     lv_obj_add_flag(low_battery_popup_, LV_OBJ_FLAG_HIDDEN);
261: }
262: 
```

## lcd_display.cc | LcdDisplay::SetEmotion | 原文件第263-276行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
263: void LcdDisplay::SetEmotion(const char* emotion) {
264:     struct Emotion {
265:         const char* icon;
266:         const char* text;
267:     };
268: 
269:     static const std::vector<Emotion> emotions = {
270:         {"😶", "neutral"},
271:         {"🙂", "happy"},
272:         {"😆", "laughing"},
273:         {"😂", "funny"},
274:         {"😔", "sad"},
275:         {"😠", "angry"},
276:         {"😭", "crying"},
```

## lcd_display.cc | LcdDisplay::SetEmotion | 原文件第277-290行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
277:         {"😍", "loving"},
278:         {"😳", "embarrassed"},
279:         {"😯", "surprised"},
280:         {"😱", "shocked"},
281:         {"🤔", "thinking"},
282:         {"😉", "winking"},
283:         {"😎", "cool"},
284:         {"😌", "relaxed"},
285:         {"🤤", "delicious"},
286:         {"😘", "kissy"},
287:         {"😏", "confident"},
288:         {"😴", "sleepy"},
289:         {"😜", "silly"},
290:         {"🙄", "confused"}
```

## lcd_display.cc | LcdDisplay::SetEmotion | 原文件第291-303行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
291:     };
292:     
293:     // 查找匹配的表情
294:     std::string_view emotion_view(emotion);
295:     auto it = std::find_if(emotions.begin(), emotions.end(),
296:         [&emotion_view](const Emotion& e) { return e.text == emotion_view; });
297: 
298:     DisplayLockGuard lock(this);
299:     if (emotion_label_ == nullptr) {
300:         return;
301:     }
302: 
303:     // 如果找到匹配的表情就显示对应图标，否则显示默认的neutral表情
```

## lcd_display.cc | LcdDisplay::SetEmotion | 原文件第304-311行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
304:     lv_obj_set_style_text_font(emotion_label_, fonts_.emoji_font, 0);
305:     if (it != emotions.end()) {
306:         lv_label_set_text(emotion_label_, it->icon);
307:     } else {
308:         lv_label_set_text(emotion_label_, "😶");
309:     }
310: }
311: 
```

## lcd_display.cc | LcdDisplay::SetIcon | 原文件第312-319行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.cc
以下为原始源码，不是截图OCR。
```
312: void LcdDisplay::SetIcon(const char* icon) {
313:     DisplayLockGuard lock(this);
314:     if (emotion_label_ == nullptr) {
315:         return;
316:     }
317:     lv_obj_set_style_text_font(emotion_label_, &font_awesome_30_4, 0);
318:     lv_label_set_text(emotion_label_, icon);
319: }
```

## lcd_display.h | 文件开头/全局定义 | 原文件第1-17行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.h
以下为原始源码，不是截图OCR。
```
1: #ifndef LCD_DISPLAY_H
2: #define LCD_DISPLAY_H
3: 
4: #include "display.h"
5: 
6: #include <esp_lcd_panel_io.h>
7: #include <esp_lcd_panel_ops.h>
8: #include <font_emoji.h>
9: 
10: #include <atomic>
11: 
12: class LcdDisplay : public Display {
13: protected:
14:     esp_lcd_panel_io_handle_t panel_io_ = nullptr;
15:     esp_lcd_panel_handle_t panel_ = nullptr;
16:     
17:     lv_draw_buf_t draw_buf_;
```

## lcd_display.h | 文件开头/全局定义 | 原文件第18-30行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.h
以下为原始源码，不是截图OCR。
```
18:     lv_obj_t* status_bar_ = nullptr;
19:     lv_obj_t* content_ = nullptr;
20:     lv_obj_t* container_ = nullptr;
21:     lv_obj_t* side_bar_ = nullptr;
22: 
23:     DisplayFonts fonts_;
24: 
25:     virtual void SetupUI();
26:     virtual bool Lock(int timeout_ms = 0) override;
27:     virtual void Unlock() override;
28: 
29: protected:
30:     // 添加protected构造函数
```

## lcd_display.h | 文件开头/全局定义 | 原文件第31-31行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.h
以下为原始源码，不是截图OCR。
```
31:     LcdDisplay(esp_lcd_panel_io_handle_t panel_io, esp_lcd_panel_handle_t panel, DisplayFonts fonts)
```

## lcd_display.h | panel_io_ | 原文件第32-43行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.h
以下为原始源码，不是截图OCR。
```
32:         : panel_io_(panel_io), panel_(panel), fonts_(fonts) {}
33:     
34: public:
35:     ~LcdDisplay();
36:     virtual void SetEmotion(const char* emotion) override;
37:     virtual void SetIcon(const char* icon) override;
38: };
39: 
40: // RGB LCD显示器
41: class RgbLcdDisplay : public LcdDisplay {
42: public:
43:     RgbLcdDisplay(esp_lcd_panel_io_handle_t panel_io, esp_lcd_panel_handle_t panel,
```

## lcd_display.h | panel_io_ | 原文件第44-53行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.h
以下为原始源码，不是截图OCR。
```
44:                   int width, int height, int offset_x, int offset_y,
45:                   bool mirror_x, bool mirror_y, bool swap_xy,
46:                   DisplayFonts fonts);
47: };
48: 
49: // MIPI LCD显示器
50: class MipiLcdDisplay : public LcdDisplay {
51: public:
52:     MipiLcdDisplay(esp_lcd_panel_io_handle_t panel_io, esp_lcd_panel_handle_t panel,
53:                    int width, int height, int offset_x, int offset_y,
```

## lcd_display.h | panel_io_ | 原文件第54-63行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.h
以下为原始源码，不是截图OCR。
```
54:                    bool mirror_x, bool mirror_y, bool swap_xy,
55:                    DisplayFonts fonts);
56: };
57: 
58: // // SPI LCD显示器
59: class SpiLcdDisplay : public LcdDisplay {
60: public:
61:     SpiLcdDisplay(esp_lcd_panel_io_handle_t panel_io, esp_lcd_panel_handle_t panel,
62:                   int width, int height, int offset_x, int offset_y,
63:                   bool mirror_x, bool mirror_y, bool swap_xy,
```

## lcd_display.h | panel_io_ | 原文件第64-75行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.h
以下为原始源码，不是截图OCR。
```
64:                   DisplayFonts fonts);
65: };
66: 
67: // QSPI LCD显示器
68: class QspiLcdDisplay : public LcdDisplay {
69: public:
70:     QspiLcdDisplay(esp_lcd_panel_io_handle_t panel_io, esp_lcd_panel_handle_t panel,
71:                    int width, int height, int offset_x, int offset_y,
72:                    bool mirror_x, bool mirror_y, bool swap_xy,
73:                    DisplayFonts fonts);
74: };
75: 
```

## lcd_display.h | panel_io_ | 原文件第76-84行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/lcd_display.h
以下为原始源码，不是截图OCR。
```
76: // MCU8080 LCD显示器
77: class Mcu8080LcdDisplay : public LcdDisplay {
78: public:
79:     Mcu8080LcdDisplay(esp_lcd_panel_io_handle_t panel_io, esp_lcd_panel_handle_t panel,
80:                       int width, int height, int offset_x, int offset_y,
81:                       bool mirror_x, bool mirror_y, bool swap_xy,
82:                       DisplayFonts fonts);
83: };
84: #endif // LCD_DISPLAY_H
```

## oled_display.cc | 文件开头/全局定义 | 原文件第1-16行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
1: #include "oled_display.h"
2: #include "font_awesome_symbols.h"
3: #include "assets/lang_config.h"
4: 
5: #include <string>
6: #include <algorithm>
7: 
8: #include <esp_log.h>
9: #include <esp_err.h>
10: #include <esp_lvgl_port.h>
11: 
12: #define TAG "OledDisplay"
13: 
14: LV_FONT_DECLARE(font_awesome_30_1);
15: 
16: OledDisplay::OledDisplay(esp_lcd_panel_io_handle_t panel_io, esp_lcd_panel_handle_t panel,
```

## oled_display.cc | 文件开头/全局定义 | 原文件第17-17行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
17:     int width, int height, bool mirror_x, bool mirror_y, DisplayFonts fonts)
```

## oled_display.cc | panel_io_ | 原文件第18-29行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
18:     : panel_io_(panel_io), panel_(panel), fonts_(fonts) {
19:     width_ = width;
20:     height_ = height;
21: 
22:     ESP_LOGI(TAG, "Initialize LVGL");
23:     lvgl_port_cfg_t port_cfg = ESP_LVGL_PORT_INIT_CONFIG();
24:     port_cfg.task_priority = 1;
25:     lvgl_port_init(&port_cfg);
26: 
27:     ESP_LOGI(TAG, "Adding LCD screen");
28:     const lvgl_port_display_cfg_t display_cfg = {
29:         .io_handle = panel_io_,
```

## oled_display.cc | panel_io_ | 原文件第30-39行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
30:         .panel_handle = panel_,
31:         .control_handle = nullptr,
32:         .buffer_size = static_cast<uint32_t>(width_ * height_),
33:         .double_buffer = false,
34:         .trans_size = 0,
35:         .hres = static_cast<uint32_t>(width_),
36:         .vres = static_cast<uint32_t>(height_),
37:         .monochrome = true,
38:         .rotation = {
39:             .swap_xy = false,
```

## oled_display.cc | panel_io_ | 原文件第40-53行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
40:             .mirror_x = mirror_x,
41:             .mirror_y = mirror_y,
42:         },
43:         .flags = {
44:             .buff_dma = 1,
45:             .buff_spiram = 0,
46:             .sw_rotate = 0,
47:             .full_refresh = 0,
48:             .direct_mode = 0,
49:         },
50:     };
51: 
52:     display_ = lvgl_port_add_disp(&display_cfg);
53:     if (display_ == nullptr) {
```

## oled_display.cc | panel_io_ | 原文件第54-71行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
54:         ESP_LOGE(TAG, "Failed to add display");
55:         return;
56:     }
57: 
58:     if (height_ == 64) {
59:         SetupUI_128x64();
60:     } else {
61:         SetupUI_128x32();
62:     }
63: }
64: 
65: OledDisplay::~OledDisplay() {
66:     if (content_ != nullptr) {
67:         lv_obj_del(content_);
68:     }
69:     if (status_bar_ != nullptr) {
70:         lv_obj_del(status_bar_);
71:     }
```

## oled_display.cc | panel_io_ | 原文件第72-87行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
72:     if (side_bar_ != nullptr) {
73:         lv_obj_del(side_bar_);
74:     }
75:     if (container_ != nullptr) {
76:         lv_obj_del(container_);
77:     }
78: 
79:     if (panel_ != nullptr) {
80:         esp_lcd_panel_del(panel_);
81:     }
82:     if (panel_io_ != nullptr) {
83:         esp_lcd_panel_io_del(panel_io_);
84:     }
85:     lvgl_port_deinit();
86: }
87: 
```

## oled_display.cc | OledDisplay::Lock | 原文件第88-91行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
88: bool OledDisplay::Lock(int timeout_ms) {
89:     return lvgl_port_lock(timeout_ms);
90: }
91: 
```

## oled_display.cc | OledDisplay::Unlock | 原文件第92-95行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
92: void OledDisplay::Unlock() {
93:     lvgl_port_unlock();
94: }
95: 
```

## oled_display.cc | OledDisplay::SetChatMessage | 原文件第96-106行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
96: void OledDisplay::SetChatMessage(const char* role, const char* content) {
97:     DisplayLockGuard lock(this);
98:     if (chat_message_label_ == nullptr) {
99:         return;
100:     }
101: 
102:     // Replace all newlines with spaces
103:     std::string content_str = content;
104:     std::replace(content_str.begin(), content_str.end(), '\n', ' ');
105: 
106:     if (content_right_ == nullptr) {
```

## oled_display.cc | OledDisplay::SetChatMessage | 原文件第107-117行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
107:         lv_label_set_text(chat_message_label_, content_str.c_str());
108:     } else {
109:         if (content == nullptr || content[0] == '\0') {
110:             lv_obj_add_flag(content_right_, LV_OBJ_FLAG_HIDDEN);
111:         } else {
112:             lv_label_set_text(chat_message_label_, content_str.c_str());
113:             lv_obj_clear_flag(content_right_, LV_OBJ_FLAG_HIDDEN);
114:         }
115:     }
116: }
117: 
```

## oled_display.cc | OledDisplay::SetupUI_128x64 | 原文件第118-127行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
118: void OledDisplay::SetupUI_128x64() {
119:     DisplayLockGuard lock(this);
120: 
121:     auto screen = lv_screen_active();
122:     lv_obj_set_style_text_font(screen, fonts_.text_font, 0);
123:     lv_obj_set_style_text_color(screen, lv_color_black(), 0);
124: 
125:     /* Container */
126:     container_ = lv_obj_create(screen);
127:     lv_obj_set_size(container_, LV_HOR_RES, LV_VER_RES);
```

## oled_display.cc | OledDisplay::SetupUI_128x64 | 原文件第128-136行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
128:     lv_obj_set_flex_flow(container_, LV_FLEX_FLOW_COLUMN);
129:     lv_obj_set_style_pad_all(container_, 0, 0);
130:     lv_obj_set_style_border_width(container_, 0, 0);
131:     lv_obj_set_style_pad_row(container_, 0, 0);
132: 
133:     /* Status bar */
134:     status_bar_ = lv_obj_create(container_);
135:     lv_obj_set_size(status_bar_, LV_HOR_RES, 16);
136:     lv_obj_set_style_border_width(status_bar_, 0, 0);
```

## oled_display.cc | OledDisplay::SetupUI_128x64 | 原文件第137-145行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
137:     lv_obj_set_style_pad_all(status_bar_, 0, 0);
138:     lv_obj_set_style_radius(status_bar_, 0, 0);
139: 
140:     /* Content */
141:     content_ = lv_obj_create(container_);
142:     lv_obj_set_scrollbar_mode(content_, LV_SCROLLBAR_MODE_OFF);
143:     lv_obj_set_style_radius(content_, 0, 0);
144:     lv_obj_set_style_pad_all(content_, 0, 0);
145:     lv_obj_set_width(content_, LV_HOR_RES);
```

## oled_display.cc | OledDisplay::SetupUI_128x64 | 原文件第146-153行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
146:     lv_obj_set_flex_grow(content_, 1);
147:     lv_obj_set_flex_flow(content_, LV_FLEX_FLOW_ROW);
148:     lv_obj_set_style_flex_main_place(content_, LV_FLEX_ALIGN_CENTER, 0);
149: 
150:     // 创建左侧固定宽度的容器
151:     content_left_ = lv_obj_create(content_);
152:     lv_obj_set_size(content_left_, 32, LV_SIZE_CONTENT);  // 固定宽度32像素
153:     lv_obj_set_style_pad_all(content_left_, 0, 0);
```

## oled_display.cc | OledDisplay::SetupUI_128x64 | 原文件第154-162行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
154:     lv_obj_set_style_border_width(content_left_, 0, 0);
155: 
156:     emotion_label_ = lv_label_create(content_left_);
157:     lv_obj_set_style_text_font(emotion_label_, &font_awesome_30_1, 0);
158:     lv_label_set_text(emotion_label_, FONT_AWESOME_AI_CHIP);
159:     lv_obj_center(emotion_label_);
160:     lv_obj_set_style_pad_top(emotion_label_, 8, 0);
161: 
162:     // 创建右侧可扩展的容器
```

## oled_display.cc | OledDisplay::SetupUI_128x64 | 原文件第163-170行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
163:     content_right_ = lv_obj_create(content_);
164:     lv_obj_set_size(content_right_, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
165:     lv_obj_set_style_pad_all(content_right_, 0, 0);
166:     lv_obj_set_style_border_width(content_right_, 0, 0);
167:     lv_obj_set_flex_grow(content_right_, 1);
168:     lv_obj_add_flag(content_right_, LV_OBJ_FLAG_HIDDEN);
169: 
170:     chat_message_label_ = lv_label_create(content_right_);
```

## oled_display.cc | OledDisplay::SetupUI_128x64 | 原文件第171-179行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
171:     lv_label_set_text(chat_message_label_, "");
172:     lv_label_set_long_mode(chat_message_label_, LV_LABEL_LONG_SCROLL_CIRCULAR);
173:     lv_obj_set_style_text_align(chat_message_label_, LV_TEXT_ALIGN_LEFT, 0);
174:     lv_obj_set_width(chat_message_label_, width_ - 32);
175:     lv_obj_set_style_pad_top(chat_message_label_, 14, 0);
176: 
177:     // 延迟一定的时间后开始滚动字幕
178:     static lv_anim_t a;
179:     lv_anim_init(&a);
```

## oled_display.cc | OledDisplay::SetupUI_128x64 | 原文件第180-187行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
180:     lv_anim_set_delay(&a, 1000);
181:     lv_anim_set_repeat_count(&a, LV_ANIM_REPEAT_INFINITE);
182:     lv_obj_set_style_anim(chat_message_label_, &a, LV_PART_MAIN);
183:     lv_obj_set_style_anim_duration(chat_message_label_, lv_anim_speed_clamped(60, 300, 60000), LV_PART_MAIN);
184: 
185:     /* Status bar */
186:     lv_obj_set_flex_flow(status_bar_, LV_FLEX_FLOW_ROW);
187:     lv_obj_set_style_pad_all(status_bar_, 0, 0);
```

## oled_display.cc | OledDisplay::SetupUI_128x64 | 原文件第188-196行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
188:     lv_obj_set_style_border_width(status_bar_, 0, 0);
189:     lv_obj_set_style_pad_column(status_bar_, 0, 0);
190: 
191:     network_label_ = lv_label_create(status_bar_);
192:     lv_label_set_text(network_label_, "");
193:     lv_obj_set_style_text_font(network_label_, fonts_.icon_font, 0);
194: 
195:     notification_label_ = lv_label_create(status_bar_);
196:     lv_obj_set_flex_grow(notification_label_, 1);
```

## oled_display.cc | OledDisplay::SetupUI_128x64 | 原文件第197-203行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
197:     lv_obj_set_style_text_align(notification_label_, LV_TEXT_ALIGN_CENTER, 0);
198:     lv_label_set_text(notification_label_, "");
199:     lv_obj_add_flag(notification_label_, LV_OBJ_FLAG_HIDDEN);
200: 
201:     status_label_ = lv_label_create(status_bar_);
202:     lv_obj_set_flex_grow(status_label_, 1);
203:     lv_label_set_text(status_label_, Lang::Strings::INITIALIZING);
```

## oled_display.cc | OledDisplay::SetupUI_128x64 | 原文件第204-212行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
204:     lv_obj_set_style_text_align(status_label_, LV_TEXT_ALIGN_CENTER, 0);
205: 
206:     mute_label_ = lv_label_create(status_bar_);
207:     lv_label_set_text(mute_label_, "");
208:     lv_obj_set_style_text_font(mute_label_, fonts_.icon_font, 0);
209: 
210:     battery_label_ = lv_label_create(status_bar_);
211:     lv_label_set_text(battery_label_, "");
212:     lv_obj_set_style_text_font(battery_label_, fonts_.icon_font, 0);
```

## oled_display.cc | OledDisplay::SetupUI_128x64 | 原文件第213-218行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
213: 
214:     low_battery_popup_ = lv_obj_create(screen);
215:     lv_obj_set_scrollbar_mode(low_battery_popup_, LV_SCROLLBAR_MODE_OFF);
216:     lv_obj_set_size(low_battery_popup_, LV_HOR_RES * 0.9, fonts_.text_font->line_height * 2);
217:     lv_obj_align(low_battery_popup_, LV_ALIGN_BOTTOM_MID, 0, 0);
218:     lv_obj_set_style_bg_color(low_battery_popup_, lv_color_black(), 0);
```

## oled_display.cc | OledDisplay::SetupUI_128x64 | 原文件第219-226行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
219:     lv_obj_set_style_radius(low_battery_popup_, 10, 0);
220:     lv_obj_t* low_battery_label = lv_label_create(low_battery_popup_);
221:     lv_label_set_text(low_battery_label, Lang::Strings::BATTERY_NEED_CHARGE);
222:     lv_obj_set_style_text_color(low_battery_label, lv_color_white(), 0);
223:     lv_obj_center(low_battery_label);
224:     lv_obj_add_flag(low_battery_popup_, LV_OBJ_FLAG_HIDDEN);
225: }
226: 
```

## oled_display.cc | OledDisplay::SetupUI_128x32 | 原文件第227-236行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
227: void OledDisplay::SetupUI_128x32() {
228:     DisplayLockGuard lock(this);
229: 
230:     auto screen = lv_screen_active();
231:     lv_obj_set_style_text_font(screen, fonts_.text_font, 0);
232: 
233:     /* Container */
234:     container_ = lv_obj_create(screen);
235:     lv_obj_set_size(container_, LV_HOR_RES, LV_VER_RES);
236:     lv_obj_set_flex_flow(container_, LV_FLEX_FLOW_ROW);
```

## oled_display.cc | OledDisplay::SetupUI_128x32 | 原文件第237-245行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
237:     lv_obj_set_style_pad_all(container_, 0, 0);
238:     lv_obj_set_style_border_width(container_, 0, 0);
239:     lv_obj_set_style_pad_column(container_, 0, 0);
240: 
241:     /* Emotion label on the left side */
242:     content_ = lv_obj_create(container_);
243:     lv_obj_set_size(content_, 32, 32);
244:     lv_obj_set_style_pad_all(content_, 0, 0);
245:     lv_obj_set_style_border_width(content_, 0, 0);
```

## oled_display.cc | OledDisplay::SetupUI_128x32 | 原文件第246-255行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
246:     lv_obj_set_style_radius(content_, 0, 0);
247: 
248:     emotion_label_ = lv_label_create(content_);
249:     lv_obj_set_style_text_font(emotion_label_, &font_awesome_30_1, 0);
250:     lv_label_set_text(emotion_label_, FONT_AWESOME_AI_CHIP);
251:     lv_obj_center(emotion_label_);
252: 
253:     /* Right side */
254:     side_bar_ = lv_obj_create(container_);
255:     lv_obj_set_size(side_bar_, width_ - 32, 32);
```

## oled_display.cc | OledDisplay::SetupUI_128x32 | 原文件第256-264行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
256:     lv_obj_set_flex_flow(side_bar_, LV_FLEX_FLOW_COLUMN);
257:     lv_obj_set_style_pad_all(side_bar_, 0, 0);
258:     lv_obj_set_style_border_width(side_bar_, 0, 0);
259:     lv_obj_set_style_radius(side_bar_, 0, 0);
260:     lv_obj_set_style_pad_row(side_bar_, 0, 0);
261: 
262:     /* Status bar */
263:     status_bar_ = lv_obj_create(side_bar_);
264:     lv_obj_set_size(status_bar_, width_ - 32, 16);
```

## oled_display.cc | OledDisplay::SetupUI_128x32 | 原文件第265-272行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
265:     lv_obj_set_style_radius(status_bar_, 0, 0);
266:     lv_obj_set_flex_flow(status_bar_, LV_FLEX_FLOW_ROW);
267:     lv_obj_set_style_pad_all(status_bar_, 0, 0);
268:     lv_obj_set_style_border_width(status_bar_, 0, 0);
269:     lv_obj_set_style_pad_column(status_bar_, 0, 0);
270: 
271:     status_label_ = lv_label_create(status_bar_);
272:     lv_obj_set_flex_grow(status_label_, 1);
```

## oled_display.cc | OledDisplay::SetupUI_128x32 | 原文件第273-281行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
273:     lv_obj_set_style_pad_left(status_label_, 2, 0);
274:     lv_label_set_text(status_label_, Lang::Strings::INITIALIZING);
275: 
276:     notification_label_ = lv_label_create(status_bar_);
277:     lv_obj_set_flex_grow(notification_label_, 1);
278:     lv_obj_set_style_pad_left(notification_label_, 2, 0);
279:     lv_label_set_text(notification_label_, "");
280:     lv_obj_add_flag(notification_label_, LV_OBJ_FLAG_HIDDEN);
281: 
```

## oled_display.cc | OledDisplay::SetupUI_128x32 | 原文件第282-290行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
282:     mute_label_ = lv_label_create(status_bar_);
283:     lv_label_set_text(mute_label_, "");
284:     lv_obj_set_style_text_font(mute_label_, fonts_.icon_font, 0);
285: 
286:     network_label_ = lv_label_create(status_bar_);
287:     lv_label_set_text(network_label_, "");
288:     lv_obj_set_style_text_font(network_label_, fonts_.icon_font, 0);
289: 
290:     battery_label_ = lv_label_create(status_bar_);
```

## oled_display.cc | OledDisplay::SetupUI_128x32 | 原文件第291-297行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
291:     lv_label_set_text(battery_label_, "");
292:     lv_obj_set_style_text_font(battery_label_, fonts_.icon_font, 0);
293: 
294:     chat_message_label_ = lv_label_create(side_bar_);
295:     lv_obj_set_size(chat_message_label_, width_ - 32, LV_SIZE_CONTENT);
296:     lv_obj_set_style_pad_left(chat_message_label_, 2, 0);
297:     lv_label_set_long_mode(chat_message_label_, LV_LABEL_LONG_SCROLL_CIRCULAR);
```

## oled_display.cc | OledDisplay::SetupUI_128x32 | 原文件第298-307行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
298:     lv_label_set_text(chat_message_label_, "");
299: 
300:     // 延迟一定的时间后开始滚动字幕
301:     static lv_anim_t a;
302:     lv_anim_init(&a);
303:     lv_anim_set_delay(&a, 1000);
304:     lv_anim_set_repeat_count(&a, LV_ANIM_REPEAT_INFINITE);
305:     lv_obj_set_style_anim(chat_message_label_, &a, LV_PART_MAIN);
306:     lv_obj_set_style_anim_duration(chat_message_label_, lv_anim_speed_clamped(60, 300, 60000), LV_PART_MAIN);
307: }
```

## oled_display.cc | OledDisplay::SetupUI_128x32 | 原文件第308-308行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.cc
以下为原始源码，不是截图OCR。
```
308: 
```

## oled_display.h | 文件开头/全局定义 | 原文件第1-16行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.h
以下为原始源码，不是截图OCR。
```
1: #ifndef OLED_DISPLAY_H
2: #define OLED_DISPLAY_H
3: 
4: #include "display.h"
5: 
6: #include <esp_lcd_panel_io.h>
7: #include <esp_lcd_panel_ops.h>
8: 
9: class OledDisplay : public Display {
10: private:
11:     esp_lcd_panel_io_handle_t panel_io_ = nullptr;
12:     esp_lcd_panel_handle_t panel_ = nullptr;
13: 
14:     lv_obj_t* status_bar_ = nullptr;
15:     lv_obj_t* content_ = nullptr;
16:     lv_obj_t* content_left_ = nullptr;
```

## oled_display.h | 文件开头/全局定义 | 原文件第17-29行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.h
以下为原始源码，不是截图OCR。
```
17:     lv_obj_t* content_right_ = nullptr;
18:     lv_obj_t* container_ = nullptr;
19:     lv_obj_t* side_bar_ = nullptr;
20: 
21:     DisplayFonts fonts_;
22: 
23:     virtual bool Lock(int timeout_ms = 0) override;
24:     virtual void Unlock() override;
25: 
26:     void SetupUI_128x64();
27:     void SetupUI_128x32();
28: 
29: public:
```

## oled_display.h | 文件开头/全局定义 | 原文件第30-37行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/display/oled_display.h
以下为原始源码，不是截图OCR。
```
30:     OledDisplay(esp_lcd_panel_io_handle_t panel_io, esp_lcd_panel_handle_t panel, int width, int height, bool mirror_x, bool mirror_y,
31:                 DisplayFonts fonts);
32:     ~OledDisplay();
33: 
34:     virtual void SetChatMessage(const char* role, const char* content) override;
35: };
36: 
37: #endif // OLED_DISPLAY_H
```

## thing.cc | 文件开头/全局定义 | 原文件第1-12行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.cc
以下为原始源码，不是截图OCR。
```
1: #include "thing.h"
2: #include "application.h"
3: 
4: #include <esp_log.h>
5: 
6: #define TAG "Thing"
7: 
8: 
9: namespace iot {
10: 
11: static std::map<std::string, std::function<Thing*()>>* thing_creators = nullptr;
12: 
```

## thing.cc | RegisterThing | 原文件第13-19行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.cc
以下为原始源码，不是截图OCR。
```
13: void RegisterThing(const std::string& type, std::function<Thing*()> creator) {
14:     if (thing_creators == nullptr) {
15:         thing_creators = new std::map<std::string, std::function<Thing*()>>();
16:     }
17:     (*thing_creators)[type] = creator;
18: }
19: 
```

## thing.cc | CreateThing | 原文件第20-28行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.cc
以下为原始源码，不是截图OCR。
```
20: Thing* CreateThing(const std::string& type) {
21:     auto creator = thing_creators->find(type);
22:     if (creator == thing_creators->end()) {
23:         ESP_LOGE(TAG, "Thing type not found: %s", type.c_str());
24:         return nullptr;
25:     }
26:     return creator->second();
27: }
28: 
```

## thing.cc | Thing::GetDescriptorJson | 原文件第29-38行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.cc
以下为原始源码，不是截图OCR。
```
29: std::string Thing::GetDescriptorJson() {
30:     std::string json_str = "{";
31:     json_str += "\"name\":\"" + name_ + "\",";
32:     json_str += "\"description\":\"" + description_ + "\",";
33:     json_str += "\"properties\":" + properties_.GetDescriptorJson() + ",";
34:     json_str += "\"methods\":" + methods_.GetDescriptorJson();
35:     json_str += "}";
36:     return json_str;
37: }
38: 
```

## thing.cc | Thing::GetStateJson | 原文件第39-46行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.cc
以下为原始源码，不是截图OCR。
```
39: std::string Thing::GetStateJson() {
40:     std::string json_str = "{";
41:     json_str += "\"name\":\"" + name_ + "\",";
42:     json_str += "\"state\":" + properties_.GetStateJson();
43:     json_str += "}";
44:     return json_str;
45: }
46: 
```

## thing.cc | Thing::Invoke | 原文件第47-54行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.cc
以下为原始源码，不是截图OCR。
```
47: void Thing::Invoke(const cJSON* command) {
48:     auto method_name = cJSON_GetObjectItem(command, "method");
49:     auto input_params = cJSON_GetObjectItem(command, "parameters");
50: 
51:     try {
52:         auto& method = methods_[method_name->valuestring];
53:         for (auto& param : method.parameters()) {
54:             auto input_param = cJSON_GetObjectItem(input_params, param.name().c_str());
```

## thing.cc | Thing::Invoke | 原文件第55-61行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.cc
以下为原始源码，不是截图OCR。
```
55:             if (param.required() && input_param == nullptr) {
56:                 throw std::runtime_error("Parameter " + param.name() + " is required");
57:             }
58:             if (param.type() == kValueTypeNumber) {
59:                 param.set_number(input_param->valueint);
60:             } else if (param.type() == kValueTypeString) {
61:                 param.set_string(input_param->valuestring);
```

## thing.cc | Thing::Invoke | 原文件第62-74行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.cc
以下为原始源码，不是截图OCR。
```
62:             } else if (param.type() == kValueTypeBoolean) {
63:                 param.set_boolean(input_param->valueint == 1);
64:             }
65:         }
66: 
67:         Application::GetInstance().Schedule([&method]() {
68:             method.Invoke();
69:         });
70:     } catch (const std::runtime_error& e) {
71:         ESP_LOGE(TAG, "Method not found: %s", method_name->valuestring);
72:         return;
73:     }
74: }
```

## thing.cc | Thing::Invoke | 原文件第75-77行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.cc
以下为原始源码，不是截图OCR。
```
75: 
76: 
77: } // namespace iot
```

## thing.h | 文件开头/全局定义 | 原文件第1-23行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
1: #ifndef THING_H
2: #define THING_H
3: 
4: #include <string>
5: #include <map>
6: #include <functional>
7: #include <vector>
8: #include <stdexcept>
9: #include <cJSON.h>
10: 
11: namespace iot {
12: 
13: enum ValueType {
14:     kValueTypeBoolean,
15:     kValueTypeNumber,
16:     kValueTypeString
17: };
18: 
19: class Property {
20: private:
21:     std::string name_;
22:     std::string description_;
23:     ValueType type_;
```

## thing.h | 文件开头/全局定义 | 原文件第24-30行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
24:     std::function<bool()> boolean_getter_;
25:     std::function<int()> number_getter_;
26:     std::function<std::string()> string_getter_;
27: 
28: public:
29:     Property(const std::string& name, const std::string& description, std::function<bool()> getter) :
30:         name_(name), description_(description), type_(kValueTypeBoolean), boolean_getter_(getter) {}
```

## thing.h | 文件开头/全局定义 | 原文件第31-35行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
31:     Property(const std::string& name, const std::string& description, std::function<int()> getter) :
32:         name_(name), description_(description), type_(kValueTypeNumber), number_getter_(getter) {}
33:     Property(const std::string& name, const std::string& description, std::function<std::string()> getter) :
34:         name_(name), description_(description), type_(kValueTypeString), string_getter_(getter) {}
35: 
```

## thing.h | 文件开头/全局定义 | 原文件第36-43行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
36:     const std::string& name() const { return name_; }
37:     const std::string& description() const { return description_; }
38:     ValueType type() const { return type_; }
39: 
40:     bool boolean() const { return boolean_getter_(); }
41:     int number() const { return number_getter_(); }
42:     std::string string() const { return string_getter_(); }
43: 
```

## thing.h | GetDescriptorJson | 原文件第44-51行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
44:     std::string GetDescriptorJson() {
45:         std::string json_str = "{";
46:         json_str += "\"description\":\"" + description_ + "\",";
47:         if (type_ == kValueTypeBoolean) {
48:             json_str += "\"type\":\"boolean\"";
49:         } else if (type_ == kValueTypeNumber) {
50:             json_str += "\"type\":\"number\"";
51:         } else if (type_ == kValueTypeString) {
```

## thing.h | GetDescriptorJson | 原文件第52-57行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
52:             json_str += "\"type\":\"string\"";
53:         }
54:         json_str += "}";
55:         return json_str;
56:     }
57: 
```

## thing.h | GetStateJson | 原文件第58-69行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
58:     std::string GetStateJson() {
59:         if (type_ == kValueTypeBoolean) {
60:             return boolean_getter_() ? "true" : "false";
61:         } else if (type_ == kValueTypeNumber) {
62:             return std::to_string(number_getter_());
63:         } else if (type_ == kValueTypeString) {
64:             return "\"" + string_getter_() + "\"";
65:         }
66:         return "null";
67:     }
68: };
69: 
```

## thing.h | GetStateJson | 原文件第70-77行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
70: class PropertyList {
71: private:
72:     std::vector<Property> properties_;
73: 
74: public:
75:     PropertyList() = default;
76:     PropertyList(const std::vector<Property>& properties) : properties_(properties) {}
77: 
```

## thing.h | AddBooleanProperty | 原文件第78-80行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
78:     void AddBooleanProperty(const std::string& name, const std::string& description, std::function<bool()> getter) {
79:         properties_.push_back(Property(name, description, getter));
80:     }
```

## thing.h | AddNumberProperty | 原文件第81-83行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
81:     void AddNumberProperty(const std::string& name, const std::string& description, std::function<int()> getter) {
82:         properties_.push_back(Property(name, description, getter));
83:     }
```

## thing.h | AddStringProperty | 原文件第84-92行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
84:     void AddStringProperty(const std::string& name, const std::string& description, std::function<std::string()> getter) {
85:         properties_.push_back(Property(name, description, getter));
86:     }
87: 
88:     const Property& operator[](const std::string& name) const {
89:         for (auto& property : properties_) {
90:             if (property.name() == name) {
91:                 return property;
92:             }
```

## thing.h | AddStringProperty | 原文件第93-96行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
93:         }
94:         throw std::runtime_error("Property not found: " + name);
95:     }
96: 
```

## thing.h | GetDescriptorJson | 原文件第97-108行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
97:     std::string GetDescriptorJson() {
98:         std::string json_str = "{";
99:         for (auto& property : properties_) {
100:             json_str += "\"" + property.name() + "\":" + property.GetDescriptorJson() + ",";
101:         }
102:         if (json_str.back() == ',') {
103:             json_str.pop_back();
104:         }
105:         json_str += "}";
106:         return json_str;
107:     }
108: 
```

## thing.h | GetStateJson | 原文件第109-121行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
109:     std::string GetStateJson() {
110:         std::string json_str = "{";
111:         for (auto& property : properties_) {
112:             json_str += "\"" + property.name() + "\":" + property.GetStateJson() + ",";
113:         }
114:         if (json_str.back() == ',') {
115:             json_str.pop_back();
116:         }
117:         json_str += "}";
118:         return json_str;
119:     }
120: };
121: 
```

## thing.h | GetStateJson | 原文件第122-133行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
122: class Parameter {
123: private:
124:     std::string name_;
125:     std::string description_;
126:     ValueType type_;
127:     bool required_;
128:     bool boolean_;
129:     int number_;
130:     std::string string_;
131: 
132: public:
133:     Parameter(const std::string& name, const std::string& description, ValueType type, bool required = true) :
```

## thing.h | GetStateJson | 原文件第134-142行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
134:         name_(name), description_(description), type_(type), required_(required) {}
135: 
136:     const std::string& name() const { return name_; }
137:     const std::string& description() const { return description_; }
138:     ValueType type() const { return type_; }
139:     bool required() const { return required_; }
140: 
141:     bool boolean() const { return boolean_; }
142:     int number() const { return number_; }
```

## thing.h | GetStateJson | 原文件第143-144行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
143:     const std::string& string() const { return string_; }
144: 
```

## thing.h | set_boolean | 原文件第145-145行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
145:     void set_boolean(bool value) { boolean_ = value; }
```

## thing.h | set_number | 原文件第146-146行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
146:     void set_number(int value) { number_ = value; }
```

## thing.h | set_string | 原文件第147-148行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
147:     void set_string(const std::string& value) { string_ = value; }
148: 
```

## thing.h | GetDescriptorJson | 原文件第149-156行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
149:     std::string GetDescriptorJson() {
150:         std::string json_str = "{";
151:         json_str += "\"description\":\"" + description_ + "\",";
152:         if (type_ == kValueTypeBoolean) {
153:             json_str += "\"type\":\"boolean\"";
154:         } else if (type_ == kValueTypeNumber) {
155:             json_str += "\"type\":\"number\"";
156:         } else if (type_ == kValueTypeString) {
```

## thing.h | GetDescriptorJson | 原文件第157-170行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
157:             json_str += "\"type\":\"string\"";
158:         }
159:         json_str += "}";
160:         return json_str;
161:     }
162: };
163: 
164: class ParameterList {
165: private:
166:     std::vector<Parameter> parameters_;
167: 
168: public:
169:     ParameterList() = default;
170:     ParameterList(const std::vector<Parameter>& parameters) : parameters_(parameters) {}
```

## thing.h | AddParameter | 原文件第171-181行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
171:     void AddParameter(const Parameter& parameter) {
172:         parameters_.push_back(parameter);
173:     }
174: 
175:     const Parameter& operator[](const std::string& name) const {
176:         for (auto& parameter : parameters_) {
177:             if (parameter.name() == name) {
178:                 return parameter;
179:             }
180:         }
181:         throw std::runtime_error("Parameter not found: " + name);
```

## thing.h | AddParameter | 原文件第182-184行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
182:     }
183: 
184:     // iterator
```

## thing.h | begin | 原文件第185-185行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
185:     auto begin() { return parameters_.begin(); }
```

## thing.h | end | 原文件第186-187行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
186:     auto end() { return parameters_.end(); }
187: 
```

## thing.h | GetDescriptorJson | 原文件第188-200行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
188:     std::string GetDescriptorJson() {
189:         std::string json_str = "{";
190:         for (auto& parameter : parameters_) {
191:             json_str += "\"" + parameter.name() + "\":" + parameter.GetDescriptorJson() + ",";
192:         }
193:         if (json_str.back() == ',') {
194:             json_str.pop_back();
195:         }
196:         json_str += "}";
197:         return json_str;
198:     }
199: };
200: 
```

## thing.h | GetDescriptorJson | 原文件第201-209行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
201: class Method {
202: private:
203:     std::string name_;
204:     std::string description_;
205:     ParameterList parameters_;
206:     std::function<void(const ParameterList&)> callback_;
207: 
208: public:
209:     Method(const std::string& name, const std::string& description, const ParameterList& parameters, std::function<void(const ParameterList&)> callback) :
```

## thing.h | GetDescriptorJson | 原文件第210-215行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
210:         name_(name), description_(description), parameters_(parameters), callback_(callback) {}
211: 
212:     const std::string& name() const { return name_; }
213:     const std::string& description() const { return description_; }
214:     ParameterList& parameters() { return parameters_; }
215: 
```

## thing.h | GetDescriptorJson | 原文件第216-223行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
216:     std::string GetDescriptorJson() {
217:         std::string json_str = "{";
218:         json_str += "\"description\":\"" + description_ + "\",";
219:         json_str += "\"parameters\":" + parameters_.GetDescriptorJson();
220:         json_str += "}";
221:         return json_str;
222:     }
223: 
```

## thing.h | Invoke | 原文件第224-236行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
224:     void Invoke() {
225:         callback_(parameters_);
226:     }
227: };
228: 
229: class MethodList {
230: private:
231:     std::vector<Method> methods_;
232: 
233: public:
234:     MethodList() = default;
235:     MethodList(const std::vector<Method>& methods) : methods_(methods) {}
236: 
```

## thing.h | AddMethod | 原文件第237-243行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
237:     void AddMethod(const std::string& name, const std::string& description, const ParameterList& parameters, std::function<void(const ParameterList&)> callback) {
238:         methods_.push_back(Method(name, description, parameters, callback));
239:     }
240: 
241:     Method& operator[](const std::string& name) {
242:         for (auto& method : methods_) {
243:             if (method.name() == name) {
```

## thing.h | AddMethod | 原文件第244-249行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
244:                 return method;
245:             }
246:         }
247:         throw std::runtime_error("Method not found: " + name);
248:     }
249: 
```

## thing.h | GetDescriptorJson | 原文件第250-263行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
250:     std::string GetDescriptorJson() {
251:         std::string json_str = "{";
252:         for (auto& method : methods_) {
253:             json_str += "\"" + method.name() + "\":" + method.GetDescriptorJson() + ",";
254:         }
255:         if (json_str.back() == ',') {
256:             json_str.pop_back();
257:         }
258:         json_str += "}";
259:         return json_str;
260:     }
261: };
262: 
263: class Thing {
```

## thing.h | GetDescriptorJson | 原文件第264-273行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
264: public:
265:     Thing(const std::string& name, const std::string& description) :
266:         name_(name), description_(description) {}
267:     virtual ~Thing() = default;
268: 
269:     virtual std::string GetDescriptorJson();
270:     virtual std::string GetStateJson();
271:     virtual void Invoke(const cJSON* command);
272: 
273:     const std::string& name() const { return name_; }
```

## thing.h | GetDescriptorJson | 原文件第274-288行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
274:     const std::string& description() const { return description_; }
275: 
276: protected:
277:     PropertyList properties_;
278:     MethodList methods_;
279: 
280: private:
281:     std::string name_;
282:     std::string description_;
283: };
284: 
285: 
286: void RegisterThing(const std::string& type, std::function<Thing*()> creator);
287: Thing* CreateThing(const std::string& type);
288: 
```

## thing.h | GetDescriptorJson | 原文件第289-300行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing.h
以下为原始源码，不是截图OCR。
```
289: #define DECLARE_THING(TypeName) \
290:     static iot::Thing* Create##TypeName() { \
291:         return new iot::TypeName(); \
292:     } \
293:     static bool Register##TypeNameHelper = []() { \
294:         RegisterThing(#TypeName, Create##TypeName); \
295:         return true; \
296:     }();
297: 
298: } // namespace iot
299: 
300: #endif // THING_H
```

## battery.cc | 文件开头/全局定义 | 原文件第1-19行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/battery.cc
以下为原始源码，不是截图OCR。
```
1: #include "iot/thing.h"
2: #include "board.h"
3: 
4: #include <esp_log.h>
5: 
6: #define TAG "Battery"
7: 
8: namespace iot {
9: 
10: // 这里仅定义 Battery 的属性和方法，不包含具体的实现
11: class Battery : public Thing {
12: private:
13:     int level_ = 0;
14:     bool charging_ = false;
15:     bool discharging_ = false;
16: 
17: public:
18:     Battery() : Thing("Battery", "电池管理") {
19:         // 定义设备的属性
```

## battery.cc | 文件开头/全局定义 | 原文件第20-29行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/battery.cc
以下为原始源码，不是截图OCR。
```
20:         properties_.AddNumberProperty("level", "当前电量百分比", [this]() -> int {
21:             auto& board = Board::GetInstance();
22:             if (board.GetBatteryLevel(level_, charging_, discharging_)) {
23:                 return level_;
24:             }
25:             return 0;
26:         });
27:         properties_.AddBooleanProperty("charging", "是否充电中", [this]() -> int {
28:             return charging_;
29:         });
```

## battery.cc | 文件开头/全局定义 | 原文件第30-35行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/battery.cc
以下为原始源码，不是截图OCR。
```
30:     }
31: };
32: 
33: } // namespace iot
34: 
35: DECLARE_THING(Battery);
```

## blaklight.cc | 文件开头/全局定义 | 原文件第1-16行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/blaklight.cc
以下为原始源码，不是截图OCR。
```
1: #include "iot/thing.h"
2: #include "board.h"
3: #include "display/lcd_display.h"
4: #include "settings.h"
5: 
6: #include <esp_log.h>
7: 
8: #define TAG "Backlight"
9: 
10: namespace iot {
11: 
12: // 这里仅定义 Backlight 的属性和方法，不包含具体的实现
13: class Backlight : public Thing {
14: public:
15:     Backlight() : Thing("Backlight", "屏幕背光") {
16:         // 定义设备的属性
```

## blaklight.cc | 文件开头/全局定义 | 原文件第17-24行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/blaklight.cc
以下为原始源码，不是截图OCR。
```
17:         properties_.AddNumberProperty("brightness", "当前亮度百分比", [this]() -> int {
18:             // 这里可以添加获取当前亮度的逻辑
19:             auto backlight = Board::GetInstance().GetBacklight();
20:             return backlight ? backlight->brightness() : 0;
21:         });
22: 
23:         // 定义设备可以被远程执行的指令
24:         methods_.AddMethod("SetBrightness", "设置亮度", ParameterList({
```

## blaklight.cc | 文件开头/全局定义 | 原文件第25-32行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/blaklight.cc
以下为原始源码，不是截图OCR。
```
25:             Parameter("brightness", "0到100之间的整数", kValueTypeNumber, true)
26:         }), [this](const ParameterList& parameters) {
27:             uint8_t brightness = static_cast<uint8_t>(parameters["brightness"].number());
28:             auto backlight = Board::GetInstance().GetBacklight();
29:             if (backlight) {
30:                 backlight->SetBrightness(brightness, true);
31:             }
32:         });
```

## blaklight.cc | 文件开头/全局定义 | 原文件第33-38行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/blaklight.cc
以下为原始源码，不是截图OCR。
```
33:     }
34: };
35: 
36: } // namespace iot
37: 
38: DECLARE_THING(Backlight);
```

## lamp.cc | 文件开头/全局定义 | 原文件第1-20行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/lamp.cc
以下为原始源码，不是截图OCR。
```
1: #include "iot/thing.h"
2: #include "board.h"
3: #include "audio_codec.h"
4: 
5: #include <driver/gpio.h>
6: #include <esp_log.h>
7: 
8: #define TAG "Lamp"
9: 
10: namespace iot {
11: 
12: // 这里仅定义 Lamp 的属性和方法，不包含具体的实现
13: class Lamp : public Thing {
14: private:
15: #ifdef CONFIG_IDF_TARGET_ESP32
16:     gpio_num_t gpio_num_ = GPIO_NUM_35;
17: #else
18:     gpio_num_t gpio_num_ = GPIO_NUM_18;
19: #endif
20:     bool power_ = false;
```

## lamp.cc | 文件开头/全局定义 | 原文件第21-21行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/lamp.cc
以下为原始源码，不是截图OCR。
```
21: 
```

## lamp.cc | InitializeGpio | 原文件第22-32行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/lamp.cc
以下为原始源码，不是截图OCR。
```
22:     void InitializeGpio() {
23:         gpio_config_t config = {
24:             .pin_bit_mask = (1ULL << gpio_num_),
25:             .mode = GPIO_MODE_OUTPUT,
26:             .pull_up_en = GPIO_PULLUP_DISABLE,
27:             .pull_down_en = GPIO_PULLDOWN_DISABLE,
28:             .intr_type = GPIO_INTR_DISABLE,
29:         };
30:         ESP_ERROR_CHECK(gpio_config(&config));
31:         gpio_set_level(gpio_num_, 0);
32:     }
```

## lamp.cc | InitializeGpio | 原文件第33-45行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/lamp.cc
以下为原始源码，不是截图OCR。
```
33: 
34: public:
35:     Lamp() : Thing("Lamp", "一个测试用的灯"), power_(false) {
36:         InitializeGpio();
37: 
38:         // 定义设备的属性
39:         properties_.AddBooleanProperty("power", "灯是否打开", [this]() -> bool {
40:             return power_;
41:         });
42: 
43:         // 定义设备可以被远程执行的指令
44:         methods_.AddMethod("TurnOn", "打开灯", ParameterList(), [this](const ParameterList& parameters) {
45:             power_ = true;
```

## lamp.cc | InitializeGpio | 原文件第46-58行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/lamp.cc
以下为原始源码，不是截图OCR。
```
46:             gpio_set_level(gpio_num_, 1);
47:         });
48: 
49:         methods_.AddMethod("TurnOff", "关闭灯", ParameterList(), [this](const ParameterList& parameters) {
50:             power_ = false;
51:             gpio_set_level(gpio_num_, 0);
52:         });
53:     }
54: };
55: 
56: } // namespace iot
57: 
58: DECLARE_THING(Lamp);
```

## roboticarm_V_1_0.cc | 文件开头/全局定义 | 原文件第1-15行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/roboticarm_V_1_0.cc
以下为原始源码，不是截图OCR。
```
1: #include "iot/thing.h"
2: #include "board.h"
3: #include "audio_codec.h"
4: 
5: #include <driver/gpio.h>
6: #include <driver/uart.h>
7: #include <esp_log.h>
8: 
9: #define TAG "RoboticArm"
10: 
11: namespace iot {
12: 
13: // 这里仅定义 RoboticArm 的属性和方法，不包含具体的实现
14: class RoboticArm: public Thing {
15: private:
```

## roboticarm_V_1_0.cc | InitializeGpio | 原文件第16-25行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/roboticarm_V_1_0.cc
以下为原始源码，不是截图OCR。
```
16:     void InitializeGpio() {
17:             // 初始化 UART0，使用 GPIO43 和 GPIO44
18:         uart_config_t uart_config = {
19:         .baud_rate = 115200,
20:         .data_bits = UART_DATA_8_BITS,
21:         .parity = UART_PARITY_DISABLE,
22:         .stop_bits = UART_STOP_BITS_1,
23:         .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
24:         .rx_flow_ctrl_thresh = 122,
25:         };
```

## roboticarm_V_1_0.cc | InitializeGpio | 原文件第26-35行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/roboticarm_V_1_0.cc
以下为原始源码，不是截图OCR。
```
26:         uart_param_config(UART_NUM_0, &uart_config);
27:         uart_set_pin(UART_NUM_0, GPIO_NUM_43, GPIO_NUM_44, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE);
28:         uart_driver_install(UART_NUM_0, 1024, 0, 0, NULL, 0);
29:     }
30: 
31: public:
32:     RoboticArm() : Thing("RoboticArm", "机械臂") {
33:         InitializeGpio();
34: 
35:         // 定义设备可以被远程执行的指令
```

## roboticarm_V_1_0.cc | InitializeGpio | 原文件第36-43行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/roboticarm_V_1_0.cc
以下为原始源码，不是截图OCR。
```
36:         methods_.AddMethod("Stands Upright", "直立", ParameterList(), [this](const ParameterList& parameters) {
37:             uart_write_bytes(UART_NUM_0, "$DJR!", 5);
38:         });
39: 
40:         methods_.AddMethod("Grab", "夹取", ParameterList(), [this](const ParameterList& parameters) {
41:             uart_write_bytes(UART_NUM_0, "$JQ!", 4);
42:         });
43: 
```

## roboticarm_V_1_0.cc | InitializeGpio | 原文件第44-51行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/roboticarm_V_1_0.cc
以下为原始源码，不是截图OCR。
```
44:         methods_.AddMethod("Place", "放置", ParameterList(), [this](const ParameterList& parameters) {
45:             uart_write_bytes(UART_NUM_0, "$FX!", 4);
46:         });
47: 
48:         methods_.AddMethod("Restract", "蜷缩", ParameterList(), [this](const ParameterList& parameters) {
49:             uart_write_bytes(UART_NUM_0, "$QS!", 4);
50:         });
51: 
```

## roboticarm_V_1_0.cc | InitializeGpio | 原文件第52-59行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/roboticarm_V_1_0.cc
以下为原始源码，不是截图OCR。
```
52:         methods_.AddMethod("Grab Left", "前抓", ParameterList(), [this](const ParameterList& parameters) {
53:             uart_write_bytes(UART_NUM_0, "$QC!", 4);
54:         });
55: 
56:         methods_.AddMethod("Grab Left", "左抓", ParameterList(), [this](const ParameterList& parameters) {
57:             uart_write_bytes(UART_NUM_0, "$ZC!", 4);
58:         });
59: 
```

## roboticarm_V_1_0.cc | InitializeGpio | 原文件第60-67行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/roboticarm_V_1_0.cc
以下为原始源码，不是截图OCR。
```
60:         methods_.AddMethod("Crab Right", "右抓", ParameterList(), [this](const ParameterList& parameters) {
61:             uart_write_bytes(UART_NUM_0, "$YC!", 4);
62:         });
63: 
64:         methods_.AddMethod("Grab Left", "前放", ParameterList(), [this](const ParameterList& parameters) {
65:             uart_write_bytes(UART_NUM_0, "$QP!", 4);
66:         });
67: 
```

## roboticarm_V_1_0.cc | InitializeGpio | 原文件第68-80行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/roboticarm_V_1_0.cc
以下为原始源码，不是截图OCR。
```
68:         methods_.AddMethod("Place Left", "左放", ParameterList(), [this](const ParameterList& parameters) {
69:             uart_write_bytes(UART_NUM_0, "$ZP!", 4);
70:         });
71: 
72:         methods_.AddMethod("Place Right", "右放", ParameterList(), [this](const ParameterList& parameters) {
73:             uart_write_bytes(UART_NUM_0, "$YP!", 4);
74:         });
75:         
76:     }
77: };
78: 
79: } // namespace iot
80: 
```

## roboticarm_V_1_0.cc | InitializeGpio | 原文件第81-81行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/roboticarm_V_1_0.cc
以下为原始源码，不是截图OCR。
```
81: DECLARE_THING(RoboticArm);
```

## speaker.cc | 文件开头/全局定义 | 原文件第1-16行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/speaker.cc
以下为原始源码，不是截图OCR。
```
1: #include "iot/thing.h"
2: #include "board.h"
3: #include "audio_codec.h"
4: 
5: #include <esp_log.h>
6: 
7: #define TAG "Speaker"
8: 
9: namespace iot {
10: 
11: // 这里仅定义 Speaker 的属性和方法，不包含具体的实现
12: class Speaker : public Thing {
13: public:
14:     Speaker() : Thing("Speaker", "扬声器") {
15:         // 定义设备的属性
16:         properties_.AddNumberProperty("volume", "当前音量值", [this]() -> int {
```

## speaker.cc | 文件开头/全局定义 | 原文件第17-25行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/speaker.cc
以下为原始源码，不是截图OCR。
```
17:             auto codec = Board::GetInstance().GetAudioCodec();
18:             return codec->output_volume();
19:         });
20: 
21:         // 定义设备可以被远程执行的指令
22:         methods_.AddMethod("SetVolume", "设置音量", ParameterList({
23:             Parameter("volume", "0到100之间的整数", kValueTypeNumber, true)
24:         }), [this](const ParameterList& parameters) {
25:             auto codec = Board::GetInstance().GetAudioCodec();
```

## speaker.cc | 文件开头/全局定义 | 原文件第26-33行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/things/speaker.cc
以下为原始源码，不是截图OCR。
```
26:             codec->SetOutputVolume(static_cast<uint8_t>(parameters["volume"].number()));
27:         });
28:     }
29: };
30: 
31: } // namespace iot
32: 
33: DECLARE_THING(Speaker);
```

## thing_manager.cc | 文件开头/全局定义 | 原文件第1-8行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing_manager.cc
以下为原始源码，不是截图OCR。
```
1: #include "thing_manager.h"
2: 
3: #include <esp_log.h>
4: 
5: #define TAG "ThingManager"
6: 
7: namespace iot {
8: 
```

## thing_manager.cc | ThingManager::AddThing | 原文件第9-12行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing_manager.cc
以下为原始源码，不是截图OCR。
```
9: void ThingManager::AddThing(Thing* thing) {
10:     things_.push_back(thing);
11: }
12: 
```

## thing_manager.cc | ThingManager::GetDescriptorsJson | 原文件第13-24行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing_manager.cc
以下为原始源码，不是截图OCR。
```
13: std::string ThingManager::GetDescriptorsJson() {
14:     std::string json_str = "[";
15:     for (auto& thing : things_) {
16:         json_str += thing->GetDescriptorJson() + ",";
17:     }
18:     if (json_str.back() == ',') {
19:         json_str.pop_back();
20:     }
21:     json_str += "]";
22:     return json_str;
23: }
24: 
```

## thing_manager.cc | ThingManager::GetStatesJson | 原文件第25-35行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing_manager.cc
以下为原始源码，不是截图OCR。
```
25: bool ThingManager::GetStatesJson(std::string& json, bool delta) {
26:     if (!delta) {
27:         last_states_.clear();
28:     }
29:     bool changed = false;
30:     json = "[";
31:     // 枚举thing，获取每个thing的state，如果发生变化，则更新，保存到last_states_
32:     // 如果delta为true，则只返回变化的部分
33:     for (auto& thing : things_) {
34:         std::string state = thing->GetStateJson();
35:         if (delta) {
```

## thing_manager.cc | ThingManager::GetStatesJson | 原文件第36-48行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing_manager.cc
以下为原始源码，不是截图OCR。
```
36:             // 如果delta为true，则只返回变化的部分
37:             auto it = last_states_.find(thing->name());
38:             if (it != last_states_.end() && it->second == state) {
39:                 continue;
40:             }
41:             changed = true;
42:             last_states_[thing->name()] = state;
43:         }
44:         json += state + ",";
45:     }
46:     if (json.back() == ',') {
47:         json.pop_back();
48:     }
```

## thing_manager.cc | ThingManager::GetStatesJson | 原文件第49-52行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing_manager.cc
以下为原始源码，不是截图OCR。
```
49:     json += "]";
50:     return changed;
51: }
52: 
```

## thing_manager.cc | ThingManager::Invoke | 原文件第53-63行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing_manager.cc
以下为原始源码，不是截图OCR。
```
53: void ThingManager::Invoke(const cJSON* command) {
54:     auto name = cJSON_GetObjectItem(command, "name");
55:     for (auto& thing : things_) {
56:         if (thing->name() == name->valuestring) {
57:             thing->Invoke(command);
58:             return;
59:         }
60:     }
61: }
62: 
63: } // namespace iot
```

## thing_manager.h | 文件开头/全局定义 | 原文件第1-21行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing_manager.h
以下为原始源码，不是截图OCR。
```
1: #ifndef THING_MANAGER_H
2: #define THING_MANAGER_H
3: 
4: 
5: #include "thing.h"
6: 
7: #include <cJSON.h>
8: 
9: #include <vector>
10: #include <memory>
11: #include <functional>
12: #include <map>
13: 
14: namespace iot {
15: 
16: class ThingManager {
17: public:
18:     static ThingManager& GetInstance() {
19:         static ThingManager instance;
20:         return instance;
21:     }
```

## thing_manager.h | 文件开头/全局定义 | 原文件第22-34行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing_manager.h
以下为原始源码，不是截图OCR。
```
22:     ThingManager(const ThingManager&) = delete;
23:     ThingManager& operator=(const ThingManager&) = delete;
24: 
25:     void AddThing(Thing* thing);
26: 
27:     std::string GetDescriptorsJson();
28:     bool GetStatesJson(std::string& json, bool delta = false);
29:     void Invoke(const cJSON* command);
30: 
31: private:
32:     ThingManager() = default;
33:     ~ThingManager() = default;
34: 
```

## thing_manager.h | 文件开头/全局定义 | 原文件第35-42行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/iot/thing_manager.h
以下为原始源码，不是截图OCR。
```
35:     std::vector<Thing*> things_;
36:     std::map<std::string, std::string> last_states_;
37: };
38: 
39: 
40: } // namespace iot
41: 
42: #endif // THING_MANAGER_H
```

## circular_strip.cc | 文件开头/全局定义 | 原文件第1-14行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
1: #include "circular_strip.h"
2: #include "application.h"
3: #include <esp_log.h>
4: 
5: #define TAG "CircularStrip"
6: 
7: #define BLINK_INFINITE -1
8: 
9: CircularStrip::CircularStrip(gpio_num_t gpio, uint8_t max_leds) : max_leds_(max_leds) {
10:     // If the gpio is not connected, you should use NoLed class
11:     assert(gpio != GPIO_NUM_NC);
12: 
13:     colors_.resize(max_leds_);
14: 
```

## circular_strip.cc | 文件开头/全局定义 | 原文件第15-23行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
15:     led_strip_config_t strip_config = {};
16:     strip_config.strip_gpio_num = gpio;
17:     strip_config.max_leds = max_leds_;
18:     strip_config.led_pixel_format = LED_PIXEL_FORMAT_GRB;
19:     strip_config.led_model = LED_MODEL_WS2812;
20: 
21:     led_strip_rmt_config_t rmt_config = {};
22:     rmt_config.resolution_hz = 10 * 1000 * 1000; // 10MHz
23: 
```

## circular_strip.cc | 文件开头/全局定义 | 原文件第24-31行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
24:     ESP_ERROR_CHECK(led_strip_new_rmt_device(&strip_config, &rmt_config, &led_strip_));
25:     led_strip_clear(led_strip_);
26: 
27:     esp_timer_create_args_t strip_timer_args = {
28:         .callback = [](void *arg) {
29:             auto strip = static_cast<CircularStrip*>(arg);
30:             std::lock_guard<std::mutex> lock(strip->mutex_);
31:             if (strip->strip_callback_ != nullptr) {
```

## circular_strip.cc | 文件开头/全局定义 | 原文件第32-44行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
32:                 strip->strip_callback_();
33:             }
34:         },
35:         .arg = this,
36:         .dispatch_method = ESP_TIMER_TASK,
37:         .name = "strip_timer",
38:         .skip_unhandled_events = false,
39:     };
40:     ESP_ERROR_CHECK(esp_timer_create(&strip_timer_args, &strip_timer_));
41: }
42: 
43: CircularStrip::~CircularStrip() {
44:     esp_timer_stop(strip_timer_);
```

## circular_strip.cc | 文件开头/全局定义 | 原文件第45-50行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
45:     if (led_strip_ != nullptr) {
46:         led_strip_del(led_strip_);
47:     }
48: }
49: 
50: 
```

## circular_strip.cc | CircularStrip::SetAllColor | 原文件第51-60行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
51: void CircularStrip::SetAllColor(StripColor color) {
52:     std::lock_guard<std::mutex> lock(mutex_);
53:     esp_timer_stop(strip_timer_);
54:     for (int i = 0; i < max_leds_; i++) {
55:         colors_[i] = color;
56:         led_strip_set_pixel(led_strip_, i, color.red, color.green, color.blue);
57:     }
58:     led_strip_refresh(led_strip_);
59: }
60: 
```

## circular_strip.cc | CircularStrip::SetSingleColor | 原文件第61-68行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
61: void CircularStrip::SetSingleColor(uint8_t index, StripColor color) {
62:     std::lock_guard<std::mutex> lock(mutex_);
63:     esp_timer_stop(strip_timer_);
64:     colors_[index] = color;
65:     led_strip_set_pixel(led_strip_, index, color.red, color.green, color.blue);
66:     led_strip_refresh(led_strip_);
67: }
68: 
```

## circular_strip.cc | CircularStrip::Blink | 原文件第69-78行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
69: void CircularStrip::Blink(StripColor color, int interval_ms) {
70:     for (int i = 0; i < max_leds_; i++) {
71:         colors_[i] = color;
72:     }
73:     StartStripTask(interval_ms, [this]() {
74:         static bool on = true;
75:         if (on) {
76:             for (int i = 0; i < max_leds_; i++) {
77:                 led_strip_set_pixel(led_strip_, i, colors_[i].red, colors_[i].green, colors_[i].blue);
78:             }
```

## circular_strip.cc | CircularStrip::Blink | 原文件第79-86行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
79:             led_strip_refresh(led_strip_);
80:         } else {
81:             led_strip_clear(led_strip_);
82:         }
83:         on = !on;
84:     });
85: }
86: 
```

## circular_strip.cc | CircularStrip::FadeOut | 原文件第87-95行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
87: void CircularStrip::FadeOut(int interval_ms) {
88:     StartStripTask(interval_ms, [this]() {
89:         bool all_off = true;
90:         for (int i = 0; i < max_leds_; i++) {
91:             colors_[i].red /= 2;
92:             colors_[i].green /= 2;
93:             colors_[i].blue /= 2;
94:             if (colors_[i].red != 0 || colors_[i].green != 0 || colors_[i].blue != 0) {
95:                 all_off = false;
```

## circular_strip.cc | CircularStrip::FadeOut | 原文件第96-107行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
96:             }
97:             led_strip_set_pixel(led_strip_, i, colors_[i].red, colors_[i].green, colors_[i].blue);
98:         }
99:         if (all_off) {
100:             led_strip_clear(led_strip_);
101:             esp_timer_stop(strip_timer_);
102:         } else {
103:             led_strip_refresh(led_strip_);
104:         }
105:     });
106: }
107: 
```

## circular_strip.cc | CircularStrip::Breathe | 原文件第108-116行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
108: void CircularStrip::Breathe(StripColor low, StripColor high, int interval_ms) {
109:     StartStripTask(interval_ms, [this, low, high]() {
110:         static bool increase = true;
111:         static StripColor color = low;
112:         if (increase) {
113:             if (color.red < high.red) {
114:                 color.red++;
115:             }
116:             if (color.green < high.green) {
```

## circular_strip.cc | CircularStrip::Breathe | 原文件第117-128行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
117:                 color.green++;
118:             }
119:             if (color.blue < high.blue) {
120:                 color.blue++;
121:             }
122:             if (color.red == high.red && color.green == high.green && color.blue == high.blue) {
123:                 increase = false;
124:             }
125:         } else {
126:             if (color.red > low.red) {
127:                 color.red--;
128:             }
```

## circular_strip.cc | CircularStrip::Breathe | 原文件第129-139行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
129:             if (color.green > low.green) {
130:                 color.green--;
131:             }
132:             if (color.blue > low.blue) {
133:                 color.blue--;
134:             }
135:             if (color.red == low.red && color.green == low.green && color.blue == low.blue) {
136:                 increase = true;
137:             }
138:         }
139:         for (int i = 0; i < max_leds_; i++) {
```

## circular_strip.cc | CircularStrip::Breathe | 原文件第140-145行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
140:             led_strip_set_pixel(led_strip_, i, color.red, color.green, color.blue);
141:         }
142:         led_strip_refresh(led_strip_);
143:     });
144: }
145: 
```

## circular_strip.cc | CircularStrip::Scroll | 原文件第146-155行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
146: void CircularStrip::Scroll(StripColor low, StripColor high, int length, int interval_ms) {
147:     for (int i = 0; i < max_leds_; i++) {
148:         colors_[i] = low;
149:     }
150:     StartStripTask(interval_ms, [this, low, high, length]() {
151:         static int offset = 0;
152:         for (int i = 0; i < max_leds_; i++) {
153:             colors_[i] = low;
154:         }
155:         for (int j = 0; j < length; j++) {
```

## circular_strip.cc | CircularStrip::Scroll | 原文件第156-166行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
156:             int i = (offset + j) % max_leds_;
157:             colors_[i] = high;
158:         }
159:         for (int i = 0; i < max_leds_; i++) {
160:             led_strip_set_pixel(led_strip_, i, colors_[i].red, colors_[i].green, colors_[i].blue);
161:         }
162:         led_strip_refresh(led_strip_);
163:         offset = (offset + 1) % max_leds_;
164:     });
165: }
166: 
```

## circular_strip.cc | CircularStrip::StartStripTask | 原文件第167-178行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
167: void CircularStrip::StartStripTask(int interval_ms, std::function<void()> cb) {
168:     if (led_strip_ == nullptr) {
169:         return;
170:     }
171: 
172:     std::lock_guard<std::mutex> lock(mutex_);
173:     esp_timer_stop(strip_timer_);
174:     
175:     strip_callback_ = cb;
176:     esp_timer_start_periodic(strip_timer_, interval_ms * 1000);
177: }
178: 
```

## circular_strip.cc | CircularStrip::SetBrightness | 原文件第179-184行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
179: void CircularStrip::SetBrightness(uint8_t default_brightness, uint8_t low_brightness) {
180:     default_brightness_ = default_brightness;
181:     low_brightness_ = low_brightness;
182:     OnStateChanged();
183: }
184: 
```

## circular_strip.cc | CircularStrip::OnStateChanged | 原文件第185-193行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
185: void CircularStrip::OnStateChanged() {
186:     auto& app = Application::GetInstance();
187:     auto device_state = app.GetDeviceState();
188:     switch (device_state) {
189:         case kDeviceStateStarting: {
190:             StripColor low = { 0, 0, 0 };
191:             StripColor high = { low_brightness_, low_brightness_, default_brightness_ };
192:             Scroll(low, high, 3, 100);
193:             break;
```

## circular_strip.cc | CircularStrip::OnStateChanged | 原文件第194-203行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
194:         }
195:         case kDeviceStateWifiConfiguring: {
196:             StripColor color = { low_brightness_, low_brightness_, default_brightness_ };
197:             Blink(color, 500);
198:             break;
199:         }
200:         case kDeviceStateIdle:
201:             FadeOut(50);
202:             break;
203:         case kDeviceStateConnecting: {
```

## circular_strip.cc | CircularStrip::OnStateChanged | 原文件第204-213行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
204:             StripColor color = { low_brightness_, low_brightness_, default_brightness_ };
205:             SetAllColor(color);
206:             break;
207:         }
208:         case kDeviceStateListening: {
209:             StripColor color = { default_brightness_, low_brightness_, low_brightness_ };
210:             SetAllColor(color);
211:             break;
212:         }
213:         case kDeviceStateSpeaking: {
```

## circular_strip.cc | CircularStrip::OnStateChanged | 原文件第214-223行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
214:             StripColor color = { low_brightness_, default_brightness_, low_brightness_ };
215:             SetAllColor(color);
216:             break;
217:         }
218:         case kDeviceStateUpgrading: {
219:             StripColor color = { low_brightness_, default_brightness_, low_brightness_ };
220:             Blink(color, 100);
221:             break;
222:         }
223:         case kDeviceStateActivating: {
```

## circular_strip.cc | CircularStrip::OnStateChanged | 原文件第224-232行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.cc
以下为原始源码，不是截图OCR。
```
224:             StripColor color = { low_brightness_, default_brightness_, low_brightness_ };
225:             Blink(color, 500);
226:             break;
227:         }
228:         default:
229:             ESP_LOGW(TAG, "Unknown led strip event: %d", device_state);
230:             return;
231:     }
232: }
```

## circular_strip.h | 文件开头/全局定义 | 原文件第1-20行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.h
以下为原始源码，不是截图OCR。
```
1: #ifndef _CIRCULAR_STRIP_H_
2: #define _CIRCULAR_STRIP_H_
3: 
4: #include "led.h"
5: #include <driver/gpio.h>
6: #include <led_strip.h>
7: #include <esp_timer.h>
8: #include <atomic>
9: #include <mutex>
10: #include <vector>
11: 
12: #define DEFAULT_BRIGHTNESS 32
13: #define LOW_BRIGHTNESS 4
14: 
15: struct StripColor {
16:     uint8_t red = 0, green = 0, blue = 0;
17: };
18: 
19: class CircularStrip : public Led {
20: public:
```

## circular_strip.h | 文件开头/全局定义 | 原文件第21-28行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.h
以下为原始源码，不是截图OCR。
```
21:     CircularStrip(gpio_num_t gpio, uint8_t max_leds);
22:     virtual ~CircularStrip();
23: 
24:     void OnStateChanged() override;
25:     void SetBrightness(uint8_t default_brightness, uint8_t low_brightness);
26:     void SetAllColor(StripColor color);
27:     void SetSingleColor(uint8_t index, StripColor color);
28:     void Blink(StripColor color, int interval_ms);
```

## circular_strip.h | 文件开头/全局定义 | 原文件第29-39行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.h
以下为原始源码，不是截图OCR。
```
29:     void Breathe(StripColor low, StripColor high, int interval_ms);
30:     void Scroll(StripColor low, StripColor high, int length, int interval_ms);
31: 
32: private:
33:     std::mutex mutex_;
34:     TaskHandle_t blink_task_ = nullptr;
35:     led_strip_handle_t led_strip_ = nullptr;
36:     int max_leds_ = 0;
37:     std::vector<StripColor> colors_;
38:     int blink_counter_ = 0;
39:     int blink_interval_ms_ = 0;
```

## circular_strip.h | 文件开头/全局定义 | 原文件第40-50行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.h
以下为原始源码，不是截图OCR。
```
40:     esp_timer_handle_t strip_timer_ = nullptr;
41:     std::function<void()> strip_callback_ = nullptr;
42: 
43:     uint8_t default_brightness_ = DEFAULT_BRIGHTNESS;
44:     uint8_t low_brightness_ = LOW_BRIGHTNESS;
45: 
46:     void StartStripTask(int interval_ms, std::function<void()> cb);
47:     void Rainbow(StripColor low, StripColor high, int interval_ms);
48:     void FadeOut(int interval_ms);
49: };
50: 
```

## circular_strip.h | 文件开头/全局定义 | 原文件第51-51行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/circular_strip.h
以下为原始源码，不是截图OCR。
```
51: #endif // _CIRCULAR_STRIP_H_
```

## gpio_led.cc | 文件开头/全局定义 | 原文件第1-18行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
1: #include "gpio_led.h"
2: #include "application.h"
3: #include <esp_log.h>
4: 
5: #define TAG "GpioLed"
6: 
7: #define DEFAULT_BRIGHTNESS 50
8: #define HIGH_BRIGHTNESS 100
9: #define LOW_BRIGHTNESS 10
10: 
11: #define IDLE_BRIGHTNESS 5
12: #define SPEAKING_BRIGHTNESS 75
13: #define UPGRADING_BRIGHTNESS 25
14: #define ACTIVATING_BRIGHTNESS 35
15: 
16: #define BLINK_INFINITE -1
17: 
18: // GPIO_LED
```

## gpio_led.cc | 文件开头/全局定义 | 原文件第19-31行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
19: #define LEDC_LS_TIMER          LEDC_TIMER_1
20: #define LEDC_LS_MODE           LEDC_LOW_SPEED_MODE
21: #define LEDC_LS_CH0_CHANNEL    LEDC_CHANNEL_0
22: 
23: #define LEDC_DUTY              (4096)
24: #define LEDC_FADE_TIME    (1000)
25: // GPIO_LED
26: 
27: GpioLed::GpioLed(gpio_num_t gpio, int output_invert) {
28:     // If the gpio is not connected, you should use NoLed class
29:     assert(gpio != GPIO_NUM_NC);
30: 
31:     /*
```

## gpio_led.cc | 文件开头/全局定义 | 原文件第32-38行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
32:      * Prepare and set configuration of timers
33:      * that will be used by LED Controller
34:      */
35:     ledc_timer_config_t ledc_timer = {};
36:     ledc_timer.duty_resolution = LEDC_TIMER_13_BIT; // resolution of PWM duty
37:     ledc_timer.freq_hz = 4000;                      // frequency of PWM signal
38:     ledc_timer.speed_mode = LEDC_LS_MODE;           // timer mode
```

## gpio_led.cc | 文件开头/全局定义 | 原文件第39-47行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
39:     ledc_timer.timer_num = LEDC_LS_TIMER;            // timer index
40:     ledc_timer.clk_cfg = LEDC_AUTO_CLK;              // Auto select the source clock
41: 
42:     ESP_ERROR_CHECK(ledc_timer_config(&ledc_timer));
43: 
44:     ledc_channel_.channel    = LEDC_LS_CH0_CHANNEL,
45:     ledc_channel_.duty       = 0,
46:     ledc_channel_.gpio_num   = gpio,
47:     ledc_channel_.speed_mode = LEDC_LS_MODE,
```

## gpio_led.cc | 文件开头/全局定义 | 原文件第48-57行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
48:     ledc_channel_.hpoint     = 0,
49:     ledc_channel_.timer_sel  = LEDC_LS_TIMER,
50:     ledc_channel_.flags.output_invert = output_invert & 0x01,
51: 
52:     // Set LED Controller with previously prepared configuration
53:     ledc_channel_config(&ledc_channel_);
54: 
55:     // Initialize fade service.
56:     ledc_fade_func_install(0);
57: 
```

## gpio_led.cc | 文件开头/全局定义 | 原文件第58-66行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
58:     // When the callback registered by ledc_cb_degister is called, run led ->OnFadeEnd()
59:     ledc_cbs_t ledc_callbacks = {
60:         .fade_cb = FadeCallback
61:     };
62:     ledc_cb_register(ledc_channel_.speed_mode, ledc_channel_.channel, &ledc_callbacks, this);
63: 
64:     esp_timer_create_args_t blink_timer_args = {
65:         .callback = [](void *arg) {
66:             auto led = static_cast<GpioLed*>(arg);
```

## gpio_led.cc | 文件开头/全局定义 | 原文件第67-81行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
67:             led->OnBlinkTimer();
68:         },
69:         .arg = this,
70:         .dispatch_method = ESP_TIMER_TASK,
71:         .name = "Blink Timer",
72:         .skip_unhandled_events = false,
73:     };
74:     ESP_ERROR_CHECK(esp_timer_create(&blink_timer_args, &blink_timer_));
75: 
76:     ledc_initialized_ = true;
77: }
78: 
79: GpioLed::~GpioLed() {
80:     esp_timer_stop(blink_timer_);
81:     if (ledc_initialized_) {
```

## gpio_led.cc | 文件开头/全局定义 | 原文件第82-87行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
82:         ledc_fade_stop(ledc_channel_.speed_mode, ledc_channel_.channel);
83:         ledc_fade_func_uninstall();
84:     }
85: }
86: 
87: 
```

## gpio_led.cc | GpioLed::SetBrightness | 原文件第88-91行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
88: void GpioLed::SetBrightness(uint8_t brightness) {
89:     duty_ = brightness * LEDC_DUTY / 100;
90: }
91: 
```

## gpio_led.cc | GpioLed::TurnOn | 原文件第92-103行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
92: void GpioLed::TurnOn() {
93:     if (!ledc_initialized_) {
94:         return;
95:     }
96: 
97:     std::lock_guard<std::mutex> lock(mutex_);
98:     esp_timer_stop(blink_timer_);
99:     ledc_fade_stop(ledc_channel_.speed_mode, ledc_channel_.channel);
100:     ledc_set_duty(ledc_channel_.speed_mode, ledc_channel_.channel, duty_);
101:     ledc_update_duty(ledc_channel_.speed_mode, ledc_channel_.channel);
102: }
103: 
```

## gpio_led.cc | GpioLed::TurnOff | 原文件第104-115行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
104: void GpioLed::TurnOff() {
105:     if (!ledc_initialized_) {
106:         return;
107:     }
108: 
109:     std::lock_guard<std::mutex> lock(mutex_);
110:     esp_timer_stop(blink_timer_);
111:     ledc_fade_stop(ledc_channel_.speed_mode, ledc_channel_.channel);
112:     ledc_set_duty(ledc_channel_.speed_mode, ledc_channel_.channel, 0);
113:     ledc_update_duty(ledc_channel_.speed_mode, ledc_channel_.channel);
114: }
115: 
```

## gpio_led.cc | GpioLed::BlinkOnce | 原文件第116-119行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
116: void GpioLed::BlinkOnce() {
117:     Blink(1, 100);
118: }
119: 
```

## gpio_led.cc | GpioLed::Blink | 原文件第120-123行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
120: void GpioLed::Blink(int times, int interval_ms) {
121:     StartBlinkTask(times, interval_ms);
122: }
123: 
```

## gpio_led.cc | GpioLed::StartContinuousBlink | 原文件第124-127行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
124: void GpioLed::StartContinuousBlink(int interval_ms) {
125:     StartBlinkTask(BLINK_INFINITE, interval_ms);
126: }
127: 
```

## gpio_led.cc | GpioLed::StartBlinkTask | 原文件第128-138行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
128: void GpioLed::StartBlinkTask(int times, int interval_ms) {
129:     if (!ledc_initialized_) {
130:         return;
131:     }
132: 
133:     std::lock_guard<std::mutex> lock(mutex_);
134:     esp_timer_stop(blink_timer_);
135:     ledc_fade_stop(ledc_channel_.speed_mode, ledc_channel_.channel);
136: 
137:     blink_counter_ = times * 2;
138:     blink_interval_ms_ = interval_ms;
```

## gpio_led.cc | GpioLed::StartBlinkTask | 原文件第139-141行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
139:     esp_timer_start_periodic(blink_timer_, interval_ms * 1000);
140: }
141: 
```

## gpio_led.cc | GpioLed::OnBlinkTimer | 原文件第142-152行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
142: void GpioLed::OnBlinkTimer() {
143:     std::lock_guard<std::mutex> lock(mutex_);
144:     blink_counter_--;
145:     if (blink_counter_ & 1) {
146:         ledc_set_duty(ledc_channel_.speed_mode, ledc_channel_.channel, duty_);
147:     } else {
148:         ledc_set_duty(ledc_channel_.speed_mode, ledc_channel_.channel, 0);
149: 
150:         if (blink_counter_ == 0) {
151:             esp_timer_stop(blink_timer_);
152:         }
```

## gpio_led.cc | GpioLed::OnBlinkTimer | 原文件第153-156行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
153:     }
154:     ledc_update_duty(ledc_channel_.speed_mode, ledc_channel_.channel);
155: }
156: 
```

## gpio_led.cc | GpioLed::StartFadeTask | 原文件第157-166行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
157: void GpioLed::StartFadeTask() {
158:     if (!ledc_initialized_) {
159:         return;
160:     }
161: 
162:     std::lock_guard<std::mutex> lock(mutex_);
163:     esp_timer_stop(blink_timer_);
164:     ledc_fade_stop(ledc_channel_.speed_mode, ledc_channel_.channel);
165:     fade_up_ = true;
166:     ledc_set_fade_with_time(ledc_channel_.speed_mode,
```

## gpio_led.cc | GpioLed::StartFadeTask | 原文件第167-171行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
167:                             ledc_channel_.channel, LEDC_DUTY, LEDC_FADE_TIME);
168:     ledc_fade_start(ledc_channel_.speed_mode,
169:                     ledc_channel_.channel, LEDC_FADE_NO_WAIT);
170: }
171: 
```

## gpio_led.cc | GpioLed::OnFadeEnd | 原文件第172-180行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
172: void GpioLed::OnFadeEnd() {
173:     std::lock_guard<std::mutex> lock(mutex_);
174:     fade_up_ = !fade_up_;
175:     ledc_set_fade_with_time(ledc_channel_.speed_mode,
176:                             ledc_channel_.channel, fade_up_ ? LEDC_DUTY : 0, LEDC_FADE_TIME);
177:     ledc_fade_start(ledc_channel_.speed_mode,
178:                     ledc_channel_.channel, LEDC_FADE_NO_WAIT);
179: }
180: 
```

## gpio_led.cc | GpioLed::FadeCallback | 原文件第181-188行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
181: bool GpioLed::FadeCallback(const ledc_cb_param_t *param, void *user_arg) {
182:     if (param->event == LEDC_FADE_END_EVT) {
183:         auto led = static_cast<GpioLed*>(user_arg);
184:         led->OnFadeEnd();
185:     }
186:     return true;
187: }
188: 
```

## gpio_led.cc | GpioLed::OnStateChanged | 原文件第189-198行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
189: void GpioLed::OnStateChanged() {
190:     auto& app = Application::GetInstance();
191:     auto device_state = app.GetDeviceState();
192:     switch (device_state) {
193:         case kDeviceStateStarting:
194:             SetBrightness(DEFAULT_BRIGHTNESS);
195:             StartContinuousBlink(100);
196:             break;
197:         case kDeviceStateWifiConfiguring:
198:             SetBrightness(DEFAULT_BRIGHTNESS);
```

## gpio_led.cc | GpioLed::OnStateChanged | 原文件第199-210行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
199:             StartContinuousBlink(500);
200:             break;
201:         case kDeviceStateIdle:
202:             SetBrightness(IDLE_BRIGHTNESS);
203:             TurnOn();
204:             // TurnOff();
205:             break;
206:         case kDeviceStateConnecting:
207:             SetBrightness(DEFAULT_BRIGHTNESS);
208:             TurnOn();
209:             break;
210:         case kDeviceStateListening:
```

## gpio_led.cc | GpioLed::OnStateChanged | 原文件第211-222行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
211:             if (app.IsVoiceDetected()) {
212:                 SetBrightness(HIGH_BRIGHTNESS);
213:             } else {
214:                 SetBrightness(LOW_BRIGHTNESS);
215:             }
216:             // TurnOn();
217:             StartFadeTask();
218:             break;
219:         case kDeviceStateSpeaking:
220:             SetBrightness(SPEAKING_BRIGHTNESS);
221:             TurnOn();
222:             break;
```

## gpio_led.cc | GpioLed::OnStateChanged | 原文件第223-232行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
223:         case kDeviceStateUpgrading:
224:             SetBrightness(UPGRADING_BRIGHTNESS);
225:             StartContinuousBlink(100);
226:             break;
227:         case kDeviceStateActivating:
228:             SetBrightness(ACTIVATING_BRIGHTNESS);
229:             StartContinuousBlink(500);
230:             break;
231:         default:
232:             ESP_LOGE(TAG, "Unknown gpio led event: %d", device_state);
```

## gpio_led.cc | GpioLed::OnStateChanged | 原文件第233-235行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.cc
以下为原始源码，不是截图OCR。
```
233:             return;
234:     }
235: }
```

## gpio_led.h | 文件开头/全局定义 | 原文件第1-18行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.h
以下为原始源码，不是截图OCR。
```
1: #ifndef _GPIO_LED_H_
2: #define _GPIO_LED_H_
3: 
4: #include <freertos/FreeRTOS.h>
5: #include <freertos/task.h>
6: #include "led.h"
7: #include <driver/gpio.h>
8: #include <driver/ledc.h>
9: #include <esp_timer.h>
10: #include <atomic>
11: #include <mutex>
12: 
13: class GpioLed : public Led {
14: public:
15:     GpioLed(gpio_num_t gpio, int output_invert=0);
16:     virtual ~GpioLed();
17: 
18:     void OnStateChanged() override;
```

## gpio_led.h | 文件开头/全局定义 | 原文件第19-31行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.h
以下为原始源码，不是截图OCR。
```
19: 
20: private:
21:     std::mutex mutex_;
22:     TaskHandle_t blink_task_ = nullptr;
23:     ledc_channel_config_t ledc_channel_ = {0};
24:     bool ledc_initialized_ = false;
25:     uint32_t duty_ = 0;
26:     int blink_counter_ = 0;
27:     int blink_interval_ms_ = 0;
28:     esp_timer_handle_t blink_timer_ = nullptr;
29:     bool fade_up_ = true;
30: 
31:     void StartBlinkTask(int times, int interval_ms);
```

## gpio_led.h | 文件开头/全局定义 | 原文件第32-45行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/gpio_led.h
以下为原始源码，不是截图OCR。
```
32:     void OnBlinkTimer();
33: 
34:     void BlinkOnce();
35:     void Blink(int times, int interval_ms);
36:     void StartContinuousBlink(int interval_ms);
37:     void TurnOn();
38:     void TurnOff();
39:     void SetBrightness(uint8_t brightness);
40:     void StartFadeTask();
41:     void OnFadeEnd();
42:     static bool FadeCallback(const ledc_cb_param_t *param, void *user_arg);
43: };
44: 
45: #endif // _GPIO_LED_H_
```

## led.h | 文件开头/全局定义 | 原文件第1-17行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/led.h
以下为原始源码，不是截图OCR。
```
1: #ifndef _LED_H_
2: #define _LED_H_
3: 
4: class Led {
5: public:
6:     virtual ~Led() = default;
7:     // Set the led state based on the device state
8:     virtual void OnStateChanged() = 0;
9: };
10: 
11: 
12: class NoLed : public Led {
13: public:
14:     virtual void OnStateChanged() override {}
15: };
16: 
17: #endif // _LED_H_
```

## single_led.cc | 文件开头/全局定义 | 原文件第1-17行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/single_led.cc
以下为原始源码，不是截图OCR。
```
1: #include "single_led.h"
2: #include "application.h"
3: #include <esp_log.h> 
4: 
5: #define TAG "SingleLed"
6: 
7: #define DEFAULT_BRIGHTNESS 4
8: #define HIGH_BRIGHTNESS 16
9: #define LOW_BRIGHTNESS 2
10: 
11: #define BLINK_INFINITE -1
12: 
13: 
14: SingleLed::SingleLed(gpio_num_t gpio) {
15:     // If the gpio is not connected, you should use NoLed class
16:     assert(gpio != GPIO_NUM_NC);
17: 
```

## single_led.cc | 文件开头/全局定义 | 原文件第18-26行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/single_led.cc
以下为原始源码，不是截图OCR。
```
18:     led_strip_config_t strip_config = {};
19:     strip_config.strip_gpio_num = gpio;
20:     strip_config.max_leds = 1;
21:     strip_config.led_pixel_format = LED_PIXEL_FORMAT_GRB;
22:     strip_config.led_model = LED_MODEL_WS2812;
23: 
24:     led_strip_rmt_config_t rmt_config = {};
25:     rmt_config.resolution_hz = 10 * 1000 * 1000; // 10MHz
26: 
```

## single_led.cc | 文件开头/全局定义 | 原文件第27-36行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/single_led.cc
以下为原始源码，不是截图OCR。
```
27:     ESP_ERROR_CHECK(led_strip_new_rmt_device(&strip_config, &rmt_config, &led_strip_));
28:     led_strip_clear(led_strip_);
29: 
30:     esp_timer_create_args_t blink_timer_args = {
31:         .callback = [](void *arg) {
32:             auto led = static_cast<SingleLed*>(arg);
33:             led->OnBlinkTimer();
34:         },
35:         .arg = this,
36:         .dispatch_method = ESP_TIMER_TASK,
```

## single_led.cc | 文件开头/全局定义 | 原文件第37-50行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/single_led.cc
以下为原始源码，不是截图OCR。
```
37:         .name = "blink_timer",
38:         .skip_unhandled_events = false,
39:     };
40:     ESP_ERROR_CHECK(esp_timer_create(&blink_timer_args, &blink_timer_));
41: }
42: 
43: SingleLed::~SingleLed() {
44:     esp_timer_stop(blink_timer_);
45:     if (led_strip_ != nullptr) {
46:         led_strip_del(led_strip_);
47:     }
48: }
49: 
50: 
```

## single_led.cc | SingleLed::SetColor | 原文件第51-56行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/single_led.cc
以下为原始源码，不是截图OCR。
```
51: void SingleLed::SetColor(uint8_t r, uint8_t g, uint8_t b) {
52:     r_ = r;
53:     g_ = g;
54:     b_ = b;
55: }
56: 
```

## single_led.cc | SingleLed::TurnOn | 原文件第57-67行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/single_led.cc
以下为原始源码，不是截图OCR。
```
57: void SingleLed::TurnOn() {
58:     if (led_strip_ == nullptr) {
59:         return;
60:     }
61:     
62:     std::lock_guard<std::mutex> lock(mutex_);
63:     esp_timer_stop(blink_timer_);
64:     led_strip_set_pixel(led_strip_, 0, r_, g_, b_);
65:     led_strip_refresh(led_strip_);
66: }
67: 
```

## single_led.cc | SingleLed::TurnOff | 原文件第68-77行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/single_led.cc
以下为原始源码，不是截图OCR。
```
68: void SingleLed::TurnOff() {
69:     if (led_strip_ == nullptr) {
70:         return;
71:     }
72: 
73:     std::lock_guard<std::mutex> lock(mutex_);
74:     esp_timer_stop(blink_timer_);
75:     led_strip_clear(led_strip_);
76: }
77: 
```

## single_led.cc | SingleLed::BlinkOnce | 原文件第78-81行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/single_led.cc
以下为原始源码，不是截图OCR。
```
78: void SingleLed::BlinkOnce() {
79:     Blink(1, 100);
80: }
81: 
```

## single_led.cc | SingleLed::Blink | 原文件第82-85行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/single_led.cc
以下为原始源码，不是截图OCR。
```
82: void SingleLed::Blink(int times, int interval_ms) {
83:     StartBlinkTask(times, interval_ms);
84: }
85: 
```

## single_led.cc | SingleLed::StartContinuousBlink | 原文件第86-89行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/single_led.cc
以下为原始源码，不是截图OCR。
```
86: void SingleLed::StartContinuousBlink(int interval_ms) {
87:     StartBlinkTask(BLINK_INFINITE, interval_ms);
88: }
89: 
```

## single_led.cc | SingleLed::StartBlinkTask | 原文件第90-102行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/single_led.cc
以下为原始源码，不是截图OCR。
```
90: void SingleLed::StartBlinkTask(int times, int interval_ms) {
91:     if (led_strip_ == nullptr) {
92:         return;
93:     }
94: 
95:     std::lock_guard<std::mutex> lock(mutex_);
96:     esp_timer_stop(blink_timer_);
97:     
98:     blink_counter_ = times * 2;
99:     blink_interval_ms_ = interval_ms;
100:     esp_timer_start_periodic(blink_timer_, interval_ms * 1000);
101: }
102: 
```

## single_led.cc | SingleLed::OnBlinkTimer | 原文件第103-115行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/single_led.cc
以下为原始源码，不是截图OCR。
```
103: void SingleLed::OnBlinkTimer() {
104:     std::lock_guard<std::mutex> lock(mutex_);
105:     blink_counter_--;
106:     if (blink_counter_ & 1) {
107:         led_strip_set_pixel(led_strip_, 0, r_, g_, b_);
108:         led_strip_refresh(led_strip_);
109:     } else {
110:         led_strip_clear(led_strip_);
111: 
112:         if (blink_counter_ == 0) {
113:             esp_timer_stop(blink_timer_);
114:         }
115:     }
```

## single_led.cc | SingleLed::OnBlinkTimer | 原文件第116-118行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/single_led.cc
以下为原始源码，不是截图OCR。
```
116: }
117: 
118: 
```

## single_led.cc | SingleLed::OnStateChanged | 原文件第119-128行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/single_led.cc
以下为原始源码，不是截图OCR。
```
119: void SingleLed::OnStateChanged() {
120:     auto& app = Application::GetInstance();
121:     auto device_state = app.GetDeviceState();
122:     switch (device_state) {
123:         case kDeviceStateStarting:
124:             SetColor(0, 0, DEFAULT_BRIGHTNESS);
125:             StartContinuousBlink(100);
126:             break;
127:         case kDeviceStateWifiConfiguring:
128:             SetColor(0, 0, DEFAULT_BRIGHTNESS);
```

## single_led.cc | SingleLed::OnStateChanged | 原文件第129-139行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/single_led.cc
以下为原始源码，不是截图OCR。
```
129:             StartContinuousBlink(500);
130:             break;
131:         case kDeviceStateIdle:
132:             TurnOff();
133:             break;
134:         case kDeviceStateConnecting:
135:             SetColor(0, 0, DEFAULT_BRIGHTNESS);
136:             TurnOn();
137:             break;
138:         case kDeviceStateListening:
139:             if (app.IsVoiceDetected()) {
```

## single_led.cc | SingleLed::OnStateChanged | 原文件第140-150行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/single_led.cc
以下为原始源码，不是截图OCR。
```
140:                 SetColor(HIGH_BRIGHTNESS, 0, 0);
141:             } else {
142:                 SetColor(LOW_BRIGHTNESS, 0, 0);
143:             }
144:             TurnOn();
145:             break;
146:         case kDeviceStateSpeaking:
147:             SetColor(0, DEFAULT_BRIGHTNESS, 0);
148:             TurnOn();
149:             break;
150:         case kDeviceStateUpgrading:
```

## single_led.cc | SingleLed::OnStateChanged | 原文件第151-162行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/single_led.cc
以下为原始源码，不是截图OCR。
```
151:             SetColor(0, DEFAULT_BRIGHTNESS, 0);
152:             StartContinuousBlink(100);
153:             break;
154:         case kDeviceStateActivating:
155:             SetColor(0, DEFAULT_BRIGHTNESS, 0);
156:             StartContinuousBlink(500);
157:             break;
158:         default:
159:             ESP_LOGW(TAG, "Unknown led strip event: %d", device_state);
160:             return;
161:     }
162: }
```

## single_led.h | 文件开头/全局定义 | 原文件第1-19行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/single_led.h
以下为原始源码，不是截图OCR。
```
1: #ifndef _SINGLE_LED_H_
2: #define _SINGLE_LED_H_
3: 
4: #include "led.h"
5: #include <driver/gpio.h>
6: #include <led_strip.h>
7: #include <esp_timer.h>
8: #include <atomic>
9: #include <mutex>
10: 
11: class SingleLed : public Led {
12: public:
13:     SingleLed(gpio_num_t gpio);
14:     virtual ~SingleLed();
15: 
16:     void OnStateChanged() override;
17: 
18: private:
19:     std::mutex mutex_;
```

## single_led.h | 文件开头/全局定义 | 原文件第20-31行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/single_led.h
以下为原始源码，不是截图OCR。
```
20:     TaskHandle_t blink_task_ = nullptr;
21:     led_strip_handle_t led_strip_ = nullptr;
22:     uint8_t r_ = 0, g_ = 0, b_ = 0;
23:     int blink_counter_ = 0;
24:     int blink_interval_ms_ = 0;
25:     esp_timer_handle_t blink_timer_ = nullptr;
26: 
27:     void StartBlinkTask(int times, int interval_ms);
28:     void OnBlinkTimer();
29: 
30:     void BlinkOnce();
31:     void Blink(int times, int interval_ms);
```

## single_led.h | 文件开头/全局定义 | 原文件第32-38行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/led/single_led.h
以下为原始源码，不是截图OCR。
```
32:     void StartContinuousBlink(int interval_ms);
33:     void TurnOn();
34:     void TurnOff();
35:     void SetColor(uint8_t r, uint8_t g, uint8_t b);
36: };
37: 
38: #endif // _SINGLE_LED_H_
```

## main.cc | 文件开头/全局定义 | 原文件第1-17行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/main.cc
以下为原始源码，不是截图OCR。
```
1: #include <esp_log.h>
2: #include <esp_err.h>
3: #include <nvs.h>
4: #include <nvs_flash.h>
5: #include <driver/gpio.h>
6: #include <esp_event.h>
7: 
8: #include "application.h"
9: #include "system_info.h"
10: 
11: #define TAG "main"
12: 
13: extern "C" void app_main(void)
14: {
15:     // Initialize the default event loop
16:     ESP_ERROR_CHECK(esp_event_loop_create_default());
17: 
```

## main.cc | 文件开头/全局定义 | 原文件第18-27行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/main.cc
以下为原始源码，不是截图OCR。
```
18:     // Initialize NVS flash for WiFi configuration
19:     esp_err_t ret = nvs_flash_init();
20:     if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
21:         ESP_LOGW(TAG, "Erasing NVS flash to fix corruption");
22:         ESP_ERROR_CHECK(nvs_flash_erase());
23:         ret = nvs_flash_init();
24:     }
25:     ESP_ERROR_CHECK(ret);
26: 
27:     // Launch the application
```

## main.cc | 文件开头/全局定义 | 原文件第28-30行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/main.cc
以下为原始源码，不是截图OCR。
```
28:     Application::GetInstance().Start();
29:     // The main thread will exit and release the stack memory
30: }
```

## ota.cc | 文件开头/全局定义 | 原文件第1-25行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
1: #include "ota.h"
2: #include "system_info.h"
3: #include "board.h"
4: #include "settings.h"
5: 
6: #include <cJSON.h>
7: #include <esp_log.h>
8: #include <esp_partition.h>
9: #include <esp_ota_ops.h>
10: #include <esp_app_format.h>
11: 
12: #include <cstring>
13: #include <vector>
14: #include <sstream>
15: #include <algorithm>
16: 
17: #define TAG "Ota"
18: 
19: 
20: Ota::Ota() {
21: }
22: 
23: Ota::~Ota() {
24: }
25: 
```

## ota.cc | Ota::SetCheckVersionUrl | 原文件第26-29行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
26: void Ota::SetCheckVersionUrl(std::string check_version_url) {
27:     check_version_url_ = check_version_url;
28: }
29: 
```

## ota.cc | Ota::SetHeader | 原文件第30-33行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
30: void Ota::SetHeader(const std::string& key, const std::string& value) {
31:     headers_[key] = value;
32: }
33: 
```

## ota.cc | Ota::SetPostData | 原文件第34-37行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
34: void Ota::SetPostData(const std::string& post_data) {
35:     post_data_ = post_data;
36: }
37: 
```

## ota.cc | Ota::CheckVersion | 原文件第38-48行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
38: bool Ota::CheckVersion() {
39:     current_version_ = esp_app_get_description()->version;
40:     ESP_LOGI(TAG, "Current version: %s", current_version_.c_str());
41: 
42:     if (check_version_url_.length() < 10) {
43:         ESP_LOGE(TAG, "Check version URL is not properly set");
44:         return false;
45:     }
46: 
47:     auto http = Board::GetInstance().CreateHttp();
48:     for (const auto& header : headers_) {
```

## ota.cc | Ota::CheckVersion | 原文件第49-60行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
49:         http->SetHeader(header.first, header.second);
50:     }
51: 
52:     http->SetHeader("Content-Type", "application/json");
53:     std::string method = post_data_.length() > 0 ? "POST" : "GET";
54:     if (!http->Open(method, check_version_url_, post_data_)) {
55:         ESP_LOGE(TAG, "Failed to open HTTP connection");
56:         delete http;
57:         return false;
58:     }
59: 
60:     auto response = http->GetBody();
```

## ota.cc | Ota::CheckVersion | 原文件第61-70行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
61:     http->Close();
62:     delete http;
63: 
64:     // Response: { "firmware": { "version": "1.0.0", "url": "http://" } }
65:     // Parse the JSON response and check if the version is newer
66:     // If it is, set has_new_version_ to true and store the new version and URL
67:     
68:     cJSON *root = cJSON_Parse(response.c_str());
69:     if (root == NULL) {
70:         ESP_LOGE(TAG, "Failed to parse JSON response");
```

## ota.cc | Ota::CheckVersion | 原文件第71-81行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
71:         return false;
72:     }
73: 
74:     has_activation_code_ = false;
75:     cJSON *activation = cJSON_GetObjectItem(root, "activation");
76:     if (activation != NULL) {
77:         cJSON* message = cJSON_GetObjectItem(activation, "message");
78:         if (message != NULL) {
79:             activation_message_ = message->valuestring;
80:         }
81:         cJSON* code = cJSON_GetObjectItem(activation, "code");
```

## ota.cc | Ota::CheckVersion | 原文件第82-93行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
82:         if (code != NULL) {
83:             activation_code_ = code->valuestring;
84:         }
85:         has_activation_code_ = true;
86:     }
87: 
88:     has_mqtt_config_ = false;
89:     cJSON *mqtt = cJSON_GetObjectItem(root, "mqtt");
90:     if (mqtt != NULL) {
91:         Settings settings("mqtt", true);
92:         cJSON *item = NULL;
93:         cJSON_ArrayForEach(item, mqtt) {
```

## ota.cc | Ota::CheckVersion | 原文件第94-104行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
94:             if (item->type == cJSON_String) {
95:                 if (settings.GetString(item->string) != item->valuestring) {
96:                     settings.SetString(item->string, item->valuestring);
97:                 }
98:             }
99:         }
100:         has_mqtt_config_ = true;
101:     }
102: 
103:     has_server_time_ = false;
104:     cJSON *server_time = cJSON_GetObjectItem(root, "server_time");
```

## ota.cc | Ota::CheckVersion | 原文件第105-114行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
105:     if (server_time != NULL) {
106:         cJSON *timestamp = cJSON_GetObjectItem(server_time, "timestamp");
107:         cJSON *timezone_offset = cJSON_GetObjectItem(server_time, "timezone_offset");
108:         
109:         if (timestamp != NULL) {
110:             // 设置系统时间
111:             struct timeval tv;
112:             double ts = timestamp->valuedouble;
113:             
114:             // 如果有时区偏移，计算本地时间
```

## ota.cc | Ota::CheckVersion | 原文件第115-125行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
115:             if (timezone_offset != NULL) {
116:                 ts += (timezone_offset->valueint * 60 * 1000); // 转换分钟为毫秒
117:             }
118:             
119:             tv.tv_sec = (time_t)(ts / 1000);  // 转换毫秒为秒
120:             tv.tv_usec = (suseconds_t)((long long)ts % 1000) * 1000;  // 剩余的毫秒转换为微秒
121:             settimeofday(&tv, NULL);
122:             has_server_time_ = true;
123:         }
124:     }
125: 
```

## ota.cc | Ota::CheckVersion | 原文件第126-135行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
126:     cJSON *firmware = cJSON_GetObjectItem(root, "firmware");
127:     if (firmware == NULL) {
128:         ESP_LOGE(TAG, "Failed to get firmware object");
129:         cJSON_Delete(root);
130:         return false;
131:     }
132:     cJSON *version = cJSON_GetObjectItem(firmware, "version");
133:     if (version == NULL) {
134:         ESP_LOGE(TAG, "Failed to get version object");
135:         cJSON_Delete(root);
```

## ota.cc | Ota::CheckVersion | 原文件第136-148行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
136:         return false;
137:     }
138:     cJSON *url = cJSON_GetObjectItem(firmware, "url");
139:     if (url == NULL) {
140:         ESP_LOGE(TAG, "Failed to get url object");
141:         cJSON_Delete(root);
142:         return false;
143:     }
144: 
145:     firmware_version_ = version->valuestring;
146:     firmware_url_ = url->valuestring;
147:     cJSON_Delete(root);
148: 
```

## ota.cc | Ota::CheckVersion | 原文件第149-158行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
149:     // Check if the version is newer, for example, 0.1.0 is newer than 0.0.1
150:     has_new_version_ = IsNewVersionAvailable(current_version_, firmware_version_);
151:     if (has_new_version_) {
152:         ESP_LOGI(TAG, "New version available: %s", firmware_version_.c_str());
153:     } else {
154:         ESP_LOGI(TAG, "Current is the latest version");
155:     }
156:     return true;
157: }
158: 
```

## ota.cc | Ota::MarkCurrentVersionValid | 原文件第159-167行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
159: void Ota::MarkCurrentVersionValid() {
160:     auto partition = esp_ota_get_running_partition();
161:     if (strcmp(partition->label, "factory") == 0) {
162:         ESP_LOGI(TAG, "Running from factory partition, skipping");
163:         return;
164:     }
165: 
166:     ESP_LOGI(TAG, "Running partition: %s", partition->label);
167:     esp_ota_img_states_t state;
```

## ota.cc | Ota::MarkCurrentVersionValid | 原文件第168-178行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
168:     if (esp_ota_get_state_partition(partition, &state) != ESP_OK) {
169:         ESP_LOGE(TAG, "Failed to get state of partition");
170:         return;
171:     }
172: 
173:     if (state == ESP_OTA_IMG_PENDING_VERIFY) {
174:         ESP_LOGI(TAG, "Marking firmware as valid");
175:         esp_ota_mark_app_valid_cancel_rollback();
176:     }
177: }
178: 
```

## ota.cc | Ota::Upgrade | 原文件第179-187行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
179: void Ota::Upgrade(const std::string& firmware_url) {
180:     ESP_LOGI(TAG, "Upgrading firmware from %s", firmware_url.c_str());
181:     esp_ota_handle_t update_handle = 0;
182:     auto update_partition = esp_ota_get_next_update_partition(NULL);
183:     if (update_partition == NULL) {
184:         ESP_LOGE(TAG, "Failed to get update partition");
185:         return;
186:     }
187: 
```

## ota.cc | Ota::Upgrade | 原文件第188-198行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
188:     ESP_LOGI(TAG, "Writing to partition %s at offset 0x%lx", update_partition->label, update_partition->address);
189:     bool image_header_checked = false;
190:     std::string image_header;
191: 
192:     auto http = Board::GetInstance().CreateHttp();
193:     if (!http->Open("GET", firmware_url)) {
194:         ESP_LOGE(TAG, "Failed to open HTTP connection");
195:         delete http;
196:         return;
197:     }
198: 
```

## ota.cc | Ota::Upgrade | 原文件第199-210行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
199:     size_t content_length = http->GetBodyLength();
200:     if (content_length == 0) {
201:         ESP_LOGE(TAG, "Failed to get content length");
202:         delete http;
203:         return;
204:     }
205: 
206:     char buffer[512];
207:     size_t total_read = 0, recent_read = 0;
208:     auto last_calc_time = esp_timer_get_time();
209:     while (true) {
210:         int ret = http->Read(buffer, sizeof(buffer));
```

## ota.cc | Ota::Upgrade | 原文件第211-220行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
211:         if (ret < 0) {
212:             ESP_LOGE(TAG, "Failed to read HTTP data: %s", esp_err_to_name(ret));
213:             delete http;
214:             return;
215:         }
216: 
217:         // Calculate speed and progress every second
218:         recent_read += ret;
219:         total_read += ret;
220:         if (esp_timer_get_time() - last_calc_time >= 1000000 || ret == 0) {
```

## ota.cc | Ota::Upgrade | 原文件第221-229行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
221:             size_t progress = total_read * 100 / content_length;
222:             ESP_LOGI(TAG, "Progress: %zu%% (%zu/%zu), Speed: %zuB/s", progress, total_read, content_length, recent_read);
223:             if (upgrade_callback_) {
224:                 upgrade_callback_(progress, recent_read);
225:             }
226:             last_calc_time = esp_timer_get_time();
227:             recent_read = 0;
228:         }
229: 
```

## ota.cc | Ota::Upgrade | 原文件第230-237行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
230:         if (ret == 0) {
231:             break;
232:         }
233: 
234:         if (!image_header_checked) {
235:             image_header.append(buffer, ret);
236:             if (image_header.size() >= sizeof(esp_image_header_t) + sizeof(esp_image_segment_header_t) + sizeof(esp_app_desc_t)) {
237:                 esp_app_desc_t new_app_info;
```

## ota.cc | Ota::Upgrade | 原文件第238-242行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
238:                 memcpy(&new_app_info, image_header.data() + sizeof(esp_image_header_t) + sizeof(esp_image_segment_header_t), sizeof(esp_app_desc_t));
239:                 ESP_LOGI(TAG, "New firmware version: %s", new_app_info.version);
240: 
241:                 auto current_version = esp_app_get_description()->version;
242:                 if (memcmp(new_app_info.version, current_version, sizeof(new_app_info.version)) == 0) {
```

## ota.cc | Ota::Upgrade | 原文件第243-250行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
243:                     ESP_LOGE(TAG, "Firmware version is the same, skipping upgrade");
244:                     delete http;
245:                     return;
246:                 }
247: 
248:                 if (esp_ota_begin(update_partition, OTA_WITH_SEQUENTIAL_WRITES, &update_handle)) {
249:                     esp_ota_abort(update_handle);
250:                     delete http;
```

## ota.cc | Ota::Upgrade | 原文件第251-260行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
251:                     ESP_LOGE(TAG, "Failed to begin OTA");
252:                     return;
253:                 }
254: 
255:                 image_header_checked = true;
256:                 std::string().swap(image_header);
257:             }
258:         }
259:         auto err = esp_ota_write(update_handle, buffer, ret);
260:         if (err != ESP_OK) {
```

## ota.cc | Ota::Upgrade | 原文件第261-271行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
261:             ESP_LOGE(TAG, "Failed to write OTA data: %s", esp_err_to_name(err));
262:             esp_ota_abort(update_handle);
263:             delete http;
264:             return;
265:         }
266:     }
267:     delete http;
268: 
269:     esp_err_t err = esp_ota_end(update_handle);
270:     if (err != ESP_OK) {
271:         if (err == ESP_ERR_OTA_VALIDATE_FAILED) {
```

## ota.cc | Ota::Upgrade | 原文件第272-282行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
272:             ESP_LOGE(TAG, "Image validation failed, image is corrupted");
273:         } else {
274:             ESP_LOGE(TAG, "Failed to end OTA: %s", esp_err_to_name(err));
275:         }
276:         return;
277:     }
278: 
279:     err = esp_ota_set_boot_partition(update_partition);
280:     if (err != ESP_OK) {
281:         ESP_LOGE(TAG, "Failed to set boot partition: %s", esp_err_to_name(err));
282:         return;
```

## ota.cc | Ota::Upgrade | 原文件第283-289行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
283:     }
284: 
285:     ESP_LOGI(TAG, "Firmware upgrade successful, rebooting in 3 seconds...");
286:     vTaskDelay(pdMS_TO_TICKS(3000));
287:     esp_restart();
288: }
289: 
```

## ota.cc | Ota::StartUpgrade | 原文件第290-294行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
290: void Ota::StartUpgrade(std::function<void(int progress, size_t speed)> callback) {
291:     upgrade_callback_ = callback;
292:     Upgrade(firmware_url_);
293: }
294: 
```

## ota.cc | Ota::ParseVersion | 原文件第295-306行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
295: std::vector<int> Ota::ParseVersion(const std::string& version) {
296:     std::vector<int> versionNumbers;
297:     std::stringstream ss(version);
298:     std::string segment;
299:     
300:     while (std::getline(ss, segment, '.')) {
301:         versionNumbers.push_back(std::stoi(segment));
302:     }
303:     
304:     return versionNumbers;
305: }
306: 
```

## ota.cc | Ota::IsNewVersionAvailable | 原文件第307-313行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
307: bool Ota::IsNewVersionAvailable(const std::string& currentVersion, const std::string& newVersion) {
308:     std::vector<int> current = ParseVersion(currentVersion);
309:     std::vector<int> newer = ParseVersion(newVersion);
310:     
311:     for (size_t i = 0; i < std::min(current.size(), newer.size()); ++i) {
312:         if (newer[i] > current[i]) {
313:             return true;
```

## ota.cc | Ota::IsNewVersionAvailable | 原文件第314-320行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.cc
以下为原始源码，不是截图OCR。
```
314:         } else if (newer[i] < current[i]) {
315:             return false;
316:         }
317:     }
318:     
319:     return newer.size() > current.size();
320: }
```

## ota.h | 文件开头/全局定义 | 原文件第1-16行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.h
以下为原始源码，不是截图OCR。
```
1: #ifndef _OTA_H
2: #define _OTA_H
3: 
4: #include <functional>
5: #include <string>
6: #include <map>
7: 
8: class Ota {
9: public:
10:     Ota();
11:     ~Ota();
12: 
13:     void SetCheckVersionUrl(std::string check_version_url);
14:     void SetHeader(const std::string& key, const std::string& value);
15:     void SetPostData(const std::string& post_data);
16:     bool CheckVersion();
```

## ota.h | HasNewVersion | 原文件第17-17行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.h
以下为原始源码，不是截图OCR。
```
17:     bool HasNewVersion() { return has_new_version_; }
```

## ota.h | HasMqttConfig | 原文件第18-18行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.h
以下为原始源码，不是截图OCR。
```
18:     bool HasMqttConfig() { return has_mqtt_config_; }
```

## ota.h | HasActivationCode | 原文件第19-19行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.h
以下为原始源码，不是截图OCR。
```
19:     bool HasActivationCode() { return has_activation_code_; }
```

## ota.h | HasServerTime | 原文件第20-25行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.h
以下为原始源码，不是截图OCR。
```
20:     bool HasServerTime() { return has_server_time_; }
21:     void StartUpgrade(std::function<void(int progress, size_t speed)> callback);
22:     void MarkCurrentVersionValid();
23: 
24:     const std::string& GetFirmwareVersion() const { return firmware_version_; }
25:     const std::string& GetCurrentVersion() const { return current_version_; }
```

## ota.h | HasServerTime | 原文件第26-35行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.h
以下为原始源码，不是截图OCR。
```
26:     const std::string& GetActivationMessage() const { return activation_message_; }
27:     const std::string& GetActivationCode() const { return activation_code_; }
28: 
29: private:
30:     std::string check_version_url_;
31:     std::string activation_message_;
32:     std::string activation_code_;
33:     bool has_new_version_ = false;
34:     bool has_mqtt_config_ = false;
35:     bool has_server_time_ = false;
```

## ota.h | HasServerTime | 原文件第36-44行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.h
以下为原始源码，不是截图OCR。
```
36:     bool has_activation_code_ = false;
37:     std::string current_version_;
38:     std::string firmware_version_;
39:     std::string firmware_url_;
40:     std::string post_data_;
41:     std::map<std::string, std::string> headers_;
42: 
43:     void Upgrade(const std::string& firmware_url);
44:     std::function<void(int progress, size_t speed)> upgrade_callback_;
```

## ota.h | HasServerTime | 原文件第45-49行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/ota.h
以下为原始源码，不是截图OCR。
```
45:     std::vector<int> ParseVersion(const std::string& version);
46:     bool IsNewVersionAvailable(const std::string& currentVersion, const std::string& newVersion);
47: };
48: 
49: #endif // _OTA_H
```

## mqtt_protocol.cc | 文件开头/全局定义 | 原文件第1-19行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
1: #include "mqtt_protocol.h"
2: #include "board.h"
3: #include "application.h"
4: #include "settings.h"
5: 
6: #include <esp_log.h>
7: #include <ml307_mqtt.h>
8: #include <ml307_udp.h>
9: #include <cstring>
10: #include <arpa/inet.h>
11: #include "assets/lang_config.h"
12: 
13: #define TAG "MQTT"
14: 
15: MqttProtocol::MqttProtocol() {
16:     event_group_handle_ = xEventGroupCreate();
17: }
18: 
19: MqttProtocol::~MqttProtocol() {
```

## mqtt_protocol.cc | 文件开头/全局定义 | 原文件第20-29行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
20:     ESP_LOGI(TAG, "MqttProtocol deinit");
21:     if (udp_ != nullptr) {
22:         delete udp_;
23:     }
24:     if (mqtt_ != nullptr) {
25:         delete mqtt_;
26:     }
27:     vEventGroupDelete(event_group_handle_);
28: }
29: 
```

## mqtt_protocol.cc | MqttProtocol::Start | 原文件第30-33行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
30: void MqttProtocol::Start() {
31:     StartMqttClient(false);
32: }
33: 
```

## mqtt_protocol.cc | MqttProtocol::StartMqttClient | 原文件第34-43行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
34: bool MqttProtocol::StartMqttClient(bool report_error) {
35:     if (mqtt_ != nullptr) {
36:         ESP_LOGW(TAG, "Mqtt client already started");
37:         delete mqtt_;
38:     }
39: 
40:     Settings settings("mqtt", false);
41:     endpoint_ = settings.GetString("endpoint");
42:     client_id_ = settings.GetString("client_id");
43:     username_ = settings.GetString("username");
```

## mqtt_protocol.cc | MqttProtocol::StartMqttClient | 原文件第44-55行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
44:     password_ = settings.GetString("password");
45:     publish_topic_ = settings.GetString("publish_topic");
46: 
47:     if (endpoint_.empty()) {
48:         ESP_LOGW(TAG, "MQTT endpoint is not specified");
49:         if (report_error) {
50:             SetError(Lang::Strings::SERVER_NOT_FOUND);
51:         }
52:         return false;
53:     }
54: 
55:     mqtt_ = Board::GetInstance().CreateMqtt();
```

## mqtt_protocol.cc | MqttProtocol::StartMqttClient | 原文件第56-66行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
56:     mqtt_->SetKeepAlive(90);
57: 
58:     mqtt_->OnDisconnected([this]() {
59:         ESP_LOGI(TAG, "Disconnected from endpoint");
60:     });
61: 
62:     mqtt_->OnMessage([this](const std::string& topic, const std::string& payload) {
63:         cJSON* root = cJSON_Parse(payload.c_str());
64:         if (root == nullptr) {
65:             ESP_LOGE(TAG, "Failed to parse json message %s", payload.c_str());
66:             return;
```

## mqtt_protocol.cc | MqttProtocol::StartMqttClient | 原文件第67-77行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
67:         }
68:         cJSON* type = cJSON_GetObjectItem(root, "type");
69:         if (type == nullptr) {
70:             ESP_LOGE(TAG, "Message type is not specified");
71:             cJSON_Delete(root);
72:             return;
73:         }
74: 
75:         if (strcmp(type->valuestring, "hello") == 0) {
76:             ParseServerHello(root);
77:         } else if (strcmp(type->valuestring, "goodbye") == 0) {
```

## mqtt_protocol.cc | MqttProtocol::StartMqttClient | 原文件第78-84行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
78:             auto session_id = cJSON_GetObjectItem(root, "session_id");
79:             ESP_LOGI(TAG, "Received goodbye message, session_id: %s", session_id ? session_id->valuestring : "null");
80:             if (session_id == nullptr || session_id_ == session_id->valuestring) {
81:                 Application::GetInstance().Schedule([this]() {
82:                     CloseAudioChannel();
83:                 });
84:             }
```

## mqtt_protocol.cc | MqttProtocol::StartMqttClient | 原文件第85-94行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
85:         } else if (on_incoming_json_ != nullptr) {
86:             on_incoming_json_(root);
87:         }
88:         cJSON_Delete(root);
89:         last_incoming_time_ = std::chrono::steady_clock::now();
90:     });
91: 
92:     ESP_LOGI(TAG, "Connecting to endpoint %s", endpoint_.c_str());
93:     if (!mqtt_->Connect(endpoint_, 8883, client_id_, username_, password_)) {
94:         ESP_LOGE(TAG, "Failed to connect to endpoint");
```

## mqtt_protocol.cc | MqttProtocol::StartMqttClient | 原文件第95-102行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
95:         SetError(Lang::Strings::SERVER_NOT_CONNECTED);
96:         return false;
97:     }
98: 
99:     ESP_LOGI(TAG, "Connected to endpoint");
100:     return true;
101: }
102: 
```

## mqtt_protocol.cc | MqttProtocol::SendText | 原文件第103-112行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
103: void MqttProtocol::SendText(const std::string& text) {
104:     if (publish_topic_.empty()) {
105:         return;
106:     }
107:     if (!mqtt_->Publish(publish_topic_, text)) {
108:         ESP_LOGE(TAG, "Failed to publish message: %s", text.c_str());
109:         SetError(Lang::Strings::SERVER_ERROR);
110:     }
111: }
112: 
```

## mqtt_protocol.cc | MqttProtocol::SendAudio | 原文件第113-123行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
113: void MqttProtocol::SendAudio(const std::vector<uint8_t>& data) {
114:     std::lock_guard<std::mutex> lock(channel_mutex_);
115:     if (udp_ == nullptr) {
116:         return;
117:     }
118: 
119:     std::string nonce(aes_nonce_);
120:     *(uint16_t*)&nonce[2] = htons(data.size());
121:     *(uint32_t*)&nonce[12] = htonl(++local_sequence_);
122: 
123:     std::string encrypted;
```

## mqtt_protocol.cc | MqttProtocol::SendAudio | 原文件第124-130行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
124:     encrypted.resize(aes_nonce_.size() + data.size());
125:     memcpy(encrypted.data(), nonce.data(), nonce.size());
126: 
127:     size_t nc_off = 0;
128:     uint8_t stream_block[16] = {0};
129:     if (mbedtls_aes_crypt_ctr(&aes_ctx_, data.size(), &nc_off, (uint8_t*)nonce.c_str(), stream_block,
130:         (uint8_t*)data.data(), (uint8_t*)&encrypted[nonce.size()]) != 0) {
```

## mqtt_protocol.cc | MqttProtocol::SendAudio | 原文件第131-136行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
131:         ESP_LOGE(TAG, "Failed to encrypt audio data");
132:         return;
133:     }
134:     udp_->Send(encrypted);
135: }
136: 
```

## mqtt_protocol.cc | MqttProtocol::CloseAudioChannel | 原文件第137-149行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
137: void MqttProtocol::CloseAudioChannel() {
138:     {
139:         std::lock_guard<std::mutex> lock(channel_mutex_);
140:         if (udp_ != nullptr) {
141:             delete udp_;
142:             udp_ = nullptr;
143:         }
144:     }
145: 
146:     std::string message = "{";
147:     message += "\"session_id\":\"" + session_id_ + "\",";
148:     message += "\"type\":\"goodbye\"";
149:     message += "}";
```

## mqtt_protocol.cc | MqttProtocol::CloseAudioChannel | 原文件第150-156行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
150:     SendText(message);
151: 
152:     if (on_audio_channel_closed_ != nullptr) {
153:         on_audio_channel_closed_();
154:     }
155: }
156: 
```

## mqtt_protocol.cc | MqttProtocol::OpenAudioChannel | 原文件第157-168行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
157: bool MqttProtocol::OpenAudioChannel() {
158:     if (mqtt_ == nullptr || !mqtt_->IsConnected()) {
159:         ESP_LOGI(TAG, "MQTT is not connected, try to connect now");
160:         if (!StartMqttClient(true)) {
161:             return false;
162:         }
163:     }
164: 
165:     error_occurred_ = false;
166:     session_id_ = "";
167:     xEventGroupClearBits(event_group_handle_, MQTT_PROTOCOL_SERVER_HELLO_EVENT);
168: 
```

## mqtt_protocol.cc | MqttProtocol::OpenAudioChannel | 原文件第169-177行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
169:     // 发送 hello 消息申请 UDP 通道
170:     std::string message = "{";
171:     message += "\"type\":\"hello\",";
172:     message += "\"version\": 3,";
173:     message += "\"transport\":\"udp\",";
174:     message += "\"audio_params\":{";
175:     message += "\"format\":\"opus\", \"sample_rate\":16000, \"channels\":1, \"frame_duration\":" + std::to_string(OPUS_FRAME_DURATION_MS);
176:     message += "}}";
177:     SendText(message);
```

## mqtt_protocol.cc | MqttProtocol::OpenAudioChannel | 原文件第178-186行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
178: 
179:     // 等待服务器响应
180:     EventBits_t bits = xEventGroupWaitBits(event_group_handle_, MQTT_PROTOCOL_SERVER_HELLO_EVENT, pdTRUE, pdFALSE, pdMS_TO_TICKS(10000));
181:     if (!(bits & MQTT_PROTOCOL_SERVER_HELLO_EVENT)) {
182:         ESP_LOGE(TAG, "Failed to receive server hello");
183:         SetError(Lang::Strings::SERVER_TIMEOUT);
184:         return false;
185:     }
186: 
```

## mqtt_protocol.cc | MqttProtocol::OpenAudioChannel | 原文件第187-196行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
187:     std::lock_guard<std::mutex> lock(channel_mutex_);
188:     if (udp_ != nullptr) {
189:         delete udp_;
190:     }
191:     udp_ = Board::GetInstance().CreateUdp();
192:     udp_->OnMessage([this](const std::string& data) {
193:         if (data.size() < sizeof(aes_nonce_)) {
194:             ESP_LOGE(TAG, "Invalid audio packet size: %zu", data.size());
195:             return;
196:         }
```

## mqtt_protocol.cc | MqttProtocol::OpenAudioChannel | 原文件第197-205行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
197:         if (data[0] != 0x01) {
198:             ESP_LOGE(TAG, "Invalid audio packet type: %x", data[0]);
199:             return;
200:         }
201:         uint32_t sequence = ntohl(*(uint32_t*)&data[12]);
202:         if (sequence < remote_sequence_) {
203:             ESP_LOGW(TAG, "Received audio packet with old sequence: %lu, expected: %lu", sequence, remote_sequence_);
204:             return;
205:         }
```

## mqtt_protocol.cc | MqttProtocol::OpenAudioChannel | 原文件第206-213行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
206:         if (sequence != remote_sequence_ + 1) {
207:             ESP_LOGW(TAG, "Received audio packet with wrong sequence: %lu, expected: %lu", sequence, remote_sequence_ + 1);
208:         }
209: 
210:         std::vector<uint8_t> decrypted;
211:         size_t decrypted_size = data.size() - aes_nonce_.size();
212:         size_t nc_off = 0;
213:         uint8_t stream_block[16] = {0};
```

## mqtt_protocol.cc | MqttProtocol::OpenAudioChannel | 原文件第214-219行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
214:         decrypted.resize(decrypted_size);
215:         auto nonce = (uint8_t*)data.data();
216:         auto encrypted = (uint8_t*)data.data() + aes_nonce_.size();
217:         int ret = mbedtls_aes_crypt_ctr(&aes_ctx_, decrypted_size, &nc_off, nonce, stream_block, encrypted, (uint8_t*)decrypted.data());
218:         if (ret != 0) {
219:             ESP_LOGE(TAG, "Failed to decrypt audio data, ret: %d", ret);
```

## mqtt_protocol.cc | MqttProtocol::OpenAudioChannel | 原文件第220-231行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
220:             return;
221:         }
222:         if (on_incoming_audio_ != nullptr) {
223:             on_incoming_audio_(std::move(decrypted));
224:         }
225:         remote_sequence_ = sequence;
226:         last_incoming_time_ = std::chrono::steady_clock::now();
227:     });
228: 
229:     udp_->Connect(udp_server_, udp_port_);
230: 
231:     if (on_audio_channel_opened_ != nullptr) {
```

## mqtt_protocol.cc | MqttProtocol::OpenAudioChannel | 原文件第232-236行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
232:         on_audio_channel_opened_();
233:     }
234:     return true;
235: }
236: 
```

## mqtt_protocol.cc | MqttProtocol::ParseServerHello | 原文件第237-245行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
237: void MqttProtocol::ParseServerHello(const cJSON* root) {
238:     auto transport = cJSON_GetObjectItem(root, "transport");
239:     if (transport == nullptr || strcmp(transport->valuestring, "udp") != 0) {
240:         ESP_LOGE(TAG, "Unsupported transport: %s", transport->valuestring);
241:         return;
242:     }
243: 
244:     auto session_id = cJSON_GetObjectItem(root, "session_id");
245:     if (session_id != nullptr) {
```

## mqtt_protocol.cc | MqttProtocol::ParseServerHello | 原文件第246-254行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
246:         session_id_ = session_id->valuestring;
247:         ESP_LOGI(TAG, "Session ID: %s", session_id_.c_str());
248:     }
249: 
250:     // Get sample rate from hello message
251:     auto audio_params = cJSON_GetObjectItem(root, "audio_params");
252:     if (audio_params != NULL) {
253:         auto sample_rate = cJSON_GetObjectItem(audio_params, "sample_rate");
254:         if (sample_rate != NULL) {
```

## mqtt_protocol.cc | MqttProtocol::ParseServerHello | 原文件第255-265行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
255:             server_sample_rate_ = sample_rate->valueint;
256:         }
257:     }
258: 
259:     auto udp = cJSON_GetObjectItem(root, "udp");
260:     if (udp == nullptr) {
261:         ESP_LOGE(TAG, "UDP is not specified");
262:         return;
263:     }
264:     udp_server_ = cJSON_GetObjectItem(udp, "server")->valuestring;
265:     udp_port_ = cJSON_GetObjectItem(udp, "port")->valueint;
```

## mqtt_protocol.cc | MqttProtocol::ParseServerHello | 原文件第266-272行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
266:     auto key = cJSON_GetObjectItem(udp, "key")->valuestring;
267:     auto nonce = cJSON_GetObjectItem(udp, "nonce")->valuestring;
268: 
269:     // auto encryption = cJSON_GetObjectItem(udp, "encryption")->valuestring;
270:     // ESP_LOGI(TAG, "UDP server: %s, port: %d, encryption: %s", udp_server_.c_str(), udp_port_, encryption);
271:     aes_nonce_ = DecodeHexString(nonce);
272:     mbedtls_aes_init(&aes_ctx_);
```

## mqtt_protocol.cc | MqttProtocol::ParseServerHello | 原文件第273-280行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
273:     mbedtls_aes_setkey_enc(&aes_ctx_, (const unsigned char*)DecodeHexString(key).c_str(), 128);
274:     local_sequence_ = 0;
275:     remote_sequence_ = 0;
276:     xEventGroupSetBits(event_group_handle_, MQTT_PROTOCOL_SERVER_HELLO_EVENT);
277: }
278: 
279: static const char hex_chars[] = "0123456789ABCDEF";
280: // 辅助函数，将单个十六进制字符转换为对应的数值
```

## mqtt_protocol.cc | CharToHex | 原文件第281-287行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
281: static inline uint8_t CharToHex(char c) {
282:     if (c >= '0' && c <= '9') return c - '0';
283:     if (c >= 'A' && c <= 'F') return c - 'A' + 10;
284:     if (c >= 'a' && c <= 'f') return c - 'a' + 10;
285:     return 0;  // 对于无效输入，返回0
286: }
287: 
```

## mqtt_protocol.cc | MqttProtocol::DecodeHexString | 原文件第288-297行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
288: std::string MqttProtocol::DecodeHexString(const std::string& hex_string) {
289:     std::string decoded;
290:     decoded.reserve(hex_string.size() / 2);
291:     for (size_t i = 0; i < hex_string.size(); i += 2) {
292:         char byte = (CharToHex(hex_string[i]) << 4) | CharToHex(hex_string[i + 1]);
293:         decoded.push_back(byte);
294:     }
295:     return decoded;
296: }
297: 
```

## mqtt_protocol.cc | MqttProtocol::DecodeHexString | 原文件第298-300行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.cc
以下为原始源码，不是截图OCR。
```
298: bool MqttProtocol::IsAudioChannelOpened() const {
299:     return udp_ != nullptr && !error_occurred_ && !IsTimeout();
300: }
```

## mqtt_protocol.h | 文件开头/全局定义 | 原文件第1-19行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.h
以下为原始源码，不是截图OCR。
```
1: #ifndef MQTT_PROTOCOL_H
2: #define MQTT_PROTOCOL_H
3: 
4: 
5: #include "protocol.h"
6: #include <mqtt.h>
7: #include <udp.h>
8: #include <cJSON.h>
9: #include <mbedtls/aes.h>
10: #include <freertos/FreeRTOS.h>
11: #include <freertos/event_groups.h>
12: 
13: #include <functional>
14: #include <string>
15: #include <map>
16: #include <mutex>
17: 
18: #define MQTT_PING_INTERVAL_SECONDS 90
19: #define MQTT_RECONNECT_INTERVAL_MS 10000
```

## mqtt_protocol.h | 文件开头/全局定义 | 原文件第20-34行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.h
以下为原始源码，不是截图OCR。
```
20: 
21: #define MQTT_PROTOCOL_SERVER_HELLO_EVENT (1 << 0)
22: 
23: class MqttProtocol : public Protocol {
24: public:
25:     MqttProtocol();
26:     ~MqttProtocol();
27: 
28:     void Start() override;
29:     void SendAudio(const std::vector<uint8_t>& data) override;
30:     bool OpenAudioChannel() override;
31:     void CloseAudioChannel() override;
32:     bool IsAudioChannelOpened() const override;
33: 
34: private:
```

## mqtt_protocol.h | 文件开头/全局定义 | 原文件第35-49行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.h
以下为原始源码，不是截图OCR。
```
35:     EventGroupHandle_t event_group_handle_;
36: 
37:     std::string endpoint_;
38:     std::string client_id_;
39:     std::string username_;
40:     std::string password_;
41:     std::string publish_topic_;
42: 
43:     std::mutex channel_mutex_;
44:     Mqtt* mqtt_ = nullptr;
45:     Udp* udp_ = nullptr;
46:     mbedtls_aes_context aes_ctx_;
47:     std::string aes_nonce_;
48:     std::string udp_server_;
49:     int udp_port_;
```

## mqtt_protocol.h | 文件开头/全局定义 | 原文件第50-61行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/mqtt_protocol.h
以下为原始源码，不是截图OCR。
```
50:     uint32_t local_sequence_;
51:     uint32_t remote_sequence_;
52: 
53:     bool StartMqttClient(bool report_error=false);
54:     void ParseServerHello(const cJSON* root);
55:     std::string DecodeHexString(const std::string& hex_string);
56: 
57:     void SendText(const std::string& text) override;
58: };
59: 
60: 
61: #endif // MQTT_PROTOCOL_H
```

## protocol.cc | 文件开头/全局定义 | 原文件第1-6行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.cc
以下为原始源码，不是截图OCR。
```
1: #include "protocol.h"
2: 
3: #include <esp_log.h>
4: 
5: #define TAG "Protocol"
6: 
```

## protocol.cc | Protocol::OnIncomingJson | 原文件第7-10行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.cc
以下为原始源码，不是截图OCR。
```
7: void Protocol::OnIncomingJson(std::function<void(const cJSON* root)> callback) {
8:     on_incoming_json_ = callback;
9: }
10: 
```

## protocol.cc | Protocol::OnIncomingAudio | 原文件第11-14行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.cc
以下为原始源码，不是截图OCR。
```
11: void Protocol::OnIncomingAudio(std::function<void(std::vector<uint8_t>&& data)> callback) {
12:     on_incoming_audio_ = callback;
13: }
14: 
```

## protocol.cc | Protocol::OnAudioChannelOpened | 原文件第15-18行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.cc
以下为原始源码，不是截图OCR。
```
15: void Protocol::OnAudioChannelOpened(std::function<void()> callback) {
16:     on_audio_channel_opened_ = callback;
17: }
18: 
```

## protocol.cc | Protocol::OnAudioChannelClosed | 原文件第19-22行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.cc
以下为原始源码，不是截图OCR。
```
19: void Protocol::OnAudioChannelClosed(std::function<void()> callback) {
20:     on_audio_channel_closed_ = callback;
21: }
22: 
```

## protocol.cc | Protocol::OnNetworkError | 原文件第23-26行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.cc
以下为原始源码，不是截图OCR。
```
23: void Protocol::OnNetworkError(std::function<void(const std::string& message)> callback) {
24:     on_network_error_ = callback;
25: }
26: 
```

## protocol.cc | Protocol::SetError | 原文件第27-33行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.cc
以下为原始源码，不是截图OCR。
```
27: void Protocol::SetError(const std::string& message) {
28:     error_occurred_ = true;
29:     if (on_network_error_ != nullptr) {
30:         on_network_error_(message);
31:     }
32: }
33: 
```

## protocol.cc | Protocol::SendAbortSpeaking | 原文件第34-42行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.cc
以下为原始源码，不是截图OCR。
```
34: void Protocol::SendAbortSpeaking(AbortReason reason) {
35:     std::string message = "{\"session_id\":\"" + session_id_ + "\",\"type\":\"abort\"";
36:     if (reason == kAbortReasonWakeWordDetected) {
37:         message += ",\"reason\":\"wake_word_detected\"";
38:     }
39:     message += "}";
40:     SendText(message);
41: }
42: 
```

## protocol.cc | Protocol::SendWakeWordDetected | 原文件第43-48行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.cc
以下为原始源码，不是截图OCR。
```
43: void Protocol::SendWakeWordDetected(const std::string& wake_word) {
44:     std::string json = "{\"session_id\":\"" + session_id_ + 
45:                       "\",\"type\":\"listen\",\"state\":\"detect\",\"text\":\"" + wake_word + "\"}";
46:     SendText(json);
47: }
48: 
```

## protocol.cc | Protocol::SendStartListening | 原文件第49-56行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.cc
以下为原始源码，不是截图OCR。
```
49: void Protocol::SendStartListening(ListeningMode mode) {
50:     std::string message = "{\"session_id\":\"" + session_id_ + "\"";
51:     message += ",\"type\":\"listen\",\"state\":\"start\"";
52:     if (mode == kListeningModeAlwaysOn) {
53:         message += ",\"mode\":\"realtime\"";
54:     } else if (mode == kListeningModeAutoStop) {
55:         message += ",\"mode\":\"auto\"";
56:     } else {
```

## protocol.cc | Protocol::SendStartListening | 原文件第57-62行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.cc
以下为原始源码，不是截图OCR。
```
57:         message += ",\"mode\":\"manual\"";
58:     }
59:     message += "}";
60:     SendText(message);
61: }
62: 
```

## protocol.cc | Protocol::SendStopListening | 原文件第63-67行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.cc
以下为原始源码，不是截图OCR。
```
63: void Protocol::SendStopListening() {
64:     std::string message = "{\"session_id\":\"" + session_id_ + "\",\"type\":\"listen\",\"state\":\"stop\"}";
65:     SendText(message);
66: }
67: 
```

## protocol.cc | Protocol::SendIotDescriptors | 原文件第68-78行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.cc
以下为原始源码，不是截图OCR。
```
68: void Protocol::SendIotDescriptors(const std::string& descriptors) {
69:     cJSON* root = cJSON_Parse(descriptors.c_str());
70:     if (root == nullptr) {
71:         ESP_LOGE(TAG, "Failed to parse IoT descriptors: %s", descriptors.c_str());
72:         return;
73:     }
74: 
75:     if (!cJSON_IsArray(root)) {
76:         ESP_LOGE(TAG, "IoT descriptors should be an array");
77:         cJSON_Delete(root);
78:         return;
```

## protocol.cc | Protocol::SendIotDescriptors | 原文件第79-89行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.cc
以下为原始源码，不是截图OCR。
```
79:     }
80: 
81:     int arraySize = cJSON_GetArraySize(root);
82:     for (int i = 0; i < arraySize; ++i) {
83:         cJSON* descriptor = cJSON_GetArrayItem(root, i);
84:         if (descriptor == nullptr) {
85:             ESP_LOGE(TAG, "Failed to get IoT descriptor at index %d", i);
86:             continue;
87:         }
88: 
89:         cJSON* messageRoot = cJSON_CreateObject();
```

## protocol.cc | Protocol::SendIotDescriptors | 原文件第90-96行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.cc
以下为原始源码，不是截图OCR。
```
90:         cJSON_AddStringToObject(messageRoot, "session_id", session_id_.c_str());
91:         cJSON_AddStringToObject(messageRoot, "type", "iot");
92:         cJSON_AddBoolToObject(messageRoot, "update", true);
93: 
94:         cJSON* descriptorArray = cJSON_CreateArray();
95:         cJSON_AddItemToArray(descriptorArray, cJSON_Duplicate(descriptor, 1));
96:         cJSON_AddItemToObject(messageRoot, "descriptors", descriptorArray);
```

## protocol.cc | Protocol::SendIotDescriptors | 原文件第97-109行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.cc
以下为原始源码，不是截图OCR。
```
97: 
98:         char* message = cJSON_PrintUnformatted(messageRoot);
99:         if (message == nullptr) {
100:             ESP_LOGE(TAG, "Failed to print JSON message for IoT descriptor at index %d", i);
101:             cJSON_Delete(messageRoot);
102:             continue;
103:         }
104: 
105:         SendText(std::string(message));
106:         cJSON_free(message);
107:         cJSON_Delete(messageRoot);
108:     }
109: 
```

## protocol.cc | Protocol::SendIotDescriptors | 原文件第110-112行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.cc
以下为原始源码，不是截图OCR。
```
110:     cJSON_Delete(root);
111: }
112: 
```

## protocol.cc | Protocol::SendIotStates | 原文件第113-120行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.cc
以下为原始源码，不是截图OCR。
```
113: void Protocol::SendIotStates(const std::string& states) {
114:     std::string message = "{\"session_id\":\"" + session_id_ + "\",\"type\":\"iot\",\"update\":true,\"states\":" + states + "}";
115:     SendText(message);
116: }
117: 
118: bool Protocol::IsTimeout() const {
119:     const int kTimeoutSeconds = 120;
120:     auto now = std::chrono::steady_clock::now();
```

## protocol.cc | Protocol::SendIotStates | 原文件第121-128行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.cc
以下为原始源码，不是截图OCR。
```
121:     auto duration = std::chrono::duration_cast<std::chrono::seconds>(now - last_incoming_time_);
122:     bool timeout = duration.count() > kTimeoutSeconds;
123:     if (timeout) {
124:         ESP_LOGE(TAG, "Channel timeout %lld seconds", duration.count());
125:     }
126:     return timeout;
127: }
128: 
```

## protocol.h | 文件开头/全局定义 | 原文件第1-21行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.h
以下为原始源码，不是截图OCR。
```
1: #ifndef PROTOCOL_H
2: #define PROTOCOL_H
3: 
4: #include <cJSON.h>
5: #include <string>
6: #include <functional>
7: #include <chrono>
8: 
9: struct BinaryProtocol3 {
10:     uint8_t type;
11:     uint8_t reserved;
12:     uint16_t payload_size;
13:     uint8_t payload[];
14: } __attribute__((packed));
15: 
16: enum AbortReason {
17:     kAbortReasonNone,
18:     kAbortReasonWakeWordDetected
19: };
20: 
21: enum ListeningMode {
```

## protocol.h | 文件开头/全局定义 | 原文件第22-37行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.h
以下为原始源码，不是截图OCR。
```
22:     kListeningModeAutoStop,
23:     kListeningModeManualStop,
24:     kListeningModeAlwaysOn // 需要 AEC 支持
25: };
26: 
27: class Protocol {
28: public:
29:     virtual ~Protocol() = default;
30: 
31:     inline int server_sample_rate() const {
32:         return server_sample_rate_;
33:     }
34:     inline const std::string& session_id() const {
35:         return session_id_;
36:     }
37: 
```

## protocol.h | 文件开头/全局定义 | 原文件第38-44行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.h
以下为原始源码，不是截图OCR。
```
38:     void OnIncomingAudio(std::function<void(std::vector<uint8_t>&& data)> callback);
39:     void OnIncomingJson(std::function<void(const cJSON* root)> callback);
40:     void OnAudioChannelOpened(std::function<void()> callback);
41:     void OnAudioChannelClosed(std::function<void()> callback);
42:     void OnNetworkError(std::function<void(const std::string& message)> callback);
43: 
44:     virtual void Start() = 0;
```

## protocol.h | 文件开头/全局定义 | 原文件第45-51行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.h
以下为原始源码，不是截图OCR。
```
45:     virtual bool OpenAudioChannel() = 0;
46:     virtual void CloseAudioChannel() = 0;
47:     virtual bool IsAudioChannelOpened() const = 0;
48:     virtual void SendAudio(const std::vector<uint8_t>& data) = 0;
49:     virtual void SendWakeWordDetected(const std::string& wake_word);
50:     virtual void SendStartListening(ListeningMode mode);
51:     virtual void SendStopListening();
```

## protocol.h | 文件开头/全局定义 | 原文件第52-59行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.h
以下为原始源码，不是截图OCR。
```
52:     virtual void SendAbortSpeaking(AbortReason reason);
53:     virtual void SendIotDescriptors(const std::string& descriptors);
54:     virtual void SendIotStates(const std::string& states);
55: 
56: protected:
57:     std::function<void(const cJSON* root)> on_incoming_json_;
58:     std::function<void(std::vector<uint8_t>&& data)> on_incoming_audio_;
59:     std::function<void()> on_audio_channel_opened_;
```

## protocol.h | 文件开头/全局定义 | 原文件第60-68行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.h
以下为原始源码，不是截图OCR。
```
60:     std::function<void()> on_audio_channel_closed_;
61:     std::function<void(const std::string& message)> on_network_error_;
62: 
63:     int server_sample_rate_ = 16000;
64:     bool error_occurred_ = false;
65:     std::string session_id_;
66:     std::chrono::time_point<std::chrono::steady_clock> last_incoming_time_;
67: 
68:     virtual void SendText(const std::string& text) = 0;
```

## protocol.h | 文件开头/全局定义 | 原文件第69-74行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/protocol.h
以下为原始源码，不是截图OCR。
```
69:     virtual void SetError(const std::string& message);
70:     virtual bool IsTimeout() const;
71: };
72: 
73: #endif // PROTOCOL_H
74: 
```

## websocket_protocol.cc | 文件开头/全局定义 | 原文件第1-18行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/websocket_protocol.cc
以下为原始源码，不是截图OCR。
```
1: #include "websocket_protocol.h"
2: #include "board.h"
3: #include "system_info.h"
4: #include "application.h"
5: 
6: #include <cstring>
7: #include <cJSON.h>
8: #include <esp_log.h>
9: #include <arpa/inet.h>
10: #include "assets/lang_config.h"
11: 
12: #define TAG "WS"
13: 
14: WebsocketProtocol::WebsocketProtocol() {
15:     event_group_handle_ = xEventGroupCreate();
16: }
17: 
18: WebsocketProtocol::~WebsocketProtocol() {
```

## websocket_protocol.cc | 文件开头/全局定义 | 原文件第19-24行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/websocket_protocol.cc
以下为原始源码，不是截图OCR。
```
19:     if (websocket_ != nullptr) {
20:         delete websocket_;
21:     }
22:     vEventGroupDelete(event_group_handle_);
23: }
24: 
```

## websocket_protocol.cc | WebsocketProtocol::Start | 原文件第25-27行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/websocket_protocol.cc
以下为原始源码，不是截图OCR。
```
25: void WebsocketProtocol::Start() {
26: }
27: 
```

## websocket_protocol.cc | WebsocketProtocol::SendAudio | 原文件第28-35行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/websocket_protocol.cc
以下为原始源码，不是截图OCR。
```
28: void WebsocketProtocol::SendAudio(const std::vector<uint8_t>& data) {
29:     if (websocket_ == nullptr) {
30:         return;
31:     }
32: 
33:     websocket_->Send(data.data(), data.size(), true);
34: }
35: 
```

## websocket_protocol.cc | WebsocketProtocol::SendText | 原文件第36-47行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/websocket_protocol.cc
以下为原始源码，不是截图OCR。
```
36: void WebsocketProtocol::SendText(const std::string& text) {
37:     if (websocket_ == nullptr) {
38:         return;
39:     }
40: 
41:     if (!websocket_->Send(text)) {
42:         ESP_LOGE(TAG, "Failed to send text: %s", text.c_str());
43:         SetError(Lang::Strings::SERVER_ERROR);
44:     }
45: }
46: 
47: bool WebsocketProtocol::IsAudioChannelOpened() const {
```

## websocket_protocol.cc | WebsocketProtocol::SendText | 原文件第48-50行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/websocket_protocol.cc
以下为原始源码，不是截图OCR。
```
48:     return websocket_ != nullptr && websocket_->IsConnected() && !error_occurred_ && !IsTimeout();
49: }
50: 
```

## websocket_protocol.cc | WebsocketProtocol::CloseAudioChannel | 原文件第51-57行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/websocket_protocol.cc
以下为原始源码，不是截图OCR。
```
51: void WebsocketProtocol::CloseAudioChannel() {
52:     if (websocket_ != nullptr) {
53:         delete websocket_;
54:         websocket_ = nullptr;
55:     }
56: }
57: 
```

## websocket_protocol.cc | WebsocketProtocol::OpenAudioChannel | 原文件第58-67行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/websocket_protocol.cc
以下为原始源码，不是截图OCR。
```
58: bool WebsocketProtocol::OpenAudioChannel() {
59:     if (websocket_ != nullptr) {
60:         delete websocket_;
61:     }
62: 
63:     error_occurred_ = false;
64:     std::string url = CONFIG_WEBSOCKET_URL;
65:     std::string token = "Bearer " + std::string(CONFIG_WEBSOCKET_ACCESS_TOKEN);
66:     websocket_ = Board::GetInstance().CreateWebSocket();
67:     websocket_->SetHeader("Authorization", token.c_str());
```

## websocket_protocol.cc | WebsocketProtocol::OpenAudioChannel | 原文件第68-74行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/websocket_protocol.cc
以下为原始源码，不是截图OCR。
```
68:     websocket_->SetHeader("Protocol-Version", "1");
69:     websocket_->SetHeader("Device-Id", SystemInfo::GetMacAddress().c_str());
70:     websocket_->SetHeader("Client-Id", Board::GetInstance().GetUuid().c_str());
71: 
72:     websocket_->OnData([this](const char* data, size_t len, bool binary) {
73:         if (binary) {
74:             if (on_incoming_audio_ != nullptr) {
```

## websocket_protocol.cc | WebsocketProtocol::OpenAudioChannel | 原文件第75-83行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/websocket_protocol.cc
以下为原始源码，不是截图OCR。
```
75:                 on_incoming_audio_(std::vector<uint8_t>((uint8_t*)data, (uint8_t*)data + len));
76:             }
77:         } else {
78:             // Parse JSON data
79:             auto root = cJSON_Parse(data);
80:             auto type = cJSON_GetObjectItem(root, "type");
81:             if (type != NULL) {
82:                 if (strcmp(type->valuestring, "hello") == 0) {
83:                     ParseServerHello(root);
```

## websocket_protocol.cc | WebsocketProtocol::OpenAudioChannel | 原文件第84-95行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/websocket_protocol.cc
以下为原始源码，不是截图OCR。
```
84:                 } else {
85:                     if (on_incoming_json_ != nullptr) {
86:                         on_incoming_json_(root);
87:                     }
88:                 }
89:             } else {
90:                 ESP_LOGE(TAG, "Missing message type, data: %s", data);
91:             }
92:             cJSON_Delete(root);
93:         }
94:         last_incoming_time_ = std::chrono::steady_clock::now();
95:     });
```

## websocket_protocol.cc | WebsocketProtocol::OpenAudioChannel | 原文件第96-107行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/websocket_protocol.cc
以下为原始源码，不是截图OCR。
```
96: 
97:     websocket_->OnDisconnected([this]() {
98:         ESP_LOGI(TAG, "Websocket disconnected");
99:         if (on_audio_channel_closed_ != nullptr) {
100:             on_audio_channel_closed_();
101:         }
102:     });
103: 
104:     if (!websocket_->Connect(url.c_str())) {
105:         ESP_LOGE(TAG, "Failed to connect to websocket server");
106:         SetError(Lang::Strings::SERVER_NOT_FOUND);
107:         return false;
```

## websocket_protocol.cc | WebsocketProtocol::OpenAudioChannel | 原文件第108-116行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/websocket_protocol.cc
以下为原始源码，不是截图OCR。
```
108:     }
109: 
110:     // Send hello message to describe the client
111:     // keys: message type, version, audio_params (format, sample_rate, channels)
112:     std::string message = "{";
113:     message += "\"type\":\"hello\",";
114:     message += "\"version\": 1,";
115:     message += "\"transport\":\"websocket\",";
116:     message += "\"audio_params\":{";
```

## websocket_protocol.cc | WebsocketProtocol::OpenAudioChannel | 原文件第117-122行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/websocket_protocol.cc
以下为原始源码，不是截图OCR。
```
117:     message += "\"format\":\"opus\", \"sample_rate\":16000, \"channels\":1, \"frame_duration\":" + std::to_string(OPUS_FRAME_DURATION_MS);
118:     message += "}}";
119:     websocket_->Send(message);
120: 
121:     // Wait for server hello
122:     EventBits_t bits = xEventGroupWaitBits(event_group_handle_, WEBSOCKET_PROTOCOL_SERVER_HELLO_EVENT, pdTRUE, pdFALSE, pdMS_TO_TICKS(10000));
```

## websocket_protocol.cc | WebsocketProtocol::OpenAudioChannel | 原文件第123-135行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/websocket_protocol.cc
以下为原始源码，不是截图OCR。
```
123:     if (!(bits & WEBSOCKET_PROTOCOL_SERVER_HELLO_EVENT)) {
124:         ESP_LOGE(TAG, "Failed to receive server hello");
125:         SetError(Lang::Strings::SERVER_TIMEOUT);
126:         return false;
127:     }
128: 
129:     if (on_audio_channel_opened_ != nullptr) {
130:         on_audio_channel_opened_();
131:     }
132: 
133:     return true;
134: }
135: 
```

## websocket_protocol.cc | WebsocketProtocol::ParseServerHello | 原文件第136-143行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/websocket_protocol.cc
以下为原始源码，不是截图OCR。
```
136: void WebsocketProtocol::ParseServerHello(const cJSON* root) {
137:     auto transport = cJSON_GetObjectItem(root, "transport");
138:     if (transport == nullptr || strcmp(transport->valuestring, "websocket") != 0) {
139:         ESP_LOGE(TAG, "Unsupported transport: %s", transport->valuestring);
140:         return;
141:     }
142: 
143:     auto audio_params = cJSON_GetObjectItem(root, "audio_params");
```

## websocket_protocol.cc | WebsocketProtocol::ParseServerHello | 原文件第144-152行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/websocket_protocol.cc
以下为原始源码，不是截图OCR。
```
144:     if (audio_params != NULL) {
145:         auto sample_rate = cJSON_GetObjectItem(audio_params, "sample_rate");
146:         if (sample_rate != NULL) {
147:             server_sample_rate_ = sample_rate->valueint;
148:         }
149:     }
150: 
151:     xEventGroupSetBits(event_group_handle_, WEBSOCKET_PROTOCOL_SERVER_HELLO_EVENT);
152: }
```

## websocket_protocol.h | 文件开头/全局定义 | 原文件第1-18行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/websocket_protocol.h
以下为原始源码，不是截图OCR。
```
1: #ifndef _WEBSOCKET_PROTOCOL_H_
2: #define _WEBSOCKET_PROTOCOL_H_
3: 
4: 
5: #include "protocol.h"
6: 
7: #include <web_socket.h>
8: #include <freertos/FreeRTOS.h>
9: #include <freertos/event_groups.h>
10: 
11: #define WEBSOCKET_PROTOCOL_SERVER_HELLO_EVENT (1 << 0)
12: 
13: class WebsocketProtocol : public Protocol {
14: public:
15:     WebsocketProtocol();
16:     ~WebsocketProtocol();
17: 
18:     void Start() override;
```

## websocket_protocol.h | 文件开头/全局定义 | 原文件第19-31行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/websocket_protocol.h
以下为原始源码，不是截图OCR。
```
19:     void SendAudio(const std::vector<uint8_t>& data) override;
20:     bool OpenAudioChannel() override;
21:     void CloseAudioChannel() override;
22:     bool IsAudioChannelOpened() const override;
23: 
24: private:
25:     EventGroupHandle_t event_group_handle_;
26:     WebSocket* websocket_ = nullptr;
27: 
28:     void ParseServerHello(const cJSON* root);
29:     void SendText(const std::string& text) override;
30: };
31: 
```

## websocket_protocol.h | 文件开头/全局定义 | 原文件第32-32行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/protocols/websocket_protocol.h
以下为原始源码，不是截图OCR。
```
32: #endif
```

## settings.cc | 文件开头/全局定义 | 原文件第1-14行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/settings.cc
以下为原始源码，不是截图OCR。
```
1: #include "settings.h"
2: 
3: #include <esp_log.h>
4: #include <nvs_flash.h>
5: 
6: #define TAG "Settings"
7: 
8: Settings::Settings(const std::string& ns, bool read_write) : ns_(ns), read_write_(read_write) {
9:     nvs_open(ns.c_str(), read_write_ ? NVS_READWRITE : NVS_READONLY, &nvs_handle_);
10: }
11: 
12: Settings::~Settings() {
13:     if (nvs_handle_ != 0) {
14:         if (read_write_ && dirty_) {
```

## settings.cc | 文件开头/全局定义 | 原文件第15-20行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/settings.cc
以下为原始源码，不是截图OCR。
```
15:             ESP_ERROR_CHECK(nvs_commit(nvs_handle_));
16:         }
17:         nvs_close(nvs_handle_);
18:     }
19: }
20: 
```

## settings.cc | Settings::GetString | 原文件第21-32行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/settings.cc
以下为原始源码，不是截图OCR。
```
21: std::string Settings::GetString(const std::string& key, const std::string& default_value) {
22:     if (nvs_handle_ == 0) {
23:         return default_value;
24:     }
25: 
26:     size_t length = 0;
27:     if (nvs_get_str(nvs_handle_, key.c_str(), nullptr, &length) != ESP_OK) {
28:         return default_value;
29:     }
30: 
31:     std::string value;
32:     value.resize(length);
```

## settings.cc | Settings::GetString | 原文件第33-39行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/settings.cc
以下为原始源码，不是截图OCR。
```
33:     ESP_ERROR_CHECK(nvs_get_str(nvs_handle_, key.c_str(), value.data(), &length));
34:     while (!value.empty() && value.back() == '\0') {
35:         value.pop_back();
36:     }
37:     return value;
38: }
39: 
```

## settings.cc | Settings::SetString | 原文件第40-48行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/settings.cc
以下为原始源码，不是截图OCR。
```
40: void Settings::SetString(const std::string& key, const std::string& value) {
41:     if (read_write_) {
42:         ESP_ERROR_CHECK(nvs_set_str(nvs_handle_, key.c_str(), value.c_str()));
43:         dirty_ = true;
44:     } else {
45:         ESP_LOGW(TAG, "Namespace %s is not open for writing", ns_.c_str());
46:     }
47: }
48: 
```

## settings.cc | Settings::GetInt | 原文件第49-60行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/settings.cc
以下为原始源码，不是截图OCR。
```
49: int32_t Settings::GetInt(const std::string& key, int32_t default_value) {
50:     if (nvs_handle_ == 0) {
51:         return default_value;
52:     }
53: 
54:     int32_t value;
55:     if (nvs_get_i32(nvs_handle_, key.c_str(), &value) != ESP_OK) {
56:         return default_value;
57:     }
58:     return value;
59: }
60: 
```

## settings.cc | Settings::SetInt | 原文件第61-69行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/settings.cc
以下为原始源码，不是截图OCR。
```
61: void Settings::SetInt(const std::string& key, int32_t value) {
62:     if (read_write_) {
63:         ESP_ERROR_CHECK(nvs_set_i32(nvs_handle_, key.c_str(), value));
64:         dirty_ = true;
65:     } else {
66:         ESP_LOGW(TAG, "Namespace %s is not open for writing", ns_.c_str());
67:     }
68: }
69: 
```

## settings.cc | Settings::EraseKey | 原文件第70-80行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/settings.cc
以下为原始源码，不是截图OCR。
```
70: void Settings::EraseKey(const std::string& key) {
71:     if (read_write_) {
72:         auto ret = nvs_erase_key(nvs_handle_, key.c_str());
73:         if (ret != ESP_ERR_NVS_NOT_FOUND) {
74:             ESP_ERROR_CHECK(ret);
75:         }
76:     } else {
77:         ESP_LOGW(TAG, "Namespace %s is not open for writing", ns_.c_str());
78:     }
79: }
80: 
```

## settings.cc | Settings::EraseAll | 原文件第81-87行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/settings.cc
以下为原始源码，不是截图OCR。
```
81: void Settings::EraseAll() {
82:     if (read_write_) {
83:         ESP_ERROR_CHECK(nvs_erase_all(nvs_handle_));
84:     } else {
85:         ESP_LOGW(TAG, "Namespace %s is not open for writing", ns_.c_str());
86:     }
87: }
```

## settings.h | 文件开头/全局定义 | 原文件第1-13行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/settings.h
以下为原始源码，不是截图OCR。
```
1: #ifndef SETTINGS_H
2: #define SETTINGS_H
3: 
4: #include <string>
5: #include <nvs_flash.h>
6: 
7: class Settings {
8: public:
9:     Settings(const std::string& ns, bool read_write = false);
10:     ~Settings();
11: 
12:     std::string GetString(const std::string& key, const std::string& default_value = "");
13:     void SetString(const std::string& key, const std::string& value);
```

## settings.h | 文件开头/全局定义 | 原文件第14-26行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/settings.h
以下为原始源码，不是截图OCR。
```
14:     int32_t GetInt(const std::string& key, int32_t default_value = 0);
15:     void SetInt(const std::string& key, int32_t value);
16:     void EraseKey(const std::string& key);
17:     void EraseAll();
18: 
19: private:
20:     std::string ns_;
21:     nvs_handle_t nvs_handle_ = 0;
22:     bool read_write_ = false;
23:     bool dirty_ = false;
24: };
25: 
26: #endif
```

## system_info.cc | 文件开头/全局定义 | 原文件第1-14行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/system_info.cc
以下为原始源码，不是截图OCR。
```
1: #include "system_info.h"
2: 
3: #include <freertos/task.h>
4: #include <esp_log.h>
5: #include <esp_flash.h>
6: #include <esp_mac.h>
7: #include <esp_system.h>
8: #include <esp_partition.h>
9: #include <esp_app_desc.h>
10: #include <esp_ota_ops.h>
11: 
12: 
13: #define TAG "SystemInfo"
14: 
```

## system_info.cc | SystemInfo::GetFlashSize | 原文件第15-23行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/system_info.cc
以下为原始源码，不是截图OCR。
```
15: size_t SystemInfo::GetFlashSize() {
16:     uint32_t flash_size;
17:     if (esp_flash_get_size(NULL, &flash_size) != ESP_OK) {
18:         ESP_LOGE(TAG, "Failed to get flash size");
19:         return 0;
20:     }
21:     return (size_t)flash_size;
22: }
23: 
```

## system_info.cc | SystemInfo::GetMinimumFreeHeapSize | 原文件第24-27行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/system_info.cc
以下为原始源码，不是截图OCR。
```
24: size_t SystemInfo::GetMinimumFreeHeapSize() {
25:     return esp_get_minimum_free_heap_size();
26: }
27: 
```

## system_info.cc | SystemInfo::GetFreeHeapSize | 原文件第28-31行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/system_info.cc
以下为原始源码，不是截图OCR。
```
28: size_t SystemInfo::GetFreeHeapSize() {
29:     return esp_get_free_heap_size();
30: }
31: 
```

## system_info.cc | SystemInfo::GetMacAddress | 原文件第32-39行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/system_info.cc
以下为原始源码，不是截图OCR。
```
32: std::string SystemInfo::GetMacAddress() {
33:     uint8_t mac[6];
34:     esp_read_mac(mac, ESP_MAC_WIFI_STA);
35:     char mac_str[18];
36:     snprintf(mac_str, sizeof(mac_str), "%02x:%02x:%02x:%02x:%02x:%02x", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
37:     return std::string(mac_str);
38: }
39: 
```

## system_info.cc | SystemInfo::GetChipModelName | 原文件第40-43行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/system_info.cc
以下为原始源码，不是截图OCR。
```
40: std::string SystemInfo::GetChipModelName() {
41:     return std::string(CONFIG_IDF_TARGET);
42: }
43: 
```

## system_info.cc | SystemInfo::PrintRealTimeStats | 原文件第44-52行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/system_info.cc
以下为原始源码，不是截图OCR。
```
44: esp_err_t SystemInfo::PrintRealTimeStats(TickType_t xTicksToWait) {
45:     #define ARRAY_SIZE_OFFSET 5
46:     TaskStatus_t *start_array = NULL, *end_array = NULL;
47:     UBaseType_t start_array_size, end_array_size;
48:     configRUN_TIME_COUNTER_TYPE start_run_time, end_run_time;
49:     esp_err_t ret;
50:     uint32_t total_elapsed_time;
51: 
52:     //Allocate array to store current task states
```

## system_info.cc | SystemInfo::PrintRealTimeStats | 原文件第53-61行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/system_info.cc
以下为原始源码，不是截图OCR。
```
53:     start_array_size = uxTaskGetNumberOfTasks() + ARRAY_SIZE_OFFSET;
54:     start_array = (TaskStatus_t*)malloc(sizeof(TaskStatus_t) * start_array_size);
55:     if (start_array == NULL) {
56:         ret = ESP_ERR_NO_MEM;
57:         goto exit;
58:     }
59:     //Get current task states
60:     start_array_size = uxTaskGetSystemState(start_array, start_array_size, &start_run_time);
61:     if (start_array_size == 0) {
```

## system_info.cc | SystemInfo::PrintRealTimeStats | 原文件第62-74行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/system_info.cc
以下为原始源码，不是截图OCR。
```
62:         ret = ESP_ERR_INVALID_SIZE;
63:         goto exit;
64:     }
65: 
66:     vTaskDelay(xTicksToWait);
67: 
68:     //Allocate array to store tasks states post delay
69:     end_array_size = uxTaskGetNumberOfTasks() + ARRAY_SIZE_OFFSET;
70:     end_array = (TaskStatus_t*)malloc(sizeof(TaskStatus_t) * end_array_size);
71:     if (end_array == NULL) {
72:         ret = ESP_ERR_NO_MEM;
73:         goto exit;
74:     }
```

## system_info.cc | SystemInfo::PrintRealTimeStats | 原文件第75-84行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/system_info.cc
以下为原始源码，不是截图OCR。
```
75:     //Get post delay task states
76:     end_array_size = uxTaskGetSystemState(end_array, end_array_size, &end_run_time);
77:     if (end_array_size == 0) {
78:         ret = ESP_ERR_INVALID_SIZE;
79:         goto exit;
80:     }
81: 
82:     //Calculate total_elapsed_time in units of run time stats clock period.
83:     total_elapsed_time = (end_run_time - start_run_time);
84:     if (total_elapsed_time == 0) {
```

## system_info.cc | SystemInfo::PrintRealTimeStats | 原文件第85-95行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/system_info.cc
以下为原始源码，不是截图OCR。
```
85:         ret = ESP_ERR_INVALID_STATE;
86:         goto exit;
87:     }
88: 
89:     printf("| Task | Run Time | Percentage\n");
90:     //Match each task in start_array to those in the end_array
91:     for (int i = 0; i < start_array_size; i++) {
92:         int k = -1;
93:         for (int j = 0; j < end_array_size; j++) {
94:             if (start_array[i].xHandle == end_array[j].xHandle) {
95:                 k = j;
```

## system_info.cc | SystemInfo::PrintRealTimeStats | 原文件第96-104行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/system_info.cc
以下为原始源码，不是截图OCR。
```
96:                 //Mark that task have been matched by overwriting their handles
97:                 start_array[i].xHandle = NULL;
98:                 end_array[j].xHandle = NULL;
99:                 break;
100:             }
101:         }
102:         //Check if matching task found
103:         if (k >= 0) {
104:             uint32_t task_elapsed_time = end_array[k].ulRunTimeCounter - start_array[i].ulRunTimeCounter;
```

## system_info.cc | SystemInfo::PrintRealTimeStats | 原文件第105-112行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/system_info.cc
以下为原始源码，不是截图OCR。
```
105:             uint32_t percentage_time = (task_elapsed_time * 100UL) / (total_elapsed_time * CONFIG_FREERTOS_NUMBER_OF_CORES);
106:             printf("| %-16s | %8lu | %4lu%%\n", start_array[i].pcTaskName, task_elapsed_time, percentage_time);
107:         }
108:     }
109: 
110:     //Print unmatched tasks
111:     for (int i = 0; i < start_array_size; i++) {
112:         if (start_array[i].xHandle != NULL) {
```

## system_info.cc | SystemInfo::PrintRealTimeStats | 原文件第113-126行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/system_info.cc
以下为原始源码，不是截图OCR。
```
113:             printf("| %s | Deleted\n", start_array[i].pcTaskName);
114:         }
115:     }
116:     for (int i = 0; i < end_array_size; i++) {
117:         if (end_array[i].xHandle != NULL) {
118:             printf("| %s | Created\n", end_array[i].pcTaskName);
119:         }
120:     }
121:     ret = ESP_OK;
122: 
123: exit:    //Common return path
124:     free(start_array);
125:     free(end_array);
126:     return ret;
```

## system_info.cc | SystemInfo::PrintRealTimeStats | 原文件第127-128行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/system_info.cc
以下为原始源码，不是截图OCR。
```
127: }
128: 
```

## system_info.h | 文件开头/全局定义 | 原文件第1-15行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/system_info.h
以下为原始源码，不是截图OCR。
```
1: #ifndef _SYSTEM_INFO_H_
2: #define _SYSTEM_INFO_H_
3: 
4: #include <string>
5: 
6: #include <esp_err.h>
7: #include <freertos/FreeRTOS.h>
8: 
9: class SystemInfo {
10: public:
11:     static size_t GetFlashSize();
12:     static size_t GetMinimumFreeHeapSize();
13:     static size_t GetFreeHeapSize();
14:     static std::string GetMacAddress();
15:     static std::string GetChipModelName();
```

## system_info.h | 文件开头/全局定义 | 原文件第16-19行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/main/system_info.h
以下为原始源码，不是截图OCR。
```
16:     static esp_err_t PrintRealTimeStats(TickType_t xTicksToWait);
17: };
18: 
19: #endif // _SYSTEM_INFO_H_
```

## gen_lang.py | 文件开头/全局定义 | 原文件第1-21行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/gen_lang.py
以下为原始源码，不是截图OCR。
```
1: #!/usr/bin/env python3
2: import argparse
3: import json
4: import os
5: 
6: HEADER_TEMPLATE = """// Auto-generated language config
7: #pragma once
8: 
9: #include <string_view>
10: 
11: #ifndef {lang_code_for_font}
12:     #define {lang_code_for_font}  // 預設語言
13: #endif
14: 
15: namespace Lang {{
16:     // 语言元数据
17:     constexpr const char* CODE = "{lang_code}";
18: 
19:     // 字符串资源
20:     namespace Strings {{
21: {strings}
```

## gen_lang.py | 文件开头/全局定义 | 原文件第22-30行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/gen_lang.py
以下为原始源码，不是截图OCR。
```
22:     }}
23: 
24:     // 音效资源
25:     namespace Sounds {{
26: {sounds}
27:     }}
28: }}
29: """
30: 
```

## gen_lang.py | generate_header | 原文件第31-36行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/gen_lang.py
以下为原始源码，不是截图OCR。
```
31: def generate_header(input_path, output_path):
32:     with open(input_path, 'r', encoding='utf-8') as f:
33:         data = json.load(f)
34: 
35:     # 验证数据结构
36:     if 'language' not in data or 'strings' not in data:
```

## gen_lang.py | ValueError | 原文件第37-49行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/gen_lang.py
以下为原始源码，不是截图OCR。
```
37:         raise ValueError("Invalid JSON structure")
38: 
39:     lang_code = data['language']['type']
40: 
41:     # 生成字符串常量
42:     strings = []
43:     sounds = []
44:     for key, value in data['strings'].items():
45:         value = value.replace('"', '\\"')
46:         strings.append(f'        constexpr const char* {key.upper()} = "{value}";')
47: 
48:     # 生成音效常量
49:     for file in os.listdir(os.path.dirname(input_path)):
```

## gen_lang.py | ValueError | 原文件第50-56行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/gen_lang.py
以下为原始源码，不是截图OCR。
```
50:         if file.endswith('.p3'):
51:             base_name = os.path.splitext(file)[0]
52:             sounds.append(f'''
53:         extern const char p3_{base_name}_start[] asm("_binary_{base_name}_p3_start");
54:         extern const char p3_{base_name}_end[] asm("_binary_{base_name}_p3_end");
55:         static const std::string_view P3_{base_name.upper()} {{
56:         static_cast<const char*>(p3_{base_name}_start),
```

## gen_lang.py | ValueError | 原文件第57-65行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/gen_lang.py
以下为原始源码，不是截图OCR。
```
57:         static_cast<size_t>(p3_{base_name}_end - p3_{base_name}_start)
58:         }};''')
59:     
60:     # 生成公共音效
61:     for file in os.listdir(os.path.join(os.path.dirname(output_path), 'common')):
62:         if file.endswith('.p3'):
63:             base_name = os.path.splitext(file)[0]
64:             sounds.append(f'''
65:         extern const char p3_{base_name}_start[] asm("_binary_{base_name}_p3_start");
```

## gen_lang.py | ValueError | 原文件第66-74行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/gen_lang.py
以下为原始源码，不是截图OCR。
```
66:         extern const char p3_{base_name}_end[] asm("_binary_{base_name}_p3_end");
67:         static const std::string_view P3_{base_name.upper()} {{
68:         static_cast<const char*>(p3_{base_name}_start),
69:         static_cast<size_t>(p3_{base_name}_end - p3_{base_name}_start)
70:         }};''')
71: 
72:     # 填充模板
73:     content = HEADER_TEMPLATE.format(
74:         lang_code=lang_code,
```

## gen_lang.py | ValueError | 原文件第75-86行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/gen_lang.py
以下为原始源码，不是截图OCR。
```
75:         lang_code_for_font=lang_code.replace('-', '_').lower(),
76:         strings="\n".join(sorted(strings)),
77:         sounds="\n".join(sorted(sounds))
78:     )
79: 
80:     # 写入文件
81:     os.makedirs(os.path.dirname(output_path), exist_ok=True)
82:     with open(output_path, 'w', encoding='utf-8') as f:
83:         f.write(content)
84: 
85: if __name__ == "__main__":
86:     parser = argparse.ArgumentParser()
```

## gen_lang.py | ValueError | 原文件第87-91行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/gen_lang.py
以下为原始源码，不是截图OCR。
```
87:     parser.add_argument("--input", required=True, help="输入JSON文件路径")
88:     parser.add_argument("--output", required=True, help="输出头文件路径")
89:     args = parser.parse_args()
90: 
91:     generate_header(args.input, args.output)
```

## batch_convert_gui.py | 文件开头/全局定义 | 原文件第1-9行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
1: import tkinter as tk
2: from tkinter import ttk, filedialog, messagebox
3: import os
4: import threading
5: import sys
6: from convert_audio_to_p3 import encode_audio_to_opus
7: from convert_p3_to_audio import decode_p3_to_audio
8: 
9: class AudioConverterApp:
```

## batch_convert_gui.py | __init__ | 原文件第10-19行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
10:     def __init__(self, master):
11:         self.master = master
12:         master.title("音频/P3 批量转换工具")
13:         master.geometry("680x600")  # 调整窗口高度
14: 
15:         # 初始化变量
16:         self.mode = tk.StringVar(value="audio_to_p3")
17:         self.output_dir = tk.StringVar()
18:         self.output_dir.set(os.path.abspath("output"))
19:         self.enable_loudnorm = tk.BooleanVar(value=True)
```

## batch_convert_gui.py | __init__ | 原文件第20-25行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
20:         self.target_lufs = tk.DoubleVar(value=-16.0)
21: 
22:         # 创建UI组件
23:         self.create_widgets()
24:         self.redirect_output()
25: 
```

## batch_convert_gui.py | create_widgets | 原文件第26-33行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
26:     def create_widgets(self):
27:         # 模式选择
28:         mode_frame = ttk.LabelFrame(self.master, text="转换模式")
29:         mode_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
30:         
31:         ttk.Radiobutton(mode_frame, text="音频转P3", variable=self.mode,
32:                         value="audio_to_p3", command=self.toggle_settings,
33:                         width=12).grid(row=0, column=0, padx=5)
```

## batch_convert_gui.py | create_widgets | 原文件第34-41行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
34:         ttk.Radiobutton(mode_frame, text="P3转音频", variable=self.mode,
35:                         value="p3_to_audio", command=self.toggle_settings,
36:                         width=12).grid(row=0, column=1, padx=5)
37: 
38:         # 响度设置
39:         self.loudnorm_frame = ttk.Frame(self.master)
40:         self.loudnorm_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
41:         
```

## batch_convert_gui.py | create_widgets | 原文件第42-49行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
42:         ttk.Checkbutton(self.loudnorm_frame, text="启用响度调整", 
43:                        variable=self.enable_loudnorm, width=15
44:                        ).grid(row=0, column=0, padx=2)
45:         ttk.Entry(self.loudnorm_frame, textvariable=self.target_lufs, 
46:                  width=6).grid(row=0, column=1, padx=2)
47:         ttk.Label(self.loudnorm_frame, text="LUFS").grid(row=0, column=2, padx=2)
48: 
49:         # 文件选择
```

## batch_convert_gui.py | create_widgets | 原文件第50-56行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
50:         file_frame = ttk.LabelFrame(self.master, text="输入文件")
51:         file_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
52:         
53:         # 文件操作按钮
54:         ttk.Button(file_frame, text="选择文件", command=self.select_files,
55:                   width=12).grid(row=0, column=0, padx=5, pady=2)
56:         ttk.Button(file_frame, text="移除选中", command=self.remove_selected,
```

## batch_convert_gui.py | create_widgets | 原文件第57-63行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
57:                   width=12).grid(row=0, column=1, padx=5, pady=2)
58:         ttk.Button(file_frame, text="清空列表", command=self.clear_files,
59:                   width=12).grid(row=0, column=2, padx=5, pady=2)
60: 
61:         # 文件列表（使用Treeview）
62:         self.tree = ttk.Treeview(file_frame, columns=("selected", "filename"), 
63:                                show="headings", height=8)
```

## batch_convert_gui.py | create_widgets | 原文件第64-70行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
64:         self.tree.heading("selected", text="选中", anchor=tk.W)
65:         self.tree.heading("filename", text="文件名", anchor=tk.W)
66:         self.tree.column("selected", width=60, anchor=tk.W)
67:         self.tree.column("filename", width=600, anchor=tk.W)
68:         self.tree.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=5, pady=2)
69:         self.tree.bind("<ButtonRelease-1>", self.on_tree_click)
70: 
```

## batch_convert_gui.py | create_widgets | 原文件第71-77行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
71:         # 输出目录
72:         output_frame = ttk.LabelFrame(self.master, text="输出目录")
73:         output_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
74:         
75:         ttk.Entry(output_frame, textvariable=self.output_dir, width=60
76:                  ).grid(row=0, column=0, padx=5, sticky="ew")
77:         ttk.Button(output_frame, text="浏览", command=self.select_output_dir,
```

## batch_convert_gui.py | create_widgets | 原文件第78-85行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
78:                   width=8).grid(row=0, column=1, padx=5)
79: 
80:         # 转换按钮区域
81:         button_frame = ttk.Frame(self.master)
82:         button_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
83:         
84:         ttk.Button(button_frame, text="转换全部文件", command=lambda: self.start_conversion(True),
85:                   width=15).pack(side=tk.LEFT, padx=5)
```

## batch_convert_gui.py | create_widgets | 原文件第86-93行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
86:         ttk.Button(button_frame, text="转换选中文件", command=lambda: self.start_conversion(False),
87:                   width=15).pack(side=tk.LEFT, padx=5)
88: 
89:         # 日志区域
90:         log_frame = ttk.LabelFrame(self.master, text="日志")
91:         log_frame.grid(row=5, column=0, padx=10, pady=5, sticky="nsew")
92:         
93:         self.log_text = tk.Text(log_frame, height=14, width=80)
```

## batch_convert_gui.py | create_widgets | 原文件第94-102行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
94:         self.log_text.pack(fill=tk.BOTH, expand=True)
95: 
96:         # 配置布局权重
97:         self.master.columnconfigure(0, weight=1)
98:         self.master.rowconfigure(2, weight=1)
99:         self.master.rowconfigure(5, weight=3)
100:         file_frame.columnconfigure(0, weight=1)
101:         file_frame.rowconfigure(1, weight=1)
102: 
```

## batch_convert_gui.py | toggle_settings | 原文件第103-108行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
103:     def toggle_settings(self):
104:         if self.mode.get() == "audio_to_p3":
105:             self.loudnorm_frame.grid()
106:         else:
107:             self.loudnorm_frame.grid_remove()
108: 
```

## batch_convert_gui.py | select_files | 原文件第109-118行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
109:     def select_files(self):
110:         file_types = [
111:             ("音频文件", "*.wav *.mp3 *.ogg *.flac") if self.mode.get() == "audio_to_p3" 
112:             else ("P3文件", "*.p3")
113:         ]
114:         
115:         files = filedialog.askopenfilenames(filetypes=file_types)
116:         for f in files:
117:             self.tree.insert("", tk.END, values=("[ ]", os.path.basename(f)), tags=(f,))
118: 
```

## batch_convert_gui.py | on_tree_click | 原文件第119-126行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
119:     def on_tree_click(self, event):
120:         """处理复选框点击事件"""
121:         region = self.tree.identify("region", event.x, event.y)
122:         if region == "cell":
123:             col = self.tree.identify_column(event.x)
124:             item = self.tree.identify_row(event.y)
125:             if col == "#1":  # 点击的是选中列
126:                 current_val = self.tree.item(item, "values")[0]
```

## batch_convert_gui.py | on_tree_click | 原文件第127-129行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
127:                 new_val = "[√]" if current_val == "[ ]" else "[ ]"
128:                 self.tree.item(item, values=(new_val, self.tree.item(item, "values")[1]))
129: 
```

## batch_convert_gui.py | remove_selected | 原文件第130-138行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
130:     def remove_selected(self):
131:         """移除选中的文件"""
132:         to_remove = []
133:         for item in self.tree.get_children():
134:             if self.tree.item(item, "values")[0] == "[√]":
135:                 to_remove.append(item)
136:         for item in reversed(to_remove):
137:             self.tree.delete(item)
138: 
```

## batch_convert_gui.py | clear_files | 原文件第139-143行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
139:     def clear_files(self):
140:         """清空所有文件"""
141:         for item in self.tree.get_children():
142:             self.tree.delete(item)
143: 
```

## batch_convert_gui.py | select_output_dir | 原文件第144-148行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
144:     def select_output_dir(self):
145:         path = filedialog.askdirectory()
146:         if path:
147:             self.output_dir.set(path)
148: 
```

## batch_convert_gui.py | redirect_output | 原文件第149-150行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
149:     def redirect_output(self):
150:         class StdoutRedirector:
```

## batch_convert_gui.py | __init__ | 原文件第151-154行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
151:             def __init__(self, text_widget):
152:                 self.text_widget = text_widget
153:                 self.original_stdout = sys.stdout
154: 
```

## batch_convert_gui.py | write | 原文件第155-159行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
155:             def write(self, message):
156:                 self.text_widget.insert(tk.END, message)
157:                 self.text_widget.see(tk.END)
158:                 self.original_stdout.write(message)
159: 
```

## batch_convert_gui.py | flush | 原文件第160-164行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
160:             def flush(self):
161:                 self.original_stdout.flush()
162: 
163:         sys.stdout = StdoutRedirector(self.log_text)
164: 
```

## batch_convert_gui.py | start_conversion | 原文件第165-173行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
165:     def start_conversion(self, convert_all):
166:         """开始转换"""
167:         input_files = []
168:         for item in self.tree.get_children():
169:             if convert_all or self.tree.item(item, "values")[0] == "[√]":
170:                 input_files.append(self.tree.item(item, "tags")[0])
171:         
172:         if not input_files:
173:             msg = "没有找到可转换的文件" if convert_all else "没有选中任何文件"
```

## batch_convert_gui.py | start_conversion | 原文件第174-181行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
174:             messagebox.showwarning("警告", msg)
175:             return
176:         
177:         os.makedirs(self.output_dir.get(), exist_ok=True)
178: 
179:         try:
180:             if self.mode.get() == "audio_to_p3":
181:                 target_lufs = self.target_lufs.get() if self.enable_loudnorm.get() else None
```

## batch_convert_gui.py | start_conversion | 原文件第182-189行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
182:                 thread = threading.Thread(target=self.convert_audio_to_p3, args=(target_lufs, input_files))
183:             else:
184:                 thread = threading.Thread(target=self.convert_p3_to_audio, args=(input_files,))
185:             
186:             thread.start()
187:         except Exception as e:
188:             print(f"转换初始化失败: {str(e)}")
189: 
```

## batch_convert_gui.py | convert_audio_to_p3 | 原文件第190-197行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
190:     def convert_audio_to_p3(self, target_lufs, input_files):
191:         """音频转P3转换逻辑"""
192:         for input_path in input_files:
193:             try:
194:                 filename = os.path.basename(input_path)
195:                 base_name = os.path.splitext(filename)[0]
196:                 output_path = os.path.join(self.output_dir.get(), f"{base_name}.p3")
197:                 
```

## batch_convert_gui.py | convert_audio_to_p3 | 原文件第198-203行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
198:                 print(f"正在转换: {filename}")
199:                 encode_audio_to_opus(input_path, output_path, target_lufs)
200:                 print(f"转换成功: {filename}\n")
201:             except Exception as e:
202:                 print(f"转换失败: {str(e)}\n")
203: 
```

## batch_convert_gui.py | convert_p3_to_audio | 原文件第204-212行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
204:     def convert_p3_to_audio(self, input_files):
205:         """P3转音频转换逻辑"""
206:         for input_path in input_files:
207:             try:
208:                 filename = os.path.basename(input_path)
209:                 base_name = os.path.splitext(filename)[0]
210:                 output_path = os.path.join(self.output_dir.get(), f"{base_name}.wav")
211:                 
212:                 print(f"正在转换: {filename}")
```

## batch_convert_gui.py | convert_p3_to_audio | 原文件第213-221行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/batch_convert_gui.py
以下为原始源码，不是截图OCR。
```
213:                 decode_p3_to_audio(input_path, output_path)
214:                 print(f"转换成功: {filename}\n")
215:             except Exception as e:
216:                 print(f"转换失败: {str(e)}\n")
217: 
218: if __name__ == "__main__":
219:     root = tk.Tk()
220:     app = AudioConverterApp(root)
221:     root.mainloop()
```

## convert_audio_to_p3.py | 文件开头/全局定义 | 原文件第1-10行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/convert_audio_to_p3.py
以下为原始源码，不是截图OCR。
```
1: # convert audio files to protocol v3 stream
2: import librosa
3: import opuslib
4: import struct
5: import sys
6: import tqdm
7: import numpy as np
8: import argparse
9: import pyloudnorm as pyln
10: 
```

## convert_audio_to_p3.py | encode_audio_to_opus | 原文件第11-19行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/convert_audio_to_p3.py
以下为原始源码，不是截图OCR。
```
11: def encode_audio_to_opus(input_file, output_file, target_lufs=None):
12:     # Load audio file using librosa
13:     audio, sample_rate = librosa.load(input_file, sr=None, mono=False, dtype=np.float32)
14:     
15:     # Convert to mono if stereo
16:     if audio.ndim == 2:
17:         audio = librosa.to_mono(audio)
18:     
19:     if target_lufs is not None:
```

## convert_audio_to_p3.py | encode_audio_to_opus | 原文件第20-23行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/convert_audio_to_p3.py
以下为原始源码，不是截图OCR。
```
20:         print("Note: Automatic loudness adjustment is enabled, which may cause", file=sys.stderr) 
21:         print("      audio distortion. If the input audio has already been ", file=sys.stderr)
22:         print("      loudness-adjusted or if the input audio is TTS audio, ", file=sys.stderr)
23:         print("      please use the `-d` parameter to disable loudness adjustment.", file=sys.stderr)
```

## convert_audio_to_p3.py | encode_audio_to_opus | 原文件第24-31行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/convert_audio_to_p3.py
以下为原始源码，不是截图OCR。
```
24:         meter = pyln.Meter(sample_rate)
25:         current_loudness = meter.integrated_loudness(audio)
26:         audio = pyln.normalize.loudness(audio, current_loudness, target_lufs)
27:         print(f"Adjusted loudness: {current_loudness:.1f} LUFS -> {target_lufs} LUFS")
28: 
29:     # Convert sample rate to 16000Hz if necessary
30:     target_sample_rate = 16000
31:     if sample_rate != target_sample_rate:
```

## convert_audio_to_p3.py | encode_audio_to_opus | 原文件第32-41行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/convert_audio_to_p3.py
以下为原始源码，不是截图OCR。
```
32:         audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=target_sample_rate)
33:         sample_rate = target_sample_rate
34:     
35:     # Convert audio data back to int16 after processing
36:     audio = (audio * 32767).astype(np.int16)
37:     
38:     # Initialize Opus encoder
39:     encoder = opuslib.Encoder(sample_rate, 1, opuslib.APPLICATION_AUDIO)
40: 
41:     # Encode and save
```

## convert_audio_to_p3.py | encode_audio_to_opus | 原文件第42-48行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/convert_audio_to_p3.py
以下为原始源码，不是截图OCR。
```
42:     with open(output_file, 'wb') as f:
43:         duration = 60  # 60ms per frame
44:         frame_size = int(sample_rate * duration / 1000)
45:         for i in tqdm.tqdm(range(0, len(audio) - frame_size, frame_size)):
46:             frame = audio[i:i + frame_size]
47:             opus_data = encoder.encode(frame.tobytes(), frame_size=frame_size)
48:             packet = struct.pack('>BBH', 0, 0, len(opus_data)) + opus_data
```

## convert_audio_to_p3.py | encode_audio_to_opus | 原文件第49-55行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/convert_audio_to_p3.py
以下为原始源码，不是截图OCR。
```
49:             f.write(packet)
50: 
51: if __name__ == "__main__":
52:     parser = argparse.ArgumentParser(description='Convert audio to Opus with loudness normalization')
53:     parser.add_argument('input_file', help='Input audio file')
54:     parser.add_argument('output_file', help='Output .opus file')
55:     parser.add_argument('-l', '--lufs', type=float, default=-16.0,
```

## convert_audio_to_p3.py | encode_audio_to_opus | 原文件第56-62行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/convert_audio_to_p3.py
以下为原始源码，不是截图OCR。
```
56:                        help='Target loudness in LUFS (default: -16)')
57:     parser.add_argument('-d', '--disable-loudnorm', action='store_true',
58:                        help='Disable loudness normalization')
59:     args = parser.parse_args()
60: 
61:     target_lufs = None if args.disable_loudnorm else args.lufs
62:     encode_audio_to_opus(args.input_file, args.output_file, target_lufs)
```

## convert_p3_to_audio.py | 文件开头/全局定义 | 原文件第1-8行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/convert_p3_to_audio.py
以下为原始源码，不是截图OCR。
```
1: import struct
2: import sys
3: import opuslib
4: import numpy as np
5: from tqdm import tqdm
6: import soundfile as sf
7: 
8: 
```

## convert_p3_to_audio.py | decode_p3_to_audio | 原文件第9-21行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/convert_p3_to_audio.py
以下为原始源码，不是截图OCR。
```
9: def decode_p3_to_audio(input_file, output_file):
10:     sample_rate = 16000
11:     channels = 1
12:     decoder = opuslib.Decoder(sample_rate, channels)
13: 
14:     pcm_frames = []
15:     frame_size = int(sample_rate * 60 / 1000)
16: 
17:     with open(input_file, "rb") as f:
18:         f.seek(0, 2)
19:         total_size = f.tell()
20:         f.seek(0)
21: 
```

## convert_p3_to_audio.py | decode_p3_to_audio | 原文件第22-30行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/convert_p3_to_audio.py
以下为原始源码，不是截图OCR。
```
22:         with tqdm(total=total_size, unit="B", unit_scale=True) as pbar:
23:             while True:
24:                 header = f.read(4)
25:                 if not header or len(header) < 4:
26:                     break
27: 
28:                 pkt_type, reserved, opus_len = struct.unpack(">BBH", header)
29:                 opus_data = f.read(opus_len)
30:                 if len(opus_data) != opus_len:
```

## convert_p3_to_audio.py | decode_p3_to_audio | 原文件第31-38行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/convert_p3_to_audio.py
以下为原始源码，不是截图OCR。
```
31:                     break
32: 
33:                 pcm = decoder.decode(opus_data, frame_size)
34:                 pcm_frames.append(np.frombuffer(pcm, dtype=np.int16))
35: 
36:                 pbar.update(4 + opus_len)
37: 
38:     if not pcm_frames:
```

## convert_p3_to_audio.py | ValueError | 原文件第39-51行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/convert_p3_to_audio.py
以下为原始源码，不是截图OCR。
```
39:         raise ValueError("No valid audio data found")
40: 
41:     pcm_data = np.concatenate(pcm_frames)
42: 
43:     sf.write(output_file, pcm_data, sample_rate, subtype="PCM_16")
44: 
45: 
46: if __name__ == "__main__":
47:     if len(sys.argv) != 3:
48:         print("Usage: python convert_p3_to_audio.py <input.p3> <output.wav>")
49:         sys.exit(1)
50: 
51:     decode_p3_to_audio(sys.argv[1], sys.argv[2])
```

## p3_gui_player.py | 文件开头/全局定义 | 原文件第1-11行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
1: import tkinter as tk
2: from tkinter import filedialog, messagebox
3: import threading
4: import time
5: import opuslib
6: import struct
7: import numpy as np
8: import sounddevice as sd
9: import os
10: 
11: 
```

## p3_gui_player.py | play_p3_file | 原文件第12-25行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
12: def play_p3_file(input_file, stop_event=None, pause_event=None):
13:     """
14:     播放p3格式的音频文件
15:     p3格式: [1字节类型, 1字节保留, 2字节长度, Opus数据]
16:     """
17:     # 初始化Opus解码器
18:     sample_rate = 16000  # 采样率固定为16000Hz
19:     channels = 1  # 单声道
20:     decoder = opuslib.Decoder(sample_rate, channels)
21:     
22:     # 帧大小 (60ms)
23:     frame_size = int(sample_rate * 60 / 1000)
24:     
25:     # 打开音频流
```

## p3_gui_player.py | play_p3_file | 原文件第26-40行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
26:     stream = sd.OutputStream(
27:         samplerate=sample_rate,
28:         channels=channels,
29:         dtype='int16'
30:     )
31:     stream.start()
32:     
33:     try:
34:         with open(input_file, 'rb') as f:
35:             print(f"正在播放: {input_file}")
36:             
37:             while True:
38:                 if stop_event and stop_event.is_set():
39:                     break
40: 
```

## p3_gui_player.py | play_p3_file | 原文件第41-51行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
41:                 if pause_event and pause_event.is_set():
42:                     time.sleep(0.1)
43:                     continue
44: 
45:                 # 读取头部 (4字节)
46:                 header = f.read(4)
47:                 if not header or len(header) < 4:
48:                     break
49:                 
50:                 # 解析头部
51:                 packet_type, reserved, data_len = struct.unpack('>BBH', header)
```

## p3_gui_player.py | play_p3_file | 原文件第52-61行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
52:                 
53:                 # 读取Opus数据
54:                 opus_data = f.read(data_len)
55:                 if not opus_data or len(opus_data) < data_len:
56:                     break
57:                 
58:                 # 解码Opus数据
59:                 pcm_data = decoder.decode(opus_data, frame_size)
60:                 
61:                 # 将字节转换为numpy数组
```

## p3_gui_player.py | play_p3_file | 原文件第62-72行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
62:                 audio_array = np.frombuffer(pcm_data, dtype=np.int16)
63:                 
64:                 # 播放音频
65:                 stream.write(audio_array)
66:                 
67:                 # 等待一帧的时间
68:                 time.sleep(60 / 1000)  # 60ms
69:             
70:             # 播放结束后添加0.5秒静音，避免破音
71:             silence = np.zeros(int(sample_rate / 2), dtype=np.int16)
72:             stream.write(silence)
```

## p3_gui_player.py | play_p3_file | 原文件第73-83行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
73:             time.sleep(0.5)  # 等待1秒
74:                 
75:     except KeyboardInterrupt:
76:         print("\n播放已停止")
77:     finally:
78:         stream.stop()
79:         stream.close()
80:         print("播放完成")
81: 
82: 
83: class P3PlayerApp:
```

## p3_gui_player.py | __init__ | 原文件第84-94行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
84:     def __init__(self, root):
85:         self.root = root
86:         self.root.title("P3 文件简易播放器")
87:         self.root.geometry("500x400")
88: 
89:         self.playlist = []
90:         self.current_index = 0
91:         self.is_playing = False
92:         self.is_paused = False
93:         self.stop_event = threading.Event()
94:         self.pause_event = threading.Event()
```

## p3_gui_player.py | __init__ | 原文件第95-99行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
95:         self.loop_playback = tk.BooleanVar(value=False)  # 循环播放复选框的状态
96: 
97:         # 创建界面组件
98:         self.create_widgets()
99: 
```

## p3_gui_player.py | create_widgets | 原文件第100-108行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
100:     def create_widgets(self):
101:         # 播放列表
102:         self.playlist_label = tk.Label(self.root, text="播放列表:")
103:         self.playlist_label.pack(pady=5)
104: 
105:         self.playlist_frame = tk.Frame(self.root)
106:         self.playlist_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
107: 
108:         self.playlist_listbox = tk.Listbox(self.playlist_frame, selectmode=tk.SINGLE)
```

## p3_gui_player.py | create_widgets | 原文件第109-118行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
109:         self.playlist_listbox.pack(fill=tk.BOTH, expand=True)
110: 
111:         # 复选框和移除按钮
112:         self.checkbox_frame = tk.Frame(self.root)
113:         self.checkbox_frame.pack(pady=5)
114: 
115:         self.remove_button = tk.Button(self.checkbox_frame, text="移除文件", command=self.remove_files)
116:         self.remove_button.pack(side=tk.LEFT, padx=5)
117: 
118:         # 循环播放复选框
```

## p3_gui_player.py | create_widgets | 原文件第119-126行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
119:         self.loop_checkbox = tk.Checkbutton(self.checkbox_frame, text="循环播放", variable=self.loop_playback)
120:         self.loop_checkbox.pack(side=tk.LEFT, padx=5)
121: 
122:         # 控制按钮
123:         self.control_frame = tk.Frame(self.root)
124:         self.control_frame.pack(pady=10)
125: 
126:         self.add_button = tk.Button(self.control_frame, text="添加文件", command=self.add_file)
```

## p3_gui_player.py | create_widgets | 原文件第127-134行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
127:         self.add_button.grid(row=0, column=0, padx=5)
128: 
129:         self.play_button = tk.Button(self.control_frame, text="播放", command=self.play)
130:         self.play_button.grid(row=0, column=1, padx=5)
131: 
132:         self.pause_button = tk.Button(self.control_frame, text="暂停", command=self.pause)
133:         self.pause_button.grid(row=0, column=2, padx=5)
134: 
```

## p3_gui_player.py | create_widgets | 原文件第135-141行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
135:         self.stop_button = tk.Button(self.control_frame, text="停止", command=self.stop)
136:         self.stop_button.grid(row=0, column=3, padx=5)
137: 
138:         # 状态标签
139:         self.status_label = tk.Label(self.root, text="未在播放", fg="blue")
140:         self.status_label.pack(pady=10)
141: 
```

## p3_gui_player.py | add_file | 原文件第142-147行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
142:     def add_file(self):
143:         files = filedialog.askopenfilenames(filetypes=[("P3 文件", "*.p3")])
144:         if files:
145:             self.playlist.extend(files)
146:             self.update_playlist()
147: 
```

## p3_gui_player.py | update_playlist | 原文件第148-152行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
148:     def update_playlist(self):
149:         self.playlist_listbox.delete(0, tk.END)
150:         for file in self.playlist:
151:             self.playlist_listbox.insert(tk.END, os.path.basename(file))  # 仅显示文件名
152: 
```

## p3_gui_player.py | update_status | 原文件第153-156行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
153:     def update_status(self, status_text, color="blue"):
154:         """更新状态标签的内容"""
155:         self.status_label.config(text=status_text, fg=color)
156: 
```

## p3_gui_player.py | play | 原文件第157-168行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
157:     def play(self):
158:         if not self.playlist:
159:             messagebox.showwarning("警告", "播放列表为空！")
160:             return
161: 
162:         if self.is_paused:
163:             self.is_paused = False
164:             self.pause_event.clear()
165:             self.update_status(f"正在播放：{os.path.basename(self.playlist[self.current_index])}", "green")
166:             return
167: 
168:         if self.is_playing:
```

## p3_gui_player.py | play | 原文件第169-176行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
169:             return
170: 
171:         self.is_playing = True
172:         self.stop_event.clear()
173:         self.pause_event.clear()
174:         self.current_index = self.playlist_listbox.curselection()[0] if self.playlist_listbox.curselection() else 0
175:         self.play_thread = threading.Thread(target=self.play_audio, daemon=True)
176:         self.play_thread.start()
```

## p3_gui_player.py | play | 原文件第177-178行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
177:         self.update_status(f"正在播放：{os.path.basename(self.playlist[self.current_index])}", "green")
178: 
```

## p3_gui_player.py | play_audio | 原文件第179-190行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
179:     def play_audio(self):
180:         while True:
181:             if self.stop_event.is_set():
182:                 break
183: 
184:             if self.pause_event.is_set():
185:                 time.sleep(0.1)
186:                 continue
187: 
188:             # 检查当前索引是否有效
189:             if self.current_index >= len(self.playlist):
190:                 if self.loop_playback.get():  # 如果勾选了循环播放
```

## p3_gui_player.py | play_audio | 原文件第191-198行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
191:                     self.current_index = 0  # 回到第一首
192:                 else:
193:                     break  # 否则停止播放
194: 
195:             file = self.playlist[self.current_index]
196:             self.playlist_listbox.selection_clear(0, tk.END)
197:             self.playlist_listbox.selection_set(self.current_index)
198:             self.playlist_listbox.activate(self.current_index)
```

## p3_gui_player.py | play_audio | 原文件第199-208行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
199:             self.update_status(f"正在播放：{os.path.basename(self.playlist[self.current_index])}", "green")
200:             play_p3_file(file, self.stop_event, self.pause_event)
201: 
202:             if self.stop_event.is_set():
203:                 break
204: 
205:             if not self.loop_playback.get():  # 如果没有勾选循环播放
206:                 break  # 播放完当前文件后停止
207: 
208:             self.current_index += 1
```

## p3_gui_player.py | play_audio | 原文件第209-216行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
209:             if self.current_index >= len(self.playlist):
210:                 if self.loop_playback.get():  # 如果勾选了循环播放
211:                     self.current_index = 0  # 回到第一首
212: 
213:         self.is_playing = False
214:         self.is_paused = False
215:         self.update_status("播放已停止", "red")
216: 
```

## p3_gui_player.py | pause | 原文件第217-226行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
217:     def pause(self):
218:         if self.is_playing:
219:             self.is_paused = not self.is_paused
220:             if self.is_paused:
221:                 self.pause_event.set()
222:                 self.update_status("播放已暂停", "orange")
223:             else:
224:                 self.pause_event.clear()
225:                 self.update_status(f"正在播放：{os.path.basename(self.playlist[self.current_index])}", "green")
226: 
```

## p3_gui_player.py | stop | 原文件第227-234行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
227:     def stop(self):
228:         if self.is_playing or self.is_paused:
229:             self.is_playing = False
230:             self.is_paused = False
231:             self.stop_event.set()
232:             self.pause_event.clear()
233:             self.update_status("播放已停止", "red")
234: 
```

## p3_gui_player.py | remove_files | 原文件第235-247行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
235:     def remove_files(self):
236:         selected_indices = self.playlist_listbox.curselection()
237:         if not selected_indices:
238:             messagebox.showwarning("警告", "请先选择要移除的文件！")
239:             return
240: 
241:         for index in reversed(selected_indices):
242:             self.playlist.pop(index)
243:         self.update_playlist()
244: 
245: 
246: if __name__ == "__main__":
247:     root = tk.Tk()
```

## p3_gui_player.py | remove_files | 原文件第248-249行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/p3_gui_player.py
以下为原始源码，不是截图OCR。
```
248:     app = P3PlayerApp(root)
249:     root.mainloop()
```

## play_p3.py | 文件开头/全局定义 | 原文件第1-8行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/play_p3.py
以下为原始源码，不是截图OCR。
```
1: # 播放p3格式的音频文件
2: import opuslib
3: import struct
4: import numpy as np
5: import sounddevice as sd
6: import time
7: import argparse
8: 
```

## play_p3.py | play_p3_file | 原文件第9-23行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/play_p3.py
以下为原始源码，不是截图OCR。
```
9: def play_p3_file(input_file):
10:     """
11:     播放p3格式的音频文件
12:     p3格式: [1字节类型, 1字节保留, 2字节长度, Opus数据]
13:     """
14:     # 初始化Opus解码器
15:     sample_rate = 16000  # 采样率固定为16000Hz
16:     channels = 1  # 单声道
17:     decoder = opuslib.Decoder(sample_rate, channels)
18:     
19:     # 帧大小 (60ms)
20:     frame_size = int(sample_rate * 60 / 1000)
21:     
22:     # 打开音频流
23:     stream = sd.OutputStream(
```

## play_p3.py | play_p3_file | 原文件第24-38行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/play_p3.py
以下为原始源码，不是截图OCR。
```
24:         samplerate=sample_rate,
25:         channels=channels,
26:         dtype='int16'
27:     )
28:     stream.start()
29:     
30:     try:
31:         with open(input_file, 'rb') as f:
32:             print(f"正在播放: {input_file}")
33:             
34:             while True:
35:                 # 读取头部 (4字节)
36:                 header = f.read(4)
37:                 if not header or len(header) < 4:
38:                     break
```

## play_p3.py | play_p3_file | 原文件第39-48行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/play_p3.py
以下为原始源码，不是截图OCR。
```
39:                 
40:                 # 解析头部
41:                 packet_type, reserved, data_len = struct.unpack('>BBH', header)
42:                 
43:                 # 读取Opus数据
44:                 opus_data = f.read(data_len)
45:                 if not opus_data or len(opus_data) < data_len:
46:                     break
47:                 
48:                 # 解码Opus数据
```

## play_p3.py | play_p3_file | 原文件第49-59行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/play_p3.py
以下为原始源码，不是截图OCR。
```
49:                 pcm_data = decoder.decode(opus_data, frame_size)
50:                 
51:                 # 将字节转换为numpy数组
52:                 audio_array = np.frombuffer(pcm_data, dtype=np.int16)
53:                 
54:                 # 播放音频
55:                 stream.write(audio_array)
56:                 
57:                 # 等待一帧的时间
58:                 time.sleep(60 / 1000)  # 60ms
59:             
```

## play_p3.py | play_p3_file | 原文件第60-71行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/play_p3.py
以下为原始源码，不是截图OCR。
```
60:             # 播放结束后添加1秒静音，避免破音
61:             silence = np.zeros(int(sample_rate), dtype=np.int16)
62:             stream.write(silence)
63:             time.sleep(1)  # 等待1秒
64:                 
65:     except KeyboardInterrupt:
66:         print("\n播放已停止")
67:     finally:
68:         stream.stop()
69:         stream.close()
70:         print("播放完成")
71: 
```

## play_p3.py | main | 原文件第72-80行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/p3_tools/play_p3.py
以下为原始源码，不是截图OCR。
```
72: def main():
73:     parser = argparse.ArgumentParser(description='播放p3格式的音频文件')
74:     parser.add_argument('input_file', help='输入的p3文件路径')
75:     args = parser.parse_args()
76:     
77:     play_p3_file(args.input_file)
78: 
79: if __name__ == "__main__":
80:     main() 
```

## release.py | 文件开头/全局定义 | 原文件第1-8行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/release.py
以下为原始源码，不是截图OCR。
```
1: import sys
2: import os
3: import json
4: import zipfile
5: 
6: # 切换到项目根目录
7: os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
8: 
```

## release.py | get_board_type | 原文件第9-18行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/release.py
以下为原始源码，不是截图OCR。
```
9: def get_board_type():
10:     with open("build/compile_commands.json") as f:
11:         data = json.load(f)
12:         for item in data:
13:             if not item["file"].endswith("main.cc"):
14:                 continue
15:             command = item["command"]
16:             # extract -DBOARD_TYPE=xxx
17:             board_type = command.split("-DBOARD_TYPE=\\\"")[1].split("\\\"")[0].strip()
18:             return board_type
```

## release.py | get_board_type | 原文件第19-20行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/release.py
以下为原始源码，不是截图OCR。
```
19:     return None
20: 
```

## release.py | get_project_version | 原文件第21-27行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/release.py
以下为原始源码，不是截图OCR。
```
21: def get_project_version():
22:     with open("CMakeLists.txt") as f:
23:         for line in f:
24:             if line.startswith("set(PROJECT_VER"):
25:                 return line.split("\"")[1].split("\"")[0].strip()
26:     return None
27: 
```

## release.py | merge_bin | 原文件第28-32行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/release.py
以下为原始源码，不是截图OCR。
```
28: def merge_bin():
29:     if os.system("idf.py merge-bin") != 0:
30:         print("merge bin failed")
31:         sys.exit(1)
32: 
```

## release.py | zip_bin | 原文件第33-40行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/release.py
以下为原始源码，不是截图OCR。
```
33: def zip_bin(board_type, project_version):
34:     if not os.path.exists("releases"):
35:         os.makedirs("releases")
36:     output_path = f"releases/v{project_version}_{board_type}.zip"
37:     if os.path.exists(output_path):
38:         os.remove(output_path)
39:     with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
40:         zipf.write("build/merged-binary.bin", arcname="merged-binary.bin")
```

## release.py | zip_bin | 原文件第41-43行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/release.py
以下为原始源码，不是截图OCR。
```
41:     print(f"zip bin to {output_path} done")
42:     
43: 
```

## release.py | release_current | 原文件第44-51行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/release.py
以下为原始源码，不是截图OCR。
```
44: def release_current():
45:     merge_bin()
46:     board_type = get_board_type()
47:     print("board type:", board_type)
48:     project_version = get_project_version()
49:     print("project version:", project_version)
50:     zip_bin(board_type, project_version)
51: 
```

## release.py | get_all_board_types | 原文件第52-60行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/release.py
以下为原始源码，不是截图OCR。
```
52: def get_all_board_types():
53:     board_configs = {}
54:     with open("main/CMakeLists.txt") as f:
55:         lines = f.readlines()
56:         for i, line in enumerate(lines):
57:             # 查找 if(CONFIG_BOARD_TYPE_*) 行
58:             if "if(CONFIG_BOARD_TYPE_" in line:
59:                 config_name = line.strip().split("if(")[1].split(")")[0]
60:                 # 查找下一行的 set(BOARD_TYPE "xxx") 
```

## release.py | get_all_board_types | 原文件第61-66行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/release.py
以下为原始源码，不是截图OCR。
```
61:                 next_line = lines[i + 1].strip()
62:                 if next_line.startswith("set(BOARD_TYPE"):
63:                     board_type = next_line.split('"')[1]
64:                     board_configs[config_name] = board_type
65:     return board_configs
66: 
```

## release.py | release | 原文件第67-76行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/release.py
以下为原始源码，不是截图OCR。
```
67: def release(board_type, board_config):
68:     config_path = f"main/boards/{board_type}/config.json"
69:     if not os.path.exists(config_path):
70:         print(f"跳过 {board_type} 因为 config.json 不存在")
71:         return
72: 
73:     # Print Project Version
74:     project_version = get_project_version()
75:     print(f"Project Version: {project_version}")
76:     release_path = f"releases/v{project_version}_{board_type}.zip"
```

## release.py | release | 原文件第77-88行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/release.py
以下为原始源码，不是截图OCR。
```
77:     if os.path.exists(release_path):
78:         print(f"跳过 {board_type} 因为 {release_path} 已存在")
79:         return
80: 
81:     with open(config_path, "r") as f:
82:         config = json.load(f)
83:     target = config["target"]
84:     builds = config["builds"]
85:     
86:     for build in builds:
87:         name = build["name"]
88:         if not name.startswith(board_type):
```

## release.py | ValueError | 原文件第89-98行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/release.py
以下为原始源码，不是截图OCR。
```
89:             raise ValueError(f"name {name} 必须 {board_type} 开头")
90: 
91:         sdkconfig_append = [f"{board_config}=y"]
92:         for append in build.get("sdkconfig_append", []):
93:             sdkconfig_append.append(append)
94:         print(f"name: {name}")
95:         print(f"target: {target}")
96:         for append in sdkconfig_append:
97:             print(f"sdkconfig_append: {append}")
98:         # unset IDF_TARGET
```

## release.py | ValueError | 原文件第99-108行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/release.py
以下为原始源码，不是截图OCR。
```
99:         os.environ.pop("IDF_TARGET", None)
100:         # Call set-target
101:         if os.system(f"idf.py set-target {target}") != 0:
102:             print("set-target failed")
103:             sys.exit(1)
104:         # Append sdkconfig
105:         with open("sdkconfig", "a") as f:
106:             f.write("\n")
107:             for append in sdkconfig_append:
108:                 f.write(f"{append}\n")
```

## release.py | ValueError | 原文件第109-118行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/release.py
以下为原始源码，不是截图OCR。
```
109:         # Build with macro BOARD_NAME defined to name
110:         if os.system(f"idf.py -DBOARD_NAME={name} build") != 0:
111:             print("build failed")
112:             sys.exit(1)
113:         # Call merge-bin
114:         if os.system("idf.py merge-bin") != 0:
115:             print("merge-bin failed")
116:             sys.exit(1)
117:         # Zip bin
118:         zip_bin(name, project_version)
```

## release.py | ValueError | 原文件第119-129行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/release.py
以下为原始源码，不是截图OCR。
```
119:         print("-" * 80)
120: 
121: if __name__ == "__main__":
122:     if len(sys.argv) > 1:
123:         board_configs = get_all_board_types()
124:         found = False
125:         for board_config, board_type in board_configs.items():
126:             if sys.argv[1] == 'all' or board_type == sys.argv[1]:
127:                 release(board_type, board_config)
128:                 found = True
129:         if not found:
```

## release.py | ValueError | 原文件第130-135行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/release.py
以下为原始源码，不是截图OCR。
```
130:             print(f"未找到板子类型: {sys.argv[1]}")
131:             print("可用的板子类型:")
132:             for board_type in board_configs.values():
133:                 print(f"  {board_type}")
134:     else:
135:         release_current()
```

## versions.py | 文件开头/全局定义 | 原文件第1-15行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
1: #! /usr/bin/env python3
2: from dotenv import load_dotenv
3: load_dotenv()
4: 
5: import os
6: import struct
7: import zipfile
8: import oss2
9: import json
10: import requests
11: from requests.exceptions import RequestException
12: 
13: # 切换到项目根目录
14: os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
15: 
```

## versions.py | get_chip_id_string | 原文件第16-29行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
16: def get_chip_id_string(chip_id):
17:     return {
18:         0x0000: "esp32",
19:         0x0002: "esp32s2",
20:         0x0005: "esp32c3",
21:         0x0009: "esp32s3",
22:         0x000C: "esp32c2",
23:         0x000D: "esp32c6",
24:         0x0010: "esp32h2",
25:         0x0011: "esp32c5",
26:         0x0012: "esp32p4",
27:         0x0017: "esp32c5",
28:     }[chip_id]
29: 
```

## versions.py | get_flash_size | 原文件第30-42行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
30: def get_flash_size(flash_size):
31:     MB = 1024 * 1024
32:     return {
33:         0x00: 1 * MB,
34:         0x01: 2 * MB,
35:         0x02: 4 * MB,
36:         0x03: 8 * MB,
37:         0x04: 16 * MB,
38:         0x05: 32 * MB,
39:         0x06: 64 * MB,
40:         0x07: 128 * MB,
41:     }[flash_size]
42: 
```

## versions.py | get_app_desc | 原文件第43-45行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
43: def get_app_desc(data):
44:     magic = struct.unpack("<I", data[0x00:0x04])[0]
45:     if magic != 0xabcd5432:
```

## versions.py | Exception | 原文件第46-53行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
46:         raise Exception("Invalid app desc magic")
47:     version = data[0x10:0x30].decode("utf-8").strip('\0')
48:     project_name = data[0x30:0x50].decode("utf-8").strip('\0')
49:     time = data[0x50:0x60].decode("utf-8").strip('\0')
50:     date = data[0x60:0x70].decode("utf-8").strip('\0')
51:     idf_ver = data[0x70:0x90].decode("utf-8").strip('\0')
52:     elf_sha256 = data[0x90:0xb0].hex()
53:     return {
```

## versions.py | Exception | 原文件第54-60行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
54:         "name": project_name,
55:         "version": version,
56:         "compile_time": date + "T" + time,
57:         "idf_version": idf_ver,
58:         "elf_sha256": elf_sha256,
59:     }
60: 
```

## versions.py | get_board_name | 原文件第61-68行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
61: def get_board_name(folder):
62:     basename = os.path.basename(folder)
63:     if basename.startswith("v0.2"):
64:         return "bread-simple"
65:     if basename.startswith("v0.3") or basename.startswith("v0.4") or basename.startswith("v0.5") or basename.startswith("v0.6"):
66:         if "ML307" in basename:
67:             return "bread-compact-ml307"
68:         elif "WiFi" in basename:
```

## versions.py | get_board_name | 原文件第69-73行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
69:             return "bread-compact-wifi"
70:         elif "KevinBox1" in basename:
71:             return "kevin-box-1"
72:     if basename.startswith("v0.7") or basename.startswith("v0.8") or basename.startswith("v0.9") or basename.startswith("v1."):
73:         return basename.split("_")[1]
```

## versions.py | Exception | 原文件第74-75行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
74:     raise Exception(f"Unknown board name: {basename}")
75: 
```

## versions.py | read_binary | 原文件第76-85行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
76: def read_binary(dir_path):
77:     merged_bin_path = os.path.join(dir_path, "merged-binary.bin")
78:     data = open(merged_bin_path, "rb").read()[0x100000:]
79:     if data[0] != 0xE9:
80:         print(dir_path, "is not a valid image")
81:         return
82:     # get flash size
83:     flash_size = get_flash_size(data[0x3] >> 4)
84:     chip_id = get_chip_id_string(data[0xC])
85:     # get segments
```

## versions.py | read_binary | 原文件第86-96行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
86:     segment_count = data[0x1]
87:     segments = []
88:     offset = 0x18
89:     for i in range(segment_count):
90:         segment_size = struct.unpack("<I", data[offset + 4:offset + 8])[0]
91:         offset += 8
92:         segment_data = data[offset:offset + segment_size]
93:         offset += segment_size
94:         segments.append(segment_data)
95:     assert offset < len(data), "offset is out of bounds"
96:     
```

## versions.py | read_binary | 原文件第97-107行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
97:     # extract bin file
98:     bin_path = os.path.join(dir_path, "xiaozhi.bin")
99:     if not os.path.exists(bin_path):
100:         print("extract bin file to", bin_path)
101:         open(bin_path, "wb").write(data)
102: 
103:     # The app desc is in the first segment
104:     desc = get_app_desc(segments[0])
105:     return {
106:         "chip_id": chip_id,
107:         "flash_size": flash_size,
```

## versions.py | read_binary | 原文件第108-112行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
108:         "board": get_board_name(dir_path),
109:         "application": desc,
110:         "firmware_size": len(data),
111:     }
112: 
```

## versions.py | extract_zip | 原文件第113-119行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
113: def extract_zip(zip_path, extract_path):
114:     if not os.path.exists(extract_path):
115:         os.makedirs(extract_path)
116:     print(f"Extracting {zip_path} to {extract_path}")
117:     with zipfile.ZipFile(zip_path, 'r') as zip_ref:
118:         zip_ref.extractall(extract_path)
119: 
```

## versions.py | upload_dir_to_oss | 原文件第120-125行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
120: def upload_dir_to_oss(source_dir, target_dir):
121:     auth = oss2.Auth(os.environ['OSS_ACCESS_KEY_ID'], os.environ['OSS_ACCESS_KEY_SECRET'])
122:     bucket = oss2.Bucket(auth, os.environ['OSS_ENDPOINT'], os.environ['OSS_BUCKET_NAME'])
123:     for filename in os.listdir(source_dir):
124:         oss_key = os.path.join(target_dir, filename)
125:         print('uploading', oss_key)
```

## versions.py | upload_dir_to_oss | 原文件第126-127行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
126:         bucket.put_object(oss_key, open(os.path.join(source_dir, filename), 'rb'))
127: 
```

## versions.py | post_info_to_server | 原文件第128-140行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
128: def post_info_to_server(info):
129:     """
130:     将固件信息发送到服务器
131:     
132:     Args:
133:         info: 包含固件信息的字典
134:     """
135:     try:
136:         # 从环境变量获取服务器URL和token
137:         server_url = os.environ.get('VERSIONS_SERVER_URL')
138:         server_token = os.environ.get('VERSIONS_TOKEN')
139:         
140:         if not server_url or not server_token:
```

## versions.py | Exception | 原文件第141-152行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
141:             raise Exception("Missing SERVER_URL or TOKEN in environment variables")
142: 
143:         # 准备请求头和数据
144:         headers = {
145:             'Authorization': f'Bearer {server_token}',
146:             'Content-Type': 'application/json'
147:         }
148:         
149:         # 发送POST请求
150:         response = requests.post(
151:             server_url,
152:             headers=headers,
```

## versions.py | Exception | 原文件第153-164行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
153:             json={'jsonData': json.dumps(info)}
154:         )
155:         
156:         # 检查响应状态
157:         response.raise_for_status()
158:         
159:         print(f"Successfully uploaded version info for tag: {info['tag']}")
160:         
161:     except RequestException as e:
162:         if hasattr(e.response, 'json'):
163:             error_msg = e.response.json().get('error', str(e))
164:         else:
```

## versions.py | Exception | 原文件第165-171行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
165:             error_msg = str(e)
166:         print(f"Failed to upload version info: {error_msg}")
167:         raise
168:     except Exception as e:
169:         print(f"Error uploading version info: {str(e)}")
170:         raise
171: 
```

## versions.py | main | 原文件第172-180行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
172: def main():
173:     release_dir = "releases"
174:     # look for zip files startswith "v"
175:     for name in os.listdir(release_dir):
176:         if name.startswith("v") and name.endswith(".zip"):
177:             tag = name[:-4]
178:             folder = os.path.join(release_dir, tag)
179:             info_path = os.path.join(folder, "info.json")
180:             if not os.path.exists(info_path):
```

## versions.py | main | 原文件第181-187行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
181:                 if not os.path.exists(folder):
182:                     os.makedirs(folder)
183:                     extract_zip(os.path.join(release_dir, name), folder)
184:                 info = read_binary(folder)
185:                 target_dir = os.path.join("firmwares", tag)
186:                 info["tag"] = tag
187:                 info["url"] = os.path.join(os.environ['OSS_BUCKET_URL'], target_dir, "xiaozhi.bin")
```

## versions.py | main | 原文件第188-199行
来源：003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/scripts/versions.py
以下为原始源码，不是截图OCR。
```
188:                 open(info_path, "w").write(json.dumps(info, indent=4))
189:                 # upload all file to oss
190:                 upload_dir_to_oss(folder, target_dir)
191:                 # read info.json
192:                 info = json.load(open(info_path))
193:                 # post info.json to server
194:                 post_info_to_server(info)
195: 
196: 
197: 
198: if __name__ == "__main__":
199:     main()
```
