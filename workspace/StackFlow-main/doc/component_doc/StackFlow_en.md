# StackFlow
StackFlow is a communication framework developed by M5STACK for AI accelerated computing, mainly running on embedded Linux platforms, with [zmq](https://zeromq.org/) providing the underlying communication services.  
StackFlow primarily offers three functions: first, remote RPC calls for function invocation between units; second, message communication, providing standard message stream services for better context integration; and third, resource allocation, mainly to avoid communication address conflicts between related units and temporary data storage.  
![](../../assets/image/StackFlow_frame.png)

## pzmq
The zmq API is repackaged to make the invocation of ZMQ_PUB, ZMQ_SUB, ZMQ_PUSH, and ZMQ_PULL simpler and more convenient, using asynchronous callback methods to provide message reception functionality.  
On the basis of ZMQ_REP and ZMQ_REQ, simple RPC functionality is encapsulated to provide RPC services.  

### Related Examples
1. ZMQ_PULL
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

2. ZMQ_PUSH
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

3. ZMQ_PUB
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

4. ZMQ_SUB
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

4. ZMQ_RPC_FUN
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

5. ZMQ_RPC_CALL
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

## StackFlow Main Body
StackFlow encapsulates pzmq and eventpp, providing basic RPC functions, asynchronous processing, and channel establishment for accelerated units.  
StackFlow provides seven basic RPC functions for basic function calls of the StackFlow JSON protocol.  
- setup: Unit configuration function, a function that each unit must implement.
- pause: Suspend unit function.
- work: Unit start work function.
- exit: Unit exit function, a function that each unit must implement.
- link: Link to the upstream output function, used to build a message communication chain.
- unlink: Unlink from the upstream output function, stop receiving messages from the upstream.
- taskinfo: Get unit running information.

StackFlow provides convenient APIs for unit usage:
- unit_call: Unit RPC call function, to call RPC functions of other units.
- sys_sql_select: sys unit simple key-value database query function.
- sys_sql_set: sys unit simple key-value database setting function.
- sys_sql_unset: sys unit simple key-value database deletion function.
- repeat_event: Asynchronous periodic execution function.
- send: Send user message function.
- sys_register_unit: Unit registration function, generally not needed to be called.
- sys_release_unit: Unit release function, generally not needed to be called.

llm_channel_obj encapsulates the communication functions required by the unit, with one configuration corresponding to one llm_channel_obj object.  
llm_channel_obj provides convenient communication APIs for unit usage:
- subscriber_work_id: Subscribe to the pub output of the upstream work_id unit.
- stop_subscriber_work_id: Unsubscribe from work_id.
- subscriber: Subscribe to the pub output of the zmq URL.
- stop_subscriber: Unsubscribe from zmq_url.
- send: Send messages of this unit through pub.

### Basic Usage Example:
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
Provide some simple and easy-to-use functions:
- sample_json_str_get: Simple function to read key values inside a JSON, used to quickly read JSON keys without parsing the JSON object.
- sample_get_work_id_num: Read the numeric index from the work_id string.
- sample_get_work_id_name: Read the unit name from the work_id string.
- sample_get_work_id: Used to synthesize the work_id string.
- sample_escapeString: Simple encoding of escape characters in a string.
- sample_unescapeString: Simple decoding of escape strings in a string.
- decode_stream: Parse streaming data flow.
- decode_base64: Decode base64.
- encode_base64: Encode base64.