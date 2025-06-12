import tkinter as tk
from tkinter import messagebox
import random
import heapq

class Puzzle:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Game with A*")
        self.goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        self.state = self.generate_solvable_puzzle()
        self.buttons = []
        self.create_ui()

    def is_solvable(self, puzzle):
        flat_list = sum(puzzle, [])
        inversions = sum(
            1
            for i in range(len(flat_list))
            for j in range(i + 1, len(flat_list))
            if flat_list[i] and flat_list[j] and flat_list[i] > flat_list[j]
        )
        return inversions % 2 == 0

    def generate_solvable_puzzle(self):
        while True:
            numbers = list(range(9))
            random.shuffle(numbers)
            puzzle = [numbers[i:i+3] for i in range(0, 9, 3)]
            if self.is_solvable(puzzle):
                return puzzle

    def create_ui(self):
        for i in range(3):
            row = []
            for j in range(3):
                btn = tk.Button(self.root, text=str(self.state[i][j]) if self.state[i][j] != 0 else "", 
                                width=5, height=2, font=("Arial", 24), 
                                command=lambda x=i, y=j: self.move_tile(x, y))
                btn.grid(row=i, column=j, padx=5, pady=5)
                row.append(btn)
            self.buttons.append(row)
        
        tk.Button(self.root, text="Hint", command=self.show_hint).grid(row=3, column=0, columnspan=1)
        tk.Button(self.root, text="Solve", command=self.solve_puzzle).grid(row=3, column=1, columnspan=1)
        tk.Button(self.root, text="Shuffle", command=self.shuffle_puzzle).grid(row=3, column=2, columnspan=1)

    def move_tile(self, x, y):
        empty_x, empty_y = self.find_empty()
        if abs(x - empty_x) + abs(y - empty_y) == 1:
            self.state[empty_x][empty_y], self.state[x][y] = self.state[x][y], self.state[empty_x][empty_y]
            self.update_ui()
            if self.state == self.goal_state:
                messagebox.showinfo("Success", "Congratulations! You have successfully solved the puzzle!")
    
    def find_empty(self):
        for i in range(3):
            for j in range(3):
                if self.state[i][j] == 0:
                    return i, j
    
    def update_ui(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text=str(self.state[i][j]) if self.state[i][j] != 0 else "", bg="SystemButtonFace")
    
    def solve_puzzle(self):
        path = self.a_star_search()
        if path:
            for step in path[1:]:
                self.state = [list(row) for row in step]
                self.update_ui()
                self.root.update()
                self.root.after(500)
            messagebox.showinfo("Solved", "The puzzle has been solved!")
        else:
            messagebox.showerror("Error", "No solution found!")
    
    def a_star_search(self):
        def heuristic(state):
            total_cost = 0
            for i in range(3):
                for j in range(3):
                    if state[i][j] != 0:
                        goal_x, goal_y = divmod(state[i][j] - 1, 3)
                        total_cost += abs(i - goal_x) + abs(j - goal_y)
            return total_cost
        
        start = tuple(map(tuple, self.state))
        pq, visited = [(heuristic(start), start, [])], set()
        
        while pq:
            _, current, path = heapq.heappop(pq)
            if current == tuple(map(tuple, self.goal_state)):
                return path + [self.goal_state]
            visited.add(current)
            empty_x, empty_y = [(i, j) for i in range(3) for j in range(3) if current[i][j] == 0][0]
            
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = empty_x + dx, empty_y + dy
                if 0 <= nx < 3 and 0 <= ny < 3:
                    new_state = [list(row) for row in current]
                    new_state[empty_x][empty_y], new_state[nx][ny] = new_state[nx][ny], new_state[empty_x][empty_y]
                    new_tuple = tuple(map(tuple, new_state))
                    if new_tuple not in visited:
                        heapq.heappush(pq, (heuristic(new_tuple) + len(path), new_tuple, path + [new_state]))
        return None
    
    def show_hint(self):
        path = self.a_star_search()
        if path and len(path) > 1:
            next_move = [list(row) for row in path[1]]
            empty_x, empty_y = self.find_empty()
            for i in range(3):
                for j in range(3):
                    if self.state[i][j] != next_move[i][j] and next_move[i][j] != 0:
                        self.buttons[i][j].config(bg="yellow")  # Highlight the suggested move
                        self.root.after(500, lambda x=i, y=j: self.buttons[x][y].config(bg="SystemButtonFace"))
                        return
        else:
            messagebox.showerror("Error", "No hint available!")
    
    def shuffle_puzzle(self):
        self.state = self.generate_solvable_puzzle()
        self.update_ui()

if __name__ == "__main__":
    root = tk.Tk()
    game = Puzzle(root)
    root.mainloop()
