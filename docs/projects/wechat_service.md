
## 微信自动化服务 (`.exe`) 开发对接文档


`https://github.com/lhnows/WeChatify`

这份文档将详细说明如何与您打包好的 `wechat_gui_service.exe` 程序进行交互，主要包含两部分：**如何接收程序推送的消息（消息回调）** 和 **如何调用程序的接口来执行任务**。

### 一、 概述

本服务程序 (`.exe`) 提供了两大核心功能，允许您的外部业务系统与微信进行集成：

1.  **消息回调**: 当监控的微信账号收到新消息时，本程序会自动将消息内容通过HTTP POST请求发送到您预先配置的回调URL。
2.  **任务执行接口**: 本程序会启动一个HTTP API服务，您的系统可以调用此接口来下发指令，如发送消息、添加好友等，程序会按顺序执行这些任务。

**核心机制**：所有微信操作（包括检查消息和执行API任务）都在一个任务队列中**串行执行**，以确保操作的稳定性和可靠性。

### 二、 消息回调接口

当程序检测到新的微信消息时，会向您在GUI界面上配置的“消息回调URL”发送一个HTTP请求。您的服务端需要准备好接收这些请求。

* **请求方法**: `POST`
* **数据格式 (`Content-Type`)**: `application/json`

#### 回调数据载荷 (Payload) 结构

您的回调接口收到的JSON对象将包含以下字段：

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `type` | String | 固定的事件类型，当前值为 `"message"`。 |
| `source_chat` | String | 消息来源的聊天窗口名称（好友昵称或群名）。 |
| `sender` | String | 消息发送者的名称（程序会优先使用备注名，如果没有则使用昵称）。  |
| `content` | String | 消息的文本内容。  |
| `message_type`| String | 消息内容的具体类型，例如 `'text'`, `'image'`, `'file'` 等。  |

#### 回调数据示例

您的服务器收到的JSON数据包示例如下：
```json
{
    "type": "message",
    "source_chat": "张三",
    "sender": "老板-张三",
    "content": "项目计划书下午发我一下",
    "message_type": "text"
}
```

#### 回调服务端示例 (使用Python Flask)

您可以搭建一个简单的Web服务来接收并处理回调数据，示例如下：
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/wechat/callback', methods=['POST'])
def wechat_message_callback():
    # 获取回调的JSON数据
    data = request.json
    print(f"收到微信消息回调: {data}")

    # 在这里编写您的业务逻辑
    # 例如，根据消息内容触发某些操作
    if "计划书" in data.get('content', ''):
        print("检测到关键词'计划书'，正在处理...")
        # ... 执行您的业务逻辑 ...

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    # 假设您的回调服务运行在 5000 端口
    app.run(host='0.0.0.0', port=5000)
```

---

### 三、 任务执行接口

您可以通过调用本程序内置的API接口来命令它执行指定的微信操作。

* **接口地址**: `http://<运行EXE的电脑IP地址>:9000/task`
    * 如果您的业务系统和`.exe`程序在同一台电脑上，可以使用 `http://127.0.0.1:9000/task`。
* **请求方法**: `POST`
* **数据格式 (`Content-Type`)**: `application/json`

#### 任务请求载荷 (Payload) 结构

所有任务请求的JSON载荷都遵循统一的格式：

| 键 | 类型 | 说明 |
| :--- | :--- | :--- |
| `action` | String | **必需。** 指定要执行的操作类型。见下文“支持的操作列表”。 |
| `params` | Object | **必需。** 一个JSON对象，包含执行该操作所需的所有参数。 |

#### 支持的操作 (`action`) 及参数 (`params`) 列表

以下是目前支持的所有`action`及其对应的`params`详解。

##### 1. 发送消息 (`send_message`)
向指定好友或群聊发送文本消息。

* `params` 结构:
  
| 参数名 | 类型  | 是否必需 | 说明 |
| :---  | :---  | :--- | :--- |
| `who` | String | 是  | 接收消息的好友昵称/备注或群名。|
| `content`| String | 是 | 要发送的文本内容。 |

* `cURL` 调用示例:
```bash
curl -X POST http://127.0.0.1:9000/task \
-H "Content-Type: application/json" \
-d '{
    "action": "send_message",
    "params": {
        "who": "文件传输助手",
        "content": "这是一条API调用的测试消息。"
    }
}'
```

##### 2. 添加好友 (`add_friend`)
通过微信号或手机号搜索并发送好友申请。

* `params` 结构:
  
| 参数名 | 类型 | 是否必需 | 说明 |
| :--- | :--- | :--- | :---  |
| `keywords`| String | 是 | 用于搜索的微信号、手机号或QQ号。  |
| `addmsg` | String | 否 | 发送的好友验证信息，默认为"你好,我是xxxx"。  |
| `remark` | String | 否 | 添加成功后为对方设置的备注名。  |

* `cURL` 调用示例:
```bash
curl -X POST http://127.0.0.1:9000/task \
-H "Content-Type: application/json" \
-d '{
    "action": "add_friend",
    "params": {
        "keywords": "wxid_xxxxxxxxxxxx",
        "addmsg": "你好，我是自动化服务机器人",
        "remark": "业务-王总"
    }
}'
```

##### 3. 接受好友请求 (`accept_friend`)
自动同意指定好友的申请。

* `params` 结构:
  
| 参数名 | 类型 | 是否必需 | 说明 |
| :--- | :--- | :--- | :--- |
| `name` | String | 是 | 申请人的**微信昵称**，用于在好友申请列表中进行匹配。  |
| `remark` | String | 否 | 同意后为对方设置的备注名。  |
| `tags` | Array of Strings | 否 | 为新好友设置的标签列表，例如 `["客户", "重要"]`。  |

* `cURL` 调用示例:
```bash
curl -X POST http://127.0.0.1:9000/task \
-H "Content-Type: application/json" \
-d '{
    "action": "accept_friend",
    "params": {
        "name": "李四",
        "remark": "渠道-李四",
        "tags": ["渠道"]
    }
}'
```

##### 4. 邀请好友进群 (`invite_to_group`)
将一个或多个好友拉入指定的群聊。

* `params` 结构:
  
| 参数名 | 类型 | 是否必需 | 说明 |
| :--- | :--- | :--- | :--- |
| `group` | String | 是 | 目标群聊的名称。  |
| `members`| Array of Strings | 是 | 要邀请的成员列表，可以是好友的昵称、备注名或微信号。  |

* `cURL` 调用示例:
```bash
curl -X POST http://127.0.0.1:9000/task \
-H "Content-Type: application/json" \
-d '{
    "action": "invite_to_group",
    "params": {
        "group": "项目紧急讨论组",
        "members": ["业务-王总", "渠道-李四"]
    }
}'
```