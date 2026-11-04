(() => {
  'use strict';

  // 只实现 BOSS 聊天所需的 MQTT 3.1.1 子集。这样扩展不需要引入一个
  // 体积很大的 MQTT 运行时，也不会依赖聊天页面的输入框和发送按钮。
  const utf8 = new TextEncoder();
  const concat = (...parts) => {
    const length = parts.reduce((total, part) => total + part.length, 0);
    const result = new Uint8Array(length);
    let offset = 0;
    parts.forEach(part => { result.set(part, offset); offset += part.length; });
    return result;
  };
  const bytes = value => utf8.encode(String(value || ''));
  const u16 = value => Uint8Array.of((value >>> 8) & 0xff, value & 0xff);
  const string = value => {
    const valueBytes = bytes(value);
    return concat(u16(valueBytes.length), valueBytes);
  };
  const varint = value => {
    let number = typeof value === 'bigint' ? value : BigInt(value || 0);
    const result = [];
    do {
      let part = Number(number & 0x7fn);
      number >>= 7n;
      if (number) part |= 0x80;
      result.push(part);
    } while (number);
    return Uint8Array.from(result);
  };
  const field = (number, wireType, value) => concat(varint((number << 3) | wireType), value);
  const message = fields => concat(...fields.filter(Boolean));
  const pbVarint = (number, value) => field(number, 0, varint(value));
  const pbString = (number, value) => {
    const valueBytes = bytes(value);
    return field(number, 2, concat(varint(valueBytes.length), valueBytes));
  };
  const pbMessage = (number, value) => field(number, 2, concat(varint(value.length), value));
  const mqttLength = length => {
    const result = [];
    do {
      let digit = length % 128;
      length = Math.floor(length / 128);
      if (length) digit |= 0x80;
      result.push(digit);
    } while (length);
    return Uint8Array.from(result);
  };
  const packet = (header, body) => concat(Uint8Array.of(header), mqttLength(body.length), body);
  const bossUuid = () => {
    const alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
    return Array.from({ length: 16 }, () => alphabet[Math.floor(Math.random() * alphabet.length)]).join('');
  };

  function makeTextPayload({ selfUid, bossUid, encryptBossId, bossSource, text, clientMid }) {
    const from = message([pbVarint(1, selfUid), pbVarint(7, 0)]);
    const to = message([pbVarint(1, bossUid), pbString(2, encryptBossId), pbVarint(7, bossSource || 0)]);
    const body = message([pbVarint(1, 1), pbVarint(2, 1), pbString(3, text)]);
    const chatMessage = message([
      pbMessage(1, from), pbMessage(2, to), pbVarint(3, 1), pbVarint(4, clientMid),
      pbVarint(5, Date.now()), pbMessage(6, body), pbVarint(11, clientMid)
    ]);
    return message([pbVarint(1, 1), pbMessage(3, chatMessage)]);
  }

  function makeImagePayload({ selfUid, bossUid, encryptBossId, bossSource, image, clientMid }) {
    const from = message([pbVarint(1, selfUid), pbVarint(7, 0)]);
    const to = message([pbVarint(1, bossUid), pbString(2, encryptBossId), pbVarint(7, bossSource || 0)]);
    const imageInfo = info => message([pbString(1, info.url), pbVarint(2, info.width), pbVarint(3, info.height)]);
    const imageBody = message([pbVarint(1, 0), pbMessage(2, imageInfo(image.tinyImage)), pbMessage(3, imageInfo(image.originImage))]);
    const body = message([pbVarint(1, 3), pbVarint(2, 1), pbMessage(5, imageBody)]);
    const chatMessage = message([
      pbMessage(1, from), pbMessage(2, to), pbVarint(3, 1), pbVarint(4, clientMid),
      pbVarint(5, Date.now()), pbMessage(6, body), pbVarint(11, clientMid)
    ]);
    return message([pbVarint(1, 1), pbMessage(3, chatMessage)]);
  }

  class BossDirectChatClient {
    constructor({ token, wt, selfUid }) {
      this.token = token;
      this.wt = wt;
      this.selfUid = selfUid;
      this.socket = null;
      this.packetId = 1;
    }

    connect() {
      if (!this.token || !this.wt || !this.selfUid) throw new Error('聊天凭据不完整');
      return new Promise((resolve, reject) => {
        const socket = this.socket = new WebSocket('wss://ws6.zhipin.com/chatws', [this.wt]);
        socket.binaryType = 'arraybuffer';
        const timeout = setTimeout(() => reject(new Error('聊天 WebSocket 连接超时')), 10000);
        socket.addEventListener('open', () => {
          const variableHeader = concat(string('MQTT'), Uint8Array.of(4, 0xc2), u16(25));
          // 严格与参考项目 getUuid(16, 16) 对齐：`ws-` 加 16 位字母数字。
          // 服务端会拒绝过长或不符合该模式的 Client ID（CONNACK 2）。
          const clientId = `ws-${bossUuid()}`;
          socket.send(packet(0x10, concat(variableHeader, string(clientId), string(`${this.token}|0`), string(this.wt))));
        }, { once: true });
        socket.addEventListener('message', event => {
          const data = new Uint8Array(event.data);
          // MQTT CONNACK: 0x20 0x02 0x00 0x00
          if (data[0] === 0x20 && data[3] === 0) {
            clearTimeout(timeout);
            resolve();
          } else if (data[0] === 0x20) {
            clearTimeout(timeout);
            reject(new Error(`聊天 WebSocket 被拒绝（CONNACK ${data[3] ?? '未知'}）`));
          }
        });
        socket.addEventListener('error', () => {
          clearTimeout(timeout);
          reject(new Error('聊天 WebSocket 连接失败'));
        }, { once: true });
        socket.addEventListener('close', () => clearTimeout(timeout), { once: true });
      });
    }

    sendPayload(payload) {
      if (!this.socket || this.socket.readyState !== WebSocket.OPEN) throw new Error('聊天 WebSocket 尚未连接');
      const id = this.packetId = this.packetId % 65535 + 1;
      // 与网页聊天客户端保持一致：chat topic、QoS 1、retain。
      this.socket.send(packet(0x33, concat(string('chat'), u16(id), payload)));
      // boss-helper 同样直接 publish，不等待 PUBACK；服务端可能把确认与其他
      // 聊天事件合并发送，不能将“未在限定时间收到单独 PUBACK”视为发送失败。
      return Promise.resolve();
    }

    sendText(target, text) {
      const clientMid = Date.now();
      return this.sendPayload(makeTextPayload({ selfUid: this.selfUid, ...target, text, clientMid }));
    }

    sendImage(target, image) {
      const clientMid = Date.now();
      return this.sendPayload(makeImagePayload({ selfUid: this.selfUid, ...target, image, clientMid }));
    }

    close() {
      if (this.socket?.readyState === WebSocket.OPEN) this.socket.send(Uint8Array.of(0xe0, 0));
      this.socket?.close();
      this.socket = null;
    }

    isOpen() {
      return this.socket?.readyState === WebSocket.OPEN;
    }
  }

  globalThis.BqaDirectChatClient = BossDirectChatClient;
})();
