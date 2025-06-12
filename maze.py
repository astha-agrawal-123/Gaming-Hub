import turtle
import random

# Set up the screen
wn = turtle.Screen()
wn.title("Enchanted Maze Adventure")
wn.setup(1300, 700)
wn.tracer(0)
wn.bgcolor("#0f111b")  # Darker background for better contrast

# Player movement variables
global start_x, start_y, end_x, end_y, score, moves_left, game_running
score = 0
moves_left = 200
game_running = True

# Define Maze wall class
class Wall(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.shape("square")
        self.penup()
        self.speed(0)

    def create_wall(self, x, y):
        self.goto(x, y)
        self.color("#9a86fd")  # Brighter purple walls
        self.stamp()

# Define Start and End markers
class Marker(turtle.Turtle):
    def __init__(self, marker_type):
        super().__init__()
        self.penup()
        self.speed(0)
        self.hideturtle()
        
        if marker_type == "start":
            self.color("#00ff9f")  # Brighter green
        else:
            self.color("#ff5ee2")  # Brighter pink

    def place(self, x, y, marker_type):
        self.goto(x, y)
        if marker_type == "start":
            self.write("START", align="center", font=("Arial", 10, "bold"))
            # Draw a star shape around start
            self.goto(x, y-15)
            self.color("#00ff9f")
            self.pendown()
            self.pensize(3)  # Thicker lines
            for _ in range(5):
                self.forward(15)
                self.right(144)
            self.penup()
        else:
            self.write("FINISH", align="center", font=("Arial", 10, "bold"))
            # Draw a flag at the end point
            self.goto(x-10, y-25)
            self.pendown()
            self.pensize(3)  # Thicker lines
            self.goto(x-10, y+5)
            self.goto(x+10, y)
            self.goto(x-10, y-5)
            self.penup()

# Define Player class
class Player(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.shape("turtle")
        self.color("#ffff00")  # Bright yellow player
        self.shapesize(1.2)  # Slightly larger player
        self.penup()
        self.speed(0)
        self.goto(start_x, start_y)
        self.setheading(90)
        self.pencolor("#00ffff")  # Bright cyan trail
        self.pensize(3)  # Thicker trail

    def move(self, x, y, heading):
        global score, moves_left, game_running
        if not game_running:
            return
        new_pos = (self.xcor() + x, self.ycor() + y)
        if moves_left <= 0:
            game_over("You ran out of moves!")
            return
        if new_pos not in walls:
            self.pendown()  # Start drawing the path
            self.goto(new_pos)
            self.setheading(heading)
            score += 1
            moves_left -= 1
            update_display()
        check_win()

    def move_up(self):
        self.move(0, 24, 90)
    
    def move_down(self):
        self.move(0, -24, 270)
    
    def move_left(self):
        self.move(-24, 0, 180)
    
    def move_right(self):
        self.move(24, 0, 0)

# Function to check if the player has won
def check_win():
    if (player.xcor(), player.ycor()) == (end_x, end_y):
        celebrate_win()

# Create a status box that stays visible
def create_status_display():
    status_box = turtle.Turtle()
    status_box.penup()
    status_box.hideturtle()
    status_box.speed(0)
    status_box.color("#333344")
    
    # Draw status box at top of screen - clearer position
    status_box.goto(390, 300)
    status_box.begin_fill()
    for _ in range(2):
        status_box.forward(250)
        status_box.right(90)
        status_box.forward(70)
        status_box.right(90)
    status_box.end_fill()
    
    # Add a border
    status_box.color("#ffcc00")  # Gold border
    status_box.goto(390, 300)
    status_box.pendown()
    status_box.pensize(3)
    for _ in range(2):
        status_box.forward(250)
        status_box.right(90)
        status_box.forward(70)
        status_box.right(90)
    status_box.penup()
    
    return status_box

def celebrate_win():
    global game_running
    game_running = False
    wn.update()

    # Create a new turtle after update to ensure it's on top
    win_prompt = turtle.Turtle()
    win_prompt.hideturtle()
    win_prompt.penup()
    win_prompt.speed(0)

    # Shadow - Title
    win_prompt.color("#000000")
    win_prompt.goto(3, 103)
    win_prompt.write("🎉 CONGRATULATIONS! 🎉", align="center", font=("Arial", 32, "bold"))

    # Main - Title
    win_prompt.color("#ff5ee2")
    win_prompt.goto(0, 100)
    win_prompt.write("🎉 CONGRATULATIONS! 🎉", align="center", font=("Arial", 32, "bold"))

    # Shadow - Subtitle
    win_prompt.color("#000000")
    win_prompt.goto(3, 23)
    win_prompt.write("You solved the maze!", align="center", font=("Arial", 24, "normal"))

    # Main - Subtitle
    win_prompt.color("#00ffff")
    win_prompt.goto(0, 20)
    win_prompt.write("You solved the maze!", align="center", font=("Arial", 24, "normal"))

    # Shadow - Stats
    win_prompt.color("#000000")
    win_prompt.goto(3, -57)
    win_prompt.write(f"Score: {score} | Moves left: {moves_left}", align="center", font=("Arial", 20, "normal"))

    # Main - Stats
    win_prompt.color("#ffffff")
    win_prompt.goto(0, -60)
    win_prompt.write(f"Score: {score} | Moves left: {moves_left}", align="center", font=("Arial", 20, "normal"))

    wn.tracer(0)
    wn.ontimer(wn.bye, 5000)

def game_over(message):
    global game_running
    game_running = False
    wn.update()

    # Create a new turtle after update to ensure it's on top
    game_over_prompt = turtle.Turtle()
    game_over_prompt.hideturtle()
    game_over_prompt.penup()
    game_over_prompt.speed(0)

    # Shadow - Title
    game_over_prompt.color("#000000")
    game_over_prompt.goto(3, 103)
    game_over_prompt.write("GAME OVER", align="center", font=("Arial", 32, "bold"))

    # Main - Title
    game_over_prompt.color("#ff3333")
    game_over_prompt.goto(0, 100)
    game_over_prompt.write("GAME OVER", align="center", font=("Arial", 32, "bold"))

    # Shadow - Message
    game_over_prompt.color("#000000")
    game_over_prompt.goto(3, 23)
    game_over_prompt.write(message, align="center", font=("Arial", 24, "normal"))

    # Main - Message
    game_over_prompt.color("#ffffff")
    game_over_prompt.goto(0, 20)
    game_over_prompt.write(message, align="center", font=("Arial", 24, "normal"))

    # Shadow - Stats
    game_over_prompt.color("#000000")
    game_over_prompt.goto(3, -57)
    game_over_prompt.write(f"Final Score: {score}", align="center", font=("Arial", 20, "normal"))

    # Main - Stats
    game_over_prompt.color("#ffcc00")
    game_over_prompt.goto(0, -60)
    game_over_prompt.write(f"Final Score: {score}", align="center", font=("Arial", 20, "normal"))

    wn.tracer(0)
    wn.ontimer(wn.bye, 5000)

def update_display():
    display.clear()
    
    #  Adjust the positions to avoid overlap with the maze
    display.goto(400, 270)  # Score moved left further
    display.color("#ffcc00")  # Gold
    display.write(f"Score: {score}", align="left", font=("Arial", 18, "bold"))
    
    display.goto(400, 240)  # Moves left moved down a bit
    display.color("#00ffff")  # Cyan
    display.write(f"Moves left: {moves_left}", align="left", font=("Arial", 18, "bold"))
    
    # Add instructions at the bottom
    display.goto(0, 310)  # Move instructions further down
    display.color("#ffffff")
    display.write("Use arrow keys to navigate the maze, Use 's' key to solve the maze and Use 'm' key to switch the maze", align="center", font=("Arial", 16, "normal"))

    wn.update()

# New, more interesting and solvable maze grid
grid = [
    "+++++++++++++++++++++++++++++++++++++++++",
    "+s            +     +     +           + +",
    "+ +++++++++ + + +++ + +++ + ++++++ ++ + +",
    "+ +       + +   +   +   + +      +    + +",
    "+ + +++++ + +++++++++++++ ++++++++++ ++ +",
    "+ + +   + +         +           +    + +",
    "+ +++ + +++++++ +++ + +++++++++++ ++++ +",
    "+     +       + + + +       +     +    +",
    "+ ++++++++++++ +++ +++++++ + +++++ +++ +",
    "+ +     +     +       +    +     +   + +",
    "+ + +++ + +++ +++++++ + +++++++++ +++ + +",
    "+   +   + + +       + +         +   + + +",
    "+++++ +++ + +++++++ + ++++++++ +++ + + +",
    "+     +   +       + +       +     +   + +",
    "+ +++ + +++++++++++ +++++++ ++++++++++ +",
    "+ + + +             +     + +         + +",
    "+ + + +++++++++++++++++ + + + +++++++ + +",
    "+ +                     + + +       + + +",
    "+ +++++++++++++++++++++++ + +++++++ + + +",
    "+       +               + +         +   +",
    "+++++++ + +++++++++++++++ +++++++++++++++",
    "+     + +               +               +",
    "+ +++ + +++++++++++++ + +++++++++++++++ +",
    "+ + + +               +               + +",
    "+ + + +++++++++++++++++++++++++++++++ + +",
    "+ + +                                 + +",
    "+ + ++++++++++++++++++++++++++++++++++ +",
    "+ +                                     +",
    "+ +++++++++++++++++++++++++++++++++++ +++",
    "+                                      e+",
    "+++++++++++++++++++++++++++++++++++++++++",
]

walls = []

def setup_maze(grid):
    global start_x, start_y, end_x, end_y
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            char = grid[y][x]
            screen_x = -588 + (x * 24)
            screen_y = 288 - (y * 24)
            if char == "+":
                wall = Wall()
                wall.create_wall(screen_x, screen_y)
                walls.append((screen_x, screen_y))
            elif char == "s":
                start_x, start_y = screen_x, screen_y
                start_marker = Marker("start")
                start_marker.place(screen_x, screen_y, "start")
            elif char == "e":
                end_x, end_y = screen_x, screen_y
                end_marker = Marker("end")
                end_marker.place(screen_x, screen_y, "end")

# Add decorative elements to the maze
def add_decorations():
    decorations = []
    decoration_chars = ["🌟", "💎", "🌿", "🔮", "✨"]
    
    for _ in range(15):  # Add 15 random decorations
        deco = turtle.Turtle()
        deco.hideturtle()
        deco.penup()
        deco.speed(0)
        
        # Find a valid position (not on a wall or start/end)
        while True:
            x_pos = random.randint(-580, 580)
            y_pos = random.randint(-280, 280)
            if (x_pos, y_pos) not in walls and \
               (x_pos, y_pos) != (start_x, start_y) and \
               (x_pos, y_pos) != (end_x, end_y):
                break
        
        deco.goto(x_pos, y_pos)
        deco.color(random.choice(["#00ff9f", "#ff5ee2", "#00ffff", "#ffff00", "#ffcc00"]))
        deco.write(random.choice(decoration_chars), align="center", font=("Arial", 16, "normal"))
        decorations.append(deco)

# Setup the game first
setup_maze(grid)
add_decorations()

# Then create status box and display on top of maze
status_box = create_status_display()
display = turtle.Turtle()
display.penup()
display.hideturtle()
display.speed(0)
update_display()

# Then create player (so it draws over maze)
player = Player()


# Keyboard bindings
wn.listen()
wn.onkey(player.move_up, "Up")
wn.onkey(player.move_down, "Down")
wn.onkey(player.move_left, "Left")
wn.onkey(player.move_right, "Right")

# Add title with shadow for better visibility
title = turtle.Turtle()
title.hideturtle()
title.penup()
title.speed(0)

# Shadow
title.color("#000000")
title.goto(3, 343)
title.write("ENCHANTED MAZE ADVENTURE", align="center", font=("Arial", 24, "bold"))

# Main title
title.color("#ffcc00")  # Gold
title.goto(0, 340)
title.write("ENCHANTED MAZE ADVENTURE", align="center", font=("Arial", 24, "bold"))

# --- Auto-solve Function ---
def solve_maze_util(x, y, visited):
    if (x, y) == (end_x, end_y):
        return True

    directions = [(0, 24), (0, -24), (-24, 0), (24, 0)]  # up, down, left, right
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if (nx, ny) not in visited and (nx, ny) not in walls:
            visited.add((nx, ny))
            player.goto(nx, ny)
            player.pendown()
            wn.update()
            if solve_maze_util(nx, ny, visited):
                return True
            player.penup()
            player.goto(x, y)
            player.pendown()
    return False

def solve_maze():
    if not game_running:
        return
    visited = set()
    visited.add((player.xcor(), player.ycor()))
    player.pendown()
    solve_maze_util(player.xcor(), player.ycor(), visited)
    check_win()

# --- Switch Maze ---
maze2 = [
    "+++++++++++++++++++++++++++++++++++++++++",
    "+s +       +     + + + + +   + +     + +e",
    "+ + +++++ + +++ + + + + + +++ + +++ + + +",
    "+     +   +   + +   + + +   +   + + +   +",
    "+++++ + +++++ + +++++ + + +++++ + + +++++",
    "+   + +       +     + +     + + +       +",
    "+ + + +++++++++++ + +++++ + + + +++++++ +",
    "+ +             + +     + + + +       + +",
    "+ +++++++++++++ + + +++ + + + +++++++ + +",
    "+             + + + +   + + + +     + + +",
    "+++++++++++++ + + + + +++ + + + +++ + + +",
    "+           + +   +     + + +   + +   + +",
    "+ +++++++++ + +++++++++++ +++++ + +++++ +",
    "+                                     + +",
    "+++++++++++++++++++++++++++++++++++++++++",
]

def switch_maze():
    global walls, score, moves_left, game_running, start_x, start_y, end_x, end_y
    for item in wn.turtles():
        item.clear()
        item.hideturtle()
    walls.clear()
    score = 0
    moves_left = 200
    game_running = True
    setup_maze(random.choice([grid, maze2]))
    add_decorations()
    create_status_display()
    update_display()
    global player
    player = Player()
    wn.update()

# --- Bind keys ---
wn.onkey(solve_maze, "s")
wn.onkey(switch_maze, "m")

wn.update()
wn.mainloop()