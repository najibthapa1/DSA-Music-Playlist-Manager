import os
import random
import json
import pygame
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

# Initialize pygame
pygame.mixer.init()

# ------------------ Data ------------------
playlist_data_file = "playlists.json"
playlists = {}        # {"PlaylistName": [ {"name":..., "path":...}, ... ]}
active_playlist = None
queue = []
history_stack = []

# ------------------ Helpers ------------------
def get_song_name(path):
    return os.path.splitext(os.path.basename(path))[0]

def save_playlists():
    global playlists, active_playlist
    data = {"playlists": playlists, "active_playlist": active_playlist}
    with open(playlist_data_file, "w") as f:
        json.dump(data, f, indent=2)

def load_playlists():
    global playlists, active_playlist
    if os.path.exists(playlist_data_file):
        try:
            with open(playlist_data_file, "r") as f:
                data = json.load(f)
                playlists = data.get("playlists", {})
                active_playlist = data.get("active_playlist")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load playlists: {e}")
    if not playlists:
        playlists["Default"] = []
        active_playlist = "Default"

def update_playlist_box():
    playlist_box.delete(0, tk.END)
    for song in playlists[active_playlist]:
        playlist_box.insert(tk.END, song["name"])
    active_playlist_var.set(active_playlist)

def create_playlist():
    global playlists, active_playlist
    name = simpledialog.askstring("New Playlist", "Enter playlist name:")
    if name:
        if name in playlists:
            messagebox.showwarning("Exists", "Playlist already exists!")
            return
        playlists[name] = []
        active_playlist = name
        update_playlist_box()
        update_playlist_dropdown()
        save_playlists()

def delete_playlist():
    global playlists, active_playlist
    if active_playlist == "Default":
        messagebox.showwarning("Cannot delete", "Cannot delete Default playlist!")
        return
    confirm = messagebox.askyesno("Delete Playlist", f"Delete playlist '{active_playlist}'?")
    if confirm:
        del playlists[active_playlist]
        active_playlist = list(playlists.keys())[0]
        update_playlist_box()
        update_playlist_dropdown()
        save_playlists()

def switch_playlist(event=None):
    global active_playlist
    selection = playlist_dropdown.get()
    if selection:
        active_playlist = selection
        update_playlist_box()
        save_playlists()

# ------------------ Song Operations ------------------
def add_song():
    global playlists
    file_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
    if file_path:
        song = {"name": get_song_name(file_path), "path": file_path}
        playlists[active_playlist].append(song)
        playlist_box.insert(tk.END, song["name"])
        save_playlists()

def delete_song():
    global playlists
    selected = playlist_box.curselection()
    if selected:
        index = selected[0]
        song = playlists[active_playlist].pop(index)
        playlist_box.delete(index)
        save_playlists()
        messagebox.showinfo("Deleted", f"Removed {song['name']}")

# ------------------ Playback ------------------
def play_song():
    selected = playlist_box.curselection()
    if selected:
        index = selected[0]
    else:
        index = 0
    play_index(index)

def play_index(index):
    global playlists, history_stack
    if not playlists[active_playlist]:
        messagebox.showwarning("Empty", "Playlist is empty!")
        return
    song = playlists[active_playlist][index]
    try:
        pygame.mixer.music.load(song["path"])
        pygame.mixer.music.play()
        now_playing_var.set(f"▶ Now Playing: {song['name']}")
        history_stack.append(song)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def stop_song():
    pygame.mixer.music.stop()
    now_playing_var.set("⏹️ Stopped")

def pause_song():
    pygame.mixer.music.pause()
    now_playing_var.set(now_playing_var.get() + " ⏸️")

def resume_song():
    pygame.mixer.music.unpause()
    now_playing_var.set(now_playing_var.get().replace(" ⏸️"," ▶"))

# ------------------ Queue ------------------
def add_to_queue():
    selected = playlist_box.curselection()
    if selected:
        index = selected[0]
        song = playlists[active_playlist][index]
        queue.append(song)
        queue_box.insert(tk.END, song["name"])

def play_next():
    if queue:
        song = queue.pop(0)
        queue_box.delete(0)
        try:
            pygame.mixer.music.load(song["path"])
            pygame.mixer.music.play()
            history_stack.append(song)
            now_playing_var.set(f"▶ Now Playing: {song['name']}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showinfo("Queue Empty", "No songs in queue")

# ------------------ Shuffle (Recursive) ------------------
def recursive_shuffle(songs, shuffled=None):
    if shuffled is None:
        shuffled = []
    if not songs:
        return shuffled
    song = random.choice(songs)
    shuffled.append(song)
    remaining = [s for s in songs if s != song]
    return recursive_shuffle(remaining, shuffled)

def shuffle_play():
    if not playlists[active_playlist]:
        messagebox.showwarning("Empty", "Playlist is empty!")
        return
    shuffled = recursive_shuffle(playlists[active_playlist])
    for song in shuffled:
        try:
            pygame.mixer.music.load(song["path"])
            pygame.mixer.music.play()
            history_stack.append(song)
            now_playing_var.set(f"▶ Now Playing: {song['name']}")
            break  # play first song only
        except Exception as e:
            messagebox.showerror("Error", str(e))

# ------------------ History ------------------
def show_history():
    history_win = tk.Toplevel(root)
    history_win.title("Listening History")
    for song in history_stack:
        tk.Label(history_win, text=song["name"]).pack()

# ------------------ Volume ------------------
def set_volume(val):
    vol = float(val)/100
    pygame.mixer.music.set_volume(vol)

# ------------------ GUI Setup ------------------
root = tk.Tk()
root.title("🎵 Tkinter Music Player (Multi-Playlist)")
root.geometry("750x400")

# Playlist Frame
playlist_frame = tk.Frame(root)
playlist_frame.pack(side=tk.LEFT, padx=10, pady=10)

tk.Label(playlist_frame, text="Playlist").pack()
playlist_box = tk.Listbox(playlist_frame, width=30, height=15)
playlist_box.pack()

tk.Button(playlist_frame, text="➕ Add Song", command=add_song).pack(pady=2)
tk.Button(playlist_frame, text="🗑️ Delete Song", command=delete_song).pack(pady=2)

# Queue Frame
queue_frame = tk.Frame(root)
queue_frame.pack(side=tk.RIGHT, padx=10, pady=10)

tk.Label(queue_frame, text="Queue").pack()
queue_box = tk.Listbox(queue_frame, width=30, height=15)
queue_box.pack()

tk.Button(queue_frame, text="📌 Add to Queue", command=add_to_queue).pack(pady=2)
tk.Button(queue_frame, text="⏭️ Play Next", command=play_next).pack(pady=2)

# Controls Frame
control_frame = tk.Frame(root)
control_frame.pack(pady=10)

tk.Button(control_frame, text="▶ Play", command=play_song).grid(row=0, column=0, padx=5)
tk.Button(control_frame, text="⏹️ Stop", command=stop_song).grid(row=0, column=1, padx=5)
tk.Button(control_frame, text="⏸️ Pause", command=pause_song).grid(row=0, column=2, padx=5)
tk.Button(control_frame, text="▶ Resume", command=resume_song).grid(row=0, column=3, padx=5)
tk.Button(control_frame, text="🔀 Shuffle Play", command=shuffle_play).grid(row=0, column=4, padx=5)
tk.Button(control_frame, text="📜 History", command=show_history).grid(row=0, column=5, padx=5)

# Volume Slider
volume_frame = tk.Frame(root)
volume_frame.pack(pady=5)
tk.Label(volume_frame, text="Volume").pack(side=tk.LEFT)
volume_slider = tk.Scale(volume_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=set_volume)
volume_slider.set(80)
volume_slider.pack(side=tk.LEFT)

# Now Playing
now_playing_var = tk.StringVar()
now_playing_var.set("No song playing")
tk.Label(root, textvariable=now_playing_var, fg="blue").pack(pady=5)

# Playlist dropdown
playlist_top_frame = tk.Frame(root)
playlist_top_frame.pack(pady=5)
active_playlist_var = tk.StringVar()
playlist_dropdown = ttk.Combobox(playlist_top_frame, textvariable=active_playlist_var)
playlist_dropdown.pack(side=tk.LEFT)
tk.Button(playlist_top_frame, text="➕ Create Playlist", command=create_playlist).pack(side=tk.LEFT, padx=5)
tk.Button(playlist_top_frame, text="🗑️ Delete Playlist", command=delete_playlist).pack(side=tk.LEFT, padx=5)

def update_playlist_dropdown():
    playlist_dropdown['values'] = list(playlists.keys())
    active_playlist_var.set(active_playlist)

playlist_dropdown.bind("<<ComboboxSelected>>", switch_playlist)

# ------------------ Initialize ------------------
load_playlists()
update_playlist_dropdown()
update_playlist_box()

root.mainloop()