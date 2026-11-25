#!/usr/bin/env python3
# Generates the Egyptian-Arabic voiceover clips (edge-tts), measures each line,
# and derives per-scene on-screen durations. The clips are placed into the final
# audio later (assemble_audio.py) at the scenes' REAL recorded timings.
import asyncio, json, os
import edge_tts
from pydub import AudioSegment

os.makedirs('out', exist_ok=True)
cfg = json.load(open('narration.json', encoding='utf-8'))
voice = cfg['voice']
scenes = cfg['scenes']

LEADIN = 600    # ms of quiet before each line
TAIL   = 700    # ms of quiet after each line
MIN    = 3800   # ms minimum a scene stays on screen


async def synth(text, path):
    await edge_tts.Communicate(text, voice, rate="-4%").save(path)


durations = []
for i, sc in enumerate(scenes):
    mp3 = f'out/vo_{i+1}.mp3'
    asyncio.run(synth(sc['text'], mp3))
    d = len(AudioSegment.from_file(mp3))
    scene_dur = max(LEADIN + d + TAIL, MIN)
    durations.append(scene_dur)
    print(f'scene {i+1} ({sc["id"]}): voice={d}ms  scene={scene_dur}ms')

json.dump(durations, open('durations.json', 'w'))
print('total scene time =', sum(durations), 'ms')
