import pyttsx3
from dotenv import load_dotenv
load_dotenv()
import openai
import os
import json
import re
import random
import uuid  # 🔑 Used to generate unique IDs

openai.api_key = os.environ.get("OPENAI_API_KEY")  # ✅ safer than hardcoding

class MusicPlayer:
    def __init__(self, songs):
        self.autoplay_genre = None
        self.library = songs
        self.user_queue = []
        self.autoplay_queue = []
        self.current_song = None
        self.last_manual_song = None
        self.played_songs = set()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def play_song(self, song):
        self.current_song = song
        self.played_songs.add(song.get('id', song['title']))
        self.autoplay_genre = song['genre']
        print(f"Now playing: {song['title']}")
        self.speak(f"Now playing {song['title']} in {song['language']}")
        self.autoplay_queue = self.generate_autoplay(song)

    def add_to_queue(self, song):
        print(f"Added to next: {song['title']}")
        self.user_queue.append(song)
        self.last_manual_song = song

    def generate_autoplay(self, seed_song):
        filtered = [
            s for s in self.library
            if s['genre'] == seed_song['genre']
            and s.get('id', s['title']) not in self.played_songs
        ]
        if not filtered:
            filtered = [
                s for s in self.library
                if s['genre'] == seed_song['genre']
                and s.get('id', s['title']) != seed_song.get('id', seed_song['title'])
            ]
        return filtered

    def next_song(self):
        if self.user_queue:
            next_s = self.user_queue.pop(0)
            self.play_song(next_s)
        elif self.autoplay_queue:
            next_s = self.autoplay_queue.pop(0)
            self.play_song(next_s)
        else:
            print("End of queue.")

    def get_gpt_recommendations(self, prompt):
        print(f"Simulating GPT for prompt: '{prompt}'")

        vibe = prompt.lower()

        # Curated song pool with tags
        song_pool = [
            {"title": "Velvet Rain", "genre": "jazz", "language": "french", "tags": ["romantic", "sad", "slow"]},
            {"title": "Cyber Drive", "genre": "electronic", "language": "english", "tags": ["party", "dance", "hype"]},
            {"title": "Golden Hour", "genre": "pop", "language": "english", "tags": ["romantic", "happy", "soft"]},
            {"title": "Ocean Eyes", "genre": "ambient", "language": "english", "tags": ["chill", "study", "relax"]},
            {"title": "Nostalgic Nights", "genre": "classic", "language": "spanish", "tags": ["nostalgic", "sad", "romantic"]},
            {"title": "Firepulse", "genre": "rock", "language": "english", "tags": ["hype", "intense", "workout"]},
            {"title": "Cloud Waltz", "genre": "instrumental", "language": "none", "tags": ["calm", "chill", "study"]},
            {"title": "Twilight Drift", "genre": "lofi", "language": "japanese", "tags": ["study", "focus", "chill"]}
        ]

        filtered = [song for song in song_pool if any(tag in vibe for tag in song["tags"])]
        if not filtered:
            filtered = song_pool

        selected = random.sample(filtered, min(3, len(filtered)))
        for song in selected:
            song["id"] = str(uuid.uuid4())  # Assign unique ID

        return selected
