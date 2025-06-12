import tkinter as tk
from tkinter import messagebox, ttk
import random
import math
import time

class WaterJugGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Water Jug Challenge")
        
        # Make window resizable
        self.root.geometry("700x550")
        self.root.minsize(600, 500)
        self.root.configure(bg="#e8f4f8")
        
        # Game state
        self.jug1_capacity = 0
        self.jug2_capacity = 0
        self.goal_amount = 0
        self.jug1_current = 0
        self.jug2_current = 0
        self.moves_count = 0
        self.game_active = False
        self.solution_path = []
        self.current_hint_index = 0
        self.difficulty_level = tk.StringVar(value="Easy")
        self.time_start = 0
        self.timer_running = False
        self.timer_id = None
        self.best_scores = {"Easy": float('inf'), "Medium": float('inf'), "Hard": float('inf')}
        self.load_scores()
        
        # Create header
        header_frame = tk.Frame(root, bg="#8B4513", height=60)
        header_frame.pack(fill=tk.X)
        
        # Game title
        title_label = tk.Label(header_frame, text="WATER JUG CHALLENGE", 
                              font=("Arial", 20, "bold"),
                              bg="#8B4513", fg="#F0E68C")
        title_label.pack(pady=10)
        
        # Main content frame - uses pack with expand to fill available space
        main_frame = tk.Frame(root, bg="#e8f4f8")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel for controls
        control_frame = tk.Frame(main_frame, bg="#deb887", bd=2, relief=tk.RAISED)
        control_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        
        # Control panel title
        tk.Label(control_frame, text="GAME CONTROLS", font=("Arial", 12, "bold"),
                bg="#deb887", fg="#654321").pack(pady=5)
        
        # Difficulty selector
        tk.Label(control_frame, text="Select Difficulty:", font=("Arial", 10, "bold"), 
                bg="#deb887", fg="#654321").pack(anchor=tk.W, padx=10, pady=(5, 0))
        
        # Style for combobox
        self.style = ttk.Style()
        self.style.configure("TCombobox", fieldbackground="#fff8dc", foreground="#654321")
        
        difficulty_options = ["Easy", "Medium", "Hard", "Custom"]
        difficulty_menu = ttk.Combobox(control_frame, textvariable=self.difficulty_level, 
                                      values=difficulty_options, state="readonly", width=15)
        difficulty_menu.pack(anchor=tk.W, padx=10, pady=5)
        difficulty_menu.bind("<<ComboboxSelected>>", self.update_difficulty_fields)
        
        # Custom settings frame
        self.custom_frame = tk.LabelFrame(control_frame, text="Custom Settings", 
                                         font=("Arial", 10, "bold"), bg="#deb887", fg="#654321",
                                         bd=2, relief=tk.GROOVE)
        self.custom_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Grid layout for custom settings
        tk.Label(self.custom_frame, text="Jug 1 Capacity:", bg="#deb887", fg="#654321").grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        self.jug1_entry = tk.Entry(self.custom_frame, width=6, bg="#fff8dc", fg="#654321", bd=2)
        self.jug1_entry.grid(row=0, column=1, pady=3)
        
        tk.Label(self.custom_frame, text="Jug 2 Capacity:", bg="#deb887", fg="#654321").grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        self.jug2_entry = tk.Entry(self.custom_frame, width=6, bg="#fff8dc", fg="#654321", bd=2)
        self.jug2_entry.grid(row=1, column=1, pady=3)
        
        tk.Label(self.custom_frame, text="Goal Amount:", bg="#deb887", fg="#654321").grid(row=2, column=0, sticky=tk.W, padx=5, pady=3)
        self.goal_entry = tk.Entry(self.custom_frame, width=6, bg="#fff8dc", fg="#654321", bd=2)
        self.goal_entry.grid(row=2, column=1, pady=3)
        
        # Button frame
        button_frame = tk.Frame(control_frame, bg="#deb887")
        button_frame.pack(fill=tk.X, pady=5)
        
        # Game control buttons
        self.new_game_btn = tk.Button(button_frame, text="New Game", command=self.new_game,
                                     bg="#8B4513", fg="white", font=("Arial", 10, "bold"), 
                                     width=9, relief=tk.RAISED, bd=2)
        self.new_game_btn.grid(row=0, column=0, padx=3, pady=3)
        
        self.hint_btn = tk.Button(button_frame, text="Hint", command=self.provide_hint,
                                 bg="#DAA520", fg="white", font=("Arial", 10, "bold"), 
                                 width=9, relief=tk.RAISED, bd=2, state=tk.DISABLED)
        self.hint_btn.grid(row=0, column=1, padx=3, pady=3)
        
        self.restart_btn = tk.Button(button_frame, text="Restart", command=self.restart_game,
                                    bg="#CD853F", fg="white", font=("Arial", 10, "bold"), 
                                    width=9, relief=tk.RAISED, bd=2, state=tk.DISABLED)
        self.restart_btn.grid(row=1, column=0, padx=3, pady=3)
        
        self.solve_btn = tk.Button(button_frame, text="Auto Solve", command=self.auto_solve,
                                  bg="#556B2F", fg="white", font=("Arial", 10, "bold"), 
                                  width=9, relief=tk.RAISED, bd=2, state=tk.DISABLED)
        self.solve_btn.grid(row=1, column=1, padx=3, pady=3)
        
        # Timer display
        timer_frame = tk.LabelFrame(control_frame, text="Timer", font=("Arial", 10, "bold"),
                                   bg="#deb887", fg="#654321", bd=2, relief=tk.GROOVE)
        timer_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.timer_label = tk.Label(timer_frame, text="00:00", font=("Arial", 16),
                                   bg="#000000", fg="#32CD32", width=6, anchor=tk.CENTER)
        self.timer_label.pack(pady=3)
        
        # Stats Frame
        stats_frame = tk.LabelFrame(control_frame, text="Game Statistics", 
                                   font=("Arial", 10, "bold"), bg="#deb887", fg="#654321",
                                   bd=2, relief=tk.GROOVE)
        stats_frame.pack(fill=tk.X, padx=10, pady=5, expand=True)
        
        stats_inner = tk.Frame(stats_frame, bg="#deb887")
        stats_inner.pack(fill=tk.X, padx=5, pady=5)
        
        # Stats grid
        tk.Label(stats_inner, text="Moves:", bg="#deb887", fg="#654321", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.moves_label = tk.Label(stats_inner, text="0", bg="#fff8dc", fg="#654321", 
                                   width=5, relief=tk.SUNKEN, bd=1)
        self.moves_label.grid(row=0, column=1, sticky=tk.E, pady=2)
        
        tk.Label(stats_inner, text="Jug 1:", bg="#deb887", fg="#654321", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.jug1_info = tk.Label(stats_inner, text="0/0", bg="#fff8dc", fg="#654321", 
                                 width=5, relief=tk.SUNKEN, bd=1)
        self.jug1_info.grid(row=1, column=1, sticky=tk.E, pady=2)
        
        tk.Label(stats_inner, text="Jug 2:", bg="#deb887", fg="#654321", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.jug2_info = tk.Label(stats_inner, text="0/0", bg="#fff8dc", fg="#654321", 
                                 width=5, relief=tk.SUNKEN, bd=1)
        self.jug2_info.grid(row=2, column=1, sticky=tk.E, pady=2)
        
        tk.Label(stats_inner, text="Goal:", bg="#deb887", fg="#654321", font=("Arial", 9, "bold")).grid(row=3, column=0, sticky=tk.W, pady=2)
        self.goal_info = tk.Label(stats_inner, text="0", bg="#fff8dc", fg="#654321", 
                                 width=5, relief=tk.SUNKEN, bd=1)
        self.goal_info.grid(row=3, column=1, sticky=tk.E, pady=2)
        
        # Best score display
        tk.Label(stats_inner, text="Best:", bg="#deb887", fg="#654321", font=("Arial", 9, "bold")).grid(row=4, column=0, sticky=tk.W, pady=2)
        self.best_score_label = tk.Label(stats_inner, text="-", bg="#fff8dc", fg="#654321", 
                                        width=5, relief=tk.SUNKEN, bd=1)
        self.best_score_label.grid(row=4, column=1, sticky=tk.E, pady=2)
        
        # Right panel for the game visual - uses expand=True to utilize available space
        game_frame = tk.Frame(main_frame, bg="#87CEEB", bd=2, relief=tk.SUNKEN)
        game_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Title for game area
        tk.Label(game_frame, text="WATER JUG LABORATORY", font=("Arial", 12, "bold"),
                bg="#87CEEB", fg="#00008B").pack(pady=5)
        
        # Canvas for jug visualization
        self.canvas = tk.Canvas(game_frame, bg="#E0F7FA", relief=tk.SUNKEN, bd=2)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Action buttons frame
        actions_frame = tk.LabelFrame(game_frame, text="ACTIONS", font=("Arial", 10, "bold"),
                                     bg="#87CEEB", fg="#00008B", bd=2, relief=tk.GROOVE)
        actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # First row of action buttons
        btn_frame1 = tk.Frame(actions_frame, bg="#87CEEB")
        btn_frame1.pack(fill=tk.X, pady=3)
        
        self.fill_jug1_btn = tk.Button(btn_frame1, text="Fill Jug 1", command=lambda: self.perform_action("fill_jug1"),
                                      bg="#4682B4", fg="white", state=tk.DISABLED, width=9,
                                      font=("Arial", 9, "bold"), relief=tk.RAISED, bd=2)
        self.fill_jug1_btn.grid(row=0, column=0, padx=5, pady=3)
        
        self.fill_jug2_btn = tk.Button(btn_frame1, text="Fill Jug 2", command=lambda: self.perform_action("fill_jug2"),
                                      bg="#4682B4", fg="white", state=tk.DISABLED, width=9,
                                      font=("Arial", 9, "bold"), relief=tk.RAISED, bd=2)
        self.fill_jug2_btn.grid(row=0, column=1, padx=5, pady=3)
        
        self.empty_jug1_btn = tk.Button(btn_frame1, text="Empty Jug 1", command=lambda: self.perform_action("empty_jug1"),
                                       bg="#DC143C", fg="white", state=tk.DISABLED, width=9,
                                       font=("Arial", 9, "bold"), relief=tk.RAISED, bd=2)
        self.empty_jug1_btn.grid(row=0, column=2, padx=5, pady=3)
        
        self.empty_jug2_btn = tk.Button(btn_frame1, text="Empty Jug 2", command=lambda: self.perform_action("empty_jug2"),
                                       bg="#DC143C", fg="white", state=tk.DISABLED, width=9,
                                       font=("Arial", 9, "bold"), relief=tk.RAISED, bd=2)
        self.empty_jug2_btn.grid(row=0, column=3, padx=5, pady=3)
        
        # Second row of action buttons
        btn_frame2 = tk.Frame(actions_frame, bg="#87CEEB")
        btn_frame2.pack(fill=tk.X, pady=3)
        
        self.pour_1to2_btn = tk.Button(btn_frame2, text="Pour 1→2", command=lambda: self.perform_action("pour_1to2"),
                                      bg="#FFA500", fg="white", state=tk.DISABLED, width=9,
                                      font=("Arial", 9, "bold"), relief=tk.RAISED, bd=2)
        self.pour_1to2_btn.grid(row=0, column=1, padx=5, pady=3)
        
        self.pour_2to1_btn = tk.Button(btn_frame2, text="Pour 2→1", command=lambda: self.perform_action("pour_2to1"),
                                      bg="#FFA500", fg="white", state=tk.DISABLED, width=9,
                                      font=("Arial", 9, "bold"), relief=tk.RAISED, bd=2)
        self.pour_2to1_btn.grid(row=0, column=2, padx=5, pady=3)
        
        # Message box for game feedback
        message_frame = tk.LabelFrame(game_frame, text="LABORATORY NOTES", 
                                     font=("Arial", 10, "bold"), bg="#87CEEB", fg="#00008B",
                                     bd=2, relief=tk.GROOVE)
        message_frame.pack(fill=tk.BOTH, padx=10, pady=5)
        
        message_scroll = tk.Scrollbar(message_frame)
        message_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.message_box = tk.Text(message_frame, height=5, bg="#FFFAF0", 
                                  relief=tk.SUNKEN, bd=2, wrap=tk.WORD,
                                  font=("Arial", 9), fg="#333333")
        self.message_box.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        self.message_box.config(state=tk.DISABLED, yscrollcommand=message_scroll.set)
        message_scroll.config(command=self.message_box.yview)
        
        # Game instructions
        self.display_instructions()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Bind resize event to redraw
        self.root.bind("<Configure>", self.on_resize)
        
        # Set initial values based on difficulty
        self.update_difficulty_fields()
    
    def on_resize(self, event):
        """Handle window resize events"""
        # Only redraw if game is active and it's the root window being resized
        if self.game_active and event.widget == self.root:
            self.draw_jugs()
    
    def load_scores(self):
        """Load best scores from file"""
        try:
            with open("water_jug_scores.txt", "r") as f:
                for line in f:
                    difficulty, score = line.strip().split(":")
                    if int(score) < self.best_scores[difficulty]:
                        self.best_scores[difficulty] = int(score)
        except:
            # If file not found or corrupt, use defaults
            pass
    
    def save_scores(self):
        """Save best scores to file"""
        try:
            with open("water_jug_scores.txt", "w") as f:
                for diff, score in self.best_scores.items():
                    if score < float('inf'):
                        f.write(f"{diff}:{score}\n")
        except:
            # If can't save, just ignore
            pass
        
    def display_instructions(self):
        """Display game instructions in the message box"""
        welcome_message = (
            "Welcome to the Water Jug Challenge!\n\n"
            "OBJECTIVE: Measure exactly the GOAL amount of water using two jugs of different capacities.\n\n"
            "You can only:\n"
            "- Fill a jug completely\n"
            "- Empty a jug completely\n"
            "- Pour water from one jug to the other\n\n"
            "Select a difficulty and press 'New Game' to start."
        )
        self.update_message(welcome_message)
    
    def update_message(self, message):
        """Update the message box with the given text"""
        self.message_box.config(state=tk.NORMAL)
        self.message_box.delete(1.0, tk.END)
        self.message_box.insert(tk.END, message)
        self.message_box.config(state=tk.DISABLED)
        self.message_box.see(tk.END)  # Auto-scroll to the end
    
    def update_difficulty_fields(self, event=None):
        """Update the custom fields based on difficulty selection"""
        difficulty = self.difficulty_level.get()
        
        # Update best score display
        best_score = self.best_scores.get(difficulty, float('inf'))
        self.best_score_label.config(text=str(best_score) if best_score < float('inf') else "-")
        
        if difficulty == "Custom":
            # Enable custom fields
            for child in self.custom_frame.winfo_children():
                if isinstance(child, tk.Entry):
                    child.config(state=tk.NORMAL)
        else:
            # Set default values based on difficulty and disable fields
            for child in self.custom_frame.winfo_children():
                if isinstance(child, tk.Entry):
                    child.config(state=tk.DISABLED)
            
            if difficulty == "Easy":
                self.jug1_entry.delete(0, tk.END)
                self.jug1_entry.insert(0, "5")
                self.jug2_entry.delete(0, tk.END)
                self.jug2_entry.insert(0, "3")
                self.goal_entry.delete(0, tk.END)
                self.goal_entry.insert(0, "4")
            elif difficulty == "Medium":
                self.jug1_entry.delete(0, tk.END)
                self.jug1_entry.insert(0, "7")
                self.jug2_entry.delete(0, tk.END)
                self.jug2_entry.insert(0, "3")
                self.goal_entry.delete(0, tk.END)
                self.goal_entry.insert(0, "2")
            elif difficulty == "Hard":
                self.jug1_entry.delete(0, tk.END)
                self.jug1_entry.insert(0, "11")
                self.jug2_entry.delete(0, tk.END)
                self.jug2_entry.insert(0, "6")
                self.goal_entry.delete(0, tk.END)
                self.goal_entry.insert(0, "8")
    
    def is_solvable(self, jug1, jug2, goal):
        """Check if the water jug problem is solvable"""
        # The problem is solvable if goal is a multiple of gcd(jug1, jug2)
        gcd = math.gcd(jug1, jug2)
        return goal % gcd == 0 and goal <= max(jug1, jug2)
    
    def start_timer(self):
        """Start the timer for tracking puzzle solve time"""
        self.time_start = time.time()
        self.timer_running = True
        self.update_timer()
    
    def update_timer(self):
        """Update the timer display"""
        if self.timer_running:
            elapsed = int(time.time() - self.time_start)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
            self.timer_id = self.root.after(1000, self.update_timer)
    
    def stop_timer(self):
        """Stop the timer"""
        self.timer_running = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
    
    def new_game(self):
        """Start a new game with current settings"""
        difficulty = self.difficulty_level.get()
        
        try:
            if difficulty == "Custom":
                jug1_capacity = int(self.jug1_entry.get())
                jug2_capacity = int(self.jug2_entry.get())
                goal_amount = int(self.goal_entry.get())
                
                if jug1_capacity <= 0 or jug2_capacity <= 0:
                    messagebox.showerror("Invalid Input", "Jug capacities must be positive!")
                    return
                
                if goal_amount > max(jug1_capacity, jug2_capacity):
                    messagebox.showerror("Invalid Input", "Goal must be ≤ max jug capacity!")
                    return
                
                if not self.is_solvable(jug1_capacity, jug2_capacity, goal_amount):
                    messagebox.showerror("Invalid Problem", "This problem is not solvable! Try different values.")
                    return
            else:
                # Use predefined values
                jug1_capacity = int(self.jug1_entry.get())
                jug2_capacity = int(self.jug2_entry.get())
                goal_amount = int(self.goal_entry.get())
            
            # Set up the game
            self.jug1_capacity = jug1_capacity
            self.jug2_capacity = jug2_capacity
            self.goal_amount = goal_amount
            self.jug1_current = 0
            self.jug2_current = 0
            self.moves_count = 0
            self.game_active = True
            self.current_hint_index = 0
            
            # Stop previous timer if running
            self.stop_timer()
            # Start new timer
            self.start_timer()
            
            # Update UI
            self.update_stats()
            self.draw_jugs()
            
            welcome_message = (
                f"New game started!\n\n"
                f"OBJECTIVE: Measure exactly {goal_amount}L of water\n"
                f"EQUIPMENT: {jug1_capacity}L jug and {jug2_capacity}L jug\n\n"
                f"Good luck!"
            )
            self.update_message(welcome_message)
            
            # Enable game buttons
            self.enable_game_buttons()
            
            # Calculate solution path for hints
            self.calculate_solution()
            
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for all fields!")
    
    def calculate_solution(self):
        """Calculate a solution path for the current problem using BFS algorithm"""
        x = self.jug1_capacity
        y = self.jug2_capacity
        z = self.goal_amount
        
        # Using BFS to find the shortest path
        visited = set()
        queue = [[(0, 0)]]  # Queue of paths
        
        while queue:
            path = queue.pop(0)
            current_state = path[-1]
            a, b = current_state
            
            if a == z or b == z:
                self.solution_path = path
                return
            
            if current_state in visited:
                continue
                
            visited.add(current_state)
            
            # Generate all possible next states
            next_states = [
                (x, b),  # Fill jug 1
                (a, y),  # Fill jug 2
                (0, b),  # Empty jug 1
                (a, 0),  # Empty jug 2
                (min(a + b, x), max(0, a + b - x)),  # Pour jug 2 to jug 1
                (max(0, a + b - y), min(a + b, y))   # Pour jug 1 to jug 2
            ]
            
            for next_state in next_states:
                if next_state not in visited:
                    new_path = path + [next_state]
                    queue.append(new_path)
        
        # If no solution is found
        self.solution_path = []
    
    def provide_hint(self):
        """Provide a hint based on the calculated solution path"""
        if not self.game_active or not self.solution_path:
            return
        
        current_state = (self.jug1_current, self.jug2_current)
        
        # Find current state in solution path
        if current_state in self.solution_path:
            idx = self.solution_path.index(current_state)
            if idx < len(self.solution_path) - 1:
                next_state = self.solution_path[idx + 1]
                hint = self.get_move_description(current_state, next_state)
                self.update_message(f"HINT: {hint}")
            else:
                self.update_message("You're at the goal state! No more hints needed.")
        else:
            # User has deviated from solution path
            self.update_message("You've deviated from the solution path. Consider restarting.")
    
    def get_move_description(self, current, next_state):
        """Get the description of the move from current to next state"""
        a, b = current
        c, d = next_state
        
        if c == self.jug1_capacity and a != self.jug1_capacity:
            return f"Fill the {self.jug1_capacity}L jug completely"
        elif d == self.jug2_capacity and b != self.jug2_capacity:
            return f"Fill the {self.jug2_capacity}L jug completely"
        elif c == 0 and a != 0:
            return "Empty the first jug"
        elif d == 0 and b != 0:
            return "Empty the second jug"
        elif a < c and b > d:
            return f"Pour water from jug 2 into jug 1"
        elif a > c and b < d:
            return f"Pour water from jug 1 into jug 2"
        else:
            return "Move to the next state in the solution"
    
    def restart_game(self):
        """Restart the game with the same parameters"""
        if not self.game_active:
            return
            
        self.jug1_current = 0
        self.jug2_current = 0
        self.moves_count = 0
        self.current_hint_index = 0
        
        # Reset timer
        self.stop_timer()
        self.start_timer()
        
        self.update_stats()
        self.draw_jugs()
        self.update_message(f"Game restarted!\n\nOBJECTIVE: Measure exactly {self.goal_amount}L of water\nEQUIPMENT: {self.jug1_capacity}L jug and {self.jug2_capacity}L jug")
    
    def auto_solve(self):
        """Automatically solve the puzzle with animation"""
        if not self.game_active or not self.solution_path:
            return
            
        # Disable all buttons during animation
        self.disable_all_buttons()
        
        # Reset to initial state
        self.jug1_current = 0
        self.jug2_current = 0
        self.moves_count = 0
        self.update_stats()
        self.draw_jugs()
        
        self.update_message("AUTO-SOLVER ACTIVATED\n\nThe solution will be demonstrated step by step...")
        
        # Schedule the animation steps
        def animate_step(step_idx):
            if step_idx < len(self.solution_path):
                a, b = self.solution_path[step_idx]
                self.jug1_current = a
                self.jug2_current = b
                self.moves_count = step_idx
                self.update_stats()
                self.draw_jugs()
                
                if step_idx > 0:
                    move_desc = self.get_move_description(self.solution_path[step_idx-1], self.solution_path[step_idx])
                    step_message = f"AUTO-SOLVER (Step {step_idx}/{len(self.solution_path)-1})\n\n{move_desc}\n\nJug 1: {a}L, Jug 2: {b}L"
                    self.update_message(step_message)
                
                self.root.after(1000, lambda: animate_step(step_idx + 1))
            else:
                self.update_message("AUTO-SOLVE COMPLETE\n\nThis is one optimal solution with minimum steps.")
                self.enable_game_buttons()
                
                # Check if goal is reached
                if self.jug1_current == self.goal_amount or self.jug2_current == self.goal_amount:
                    self.update_message("AUTO-SOLVE COMPLETE!\n\nPuzzle solved in " + 
                                     f"{len(self.solution_path)-1} moves.\n\n" +
                                     "This is one optimal solution with minimum steps.")
                    # Update best score if this is better
                    if self.difficulty_level.get() != "Custom":
                        diff = self.difficulty_level.get()
                        if len(self.solution_path)-1 < self.best_scores[diff]:
                            self.best_scores[diff] = len(self.solution_path)-1
                            self.best_score_label.config(text=str(self.best_scores[diff]))
                            self.save_scores()
                else:
                    self.update_message("AUTO-SOLVE FAILED\n\nUnable to reach the goal state.")
                
                self.enable_game_buttons()
        
        # Start animation from the beginning
        animate_step(0)
    
    def enable_game_buttons(self):
        """Enable all game control buttons"""
        self.fill_jug1_btn.config(state=tk.NORMAL)
        self.fill_jug2_btn.config(state=tk.NORMAL)
        self.empty_jug1_btn.config(state=tk.NORMAL)
        self.empty_jug2_btn.config(state=tk.NORMAL)
        self.pour_1to2_btn.config(state=tk.NORMAL)
        self.pour_2to1_btn.config(state=tk.NORMAL)
        self.hint_btn.config(state=tk.NORMAL)
        self.restart_btn.config(state=tk.NORMAL)
        self.solve_btn.config(state=tk.NORMAL)
    
    def disable_all_buttons(self):
        """Disable all game control buttons"""
        self.fill_jug1_btn.config(state=tk.DISABLED)
        self.fill_jug2_btn.config(state=tk.DISABLED)
        self.empty_jug1_btn.config(state=tk.DISABLED)
        self.empty_jug2_btn.config(state=tk.DISABLED)
        self.pour_1to2_btn.config(state=tk.DISABLED)
        self.pour_2to1_btn.config(state=tk.DISABLED)
        self.hint_btn.config(state=tk.DISABLED)
        self.restart_btn.config(state=tk.DISABLED)
        self.solve_btn.config(state=tk.DISABLED)
    
    def update_stats(self):
        """Update the game statistics display"""
        self.moves_label.config(text=str(self.moves_count))
        self.jug1_info.config(text=f"{self.jug1_current}/{self.jug1_capacity}")
        self.jug2_info.config(text=f"{self.jug2_current}/{self.jug2_capacity}")
        self.goal_info.config(text=str(self.goal_amount))
    
    def draw_jugs(self):
        """Draw the jugs on the canvas with water visualization"""
        # Clear canvas
        self.canvas.delete("all")
        
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Calculate jug dimensions and positions
        jug_width = min(80, canvas_width / 5)
        jug_height = min(180, canvas_height * 0.7)
        jug_spacing = min(canvas_width / 3, 160)
        
        center_x = canvas_width / 2
        jug1_x = center_x - jug_spacing / 2
        jug2_x = center_x + jug_spacing / 2
        jug_bottom_y = canvas_height - 40
        
        # Draw jug outlines
        self.canvas.create_rectangle(jug1_x - jug_width/2, jug_bottom_y - jug_height, 
                                    jug1_x + jug_width/2, jug_bottom_y, 
                                    width=2, outline="#4682B4", fill="#F0F8FF")
        
        self.canvas.create_rectangle(jug2_x - jug_width/2, jug_bottom_y - jug_height, 
                                    jug2_x + jug_width/2, jug_bottom_y, 
                                    width=2, outline="#4682B4", fill="#F0F8FF")
        
        # Draw capacity labels
        self.canvas.create_text(jug1_x, jug_bottom_y + 15, 
                               text=f"{self.jug1_capacity}L Jug", 
                               fill="#00008B", font=("Arial", 10, "bold"))
        
        self.canvas.create_text(jug2_x, jug_bottom_y + 15, 
                               text=f"{self.jug2_capacity}L Jug", 
                               fill="#00008B", font=("Arial", 10, "bold"))
        
        # Draw water in jugs (if any)
        if self.jug1_current > 0:
            water_height = (self.jug1_current / self.jug1_capacity) * jug_height
            self.canvas.create_rectangle(jug1_x - jug_width/2 + 2, 
                                        jug_bottom_y - water_height,
                                        jug1_x + jug_width/2 - 2, 
                                        jug_bottom_y - 2,
                                        fill="#1E90FF", outline="")
            
            # Water level text
            self.canvas.create_text(jug1_x, jug_bottom_y - water_height/2, 
                                   text=f"{self.jug1_current}L", 
                                   fill="white", font=("Arial", 12, "bold"))
        
        if self.jug2_current > 0:
            water_height = (self.jug2_current / self.jug2_capacity) * jug_height
            self.canvas.create_rectangle(jug2_x - jug_width/2 + 2, 
                                        jug_bottom_y - water_height,
                                        jug2_x + jug_width/2 - 2, 
                                        jug_bottom_y - 2,
                                        fill="#1E90FF", outline="")
            
            # Water level text
            self.canvas.create_text(jug2_x, jug_bottom_y - water_height/2, 
                                   text=f"{self.jug2_current}L", 
                                   fill="white", font=("Arial", 12, "bold"))
        
        # Draw goal indicator
        goal_y = 30
        self.canvas.create_text(canvas_width/2, goal_y, 
                               text=f"GOAL: {self.goal_amount}L", 
                               fill="#B22222", font=("Arial", 14, "bold"))
    
    def perform_action(self, action):
        """Perform a water jug action"""
        if not self.game_active:
            return
            
        old_state = (self.jug1_current, self.jug2_current)
        
        # Increase move counter
        self.moves_count += 1
        
        action_desc = ""
        
        # Perform the selected action
        if action == "fill_jug1":
            self.jug1_current = self.jug1_capacity
            action_desc = f"Filled Jug 1 to capacity ({self.jug1_capacity}L)"
        
        elif action == "fill_jug2":
            self.jug2_current = self.jug2_capacity
            action_desc = f"Filled Jug 2 to capacity ({self.jug2_capacity}L)"
        
        elif action == "empty_jug1":
            self.jug1_current = 0
            action_desc = "Emptied Jug 1"
        
        elif action == "empty_jug2":
            self.jug2_current = 0
            action_desc = "Emptied Jug 2"
        
        elif action == "pour_1to2":
            # Pour from jug 1 to jug 2
            amount = min(self.jug1_current, self.jug2_capacity - self.jug2_current)
            self.jug1_current -= amount
            self.jug2_current += amount
            action_desc = f"Poured {amount}L from Jug 1 to Jug 2"
        
        elif action == "pour_2to1":
            # Pour from jug 2 to jug 1
            amount = min(self.jug2_current, self.jug1_capacity - self.jug1_current)
            self.jug2_current -= amount
            self.jug1_current += amount
            action_desc = f"Poured {amount}L from Jug 2 to Jug 1"
        
        # Update display
        self.update_stats()
        self.draw_jugs()
        
        # Check for solution
        if self.jug1_current == self.goal_amount or self.jug2_current == self.goal_amount:
            self.stop_timer()
            elapsed_time = int(time.time() - self.time_start)
            
            # Update best score if applicable
            if self.difficulty_level.get() != "Custom":
                diff = self.difficulty_level.get()
                if self.moves_count < self.best_scores[diff]:
                    self.best_scores[diff] = self.moves_count
                    self.best_score_label.config(text=str(self.best_scores[diff]))
                    self.save_scores()
                    
            congrats_msg = (
                f"CONGRATULATIONS!\n\n"
                f"You've successfully measured {self.goal_amount}L of water!\n\n"
                f"Moves: {self.moves_count}\n"
                f"Time: {elapsed_time // 60}m {elapsed_time % 60}s"
            )
            self.update_message(congrats_msg)
            messagebox.showinfo("Puzzle Solved!", "You've solved the Water Jug Challenge!")
        else:
            # Update message with the action performed
            status_msg = (
                f"Move #{self.moves_count}: {action_desc}\n\n"
                f"Current state:\n"
                f"Jug 1: {self.jug1_current}L / {self.jug1_capacity}L\n"
                f"Jug 2: {self.jug2_current}L / {self.jug2_capacity}L\n\n"
                f"Goal: {self.goal_amount}L"
            )
            self.update_message(status_msg)
    
    def on_close(self):
        """Handle window close event"""
        if self.game_active:
            if messagebox.askokcancel("Quit Game", "Do you want to quit the game?"):
                self.stop_timer()
                self.save_scores()
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = WaterJugGame(root)
    root.mainloop()