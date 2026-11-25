#!/usr/bin/env python3
# Builds the narration track aligned to the ACTUAL recorded scene timings.
# Each voice clip is overlaid at the real moment its scene appeared on screen,
# which keeps voice and visuals in sync regardless of headless clock drift.
import json, subprocess
from pydub import AudioSegment

LEADIN = 600  # ms after a scene appears before its voice starts

timeline = json.load(open('out/timeline.json'))  # ms from recording start per scene

dur = subprocess.check_output(
    ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
     '-of', 'csv=p=0', 'out/video.webm']
).decode().strip()
video_ms = int(float(dur) * 1000)

base = AudioSegment.silent(duration=video_ms, frame_rate=44100).set_channels(2)
for i, start in enumerate(timeline):
    if start is None:
        print(f'scene {i+1}: no timing captured, skipped')
        continue
    clip = AudioSegment.from_file(f'out/vo_{i+1}.mp3').set_frame_rate(44100).set_channels(2)
    pos = max(0, int(start) + LEADIN)
    base = base.overlay(clip, position=pos)
    print(f'scene {i+1}: voice placed at {pos} ms')

base.export('out/narration.wav', format='wav')
print('narration built; video length =', video_ms, 'ms')
