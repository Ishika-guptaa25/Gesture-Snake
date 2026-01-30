import pygame
import random
from collections import deque
from enum import Enum
from typing import Tuple

from config import ConfigManager

class Direction(Enum):
    """Snake movement directions"""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class GameState(Enum):
    """Game state enumeration"""
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3

class SnakeGame:
    """Main game logic controller"""

    def __init__(self):
        """Initialize the game"""
        pygame.init()

        self.config = ConfigManager.get_game_config()

        self.screen = pygame.display.set_mode(
            (self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT)
        )
        pygame.display.set_caption(self.config.WINDOW_TITLE)

        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, self.config.FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, self.config.FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, self.config.FONT_SIZE_SMALL)

        # Game state
        self.state = GameState.MENU
        self.score = 0
        self.high_score = self._load_high_score()
        self.frame_count = 0
        self.speed_multiplier = 1.0

        # Snake and food
        self.snake = None
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.food = None

        self.reset_game()

    def reset_game(self):
        """Reset game to initial state"""
        # Initialize snake in center
        grid_cols, grid_rows = self.config.get_grid_dimensions()
        start_x = grid_cols // 2
        start_y = grid_rows // 2

        self.snake = deque([
            (start_x, start_y),
            (start_x - 1, start_y),
            (start_x - 2, start_y)
        ])

        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.food = self._spawn_food()
        self.score = 0
        self.frame_count = 0
        self.speed_multiplier = 1.0
        self.state = GameState.MENU

    def start_game(self):
        """Start the game from menu"""
        if self.state == GameState.MENU:
            self.state = GameState.PLAYING

    def toggle_pause(self):
        """Toggle pause state"""
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.state = GameState.PLAYING

    def _spawn_food(self) -> Tuple[int, int]:
        """
        Spawn food at random location not occupied by snake

        Returns:
            Tuple of (x, y) grid coordinates
        """
        grid_cols, grid_rows = self.config.get_grid_dimensions()

        while True:
            x = random.randint(0, grid_cols - 1)
            y = random.randint(0, grid_rows - 1)

            if (x, y) not in self.snake:
                return (x, y)

    def update_direction(self, hand_pos: Tuple[int, int]):
        """
        Update snake direction based on hand position

        Args:
            hand_pos: Current hand position in pixels
        """
        if hand_pos is None or len(self.snake) == 0:
            return

        if self.state != GameState.PLAYING:
            return

        head = self.snake[0]
        head_screen = (
            head[0] * self.config.GRID_SIZE + self.config.GRID_SIZE // 2,
            head[1] * self.config.GRID_SIZE + self.config.GRID_SIZE // 2
        )

        dx = hand_pos[0] - head_screen[0]
        dy = hand_pos[1] - head_screen[1]

        # Only update if movement is significant
        if abs(dx) > self.config.DIRECTION_THRESHOLD or \
           abs(dy) > self.config.DIRECTION_THRESHOLD:

            if abs(dx) > abs(dy):
                self.next_direction = Direction.RIGHT if dx > 0 else Direction.LEFT
            else:
                self.next_direction = Direction.DOWN if dy > 0 else Direction.UP

    def update(self):
        """Update game logic"""
        if self.state != GameState.PLAYING:
            return

        self.frame_count += 1

        # Prevent 180-degree turns
        if (self.next_direction.value[0] * -1, self.next_direction.value[1] * -1) != \
           self.direction.value:
            self.direction = self.next_direction

        # Move snake
        head = self.snake[0]
        new_head = (
            head[0] + self.direction.value[0],
            head[1] + self.direction.value[1]
        )

        grid_cols, grid_rows = self.config.get_grid_dimensions()

        # Check wall collision
        if new_head[0] < 0 or new_head[0] >= grid_cols or \
           new_head[1] < 0 or new_head[1] >= grid_rows:
            self.state = GameState.GAME_OVER
            self._update_high_score()
            return

        # Check self collision
        if new_head in self.snake:
            self.state = GameState.GAME_OVER
            self._update_high_score()
            return

        self.snake.appendleft(new_head)

        # Check food collision
        if new_head == self.food:
            self.score += self.config.FOOD_POINTS
            self.food = self._spawn_food()
            self._increase_speed()
        else:
            self.snake.pop()

    def _increase_speed(self):
        """Increase game speed based on score"""
        snake_length = len(self.snake)
        self.speed_multiplier = 1.0 + (snake_length * 0.05)

    def draw(self):
        """Render game to screen"""
        self.screen.fill(self.config.COLOR_BACKGROUND)

        # Draw grid
        if self.config.SHOW_GRID:
            self._draw_grid()

        # Draw game elements
        if self.state != GameState.MENU:
            self._draw_snake()
            self._draw_food()

        # Draw UI
        self._draw_ui()

        pygame.display.flip()

    def _draw_grid(self):
        """Draw game grid"""
        for x in range(0, self.config.WINDOW_WIDTH, self.config.GRID_SIZE):
            pygame.draw.line(
                self.screen,
                self.config.COLOR_GRID,
                (x, 0),
                (x, self.config.WINDOW_HEIGHT)
            )

        for y in range(0, self.config.WINDOW_HEIGHT, self.config.GRID_SIZE):
            pygame.draw.line(
                self.screen,
                self.config.COLOR_GRID,
                (0, y),
                (self.config.WINDOW_WIDTH, y)
            )

    def _draw_snake(self):
        """Draw snake on screen"""
        for i, segment in enumerate(self.snake):
            x = segment[0] * self.config.GRID_SIZE
            y = segment[1] * self.config.GRID_SIZE

            # Head is brighter
            color = self.config.COLOR_HEAD if i == 0 else self.config.COLOR_SNAKE

            rect = pygame.Rect(
                x + 1,
                y + 1,
                self.config.GRID_SIZE - 2,
                self.config.GRID_SIZE - 2
            )
            pygame.draw.rect(self.screen, color, rect)

    def _draw_food(self):
        """Draw food on screen"""
        x = self.food[0] * self.config.GRID_SIZE
        y = self.food[1] * self.config.GRID_SIZE

        rect = pygame.Rect(
            x + 1,
            y + 1,
            self.config.GRID_SIZE - 2,
            self.config.GRID_SIZE - 2
        )
        pygame.draw.rect(self.screen, self.config.COLOR_FOOD, rect)

    def _draw_ui(self):
        """Draw UI elements"""
        # Draw score
        score_text = self.font_medium.render(
            f"Score: {self.score}",
            True,
            self.config.COLOR_TEXT
        )
        self.screen.blit(score_text, (10, 10))

        # Draw high score
        high_score_text = self.font_small.render(
            f"Best: {self.high_score}",
            True,
            self.config.COLOR_TEXT
        )
        self.screen.blit(high_score_text, (10, 50))

        # Draw snake length
        length_text = self.font_small.render(
            f"Length: {len(self.snake)}",
            True,
            self.config.COLOR_TEXT
        )
        self.screen.blit(length_text, (self.config.WINDOW_WIDTH - 200, 10))

        # Draw state-specific UI
        if self.state == GameState.MENU:
            self._draw_menu()
        elif self.state == GameState.PAUSED:
            self._draw_paused()
        elif self.state == GameState.GAME_OVER:
            self._draw_game_over()

    def _draw_menu(self):
        """Draw menu screen"""
        title = self.font_large.render(
            "SNAKE GAME",
            True,
            self.config.COLOR_TEXT
        )
        subtitle = self.font_medium.render(
            "Hand Gesture Control",
            True,
            self.config.COLOR_TEXT
        )
        start_text = self.font_medium.render(
            "Press SPACE to Start",
            True,
            self.config.COLOR_TEXT
        )

        center_x = self.config.WINDOW_WIDTH // 2
        center_y = self.config.WINDOW_HEIGHT // 2

        self.screen.blit(title, (center_x - 200, center_y - 100))
        self.screen.blit(subtitle, (center_x - 180, center_y - 20))
        self.screen.blit(start_text, (center_x - 180, center_y + 60))

    def _draw_paused(self):
        """Draw paused overlay"""
        overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        pause_text = self.font_large.render(
            "PAUSED",
            True,
            self.config.COLOR_TEXT
        )
        resume_text = self.font_medium.render(
            "Make a fist to resume",
            True,
            self.config.COLOR_TEXT
        )

        center_x = self.config.WINDOW_WIDTH // 2
        center_y = self.config.WINDOW_HEIGHT // 2

        self.screen.blit(pause_text, (center_x - 120, center_y - 40))
        self.screen.blit(resume_text, (center_x - 160, center_y + 40))

    def _draw_game_over(self):
        """Draw game over screen"""
        overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        over_text = self.font_large.render(
            "GAME OVER",
            True,
            self.config.COLOR_DANGER
        )
        score_text = self.font_medium.render(
            f"Score: {self.score}",
            True,
            self.config.COLOR_TEXT
        )
        best_text = self.font_medium.render(
            f"Best: {self.high_score}",
            True,
            self.config.COLOR_TEXT
        )
        restart_text = self.font_medium.render(
            "Press SPACE to Restart",
            True,
            self.config.COLOR_TEXT
        )

        center_x = self.config.WINDOW_WIDTH // 2
        center_y = self.config.WINDOW_HEIGHT // 2

        self.screen.blit(over_text, (center_x - 180, center_y - 80))
        self.screen.blit(score_text, (center_x - 100, center_y - 20))
        self.screen.blit(best_text, (center_x - 80, center_y + 20))
        self.screen.blit(restart_text, (center_x - 180, center_y + 80))

    def _load_high_score(self) -> int:
        """Load high score from file"""
        try:
            with open('high_score.txt', 'r') as f:
                return int(f.read())
        except:
            return 0

    def _update_high_score(self):
        """Update high score if current score is higher"""
        if self.score > self.high_score:
            self.high_score = self.score
            try:
                with open('high_score.txt', 'w') as f:
                    f.write(str(self.high_score))
            except:
                pass

    def cleanup(self):
        """Clean up pygame resources"""
        pygame.quit()