import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from player import MusicPlayer
# Load songs
with open("song_data.json") as f:
    songs = json.load(f)

player = MusicPlayer(songs)
queue_songs = []  # will hold merged user + autoplay queue
index_to_song = {}  # tracks only the rows that are actual songs

# --- Tkinter GUI Setup ---
root = tk.Tk()
root.title("🎵 Smart Autoplay Player")
root.geometry("600x720")
root.configure(bg="#f7f7fa")

# --- Fonts and Styles ---
HEADER_FONT = ("Helvetica", 16, "bold")
LABEL_FONT = ("Helvetica", 12)
BUTTON_FONT = ("Helvetica", 11)
BOX_WIDTH = 60

# --- Now Playing ---
now_playing_label = tk.Label(root, text="📻 Now Playing: None", font=HEADER_FONT, bg="#f7f7fa")
now_playing_label.pack(pady=(20, 10))
autoplay_genre_label = tk.Label(root, text="🎵 Now Autoplaying From: —", font=("Helvetica", 10, "italic"), fg="gray", bg="#f7f7fa")
autoplay_genre_label.pack()


# --- Queue Section ---
queue_label = tk.Label(root, text="🎧 Upcoming Queue", font=LABEL_FONT, bg="#f7f7fa")
queue_label.pack()

queue_box = tk.Listbox(root, height=6, width=BOX_WIDTH, font=("Helvetica", 10), bd=2, relief="groove")
queue_box.pack(pady=5)


# --- Library Header ---
library_label = tk.Label(root, text="🎶 Song Library", font=LABEL_FONT, bg="#f7f7fa")
library_label.pack(pady=(20, 5))

song_listbox = tk.Listbox(root, height=10, width=BOX_WIDTH, font=("Helvetica", 10), bd=2, relief="groove")
song_listbox.pack(pady=5)

for idx, song in enumerate(songs):
    song_listbox.insert(tk.END, f"{song['title']} ({song['genre']}, {song['language']})")

# --- Control Buttons ---
def update_ui():
    global index_to_song
    index_to_song.clear()

    now = player.current_song["title"] if player.current_song else "None"
    now_playing_label.config(text=f"📻 Now Playing: {now}")

    genre = player.autoplay_genre.capitalize() if player.autoplay_genre else "—"
    autoplay_genre_label.config(text=f"🎵 Now Autoplaying From: {genre}")

    queue_box.delete(0, tk.END)

    # ▶ Continue Playing section
    if player.user_queue:
        queue_box.insert(tk.END, "▶ Continue Playing")
        queue_box.itemconfig(tk.END, {'fg': '#000'})
        for song in player.user_queue:
            idx = queue_box.size()
            queue_box.insert(tk.END, f"   {song['title']} — {song['genre'].capitalize()}")
            index_to_song[idx] = song  # map to song

    # Divider
    if player.user_queue and player.autoplay_queue:
        queue_box.insert(tk.END, "──────────────")
        queue_box.itemconfig(tk.END, {'fg': '#aaa'})

    # ♾ Autoplay section
    if player.autoplay_queue:
        queue_box.insert(tk.END, "♾ Autoplay (Similar music will keep playing)")
        queue_box.itemconfig(tk.END, {'fg': '#555'})
        for song in player.autoplay_queue:
            idx = queue_box.size()
            queue_box.insert(tk.END, f"   {song['title']} — {song['genre'].capitalize()}")
            index_to_song[idx] = song  # map to song

def play_selected():
    try:
        index = song_listbox.curselection()[0]
        player.play_song(songs[index])
        update_ui()
    except IndexError:
        messagebox.showerror("Error", "No song selected!")

def add_to_queue():
    try:
        index = song_listbox.curselection()[0]
        player.add_to_queue(songs[index])
        update_ui()
    except IndexError:
        messagebox.showerror("Error", "No song selected!")

def next_song():
    player.next_song()
    update_ui()

def surprise_me():
    user_input = simpledialog.askstring("🎧 AI DJ", "What kind of vibe are you feeling?")
    if user_input:
        suggestions = player.get_gpt_recommendations(user_input)
        for song in suggestions:
            print(f"AI added: {song['title']} ({song['genre']}, {song['language']})")
            player.add_to_queue(song)
        player.next_song()
        update_ui()

btn_frame = tk.Frame(root, bg="#f7f7fa")
btn_frame.pack(pady=20)

tk.Button(btn_frame, text="▶ Play", font=BUTTON_FONT, width=12, bg="#4CAF50", fg="white", command=play_selected).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="➕ Add to Queue", font=BUTTON_FONT, width=14, bg="#2196F3", fg="white", command=add_to_queue).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="⏭ Next", font=BUTTON_FONT, width=12, bg="#FF9800", fg="white", command=next_song).grid(row=0, column=2, padx=5)
tk.Button(btn_frame, text="🎧 Surprise Me (AI)", font=BUTTON_FONT, width=24, bg="#9C27B0", fg="white", command=surprise_me).grid(row=1, column=0, columnspan=3, pady=10)

update_ui()

def on_queue_click(event):
    selection = queue_box.curselection()
    if not selection:
        return

    index = selection[0]
    if index in index_to_song:
        song = index_to_song[index]
        player.play_song(song)
        update_ui()

queue_box.bind("<Double-Button-1>", on_queue_click)

update_ui()

root.mainloop()
