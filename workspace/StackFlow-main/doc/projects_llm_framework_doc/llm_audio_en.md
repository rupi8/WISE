# llm-audio
System audio unit for providing system audio playback and recording.

## API
- play: Play audio. This call will interrupt any previously unfinished audio playback.
- queue_play: Queue playback. Add audio to the playback queue.
- play_stop: Stop playback.
- queue_play_stop: Clear the playback queue.
- audio_status: Get the current playback status.
- cap: Start a recording task, can be called repeatedly.
- cap_stop: Stop a recording task, can be called repeatedly. The last call will stop the data output of the recording channel.
- cap_stop_all: Force stop all ongoing recording tasks.
- setup: Configure the working parameters of the recording unit.