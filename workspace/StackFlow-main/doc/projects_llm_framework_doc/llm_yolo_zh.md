# llm-yolo
yolo 视觉检测单元，用于提供图片检测服务。可选择多用 yolo 模型。

## setup
配置单元工作。

发送 json：
```json
{
    "request_id": "2",
    "work_id": "yolo",
    "action": "setup",
    "object": "yolo.setup",
    "data": {
        "model": "yolov5",
        "response_format": "yolo.box",
        "input": "yolo.jpg.base64",
        "enoutput": true
    }
}
```
- request_id：参考基本数据解释。
- work_id：配置单元时，为 `yolo`。
- action：调用的方法为 `setup`。
- object：传输的数据类型为 `yolo.setup`。
- model：使用的模型为 `yolov5` 模型。
- response_format：返回结果为 `yolo.box`。
- input：输入的为 `yolo.jpg.base64`,代表的是从用户输入，数据类型为 jpg, base64编码。
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
    "work_id":"yolo.1003"
}
```
- created：消息创建时间，unix 时间。
- work_id：返回成功创建的 work_id 单元。


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
	"work_id": "yolo",
	"action": "taskinfo"
}
```

响应 json：

```json
{
    "created":1731652311,
    "data":["yolo.1003"],
    "error":{
        "code":0,
        "message":""
    },
    "object":"yolo.tasklist",
    "request_id":"2",
    "work_id":"yolo"
}
```

获取任务运行参数。

发送 json：
```json
{
	"request_id": "2",
	"work_id": "yolo.1003",
	"action": "taskinfo"
}
```

响应 json：

```json
{
    "created":1731652344,
    "data":{
        "enoutput":false,
        "inputs_":["yolo.jpg.base64"],
        "model":"yolov5",
        "response_format":"yolo.box"
    },
    "error":{
        "code":0,
        "message":""
    },
    "object":"tts.taskinfo",
    "request_id":"2",
    "work_id":"yolo.1003"
}
```


> **注意：work_id 是按照单元的初始化注册顺序增加的，并不是固定的索引值。**  