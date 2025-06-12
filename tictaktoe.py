import pygame
import sys
import random
import time
import os
from pygame import mixer

# Initialize pygame
pygame.init()
mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BOARD_SIZE = 450
CELL_SIZE = BOARD_SIZE // 3

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (100, 100, 100)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
CYAN = (0, 180, 240)
YELLOW = (255, 220, 0)
PURPLE = (150, 50, 250)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tic Tac Toe Game")

# Load fonts
title_font = pygame.font.SysFont('comicsans', 70, bold=True)
large_font = pygame.font.SysFont('comicsans', 50)
medium_font = pygame.font.SysFont('comicsans', 36)
small_font = pygame.font.SysFont('comicsans', 24)

# Load sounds
try:
    click_sound = mixer.Sound("click.wav")
    win_sound = mixer.Sound("win.wav")
    draw_sound = mixer.Sound("draw.wav")
except:
    # Create placeholder sounds if files don't exist
    click_sound = mixer.Sound(buffer=bytearray(24))
    win_sound = mixer.Sound(buffer=bytearray(24))
    draw_sound = mixer.Sound(buffer=bytearray(24))

# Game states
START_MENU = 0
MODE_SELECTION = 1
DIFFICULTY_SELECTION = 2
SYMBOL_SELECTION = 3
GAME_PLAYING = 4
GAME_OVER = 5
HELP_SCREEN = 6


class Button:
    def __init__(self, x, y, width, height, text, color=CYAN, hover_color=BLUE, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.current_color = color
        self.is_hovered = False
        
    def draw(self, surface, font=medium_font):
        # Draw button with rounded corners
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=15)
        pygame.draw.rect(surface, DARK_GRAY, self.rect, 3, border_radius=15)
        
        # Draw text
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def update(self, mouse_pos):
        # Check if mouse is hovering over button
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.current_color = self.hover_color if self.is_hovered else self.color
        
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                click_sound.play()
                return True
        return False


class TicTacToe:
    def __init__(self):
        # Game variables
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.game_mode = None
        self.player_symbol = None
        self.computer_symbol = None
        self.difficulty = None
        self.winner = None
        self.game_over = False
        self.winning_cells = []
        
        # Animation variables
        self.board_alpha = 0
        self.piece_alphas = [[0 for _ in range(3)] for _ in range(3)]
        self.win_alpha = 0
        self.animation_speed = 15  # Alpha increase per frame
        
        # Time tracking for computer move delay
        self.computer_think_time = 0
        self.computer_move_time = 0
        
    def reset_game(self):
        """Reset the game state"""
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.winner = None
        self.game_over = False
        self.winning_cells = []
        
        # Reset animations
        self.board_alpha = 0
        self.piece_alphas = [[0 for _ in range(3)] for _ in range(3)]
        self.win_alpha = 0
        self.computer_think_time = 0
        self.computer_move_time = 0
    
    def make_move(self, row, col):
        """Make a move on the board"""
        if 0 <= row < 3 and 0 <= col < 3 and self.board[row][col] == " " and not self.game_over:
            self.board[row][col] = self.current_player
            
            # Check for win or draw
            if self.check_winner():
                self.game_over = True
                self.winner = self.current_player
                win_sound.play()
            elif self.is_draw():
                self.game_over = True
                draw_sound.play()
            else:
                self.switch_player()
                
            return True
        return False
    
    def check_winner(self):
        """Check if there's a winner and set winning cells"""
        # Check rows
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != " ":
                self.winning_cells = [(i, 0), (i, 1), (i, 2)]
                return True
        
        # Check columns
        for i in range(3):
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != " ":
                self.winning_cells = [(0, i), (1, i), (2, i)]
                return True
        
        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != " ":
            self.winning_cells = [(0, 0), (1, 1), (2, 2)]
            return True
        
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != " ":
            self.winning_cells = [(0, 2), (1, 1), (2, 0)]
            return True
        
        return False
    
    def is_draw(self):
        """Check if the game is a draw"""
        for row in self.board:
            if " " in row:
                return False
        return True
    
    def switch_player(self):
        """Switch the current player"""
        self.current_player = "O" if self.current_player == "X" else "X"
        
    def computer_move_easy(self):
        """Make a random computer move"""
        empty_cells = []
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == " ":
                    empty_cells.append((i, j))
        
        if empty_cells:
            row, col = random.choice(empty_cells)
            return row, col
        return None
    
    def computer_move_medium(self):
        """Make a smarter computer move"""
        # Check if computer can win
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == " ":
                    self.board[i][j] = self.computer_symbol
                    if self.check_winner():
                        self.board[i][j] = " "
                        self.winning_cells = []
                        return i, j
                    self.board[i][j] = " "
        
        # Check if player can win and block
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == " ":
                    self.board[i][j] = self.player_symbol
                    if self.check_winner():
                        self.board[i][j] = " "
                        self.winning_cells = []
                        return i, j
                    self.board[i][j] = " "
        
        # Try to take center
        if self.board[1][1] == " ":
            return 1, 1
        
        # Take corners if available
        corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
        random.shuffle(corners)
        for i, j in corners:
            if self.board[i][j] == " ":
                return i, j
        
        # Take edges
        edges = [(0, 1), (1, 0), (1, 2), (2, 1)]
        random.shuffle(edges)
        for i, j in edges:
            if self.board[i][j] == " ":
                return i, j
        
        return None
    
    def minimax(self, board, depth, is_maximizing):
        """Minimax algorithm for hard difficulty"""
        # Check for terminal states
        if self.check_winner_minimax(board, self.computer_symbol):
            return 10 - depth
        if self.check_winner_minimax(board, self.player_symbol):
            return depth - 10
        
        # Check for draw
        is_full = True
        for row in board:
            if " " in row:
                is_full = False
                break
        if is_full:
            return 0
        
        if is_maximizing:
            best_score = -float('inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == " ":
                        board[i][j] = self.computer_symbol
                        score = self.minimax(board, depth + 1, False)
                        board[i][j] = " "
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == " ":
                        board[i][j] = self.player_symbol
                        score = self.minimax(board, depth + 1, True)
                        board[i][j] = " "
                        best_score = min(score, best_score)
            return best_score
    
    def check_winner_minimax(self, board, player):
        """Helper function for minimax to check winner"""
        # Check rows
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] == player:
                return True
        
        # Check columns
        for i in range(3):
            if board[0][i] == board[1][i] == board[2][i] == player:
                return True
        
        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] == player:
            return True
        if board[0][2] == board[1][1] == board[2][0] == player:
            return True
        
        return False
    
    def computer_move_hard(self):
        """Make an optimal move using minimax algorithm"""
        best_score = -float('inf')
        best_move = None
        
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == " ":
                    self.board[i][j] = self.computer_symbol
                    score = self.minimax(self.board, 0, False)
                    self.board[i][j] = " "
                    
                    if score > best_score:
                        best_score = score
                        best_move = (i, j)
        
        if best_move:
            return best_move
        return None
    
    def computer_move(self):
        """Make a computer move based on difficulty"""
        if self.difficulty == "easy":
            return self.computer_move_easy()
        elif self.difficulty == "medium":
            return self.computer_move_medium()
        else:  # hard
            return self.computer_move_hard()
    
    def draw_board(self, surface, x_offset, y_offset):
        """Draw the game board with animations"""
        # Create a board surface with transparency
        board_surface = pygame.Surface((BOARD_SIZE, BOARD_SIZE), pygame.SRCALPHA)
        
        # Animate board alpha
        if self.board_alpha < 255:
            self.board_alpha += self.animation_speed
            if self.board_alpha > 255:
                self.board_alpha = 255
        
        # Draw board background
        board_surface.fill((255, 255, 255, self.board_alpha))
        
        # Draw grid lines with animation
        line_alpha = min(255, self.board_alpha + 40)
        line_color = (*BLACK[:3], line_alpha)
        line_width = 6
        
        # Vertical lines
        pygame.draw.line(board_surface, line_color, (CELL_SIZE, 0), 
                         (CELL_SIZE, BOARD_SIZE), line_width)
        pygame.draw.line(board_surface, line_color, (CELL_SIZE * 2, 0), 
                         (CELL_SIZE * 2, BOARD_SIZE), line_width)
        
        # Horizontal lines
        pygame.draw.line(board_surface, line_color, (0, CELL_SIZE), 
                         (BOARD_SIZE, CELL_SIZE), line_width)
        pygame.draw.line(board_surface, line_color, (0, CELL_SIZE * 2), 
                         (BOARD_SIZE, CELL_SIZE * 2), line_width)
        
        # Draw X's and O's with animations
        for i in range(3):
            for j in range(3):
                cell_center_x = j * CELL_SIZE + CELL_SIZE // 2
                cell_center_y = i * CELL_SIZE + CELL_SIZE // 2
                
                # Animate piece alpha when placed
                if self.board[i][j] != " " and self.piece_alphas[i][j] < 255:
                    self.piece_alphas[i][j] += self.animation_speed
                    if self.piece_alphas[i][j] > 255:
                        self.piece_alphas[i][j] = 255
                
                if self.board[i][j] == "X":
                    x_color = (*RED[:3], self.piece_alphas[i][j])
                    # Draw X
                    line_length = CELL_SIZE // 2 - 20
                    pygame.draw.line(board_surface, x_color, 
                                     (cell_center_x - line_length, cell_center_y - line_length),
                                     (cell_center_x + line_length, cell_center_y + line_length), 10)
                    pygame.draw.line(board_surface, x_color, 
                                     (cell_center_x - line_length, cell_center_y + line_length),
                                     (cell_center_x + line_length, cell_center_y - line_length), 10)
                elif self.board[i][j] == "O":
                    o_color = (*BLUE[:3], self.piece_alphas[i][j])
                    # Draw O
                    radius = CELL_SIZE // 2 - 20
                    pygame.draw.circle(board_surface, o_color, (cell_center_x, cell_center_y), radius, 10)
        
        # Draw winning line if there's a winner
        if self.winner and self.winning_cells:
            # Animate winning line
            if self.win_alpha < 255:
                self.win_alpha += self.animation_speed
                if self.win_alpha > 255:
                    self.win_alpha = 255
            
            win_color = (*YELLOW[:3], self.win_alpha)
            
            # Get start and end points of winning line
            start_cell = self.winning_cells[0]
            end_cell = self.winning_cells[2]
            
            start_x = start_cell[1] * CELL_SIZE + CELL_SIZE // 2
            start_y = start_cell[0] * CELL_SIZE + CELL_SIZE // 2
            end_x = end_cell[1] * CELL_SIZE + CELL_SIZE // 2
            end_y = end_cell[0] * CELL_SIZE + CELL_SIZE // 2
            
            # Draw winning line
            pygame.draw.line(board_surface, win_color, (start_x, start_y), (end_x, end_y), 12)
        
        # Draw the board surface on the main surface
        surface.blit(board_surface, (x_offset, y_offset))
    
    def handle_computer_turn(self, current_time):
        """Handle the computer's turn with timing delay"""
        if self.current_player == self.computer_symbol and not self.game_over:
            if self.computer_think_time == 0:
                # Start the timer
                self.computer_think_time = current_time
            
            # Add a delay before the computer moves
            think_delay = 500  # 500 ms for easy, longer for harder difficulties
            if self.difficulty == "medium":
                think_delay = 800
            elif self.difficulty == "hard":
                think_delay = 1200
            
            if current_time - self.computer_think_time >= think_delay:
                if self.computer_move_time == 0:
                    # Make the move
                    move = self.computer_move()
                    if move:
                        row, col = move
                        self.make_move(row, col)
                        click_sound.play()
                        self.computer_move_time = current_time
                        
                        # Reset timers
                        self.computer_think_time = 0
                        self.computer_move_time = 0


def draw_start_menu(surface):
    """Draw the start menu screen"""
    # Draw background
    surface.fill(LIGHT_GRAY)
    
    # Create gradient effect
    gradient_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for i in range(SCREEN_HEIGHT):
        alpha = 100 - int(i / SCREEN_HEIGHT * 100)
        pygame.draw.line(gradient_surface, (0, 0, 255, alpha), (0, i), (SCREEN_WIDTH, i))
    surface.blit(gradient_surface, (0, 0))
    
    # Draw title with shadow effect
    title_shadow = title_font.render("TIC TAC TOE", True, BLACK)
    title_text = title_font.render("TIC TAC TOE", True, YELLOW)
    
    shadow_x, shadow_y = SCREEN_WIDTH // 2 - title_text.get_width() // 2 + 3, 100 + 3
    text_x, text_y = SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100
    
    surface.blit(title_shadow, (shadow_x, shadow_y))
    surface.blit(title_text, (text_x, text_y))
    
    # Draw decorative X and O
    x_center = SCREEN_WIDTH // 4
    o_center = SCREEN_WIDTH * 3 // 4
    y_center = 250
    
    # Draw X
    line_length = 50
    pygame.draw.line(surface, RED, 
                     (x_center - line_length, y_center - line_length),
                     (x_center + line_length, y_center + line_length), 15)
    pygame.draw.line(surface, RED, 
                     (x_center - line_length, y_center + line_length),
                     (x_center + line_length, y_center - line_length), 15)
    
    # Draw O
    pygame.draw.circle(surface, BLUE, (o_center, y_center), 60, 15)
    
    # Draw buttons
    play_button = Button(SCREEN_WIDTH // 2 - 100, 350, 200, 60, "PLAY", CYAN)
    help_button = Button(SCREEN_WIDTH // 2 - 100, 430, 200, 60, "HOW TO PLAY", GREEN)
    quit_button = Button(SCREEN_WIDTH // 2 - 100, 510, 200, 60, "QUIT", RED)
    
    # Get mouse position for hover effects
    mouse_pos = pygame.mouse.get_pos()
    
    # Update and draw buttons
    play_button.update(mouse_pos)
    help_button.update(mouse_pos)
    quit_button.update(mouse_pos)
    
    play_button.draw(surface)
    help_button.draw(surface)
    quit_button.draw(surface)
    
    return play_button, help_button, quit_button


def draw_mode_selection(surface):
    """Draw the game mode selection screen"""
    surface.fill(LIGHT_GRAY)
    
    # Create gradient effect
    gradient_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for i in range(SCREEN_HEIGHT):
        alpha = 80 - int(i / SCREEN_HEIGHT * 80)
        pygame.draw.line(gradient_surface, (0, 180, 0, alpha), (0, i), (SCREEN_WIDTH, i))
    surface.blit(gradient_surface, (0, 0))
    
    # Draw title
    title_text = large_font.render("Select Game Mode", True, PURPLE)
    text_x = SCREEN_WIDTH // 2 - title_text.get_width() // 2
    surface.blit(title_text, (text_x, 80))
    
    # Draw buttons
    single_player_button = Button(SCREEN_WIDTH // 2 - 150, 200, 300, 80, "Single Player", CYAN)
    two_player_button = Button(SCREEN_WIDTH // 2 - 150, 320, 300, 80, "Two Players", GREEN)
    back_button = Button(SCREEN_WIDTH // 2 - 150, 440, 300, 60, "Back", YELLOW)
    
    # Get mouse position for hover effects
    mouse_pos = pygame.mouse.get_pos()
    
    # Update and draw buttons
    single_player_button.update(mouse_pos)
    two_player_button.update(mouse_pos)
    back_button.update(mouse_pos)
    
    single_player_button.draw(surface)
    two_player_button.draw(surface)
    back_button.draw(surface)
    
    return single_player_button, two_player_button, back_button


def draw_difficulty_selection(surface):
    """Draw the difficulty selection screen"""
    surface.fill(LIGHT_GRAY)
    
    # Create gradient effect
    gradient_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for i in range(SCREEN_HEIGHT):
        alpha = 80 - int(i / SCREEN_HEIGHT * 80)
        pygame.draw.line(gradient_surface, (0, 0, 180, alpha), (0, i), (SCREEN_WIDTH, i))
    surface.blit(gradient_surface, (0, 0))
    
    # Draw title
    title_text = large_font.render("Select Difficulty", True, PURPLE)
    text_x = SCREEN_WIDTH // 2 - title_text.get_width() // 2
    surface.blit(title_text, (text_x, 80))
    
    # Draw buttons
    easy_button = Button(SCREEN_WIDTH // 2 - 125, 180, 250, 70, "Easy", GREEN)
    medium_button = Button(SCREEN_WIDTH // 2 - 125, 270, 250, 70, "Medium", YELLOW)
    hard_button = Button(SCREEN_WIDTH // 2 - 125, 360, 250, 70, "Hard", RED)
    back_button = Button(SCREEN_WIDTH // 2 - 125, 450, 250, 60, "Back", CYAN)
    
    # Get mouse position for hover effects
    mouse_pos = pygame.mouse.get_pos()
    
    # Update and draw buttons
    easy_button.update(mouse_pos)
    medium_button.update(mouse_pos)
    hard_button.update(mouse_pos)
    back_button.update(mouse_pos)
    
    easy_button.draw(surface)
    medium_button.draw(surface)
    hard_button.draw(surface)
    back_button.draw(surface)
    
    return easy_button, medium_button, hard_button, back_button


def draw_symbol_selection(surface):
    """Draw the symbol selection screen"""
    surface.fill(LIGHT_GRAY)
    
    # Create gradient effect
    gradient_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for i in range(SCREEN_HEIGHT):
        alpha = 80 - int(i / SCREEN_HEIGHT * 80)
        pygame.draw.line(gradient_surface, (180, 0, 180, alpha), (0, i), (SCREEN_WIDTH, i))
    surface.blit(gradient_surface, (0, 0))
    
    # Draw title
    title_text = large_font.render("Choose Your Symbol", True, PURPLE)
    text_x = SCREEN_WIDTH // 2 - title_text.get_width() // 2
    surface.blit(title_text, (text_x, 80))
    
    # Draw buttons
    x_button = Button(SCREEN_WIDTH // 2 - 200, 220, 150, 150, "X", RED)
    o_button = Button(SCREEN_WIDTH // 2 + 50, 220, 150, 150, "O", BLUE)
    back_button = Button(SCREEN_WIDTH // 2 - 100, 430, 200, 60, "Back", CYAN)
    
    # Get mouse position for hover effects
    mouse_pos = pygame.mouse.get_pos()
    
    # Update and draw buttons
    x_button.update(mouse_pos)
    o_button.update(mouse_pos)
    back_button.update(mouse_pos)
    
    # Use larger font for X and O
    x_button.draw(surface, large_font)
    o_button.draw(surface, large_font)
    back_button.draw(surface)
    
    # Add labels
    x_label = small_font.render("(Goes First)", True, BLACK)
    surface.blit(x_label, (SCREEN_WIDTH // 2 - 200 + 75 - x_label.get_width() // 2, 380))
    
    return x_button, o_button, back_button


def draw_game_screen(surface, game):
    """Draw the game screen"""
    surface.fill(LIGHT_GRAY)
    
    # Create subtle gradient effect
    gradient_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for i in range(SCREEN_HEIGHT):
        alpha = 40 - int(i / SCREEN_HEIGHT * 40)
        pygame.draw.line(gradient_surface, (100, 100, 200, alpha), (0, i), (SCREEN_WIDTH, i))
    surface.blit(gradient_surface, (0, 0))
    
    # Calculate board position (centered)
    board_x = (SCREEN_WIDTH - BOARD_SIZE) // 2
    board_y = (SCREEN_HEIGHT - BOARD_SIZE) // 2 - 20
    
    # Draw game status
    status_text = ""
    if game.game_over:
        if game.winner:
            if game.game_mode == "single":
                if game.winner == game.player_symbol:
                    status_text = "You Win!"
                else:
                    status_text = "Computer Wins"
            else:
                status_text = f"Player {game.winner} Wins!"
        else:
            status_text = "It's a Draw!"
    else:
        if game.game_mode == "single" and game.current_player == game.computer_symbol:
            status_text = "Computer's Turn..."
        elif game.game_mode == "single":
            status_text = "Your Turn"
        else:
            status_text = f"Player {game.current_player}'s Turn"
    
    status_surface = medium_font.render(status_text, True, PURPLE)
    surface.blit(status_surface, (SCREEN_WIDTH // 2 - status_surface.get_width() // 2, 50))
    
    # Draw board
    game.draw_board(surface, board_x, board_y)
    
    # Draw buttons
    reset_button = Button(100, 500, 200, 60, "New Game", GREEN)
    menu_button = Button(SCREEN_WIDTH - 300, 500, 200, 60, "Main Menu", CYAN)
    
    # Get mouse position for hover effects
    mouse_pos = pygame.mouse.get_pos()
    
    # Update and draw buttons
    reset_button.update(mouse_pos)
    menu_button.update(mouse_pos)
    
    reset_button.draw(surface)
    menu_button.draw(surface)
    
    return reset_button, menu_button, board_x, board_y


def draw_help_screen(surface):
    """Draw the help screen"""
    surface.fill(LIGHT_GRAY)
    
    # Create gradient effect
    gradient_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for i in range(SCREEN_HEIGHT):
        alpha = 60 - int(i / SCREEN_HEIGHT * 60)
        pygame.draw.line(gradient_surface, (0, 180, 180, alpha), (0, i), (SCREEN_WIDTH, i))
    surface.blit(gradient_surface, (0, 0))
    
    # Draw title
    title_text = large_font.render("How To Play", True, PURPLE)
    text_x = SCREEN_WIDTH // 2 - title_text.get_width() // 2
    surface.blit(title_text, (text_x, 50))
    
    # Draw instructions
    instructions = [
        "1. The game is played on a 3x3 grid.",
        "2. Players take turns placing X or O in empty spaces.",
        "3. The first player to get 3 marks in a row",
        "   (horizontally, vertically, or diagonally) wins.",
        "4. If all spaces are filled with no winner, it's a draw.",
        "",
        "Game Modes:",
        "• Single Player: Play against the computer with",
        "  different difficulty levels."
        "• Two Players: Play against a friend on the same device.",
        "",
        "Difficulty Levels:",
        "• Easy: Computer makes random moves.",
        "• Medium: Computer can block your winning moves.",
        "• Hard: Computer plays optimally and cannot be beaten.",
    ]
    
    y_pos = 130
    for line in instructions:
        line_text = small_font.render(line, True, BLACK)
        surface.blit(line_text, (100, y_pos))
        y_pos += 30
    
    # Draw example board
    example_board_size = 180
    example_cell_size = example_board_size // 3
    example_board_x = SCREEN_WIDTH - 250
    example_board_y = 200
    
    # Draw example board background
    pygame.draw.rect(surface, WHITE, (example_board_x, example_board_y, 
                                     example_board_size, example_board_size))
    
    # Draw grid lines
    for i in range(1, 3):
        # Vertical lines
        pygame.draw.line(surface, BLACK,
                         (example_board_x + i * example_cell_size, example_board_y),
                         (example_board_x + i * example_cell_size, example_board_y + example_board_size), 3)
        # Horizontal lines
        pygame.draw.line(surface, BLACK,
                         (example_board_x, example_board_y + i * example_cell_size),
                         (example_board_x + example_board_size, example_board_y + i * example_cell_size), 3)
    
    # Draw example X and O
    # Draw X
    x_center_x = example_board_x + example_cell_size // 2
    x_center_y = example_board_y + example_cell_size // 2
    line_length = example_cell_size // 2 - 10
    pygame.draw.line(surface, RED,
                     (x_center_x - line_length, x_center_y - line_length),
                     (x_center_x + line_length, x_center_y + line_length), 5)
    pygame.draw.line(surface, RED,
                     (x_center_x - line_length, x_center_y + line_length),
                     (x_center_x + line_length, x_center_y - line_length), 5)
    
    # Draw O
    o_center_x = example_board_x + example_cell_size // 2 + example_cell_size
    o_center_y = example_board_y + example_cell_size // 2 + example_cell_size
    pygame.draw.circle(surface, BLUE, (o_center_x, o_center_y), line_length, 5)
    
    # Draw back button
    back_button = Button(SCREEN_WIDTH // 2 - 100, 500, 200, 60, "Back", CYAN)
    
    # Get mouse position for hover effects
    mouse_pos = pygame.mouse.get_pos()
    back_button.update(mouse_pos)
    back_button.draw(surface)
    
    return back_button


def main():
    """Main function to run the game"""
    clock = pygame.time.Clock()
    game = TicTacToe()
    current_state = START_MENU
    running = True
    
    while running:
        current_time = pygame.time.get_ticks()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle state-specific events
            if current_state == START_MENU:
                play_button, help_button, quit_button = draw_start_menu(screen)
                
                if play_button.is_clicked(event):
                    current_state = MODE_SELECTION
                elif help_button.is_clicked(event):
                    current_state = HELP_SCREEN
                elif quit_button.is_clicked(event):
                    running = False
            
            elif current_state == MODE_SELECTION:
                single_player_button, two_player_button, back_button = draw_mode_selection(screen)
                
                if single_player_button.is_clicked(event):
                    game.game_mode = "single"
                    current_state = DIFFICULTY_SELECTION
                elif two_player_button.is_clicked(event):
                    game.game_mode = "two_player"
                    game.reset_game()
                    current_state = GAME_PLAYING
                elif back_button.is_clicked(event):
                    current_state = START_MENU
            
            elif current_state == DIFFICULTY_SELECTION:
                easy_button, medium_button, hard_button, back_button = draw_difficulty_selection(screen)
                
                if easy_button.is_clicked(event):
                    game.difficulty = "easy"
                    current_state = SYMBOL_SELECTION
                elif medium_button.is_clicked(event):
                    game.difficulty = "medium"
                    current_state = SYMBOL_SELECTION
                elif hard_button.is_clicked(event):
                    game.difficulty = "hard"
                    current_state = SYMBOL_SELECTION
                elif back_button.is_clicked(event):
                    current_state = MODE_SELECTION
            
            elif current_state == SYMBOL_SELECTION:
                x_button, o_button, back_button = draw_symbol_selection(screen)
                
                if x_button.is_clicked(event):
                    game.player_symbol = "X"
                    game.computer_symbol = "O"
                    game.reset_game()
                    current_state = GAME_PLAYING
                elif o_button.is_clicked(event):
                    game.player_symbol = "O"
                    game.computer_symbol = "X"
                    game.reset_game()
                    current_state = GAME_PLAYING
                elif back_button.is_clicked(event):
                    current_state = DIFFICULTY_SELECTION
            
            elif current_state == GAME_PLAYING:
                reset_button, menu_button, board_x, board_y = draw_game_screen(screen, game)
                
                # Handle mouse clicks on the board
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_x, mouse_y = event.pos
                    
                    # Check if click is inside the board
                    if (board_x <= mouse_x <= board_x + BOARD_SIZE and
                        board_y <= mouse_y <= board_y + BOARD_SIZE):
                        
                        # Convert mouse position to grid position
                        col = (mouse_x - board_x) // CELL_SIZE
                        row = (mouse_y - board_y) // CELL_SIZE
                        
                        # Check if it's player's turn
                        if (game.game_mode == "two_player" or 
                            (game.game_mode == "single" and game.current_player == game.player_symbol)):
                            if game.make_move(row, col):
                                click_sound.play()
                
                # Handle button clicks
                if reset_button.is_clicked(event):
                    game.reset_game()
                elif menu_button.is_clicked(event):
                    current_state = START_MENU
            
            elif current_state == HELP_SCREEN:
                back_button = draw_help_screen(screen)
                
                if back_button.is_clicked(event):
                    current_state = START_MENU
        
        # Handle computer's turn in game playing state
        if current_state == GAME_PLAYING and game.game_mode == "single":
            game.handle_computer_turn(current_time)
        
        # Update display
        if current_state == START_MENU:
            draw_start_menu(screen)
        elif current_state == MODE_SELECTION:
            draw_mode_selection(screen)
        elif current_state == DIFFICULTY_SELECTION:
            draw_difficulty_selection(screen)
        elif current_state == SYMBOL_SELECTION:
            draw_symbol_selection(screen)
        elif current_state == GAME_PLAYING:
            draw_game_screen(screen, game)
        elif current_state == HELP_SCREEN:
            draw_help_screen(screen)
        
        # Flip the display to show what we've drawn
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    # Clean up pygame
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()