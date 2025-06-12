import tkinter as tk
from tkinter import messagebox, PhotoImage
import random
import heapq
import json
import os
from typing import List, Tuple, Dict, Any, Optional

class PuzzleGame:
    """An 8-Puzzle game implementation with A* search algorithm for solving."""
    
    # Define a clean, minimal color scheme
    COLORS = {
        "background": "#f8f9fa",
        "frame": "#ffffff",
        "header": "#4a5568",
        "header_text": "#ffffff",
        "tile": "#718096",
        "tile_text": "#ffffff",
        "empty": "#f1f5f9",
        "button_hint": "#a3bffa",
        "button_solve": "#9ae6b4",
        "button_shuffle": "#fbd38d",
        "hint_highlight": "#fc8181",
        "start_button": "#4299e1",
        "start_button_text": "#ffffff",
        "highscore": "#2c7a7b"
    }
    
    TILE_SIZE = 70
    FONT_TITLE = ("Helvetica", 20, "bold")
    FONT_TILE = ("Helvetica", 22, "bold")
    FONT_SCORE = ("Helvetica", 14)
    FONT_BUTTON = ("Helvetica", 11)
    FONT_HIGHSCORE = ("Helvetica", 12, "bold")
    FONT_START = ("Helvetica", 16, "bold")
    
    SCORES_FILE = "puzzle_scores.json"

    def __init__(self, root: tk.Tk) -> None:
        """Initialize the puzzle game with the given root window."""
        self.root = root
        self.root.title("8-Puzzle Game")
        self.root.configure(bg=self.COLORS["background"])
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        
        # Set goal state
        self.goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        self.state = None
        self.buttons = []
        self.score = 0
        self.streak = 1
        self.high_scores = self.load_high_scores()
        
        # Create the start page
        self.create_start_page()

    def load_high_scores(self) -> Dict[str, int]:
        """Load high scores from file or create new if not exists."""
        if os.path.exists(self.SCORES_FILE):
            try:
                with open(self.SCORES_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {"highest": 0, "total_games": 0, "total_score": 0}
        else:
            return {"highest": 0, "total_games": 0, "total_score": 0}
    
    def save_high_scores(self) -> None:
        """Save high scores to file."""
        with open(self.SCORES_FILE, 'w') as f:
            json.dump(self.high_scores, f)

    def create_start_page(self) -> None:
        """Create the game's start page."""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main container
        container = tk.Frame(self.root, bg=self.COLORS["background"], padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Create game frame
        start_frame = tk.Frame(container, bg=self.COLORS["frame"], padx=20, pady=20,
                              relief=tk.RAISED, borderwidth=1)
        start_frame.pack(fill=tk.BOTH, expand=True)
        
        # Game title
        header_frame = tk.Frame(start_frame, bg=self.COLORS["header"], padx=20, pady=10)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="8-Puzzle Game", 
                             font=("Helvetica", 24, "bold"), bg=self.COLORS["header"], 
                             fg=self.COLORS["header_text"])
        title_label.pack()
        
        # Game description
        description = (
            "Arrange the tiles in order from 1 to 8\n"
            "by sliding them into the empty space.\n\n"
            "Use the hint button if you get stuck!"
        )
        
        desc_label = tk.Label(start_frame, text=description, 
                             font=("Helvetica", 12), bg=self.COLORS["frame"],
                             justify=tk.CENTER, pady=10)
        desc_label.pack(pady=10)
        
        # High scores display
        highscore_frame = tk.Frame(start_frame, bg=self.COLORS["frame"], padx=10, pady=10)
        highscore_frame.pack(fill=tk.X, pady=10)
        
        highest_score = self.high_scores.get("highest", 0)
        total_games = self.high_scores.get("total_games", 0)
        avg_score = 0
        if total_games > 0:
            avg_score = round(self.high_scores.get("total_score", 0) / total_games)
        
        tk.Label(highscore_frame, text="HIGH SCORE", font=self.FONT_HIGHSCORE, 
                fg=self.COLORS["highscore"], bg=self.COLORS["frame"]).pack()
        
        tk.Label(highscore_frame, text=str(highest_score), font=("Helvetica", 18, "bold"), 
                fg=self.COLORS["highscore"], bg=self.COLORS["frame"]).pack()
        
        stats_frame = tk.Frame(highscore_frame, bg=self.COLORS["frame"])
        stats_frame.pack(pady=5)
        
        tk.Label(stats_frame, text=f"Games Played: {total_games}",
                font=("Helvetica", 10), bg=self.COLORS["frame"]).pack()
        
        if total_games > 0:
            tk.Label(stats_frame, text=f"Average Score: {avg_score}",
                    font=("Helvetica", 10), bg=self.COLORS["frame"]).pack()
        
        # Start button
        start_btn = tk.Button(start_frame, text="Start Game", command=self.start_game,
                            font=self.FONT_START, bg=self.COLORS["start_button"],
                            fg=self.COLORS["start_button_text"], padx=20, pady=10,
                            relief=tk.RAISED, borderwidth=2)
        start_btn.pack(pady=20)

    def start_game(self) -> None:
        """Start a new game."""
        self.state = self.generate_solvable_puzzle()
        self.score = 0
        self.streak = 1
        self.create_game_ui()

    def is_solvable(self, puzzle: List[List[int]]) -> bool:
        """Check if the given puzzle configuration is solvable."""
        flat_list = sum(puzzle, [])
        inversions = sum(
            1
            for i in range(len(flat_list))
            for j in range(i + 1, len(flat_list))
            if flat_list[i] and flat_list[j] and flat_list[i] > flat_list[j]
        )
        return inversions % 2 == 0

    def generate_solvable_puzzle(self) -> List[List[int]]:
        """Generate a random but solvable puzzle configuration."""
        while True:
            numbers = list(range(9))
            random.shuffle(numbers)
            puzzle = [numbers[i:i+3] for i in range(0, 9, 3)]
            if self.is_solvable(puzzle) and puzzle != self.goal_state:
                return puzzle

    def create_game_ui(self) -> None:
        """Create and set up the game user interface."""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main container with padding
        container = tk.Frame(self.root, bg=self.COLORS["background"], padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Create game frame
        self.frame = tk.Frame(container, bg=self.COLORS["frame"], padx=15, pady=15,
                              relief=tk.RAISED, borderwidth=1)
        self.frame.pack()
        
        # Game title
        header_frame = tk.Frame(self.frame, bg=self.COLORS["header"], padx=10, pady=6)
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        
        self.label = tk.Label(header_frame, text="8-Puzzle Game", 
                             font=self.FONT_TITLE, bg=self.COLORS["header"], 
                             fg=self.COLORS["header_text"])
        self.label.pack()
        
        # Create tile grid
        self.tiles_frame = tk.Frame(self.frame, bg=self.COLORS["frame"])
        self.tiles_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
        
        self.buttons = []  # Clear existing buttons
        
        for i in range(3):
            row = []
            for j in range(3):
                tile_value = self.state[i][j]
                is_empty = tile_value == 0
                
                btn = tk.Button(self.tiles_frame, text=str(tile_value) if not is_empty else "", 
                               font=self.FONT_TILE, width=2, height=1,
                               bg=self.COLORS["empty"] if is_empty else self.COLORS["tile"],
                               fg=self.COLORS["tile_text"],
                               relief=tk.FLAT if is_empty else tk.RAISED,
                               borderwidth=1,
                               command=lambda x=i, y=j: self.move_tile(x, y))
                btn.grid(row=i, column=j, padx=3, pady=3, ipadx=10, ipady=10)
                row.append(btn)
            self.buttons.append(row)
        
        # Score display
        score_frame = tk.Frame(self.frame, bg=self.COLORS["frame"], pady=10)
        score_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=10)
        
        # Current score and high score display side by side
        current_score_frame = tk.Frame(score_frame, bg=self.COLORS["frame"])
        current_score_frame.pack(side=tk.LEFT, expand=True)
        
        self.score_label = tk.Label(current_score_frame, text=f"Score: {self.score}", 
                                   font=self.FONT_SCORE, bg=self.COLORS["frame"])
        self.score_label.pack()
        
        high_score_frame = tk.Frame(score_frame, bg=self.COLORS["frame"])
        high_score_frame.pack(side=tk.RIGHT, expand=True)
        
        self.high_score_label = tk.Label(high_score_frame, 
                                       text=f"Best: {self.high_scores.get('highest', 0)}", 
                                       font=self.FONT_SCORE, bg=self.COLORS["frame"],
                                       fg=self.COLORS["highscore"])
        self.high_score_label.pack()
        
        # Button panel
        button_frame = tk.Frame(self.frame, bg=self.COLORS["frame"])
        button_frame.grid(row=3, column=0, columnspan=3, pady=(5, 10))
        
        # Action buttons
        tk.Button(button_frame, text="Hint", command=self.show_hint, font=self.FONT_BUTTON,
                 bg=self.COLORS["button_hint"], padx=10, pady=5, 
                 relief=tk.RAISED).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Solve", command=self.solve_puzzle, font=self.FONT_BUTTON,
                 bg=self.COLORS["button_solve"], padx=10, pady=5,
                 relief=tk.RAISED).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Shuffle", command=self.shuffle_puzzle, font=self.FONT_BUTTON,
                 bg=self.COLORS["button_shuffle"], padx=10, pady=5,
                 relief=tk.RAISED).pack(side=tk.LEFT, padx=5)
        
        # Home button
        tk.Button(button_frame, text="Home", command=self.create_start_page, font=self.FONT_BUTTON,
                 bg=self.COLORS["header"], fg=self.COLORS["header_text"], padx=10, pady=5,
                 relief=tk.RAISED).pack(side=tk.LEFT, padx=5)

    def move_tile(self, x: int, y: int) -> None:
        """Handle tile movement when clicked."""
        empty_x, empty_y = self.find_empty()
        if abs(x - empty_x) + abs(y - empty_y) == 1:
            # Valid move - swap tile with empty space
            self.state[empty_x][empty_y], self.state[x][y] = self.state[x][y], self.state[empty_x][empty_y]
            self.update_ui()
            
            # Update score with streak multiplier
            self.score += 10 * self.streak
            self.streak += 1
            self.score_label.config(text=f"Score: {self.score}")

            # Check for win condition
            if self.state == self.goal_state:
                self.handle_game_completion()
        else:
            # Invalid move - reset streak
            self.streak = 1
    
    def handle_game_completion(self) -> None:
        """Handle game completion, update scores and show completion screen."""
        # Update high scores
        is_new_record = False
        if self.score > self.high_scores.get("highest", 0):
            self.high_scores["highest"] = self.score
            is_new_record = True
        
        self.high_scores["total_games"] = self.high_scores.get("total_games", 0) + 1
        self.high_scores["total_score"] = self.high_scores.get("total_score", 0) + self.score
        
        # Save high scores
        self.save_high_scores()
        
        # Show congratulations message
        if is_new_record:
            messagebox.showinfo("New High Score!", 
                              f"Congratulations! You solved the puzzle with a new high score of {self.score}!")
        else:
            messagebox.showinfo("Success", 
                              f"Congratulations! You solved the puzzle!\nYour score: {self.score}")
        
        # Show completion screen
        self.show_completion_screen()
    
    def show_completion_screen(self) -> None:
        """Show the game completion screen."""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main container
        container = tk.Frame(self.root, bg=self.COLORS["background"], padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Create completion frame
        completion_frame = tk.Frame(container, bg=self.COLORS["frame"], padx=20, pady=20,
                                  relief=tk.RAISED, borderwidth=1)
        completion_frame.pack(fill=tk.BOTH, expand=True)
        
        # Congratulations header
        header_frame = tk.Frame(completion_frame, bg=self.COLORS["header"], padx=20, pady=10)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        congrats_label = tk.Label(header_frame, text="Puzzle Solved!", 
                                font=("Helvetica", 24, "bold"), bg=self.COLORS["header"], 
                                fg=self.COLORS["header_text"])
        congrats_label.pack()
        
        # Score display
        score_frame = tk.Frame(completion_frame, bg=self.COLORS["frame"], pady=10)
        score_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(score_frame, text=f"Your Score: {self.score}", 
               font=("Helvetica", 18, "bold"), bg=self.COLORS["frame"]).pack()
        
        # High score info
        highscore_frame = tk.Frame(completion_frame, bg=self.COLORS["frame"], pady=10)
        highscore_frame.pack(fill=tk.X, pady=10)
        
        highest_score = self.high_scores.get("highest", 0)
        total_games = self.high_scores.get("total_games", 0)
        avg_score = 0
        if total_games > 0:
            avg_score = round(self.high_scores.get("total_score", 0) / total_games)
        
        tk.Label(highscore_frame, text=f"High Score: {highest_score}", 
               font=self.FONT_HIGHSCORE, fg=self.COLORS["highscore"], 
               bg=self.COLORS["frame"]).pack()
        
        tk.Label(highscore_frame, text=f"Games Played: {total_games}", 
               font=("Helvetica", 12), bg=self.COLORS["frame"]).pack()
        
        tk.Label(highscore_frame, text=f"Average Score: {avg_score}", 
               font=("Helvetica", 12), bg=self.COLORS["frame"]).pack()
        
        # Action buttons
        button_frame = tk.Frame(completion_frame, bg=self.COLORS["frame"], pady=20)
        button_frame.pack(fill=tk.X)
        
        tk.Button(button_frame, text="Play Again", command=self.start_game,
                font=self.FONT_BUTTON, bg=self.COLORS["start_button"],
                fg=self.COLORS["start_button_text"], padx=15, pady=8).pack(side=tk.LEFT, expand=True)
        
        tk.Button(button_frame, text="Home", command=self.create_start_page,
                font=self.FONT_BUTTON, bg=self.COLORS["header"],
                fg=self.COLORS["header_text"], padx=15, pady=8).pack(side=tk.RIGHT, expand=True)
    
    def find_empty(self) -> Tuple[int, int]:
        """Find the position of the empty space in the puzzle."""
        for i in range(3):
            for j in range(3):
                if self.state[i][j] == 0:
                    return i, j
        return 0, 0  # Fallback (shouldn't happen)
    
    def update_ui(self) -> None:
        """Update the UI to reflect the current state."""
        for i in range(3):
            for j in range(3):
                tile_value = self.state[i][j]
                is_empty = tile_value == 0
                
                # Update button appearance
                self.buttons[i][j].config(
                    text=str(tile_value) if not is_empty else "",
                    bg=self.COLORS["empty"] if is_empty else self.COLORS["tile"],
                    relief=tk.FLAT if is_empty else tk.RAISED
                )
    
    def solve_puzzle(self) -> None:
        """Solve the puzzle using A* algorithm and animate the solution."""
        # Reset streak since we're auto-solving
        self.streak = 1
        
        # Find solution path
        path = self.a_star_search()
        if path:
            # Animate solution
            for step_idx, step in enumerate(path[1:]):
                self.state = [list(row) for row in step]
                self.update_ui()
                self.root.update()
                
                # Add "solving" indicator to score label
                if step_idx < len(path) - 2:
                    self.score_label.config(text=f"Solving: {step_idx + 1}/{len(path) - 1}")
                
                # Pause between steps
                self.root.after(300)
            
            # Show completion message but don't update high score since it was auto-solved
            self.score_label.config(text=f"Score: {self.score}")
            messagebox.showinfo("Solved", "The puzzle has been solved automatically!")
            
            # Return to start page
            self.create_start_page()
        else:
            messagebox.showerror("Error", "No solution found!")
    
    def a_star_search(self) -> List[List[List[int]]]:
        """Implement A* search algorithm to find the solution path."""
        def heuristic(state):
            """Calculate Manhattan distance heuristic."""
            h = 0
            for i in range(3):
                for j in range(3):
                    if state[i][j] != 0:
                        # Calculate where this tile should be in the goal state
                        value = state[i][j]
                        goal_row, goal_col = (value - 1) // 3, (value - 1) % 3
                        h += abs(i - goal_row) + abs(j - goal_col)
            return h
        
        # Convert state to tuple for hashability
        start = tuple(map(tuple, self.state))
        goal = tuple(map(tuple, self.goal_state))
        
        # Initialize priority queue and visited set
        open_set = []
        heapq.heappush(open_set, (heuristic(start), 0, start, [start]))
        closed_set = set()
        
        while open_set:
            _, g_score, current, path = heapq.heappop(open_set)
            
            # Check if we've reached the goal
            if current == goal:
                # Convert path of tuples back to lists for returning
                return [list(map(list, state)) for state in path]
            
            # Skip if already visited
            if current in closed_set:
                continue
                
            closed_set.add(current)
            
            # Find empty position
            empty_pos = None
            for i in range(3):
                for j in range(3):
                    if current[i][j] == 0:
                        empty_pos = (i, j)
                        break
                if empty_pos:
                    break
                    
            empty_x, empty_y = empty_pos
            
            # Try all four possible moves
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = empty_x + dx, empty_y + dy
                
                if 0 <= nx < 3 and 0 <= ny < 3:
                    # Create new state by swapping tiles
                    new_state = [list(row) for row in current]
                    new_state[empty_x][empty_y], new_state[nx][ny] = new_state[nx][ny], new_state[empty_x][empty_y]
                    new_tuple = tuple(map(tuple, new_state))
                    
                    if new_tuple not in closed_set:
                        new_g_score = g_score + 1
                        new_h_score = heuristic(new_tuple)
                        heapq.heappush(
                            open_set, 
                            (new_g_score + new_h_score, new_g_score, new_tuple, path + [new_tuple])
                        )
        
        # No solution found
        return None
    
    def show_hint(self) -> None:
        """Show a hint for the next move using A* algorithm."""
        # Reset streak since user needed a hint
        self.streak = 1
        
        # Find solution path
        path = self.a_star_search()
        if path and len(path) > 1:
            next_state = path[1]
            self.highlight_hint(next_state)
        else:
            messagebox.showerror("Error", "No hint available!")
    
    def highlight_hint(self, next_state: List[List[int]]) -> None:
        """Highlight the tile that should be moved next."""
        # First restore all tiles to normal appearance
        self.update_ui()
        
        # Find the empty space in current state
        empty_x, empty_y = self.find_empty()
        
        # Find the tile that will move into the empty space
        # This is done by finding which tile in next_state is at the empty position in current state
        tile_value = next_state[empty_x][empty_y]
        
        # Now find where that tile is in the current state
        tile_x, tile_y = None, None
        for i in range(3):
            for j in range(3):
                if self.state[i][j] == tile_value:
                    tile_x, tile_y = i, j
                    break
            if tile_x is not None:
                break
        
        # Highlight the tile that should be moved
        if tile_x is not None and tile_y is not None:
            self.buttons[tile_x][tile_y].config(
                bg=self.COLORS["hint_highlight"]
            )
    
    def shuffle_puzzle(self) -> None:
        """Generate a new random puzzle configuration."""
        self.state = self.generate_solvable_puzzle()
        self.update_ui()
        self.score = 0
        self.streak = 1
        self.score_label.config(text=f"Score: {self.score}")


if __name__ == "__main__":
    root = tk.Tk()
    game = PuzzleGame(root)
    root.mainloop()