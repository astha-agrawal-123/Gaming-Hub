import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import sys

# Get the directory of this script
base_path = os.path.dirname(os.path.abspath(__file__))

# Game information
GAMES = {
    "8 Puzzle": {
        "script": "8 puzzle.py",
        "description": "Slide tiles to arrange them in order",
        "color": "#3498db"
    },
    "Jumping Frog": {
        "script": "frog_game.py",
        "description": "Help the frog jump to safety",
        "color": "#2ecc71"
    },
    "Tic Tac Toe": {
        "script": "tictaktoe.py",
        "description": "Classic X's and O's game",
        "color": "#9b59b6"
    },
    "Water Jug Puzzle": {
        "script": "water_jug.py",
        "description": "Solve the water measurement puzzle",
        "color": "#e74c3c"
    },
    "Maze Game": {
        "script": "maze.py",
        "description": "Navigate through a maze and find the exit",
        "color": "#000000"
    }
}

def launch_game(script_name):
    script_path = os.path.join(base_path, script_name)
    try:
        subprocess.Popen([sys.executable, script_path])
    except Exception as e:
        messagebox.showerror("Launch Error", f"Error launching {script_name}:\n{e}")

class GameButton(tk.Frame):
    def __init__(self, parent, game_name, game_info, command):
        super().__init__(parent, bg="#f5f5f5", padx=10, pady=5)
        self.pack(fill=tk.X, padx=20, pady=5)
        
        self.game_color = game_info["color"]
        
        self.button_frame = tk.Frame(self, bg=self.game_color, padx=2, pady=2)
        self.button_frame.pack(fill=tk.X)
        
        self.content = tk.Frame(self.button_frame, bg="white")
        self.content.pack(fill=tk.X)
        
        self.title_label = tk.Label(self.content, text=game_name, 
                                   font=("Helvetica", 14, "bold"), 
                                   bg="white", fg="#333")
        self.title_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        self.desc_label = tk.Label(self.content, text=game_info["description"], 
                                  font=("Helvetica", 10), 
                                  bg="white", fg="#666")
        self.desc_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.play_btn = tk.Button(self.content, text="▶ Play", 
                                 font=("Helvetica", 10, "bold"),
                                 bg=self.game_color, fg="white",
                                 activebackground=self.lighten_color(self.game_color),
                                 activeforeground="white",
                                 bd=0, padx=15, pady=5,
                                 command=command)
        self.play_btn.pack(anchor="e", padx=10, pady=10)
        
        for widget in [self.content, self.title_label, self.desc_label]:
            widget.bind("<Enter>", self.on_enter)
            widget.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event):
        self.content.config(bg="#f0f0f0")
        self.title_label.config(bg="#f0f0f0")
        self.desc_label.config(bg="#f0f0f0")
    
    def on_leave(self, event):
        self.content.config(bg="white")
        self.title_label.config(bg="white")
        self.desc_label.config(bg="white")
    
    def lighten_color(self, color):
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        factor = 0.2
        r = min(int(r + (255 - r) * factor), 255)
        g = min(int(g + (255 - g) * factor), 255)
        b = min(int(b + (255 - b) * factor), 255)
        return f"#{r:02x}{g:02x}{b:02x}"

class GameHub:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Hub")
        self.root.geometry("800x1200")
        self.root.minsize(450, 500)
        self.root.configure(bg="#f5f5f5")
        self.create_widgets()

    def create_widgets(self):
        header_frame = tk.Frame(self.root, bg="#333")
        header_frame.pack(fill=tk.X)
        title = tk.Label(header_frame, text="🎮 Game Hub", 
                         font=("Helvetica", 24, "bold"), 
                         bg="#333", fg="white", padx=20, pady=20)
        title.pack(side=tk.LEFT)
        
        main_frame = tk.Frame(self.root, bg="#f5f5f5")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(main_frame, bg="#f5f5f5", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.games_frame = tk.Frame(self.canvas, bg="#f5f5f5")
        self.canvas.create_window((0, 0), window=self.games_frame, anchor="nw")

        def on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.games_frame.bind("<Configure>", on_frame_configure)

        def resize_canvas(event):
            self.canvas.itemconfig("all", width=event.width)
        self.canvas.bind("<Configure>", resize_canvas)

        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.canvas.bind_all("<MouseWheel>", on_mousewheel)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

        section_label = tk.Label(self.games_frame, text="Available Games", 
                             font=("Helvetica", 16), 
                             bg="#f5f5f5", fg="#333")
        section_label.pack(anchor="w", padx=20, pady=(10, 15))
        
        for game_name, game_info in GAMES.items():
            GameButton(self.games_frame, game_name, game_info, 
                       command=lambda s=game_info["script"]: launch_game(s))
        
        footer_frame = tk.Frame(self.root, bg="#f5f5f5", pady=15)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        exit_btn = tk.Button(
            footer_frame, text="Exit", width=15, pady=8,
            font=("Helvetica", 12, "bold"),
            bg="#f44336", fg="white",
            activebackground="#e53935",
            activeforeground="white",
            bd=0,
            command=self.root.quit
        )
        exit_btn.pack(pady=10)

        version_label = tk.Label(footer_frame, text="Game Hub v1.1", 
                             font=("Helvetica", 8), 
                             bg="#f5f5f5", fg="#999")
        version_label.pack(pady=(0, 10))

if __name__ == "__main__":
    root = tk.Tk()
    app = GameHub(root)
    root.mainloop()
