# llm-tts
文字转语音单元，用于提供文字转语音服务，可选择中英文模型，用于提供中英文文字转语音服务。  

## setup
配置单元工作。

发送 json：
```json
{
    "request_id": "2",
    "work_id": "tts",
    "action": "setup",
    "object": "tts.setup",
    "data": {
        "model": "single_speaker_fast",
        "response_format": "sys.pcm",
        "input": "tts.utf-8",
        "enoutput": false
    }
}
```
- request_id：参考基本数据解释。
- work_id：配置单元时，为 `tts`。
- action：调用的方法为 `setup`。
- object：传输的数据类型为 `tts.setup`。
- model：使用的模型为 `single_speaker_fast` 中文模型。
- response_format：返回结果为 `sys.pcm`, 系统音频数据，并直接发送到 llm-audio 模块进行播放。
- input：输入的为 `tts.utf-8`,代表的是从用户输入。
- enoutput：是否起用用户结果输出。

响应 json：

```json
{
    "created":1731488402,
    "data":"None",
    "error":{
        "code":0,
        "message":""
    },
    "object":"None",
    "request_id":"2",
    "work_id":"llm.1003"
}
```
- created：消息创建时间，unix 时间。
- work_id：返回成功创建的 work_id 单元。

## link
链接上级单元的输出。

发送 json：
```json
{
    "request_id": "3",
    "work_id": "tts.1003",
    "action": "link",
    "object":"work_id",
    "data":"kws.1000"
}
```

响应 json：

```json
{
    "created":1731488402,
    "data":"None",
    "error":{
        "code":0,
        "message":""
    },
    "object":"None",
    "request_id":"3",
    "work_id":"tts.1003"
}
```
error::code 为 0 表示执行成功。

将 llm 和 tts 单元链接起来，当 kws 唤醒时 tts 单元停止上次未完成的推理，用于重复唤醒功能。

> **link 时必须保证 kws 此时已经配置好进入工作状态。link 也可以在 setup 阶段进行。**

示例:

```json
{
    "request_id": "2",
    "work_id": "tts",
    "action": "setup",
    "object": "tts.setup",
    "data": {
        "model": "single_speaker_fast",
        "response_format": "sys.pcm",
        "input": ["tts.utf-8", "llm.1002", "kws.1000"],
        "enoutput": false
    }
}
```

## unlink
取消链接。

发送 json：

```json
{
    "request_id": "4",
    "work_id": "tts.1003",
    "action": "unlink",
    "object":"work_id",
    "data":"kws.1000"
}
```

响应 json：

```json
{
    "created":1731488402,
    "data":"None",
    "error":{
        "code":0,
        "message":""
    },
    "object":"None",
    "request_id":"4",
    "work_id":"tts.1003"
}
```

error::code 为 0 表示执行成功。

## pause
暂停单元工作。

发送 json：

```json
{
    "request_id": "5",
    "work_id": "tts.1003",
    "action": "pause",
}
```

响应 json：

```json
{
    "created":1731488402,
    "data":"None",
    "error":{
        "code":0,
        "message":""
    },
    "object":"None",
    "request_id":"5",
    "work_id":"tts.1003"
}
```
error::code 为 0 表示执行成功。

## work
恢复单元工作。

发送 json：

```json
{
    "request_id": "6",
    "work_id": "tts.1003",
    "action": "work",
}
```

响应 json：

```json
{
    "created":1731488402,
    "data":"None",
    "error":{
        "code":0,
        "message":""
    },
    "object":"None",
    "request_id":"6",
    "work_id":"tts.1003"
}
```
error::code 为 0 表示执行成功。

## exit

单元退出。

发送 json：

```json
{
    "request_id": "7",
    "work_id": "tts.1003",
    "action": "exit",
}
```

响应 json：

```json
{
    "created":1731488402,
    "data":"None",
    "error":{
        "code":0,
        "message":""
    },
    "object":"None",
    "request_id":"7",
    "work_id":"tts.1003"
}
```

error::code 为 0 表示执行成功。

## taskinfo

获取任务列表。

发送 json：
```json
{
	"request_id": "2",
	"work_id": "tts",
	"action": "taskinfo"
}
```

响应 json：

```json
{
    "created":1731652311,
    "data":["tts.1003"],
    "error":{
        "code":0,
        "message":""
    },
    "object":"tts.tasklist",
    "request_id":"2",
    "work_id":"tts"
}
```

获取任务运行参数。

发送 json：
```json
{
	"request_id": "2",
	"work_id": "tts.1003",
	"action": "taskinfo"
}
```

响应 json：

```json
{
    "created":1731652344,
    "data":{
        "enoutput":false,
        "inputs_":["tts.utf-8"],
        "model":"single_speaker_fast",
        "response_format":"sys.pcm"
    },
    "error":{
        "code":0,
        "message":""
    },
    "object":"tts.taskinfo",
    "request_id":"2",
    "work_id":"tts.1003"
}
```


> **注意：work_id 是按照单元的初始化注册顺序增加的，并不是固定的索引值。**  
> **同类型单元不能配置多个单元同时工作，否则会产生未知错误。例如 tts 和 melo tts 不能同时拍起用工作。**