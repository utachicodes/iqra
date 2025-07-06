import pygame
import math
import random
from pygame import gfxdraw
import arabic_reshaper
from bidi.algorithm import get_display
import os # Added for path manipulation

pygame.init()

# Determine the script's directory for relative paths
try:
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Fallback if __file__ is not defined (e.g., in some interactive environments)
    script_dir = os.getcwd()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("DMSA Quranic Letter Wheel")

NAVY = (28, 49, 94)
WHITE = (255, 255, 255)
GOLD = (199, 161, 77)
LIGHT_GRAY = (245, 245, 245)
RED = (255, 99, 71)
GREEN = (34, 139, 34)
YELLOW = (255, 223, 0) # For the star

CHOOSE_LETTER_SYMBOL = "★"
CHOOSE_LETTER_STATE_VALUE = "CHOOSE_LETTER" # Special value for selected_letter

ARABIC_LETTERS = [
    'ا', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش',
    'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن',
    'ه', 'و', 'ي', CHOOSE_LETTER_SYMBOL # Added star to the list
]

# --- Asset Loading ---
DEFAULT_FONT_FILE_NAME = "Janna LT Bold.ttf"
LOGO_FILE_NAME = "dmsa_logo.png"
SPIN_SOUND_FILE_NAME = "wheel_spin.wav" # Centralize sound file name

def load_font(font_file_name, size):
    """Loads a font, falling back to default system font if not found."""
    path = os.path.join(script_dir, font_file_name)
    if os.path.exists(path):
        try:
            return pygame.font.Font(path, size)
        except pygame.error as e:
            print(f"Error loading font '{font_file_name}' at '{path}': {e}. Using default system font.")
    else:
        print(f"Font '{font_file_name}' not found at '{path}'. Using default system font.")
    # Fallback to Pygame's default font
    return pygame.font.Font(None, size)

def load_image(image_file_name, scale_to=None):
    """Loads an image, returning None if not found or on error."""
    path = os.path.join(script_dir, image_file_name)
    if os.path.exists(path):
        try:
            image = pygame.image.load(path)
            if scale_to:
                image = pygame.transform.scale(image, scale_to)
            return image
        except pygame.error as e:
            print(f"Error loading image '{image_file_name}' at '{path}': {e}")
    else:
        print(f"Image '{image_file_name}' not found at '{path}'.")
    return None

def load_sound(sound_file_name):
    """Loads a sound, returning None if not found, on error, or if mixer is unavailable."""
    if not pygame.mixer or not pygame.mixer.get_init(): # Check if mixer is initialized
        print("Pygame mixer not initialized or unavailable. Cannot load sounds.")
        return None
    path = os.path.join(script_dir, sound_file_name)
    if os.path.exists(path):
        try:
            sound = pygame.mixer.Sound(path)
            return sound
        except pygame.error as e:
            print(f"Error loading sound '{sound_file_name}' at '{path}': {e}")
    else:
        print(f"Sound file '{sound_file_name}' not found at '{path}'.")
    return None

# Define font sizes
TEXT_INPUT_FONT_SIZE = 36
BUTTON_FONT_SIZE = 36
GAME_MAIN_FONT_SIZE = 48
GAME_SMALL_FONT_SIZE = 24
TITLE_FONT_SIZE = 64
INSTRUCTION_FONT_SIZE = 36

# Load global font objects
FONT_TEXT_INPUT = load_font(DEFAULT_FONT_FILE_NAME, TEXT_INPUT_FONT_SIZE)
FONT_BUTTON = load_font(DEFAULT_FONT_FILE_NAME, BUTTON_FONT_SIZE)
FONT_GAME_MAIN = load_font(DEFAULT_FONT_FILE_NAME, GAME_MAIN_FONT_SIZE)
FONT_GAME_SMALL = load_font(DEFAULT_FONT_FILE_NAME, GAME_SMALL_FONT_SIZE)
FONT_TITLE = load_font(DEFAULT_FONT_FILE_NAME, TITLE_FONT_SIZE)
FONT_INSTRUCTION = load_font(DEFAULT_FONT_FILE_NAME, INSTRUCTION_FONT_SIZE)
# --- End Asset Loading ---

# Load a font that supports Arabic and the path to it now remember to and "r" in front of the path.
# This line is now effectively replaced by the asset loading functions and globals above.
# We'll remove direct uses of 'font_path' next.
# font_path = os.path.join(script_dir, DEFAULT_FONT_FILE_NAME) # This line is no longer needed

# Game States
STATE_HOME_SCREEN = "home_screen"
STATE_NAME_INPUT_CLASSIC = "name_input_classic" # For classic game's player name input
STATE_CLASSIC_WHEEL_GAME = "classic_wheel_game"
STATE_DAILY_QUIZ_PLACEHOLDER = "daily_quiz_placeholder"


class TextInput:
    def __init__(self, x, y, width, height, placeholder="Enter name"):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.font = FONT_TEXT_INPUT # Use loaded global font

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)
        pygame.draw.rect(surface, NAVY if self.active else GOLD, self.rect, 2)

        if len(self.text) > 0:
            text = self.font.render(self.text, True, NAVY)
        else:
            text = self.font.render(self.placeholder, True, LIGHT_GRAY)

        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = FONT_BUTTON # Use loaded global font

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, NAVY, self.rect, 2, border_radius=10)

        text_surface = self.font.render(self.text, True, NAVY)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class Game:
    def __init__(self):
        self.current_game_state = STATE_HOME_SCREEN  # Start with the home screen
        # self.classic_game_phase is no longer needed, game flow is managed by self.current_game_state

        # Variables for Classic Wheel Game (many will be initialized/reset when classic game starts)
        self.players = [
            {"name": "", "score": 0},
            {"name": "", "score": 0}
        ]
        self.current_player = 0
        self.angle = 0
        self.spin_speed = 0
        self.is_spinning = False
        self.selected_letter = None
        self.is_choosing_letter = False
        self.clickable_letters_rects = []

        # UI Elements - some are general, some specific to classic game
        # Home Screen Buttons
        button_width = 300
        button_height = 60
        button_spacing = 20
        home_buttons_start_y = SCREEN_HEIGHT // 2 - (button_height * 3 + button_spacing * 2) // 2 # Centered vertically

        self.home_play_classic_button = Button(
            SCREEN_WIDTH // 2 - button_width // 2,
            home_buttons_start_y,
            button_width, button_height, "Classic Quranic Wheel", LIGHT_GRAY, GOLD
        )
        self.home_daily_quiz_button = Button(
            SCREEN_WIDTH // 2 - button_width // 2,
            home_buttons_start_y + button_height + button_spacing,
            button_width, button_height, "Daily Islamic Quiz", LIGHT_GRAY, GOLD
        )
        self.home_quit_button = Button(
            SCREEN_WIDTH // 2 - button_width // 2,
            home_buttons_start_y + (button_height + button_spacing) * 2,
            button_width, button_height, "Quit", LIGHT_GRAY, RED
        )

        # Classic Game Buttons & Inputs
        self.spin_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100,
                                  200, 50, "SPIN", LIGHT_GRAY, GOLD)
        self.correct_button = Button(SCREEN_WIDTH//2 + 120, SCREEN_HEIGHT - 100,
                                     200, 50, "✓ Correct", GREEN, LIGHT_GRAY)
        self.wrong_button = Button(SCREEN_WIDTH//2 - 320, SCREEN_HEIGHT - 100,
                                   200, 50, "✗ Wrong", RED, LIGHT_GRAY)
        self.name_inputs = [
            TextInput(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 50, 300, 50, "Player 1"),
            TextInput(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 50, 300, 50, "Player 2")
        ]
        self.start_classic_game_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 150, # Renamed for clarity
                                                200, 50, "Start Game", GOLD, LIGHT_GRAY)
        self.back_to_menu_button = Button(
            20, 20, 150, 40, "Back to Menu", LIGHT_GRAY, GOLD # Position top-left
        )

        self.logo = load_image(LOGO_FILE_NAME, scale_to=(150,150))

        self.spin_sound = load_sound(SPIN_SOUND_FILE_NAME)
        if not self.spin_sound:
            # This message is now more general as load_sound prints specifics
            print("Spin sound effect not loaded. Game will continue without spin sound.")
            print(f"Please ensure '{SPIN_SOUND_FILE_NAME}' is in the script directory if you want spin sounds.")


    def draw_wheel(self, surface):
        center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        radius = 200

        pygame.draw.circle(surface, NAVY, center, radius, 3)

        for i, letter in enumerate(ARABIC_LETTERS):
            angle = math.radians(i * (360 / len(ARABIC_LETTERS)) + self.angle)
            x = center[0] + int(radius * 0.8 * math.cos(angle))
            y = center[1] + int(radius * 0.8 * math.sin(angle))

            text_color = NAVY
            if letter == CHOOSE_LETTER_SYMBOL:
                text_color = YELLOW # Star color

            reshaped_text = arabic_reshaper.reshape(letter)
            bidi_text = get_display(reshaped_text)

            # Use a slightly larger font for the star to make it stand out
            current_font = FONT_GAME_SMALL
            if letter == CHOOSE_LETTER_SYMBOL:
                current_font = FONT_INSTRUCTION # Re-use instruction font size for star, or define a new one

            text = current_font.render(bidi_text, True, text_color)
            text_rect = text.get_rect(center=(x, y))
            surface.blit(text, text_rect)

        arrow_length = 30
        arrow_angle = math.radians(self.angle)
        arrow_end_x = center[0] + int(arrow_length * math.cos(arrow_angle))
        arrow_end_y = center[1] - int(arrow_length * math.sin(arrow_angle))

        pygame.draw.polygon(surface, GOLD, [
            (center[0], center[1]),
            (arrow_end_x - 10, arrow_end_y),
            (arrow_end_x + 10, arrow_end_y)
        ])

    def draw_classic_name_input(self, surface): # Renamed
        if self.logo: # Check if logo was loaded successfully
            logo_rect = self.logo.get_rect(midtop=(SCREEN_WIDTH // 2, 50))
            surface.blit(self.logo, logo_rect)

        # title_font = pygame.font.Font(font_path, 64) # No longer needed
        title = FONT_TITLE.render("Enter Player Names", True, NAVY) # Use global font
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        surface.blit(title, title_rect)

        for input_field in self.name_inputs:
            input_field.draw(surface)

        self.start_classic_game_button.draw(surface) # Ensure this uses the renamed button variable
        self.back_to_menu_button.draw(surface)

    def draw_classic_game_play(self, surface): # Renamed
        if self.logo: # Check if logo was loaded successfully
            logo_rect = self.logo.get_rect(midtop=(SCREEN_WIDTH // 2, 20))
            surface.blit(self.logo, logo_rect)

        self.draw_wheel(surface)

        for i, player in enumerate(self.players):
            box_rect = pygame.Rect(50 if i == 0 else SCREEN_WIDTH - 300, 100,
                                  250, 150)
            pygame.draw.rect(surface, LIGHT_GRAY, box_rect, border_radius=10)
            pygame.draw.rect(surface, NAVY, box_rect, 2, border_radius=10)

            name_text = FONT_GAME_MAIN.render(player["name"], True, # Use global font
                                        GOLD if i == self.current_player else NAVY)
            name_rect = name_text.get_rect(center=(box_rect.centerx, box_rect.centery - 30))
            surface.blit(name_text, name_rect)

            score_text = FONT_GAME_MAIN.render(f"{player['score']}/5", True, NAVY) # Use global font
            score_rect = score_text.get_rect(center=(box_rect.centerx, box_rect.centery + 30))
            surface.blit(score_text, score_rect)

        self.spin_button.draw(surface)
        if self.selected_letter and not self.is_spinning:
            self.correct_button.draw(surface)
            self.wrong_button.draw(surface)

        if self.selected_letter and not self.is_spinning and not self.is_choosing_letter:
            # instruction_font = pygame.font.Font(font_path, 36) # No longer needed
            instruction_text_content = f"Recite an Ayat starting with {self.selected_letter}"
            instruction_text = FONT_INSTRUCTION.render(instruction_text_content, True, NAVY) # Use global font
            instruction_rect = instruction_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150))
            surface.blit(instruction_text, instruction_rect)
        elif self.is_choosing_letter: # This block will now handle the instruction when choosing
            # Instruction for choosing a letter (already handled below, but good to have distinct logic)
            # The main instruction for choosing is now drawn after the letter grid.
            pass # Covered by the block below

        if self.is_choosing_letter:
            # Display letter choices
            for item in self.clickable_letters_rects:
                pygame.draw.rect(surface, LIGHT_GRAY, item["rect"], border_radius=5)
                pygame.draw.rect(surface, NAVY, item["rect"], 2, border_radius=5)
                letter_text = FONT_GAME_SMALL.render(item["reshaped"], True, NAVY)
                text_rect = letter_text.get_rect(center=item["rect"].center)
                surface.blit(letter_text, text_rect)

            # Instruction for choosing a letter
            choose_instruction_text = FONT_INSTRUCTION.render(
                f"{self.players[self.current_player]['name']}, pick a letter!", True, NAVY)
            choose_rect = choose_instruction_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)) # Positioned at bottom
            surface.blit(choose_instruction_text, choose_rect)

        self.back_to_menu_button.draw(surface)

    def draw_home_screen(self, surface):
        # Optional: Draw logo or title
        if self.logo:
            logo_rect = self.logo.get_rect(midtop=(SCREEN_WIDTH // 2, 100)) # Position logo higher
            surface.blit(self.logo, logo_rect)

        game_title_text = FONT_TITLE.render("IQRA Challenge", True, NAVY) # Example Title
        title_rect = game_title_text.get_rect(center=(SCREEN_WIDTH // 2, 250)) # Position below logo
        surface.blit(game_title_text, title_rect)

        self.home_play_classic_button.draw(surface)
        self.home_daily_quiz_button.draw(surface)
        self.home_quit_button.draw(surface)


    def draw(self, surface):
        surface.fill(WHITE)
        if self.current_game_state == STATE_HOME_SCREEN:
            self.draw_home_screen(surface)
        elif self.current_game_state == STATE_NAME_INPUT_CLASSIC:
            # This was previously self.draw_name_input(surface)
            # We'll rename/refactor draw_name_input to be specific for classic game's name input phase
            self.draw_classic_name_input(surface)
        elif self.current_game_state == STATE_CLASSIC_WHEEL_GAME:
            # This was previously self.draw_game(surface)
            self.draw_classic_game_play(surface)
        elif self.current_game_state == STATE_DAILY_QUIZ_PLACEHOLDER:
            # Simple placeholder drawing for now
            placeholder_text = FONT_TITLE.render("Daily Quiz Coming Soon!", True, NAVY)
            text_rect = placeholder_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            surface.blit(placeholder_text, text_rect)
            self.back_to_menu_button.draw(surface) # Add back button here too


    def update(self):
        if self.current_game_state == STATE_CLASSIC_WHEEL_GAME or self.current_game_state == STATE_NAME_INPUT_CLASSIC:
            if self.is_spinning:
                self.angle += self.spin_speed
                self.spin_speed *= 0.99

                if self.spin_speed < 0.1:
                    self.is_spinning = False
                    landed_on = self.get_selected_letter()
                    if landed_on == CHOOSE_LETTER_SYMBOL:
                        self.selected_letter = CHOOSE_LETTER_STATE_VALUE
                        self.is_choosing_letter = True
                        self.setup_letter_choices()
                    else:
                        self.selected_letter = landed_on
                        self.is_choosing_letter = False
        # Add other state updates here if needed in the future
        # elif self.current_game_state == STATE_DAILY_QUIZ_PLACEHOLDER:
            # pass # No updates for placeholder quiz state yet

    def spin(self):
        if not self.is_spinning and not self.is_choosing_letter: # Can't spin if choosing letter
            self.is_spinning = True
            self.spin_speed = random.uniform(10, 20)
            self.selected_letter = None # Clear previous selection when starting a new spin
            if self.spin_sound:
                self.spin_sound.play()

    def setup_letter_choices(self):
        self.clickable_letters_rects = []
        # Standard Arabic letters count is 28 (excluding the star symbol).
        actual_letters = [l for l in ARABIC_LETTERS if l != CHOOSE_LETTER_SYMBOL]
        num_actual_letters = len(actual_letters)

        letters_per_row = 10
        button_width = 60
        button_height = 60
        padding = 15

        # Calculate total width required for a row to center it
        total_width_for_row = letters_per_row * button_width + (letters_per_row - 1) * padding
        if num_actual_letters < letters_per_row: # Adjust if less than one full row
             total_width_for_row = num_actual_letters * button_width + (num_actual_letters - 1) * padding

        start_x = (SCREEN_WIDTH - total_width_for_row) // 2

        num_rows = (num_actual_letters + letters_per_row - 1) // letters_per_row
        total_height_for_letters = num_rows * button_height + (num_rows - 1) * padding
        start_y = (SCREEN_HEIGHT - total_height_for_letters) // 2 - 70 # Shifted up a bit more

        for i, letter in enumerate(actual_letters):
            row = i // letters_per_row
            col = i % letters_per_row

            # Recalculate start_x for the last row if it's not full, to keep it centered
            current_row_letters = num_actual_letters - (row * letters_per_row)
            if current_row_letters < letters_per_row and row == num_rows -1:
                current_row_width = current_row_letters * button_width + (current_row_letters - 1) * padding
                loop_start_x = (SCREEN_WIDTH - current_row_width) // 2
            else:
                loop_start_x = start_x

            x = loop_start_x + col * (button_width + padding)
            y = start_y + row * (button_height + padding)
            rect = pygame.Rect(x, y, button_width, button_height)
            self.clickable_letters_rects.append({
                "letter": letter,
                "rect": rect,
                "reshaped": get_display(arabic_reshaper.reshape(letter))
            })

    def get_selected_letter(self):
        normalized_angle = self.angle % 360
        letter_index = int(normalized_angle / (360 / len(ARABIC_LETTERS)))
        return ARABIC_LETTERS[letter_index % len(ARABIC_LETTERS)]

    def handle_correct(self):
        if self.players[self.current_player]["score"] < 5:
            self.players[self.current_player]["score"] += 1
        self.current_player = (self.current_player + 1) % len(self.players)
        self.selected_letter = None
        self.is_choosing_letter = False # Ensure reset
        self.clickable_letters_rects = [] # Clear any choice UI state

    def handle_wrong(self):
        self.current_player = (self.current_player + 1) % len(self.players)
        self.selected_letter = None
        self.is_choosing_letter = False # Ensure reset
        self.clickable_letters_rects = [] # Clear any choice UI state

    def reset_classic_game_vars(self):
        """Resets variables specific to the classic wheel game."""
        self.players = [{"name": "", "score": 0}, {"name": "", "score": 0}]
        self.current_player = 0
        self.angle = 0
        self.spin_speed = 0
        self.is_spinning = False
        self.selected_letter = None
        self.is_choosing_letter = False
        self.clickable_letters_rects = []
        # self.classic_game_phase = STATE_NAME_INPUT_CLASSIC # This line is removed
        # Reset text in name input fields
        for T_input in self.name_inputs: # Corrected variable name from input_field to T_input
            T_input.text = ""
            T_input.active = False


    def handle_event(self, event):
        if self.current_game_state == STATE_HOME_SCREEN:
            if self.home_play_classic_button.handle_event(event):
                self.current_game_state = STATE_NAME_INPUT_CLASSIC
                self.reset_classic_game_vars() # Reset classic game before starting
            elif self.home_daily_quiz_button.handle_event(event):
                self.current_game_state = STATE_DAILY_QUIZ_PLACEHOLDER
            elif self.home_quit_button.handle_event(event):
                pygame.event.post(pygame.event.Event(pygame.QUIT))

        elif self.current_game_state == STATE_NAME_INPUT_CLASSIC:
            for T_input in self.name_inputs: # Corrected variable name
                T_input.handle_event(event)
            if self.start_classic_game_button.handle_event(event):
                self.players[0]["name"] = self.name_inputs[0].text or "Player 1"
                self.players[1]["name"] = self.name_inputs[1].text or "Player 2"
                self.current_game_state = STATE_CLASSIC_WHEEL_GAME # Transition to playing the classic game
            elif self.back_to_menu_button.handle_event(event):
                self.current_game_state = STATE_HOME_SCREEN

        elif self.current_game_state == STATE_CLASSIC_WHEEL_GAME:
            if self.back_to_menu_button.handle_event(event): # Check this first
                self.current_game_state = STATE_HOME_SCREEN
            elif self.is_choosing_letter:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left click
                    for item in self.clickable_letters_rects:
                        if item["rect"].collidepoint(event.pos):
                            self.selected_letter = item["letter"] # Set the chosen letter
                            self.is_choosing_letter = False # Exit choosing mode
                            self.clickable_letters_rects = [] # Clear choices
                            break
            elif self.spin_button.handle_event(event) and not self.is_spinning:
                self.spin()
            elif self.selected_letter and not self.is_spinning and self.selected_letter != CHOOSE_LETTER_STATE_VALUE:
                if self.correct_button.handle_event(event):
                    self.handle_correct()
                elif self.wrong_button.handle_event(event):
                    self.handle_wrong()

        # Placeholder for quiz event handling
        elif self.current_game_state == STATE_DAILY_QUIZ_PLACEHOLDER:
            if self.back_to_menu_button.handle_event(event):
                self.current_game_state = STATE_HOME_SCREEN
            # Add other quiz-specific event handling here in the future

def main():
    clock = pygame.time.Clock()
    game = Game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)

        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
