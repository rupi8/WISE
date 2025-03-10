# Module-LLM

<div class="product_pic"><img class="pic" src="https://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/docs/products/module/Module%20LLM/4.webp" width="25%">

## 描述

**Module LLM**是一款集成化的离线大语言模型 (LLM) 推理模块，专为需要高效，智能交互的终端设备设计，无论是在智能家居，语音助手，还是在工业控制中，Module LLM 都能为您带来流畅，自然的 AI 体验，无需依赖云端，确保隐私安全与稳定性。集成 **StackFlow** 框架，配合 **Arduino/UiFlow** 库，几行代码就可轻松实现端侧智能。<br>
搭载爱芯 **AX630C** SoC 先进处理器，集成 3.2 TOPs 高能效 NPU，原生支持 Transformer 模型，轻松应对复杂 AI 任务。配备 **4GB LPDDR4** 内存（其中1GB供用户使用，3GB专用于硬件加速）和**32GB eMMC**存储，支持多模型并行加载与串联推理，确保多任务处理流畅无阻。运行功耗仅约 1.5W，远低于同类产品，节能高效，适合长时间运行。<br>
集成麦克风，扬声器，TF存储卡，**USB OTG** 及 RGB状态灯，满足多样化应用需求，轻松实现语音交互与数据传输。灵活扩展：板载 SD 卡槽支持固件冷/热升级，**UART** 通信接口简化连接与调试，确保模块功能持续优化与扩展。USB 口支持主从自动切换，既可以做调试口，也可以外接更多 USB 设备如摄像头。搭配 LLM 调试套件，用于扩展百兆以太网口，及内核串口，作为 SBC 使用。<br>
多模型兼容，出厂预装 **Qwen2.5-0.5B** 大语言模型，内置**KWS**（唤醒词），**ASR**（语音识别），**LLM**（大语言模型）及**TTS**（文本转语音）功能，且支持分开调用或 **pipeline** 自动流转，方便开发。后续将支持Qwen2.5-1.5B、Llama3.2-1B及InternVL2-1B等多种端侧LLM/VLM模型，支持热更新模型，紧跟社区潮流，适应不同复杂度的AI任务；视觉识别能力：支持CLIP、YoloWorld等Open world模型，未来将持续更新DepthAnything、SegmentAnything等先进模型，赋能智能识别与分析；<br>
即插即用，搭配**M5主机**，Module LLM 实现即插即用的AI交互体验。用户无需繁琐设置，即可将其集成到现有智能设备中，快速启用智能化功能，提升设备智能水平。该产品适用于离线语音助手，文本语音转换，智能家居控制，互动机器人等领域。




## 产品特性

- 离线推理,3.2T@INT8精度算力

- 集成KWS（唤醒词），ASR（语音识别），LLM（大语言模型），TTS（文本生成语音）

- 多模型并行

- 板载32GB eMMC存储和4GB LPDDR4内存

- 板载麦克风及扬声器

- 串口通信

- SD卡固件升级

- 支持ADB调试

- RGB提示灯

- 内置ubuntu系统

- 支持OTG功能

- 支持Arduino/UIFlow

  


## 应用

- 离线语音助手
- 文本语音转换
- 智能家居控制
- 互动机器人

## 规格参数

| 规格         | 参数                                                                        |
| ------------ | --------------------------------------------------------------------------- |
| 处理器SoC    | AX630C@Dual Cortex A53 1.2 GHz <br> MAX.12.8 TOPS  @INT4,and 3.2 TOPS @INT8 |
| 内存         | 4GB LPDDR4(1GB系统内存 + 3GB 硬件加速专用内存)                              |
| 存储         | 32GB eMMC5.1                                                                |
| 通信接口     | 串口通信 波特率默认 115200@8N1（可调）                                      |
| 麦克风       | MSM421A                                                                     |
| 音频驱动     | AW8737                                                                      |
| 扬声器       | 8Ω@1W,尺寸:2014 腔体喇叭                                                    |
| 内置功能单元 | KWS（唤醒词），ASR（语音识别），LLM（大语言模型），TTS（文本生成语音）      |
| RGB灯        | 3x RGB LED@2020 由LP5562驱动 (状态指示)                                     |
| 功耗         | 空载：5V@0.5W，满载:5V@1.5W                                                 |
| 按键         | 用于升级固件进入下载模式                                                    |
| 升级接口     | SD卡/Type C口                                                               |
| 工作温度     | 0-40°C                                                                      |
| 产品尺寸     | 54x54x13mm                                                                  |
| 包装尺寸     | 133x95x16mm                                                                 |
| 产品重量     | 17.4g                                                                       |
| 包装重量     | 32.0g                                                                       |

## 相关链接

- [AX630C](https://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/docs/products/module/Module%20LLM/AX630C.pdf)

## PinMap

| Module LLM   | RXD | TXD |
| ------------ | --- | --- |
| Core (Basic) | G16 | G17 |
| Core2        | G13 | G14 |
| CoreS3       | G18 | G17 |

>LLM Module引脚切换| LLM Module预留了引脚切换焊盘, 一些出现引脚复用冲突的情况下, 可以通过切割PCB线路然后跳线连接至其他组引脚。

<img alt="module size" src="https://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/docs/products/module/Module%20LLM/03.jpg" width="25%" />

> 以`CoreS3`为例子，第一列（左绿色框）是串口通讯的TX引脚，用户根据需要四选一，（从上到下分别代表引脚G18 G7 G14 G10）,默认是IO18引脚，如需要切换其他引脚，切断焊盘连接线（红线处）（建议使用刀片切割），然后连接下面三个引脚之间的一个即可；第二列（右绿色框）是RX引脚切换，如上所述，也是四选一操作。



## 视频

- Module LLM 产品介绍以及例子展示 [Module_LLM_Video.mp4](https://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/docs/products/module/Module%20LLM/Module_LLM_Video.mp4)

## AI Benchmark 对比

<img alt="compare" src="https://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/docs/products/module/Module%20LLM/Benchmark%E5%AF%B9%E6%AF%94.png" width="100%" />
