#!/usr/bin/env python3
# Generates the Egyptian-Arabic voiceover (edge-tts), measures each line,
# derives per-scene durations, and builds the core narration track.
import asyncio, json, os
import edge_tts
from pydub import AudioSegment

os.makedirs('out', exist_ok=True)
cfg = json.load(open('narration.json', encoding='utf-8'))
voice = cfg['voice']
scenes = cfg['scenes']

LEADIN = 600    # ms of quiet before each line (scene appears, then voice starts)
TAIL   = 700    # ms of quiet after each line
MIN    = 3800   # ms minimum a scene stays on screen


async def synth(text, path):
    await edge_tts.Communicate(text, voice, rate="-4%").save(path)


durations = []
narration = AudioSegment.silent(duration=0)
for i, sc in enumerate(scenes):
    mp3 = f'out/vo_{i+1}.mp3'
    asyncio.run(synth(sc['text'], mp3))
    clip = AudioSegment.from_file(mp3)
    d = len(clip)
    scene_dur = max(LEADIN + d + TAIL, MIN)
    tail = scene_dur - LEADIN - d
    durations.append(scene_dur)
    narration += AudioSegment.silent(LEADIN) + clip + AudioSegment.silent(tail)
    print(f'scene {i+1} ({sc["id"]}): voice={d}ms  scene={scene_dur}ms')

narration = narration.set_frame_rate(44100).set_channels(2)
narration.export('out/narration_core.wav', format='wav')
json.dump(durations, open('durations.json', 'w'))
print('total scene time =', sum(durations), 'ms')
