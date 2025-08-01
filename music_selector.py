import os
import random

def select_music(mood):
    folder = os.path.join("music", mood.lower())
    if not os.path.exists(folder):
        return None
    mp3s = [f for f in os.listdir(folder) if f.endswith(".mp3")]
    if not mp3s:
        return None
    return os.path.join(folder, random.choice(mp3s))
