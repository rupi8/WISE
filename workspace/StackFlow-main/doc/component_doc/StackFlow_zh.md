# StackFlow
StackFlow 是 M5STACK 为 AI 加速计算开发的一个通信框架，主要运行在嵌入式 Linux 平台，由 [zmq](https://zeromq.org/) 提供底层通信服务。  
StackFlow 主要提供三种功能，一、远程 RPC 调用，承载单元之间的函数调用。二、消息通信，提供标准消息流服务，更好的串通上下文。三、资源分配，主要用于避免相关单元的通信地址冲突和临时数据储存。  
![](../../assets/image/StackFlow_frame.png)

## pzmq
重新包装了 zmq 的 api，让 ZMQ_PUB、ZMQ_SUB、ZMQ_PUSH、ZMQ_PULL 的调用更加简单便捷，采用异步式回调的方法提供接收消息功能。  
在 ZMQ_REP、ZMQ_REQ 的基础上封装了简单的 RPC 功能，提供 RPC 服务。  

### 相关示例
1、ZMQ_PULL
```c++
/*
 * SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
 *
 * SPDX-License-Identifier: MIT
 */
#include <iostream>
#include "pzmq.hpp"
#include <string>
using namespace StackFlows;
void pull_msg(const std::string &raw_msg){
    std::cout << raw_msg << std::endl;
}
int main(int argc, char *argv[]) {
    pzmq zpull_("ipc:///tmp.5000.socket", ZMQ_PULL, pull_msg);
    while(1) {
        sleep(1);
    }
    return 0;
}
```

2、ZMQ_PUSH
```c++
/*
 * SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
 *
 * SPDX-License-Identifier: MIT
 */
#include <iostream>
#include "pzmq.hpp"
#include <string>
using namespace StackFlows;
int main(int argc, char *argv[]) {
    pzmq zpush_("ipc:///tmp.5000.socket", ZMQ_PUSH);
    zpush_.send_data("nihao");
    return 0;
}
```

3、ZMQ_PUB
```c++
/*
 * SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
 *
 * SPDX-License-Identifier: MIT
 */
#include <iostream>
#include "pzmq.hpp"
#include <string>
using namespace StackFlows;
int main(int argc, char *argv[]) {
    pzmq zpush_("ipc:///tmp.5001.socket", ZMQ_PUB);
    zpush_.send_data("nihao");
    return 0;
}
```

4、ZMQ_SUB
```c++
/*
 * SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
 *
 * SPDX-License-Identifier: MIT
 */
#include <iostream>
#include "pzmq.hpp"
#include <string>
using namespace StackFlows;
void sub_msg(const std::string &raw_msg){
    std::cout << raw_msg << std::endl;
}
int main(int argc, char *argv[]) {
    pzmq zpull_("ipc:///tmp.5001.socket", ZMQ_SUB, sub_msg);
    while(1) {
        sleep(1);
    }
    return 0;
}
```

4、ZMQ_RPC_FUN
```c++
/*
 * SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
 *
 * SPDX-License-Identifier: MIT
 */
#include <iostream>
#include "pzmq.hpp"
#include <string>
using namespace StackFlows;
std::string fun1_(const std::string &raw_msg){
    std::cout << raw_msg << std::endl;
    return std::string("nihao");
}
std::string fun2_(const std::string &raw_msg){
    std::cout << raw_msg << std::endl;
    return std::string("hello");
}
int main(int argc, char *argv[]) {
    pzmq _rpc("test");
    _rpc.register_rpc_action("fun1", fun1_);
    _rpc.register_rpc_action("fun2", fun2_);
    while(1) {
        sleep(1);
    }
    return 0;
}
```

5、ZMQ_RPC_CALL
```c++
/*
 * SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
 *
 * SPDX-License-Identifier: MIT
 */
#include <iostream>
#include "pzmq.hpp"
#include <string>
using namespace StackFlows;
std::string fun1_(const std::string &raw_msg){
    return std::string("nihao");
}
std::string fun2_(const std::string &raw_msg){
    return std::string("hello");
}
int main(int argc, char *argv[]) {
    pzmq _rpc("test");
    _rpc.call_rpc_action("fun1", "call fun1_", [](const std::string &raw_msg){std::cout << raw_msg << std::endl;});
    _rpc.call_rpc_action("fun2", "call fun2_", [](const std::string &raw_msg){std::cout << raw_msg << std::endl;});
    return 0;
}
```

## StackFlow 主体
StackFlow 封装了 pzmq 和 eventpp，为加速单元提供基础的 RPC 函数、异步处理和信道建立。  
StackFlow 提供基本的七个 RPC 函数，用于 StackFlow json 协议的基础功能调用。  
- setup：单元配置函数，是每个单元必须实现的函数。
- pause：暂停单元函数。
- work：单元开始工作函数。
- exit：单元退出函数，是每个单元必须实现的函数。
- link：链接单元上级输出函数，用于构建消息通信链。
- unlink：解除上级输出函数，不在接收上级的消息。
- taskinfo：获取单元运行信息。

StackFlow 提供了简便 API 方便单元使用：
- unit_call: 单元 RPC 调用函数，调用其他单元的 RPC 函数。
- sys_sql_select: sys 单元的简单键值数据库查寻函数。
- sys_sql_set: sys 单元的简单键值数据库键值设置函数。
- sys_sql_unset: sys 单元的简单键值数据库删除键值函数。
- repeat_event: 异步的定时重复执行函数。
- send: 发送用户消息函数。
- sys_register_unit: 单元注册函数，一般情况不需要调用。
- sys_release_unit: 单元释放函数，一般情况不需要调用。

llm_channel_obj 封装了单元所需的通信函数，一份配置对应一个 llm_channel_obj 对象。  
llm_channel_obj 提供了通信简便 API 方便单元使用：
- subscriber_work_id: 订阅上级 work_id 单元的 pub 输出。
- stop_subscriber_work_id：取消订阅 work_id 。
- subscriber： 订阅 zmq url 的 pub 输出。
- stop_subscriber： 取消订阅 zmq_url 。
- send：将本单元的消息通过 pub 发送出去。

### 基本使用示例：
``` c++
/*
 * SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
 *
 * SPDX-License-Identifier: MIT
 */
#include "StackFlow.h"
#include <signal.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <fstream>
#include <stdexcept>
#include <iostream>
using namespace StackFlows;
int main_exit_flage = 0;
static void __sigint(int iSigNo) {
    main_exit_flage = 1;
}
typedef std::function<void(const std::string &data, bool finish)> task_callback_t;
class llm_task {
   private:
   public:
    std::string model_;
    std::string response_format_;
    std::vector<std::string> inputs_;
    task_callback_t out_callback_;
    bool enoutput_;
    bool enstream_;

    void set_output(task_callback_t out_callback) {
        out_callback_ = out_callback;
    }

    bool parse_config(const nlohmann::json &config_body) {
        try {
            model_           = config_body.at("model");
            response_format_ = config_body.at("response_format");
            enoutput_        = config_body.at("enoutput");
            if (config_body.contains("input")) {
                if (config_body["input"].is_string()) {
                    inputs_.push_back(config_body["input"].get<std::string>());
                } else if (config_body["input"].is_array()) {
                    for (auto _in : config_body["input"]) {
                        inputs_.push_back(_in.get<std::string>());
                    }
                }
            }
        } catch (...) {
            return true;
        }
        enstream_ = (response_format_.find("stream") != std::string::npos);
        return false;
    }

    int load_model(const nlohmann::json &config_body) {
        if (parse_config(config_body)) {
            return -1;
        }
        return 0;
    }

    void inference(const std::string &msg) {
        std::cout << msg << std::endl;
        if (out_callback_) out_callback_(std::string("hello"), true);
    }

    llm_task(const std::string &workid) {
    }

    ~llm_task() {
    }
};

class llm_llm : public StackFlow {
   private:
    int task_count_;
    std::unordered_map<int, std::shared_ptr<llm_task>> llm_task_;

   public:
    llm_llm() : StackFlow("test") {
        task_count_ = 1;
    }

    void task_output(const std::shared_ptr<llm_task> llm_task_obj, const std::shared_ptr<llm_channel_obj> llm_channel,
                     const std::string &data, bool finish) {
        if (llm_channel->enstream_) {
            static int count = 0;
            nlohmann::json data_body;
            data_body["index"] = count++;
            data_body["delta"] = data;
            if (!finish)
                data_body["delta"] = data;
            else
                data_body["delta"] = std::string("");
            data_body["finish"] = finish;
            if (finish) count = 0;
            llm_channel->send(llm_task_obj->response_format_, data_body, LLM_NO_ERROR);
        } else if (finish) {
            llm_channel->send(llm_task_obj->response_format_, data, LLM_NO_ERROR);
        }
    }

    void task_user_data(const std::shared_ptr<llm_task> llm_task_obj,
                        const std::shared_ptr<llm_channel_obj> llm_channel, const std::string &object,
                        const std::string &data) {
        const std::string *next_data = &data;
        int ret;
        std::string tmp_msg1;
        if (object.find("stream") != std::string::npos) {
            static std::unordered_map<int, std::string> stream_buff;
            if (decode_stream(data, tmp_msg1, stream_buff)) return;
            next_data = &tmp_msg1;
        }
        std::string tmp_msg2;
        if (object.find("base64") != std::string::npos) {
            ret = decode_base64((*next_data), tmp_msg2);
            if (!ret) {
                return;
            }
            next_data = &tmp_msg2;
        }
        llm_task_obj->inference((*next_data));
    }

    int setup(const std::string &work_id, const std::string &object, const std::string &data) override {
        nlohmann::json error_body;
        if ((llm_task_channel_.size() - 1) == task_count_) {
            error_body["code"]    = -21;
            error_body["message"] = "task full";
            send("None", "None", error_body, unit_name_);
            return -1;
        }
        int work_id_num   = sample_get_work_id_num(work_id);
        auto llm_channel  = get_channel(work_id);
        auto llm_task_obj = std::make_shared<llm_task>(work_id);
        nlohmann::json config_body;
        try {
            config_body = nlohmann::json::parse(data);
        } catch (...) {
            error_body["code"]    = -2;
            error_body["message"] = "json format error.";
            send("None", "None", error_body, unit_name_);
            return -2;
        }
        int ret = llm_task_obj->load_model(config_body);
        if (ret == 0) {
            llm_channel->set_output(llm_task_obj->enoutput_);
            llm_channel->set_stream(llm_task_obj->enstream_);
            llm_task_obj->set_output(std::bind(&llm_llm::task_output, this, llm_task_obj, llm_channel,
                                               std::placeholders::_1, std::placeholders::_2));
            llm_channel->subscriber_work_id("", std::bind(&llm_llm::task_user_data, this, llm_task_obj, llm_channel,
                                                          std::placeholders::_1, std::placeholders::_2));
            llm_task_[work_id_num] = llm_task_obj;
            send("None", "None", LLM_NO_ERROR, work_id);
            return 0;
        } else {
            error_body["code"]    = -5;
            error_body["message"] = "Model loading failed.";
            send("None", "None", error_body, unit_name_);
            return -1;
        }
    }

    void taskinfo(const std::string &work_id, const std::string &object, const std::string &data) override {
        nlohmann::json req_body;
        int work_id_num = sample_get_work_id_num(work_id);
        if (WORK_ID_NONE == work_id_num) {
            std::vector<std::string> task_list;
            std::transform(llm_task_channel_.begin(), llm_task_channel_.end(), std::back_inserter(task_list),
                           [](const auto task_channel) { return task_channel.second->work_id_; });
            req_body = task_list;
            send("llm.tasklist", req_body, LLM_NO_ERROR, work_id);
        } else {
            if (llm_task_.find(work_id_num) == llm_task_.end()) {
                req_body["code"]    = -6;
                req_body["message"] = "Unit Does Not Exist";
                send("None", "None", req_body, work_id);
                return;
            }
            auto llm_task_obj           = llm_task_[work_id_num];
            req_body["model"]           = llm_task_obj->model_;
            req_body["response_format"] = llm_task_obj->response_format_;
            req_body["enoutput"]        = llm_task_obj->enoutput_;
            req_body["inputs_"]         = llm_task_obj->inputs_;
            send("llm.taskinfo", req_body, LLM_NO_ERROR, work_id);
        }
    }

    int exit(const std::string &work_id, const std::string &object, const std::string &data) override {
        nlohmann::json error_body;
        int work_id_num = sample_get_work_id_num(work_id);
        if (llm_task_.find(work_id_num) == llm_task_.end()) {
            error_body["code"]    = -6;
            error_body["message"] = "Unit Does Not Exist";
            send("None", "None", error_body, work_id);
            return -1;
        }
        auto llm_channel = get_channel(work_id_num);
        llm_channel->stop_subscriber("");
        llm_task_.erase(work_id_num);
        send("None", "None", LLM_NO_ERROR, work_id);
        return 0;
    }

    ~llm_llm() {
        while (1) {
            auto iteam = llm_task_.begin();
            if (iteam == llm_task_.end()) {
                break;
            }
            iteam->second.reset();
            llm_task_.erase(iteam->first);
        }
    }
};

int main(int argc, char *argv[]) {
    signal(SIGTERM, __sigint);
    signal(SIGINT, __sigint);
    mkdir("/tmp/llm", 0777);
    llm_llm llm;
    while (!main_exit_flage) {
        sleep(1);
    }
    llm.llm_firework_exit();
    return 0;
}
```

## StackFlowUtil
提供一些简便使用的函数：
- sample_json_str_get: 简单的读取 json 内的键值函数，用于在不解析 json 对象的情况下快速读取 json 键值。
- sample_get_work_id_num： 从 work_id 字符串中读取数字索引。
- sample_get_work_id_name： 从 work_id 字符串中读取单元名。
- sample_get_work_id： 用于合成 work_id 字符串。
- sample_escapeString：简单的对字符串中的转义字符进行编码。
- sample_unescapeString：简单的对字符串中的转义字符串进行解码。
- decode_stream：解析流式数据流。
- decode_base64：解码 base64 。
- encode_base64：编码 base64 。