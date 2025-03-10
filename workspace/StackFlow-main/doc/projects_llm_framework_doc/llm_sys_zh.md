# llm-sys
StackFlow 的基本服务单元，对外提供串口和 TCP 外部信道和一部分系统功能服务，对内进行端口资源分配，和一个简单的内存数据库。

## 外部 API
- sys.ping：测试是否能够和 LLM 进行通信。
- sys.lsmode：过去系统中存在的模型。
- sys.bashexec：执行 bash 命令。
- sys.hwinfo：获取 LLM 板载 cpu、内存、温度参数。
- sys.uartsetup：设置串口参数，单次生效。
- sys.reset：复位整个 LLM 框架的应用程序。
- sys.reboot：重启系统。
- sys.version：获取 LLM 框架程序版本。

## 内部 API：
- sql_select：查寻小型内存 KV 数据库键值。
- register_unit：注册单元。
- release_unit：释放单元。
- sql_set：设定小型内存 KV 数据库键值。
- sql_unset：删除小型内存 KV 数据库键值。

