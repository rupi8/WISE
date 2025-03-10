# llm-llm
Large Model Unit, used to provide large model inference services.

## setup
Configure the unit.

Send json:
```json
{
    "request_id": "2",
    "work_id": "llm",
    "action": "setup",
    "object": "llm.setup",
    "data": {
        "model": "qwen2.5-0.5B-prefill-20e",
        "response_format": "llm.utf-8.stream",
        "input": "llm.utf-8",
        "enoutput": true,
        "max_token_len": 256,
        "prompt": "You are a knowledgeable assistant capable of answering various questions and providing information."
    }
}
```
- request_id: Refer to the basic data explanation.
- work_id: For configuration unit, it is `llm`.
- action: The method called is `setup`.
- object: The type of data transmitted is `llm.setup`.
- model: The model used is the Chinese model `qwen2.5-0.5B-prefill-20e`.
- response_format: The result returned is in `llm.utf-8.stream`, utf-8 streaming output.
- input: The input is `llm.utf-8`, representing input from the user.
- enoutput: Whether to enable user result output.
- max_token_len: Maximum output token, this value is limited by the model's maximum limit.
- prompt: The prompt for the model.

Response json:

```json
{
    "created": 1731488402,
    "data": "None",
    "error": {
        "code": 0,
        "message": ""
    },
    "object": "None",
    "request_id": "2",
    "work_id": "llm.1002"
}
```
- created: Message creation time, unix time.
- work_id: The successfully created work_id unit.

## link
Link the output of the upper unit.

Send json:
```json
{
    "request_id": "3",
    "work_id": "llm.1002",
    "action": "link",
    "object": "work_id",
    "data": "kws.1000"
}
```

Response json:

```json
{
    "created": 1731488402,
    "data": "None",
    "error": {
        "code": 0,
        "message": ""
    },
    "object": "None",
    "request_id": "3",
    "work_id": "llm.1002"
}
```
error::code of 0 indicates successful execution.

Link the llm and kws units so that when kws issues wake-up data, the llm unit stops the previous unfinished inference for repeated wake-up functionality.

> **When linking, ensure that kws has been configured and is in working status. Linking can also be done during the setup phase.**

Example:

```json
{
    "request_id": "2",
    "work_id": "llm",
    "action": "setup",
    "object": "llm.setup",
    "data": {
        "model": "qwen2.5-0.5B-prefill-20e",
        "response_format": "llm.utf-8.stream",
        "input": ["llm.utf-8", "asr.1001", "kws.1000"],
        "enoutput": true,
        "max_token_len": 256,
        "prompt": "You are a knowledgeable assistant capable of answering various questions and providing information."
    }
}
```

## unlink
Unlink.

Send json:
```json
{
    "request_id": "4",
    "work_id": "llm.1002",
    "action": "unlink",
    "object": "work_id",
    "data": "kws.1000"
}
```

Response json:

```json
{
    "created": 1731488402,
    "data": "None",
    "error": {
        "code": 0,
        "message": ""
    },
    "object": "None",
    "request_id": "4",
    "work_id": "llm.1002"
}
```
error::code of 0 indicates successful execution.

## pause
Pause the unit.

Send json:
```json
{
    "request_id": "5",
    "work_id": "llm.1002",
    "action": "pause"
}
```

Response json:

```json
{
    "created": 1731488402,
    "data": "None",
    "error": {
        "code": 0,
        "message": ""
    },
    "object": "None",
    "request_id": "5",
    "work_id": "llm.1002"
}
```
error::code of 0 indicates successful execution.

## work
Resume the unit.

Send json:
```json
{
    "request_id": "6",
    "work_id": "llm.1002",
    "action": "work"
}
```

Response json:

```json
{
    "created": 1731488402,
    "data": "None",
    "error": {
        "code": 0,
        "message": ""
    },
    "object": "None",
    "request_id": "6",
    "work_id": "llm.1002"
}
```
error::code of 0 indicates successful execution.

## exit
Exit the unit.

Send json:
```json
{
    "request_id": "7",
    "work_id": "llm.1002",
    "action": "exit"
}
```

Response json:

```json
{
    "created": 1731488402,
    "data": "None",
    "error": {
        "code": 0,
        "message": ""
    },
    "object": "None",
    "request_id": "7",
    "work_id": "llm.1002"
}
```
error::code of 0 indicates successful execution.

## Task Information

Get task list.

Send JSON:
```json
{
	"request_id": "2",
	"work_id": "llm",
	"action": "taskinfo"
}
```

Response JSON:
```json
{
    "created":1731652149,
    "data":["llm.1002"],
    "error":{
        "code":0,
        "message":""
    },
    "object":"llm.tasklist",
    "request_id":"2",
    "work_id":"llm"
}
```

Get task runtime parameters.

Send JSON:
```json
{
	"request_id": "2",
	"work_id": "llm.1002",
	"action": "taskinfo"
}
```

Response JSON:
```json
{
    "created":1731652187,
    "data":{
        "enoutput":true,
        "inputs_":["llm.utf-8"],
        "model":"qwen2.5-0.5B-prefill-20e",
        "response_format":"llm.utf-8.stream"
    },
    "error":{
        "code":0,
        "message":""
    },
    "object":"llm.taskinfo",
    "request_id":"2",
    "work_id":"llm.1002"
}
```

> **Note: work_id increases according to the initialization registration order of the unit and is not a fixed index value.**