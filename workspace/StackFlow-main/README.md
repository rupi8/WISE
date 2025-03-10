# Module-LLM

<div class="product_pic"><img class="pic" src="https://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/docs/products/module/Module%20LLM/4.webp" width="25%">

## Description

**Module LLM** is an integrated offline Large Language Model (LLM) inference module designed for terminal devices that require efficient and intelligent interaction. Whether for smart homes, voice assistants, or industrial control, Module LLM provides a smooth and natural AI experience without relying on the cloud, ensuring privacy and stability. Integrated with the **StackFlow** framework and **Arduino/UiFlow** libraries, smart features can be easily implemented with just a few lines of code.<br>
Powered by the advanced **AX630C** SoC processor, it integrates a 3.2 TOPs high-efficiency NPU with native support for Transformer models, handling complex AI tasks with ease. Equipped with **4GB LPDDR4** memory (1GB available for user applications, 3GB dedicated to hardware acceleration) and **32GB eMMC** storage, it supports parallel loading and sequential inference of multiple models, ensuring smooth multitasking. The main chip's runtime power consumption of approximately 1.5W, making it highly efficient and suitable for long-term operation.<br>
It features a built-in microphone, speaker, TF storage card, **USB OTG**, and RGB status light, meeting diverse application needs with support for voice interaction and data transfer. The module offers flexible expansion: the onboard SD card slot supports cold/hot firmware upgrades, and the **UART** communication interface simplifies connection and debugging, ensuring continuous optimization and expansion of module functionality. The USB port supports master-slave auto-switching, serving as both a debugging port and allowing connection to additional USB devices like cameras. Users can purchase the LLM debugging kit to add a 100 Mbps Ethernet port and kernel serial port, using it as an SBC.<br>
The module is compatible with multiple models and comes pre-installed with the **Qwen2.5-0.5B** language model. It features **KWS** (wake word), **ASR** (speech recognition), **LLM** (large language model), and **TTS** (text-to-speech) functionalities, with support for standalone calls or **pipeline** automatic transfer for convenient development. Future support includes Qwen2.5-1.5B, Llama3.2-1B, and InternVL2-1B models, allowing hot model updates to keep up with community trends and accommodate various complex AI tasks. Vision recognition capabilities include support for CLIP, YoloWorld, and future updates for DepthAnything, SegmentAnything, and other advanced models to enhance intelligent recognition and analysis.<br>
Plug and play with **M5 hosts**, Module LLM offers an easy-to-use AI interaction experience. Users can quickly integrate it into existing smart devices without complex settings, enabling smart functionality and improving device intelligence. This product is suitable for offline voice assistants, text-to-speech conversion, smart home control, interactive robots, and more.



## Product Features

- Offline inference, 3.2T@INT8 precision computing power
- Integrated KWS (wake word), ASR (speech recognition), LLM (large language model), TTS (text-to-speech generation)
- Multi-model parallel processing
- Onboard 32GB eMMC storage and 4GB LPDDR4 memory
- Onboard microphone and speaker
- Serial communication
- SD card firmware upgrade
- Supports ADB debugging
- RGB indicator light
- Built-in Ubuntu system
- Supports OTG functionality
- Compatible with Arduino/UIFlow

> 

## Applications

- Offline voice assistants
- Text-to-speech conversion
- Smart home control
- Interactive robots

## Specifications

| Specification    | Parameter                                                                                   |
| ---------------- | ------------------------------------------------------------------------------------------- |
| Processor SoC    | AX630C@Dual Cortex A53 1.2 GHz <br> MAX.12.8 TOPS @INT4 and 3.2 TOPS @INT8                  |
| Memory           | 4GB LPDDR4 (1GB system memory + 3GB dedicated for hardware acceleration)                    |
| Storage          | 32GB eMMC5.1                                                                                |
| Communication    | Serial communication default baud rate 115200@8N1 (adjustable)                              |
| Microphone       | MSM421A                                                                                     |
| Audio Driver     | AW8737                                                                                      |
| Speaker          | 8Ω@1W, Size:2014 cavity speaker                                                             |
| Built-in Units   | KWS (wake word), ASR (speech recognition), LLM (large language model), TTS (text-to-speech) |
| RGB Light        | 3x RGB LED@2020 driven by LP5562 (status indication)                                        |
| Power            | Idle: 5V@0.5W, Full load: 5V@1.5W                                                           |
| Button           | For entering download mode for firmware upgrade                                             |
| Upgrade Port     | SD card / Type-C port                                                                       |
| Working Temp     | 0-40°C                                                                                      |
| Product Size     | 54x54x13mm                                                                                  |
| Packaging Size   | 133x95x16mm                                                                                 |
| Product Weight   | 17.4g                                                                                       |
| Packaging Weight | 32.0g                                                                                       |


## Related Links

- [AX630C](https://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/docs/products/module/Module%20LLM/AX630C.pdf)

## PinMap

| Module LLM   | RXD | TXD |
| ------------ | --- | --- |
| Core (Basic) | G16 | G17 |
| Core2        | G13 | G14 |
| CoreS3       | G18 | G17 |

>LLM Module Pin Switching| LLM Module has reserved soldering pads for pin switching. In cases of pin multiplexing conflicts, the PCB trace can be cut and reconnected to other sets of pins.

<img alt="module size" src="https://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/docs/products/module/Module%20LLM/03.jpg" width="25%" />

> Taking `CoreS3` as an example, the first column (left green box) is the TX pin for serial communication, where users can choose one out of four options as needed (from top to bottom, the pins are G18, G7, G14, and G10). The default is set to IO18. To switch to a different pin, cut the connection on the solder pad (at the red line) — it’s recommended to use a blade for this — and then connect to one of the three remaining pins below. The second column (right green box) is for RX pin selection, and, as with the TX pin, it also allows a choice of one out of four options.



## Video

- Module LLM product introduction and example showcase  [Module_LLM_Video.mp4](https://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/docs/products/module/Module%20LLM/Module_LLM_Video.mp4)

## AI Benchmark Comparison

<img alt="compare" src="https://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/docs/products/module/Module%20LLM/Benchmark%E5%AF%B9%E6%AF%94.png" width="100%" />