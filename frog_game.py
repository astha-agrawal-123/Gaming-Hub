import pygame
import random
import os
import sys

pygame.init()

# Set up display with more flexible sizing
WIDTH, HEIGHT = 1200, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jumping Frog Game")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 72)
subtitle_font = pygame.font.Font(None, 48)

# Asset path setup
ASSET_DIR = '/Users/astha/Desktop/game for project/assets'

# Load and scale images
def load_and_scale(image_path, width, height):
    img = pygame.image.load(os.path.join(ASSET_DIR, image_path))
    return pygame.transform.scale(img, (width, height))

# Scale images appropriately for the game
frog_img = load_and_scale("frog.png", 40, 40)
car_img = load_and_scale("car.png", 80, 40)
truck_img = load_and_scale("truck.png", 120, 40)
log_img = load_and_scale("log.png", 160, 40)
lilypad_img = load_and_scale("lilypad.png", 60, 60)

# Constants for game grid
GRID_SIZE = 50  # Size of each grid cell
FROG_SIZE = 40  # Size of the frog

# Game state
MENU = 0
PLAYING = 1
GAME_OVER = 2
LEVEL_COMPLETE = 3

# Colors
GREEN = (50, 180, 50)
DARK_GREEN = (20, 120, 20)
BLUE = (0, 100, 255)
DARK_BLUE = (0, 70, 180)
ROAD_GRAY = (80, 80, 80)
ROAD_LINE = (255, 255, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Button class for menu
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.text_surf = font.render(text, True, BLACK)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        
    def draw(self):
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 3, border_radius=10)
        screen.blit(self.text_surf, self.text_rect)
        
    def check_hover(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            return True
        else:
            self.current_color = self.color
            return False

# Frog class
class Frog:
    def __init__(self):
        self.width, self.height = FROG_SIZE, FROG_SIZE
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 10
        self.lives = 3
        self.animation_timer = 0
        self.jump_animation = False
        self.original_img = frog_img
        self.image = self.original_img

    def draw(self):
        # Simple jump animation
        if self.jump_animation:
            self.animation_timer += 1
            if self.animation_timer <= 5:
                # Scale up slightly during jump
                scale = 1.2
                jump_img = pygame.transform.scale(
                    self.original_img, 
                    (int(self.width * scale), int(self.height * scale))
                )
                screen.blit(jump_img, (self.x - (self.width * (scale-1))/2, self.y - (self.height * (scale-1))/2))
            else:
                screen.blit(self.image, (self.x, self.y))
                
            if self.animation_timer >= 10:
                self.jump_animation = False
                self.animation_timer = 0
        else:
            screen.blit(self.image, (self.x, self.y))

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Keep frog within bounds
        if 0 <= new_x <= WIDTH - self.width:
            self.x = new_x
        if 0 <= new_y <= HEIGHT - self.height:
            self.y = new_y
            
        # Trigger jump animation
        if dx != 0 or dy != 0:
            self.jump_animation = True
            self.animation_timer = 0

    def reset_position(self):
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 10

    def lose_life(self):
        self.lives -= 1
        self.reset_position()
        return self.lives > 0

# Obstacle class (used for cars, trucks, logs)
class Obstacle:
    def __init__(self, x, y, speed, image):
        self.x = x
        self.y = y
        self.speed = speed
        self.original_img = image
        # Flip image if moving left
        if speed < 0:
            self.image = pygame.transform.flip(image, True, False)
        else:
            self.image = image
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        self.x += self.speed
        # Check if off screen
        if (self.speed > 0 and self.x > WIDTH) or (self.speed < 0 and self.x + self.width < 0):
            return False
        return True

# Lily pad class
class LilyPad:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = lilypad_img.get_width()
        self.height = lilypad_img.get_height()
        self.occupied = False
        self.pulse_timer = 0
        self.pulse_direction = 1
        self.pulse_scale = 1.0

    def draw(self):
        if self.occupied:
            # Pulsing effect for occupied lily pads
            self.pulse_timer += 1
            if self.pulse_timer % 30 == 0:
                self.pulse_direction *= -1
                
            # Calculate scale factor
            pulse_amount = 0.1
            self.pulse_scale += 0.005 * self.pulse_direction
            if self.pulse_scale > 1 + pulse_amount:
                self.pulse_scale = 1 + pulse_amount
                self.pulse_direction = -1
            elif self.pulse_scale < 1 - pulse_amount:
                self.pulse_scale = 1 - pulse_amount
                self.pulse_direction = 1
                
            # Draw with scale
            scaled_img = pygame.transform.scale(
                lilypad_img, 
                (int(self.width * self.pulse_scale), int(self.height * self.pulse_scale))
            )
            screen.blit(scaled_img, 
                       (self.x - (scaled_img.get_width() - self.width)/2, 
                        self.y - (scaled_img.get_height() - self.height)/2))
            
            # Draw a frog on top to show it's occupied
            small_frog = pygame.transform.scale(frog_img, (30, 30))
            screen.blit(small_frog, (self.x + 15, self.y + 15))
        else:
            screen.blit(lilypad_img, (self.x, self.y))

# Game area definitions with clear spacing
BOTTOM_MARGIN = 50
GRASS_HEIGHT = GRID_SIZE * 2
ROAD_HEIGHT = GRID_SIZE * 3
MIDDLE_GRASS_HEIGHT = GRID_SIZE
RIVER_HEIGHT = GRID_SIZE * 3
TOP_MARGIN = GRID_SIZE

# Calculate positions from bottom up
grass_start = HEIGHT - GRASS_HEIGHT - BOTTOM_MARGIN
road_start = grass_start - ROAD_HEIGHT
middle_grass_start = road_start - MIDDLE_GRASS_HEIGHT
river_start = middle_grass_start - RIVER_HEIGHT
lily_pad_start = river_start - TOP_MARGIN

# Set up lanes and objects with proper spacing
vehicle_lanes = [
    {"y": grass_start - GRID_SIZE, "speed": 2, "image": car_img, "frequency": 120},
    {"y": grass_start - GRID_SIZE*2, "speed": -3, "image": truck_img, "frequency": 150},
    {"y": grass_start - GRID_SIZE*3, "speed": 2.5, "image": car_img, "frequency": 130},
]

log_lanes = [
    {"y": middle_grass_start - GRID_SIZE, "speed": -1.5, "image": log_img, "frequency": 160},
    {"y": middle_grass_start - GRID_SIZE*2, "speed": 2, "image": log_img, "frequency": 170},
    {"y": middle_grass_start - GRID_SIZE*3, "speed": -1.8, "image": log_img, "frequency": 180},
]

# Particle class for visual effects
class Particle:
    def __init__(self, x, y, color, size=5, vel_x=0, vel_y=0, life=30):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.life = life
        self.alpha = 255
        self.fade_rate = 255 / life
        
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.life -= 1
        self.alpha -= self.fade_rate
        self.size *= 0.95
        return self.life > 0
        
    def draw(self):
        if self.alpha > 0:
            surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, int(self.alpha)), (self.size, self.size), self.size)
            screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))

# Create lily pads in the water area
lily_pads_y = middle_grass_start - GRID_SIZE*4  # Position lily pads at the top of river
lilypads = [LilyPad(100 + i*200, lily_pads_y) for i in range(5)]

# Initialize game variables
vehicles = []
logs = []
particles = []
vehicle_timers = [0 for _ in vehicle_lanes]
log_timers = [0 for _ in log_lanes]

frog = Frog()

level = 1
score = 0
high_score = 0
game_state = MENU
message_timer = 0
level_complete_timer = 0

# Menu buttons
play_button = Button(WIDTH//2 - 100, HEIGHT//2, 200, 60, "PLAY", GREEN, YELLOW)
quit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 60, "QUIT", RED, YELLOW)

# Draw game areas with enhanced visuals
def draw_game_areas():
    # Bottom safe zone (grass with texture)
    pygame.draw.rect(screen, GREEN, (0, grass_start, WIDTH, GRASS_HEIGHT))
    for i in range(0, WIDTH, 20):
        for j in range(0, GRASS_HEIGHT, 20):
            if (i + j) % 40 == 0:
                pygame.draw.rect(screen, DARK_GREEN, (i, grass_start + j, 10, 10))
    
    # Road with lane markings
    pygame.draw.rect(screen, ROAD_GRAY, (0, road_start, WIDTH, ROAD_HEIGHT))
    # Draw road lines
    for y in range(road_start + GRID_SIZE, road_start + ROAD_HEIGHT, GRID_SIZE):
        for x in range(0, WIDTH, 40):
            pygame.draw.rect(screen, ROAD_LINE, (x, y - 2, 20, 4))
    
    # Middle safe zone
    pygame.draw.rect(screen, GREEN, (0, middle_grass_start, WIDTH, MIDDLE_GRASS_HEIGHT))
    for i in range(0, WIDTH, 20):
        if i % 40 == 0:
            pygame.draw.rect(screen, DARK_GREEN, (i, middle_grass_start, 10, 10))
    
    # River with wave effect
    pygame.draw.rect(screen, BLUE, (0, river_start, WIDTH, RIVER_HEIGHT))
    wave_offset = pygame.time.get_ticks() // 100  # Slow wave movement
    for i in range(0, WIDTH, 40):
        for j in range(0, RIVER_HEIGHT, 40):
            offset = (i + j + wave_offset) % 80
            if offset < 20:
                pygame.draw.rect(screen, DARK_BLUE, (i, river_start + j, 20, 10))
    
    # Lily pad area/goal
    pygame.draw.rect(screen, GREEN, (0, lily_pad_start, WIDTH, TOP_MARGIN))
    # Add some decoration
    for i in range(0, WIDTH, 30):
        pygame.draw.rect(screen, DARK_GREEN, (i, lily_pad_start + 10, 15, 15))

# Create water splash effect
def create_water_splash(x, y):
    for _ in range(20):
        vel_x = random.uniform(-2, 2)
        vel_y = random.uniform(-4, -1)
        size = random.uniform(3, 6)
        particles.append(Particle(x, y, BLUE, size, vel_x, vel_y, 40))

# Create confetti effect for level completion
def create_confetti():
    for _ in range(50):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT//3)
        vel_x = random.uniform(-1, 1)
        vel_y = random.uniform(1, 3)
        size = random.uniform(5, 10)
        color = random.choice([GREEN, YELLOW, RED, (255, 0, 255), (0, 255, 255)])
        particles.append(Particle(x, y, color, size, vel_x, vel_y, 120))

# Reset the game
def reset_game():
    global frog, vehicles, logs, score, level, particles
    frog = Frog()
    vehicles = []
    logs = []
    particles = []
    for pad in lilypads:
        pad.occupied = False
    if game_state == GAME_OVER:
        score = 0
        level = 1

# Update and draw particles
def update_particles():
    for particle in particles[:]:
        if not particle.update():
            particles.remove(particle)
        else:
            particle.draw()

# Main game loop
running = True
while running:
    clock.tick(60)
    mouse_pos = pygame.mouse.get_pos()
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == MENU:
                if play_button.check_hover(mouse_pos):
                    game_state = PLAYING
                    reset_game()
                elif quit_button.check_hover(mouse_pos):
                    running = False
                    
        elif event.type == pygame.KEYDOWN:
            if game_state == PLAYING:
                if event.key == pygame.K_LEFT and frog.x > 0:
                    frog.move(-GRID_SIZE, 0)
                elif event.key == pygame.K_RIGHT and frog.x + frog.width < WIDTH:
                    frog.move(GRID_SIZE, 0)
                elif event.key == pygame.K_UP and frog.y > 0:
                    frog.move(0, -GRID_SIZE)
                elif event.key == pygame.K_DOWN and frog.y + frog.height < HEIGHT:
                    frog.move(0, GRID_SIZE)
            elif game_state == GAME_OVER or game_state == LEVEL_COMPLETE:
                if event.key == pygame.K_r:
                    game_state = PLAYING
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    game_state = MENU
            elif game_state == MENU:
                if event.key == pygame.K_RETURN:
                    game_state = PLAYING
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    running = False
    
    # Clear screen
    screen.fill((20, 100, 20))
    
    # Handle different game states
    if game_state == MENU:
        # Draw decorative background
        for i in range(0, WIDTH, 50):
            for j in range(0, HEIGHT, 50):
                if (i + j) % 100 == 0:
                    pygame.draw.rect(screen, DARK_GREEN, (i, j, 25, 25))
        
        # Draw title
        title_text = title_font.render("JUMPING FROG", True, YELLOW)
        shadow_text = title_font.render("JUMPING FROG", True, BLACK)
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//4))
        screen.blit(shadow_text, (title_rect.x + 4, title_rect.y + 4))
        screen.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_text = subtitle_font.render("ADVENTURE", True, WHITE)
        sub_rect = subtitle_text.get_rect(center=(WIDTH//2, HEIGHT//4 + 70))
        screen.blit(subtitle_text, sub_rect)
        
        # Draw instructions
        inst_text1 = font.render("Use arrow keys to move", True, WHITE)
        inst_text2 = font.render("Cross the road and river to reach the lily pads", True, WHITE)
        inst_text3 = font.render("Fill all lily pads to advance to the next level", True, WHITE)
        screen.blit(inst_text1, (WIDTH//2 - inst_text1.get_width()//2, HEIGHT//2 - 100))
        screen.blit(inst_text2, (WIDTH//2 - inst_text2.get_width()//2, HEIGHT//2 - 60))
        screen.blit(inst_text3, (WIDTH//2 - inst_text3.get_width()//2, HEIGHT//2 - 20))
        
        # Draw high score
        high_score_text = font.render(f"High Score: {high_score}", True, YELLOW)
        screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT - 100))
        
        # Update button hover states
        play_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)
        
        # Draw buttons
        play_button.draw()
        quit_button.draw()
        
        # Draw a decorative frog
        big_frog = pygame.transform.scale(frog_img, (80, 80))
        screen.blit(big_frog, (WIDTH//2 - 40, HEIGHT//4 - 120))
        
    elif game_state == PLAYING:
        # Draw game zones
        draw_game_areas()
        
        # Update and draw vehicles
        for i, lane in enumerate(vehicle_lanes):
            vehicle_timers[i] += 1
            if vehicle_timers[i] >= lane["frequency"]:
                if sum(1 for v in vehicles if v.y == lane["y"]) < 2:  # LIMIT TO 2 VEHICLES PER LANE
                    vehicle_timers[i] = 0
                    start_x = -lane["image"].get_width() if lane["speed"] > 0 else WIDTH
                    speed_modifier = 1 + (level - 1) * 0.1  # Reduced speed scaling
                    vehicles.append(Obstacle(
                        start_x, 
                        lane["y"], 
                        lane["speed"] * speed_modifier, 
                        lane["image"]
                    ))

        # Update vehicles and check collisions
        for vehicle in vehicles[:]:
            if not vehicle.move():
                vehicles.remove(vehicle)
            else:
                vehicle.draw()
                
                # Collision detection
                frog_rect = pygame.Rect(frog.x, frog.y, frog.width, frog.height)
                vehicle_rect = pygame.Rect(vehicle.x, vehicle.y, vehicle.width, vehicle.height)
                if frog_rect.colliderect(vehicle_rect):
                    if not frog.lose_life():
                        game_state = GAME_OVER
                        if score > high_score:
                            high_score = score
                    else:
                        # Create crash particles
                        for _ in range(20):
                            vel_x = random.uniform(-2, 2)
                            vel_y = random.uniform(-2, 2)
                            size = random.uniform(3, 6)
                            particles.append(Particle(frog.x + frog.width//2, frog.y + frog.height//2, 
                                                    RED, size, vel_x, vel_y, 30))

        # Update and draw logs
        for i, lane in enumerate(log_lanes):
            log_timers[i] += 1
            if log_timers[i] >= lane["frequency"]:
                if sum(1 for l in logs if l.y == lane["y"]) < 2:  # LIMIT TO 2 LOGS PER LANE
                    log_timers[i] = 0
                    start_x = -lane["image"].get_width() if lane["speed"] > 0 else WIDTH
                    logs.append(Obstacle(start_x, lane["y"], lane["speed"], lane["image"]))

        # Handle log interactions
        on_log = False
        for log in logs[:]:
            if not log.move():
                logs.remove(log)
            else:
                log.draw()

                # Log collision
                frog_rect = pygame.Rect(frog.x, frog.y, frog.width, frog.height)
                log_rect = pygame.Rect(log.x, log.y, log.width, log.height)
                if frog_rect.colliderect(log_rect):
                    frog.x += log.speed
                    on_log = True
                    
                    # Keep frog within bounds while on log
                    if frog.x < 0:
                        frog.x = 0
                    elif frog.x > WIDTH - frog.width:
                        frog.x = WIDTH - frog.width

        # Check if frog is in water without a log
        if river_start < frog.y < middle_grass_start and not on_log:
            # Create water splash
            create_water_splash(frog.x + frog.width//2, frog.y + frog.height//2)
            
            if not frog.lose_life():
                game_state = GAME_OVER
                if score > high_score:
                    high_score = score
        
        # Check lily pad collisions
        frog_rect = pygame.Rect(frog.x, frog.y, frog.width, frog.height)
        for pad in lilypads:
            pad_rect = pygame.Rect(pad.x, pad.y, pad.width, pad.height)
            if frog_rect.colliderect(pad_rect) and not pad.occupied:
                pad.occupied = True
                frog.reset_position()
                score += 100
                # Create success particles
                for _ in range(20):
                    vel_x = random.uniform(-2, 2)
                    vel_y = random.uniform(-2, 2)
                    size = random.uniform(3, 6)
                    particles.append(Particle(pad.x + pad.width//2, pad.y + pad.height//2, 
                                            YELLOW, size, vel_x, vel_y, 40))
                
                # Check if all lily pads are filled
                if all(pad.occupied for pad in lilypads):
                    level += 1
                    game_state = LEVEL_COMPLETE
                    level_complete_timer = 180  # 3 seconds
                    create_confetti()

        # Draw lily pads
        for pad in lilypads:
            pad.draw()
            
        # Update and draw particles
        update_particles()
            
        # Draw frog last so it appears on top
        frog.draw()
        
    elif game_state == GAME_OVER:
        # Keep drawing the game state in the background
        draw_game_areas()
        for vehicle in vehicles:
            vehicle.draw()
        for log in logs:
            log.draw()
        for pad in lilypads:
            pad.draw()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Game Over Message
        game_over_text = title_font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//3))
        screen.blit(game_over_text, text_rect)
        
        # Display score
        final_score_text = subtitle_font.render(f"Final Score: {score}", True, WHITE)
        final_score_rect = final_score_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(final_score_text, final_score_rect)
        
        # Display high score
        if score >= high_score:
            high_score = score
            high_score_text = subtitle_font.render(f"NEW HIGH SCORE!", True, YELLOW)
        else:
            high_score_text = subtitle_font.render(f"High Score: {high_score}", True, WHITE)
        high_score_rect = high_score_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 60))
        screen.blit(high_score_text, high_score_rect)
        
        # Restart instructions
        restart_text = font.render("Press R to Restart or ESC for Menu", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT*3//4))
        screen.blit(restart_text, restart_rect)
        
        # Update particles for visual effect
        update_particles()
        
    elif game_state == LEVEL_COMPLETE:
        # Keep drawing the game state in the background
        draw_game_areas()
        for vehicle in vehicles:
            vehicle.draw()
        for log in logs:
            log.draw()
        for pad in lilypads:
            pad.draw()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))
        
        # Level Complete Message
        level_text = title_font.render(f"LEVEL {level-1} COMPLETE!", True, YELLOW)
        text_rect = level_text.get_rect(center=(WIDTH//2, HEIGHT//3))
        screen.blit(level_text, text_rect)
        
        # Next level message
        next_level_text = subtitle_font.render(f"Get Ready for Level {level}", True, WHITE)
        next_level_rect = next_level_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(next_level_text, next_level_rect)
        
        # Current score
        score_text = font.render(f"Score: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 60))
        screen.blit(score_text, score_rect)
        
        # Update particles for confetti effect
        update_particles()
        
        # Timer to auto-continue
        level_complete_timer -= 1
        if level_complete_timer <= 0:
            game_state = PLAYING
            # Reset for next level but keep score
            for pad in lilypads:
                pad.occupied = False
            vehicles = []
            logs = []
    
    # Draw UI elements (except in MENU state)
    if game_state != MENU:
        # Background panel for UI
        pygame.draw.rect(screen, (0, 0, 0, 180), (5, 5, 180, 110), border_radius=10)
        pygame.draw.rect(screen, WHITE, (5, 5, 180, 110), 2, border_radius=10)
        
        score_text = font.render(f"Score: {score}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        lives_text = font.render(f"Lives: {frog.lives}", True, WHITE)
        
        screen.blit(score_text, (15, 15))
        screen.blit(level_text, (15, 45))
        screen.blit(lives_text, (15, 75))
        
        # Draw small frogs to represent lives
        for i in range(frog.lives):
            small_frog = pygame.transform.scale(frog_img, (25, 25))
            screen.blit(small_frog, (100 + i*30, 70))
    
    # Update display
    pygame.display.flip()

pygame.quit()
sys.exit()

