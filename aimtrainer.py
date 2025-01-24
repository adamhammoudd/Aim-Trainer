# Description: A simple aim trainer game built using Pygame
# Importing the necessary libraries
import math
import random
import time
import pygame
import json
import sys
import os
pygame.init()

# Path to the high_scores.json file in the user's home directory
high_scores_path = os.path.join(os.path.expanduser("~"), "high_scores.json")

# Constants
WIDTH, HEIGHT = 1200, 700 # The width and height of the window

WIN = pygame.display.set_mode((WIDTH, HEIGHT)) # Create the window
pygame.display.set_caption("🎯 Aim Trainer") # Set the title of the window

TARGET_INCREMENT =  0 # The time interval between each target
INCREMENT_LABEL = "" # The label for the target increment
TARGET_EVENT = pygame.USEREVENT # The event to create a new target

TARGET_PADDING = 30 # The padding around the target

BG_COLOR = (0, 25, 40) # The background color
LIVES = 3 # The number of lives
TOP_BAR_HEIGHT = 50 # The height of the top bar

LABEL_FONT = pygame.font.SysFont("comicsans", 24) # The font for labels
TITLE_FONT = pygame.font.SysFont("comicsans", 48) # The font for titles
H1_FONT = pygame.font.SysFont("comicsans", 36) # The font for headings

# Global variables
player_name = "" # The name of the player
high_scores = {} # The high scores of the players

# Classes
class Target:
    # Constants
    MAX_SIZE = 30 # The maximum size of the target
    GROWTH_RATE = 0.2 # The rate at which the target grows
    COLOR = "red" # The color of the target
    SECOND_COLOR = "white" # The second color of the target

    # Constructor
    def __init__(self, x, y):
        self.x = x # The x-coordinate of the target
        self.y = y # The y-coordinate of the target
        self.size = 0  # The size of the target
        self.grow = True # Whether the target is growing or shrinking
    
    # Function to update the target
    def update(self):
        if self.size + self.GROWTH_RATE >= self.MAX_SIZE:
            self.grow = False # Stop growing if the target reaches the maximum size
        
        if self.grow:
            self.size += self.GROWTH_RATE # Increase the size of the target
        else:
            self.size -= self.GROWTH_RATE # Decrease the size of the target

    # Function to draw the target    
    def draw(self, win):
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size)
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), self.size * 0.8)
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size * 0.6)
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), self.size * 0.4)
    
    # Function to check if the target has been clicked
    def collide(self, x, y):
        dis = math.sqrt((self.x - x)**2 + (self.y - y)**2) # Calculate the distance between the target and the click
        return dis <= self.size # Return True if the distance is less than the size of the target

# Functions

# Function to draw the game
def draw(win, targets):
    # Fill the background
    win.fill(BG_COLOR)

    # Draw the targets
    for target in targets:
        target.draw(win)

# Function to format time in minutes, seconds and milliseconds
def format_time(secs):
    milli = math.floor(int(secs * 1000 % 1000 / 100)) # Calculate milliseconds
    seconds = int(round(secs % 60, 1))  # Calculate seconds
    minutes = int(secs // 60) # Calculate minutes

    return f"{minutes:02d}:{seconds:02d}:{milli}" # Return the formatted time

# Function to draw the top bar
def draw_top_bar(win, elapsed_time, targets_pressed, misses):
    # Draw the top bar
    pygame.draw.rect(win, "grey", (0, 0, WIDTH, TOP_BAR_HEIGHT))
    time_label = LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", 1, "black")

    # Calculate the speed
    speed = round(targets_pressed // elapsed_time, 1)

    #Labels
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "black")
    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "black")
    lives_label = LABEL_FONT.render(f"Lives: {LIVES - misses}", 1, "black")
    settings_label = LABEL_FONT.render("Options", 1, "black")

    # Draw the labels
    win.blit(time_label, (5, 5))
    win.blit(speed_label, (245, 5))
    win.blit(hits_label, (485, 5))
    win.blit(lives_label, (730, 5))
    win.blit(settings_label, (975, 5))

# Function to display the home screen
def home_screen(win, difficulty):
    # Global variables
    global player_name
    run = True
    user_input = ""
    difficulty = None
    is_displayed_name = False
    is_displayed_difficulty = False

    # Event Handling
    while run:
        # Background
        win.fill(BG_COLOR)

        # Title
        title_label = TITLE_FONT.render("Aim Trainer", 1, "white")
        win.blit(title_label, (get_middle(title_label), 150))

        # Ask for player's name
        name_label = LABEL_FONT.render("Enter your name:", 1, "white")
        win.blit(name_label, (WIDTH // 2 - 100, 375))

        # Input Box
        input_box = pygame.Rect(WIDTH // 2 - name_label.get_width() // 2, 425, 200, 40)
        pygame.draw.rect(win, "white", input_box, 2)

        # Render the user input
        text_surface = LABEL_FONT.render(user_input, True, "white")
        win.blit(text_surface, (input_box.x + 10, input_box.y + 5))

        # Difficulty Buttons
        difficulty_label = LABEL_FONT.render("Select Difficulty:", 1, "white")
        win.blit(difficulty_label, (WIDTH // 2 - 100, 500))

        button_width, button_height = 150, 50
        border_width = 5  # Thickness of the border
        easy_button = pygame.Rect(325, 550, button_width, button_height)
        medium_button = pygame.Rect(525, 550, button_width, button_height)
        hard_button = pygame.Rect(725, 550, button_width, button_height)

        # Draw the buttons
        pygame.draw.rect(win, BG_COLOR if difficulty == "easy" else "white", easy_button)
        pygame.draw.rect(win, "white" if difficulty == "easy" else BG_COLOR, easy_button, border_width)  # Black border for Easy
        
        pygame.draw.rect(win, BG_COLOR if difficulty == "medium" else "white", medium_button)
        pygame.draw.rect(win, "white" if difficulty == "medium" else BG_COLOR, medium_button, border_width)  # Black border for Medium
        
        pygame.draw.rect(win, BG_COLOR if difficulty == "hard" else "white", hard_button)
        pygame.draw.rect(win, "white" if difficulty == "hard" else BG_COLOR, hard_button, border_width)  # Black border for Hard

        easy_label = LABEL_FONT.render("Easy", 1, "white" if difficulty == "easy" else BG_COLOR)
        medium_label = LABEL_FONT.render("Medium", 1, "white" if difficulty == "medium" else BG_COLOR)
        hard_label = LABEL_FONT.render("Hard", 1, "white" if difficulty == "hard" else BG_COLOR)

        win.blit(easy_label, (easy_button.x + button_width // 2 - easy_label.get_width() // 2, 
                              easy_button.y + button_height // 2 - easy_label.get_height() // 2))
        win.blit(medium_label, (medium_button.x + button_width // 2 - medium_label.get_width() // 2, 
                                medium_button.y + button_height // 2 - medium_label.get_height() // 2))
        win.blit(hard_label, (hard_button.x + button_width // 2 - hard_label.get_width() // 2, 
                              hard_button.y + button_height // 2 - hard_label.get_height() // 2))

        # Start Button
        start_button_width, start_button_height = 200, 50
        start_button_x = WIDTH // 2 - start_button_width // 2
        start_button_y = 300
        pygame.draw.rect(win, "white", (start_button_x, start_button_y, start_button_width, start_button_height))
        start_button_text = LABEL_FONT.render("Start", 1, BG_COLOR)
        win.blit(start_button_text, (start_button_x + start_button_width // 2 - start_button_text.get_width() // 2, 
                               start_button_y + start_button_height // 2 - start_button_text.get_height() // 2))
        
        # Function to set the target increment based on the difficulty
        def set_target_increment(difficulty):
            global TARGET_INCREMENT
            global INCREMENT_LABEL
            if difficulty == "easy":
                TARGET_INCREMENT = 600
                INCREMENT_LABEL = "Easy"
            elif difficulty == "medium":
                TARGET_INCREMENT = 400
                INCREMENT_LABEL = "Medium"
            elif difficulty == "hard":
                TARGET_INCREMENT = 250
                INCREMENT_LABEL = "Hard"

       # Render error messages
        if is_displayed_name:
            error_message_name = LABEL_FONT.render("Please enter your name.", 1, "red")
            win.blit(error_message_name, (WIDTH // 2 - error_message_name.get_width() // 2, 465))

        if is_displayed_difficulty:
            error_message_difficulty = LABEL_FONT.render("Please select a difficulty.", 1, "red")
            win.blit(error_message_difficulty, (WIDTH // 2 - error_message_difficulty.get_width() // 2, 600))


        # Update the display
        pygame.display.update()

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Difficulty Selection
                if easy_button.collidepoint(mouse_x, mouse_y):
                    difficulty = "easy"
                elif medium_button.collidepoint(mouse_x, mouse_y):
                    difficulty = "medium"
                elif hard_button.collidepoint(mouse_x, mouse_y):
                    difficulty = "hard"

                # Start Game
                if start_button_x <= mouse_x <= start_button_x + start_button_width and start_button_y <= mouse_y <= start_button_y + start_button_height:
                    is_displayed_name = not user_input.strip()  # Show error if name is empty
                    is_displayed_difficulty = not difficulty    # Show error if difficulty not selected
                    if not is_displayed_name and not is_displayed_difficulty:
                        player_name = user_input.strip()
                        set_target_increment(difficulty)
                        run = False  # Exit the loop
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:  # Handle backspace
                    user_input = user_input[:-1]    # Remove the last character
                else:
                    user_input += event.unicode # Add the character to the user input

# Function to display the options screen
def options_screen(win):
    # Global variables
    win.fill(BG_COLOR)

    # Title
    title_label = TITLE_FONT.render("Options", 1, "white")
    win.blit(title_label, (get_middle(title_label), 150))

    # Continue Button
    continue_width, continue_height = 200, 50
    continue_x = WIDTH // 2 - continue_width // 2
    continue_y = 250
    pygame.draw.rect(win, "white", (continue_x, continue_y, continue_width, continue_height))
    continue_text = LABEL_FONT.render("Continue", 1, BG_COLOR)
    win.blit(continue_text, (continue_x + continue_width // 2 - continue_text.get_width() // 2, 
                             continue_y + continue_height // 2 - continue_text.get_height() // 2))

    # Restart Button
    restart_width, restart_height = 200, 50
    restart_x = WIDTH // 2 - restart_width // 2
    restart_y = 400
    pygame.draw.rect(win, "white", (restart_x, restart_y, restart_width, restart_height))
    restart_text = LABEL_FONT.render("Restart", 1, BG_COLOR)
    win.blit(restart_text, (restart_x + restart_width // 2 - restart_text.get_width() // 2, 
                            restart_y + restart_height // 2 - restart_text.get_height() // 2))
    
    # Main Menu Button
    main_width, main_height = 200, 50
    main_x = WIDTH // 2 - main_width // 2
    main_y = 550
    pygame.draw.rect(win, "white", (main_x, main_y, main_width, main_height))
    main_text = LABEL_FONT.render("Main Menu", 1, BG_COLOR)
    win.blit(main_text, (main_x + main_width // 2 - main_text.get_width() // 2, 
                            main_y + main_height // 2 - main_text.get_height() // 2))

    run_options = True
    while run_options:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()   # Quit the game
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()   # Get the mouse position
                if continue_x <= mouse_x <= continue_x + continue_width and continue_y <= mouse_y <= continue_y + continue_height:
                    return  # Continue the game
                if restart_x <= mouse_x <= restart_x + restart_width and restart_y <= mouse_y <= restart_y + restart_height:
                    main()  # Restart the game
                if main_x <= mouse_x <= main_x + main_width and main_y <= mouse_y <= main_y + main_height: 
                    run_options = False
                    start_game()

        pygame.display.update() # Update the display

# Function to display the end screen
def end_screen(win, elapsed_time, targets_pressed, clicks, player_name, high_scores, difficulty, high_scores_dic):
    # Global variables
    win.fill(BG_COLOR)

    # Update high score for the current player
    if player_name in high_scores_dic:
        if clicks > high_scores_dic[player_name][0]:
            high_scores[player_name] = (clicks, difficulty) # Update the high score
    else:
        high_scores[player_name] = (clicks, difficulty) # Add the player to the high scores

    # Save the updated high scores
    save_high_scores()

    # Render the end screen
    title_label = TITLE_FONT.render("Game Over", 1, "white")
    stats_label = TITLE_FONT.render("Stats", 1, "white")
    time_label = LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", 1, "white")
    
    # Calculate the speed
    speed = round(targets_pressed // elapsed_time, 1)
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "white")
    
    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "white")

    # Calculate the accuracy
    if clicks == 0:
            accuracy = 0 # Prevent division by zero
    else:
        accuracy = round(targets_pressed / clicks * 100, 1)
    accuracy_label = LABEL_FONT.render(f"Accuracy: {accuracy}%", 1, "white") # Render the accuracy

    # Render the labels
    win.blit(title_label, (get_middle(title_label), 50))
    win.blit(stats_label, (150, 100))
    win.blit(time_label, (50, 200))
    win.blit(speed_label, (50, 300))
    win.blit(hits_label, (50, 400))
    win.blit(accuracy_label, (50, 500))

    # Render high scores
    high_scores_label = TITLE_FONT.render("High Scores", 1, "white")
    sorted_scores = sorted(high_scores_dic.items(), key=lambda x: x[1], reverse=True)  # Sort by score
    win.blit(high_scores_label, (get_middle(title_label) + 350, 100))
    for idx, (player_name, (high_scores, difficulty)) in enumerate(sorted_scores):
        score_label = LABEL_FONT.render(f"{idx + 1}. {player_name} ({difficulty}): {high_scores}", 1, "white") # Render the high scores
        win.blit(score_label, (850, 200 + idx * 30)) # Position the high scores
        if idx + 1 == 5:
            win.blit(LABEL_FONT.render("", 1, "white"), (850, 200 + (idx + 1) * 30)) # Render the ellipsis
            break

    # Main Button
    main_button_width, main_button_height = 200, 50
    main_button_x = WIDTH // 2 - main_button_width // 2
    main_button_y = 600
    pygame.draw.rect(win, "white", (main_button_x, main_button_y, main_button_width, main_button_height)) # Draw the button
    main_button_text = LABEL_FONT.render("Main Menu", 1, BG_COLOR)
    win.blit(main_button_text, (main_button_x + main_button_width // 2 - main_button_text.get_width() // 2, 
                               main_button_y + main_button_height // 2 - main_button_text.get_height() // 2)) # Position the button
    
    # Reset High Score Button
    reset_high_score_button_width, reset_high_score_button_height = 200, 50
    reset_high_score_button_x = 850
    reset_high_score_button_y = 600
    pygame.draw.rect(win, "white", (reset_high_score_button_x, reset_high_score_button_y, reset_high_score_button_width, reset_high_score_button_height)) # Draw the button
    reset_high_score_button_text = LABEL_FONT.render("Reset High Score", 1, BG_COLOR)
    win.blit(reset_high_score_button_text, (reset_high_score_button_x + reset_high_score_button_width // 2 - reset_high_score_button_text.get_width() // 2, 
                               reset_high_score_button_y + reset_high_score_button_height // 2 - reset_high_score_button_text.get_height() // 2)) # Position the button

    pygame.display.update() # Update the display

    run_end = True
    while run_end:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Handle window close button
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:  # Handle mouse clicks
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if main_button_x <= mouse_x <= main_button_x + main_button_width and main_button_y <= mouse_y <= main_button_y + main_button_height:
                    run_end = False
                    start_game()

                if reset_high_score_button_x <= mouse_x <= reset_high_score_button_x + reset_high_score_button_width and reset_high_score_button_y <= mouse_y <= reset_high_score_button_y + reset_high_score_button_height:
                    win.fill(BG_COLOR)  # Clear the screen

                    title_label = H1_FONT.render("Are you sure you want to reset your high scores?", 1, "white")
                    win.blit(title_label, (get_middle(title_label), 150))

                    # Yes Button
                    yes_button_width, yes_button_height = 200, 50
                    yes_button_x = 325
                    yes_button_y = 400
                    pygame.draw.rect(win, "white", (yes_button_x, yes_button_y, yes_button_width, yes_button_height)) # Draw the button
                    yes_button_text = LABEL_FONT.render("Yes", 1, BG_COLOR)
                    win.blit(yes_button_text, (yes_button_x + yes_button_width // 2 - yes_button_text.get_width() // 2, 
                               yes_button_y + yes_button_height // 2 - yes_button_text.get_height() // 2)) # Position the button

                    # No Button
                    no_button_width, no_button_height = 200, 50
                    no_button_x = 725
                    no_button_y = 400
                    pygame.draw.rect(win, "white", (no_button_x, no_button_y, no_button_width, no_button_height)) # Draw the button
                    no_button_text = LABEL_FONT.render("No", 1, BG_COLOR)
                    win.blit(no_button_text, (no_button_x + no_button_width // 2 - no_button_text.get_width() // 2, 
                               no_button_y + no_button_height // 2 - no_button_text.get_height() // 2)) # Position the button
                    pygame.display.update() # Update the display

                    confirm_reset = True
                    while confirm_reset:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:  # Handle window close button
                                pygame.quit()
                                exit()
                            if event.type == pygame.MOUSEBUTTONDOWN:  # Handle mouse clicks
                                mouse_x, mouse_y = pygame.mouse.get_pos()
                                if yes_button_x <= mouse_x <= yes_button_x + yes_button_width and yes_button_y <= mouse_y <= yes_button_y + yes_button_height:
                                    high_scores_dic.clear()  # Clear the high scores
                                    save_high_scores()  # Save the empty high scores
                                    confirm_reset = False
                                    run_end = False
                                    start_game()  # Restart the game

                                if no_button_x <= mouse_x <= no_button_x + no_button_width and no_button_y <= mouse_y <= no_button_y + no_button_height:
                                    confirm_reset = False
                                    end_screen(win, elapsed_time, targets_pressed, clicks, player_name, high_scores, difficulty, high_scores_dic)  # Display the end screen

# Function to get the middle of the screen
def get_middle(surface):
    return WIDTH / 2 - surface.get_width()/2 # Return the middle of the screen

# Function to load high scores from a JSON file
def load_high_scores():
    # Global variables
    global high_scores 
    try:
        with open(high_scores_path, "r") as file:
            high_scores = json.load(file) # Load the high scores from the file
            high_scores = {player: tuple(data) for player, data in high_scores.items()}
    except FileNotFoundError:
        high_scores = {} # Create an empty dictionary if the file does not exist

# Function to save high scores to a JSON file
def save_high_scores():
    with open(high_scores_path, "w") as file:
        json.dump(high_scores, file) # Save the high scores to the file

# Main function
def main():
    # Global variables
    load_high_scores()  # Load high scores at the start
    run_main = True
    targets = []
    clock = pygame.time.Clock()
    global run_end
    global run_options

    # Reset the game variables
    targets_pressed = 0
    clicks = 0
    misses = 0
    start_time = time.time()

    pygame.time.set_timer(TARGET_EVENT, TARGET_INCREMENT)

    # Game loop
    while run_main:
        # Set the frame rate
        clock.tick(60)
        click = False
        mouse_pos = pygame.mouse.get_pos()
        elapsed_time = time.time() - start_time
        
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False # Exit the game
                break
            
            # Check if the target event is triggered
            if event.type == TARGET_EVENT:
                x = random.randint(TARGET_PADDING, WIDTH - TARGET_PADDING) # Generate a random x-coordinate
                y = random.randint(TARGET_PADDING + TOP_BAR_HEIGHT, HEIGHT - TARGET_PADDING) # Generate a random y-coordinate
                target = Target(x, y) # Create a new target
                targets.append(target) # Add the target to the list
            
            # Check if the mouse is clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True # Set click to True
                clicks += 1 # Increment the number of clicks

                # Check if settings button is clicked
                if 975 <= mouse_pos[0] <= 975 + 100 and 5 <= mouse_pos[1] <= 5 + 30:
                    options_screen(WIN) # Display the options screen

        # Update the targets
        for target in targets:
            target.update() # Update the target

            # Check if the target is out of bounds
            if target.size <= 0:
                targets.remove(target) # Remove the target
                misses += 1 # Increment the number of misses

            # Check if the target is clicked
            if click and target.collide(*mouse_pos):
                targets.remove(target) # Remove the target
                targets_pressed += 1 # Increment the number of targets pressed

        # Check if the player has lost
        if misses >= LIVES:
            end_screen(WIN, elapsed_time, targets_pressed, clicks, player_name, high_scores, INCREMENT_LABEL, high_scores) # Display the end screen

        draw(WIN, targets) # Draw the game
        draw_top_bar(WIN, elapsed_time, targets_pressed, misses) # Draw the top bar
        load_high_scores() # Load the high scores
        pygame.display.update() # Update the display


# Entry point
def start_game():
    if __name__ == "__main__":
        home_screen(WIN, TARGET_INCREMENT) # Display the home screen
        main() # Start the game

start_game()
