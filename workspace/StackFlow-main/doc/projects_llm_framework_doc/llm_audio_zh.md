# llm-audio
系统音频单元，用于提供系统音频播放和录音。


## API
- play: 播放音频，本次调用会打断上次未播放的完的音频。
- queue_play：队列播放，将音频加入播放队列。
- play_stop：停止播放。
- queue_play_stop：清理播放队列。
- audio_status：当前播放状态。
- cap：开始一个录音任务，可重复调用。
- cap_stop：停止一个录音任务，可重复调用，最后一个调用会停止录音信道的数据输出。
- cap_stop_all：强制停止所有开启的录音任务。
- setup: 配置录音单元的工作参数。


