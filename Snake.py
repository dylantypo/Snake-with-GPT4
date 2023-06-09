#### Imports
import pygame
import pygame.gfxdraw
import random
import time
import sys
import os

#### Game Parameters
# Game Files
snake_logo = pygame.image.load("Assets\Static\snake-logo.png")
FONT = "Assets\Static\PressStart2P-Regular.ttf"
HIGH_SCORES_FILE = "Assets\high_scores.txt"
music_file = "Assets\Static\snake_song.wav"
munch_file = "Assets\Static\munch.wav"

# EXE File Extensions
# snake_logo = pygame.image.load("..\..\Assets\Static\snake-logo.png")
# FONT = "..\..\Assets\Static\PressStart2P-Regular.ttf"
# HIGH_SCORES_FILE = "..\..\Assets\high_scores.txt"
# music_file = "..\..\Assets\Static\snake_song.wav"
# munch_file = "..\..\Assets\Static\munch.wav"
# Game constants
SNEK_START_LEN = 1 # Initial snake length
SNEK_MULTIPLIER = 3 # Amount snake grows after eating food
CELL_SIZE = 40 # Size of each grid cell
SPEED = 20 # Game speed
sX = 1 # Initial snake x-direction
sY = 0 # Initial snake y-direction

theme_dict = {
    "classic": {
        "background_color": "#E8E9EB",
        "snake_color": "#E4B363",
        "food_color": "#EF6461",
    },
    "retro": {
        "background_color": "#1E1E1E",
        "snake_color": "#00FF00",
        "food_color": "#FF0000",
    },
    "aquatic": {
        "background_color": "#4A90D9",
        "snake_color": "#285238",
        "food_color": "#FAD848",
    },
    "desert": {
        "background_color": "#E9C46A",
        "snake_color": "#264653",
        "food_color": "#F4A261",
    },
    "night": {
        "background_color": "#1F1F3D",
        "snake_color": "#E63946",
        "food_color": "#F1FAEE",
    }
}

#### Creating Classes
class Snake:
    def __init__(self, start_len):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)] # Initialize snake body at center of grid
        self.direction = (sX, sY) # Set initial direction
        self.direction_queue = [] # Queue to store direction changes
        # Initial Snake Size
        for _ in range(start_len):
            self.grow()

    def move(self):
        # Apply one direction change from the queue if available
        if self.direction_queue:
            self.direction = self.direction_queue.pop(0)

        # Calculate new head position based on current head position and direction
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = ((head_x + dir_x) % GRID_WIDTH, (head_y + dir_y) % GRID_HEIGHT)
        # Insert new head position at the beginning of the body and remove the last element
        self.body.insert(0, new_head)
        self.body.pop()

    def change_direction(self, new_direction):
        # Check if the new direction is not directly opposite to the current direction
        if self.direction_queue:
            last_direction = self.direction_queue[-1]
        else:
            last_direction = self.direction
        last_dir_x, last_dir_y = last_direction
        new_dir_x, new_dir_y = new_direction
        if last_dir_x != -new_dir_x and last_dir_y != -new_dir_y:
            # Add the new direction to the queue
            self.direction_queue.append(new_direction)

    def grow(self):
        tail_x, tail_y = self.body[-1] # Get the tail position

        if len(self.body) == 1:
            # If the snake has only one segment, grow in the opposite direction
            dir_x, dir_y = self.direction
            new_tail_x, new_tail_y = (tail_x - dir_x) % GRID_WIDTH, (tail_y - dir_y) % GRID_HEIGHT
        else:
            # If the snake has more than one segment, grow by extending the last segment
            prev_x, prev_y = self.body[-2]
            new_tail_x, new_tail_y = (2 * tail_x - prev_x) % GRID_WIDTH, (2 * tail_y - prev_y) % GRID_HEIGHT

        self.body.append((new_tail_x, new_tail_y)) # Add new tail segment to the body

    def collides_with(self, pos, ignore_head=False):
        # Check if position collides with any of the snake's body segments or food
        return pos in self.body[1 if ignore_head else 0:]

class Food:
    def __init__(self, snake):
        # Generate a new food position on the grid, making sure it doesn't collide with the snake
        self.position = self.generate_new_position(snake)

    # Function to generate a new position for the food on the grid
    def generate_new_position(self, snake):
        while True:
            # Generate a random position on the grid
            position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            # Check if the generated position collides with the snake
            if not snake.collides_with(position):
                return position
            
class Button:
    def __init__(self, 
                 x, y, 
                 width, height, 
                 text, 
                 function=None, 
                 color=(255, 255, 255), 
                 text_color = (0, 0, 0),
                 top_rounded = True, bottom_rounded = True):
        self.rect = pygame.Rect(x, y, width, height) # Button rectangle
        self.text = text # Button text
        self.text_color = text_color # Color of button text
        self.function = function # Function to call when the button is clicked
        self.color = color # Button color
        self.top_rounded = top_rounded # Flag for rounded top corners
        self.bottom_rounded = bottom_rounded # Flag for rounded bottom corners
        # Calculate the highlighted color when the mouse is over the button
        self.highlighted_color = tuple([min(c + 50, 255) for c in self.color])
        self.font = pygame.font.Font(FONT, 11) # Button font
        self.text_surface = self.font.render(self.text, True, self.text_color) # Rendered text surface
        self.text_rect = self.text_surface.get_rect(center=(width // 2, height // 2)) # Text rectangle

    # Update the button state and check for mouse clicks
    def update(self, screen, event):
        self.draw(screen)
        # Check if the button was clicked
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(pygame.mouse.get_pos()):
            if self.function:
                return self.function()
            

    # Checks for a border radius
    def get_border_radius(self):
        return 10 if self.top_rounded or self.bottom_rounded else 0

    def get_top_left_radius(self):
        return 10 if self.top_rounded else 0

    def get_top_right_radius(self):
        return 10 if self.top_rounded else 0

    def get_bottom_left_radius(self):
        return 10 if self.bottom_rounded else 0

    def get_bottom_right_radius(self):
        return 10 if self.bottom_rounded else 0

    # Draw the button on the screen
    def draw(self, screen):
        # Check if the mouse is over the button and change its color accordingly
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, 
                             self.highlighted_color, 
                             self.rect, 
                             border_radius=self.get_border_radius(), 
                             border_top_left_radius=self.get_top_left_radius(), 
                             border_top_right_radius=self.get_top_right_radius(), 
                             border_bottom_left_radius=self.get_bottom_left_radius(), 
                             border_bottom_right_radius=self.get_bottom_right_radius())
        else:
            pygame.draw.rect(screen, 
                             self.color, 
                             self.rect, 
                             border_radius=self.get_border_radius(), 
                             border_top_left_radius=self.get_top_left_radius(), 
                             border_top_right_radius=self.get_top_right_radius(), 
                             border_bottom_left_radius=self.get_bottom_left_radius(), 
                             border_bottom_right_radius=self.get_bottom_right_radius())

        # Draw the button text
        if self.text:
            screen.blit(self.text_surface, self.text_rect.move(self.rect.topleft))

# Restart game flag
class Restart:
    def __init__(self):
        self.value = False
        self.new_theme = None
        self.new_difficulty = None

#### Main Functions
# Function to display pre-game selection menus
def display_menu(GRID_WIDTH, GRID_HEIGHT, screen, text, themes):
    # Menu button parameters
    button_width = 250
    button_height = 90
    button_spacing = 10
    total_buttons_height = len(themes) * button_height + (len(themes) - 1) * button_spacing
    start_y = (GRID_HEIGHT * CELL_SIZE - total_buttons_height) // 2

    # Create menu buttons
    menu_buttons = []
    for i, theme_name in enumerate(themes):
        button_x = (GRID_WIDTH * CELL_SIZE - button_width) // 2
        button_y = start_y + i * (button_height + button_spacing)
        top_rounded = (i == 0)
        bottom_rounded = (i == len(themes) - 1)
        menu_buttons.append(Button(button_x, 
                                   button_y, 
                                   button_width, 
                                   button_height, 
                                   theme_name, 
                                   function=lambda i=i: i, 
                                   top_rounded=top_rounded, 
                                   bottom_rounded=bottom_rounded))
    
    # Function to draw buttons on the screen
    def draw_buttons(screen, menu_buttons):
        for button in menu_buttons:
            button.draw(screen)

    # Main menu loop
    menu_running = True
    while menu_running:
        screen.fill((0, 0, 0))

        # Display title text
        font_title = pygame.font.Font(FONT, 24)
        text_title = font_title.render(str(text), True, (255, 255, 255))
        text_title_rect = text_title.get_rect(center=(GRID_WIDTH * CELL_SIZE // 2, 50))
        screen.blit(text_title, text_title_rect)

        # Handle menu events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in menu_buttons:
                    button_result = button.update(screen, event)
                    if button_result is not None:
                        return button_result

        # Draw buttons and update the display
        draw_buttons(screen, menu_buttons)
        pygame.display.flip()

    time.sleep(2)  # Pause for a moment before returning

def check_and_create_highscores_file(file_name):
    if not os.path.exists(file_name):
        with open(file_name, "w") as file:
            file.write(f"0,AAA\n0,AAA\n0,AAA\n0,AAA\n0,AAA\n0,AAA\n0,AAA\n0,AAA\n0,AAA\n0,AAA")

def save_high_scores(high_scores):
    with open(HIGH_SCORES_FILE, "w") as file:
        for score, initials in high_scores:
            file.write(f"{score},{initials}\n")

def show_high_scores_screen(screen, high_scores, background_color, food_color):
    # Fill the screen with background color
    screen.fill(background_color)

    font = pygame.font.Font(FONT, 36)
    text = font.render("High Scores", 1, background_color, food_color)
    screen.blit(text, (250, 50))

    # Display high scores
    y_offset = 100
    for index, (score, initials) in enumerate(high_scores):
        text = font.render(f"{index + 1}.{score}->{initials}", 1, background_color, food_color)
        screen.blit(text, (250, 50 + y_offset))
        y_offset += 40

    # Update the display
    pygame.display.flip()

    # Wait for user input to exit high scores screen
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    screen.fill(background_color)
                    return
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def draw_glowing_circle(screen, pos, radius, color, alpha):
    x, y = pos
    for i in range(radius, 0, -1):
        pygame.gfxdraw.filled_circle(screen, x, y, i, (*color, min(alpha // i, 255)))

def draw_cell(screen, pos, color, glow_color=None, glow_radius=35, glow_alpha=70, alpha=100):
    if glow_color:
        x, y = pos
        draw_glowing_circle(screen, 
                            (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), 
                            glow_radius, 
                            glow_color, 
                            alpha)

    x, y = pos
    cell_margin = 2

    if len(color) == 3:
        color = (*color, alpha)
    elif len(color) == 4:
        color = (*color[:3], alpha)

    pygame.draw.rect(screen, 
                     color, 
                     (x * CELL_SIZE + cell_margin, y * CELL_SIZE + cell_margin, CELL_SIZE - 2 * cell_margin, CELL_SIZE - 2 * cell_margin))

def hex_to_rgb(hex_color):
    return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

def get_initials(GRID_WIDTH, GRID_HEIGHT, screen, prompt="Enter name: ", color=(255, 255, 255), background_color=(0, 0, 0)):
    text = ''
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return text.upper()[:3]  # Return the first three characters in upper case
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Clear the previous text
        rect = pygame.Rect(0, (GRID_HEIGHT * CELL_SIZE // 2 + 60), GRID_WIDTH * CELL_SIZE, 40)
        pygame.draw.rect(screen, background_color, rect)

        # Render the current text input
        font = pygame.font.Font(FONT, 16)
        block = font.render(prompt + text, True, color, background_color)
        rect = block.get_rect(center=(GRID_WIDTH * CELL_SIZE // 2, GRID_HEIGHT * CELL_SIZE // 2 + 80))
        screen.blit(block, rect)

        pygame.display.flip()

# Theme Select Menu
def theme_menu(GRID_WIDTH, GRID_HEIGHT, screen, background_color = (0, 0, 0)):
    theme_names = list(theme_dict.keys()) # Get theme names from dictionary of themes
    selected_theme_index = display_menu(GRID_WIDTH, GRID_HEIGHT, screen, "Select Theme", theme_names) # Display theme selection menu
    game_theme = theme_dict[theme_names[selected_theme_index]] # Store selected theme
    screen.fill(background_color)
    return game_theme

# Difficulty selection
def diff_menu(GRID_WIDTH, GRID_HEIGHT, screen, background_color = (0, 0, 0)):
    difficulty_index = display_menu(GRID_WIDTH, GRID_HEIGHT, screen, "Select Difficulty", ["Easy", "Medium", "Hard"]) # Display difficulty selection menu
    difficulty_lambda = lambda index: {0: -10, 1: 0, 2: 10}[index]
    difficulty_value = difficulty_lambda(difficulty_index) # Convert button index into difficulty value and store as a variable
    screen.fill(background_color)
    return difficulty_value + SPEED

def get_display_info():
    #### Get Current Display Info
    infoObject = pygame.display.Info()
    DISPLAY_WIDTH, DISPLAY_HEIGHT = infoObject.current_w, infoObject.current_h
    return DISPLAY_WIDTH, DISPLAY_HEIGHT

def intro_screen(DISPLAY_WIDTH, DISPLAY_HEIGHT, screen, logo, game_title):
    #Black Screen
    screen.fill((0, 0, 0))

    # Scale the logo
    scaled_logo = pygame.transform.scale(logo, (logo.get_width() * 5, logo.get_height() * 5))

    # Create a font object for the game title
    font = pygame.font.Font(FONT, 72)
    # Create a surface for the game title
    title_surf = font.render(game_title, True, (255, 255, 255))

    # Calculate the positions of the logo and game title
    total_width = scaled_logo.get_width() + title_surf.get_width()
    logo_pos = ((DISPLAY_WIDTH - total_width) // 2, (DISPLAY_HEIGHT - scaled_logo.get_height()) // 2)
    title_pos = (logo_pos[0] + scaled_logo.get_width(), (DISPLAY_HEIGHT - title_surf.get_height()) // 2)

    # Draw the logo and game title onto the screen
    screen.blit(scaled_logo, logo_pos)
    screen.blit(title_surf, title_pos)

    # Update the display
    pygame.display.flip()

    # Wait for any key press or mouse click
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                running = False
                break

def game_loop(running, screen, clock, game_theme, high_scores, difficulty_value):
    # Initialize colors and game objects
    background_color, snake_color, food_color = game_theme["background_color"], game_theme["snake_color"], game_theme["food_color"]
    snake = Snake(SNEK_START_LEN)
    food = Food(snake)

    total_food = 0
    munch = 0 
    score = 0 # initial score value
    snake_length = len(snake.body)

    game_over = False

    # Create a custom event for snake growth
    GROWTH_EVENT = pygame.USEREVENT + 1
    growth_counter = 0

    # Main game loop
    while not game_over:
        # Handle events
        for event in pygame.event.get():
            # Handle quit event
            if (event.type == pygame.QUIT):
                running = False
                game_over = True
            # Handle the growth event
            if event.type == GROWTH_EVENT:
                snake.grow()
                growth_counter -= 1
                if growth_counter <= 0:
                    pygame.time.set_timer(GROWTH_EVENT, 0)  # Stop the timer
            # Handle keydown events for snake movement and quitting
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    game_over = True
                    break
                if (event.key == pygame.K_UP or event.key == pygame.K_w) and snake.direction != (0, 1):
                    snake.change_direction((0, -1))
                if (event.key == pygame.K_DOWN or event.key == pygame.K_s) and snake.direction != (0, -1):
                    snake.change_direction((0, 1))
                if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and snake.direction != (1, 0):
                    snake.change_direction((-1, 0))
                if (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and snake.direction != (-1, 0):
                    snake.change_direction((1, 0))

        snake.move()

        # Check for collisions with food and grow snake
        if snake.collides_with(food.position):
            growth_counter = SNEK_MULTIPLIER
            munch_sound = pygame.mixer.Sound(munch_file) # Load munch sound
            munch_sound.set_volume(0.25)
            munch_sound.play()
            pygame.time.set_timer(GROWTH_EVENT, 150, loops=growth_counter)
            food = Food(snake)

            if munch == 10:
                difficulty_value += 5 # increase speed every 10 foods
                score += round((len(snake.body) - snake_length) * 2.5) # double score bonus every 10 foods
                munch -= 10
            else:
                score += round((len(snake.body) - snake_length) * 1.25) # normal score increase
            
            # eating + 1
            total_food += 1
            munch += 1
        
        # Check for collisions with the snake itself
        if snake.collides_with(snake.body[0], ignore_head=True):
            game_over = True

        # Draw solid background
        screen.fill(background_color)

        # Draw snake
        for i, segment in enumerate(snake.body):
            segment_alpha = 100 - int(0.5 * 100 * (i / (len(snake.body) - 1)))
            segment_color = hex_to_rgb(snake_color)
            draw_cell(screen, segment, segment_color, glow_color=segment_color, alpha=segment_alpha)

        #Draw food
        draw_cell(screen, food.position, food_color, glow_color=hex_to_rgb(food_color))

        # Update the display and control game speed
        pygame.display.flip()
        clock.tick(difficulty_value)

    return running, score, background_color, snake_color, high_scores

def game_over(running, restart, GRID_WIDTH, GRID_HEIGHT, screen, score, high_scores, snake_color, background_color):
    # Get player initials after game over
    initials = get_initials(GRID_WIDTH, GRID_HEIGHT, screen, color = snake_color, background_color = background_color)

    high_scores.append((score, initials))
    high_scores.sort(reverse=True)
    high_scores = high_scores[:10]

    # Save high scores to file
    save_high_scores(high_scores)

    # Redrawing background to display "Game Over" screen
    screen.fill(background_color)

    # Set up the font and create text surfaces
    font = pygame.font.Font(FONT, 16)
    text_game_over = font.render("Game Over!", True, snake_color, background_color)
    text_restart = font.render("Press R to restart or Q to quit.", True, snake_color, background_color)
    text_score = font.render(f"Score: {score}", True, snake_color, background_color)

    # Set the position of the text surfaces
    text_game_over_rect = text_game_over.get_rect(center=(GRID_WIDTH * CELL_SIZE // 2, GRID_HEIGHT * CELL_SIZE // 2 - 40))
    text_restart_rect = text_restart.get_rect(center=(GRID_WIDTH * CELL_SIZE // 2, GRID_HEIGHT * CELL_SIZE // 2 - 20))
    text_score_rect = text_score.get_rect(center=(GRID_WIDTH * CELL_SIZE // 2, GRID_HEIGHT * CELL_SIZE // 2))

    # Create the "High Scores" button
    high_scores_button = Button(
        (GRID_WIDTH * CELL_SIZE // 2) - 100, 
        GRID_HEIGHT * CELL_SIZE // 2 + 30, 
        200, 50, 
        "High Scores", 
        function=lambda: show_high_scores_screen(screen, high_scores, background_color, snake_color), 
        color=hex_to_rgb(snake_color), 
        text_color=hex_to_rgb(background_color))

    # "Change Theme" button
    theme_select_button = Button(
        (GRID_WIDTH * CELL_SIZE // 2) - 100, 
        GRID_HEIGHT * CELL_SIZE // 2 + 90, 
        200, 50, 
        "Change Theme", 
        function=lambda: setattr(restart, 'new_theme', theme_menu(GRID_WIDTH, GRID_HEIGHT, screen, background_color)), 
        color=hex_to_rgb(snake_color), 
        text_color=hex_to_rgb(background_color))

    # "Change Difficulty" button
    diff_select_button = Button(
        (GRID_WIDTH * CELL_SIZE // 2) - 100, 
        GRID_HEIGHT * CELL_SIZE // 2 + 150, 
        200, 50, 
        "Change Difficulty", 
        function=lambda: setattr(restart, 'new_difficulty', diff_menu(GRID_WIDTH, GRID_HEIGHT, screen, background_color)), 
        color=hex_to_rgb(snake_color), 
        text_color=hex_to_rgb(background_color))

    # Loop to handle input events for restarting or quitting
    while True:
        for event in pygame.event.get():
            # Handle quit event
            if event.type == pygame.QUIT:
                running = False
                break
            # Handle keydown events for restarting and quitting
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    restart.value = True
                    break
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
            # Update the "High Scores" button
            high_scores_button.update(screen, event)
            # Update the "Change Theme" button
            theme_select_button.update(screen, event)
            # Update the "Change Difficulty" button
            diff_select_button.update(screen, event)

        # Break the loop if restarting or not running
        if restart.value or not running:
            break
        
        # Draw the text surfaces on the screen
        screen.blit(text_game_over, text_game_over_rect)
        screen.blit(text_restart, text_restart_rect)
        screen.blit(text_score, text_score_rect)

        # Update the display
        pygame.display.flip()
    
    return running, restart

def main(GRID_WIDTH, GRID_HEIGHT):
    pygame.mixer.music.load(music_file)
    pygame.display.set_icon(snake_logo) # Set snake logo as window icon
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE), pygame.FULLSCREEN) # Create a full screen view
    pygame.display.set_caption("Snake.") # PyGame screen title
    clock = pygame.time.Clock() # Initialize game time
    pygame.mixer.music.play(-1) # Loop theme song

    ### Intro Screen
    intro_screen(DISPLAY_WIDTH, DISPLAY_HEIGHT, screen, snake_logo, "Snake.")

    game_theme = theme_menu(GRID_WIDTH, GRID_HEIGHT, screen) # Show theme select menu
    difficulty_value = diff_menu(GRID_WIDTH, GRID_HEIGHT, screen) # Show difficulty select menu

    #### ALL-TIME SCORES RECORD
    check_and_create_highscores_file(HIGH_SCORES_FILE)
    high_scores = []

    # Load high scores from file
    if os.path.exists(HIGH_SCORES_FILE):
        with open(HIGH_SCORES_FILE, "r") as file:
            high_scores = [tuple(line.strip().split(",")) for line in file]
            high_scores = [(int(score), initials) for score, initials in high_scores]

    running = True

    # Main game loop
    while running:
        restart = Restart()

        # Play the game and update high scores
        running, score, background_color, snake_color, high_scores = game_loop(running, screen, clock, game_theme, high_scores, difficulty_value)

        # Display a "Game Over" screen
        if running:
            running, restart = game_over(running, restart, GRID_WIDTH, GRID_HEIGHT, screen, score, high_scores, snake_color, background_color)
            
            if restart.value:
                game_theme = restart.new_theme if restart.new_theme is not None else game_theme
                difficulty_value = restart.new_difficulty if restart.new_difficulty is not None else difficulty_value

                ### Re-Play Intro Screen
                intro_screen(DISPLAY_WIDTH, DISPLAY_HEIGHT, screen, snake_logo, "Snake.")
                restart = Restart()  # Reset the restart object for the next game

if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    DISPLAY_WIDTH, DISPLAY_HEIGHT = get_display_info()
    # Calculate grid dimensions based on the display size and cell size
    GRID_WIDTH = DISPLAY_WIDTH // CELL_SIZE
    GRID_HEIGHT = DISPLAY_HEIGHT // CELL_SIZE
    # Play Snake
    main(GRID_WIDTH, GRID_HEIGHT)
    pygame.quit()