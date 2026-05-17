"""
Flotti Karotti - Pygame Version
A faithful port of the CLI board game with visual improvements.
"""

import pygame
import random
import os
import sys
import math

# Initialize Pygame
pygame.init()

# =============================================================================
# CONSTANTS
# =============================================================================
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
FPS = 60
DEBUG = True  # Set to True to see position indices and path lines

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
RED = (220, 60, 60)
ORANGE = (255, 165, 0)
DARK_OVERLAY = (0, 0, 0, 180)

# Game Constants
NUM_POSITIONS = 28
HOLES_SEQUENCE = [13, 25, 16, 23, 4, 21, 7, 19, 10]
CARDS = [1] * 24 + [2] * 8 + [3] * 4 + ["KLICK"] * 12

# Board field states
FREE = "free"
HOLE = "hole"
TARGET = "target"
OCCUPIED = "occupied"

# Assets Directory (relative to script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")


# =============================================================================
# ASSET LOADING
# =============================================================================
def find_asset(prefix: str) -> str | None:
    """Find an asset file by prefix (handles timestamped filenames)."""
    if not os.path.exists(ASSETS_DIR):
        return None
    for f in os.listdir(ASSETS_DIR):
        if f.startswith(prefix) and f.endswith(".png"):
            return f
    return None


def load_img(name: str | None, scale: tuple[int, int] | None = None) -> pygame.Surface:
    """Load an image with optional scaling. Returns placeholder on failure."""
    if name is None:
        surf = pygame.Surface((50, 50))
        surf.fill((255, 0, 255))
        return surf
    
    path = os.path.join(ASSETS_DIR, name)
    try:
        img = pygame.image.load(path).convert_alpha()
        if scale:
            img = pygame.transform.scale(img, scale)
        return img
    except Exception as e:
        print(f"Error loading {name}: {e}")
        surf = pygame.Surface(scale or (50, 50))
        surf.fill((255, 0, 255))
        return surf


# =============================================================================
# PATH COORDINATES
# =============================================================================
def generate_path_coords() -> list[tuple[float, float]]:
    """
    Generate screen coordinates for the 28 board positions.
    Creates an upward spiral path starting from the bottom.
    """
    coords = []
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    
    # Mountain path starting from bottom, winding upward
    radius_x, radius_y = 350, 260
    
    for i in range(NUM_POSITIONS):
        # Progress from 0.0 to 1.0
        progress = i / (NUM_POSITIONS - 1)
        
        # Start at bottom (pi/2) and go counter-clockwise (or clockwise)
        # 1.5 rotations winding upward
        angle = math.pi/2 - (progress * 2.5 * math.pi)
        
        # Inward spiral factor: radius gets smaller as we go up
        r_factor = 1.0 - (progress * 0.7)
        
        # Calculate base position
        x = center_x + radius_x * r_factor * math.cos(angle)
        y = center_y + radius_y * r_factor * math.sin(angle)
        
        # Lift the whole thing as we go up to simulate a mountain slope
        y -= progress * 150
        
        coords.append((x - 40, y - 40))  # Offset for sprite centering
    
    # Position 28 (index 27) is the carrot/win position at center-top (peak)
    coords[27] = (center_x - 40, center_y - 280)
    return coords


PATH_COORDS = generate_path_coords()


# =============================================================================
# PLAYER CLASS
# =============================================================================
class Player:
    """Represents a game player with their rabbit piece."""
    
    def __init__(self, player_id: int, name: str, image: pygame.Surface, color: tuple):
        self.id = player_id
        self.name = name
        self.image = image
        self.color = color
        self.position = 0  # 0 = not on board yet
        self.is_active = True
    
    def reset(self):
        """Reset player to starting state."""
        self.position = 0
        self.is_active = True


# =============================================================================
# GAME STATE CLASS
# =============================================================================
class GameState:
    """Manages the complete game state."""
    
    def __init__(self, player_images: dict, player_colors: dict):
        self.player_images = player_images
        self.player_colors = player_colors
        self.players: list[Player] = []
        self.current_player_idx = 0
        self.deck: list = []
        self.holes_list = list(HOLES_SEQUENCE)
        self.current_hole_idx = 0
        self.active_hole: int | None = None
        self.last_card = None
        self.winner: Player | None = None
        self.message = ""
        self.board: dict[int, str] = {}
        
        self.reset()
    
    def reset(self):
        """Reset game to initial state."""
        # Create players
        self.players = [
            Player(1, "Flora", self.player_images[1], self.player_colors[1]),
            Player(2, "Mathea", self.player_images[2], self.player_colors[2]),
        ]
        
        # Reset player positions
        for p in self.players:
            p.reset()
        
        # Initialize board - all positions free except target
        self.board = {i: FREE for i in range(1, NUM_POSITIONS + 1)}
        self.board[NUM_POSITIONS] = TARGET
        
        # Reset deck
        self.deck = list(CARDS)
        random.shuffle(self.deck)
        
        # Reset holes
        self.holes_list = list(HOLES_SEQUENCE)
        self.current_hole_idx = 0
        self.active_hole = None
        
        # Reset game state
        self.current_player_idx = 0
        self.last_card = None
        self.winner = None
        self.message = f"{self.players[0].name}'s Turn! Click to Draw Card."
    
    def get_current_player(self) -> Player:
        """Get the current player."""
        return self.players[self.current_player_idx]
    
    def draw_card(self):
        """Draw a card and execute its effect."""
        if self.winner:
            return
        
        # Reshuffle if deck empty
        if not self.deck:
            self.deck = list(CARDS)
            random.shuffle(self.deck)
        
        self.last_card = self.deck.pop()
        player = self.get_current_player()
        
        if self.last_card == "KLICK":
            self.message = f"KLICK! {player.name} twists the carrot!"
            self.rotate_carrot()
        else:
            steps = self.last_card
            self.move_player(player, steps)
        
        # Next player if no winner
        if not self.winner:
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            next_player = self.get_current_player()
            self.message += f" → {next_player.name}'s turn!"
    
    def get_target_field(self, start_pos: int, steps: int) -> int:
        """
        Calculate target position, skipping occupied fields.
        Ported from CLI logic for accurate movement.
        """
        if start_pos == 0:
            # First move onto the board - count from position 1
            current = 0
        else:
            current = start_pos
        
        steps_taken = 0
        while steps_taken < steps:
            current += 1
            if current > NUM_POSITIONS:
                return NUM_POSITIONS  # Win!
            
            # Only count free, hole, or target positions (skip occupied by other players)
            field_state = self.board.get(current, FREE)
            if field_state in (FREE, HOLE, TARGET):
                steps_taken += 1
        
        return current
    
    def move_player(self, player: Player, steps: int):
        """Move a player by the given number of steps."""
        old_pos = player.position
        new_pos = self.get_target_field(old_pos, steps)
        
        # Clear old position on board
        if old_pos > 0:
            self.board[old_pos] = FREE
        
        # Check win condition
        if new_pos >= NUM_POSITIONS:
            player.position = NUM_POSITIONS
            self.board[NUM_POSITIONS] = OCCUPIED
            self.winner = player
            self.message = f"🎉 {player.name} WINS! 🎉"
            return
        
        # Check if landing on hole
        if self.board.get(new_pos) == HOLE:
            player.position = 0
            self.message = f"OH NO! {player.name} jumped into the hole! Back to start."
        else:
            player.position = new_pos
            self.board[new_pos] = OCCUPIED
            self.message = f"{player.name} moves {steps} → position {new_pos}."
    
    def rotate_carrot(self):
        """Rotate the carrot (activate next hole)."""
        # Clear previous hole
        if self.active_hole and self.board.get(self.active_hole) == HOLE:
            self.board[self.active_hole] = FREE
        
        # Activate next hole
        self.active_hole = self.holes_list[self.current_hole_idx]
        self.current_hole_idx = (self.current_hole_idx + 1) % len(self.holes_list)
        
        # Check if any player falls in
        for p in self.players:
            if p.position == self.active_hole:
                p.position = 0
                # Clear from board
                self.board[self.active_hole] = HOLE
                self.message += f" 💀 {p.name} fell in!"
            elif p.position > 0:
                # Mark their position as occupied
                self.board[p.position] = OCCUPIED
        
        # Mark hole on board
        if self.board.get(self.active_hole) != OCCUPIED:
            self.board[self.active_hole] = HOLE
    
    def update_board(self):
        """Sync board state with player positions."""
        # Reset to free/hole/target
        for pos in range(1, NUM_POSITIONS + 1):
            if pos == self.active_hole:
                self.board[pos] = HOLE
            elif pos == NUM_POSITIONS:
                self.board[pos] = TARGET
            else:
                self.board[pos] = FREE
        
        # Mark player positions
        for p in self.players:
            if p.position > 0:
                self.board[p.position] = OCCUPIED


# =============================================================================
# UI COMPONENTS
# =============================================================================
class Button:
    """A clickable button with hover effect."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 color: tuple = (70, 130, 180), hover_color: tuple = (100, 160, 210)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
    
    def update(self, mouse_pos: tuple):
        """Update hover state based on mouse position."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Draw the button."""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 3, border_radius=10)
        
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def is_clicked(self, event: pygame.event.Event) -> bool:
        """Check if button was clicked."""
        return (event.type == pygame.MOUSEBUTTONDOWN and 
                event.button == 1 and 
                self.is_hovered)


# =============================================================================
# MAIN GAME CLASS
# =============================================================================
class FlottiKarottiGame:
    """Main game class handling rendering and input."""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🥕 Flotti Karotti 🐰")
        self.clock = pygame.time.Clock()
        
        # Load fonts
        self.font = pygame.font.SysFont("Arial", 28, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 22)
        self.big_font = pygame.font.SysFont("Arial", 48, bold=True)
        
        # Load images
        self.bg_img = load_img(find_asset("board_background"), (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        player_images = {
            1: load_img(find_asset("rabbit_blue"), (80, 80)),
            2: load_img(find_asset("rabbit_red"), (80, 80)),
            3: load_img(find_asset("rabbit_green"), (80, 80)),
            4: load_img(find_asset("rabbit_yellow"), (80, 80)),
        }
        player_colors = {
            1: (65, 105, 225),   # Blue
            2: (220, 60, 60),    # Red
            3: (60, 179, 113),   # Green
            4: (255, 215, 0),    # Yellow
        }
        
        self.card_1 = load_img(find_asset("game_card_1"), (160, 240))
        self.card_click = load_img(find_asset("game_card_click"), (160, 240))
        
        # Initialize game state
        self.game = GameState(player_images, player_colors)
        
        # UI elements
        self.draw_button = Button(
            SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT - 100, 160, 50, "Draw Card"
        )
        self.restart_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80, 200, 50, 
            "Play Again", color=(60, 160, 60), hover_color=(80, 200, 80)
        )
        
        # Animation state
        self.hole_pulse = 0
    
    def run(self):
        """Main game loop."""
        running = True
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.game.winner:
                    if self.restart_button.is_clicked(event):
                        self.game.reset()
                else:
                    if self.draw_button.is_clicked(event):
                        self.game.draw_card()
            
            # Update
            self.draw_button.update(mouse_pos)
            self.restart_button.update(mouse_pos)
            self.hole_pulse = (self.hole_pulse + 5) % 360
            
            # Render
            self.render()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
    
    def render(self):
        """Render the complete game screen."""
        # Background
        self.screen.blit(self.bg_img, (0, 0))
        
        # Draw hole indicator (animated)
        if self.game.active_hole:
            self.draw_hole_indicator()
        
        # Draw players on board
        self.draw_players()
        
        # Draw waiting area for players not on board
        self.draw_waiting_area()
        
        # Draw UI
        self.draw_ui()
        
        # Draw win overlay
        if self.game.winner:
            self.draw_win_screen()
            
        # Debug visualization
        if DEBUG:
            self.draw_debug_info()
    
    def draw_debug_info(self):
        """Draw path lines and position indices for debugging."""
        # Draw lines between positions
        for i in range(len(PATH_COORDS) - 1):
            p1 = (PATH_COORDS[i][0] + 40, PATH_COORDS[i][1] + 40)
            p2 = (PATH_COORDS[i+1][0] + 40, PATH_COORDS[i+1][1] + 40)
            pygame.draw.line(self.screen, ORANGE, p1, p2, 2)
        
        # Draw indices
        for i, pos in enumerate(PATH_COORDS):
            center = (int(pos[0] + 40), int(pos[1] + 40))
            # Circle background
            pygame.draw.circle(self.screen, WHITE, center, 15)
            pygame.draw.circle(self.screen, BLACK, center, 15, 2)
            
            # Index number (1-based)
            idx_surf = self.small_font.render(str(i + 1), True, BLACK)
            idx_rect = idx_surf.get_rect(center=center)
            self.screen.blit(idx_surf, idx_rect)
    
    def draw_hole_indicator(self):
        """Draw animated hole indicator."""
        hole_pos = PATH_COORDS[self.game.active_hole - 1]
        center = (int(hole_pos[0] + 40), int(hole_pos[1] + 40))
        
        # Pulsing effect
        pulse = abs(math.sin(math.radians(self.hole_pulse)))
        radius = int(35 + pulse * 10)
        
        # Draw concentric circles
        pygame.draw.circle(self.screen, (255, 0, 0), center, radius, 4)
        pygame.draw.circle(self.screen, (255, 100, 100), center, radius - 8, 2)
        
        # "HOLE" label
        label = self.small_font.render("HOLE", True, RED)
        label_rect = label.get_rect(center=(center[0], center[1] - 50))
        pygame.draw.rect(self.screen, WHITE, label_rect.inflate(10, 4))
        self.screen.blit(label, label_rect)
    
    def draw_players(self):
        """Draw player rabbits on the board."""
        for player in self.game.players:
            if player.position > 0:
                pos = PATH_COORDS[player.position - 1]
                self.screen.blit(player.image, pos)
                
                # Draw name label
                name_surf = self.small_font.render(player.name, True, player.color)
                name_rect = name_surf.get_rect(center=(pos[0] + 40, pos[1] + 90))
                
                # Background for readability
                bg_rect = name_rect.inflate(8, 4)
                pygame.draw.rect(self.screen, (255, 255, 255, 200), bg_rect, border_radius=4)
                self.screen.blit(name_surf, name_rect)
    
    def draw_waiting_area(self):
        """Draw area showing players not yet on the board."""
        waiting = [p for p in self.game.players if p.position == 0]
        if not waiting:
            return
        
        # Draw waiting area box
        box_x, box_y = 20, SCREEN_HEIGHT - 180
        pygame.draw.rect(self.screen, (50, 50, 50, 180), 
                        (box_x, box_y, 180, 160), border_radius=10)
        pygame.draw.rect(self.screen, WHITE, 
                        (box_x, box_y, 180, 160), 2, border_radius=10)
        
        title = self.small_font.render("Waiting:", True, WHITE)
        self.screen.blit(title, (box_x + 10, box_y + 10))
        
        for i, player in enumerate(waiting):
            y_offset = box_y + 40 + i * 55
            # Small rabbit icon
            small_img = pygame.transform.scale(player.image, (45, 45))
            self.screen.blit(small_img, (box_x + 15, y_offset))
            # Name
            name = self.small_font.render(player.name, True, player.color)
            self.screen.blit(name, (box_x + 70, y_offset + 12))
    
    def draw_ui(self):
        """Draw UI elements: message, current card, buttons."""
        # Message bar at top
        msg_bg = pygame.Rect(0, 0, SCREEN_WIDTH, 60)
        pygame.draw.rect(self.screen, (40, 40, 40), msg_bg)
        
        msg_surf = self.font.render(self.game.message, True, WHITE)
        msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.screen.blit(msg_surf, msg_rect)
        
        # Current player indicator
        if not self.game.winner:
            current = self.game.get_current_player()
            indicator = self.small_font.render(f"▶ {current.name}", True, current.color)
            self.screen.blit(indicator, (20, 70))
        
        # Last card display
        if self.game.last_card:
            card_x = SCREEN_WIDTH - 200
            card_y = 80
            
            card_img = self.card_click if self.game.last_card == "KLICK" else self.card_1
            self.screen.blit(card_img, (card_x, card_y))
            
            # Card value label
            card_text = f"Card: {self.game.last_card}"
            text_surf = self.small_font.render(card_text, True, BLACK)
            text_rect = text_surf.get_rect(center=(card_x + 80, card_y + 260))
            pygame.draw.rect(self.screen, WHITE, text_rect.inflate(10, 4), border_radius=4)
            self.screen.blit(text_surf, text_rect)
        
        # Draw button
        if not self.game.winner:
            self.draw_button.draw(self.screen, self.font)
    
    def draw_win_screen(self):
        """Draw the winner overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Winner box
        box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 120, 400, 250)
        pygame.draw.rect(self.screen, (30, 30, 30), box_rect, border_radius=20)
        pygame.draw.rect(self.screen, (255, 215, 0), box_rect, 4, border_radius=20)
        
        # Winner text
        win_text = self.big_font.render("🎉 WINNER! 🎉", True, (255, 215, 0))
        win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(win_text, win_rect)
        
        # Winner name
        name_text = self.font.render(self.game.winner.name, True, self.game.winner.color)
        name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(name_text, name_rect)
        
        # Restart button
        self.restart_button.draw(self.screen, self.font)


# =============================================================================
# ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    game = FlottiKarottiGame()
    game.run()
