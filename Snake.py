# # Snake Game Created with ChatGPT-4

# ### Message from ChatGPT
# This code provides a basic snake game with a simple retro style. 
# You can run the code, and it will display a snake game window with a white background, a green snake, and red food. 
# Use the arrow keys to control the snake. 
# If you want to modify the game's appearance or behavior further, you can do so by changing the constants, colors, or other parts of the code.

# Some ideas for expanding the game or enhancing its retro style:

# 1. ~~Add a score display that shows the player's current score, which could be based on the snake's length.~~
# 2. ~~Add a game over screen with the option to restart the game.~~
# 3. ~~Implement different levels of difficulty, such as faster snake movement~~ or additional obstacles.
# 4. Add sounds or music to create a more immersive experience.
# 5. Create a retro-style pixel art for the snake, food, and background.
# 6. Customize the game window's appearance, such as adding a retro border or ~~using a pixelated font.~~

# Feel free to experiment and modify the code as needed to create the snake game you envision.

#### Imports
import pygame
import pygame.gfxdraw
import sys
import random
import os

#### Game Parameters
# Game constants
SNEK_START_LEN = 1 # Initial snake length
SNEK_MULTIPLIER = 3 # Amount snake grows after eating food
CELL_SIZE = 40 # Size of each grid cell
GRID_WIDTH = 30 # Grid width (number of cells)
GRID_HEIGHT = 20 # Grid height (number of cells)
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
        # Initial Snake Size
        for _ in range(start_len):
            self.grow()

    def move(self):
        # Calculate new head position based on current head position and direction
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = ((head_x + dir_x) % GRID_WIDTH, (head_y + dir_y) % GRID_HEIGHT)
        # Insert new head position at the beginning of the body and remove the last element
        self.body.insert(0, new_head)
        self.body.pop()

    def change_direction(self, new_direction):
        self.direction = new_direction # Update the snake's direction

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
    def __init__(self, x, y, width, height, text, function=None, color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height) # Button rectangle
        self.text = text # Button text
        self.function = function # Function to call when the button is clicked
        self.color = color # Button color
        # Calculate the highlighted color when the mouse is over the button
        self.highlighted_color = tuple([min(c + 50, 255) for c in self.color])
        self.font = pygame.font.Font("PressStart2P-Regular.ttf", 16) # Button font
        self.image = pygame.Surface((width, height)) # Button surface
        self.text_surface = self.font.render(self.text, True, (0, 0, 0)) # Rendered text surface
        self.text_rect = self.text_surface.get_rect(center=(width // 2, height // 2)) # Text rectangle

    # Update the button state and check for mouse clicks
    def update(self, screen, event):
        self.draw(screen)
        # Check if the button was clicked
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(pygame.mouse.get_pos()):
            if self.function:
                return self.function()

    # Draw the button on the screen
    def draw(self, screen):
        # Check if the mouse is over the button and change its color accordingly
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.image.fill(self.highlighted_color)
        else:
            self.image.fill(self.color)

        # Draw the button text
        if self.text:
            self.image.blit(self.text_surface, self.text_rect)

        # Draw the button surface on the screen
        screen.blit(self.image, self.rect.topleft)

#### Main Functions
# Function to display pre-game selection menus
def display_menu(screen, title, themes):
    # Menu button parameters
    button_width = 200
    button_height = 40
    button_spacing = 10
    total_buttons_height = len(themes) * button_height + (len(themes) - 1) * button_spacing
    start_y = (GRID_HEIGHT * CELL_SIZE - total_buttons_height) // 2

    # Create menu buttons
    menu_buttons = []
    for i, theme_name in enumerate(themes):
        button_x = (GRID_WIDTH * CELL_SIZE - button_width) // 2
        button_y = start_y + i * (button_height + button_spacing)
        menu_buttons.append(Button(button_x, button_y, button_width, button_height, theme_name, function=lambda i=i: i))
    
    # Function to draw buttons on the screen
    def draw_buttons(screen, menu_buttons):
        for button in menu_buttons:
            button.draw(screen)

    # Main menu loop
    menu_running = True
    while menu_running:
        screen.fill((0, 0, 0))

        # Display title text
        font_title = pygame.font.Font("PressStart2P-Regular.ttf", 24)
        text_title = font_title.render(str(title), True, (255, 255, 255))
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

def check_and_create_highscores_file(file_name):
    if not os.path.exists(file_name):
        with open(file_name, "w") as file:
            file.write(f"0\n0\n0\n0\n0\n0\n0\n0\n0\n0")

def save_high_scores(high_scores):
    with open(HIGH_SCORES_FILE, "w") as file:
        for score in high_scores:
            file.write(f"{score}\n")

def show_high_scores_screen(screen, high_scores, background_color, food_color):
    # Fill the screen with background color
    screen.fill(background_color)

    font = pygame.font.Font("PressStart2P-Regular.ttf", 36)
    text = font.render("High Scores", 1, background_color, food_color)
    screen.blit(text, (250, 50))

    # Display high scores
    y_offset = 100
    for index, score in enumerate(high_scores):
        text = font.render(f"{index + 1}. {score}", 1, background_color, food_color)
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

def draw_cell(screen, pos, color, glow_color=None, glow_radius=35, glow_alpha=35, alpha=100):
    if glow_color:
        x, y = pos
        draw_glowing_circle(screen, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), glow_radius, glow_color, alpha)

    x, y = pos
    cell_margin = 2

    if len(color) == 3:
        color = (*color, alpha)
    elif len(color) == 4:
        color = (*color[:3], alpha)

    pygame.draw.rect(screen, color, (x * CELL_SIZE + cell_margin, y * CELL_SIZE + cell_margin, CELL_SIZE - 2 * cell_margin, CELL_SIZE - 2 * cell_margin))

def hex_to_rgb(hex_color):
    return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

def game_loop(running, screen, clock, theme, high_scores, SPEED):
    # Initialize colors and game objects
    background_color, snake_color, food_color = theme["background_color"], theme["snake_color"], theme["food_color"]
    snake = Snake(SNEK_START_LEN)
    food = Food(snake)
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
            pygame.time.set_timer(GROWTH_EVENT, 100, loops=growth_counter)
            food = Food(snake)
        
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
        clock.tick(SPEED)

    # Calculate the score
    score = round((len(snake.body) - SNEK_START_LEN) * 2.5)

    return running, score, background_color, snake_color, food_color, high_scores

def main(theme, high_scores, screen, clock, SPEED):
    running = True

    # Main game loop
    while running:
        # Play the game and update high scores
        running, score, background_color, snake_color, food_color, high_scores = game_loop(running, screen, clock, theme, high_scores, SPEED)
        high_scores.append(score)
        high_scores.sort(reverse=True)
        high_scores = high_scores[:10]

        # Save high scores to file
        save_high_scores(high_scores)

        # Display a "Game Over" screen
        if running:
            restart = False

            # Set up the font and create text surfaces
            font = pygame.font.Font("PressStart2P-Regular.ttf", 16)
            text_game_over = font.render("Game Over!", True, snake_color, background_color)
            text_restart = font.render("Press R to restart or Q to quit.", True, snake_color, background_color)
            text_score = font.render(f"Score: {score}", True, snake_color, background_color)
            
            # Set the position of the text surfaces
            text_game_over_rect = text_game_over.get_rect(center=(GRID_WIDTH * CELL_SIZE // 2, GRID_HEIGHT * CELL_SIZE // 2 - 40))
            text_restart_rect = text_restart.get_rect(center=(GRID_WIDTH * CELL_SIZE // 2, GRID_HEIGHT * CELL_SIZE // 2 - 20))
            text_score_rect = text_score.get_rect(center=(GRID_WIDTH * CELL_SIZE // 2, GRID_HEIGHT * CELL_SIZE // 2))
            
            # Create the "High Scores" button
            high_scores_button = Button((GRID_WIDTH * CELL_SIZE // 2) - 100, GRID_HEIGHT * CELL_SIZE // 2 + 30, 200, 50, "High Scores", function=lambda: show_high_scores_screen(screen, high_scores, background_color, food_color), color=hex_to_rgb(snake_color))

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
                            restart = True
                            break
                        if event.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()
                    # Update the "High Scores" button
                    high_scores_button.update(screen, event)

                # Break the loop if restarting or not running
                if restart or not running:
                    break
                
                # Draw the text surfaces on the screen
                screen.blit(text_game_over, text_game_over_rect)
                screen.blit(text_restart, text_restart_rect)
                screen.blit(text_score, text_score_rect)

                # Update the display
                pygame.display.flip()

    print("...bye")

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE)) # Create PyGame screen with prarameters defined at the top
    pygame.display.set_caption("Snake.") # PyGame screen title
    clock = pygame.time.Clock() # Initialize game time

    #### ALL-TIME SCORES RECORD
    HIGH_SCORES_FILE = "high_scores.txt" # Store high scores file as a variable
    check_and_create_highscores_file(HIGH_SCORES_FILE)
    high_scores = []

    # Theme Select Menu
    theme_names = list(theme_dict.keys()) # Get theme names from dictionary of themes
    selected_theme_index = display_menu(screen, "Select Theme", theme_names) # Display theme selection menu
    game_theme = theme_dict[theme_names[selected_theme_index]] # Store selected theme

    # Difficulty selection
    difficulty_index = display_menu(screen, "Select Difficulty", ["Easy", "Medium", "Hard"]) # Display difficulty selection menu
    difficulty_lambda = lambda index: {0: -10, 1: 0, 2: 10}[index]
    difficulty_value = difficulty_lambda(difficulty_index) # Convert button index into difficulty value and store as a variable

    # Load high scores from file
    if os.path.exists(HIGH_SCORES_FILE):
        with open(HIGH_SCORES_FILE, "r") as file:
            lines = file.readlines() # Read all lines in the file
            high_scores = [int(score) for score in lines] # Add each score to the high_scores list
 
    # Play Snake
    main(game_theme, high_scores, screen, clock, (SPEED + difficulty_value))

    pygame.quit()