import pygame
import math
import random
from pygame import gfxdraw
import arabic_reshaper
from bidi.algorithm import get_display

pygame.init()

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

ARABIC_LETTERS = [
    'ا', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش',
    'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن',
    'ه', 'و', 'ي'
]

# Load a font that supports Arabic
font_path = r"C:\Users\abdou\project_folder\Janna LT Bold.ttf"  # Use a raw string literal

class TextInput:
    def __init__(self, x, y, width, height, placeholder="Enter name"):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.font = pygame.font.Font(font_path, 36)

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
        self.font = pygame.font.Font(font_path, 36)

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
        self.state = "name_input"
        self.players = [
            {"name": "", "score": 0},
            {"name": "", "score": 0}
        ]
        self.current_player = 0
        self.angle = 0
        self.spin_speed = 0
        self.is_spinning = False
        self.selected_letter = None
        self.font = pygame.font.Font(font_path, 48)
        self.small_font = pygame.font.Font(font_path, 24)  # Smaller font for Arabic letters

        self.spin_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100,
                                  200, 50, "SPIN", LIGHT_GRAY, GOLD)
        self.correct_button = Button(SCREEN_WIDTH//2 + 120, SCREEN_HEIGHT - 100,
                                     200, 50, "✓ Correct", GREEN, LIGHT_GRAY)
        self.wrong_button = Button(SCREEN_WIDTH//2 - 320, SCREEN_HEIGHT - 100,
                                   200, 50, "✗ Wrong", RED, LIGHT_GRAY)

        self.name_inputs = [
            TextInput(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 50, 300, 50, "Enter Player 1 Name"),
            TextInput(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 50, 300, 50, "Enter Player 2 Name")
        ]
        self.start_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 150,
                                   200, 50, "Start Game", GOLD, LIGHT_GRAY)

        self.logo = pygame.image.load("dmsa_logo.png")
        self.logo = pygame.transform.scale(self.logo, (100, 100))

    def draw_wheel(self, surface):
        center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        radius = 200

        pygame.draw.circle(surface, NAVY, center, radius, 3)

        for i, letter in enumerate(ARABIC_LETTERS):
            angle = math.radians(i * (360 / len(ARABIC_LETTERS)) + self.angle)
            x = center[0] + int(radius * 0.8 * math.cos(angle))
            y = center[1] + int(radius * 0.8 * math.sin(angle))

            reshaped_text = arabic_reshaper.reshape(letter)
            bidi_text = get_display(reshaped_text)
            text = self.small_font.render(bidi_text, True, NAVY)  # Use smaller font
            text_rect = text.get_rect(center=(x, y))
            surface.blit(text, text_rect)

        arrow_length = 30
        pygame.draw.polygon(surface, GOLD, [
            (center[0], center[1] - arrow_length),
            (center[0] - 10, center[1] + 10),
            (center[0] + 10, center[1] + 10)
        ])

    def draw_name_input(self, surface):
        logo_rect = self.logo.get_rect(midtop=(SCREEN_WIDTH // 2, 50))
        surface.blit(self.logo, logo_rect)

        title_font = pygame.font.Font(font_path, 64)
        title = title_font.render("Enter Player Names", True, NAVY)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        surface.blit(title, title_rect)

        for input_field in self.name_inputs:
            input_field.draw(surface)

        self.start_button.draw(surface)

    def draw_game(self, surface):
        logo_rect = self.logo.get_rect(midtop=(SCREEN_WIDTH // 2, 20))
        surface.blit(self.logo, logo_rect)

        self.draw_wheel(surface)

        for i, player in enumerate(self.players):
            box_rect = pygame.Rect(50 if i == 0 else SCREEN_WIDTH - 300, 100,
                                  250, 150)  # Increased box size
            pygame.draw.rect(surface, LIGHT_GRAY, box_rect, border_radius=10)
            pygame.draw.rect(surface, NAVY, box_rect, 2, border_radius=10)

            name_text = self.font.render(player["name"], True,
                                        GOLD if i == self.current_player else NAVY)
            name_rect = name_text.get_rect(center=(box_rect.centerx, box_rect.centery - 30))
            surface.blit(name_text, name_rect)

            score_text = self.font.render(f"{player['score']}/5", True, NAVY)
            score_rect = score_text.get_rect(center=(box_rect.centerx, box_rect.centery + 30))
            surface.blit(score_text, score_rect)

        self.spin_button.draw(surface)
        if self.selected_letter and not self.is_spinning:
            self.correct_button.draw(surface)
            self.wrong_button.draw(surface)

        if self.selected_letter and not self.is_spinning:
            instruction_font = pygame.font.Font(font_path, 36)
            instruction_text = instruction_font.render(
                f"Recite an Ayat starting with {self.selected_letter}", True, NAVY)
            instruction_rect = instruction_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150))
            surface.blit(instruction_text, instruction_rect)

    def draw(self, surface):
        surface.fill(WHITE)
        if self.state == "name_input":
            self.draw_name_input(surface)
        else:
            self.draw_game(surface)

    def update(self):
        if self.is_spinning:
            self.angle += self.spin_speed
            self.spin_speed *= 0.99

            if self.spin_speed < 0.1:
                self.is_spinning = False
                self.selected_letter = self.get_selected_letter()

    def spin(self):
        if not self.is_spinning:
            self.is_spinning = True
            self.spin_speed = random.uniform(10, 20)

    def get_selected_letter(self):
        normalized_angle = self.angle % 360
        letter_index = int(normalized_angle / (360 / len(ARABIC_LETTERS)))
        return ARABIC_LETTERS[letter_index % len(ARABIC_LETTERS)]

    def handle_correct(self):
        if self.players[self.current_player]["score"] < 5:
            self.players[self.current_player]["score"] += 1
        self.current_player = (self.current_player + 1) % len(self.players)
        self.selected_letter = None

    def handle_wrong(self):
        self.current_player = (self.current_player + 1) % len(self.players)
        self.selected_letter = None

    def handle_event(self, event):
        if self.state == "name_input":
            for input_field in self.name_inputs:
                input_field.handle_event(event)
            if self.start_button.handle_event(event):
                self.players[0]["name"] = self.name_inputs[0].text or "Player 1"
                self.players[1]["name"] = self.name_inputs[1].text or "Player 2"
                self.state = "playing"
        else:
            if self.spin_button.handle_event(event) and not self.is_spinning:
                self.spin()
            elif self.selected_letter and not self.is_spinning:
                if self.correct_button.handle_event(event):
                    self.handle_correct()
                elif self.wrong_button.handle_event(event):
                    self.handle_wrong()

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

