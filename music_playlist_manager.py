import random
import json
from collections import deque
import os

# --------- Linked List for Playlist -----------
class SongNode:
    def __init__(self, title, artist):
        self.title = title
        self.artist = artist
        self.next = None
        self.prev = None

class Playlist:
    def __init__(self, name="Default"):
        self.name = name
        self.head = None
        self.tail = None
        self.size = 0

    def add_song(self, title, artist):
        node = SongNode(title, artist)
        if not self.head:
            self.head = self.tail = node
        else:
            self.tail.next = node
            node.prev = self.tail
            self.tail = node
        self.size += 1

    def remove_song(self, index):
        if index < 0 or index >= self.size:
            print("Invalid index")
            return
        current = self.head
        for _ in range(index):
            current = current.next
        if current.prev:
            current.prev.next = current.next
        if current.next:
            current.next.prev = current.prev
        if current == self.head:
            self.head = current.next
        if current == self.tail:
            self.tail = current.prev
        self.size -= 1
        print(f"Removed: {current.title} by {current.artist}")

    def list_songs(self):
        current = self.head
        songs = []
        while current:
            songs.append(current)
            current = current.next
        return songs

    def print_playlist(self):
        print(f"\nPlaylist: {self.name}")
        for i, node in enumerate(self.list_songs(), 1):
            print(f"{i}. {node.title} - {node.artist}")
        if self.size == 0:
            print("(empty)")
        print()

# -------- JSON Persistence for all playlists --------------
def save_all_playlists(playlists, filename="playlistsCLI.json"):
    data = {}
    for pl_name, pl in playlists.items():
        data[pl_name] = [{"title": node.title, "artist": node.artist} for node in pl.list_songs()]
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"All playlists saved to {filename}")

def load_all_playlists(filename="playlistsCLI.json"):
    playlists = {}
    if os.path.exists(filename):
        with open(filename, "r") as f:
            data = json.load(f)
        for pl_name, songs in data.items():
            pl = Playlist(pl_name)
            for song in songs:
                pl.add_song(song["title"], song["artist"])
            playlists[pl_name] = pl
        print(f"Loaded {len(playlists)} playlists from {filename}")
    else:
        print("No saved playlists found, starting fresh.")
    return playlists

# ------------- Recursive Shuffle -------------
def recursive_shuffle(song_nodes):
    if len(song_nodes) <= 1:
        return song_nodes.copy()
    idx = random.randint(0, len(song_nodes) - 1)
    chosen = song_nodes[idx]
    remaining = song_nodes[:idx] + song_nodes[idx+1:]
    return [chosen] + recursive_shuffle(remaining)

# -------- Stack & Queue -------------
play_next_queue = deque()
listening_history = []
party_queue = []

# -------- Filtering by artist -------------
def filter_by_artist(playlist, artist_name):
    filtered = [node for node in playlist.list_songs() if node.artist.lower() == artist_name.lower()]
    if not filtered:
        print(f"No songs found for artist '{artist_name}'")
    else:
        print(f"Songs by {artist_name}:")
        for i, node in enumerate(filtered, 1):
            print(f"{i}. {node.title}")
    print()

# ---------- Main Menu ---------------
def main():
    playlists = load_all_playlists()
    if not playlists:
        # create default playlist
        current_playlist = Playlist("playlist1")
        playlists[current_playlist.name] = current_playlist
    else:
        current_playlist = list(playlists.values())[0]

    while True:
        console_width = 60
        print('\n')
        menu_title = "🎶 Music Playlist Manager 🎶"
        border = "-" * console_width

        menu_items = [
            "(1) Show Playlist",
            "(2) Add Song",
            "(3) Remove Song",
            "(4) Filter by Artist",
            "(5) Shuffle Playlist",
            "(6) Queue Song to Play Next",
            "(7) Upvote Song for Party Mode",
            "(8) Play Next (simulate)",
            "(9) Show Listening History",
            "(10) Create New Playlist",
            "(11) Switch Playlist",
            "(12) Save & Exit"
        ]

        # Print header
        print(border)
        print(menu_title.center(console_width))
        print(border)

        # Find the max length for left alignment
        max_len = max(len(item) for item in menu_items)

        for item in menu_items:
            print(item.ljust(max_len).center(console_width))

        print(border)
        choice = input("Enter choice: ".center(console_width)).strip()
        print(border)

        if choice == "1":
            current_playlist.print_playlist()
        elif choice == "2":
            title = input("Song title: ").strip()
            artist = input("Artist: ").strip()
            current_playlist.add_song(title, artist)
            print("Added song!")
        elif choice == "3":
            current_playlist.print_playlist()
            idx = int(input("Song number to remove: ")) - 1
            current_playlist.remove_song(idx)
        elif choice == "4":
            artist = input("Artist name: ").strip()
            filter_by_artist(current_playlist, artist)
        elif choice == "5":
            nodes = current_playlist.list_songs()
            shuffled = recursive_shuffle(nodes)
            current_playlist.head = current_playlist.tail = None
            current_playlist.size = 0
            for node in shuffled:
                current_playlist.add_song(node.title, node.artist)
            print("Playlist shuffled!")
        elif choice == "6":
            current_playlist.print_playlist()
            idx = int(input("Song number to queue next: ")) - 1
            nodes = current_playlist.list_songs()
            if 0 <= idx < len(nodes):
                play_next_queue.append(nodes[idx])
                print(f"Queued {nodes[idx].title} to play next")
            else:
                print("Invalid song number")
        elif choice == "7":
            current_playlist.print_playlist()
            idx = int(input("Song number to upvote for party mode: ")) - 1
            nodes = current_playlist.list_songs()
            if 0 <= idx < len(nodes):
                party_queue.append(nodes[idx])
                print(f"{nodes[idx].title} upvoted!")
            else:
                print("Invalid song number")
        elif choice == "8":
            next_song = None
            if play_next_queue:
                next_song = play_next_queue.popleft()
            elif party_queue:
                next_song = party_queue.pop(0)
            else:
                nodes = current_playlist.list_songs()
                next_song = nodes[0] if nodes else None
            if next_song:
                print(f"Now playing: {next_song.title} - {next_song.artist}")
                listening_history.append(next_song)
            else:
                print("No songs to play")
        elif choice == "9":
            print("Listening History:")
            for i, song in enumerate(reversed(listening_history), 1):
                print(f"{i}. {song.title} - {song.artist}")
        elif choice == "10":
            name = input("New playlist name: ").strip()
            if name in playlists:
                print("Playlist already exists")
            else:
                new_pl = Playlist(name)
                playlists[name] = new_pl
                current_playlist = new_pl
                print(f"Created and switched to playlist '{name}'")
        elif choice == "11":
            print("Available playlists:")
            for i, name in enumerate(playlists.keys(), 1):
                print(f"{i}. {name}")
            idx = int(input("Enter number to switch: ")) - 1
            if 0 <= idx < len(playlists):
                current_playlist = list(playlists.values())[idx]
                print(f"Switched to '{current_playlist.name}'")
            else:
                print("Invalid choice")
        elif choice == "12":
            save_all_playlists(playlists)
            print("Exiting...")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()