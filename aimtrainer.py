import math
import random
import time
import pygame
import json
pygame.init()

HIGH_SCORE_FILE = "high_scores.txt"

WIDTH, HEIGHT = 1200, 700

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aim Trainer")

TARGET_INCREMENT = 500
TARGET_EVENT = pygame.USEREVENT

TARGET_PADDING = 30

BG_COLOR = (0, 25, 40)
LIVES = 3
TOP_BAR_HEIGHT = 50

LABEL_FONT = pygame.font.SysFont("comicsans", 24)
TITLE_FONT = pygame.font.SysFont("comicsans", 48)

player_name = ""
high_scores = {}

class Target:
    MAX_SIZE = 30
    GROWTH_RATE = 0.2
    COLOR = "red"
    SECOND_COLOR = "white"

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 0
        self.grow = True
    
    def update(self):
        if self.size + self.GROWTH_RATE >= self.MAX_SIZE:
            self.grow = False
        
        if self.grow:
            self.size += self.GROWTH_RATE
        else:
            self.size -= self.GROWTH_RATE
        
    def draw(self, win):
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size)
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), self.size * 0.8)
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size * 0.6)
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), self.size * 0.4)

    def collide(self, x, y):
        dis = math.sqrt((self.x - x)**2 + (self.y - y)**2)
        return dis <= self.size

def draw(win, targets):
    win.fill(BG_COLOR)

    for target in targets:
        target.draw(win)

def format_time(secs):
    milli = math.floor(int(secs * 1000 % 1000 / 100))
    seconds = int(round(secs % 60, 1))
    minutes = int(secs // 60)

    return f"{minutes:02d}:{seconds:02d}:{milli}"

def draw_top_bar(win, elapsed_time, targets_pressed, misses):
    pygame.draw.rect(win, "grey", (0, 0, WIDTH, TOP_BAR_HEIGHT))
    time_label = LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", 1, "black")

    speed = round(targets_pressed // elapsed_time, 1)
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "black")

    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "black")

    lives_label = LABEL_FONT.render(f"Lives: {LIVES - misses}", 1, "black")

    settings_label = LABEL_FONT.render("Settings", 1, "black")

    win.blit(time_label, (5, 5))
    win.blit(speed_label, (245, 5))
    win.blit(hits_label, (485, 5))
    win.blit(lives_label, (730, 5))
    win.blit(settings_label, (975, 5))

def home_screen(win):
    global player_name
    run = True
    user_input = ""
    while run:
        win.fill(BG_COLOR)

        # Title
        title_label = TITLE_FONT.render("Aim Trainer", 1, "white")
        win.blit(title_label, (get_middle(title_label), 150))

        # Ask for player's name
        name_label = LABEL_FONT.render("Enter your name:", 1, "white")
        win.blit(name_label, (WIDTH // 2 - 100, 400))

        input_box = pygame.Rect(WIDTH // 2 - name_label.get_width() // 2, 450, 200, 40)
        pygame.draw.rect(win, "white", input_box, 2)

        text_surface = LABEL_FONT.render(user_input, True, "white")
        win.blit(text_surface, (input_box.x + 10, input_box.y + 5))

        # Start Button
        button_width, button_height = 200, 50
        button_x = WIDTH // 2 - button_width // 2
        button_y = 300
        pygame.draw.rect(win, "white", (button_x, button_y, button_width, button_height))
        button_text = LABEL_FONT.render("Start", 1, BG_COLOR)
        win.blit(button_text, (button_x + button_width // 2 - button_text.get_width() // 2, 
                               button_y + button_height // 2 - button_text.get_height() // 2))

        pygame.display.update()

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if button_x <= mouse_x <= button_x + button_width and button_y <= mouse_y <= button_y + button_height:
                    if user_input.strip():  # Ensure the user has entered a valid name
                        player_name = user_input.strip()
                        run = False  # Exit home screen and start the game
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:  # Handle backspace
                    user_input = user_input[:-1]
                else:
                    user_input += event.unicode

def options_screen(win):
    win.fill(BG_COLOR)

    title_label = TITLE_FONT.render("Options", 1, "white")
    win.blit(title_label, (get_middle(title_label), 150))

    # Continue Button
    continue_width, continue_height = 200, 50
    continue_x = WIDTH // 2 - continue_width // 2
    continue_y = 300
    pygame.draw.rect(win, "white", (continue_x, continue_y, continue_width, continue_height))
    continue_text = LABEL_FONT.render("Continue", 1, BG_COLOR)
    win.blit(continue_text, (continue_x + continue_width // 2 - continue_text.get_width() // 2, 
                             continue_y + continue_height // 2 - continue_text.get_height() // 2))

    # Restart Button
    restart_width, restart_height = 200, 50
    restart_x = WIDTH // 2 - restart_width // 2
    restart_y = 450
    pygame.draw.rect(win, "white", (restart_x, restart_y, restart_width, continue_height))
    restart_text = LABEL_FONT.render("Restart", 1, BG_COLOR)
    win.blit(restart_text, (restart_x + restart_width // 2 - restart_text.get_width() // 2, 
                            restart_y + restart_height // 2 - restart_text.get_height() // 2))

    # Event Handling
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if continue_x <= mouse_x <= continue_x + continue_width and continue_y <= mouse_y <= continue_y + continue_height:
                    return  # Continue the game
                if restart_x <= mouse_x <= restart_x + restart_width and restart_y <= mouse_y <= restart_y + restart_height:
                    main()  # Restart the game

        pygame.display.update()


def end_screen(win, elapsed_time, targets_pressed, clicks, player_name, high_scores):
    win.fill(BG_COLOR)

    # Update high score for the current player
    if player_name in high_scores:
        if clicks > high_scores[player_name]:
            high_scores[player_name] = clicks
    else:
        high_scores[player_name] = clicks

    # Save the updated high scores
    save_high_scores()


    title_label = TITLE_FONT.render("Game Over", 1, "white")

    stats_label = TITLE_FONT.render("Stats", 1, "white")

    time_label = LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", 1, "white")

    speed = round(targets_pressed // elapsed_time, 1)
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "white")

    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "white")

    accuracy = round(targets_pressed / clicks * 100, 1)
    if clicks == 0:
        accuracy = 0
    accuracy_label = LABEL_FONT.render(f"Accuracy: {accuracy}%", 1, "white")

    win.blit(title_label, (get_middle(title_label), 50))
    win.blit(stats_label, (150, 100))

    win.blit(time_label, (50, 200))
    win.blit(speed_label, (50, 300))
    win.blit(hits_label, (50, 400))
    win.blit(accuracy_label, (50, 500))

    # Render high scores
    high_scores_label = TITLE_FONT.render("High Scores", 1, "white")
    win.blit(high_scores_label, (get_middle(title_label) + 350, 100))
    sorted_scores = sorted(high_scores.items(), key=lambda x: x[1], reverse=True)  # Sort by score
    for idx, (player_name, high_scores) in enumerate(sorted_scores):
        score_label = LABEL_FONT.render(f"{idx + 1}. {player_name}: {high_scores}", 1, "white")
        win.blit(score_label, (850, 200 + idx * 30))


    button_width, button_height = 200, 50
    button_x = WIDTH // 2 - button_width // 2
    button_y = 600
    pygame.draw.rect(win, "white", (button_x, button_y, button_width, button_height))
    button_text = LABEL_FONT.render("Restart", 1, BG_COLOR)
    win.blit(button_text, (button_x + button_width // 2 - button_text.get_width() // 2, 
                               button_y + button_height // 2 - button_text.get_height() // 2))

    pygame.display.update()

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if button_x <= mouse_x <= button_x + button_width and button_y <= mouse_y <= button_y + button_height:
                    main()  # Restart the game

def get_middle(surface):
    return WIDTH / 2 - surface.get_width()/2

def load_high_scores():
    global high_scores
    try:
        with open("high_scores.json", "r") as file:
            high_scores = json.load(file)
    except FileNotFoundError:
        high_scores = {}

# Function to save high scores to a JSON file
def save_high_scores():
    with open("high_scores.json", "w") as file:
        json.dump(high_scores, file)

def main():
    run = True
    targets = []
    clock = pygame.time.Clock()

    targets_pressed = 0
    clicks = 0
    misses = 0
    start_time = time.time()
    show_menu = False

    pygame.time.set_timer(TARGET_EVENT, TARGET_INCREMENT)

    while run:
        clock.tick(60)
        click = False
        mouse_pos = pygame.mouse.get_pos()
        elapsed_time = time.time() - start_time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            
            if event.type == TARGET_EVENT:
                x = random.randint(TARGET_PADDING, WIDTH - TARGET_PADDING)
                y = random.randint(TARGET_PADDING + TOP_BAR_HEIGHT, HEIGHT - TARGET_PADDING)
                target = Target(x, y)
                targets.append(target)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
                clicks += 1

                # Check if settings button is clicked
                if 975 <= mouse_pos[0] <= 975 + 100 and 5 <= mouse_pos[1] <= 5 + 30:
                    options_screen(WIN)

        for target in targets:
            target.update()

            if target.size <= 0:
                targets.remove(target)
                misses += 1

            if click and target.collide(*mouse_pos):
                targets.remove(target)
                targets_pressed += 1

        if misses >= LIVES:
            end_screen(WIN, elapsed_time, targets_pressed, clicks, player_name, high_scores)

        draw(WIN, targets)
        draw_top_bar(WIN, elapsed_time, targets_pressed, misses)
        load_high_scores()
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    home_screen(WIN)
    main()
