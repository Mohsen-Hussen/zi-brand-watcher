#!/usr/bin/env python3
# Builds the narration track aligned to the ACTUAL recorded scene timings, and
# computes where the visible content ends so the video can be trimmed to a tight
# ending (no long frozen outro hold).
import json, subprocess
from pydub import AudioSegment

LEADIN = 600       # ms after a scene appears before its voice starts
TAIL_HOLD = 2200   # ms to hold after the last scene's content before the video ends

timeline = json.load(open('out/timeline.json'))   # ms from recording start per scene
durations = json.load(open('durations.json'))      # on-screen ms per scene

dur = subprocess.check_output(
    ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
     '-of', 'csv=p=0', 'out/video.webm']
).decode().strip()
video_ms = int(float(dur) * 1000)

last = max(i for i, t in enumerate(timeline) if t is not None)
content_end = min(video_ms, int(timeline[last]) + int(durations[last]) + TAIL_HOLD)

base = AudioSegment.silent(duration=content_end, frame_rate=44100).set_channels(2)
for i, start in enumerate(timeline):
    if start is None:
        continue
    pos = max(0, int(start) + LEADIN)
    if pos >= content_end:
        continue
    clip = AudioSegment.from_file(f'out/vo_{i+1}.mp3').set_frame_rate(44100).set_channels(2)
    base = base.overlay(clip, position=pos)
    print(f'scene {i+1}: voice placed at {pos} ms')

base.export('out/narration.wav', format='wav')
json.dump({'end_ms': content_end}, open('out/meta.json', 'w'))
print('content_end =', content_end, 'ms  (video was', video_ms, 'ms)')
