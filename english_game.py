import asyncio
import pygame
import sys
import random
import math
import numpy as np

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 1200, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fun English Learning Game")

# Colors
BACKGROUND = (230, 240, 255)
TEXT_COLOR = (50, 50, 120)
BUTTON_COLOR = (255, 180, 80)
BUTTON_HOVER = (255, 200, 100)
CORRECT_COLOR = (120, 220, 120)
WRONG_COLOR = (255, 120, 120)
INSTRUCTION_COLOR = (80, 80, 150)
AUDIO_ON_COLOR = (100, 200, 100)
AUDIO_OFF_COLOR = (200, 100, 100)
PROGRESS_COLOR = (100, 180, 255)

# Fonts
title_font = pygame.font.SysFont("Arial", 48, bold=True)
normal_font = pygame.font.SysFont("Arial", 32)
button_font = pygame.font.SysFont("Arial", 28)
instruction_font = pygame.font.SysFont("Arial", 20)

# Categories and words with definitions
categories = {
    "Animals": {
        "words": ["cat", "dog", "lion", "fish", "bird", "elephant", "monkey"],
        "definitions": {
            "cat": "A small domesticated carnivorous mammal with soft fur.",
            "dog": "A domesticated carnivorous mammal that typically has a long snout.",
            "lion": "A large, powerful cat that lives in parts of Africa and India.",
            "fish": "A limbless cold-blooded vertebrate animal with gills and fins.",
            "bird": "A warm-blooded egg-laying vertebrate with feathers and wings.",
            "elephant": "A very large plant-eating mammal with a prehensile trunk.",
            "monkey": "A primate, often with a long tail, typically living in trees."
        }
    },
    "Fruits": {
        "words": ["apple", "banana", "orange", "grape", "mango", "strawberry"],
        "definitions": {
            "apple": "A round fruit with red, green, or yellow skin and crisp flesh.",
            "banana": "A long curved fruit with a yellow skin and soft sweet flesh.",
            "orange": "A round juicy citrus fruit with a tough bright reddish-yellow rind.",
            "grape": "A small round fruit that grows in clusters on a vine.",
            "mango": "A tropical fruit with smooth yellow or red skin and sweet yellow flesh.",
            "strawberry": "A sweet soft red fruit with a seed-studded surface."
        }
    },
    "Colors": {
        "words": ["red", "blue", "green", "yellow", "purple", "pink"],
        "definitions": {
            "red": "The color of blood, rubies, or strawberries.",
            "blue": "The color of the sky or the sea on a sunny day.",
            "green": "The color of grass, leaves, or emeralds.",
            "yellow": "The color of lemons, butter, or ripe corn.",
            "purple": "A color intermediate between red and blue.",
            "pink": "A pale red color, named after the flower of the same name."
        }
    },
    "Shapes": {
        "words": ["circle", "square", "triangle", "star", "heart", "rectangle"],
        "definitions": {
            "circle": "A round plane figure whose boundary consists of points equidistant from the center.",
            "square": "A plane figure with four equal straight sides and four right angles.",
            "triangle": "A plane figure with three straight sides and three angles.",
            "star": "A shape that represents a star, typically having five or more points.",
            "heart": "A shape representing the human heart, often symbolizing love.",
            "rectangle": "A plane figure with four straight sides and four right angles."
        }
    }
}

# Game state
current_category = "Animals"
current_word = ""
score = 0
attempts = 0
max_attempts = 10
game_active = False
feedback = ""
feedback_time = 0
show_instructions = True
audio_enabled = True
show_definition = False
streak = 0
high_score = 0
difficulty = "Normal"
timer_active = False
time_left = 0
particles = []
word_images = {}

# Create colored placeholder images
def create_placeholder_images():
    images = {}
    color_map = {
        "Animals": (200, 150, 100),
        "Fruits": (255, 200, 150),
        "Colors": (200, 200, 255),
        "Shapes": (200, 255, 200)
    }
    
    for category, data in categories.items():
        base_color = color_map[category]
        for word in data["words"]:
            img = pygame.Surface((150, 150))
            # Create a slightly varied color for each word
            color = (
                max(50, min(255, base_color[0] + random.randint(-30, 30))),
                max(50, min(255, base_color[1] + random.randint(-30, 30))),
                max(50, min(255, base_color[2] + random.randint(-30, 30)))
            )
            img.fill(color)
            
            # Add text to the image
            font = pygame.font.SysFont("Arial", 20)
            text = font.render(word, True, (0, 0, 0))
            text_rect = text.get_rect(center=(75, 75))
            img.blit(text, text_rect)
            
            images[word] = img
    
    return images

# Generate simple sound effects
def generate_sounds():
    sounds = {}
    
    # Correct sound (rising tone)
    sample_rate = 44100
    duration = 0.5
    samples = int(sample_rate * duration)
    
    # Generate correct sound (rising pitch)
    correct_buffer = np.zeros((samples, 2), dtype=np.int16)
    for i in range(samples):
        freq = 440 + (i / samples) * 440
        value = int(32767 * math.sin(2.0 * math.pi * freq * i / sample_rate))
        correct_buffer[i][0] = value
        correct_buffer[i][1] = value
    sounds["correct"] = pygame.sndarray.make_sound(correct_buffer)
    
    # Wrong sound (falling pitch)
    wrong_buffer = np.zeros((samples, 2), dtype=np.int16)
    for i in range(samples):
        freq = 880 - (i / samples) * 440
        value = int(32767 * math.sin(2.0 * math.pi * freq * i / sample_rate))
        wrong_buffer[i][0] = value
        wrong_buffer[i][1] = value
    sounds["wrong"] = pygame.sndarray.make_sound(wrong_buffer)
    
    # Button click sound
    click_buffer = np.zeros((samples // 3, 2), dtype=np.int16)
    for i in range(samples // 3):
        freq = 330
        value = int(32767 * math.sin(2.0 * math.pi * freq * i / sample_rate))
        click_buffer[i][0] = value
        click_buffer[i][1] = value
    sounds["click"] = pygame.sndarray.make_sound(click_buffer)
    
    # Word sounds (simple tones for each word)
    for category, data in categories.items():
        for word in data["words"]:
            word_buffer = np.zeros((samples, 2), dtype=np.int16)
            freq = 300 + len(word) * 50
            for i in range(samples):
                value = int(32767 * math.sin(2.0 * math.pi * freq * i / sample_rate))
                word_buffer[i][0] = value
                word_buffer[i][1] = value
            sounds[word] = pygame.sndarray.make_sound(word_buffer)
    
    return sounds

# Create placeholder images
word_images = create_placeholder_images()

# Try to generate sounds, but continue without them if there's an error
try:
    sounds = generate_sounds()
except Exception as e:
    print(f"Could not generate sounds: {e}")
    sounds = {}
    audio_enabled = False

# Particle effect class
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 6)
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-3, 3)
        self.life = random.randint(20, 40)
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.size = max(0, self.size - 0.1)
        return self.life > 0
        
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = BUTTON_HOVER
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, (50, 50, 50), self.rect, 3, border_radius=12)
        
        text_surf = button_font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                if audio_enabled and "click" in sounds:
                    sounds["click"].play()
                return True
        return False

# Toggle button class
class ToggleButton:
    def __init__(self, x, y, width, height, text, state=True, on_color=AUDIO_ON_COLOR, off_color=AUDIO_OFF_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.state = state
        self.on_color = on_color
        self.off_color = off_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.on_color if self.state else self.off_color
        if self.is_hovered:
            color = (min(color[0] + 20, 255), min(color[1] + 20, 255), min(color[2] + 20, 255))
            
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, (50, 50, 50), self.rect, 3, border_radius=12)
        
        status = "ON" if self.state else "OFF"
        text_surf = button_font.render(f"{self.text}: {status}", True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                self.state = not self.state
                if audio_enabled and "click" in sounds:
                    sounds["click"].play()
                return True
        return False

# Create buttons
category_buttons = []
for i, category in enumerate(categories.keys()):
    button = Button(100 + i * 200, 150, 160, 60, category)
    category_buttons.append(button)

start_button = Button(WIDTH // 2 - 80, HEIGHT // 2 + 50, 160, 60, "Start Game")
instruction_button = Button(WIDTH // 2 - 80, HEIGHT // 2 + 130, 160, 60, "Instructions")
back_button = Button(50, 50, 120, 50, "Back")
audio_button = ToggleButton(WIDTH - 150, 50, 120, 50, "Audio", audio_enabled)
definition_button = ToggleButton(WIDTH - 150, 110, 120, 50, "Define", False)
difficulty_button = Button(WIDTH - 150, 170, 120, 50, f"Diff: {difficulty}")
option_buttons = []

# Function to start a new game
def start_new_game():
    global game_active, score, attempts, current_word, feedback, show_instructions, streak, timer_active, time_left
    game_active = True
    score = 0
    attempts = 0
    streak = 0
    feedback = ""
    show_instructions = False
    timer_active = difficulty == "Hard"
    next_word()

# Function to select the next word
def next_word():
    global current_word, option_buttons, feedback, time_left
    current_word = random.choice(categories[current_category]["words"])
    
    # Play word sound if audio is enabled
    if audio_enabled and current_word in sounds:
        sounds[current_word].play()
    
    # Create options (correct answer + 3 random wrong answers)
    options = [current_word]
    while len(options) < 4:
        random_word = random.choice(categories[current_category]["words"])
        if random_word not in options:
            options.append(random_word)
    
    random.shuffle(options)
    
    # Create buttons for options
    option_buttons = []
    for i, option in enumerate(options):
        button = Button(200 + (i % 2) * 300, 350 + (i // 2) * 100, 250, 80, option)
        option_buttons.append(button)
    
    # Set timer for hard difficulty
    if timer_active:
        time_left = 10

# Function to check answer
def check_answer(selected_word):
    global score, attempts, feedback, feedback_time, audio_enabled, streak, particles, high_score
    
    attempts += 1
    if selected_word == current_word:
        score += 1
        streak += 1
        feedback = "Correct! Good job!"
        if audio_enabled and "correct" in sounds:
            sounds["correct"].play()
        
        # Create particles for correct answer
        for _ in range(20):
            particles.append(Particle(WIDTH // 2, 270 + 75, 
                                    (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))))
    else:
        streak = 0
        feedback = f"Oops! It's {current_word}"
        if audio_enabled and "wrong" in sounds:
            sounds["wrong"].play()
    
    feedback_time = pygame.time.get_ticks()
    
    if attempts < max_attempts:
        # Wait a moment before showing next word
        pygame.time.set_timer(pygame.USEREVENT, 1500)
    else:
        # Game over
        pygame.time.set_timer(pygame.USEREVENT, 2000)

# Function to draw instructions
def draw_instructions():
    screen.fill(BACKGROUND)
    
    title_text = title_font.render("How to Play", True, TEXT_COLOR)
    screen.blit(title_title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
    
    instructions = [
        "1. Select a category from the top",
        "2. Click 'Start Game' to begin",
        "3. Look at the picture and choose the correct word",
        "4. Get points for correct answers",
        "5. Complete 10 questions to finish the game",
        "6. Use the Audio button to turn sounds on/off",
        "7. Use the Define button to show word definitions",
        "8. Difficulty levels:",
        "   - Easy: No timer, easier words",
        "   - Normal: No timer, all words",
        "   - Hard: 10-second timer per question",
        "9. Have fun learning English!"
    ]
    
    for i, instruction in enumerate(instructions):
        text = instruction_font.render(instruction, True, INSTRUCTION_COLOR)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 150 + i * 30))
    
    back_button.draw(screen)

# Function to draw progress bar
def draw_progress_bar():
    if max_attempts == 0:
        return
        
    bar_width = 500
    bar_height = 20
    x = (WIDTH - bar_width) // 2
    y = HEIGHT - 40
    
    # Draw background bar
    pygame.draw.rect(screen, (200, 200, 200), (x, y, bar_width, bar_height), border_radius=10)
    
    # Draw progress
    progress_width = (attempts / max_attempts) * bar_width
    pygame.draw.rect(screen, PROGRESS_COLOR, (x, y, progress_width, bar_height), border_radius=10)
    
    # Draw border
    pygame.draw.rect(screen, (50, 50, 50), (x, y, bar_width, bar_height), 2, border_radius=10)
    
    # Draw text
    progress_text = instruction_font.render(f"{attempts}/{max_attempts}", True, TEXT_COLOR)
    screen.blit(progress_text, (x + bar_width + 10, y - 2))

# Function to draw timer
def draw_timer():
    if not timer_active or not game_active:
        return
        
    timer_width = 200
    timer_height = 20
    x = (WIDTH - timer_width) // 2
    y = 240
    
    # Draw background bar
    pygame.draw.rect(screen, (200, 200, 200), (x, y, timer_width, timer_height), border_radius=10)
    
    # Draw timer
    timer_progress = (time_left / 10) * timer_width
    color = (
        max(0, min(255, 255 - (time_left * 25))),
        min(255, time_left * 25),
        0
    )
    pygame.draw.rect(screen, color, (x, y, timer_progress, timer_height), border_radius=10)
    
    # Draw border
    pygame.draw.rect(screen, (50, 50, 50), (x, y, timer_width, timer_height), 2, border_radius=10)
    
    # Draw text
    timer_text = instruction_font.render(f"Time: {time_left}s", True, TEXT_COLOR)
    screen.blit(timer_text, (x + timer_width // 2 - timer_text.get_width() // 2, y + 25))

# Main game loop
async def main():
    global game_active, score, attempts, current_word, feedback, feedback_time
    global show_instructions, audio_enabled, show_definition, streak, high_score
    global difficulty, timer_active, time_left, particles
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        
        # Update timer if active
        if timer_active and game_active:
            time_left -= 1/60
            if time_left <= 0:
                time_left = 0
                # Time's up - count as wrong answer
                if game_active and attempts < max_attempts:
                    streak = 0
                    feedback = f"Time's up! It's {current_word}"
                    feedback_time = pygame.time.get_ticks()
                    attempts += 1
                    pygame.time.set_timer(pygame.USEREVENT, 1500)
        
        # Update particles
        particles = [p for p in particles if p.update()]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.USEREVENT:
                pygame.time.set_timer(pygame.USEREVENT, 0)
                if attempts < max_attempts:
                    next_word()
                else:
                    game_active = False
                    feedback = f"Game Over! Score: {score}/{max_attempts}"
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not game_active and not show_instructions and start_button.is_clicked(mouse_pos, event):
                    start_new_game()
                
                if not game_active and not show_instructions and instruction_button.is_clicked(mouse_pos, event):
                    show_instructions = True
                    
                if show_instructions and back_button.is_clicked(mouse_pos, event):
                    show_instructions = False
                
                if audio_button.is_clicked(mouse_pos, event):
                    audio_enabled = audio_button.state
                
                if definition_button.is_clicked(mouse_pos, event):
                    show_definition = definition_button.state
                
                if difficulty_button.is_clicked(mouse_pos, event):
                    difficulties = ["Easy", "Normal", "Hard"]
                    current_index = difficulties.index(difficulty)
                    difficulty = difficulties[(current_index + 1) % len(difficulties)]
                    difficulty_button.text = f"Diff: {difficulty}"
                
                if game_active:
                    for button in option_buttons:
                        if button.is_clicked(mouse_pos, event):
                            check_answer(button.text)
                
                for button in category_buttons:
                    if button.is_clicked(mouse_pos, event):
                        current_category = button.text
                        if game_active:
                            next_word()
        
        # Update button hover states
        if not game_active and not show_instructions:
            start_button.check_hover(mouse_pos)
            instruction_button.check_hover(mouse_pos)
        
        if show_instructions:
            back_button.check_hover(mouse_pos)
        
        audio_button.check_hover(mouse_pos)
        definition_button.check_hover(mouse_pos)
        difficulty_button.check_hover(mouse_pos)
        
        for button in category_buttons:
            button.check_hover(mouse_pos)
        
        for button in option_buttons:
            button.check_hover(mouse_pos)
        
        # Draw everything
        screen.fill(BACKGROUND)
        
        # Draw particles
        for particle in particles:
            particle.draw(screen)
        
        if show_instructions:
            draw_instructions()
        elif game_active:
            # Draw the current word's image with a border
            image_rect = pygame.Rect(WIDTH // 2 - 75, 270, 150, 150)
            pygame.draw.rect(screen, (100, 100, 100), image_rect, 2)
            
            if current_word in word_images:
                screen.blit(word_images[current_word], (WIDTH // 2 - 75, 270))
            else:
                # Fallback if image didn't load
                placeholder = pygame.Surface((150, 150))
                placeholder.fill((200, 200, 200))
                screen.blit(placeholder, (WIDTH // 2 - 75, 270))
                
                # Add text to the placeholder
                text = normal_font.render(current_word, True, (0, 0, 0))
                text_rect = text.get_rect(center=(WIDTH // 2, 270 + 75))
                screen.blit(text, text_rect)
            
            # Draw word definition if enabled
            if show_definition and current_word in categories[current_category]["definitions"]:
                definition = categories[current_category]["definitions"][current_word]
                # Split definition into multiple lines if too long
                words = definition.split()
                lines = []
                current_line = ""
                
                for word in words:
                    test_line = current_line + word + " "
                    if instruction_font.size(test_line)[0] < 600:
                        current_line = test_line
                    else:
                        lines.append(current_line)
                        current_line = word + " "
                
                if current_line:
                    lines.append(current_line)
                
                for i, line in enumerate(lines):
                    def_text = instruction_font.render(line, True, INSTRUCTION_COLOR)
                    screen.blit(def_text, (WIDTH // 2 - def_text.get_width() // 2, 270 + 170 + i * 25))
            
            # Draw option buttons
            for button in option_buttons:
                button.draw(screen)
            
            # Draw score and streak
            score_text = normal_font.render(f"Score: {score}/{attempts}", True, TEXT_COLOR)
            screen.blit(score_text, (WIDTH - 200, 50))
            
            if streak > 1:
                streak_text = normal_font.render(f"Streak: {streak}!", True, (255, 100, 100))
                screen.blit(streak_text, (WIDTH - 200, 90))
            
            # Draw feedback if any
            if feedback and current_time - feedback_time < 1000:
                feedback_surf = normal_font.render(feedback, True, TEXT_COLOR)
                screen.blit(feedback_surf, (WIDTH // 2 - feedback_surf.get_width() // 2, 500))
            
            # Draw progress bar
            draw_progress_bar()
            
            # Draw timer
            draw_timer()
        else:
            # Draw title
            title_text = title_font.render("Fun English Learning", True, TEXT_COLOR)
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
            
            # Draw category buttons
            for button in category_buttons:
                button.draw(screen)
            
            # Draw current category
            category_text = normal_font.render(f"Category: {current_category}", True, TEXT_COLOR)
            screen.blit(category_text, (WIDTH // 2 - category_text.get_width() // 2, 230))
            
            # Draw high score
            high_score_text = normal_font.render(f"High Score: {high_score}", True, TEXT_COLOR)
            screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2 - 100))
            
            # Draw start button
            start_button.draw(screen)
            instruction_button.draw(screen)
            
            # Draw final score if game was just completed
            if feedback:
                final_score = normal_font.render(feedback, True, TEXT_COLOR)
                screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, HEIGHT // 2 - 50))
        
        # Draw audio button and definition button
        audio_button.draw(screen)
        definition_button.draw(screen)
        difficulty_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()

# Run the game
if __name__ == "__main__":
    asyncio.run(main())