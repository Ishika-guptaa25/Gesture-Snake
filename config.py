from dataclasses import dataclass
from typing import Tuple


@dataclass
class GameConfig:


    # Window Settings
    WINDOW_WIDTH: int = 800
    WINDOW_HEIGHT: int = 600
    WINDOW_TITLE: str = "Snake Game - Hand Gesture Control"

    # Grid Settings
    GRID_SIZE: int = 20

    # Game Mechanics
    FPS: int = 10
    INITIAL_SPEED: int = 10
    MAX_SPEED: int = 20
    SPEED_INCREMENT: float = 0.5

    # Scoring
    FOOD_POINTS: int = 10
    BONUS_POINTS_PER_SEGMENT: int = 1

    # Colors (BGR format for OpenCV compatibility)
    COLOR_SNAKE: Tuple[int, int, int] = (0, 255, 0)
    COLOR_FOOD: Tuple[int, int, int] = (255, 0, 0)
    COLOR_BACKGROUND: Tuple[int, int, int] = (0, 0, 0)
    COLOR_GRID: Tuple[int, int, int] = (30, 30, 30)
    COLOR_TEXT: Tuple[int, int, int] = (255, 255, 255)
    COLOR_HEAD: Tuple[int, int, int] = (0, 200, 0)
    COLOR_DANGER: Tuple[int, int, int] = (255, 0, 0)

    # Hand Tracking Settings
    HAND_DETECTION_CONFIDENCE: float = 0.7
    HAND_TRACKING_CONFIDENCE: float = 0.5
    MAX_NUM_HANDS: int = 1
    GESTURE_SMOOTHING_WINDOW: int = 5

    # Direction Detection
    DIRECTION_THRESHOLD: int = 30  # pixels
    MIN_MOVEMENT_DISTANCE: int = 15  # pixels

    # Gesture Detection
    FIST_CLOSED_THRESHOLD: float = 0.12
    PALM_SIZE_THRESHOLD: float = 0.15

    # Webcam Settings
    WEBCAM_WIDTH: int = 640
    WEBCAM_HEIGHT: int = 480
    CAMERA_ID: int = 0

    # UI Settings
    FONT_SIZE_LARGE: int = 48
    FONT_SIZE_MEDIUM: int = 36
    FONT_SIZE_SMALL: int = 24

    # Display Options
    SHOW_GRID: bool = True
    SHOW_COORDINATES: bool = False
    SHOW_DEBUG_INFO: bool = False
    SHOW_HAND_LANDMARKS: bool = True

    # Difficulty Settings (can be adjusted)
    DIFFICULTY_LEVELS = {
        'easy': {'speed': 5, 'speed_increment': 0.2},
        'medium': {'speed': 10, 'speed_increment': 0.5},
        'hard': {'speed': 15, 'speed_increment': 1.0},
    }

    def get_grid_dimensions(self) -> Tuple[int, int]:
        """Get grid dimensions in terms of grid size"""
        grid_cols = self.WINDOW_WIDTH // self.GRID_SIZE
        grid_rows = self.WINDOW_HEIGHT // self.GRID_SIZE
        return grid_cols, grid_rows

    def get_cell_rect(self, col: int, row: int) -> Tuple[int, int, int, int]:
        """Get pixel coordinates for a grid cell"""
        x = col * self.GRID_SIZE
        y = row * self.GRID_SIZE
        return (x, y, self.GRID_SIZE - 1, self.GRID_SIZE - 1)


@dataclass
class PerformanceConfig:
    """Performance optimization settings"""

    # Frame Rate
    TARGET_FPS: int = 30
    WEBCAM_FPS: int = 30

    # Hand Detection Optimization
    SKIP_FRAMES: int = 0  # Process every nth frame (0 = process all)
    USE_GPU: bool = True
    REDUCE_HAND_POINTS: bool = False

    # Display Optimization
    RESIZE_LARGE_FRAMES: bool = True
    MAX_FRAME_WIDTH: int = 1280

    # Memory Management
    HISTORY_SIZE: int = 100
    CLEAR_CACHE_INTERVAL: int = 100


class ConfigManager:
    """Manages configuration settings"""

    _instance = None
    _game_config = GameConfig()
    _performance_config = PerformanceConfig()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_game_config(cls) -> GameConfig:
        """Get game configuration"""
        return cls._game_config

    @classmethod
    def get_performance_config(cls) -> PerformanceConfig:
        """Get performance configuration"""
        return cls._performance_config

    @classmethod
    def set_difficulty(cls, difficulty: str) -> None:
        """Set difficulty level"""
        if difficulty in GameConfig.DIFFICULTY_LEVELS:
            settings = GameConfig.DIFFICULTY_LEVELS[difficulty]
            cls._game_config.FPS = settings['speed']
            cls._game_config.SPEED_INCREMENT = settings['speed_increment']

    @classmethod
    def to_dict(cls) -> dict:
        """Convert configuration to dictionary"""
        return {
            'game': cls._game_config.__dict__,
            'performance': cls._performance_config.__dict__,
        }