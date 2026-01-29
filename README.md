#  Advanced Snake Game with Hand Gesture Control

A modern, interactive Snake game controlled entirely through **real-time hand gestures** using your webcam. Built with Python, OpenCV, MediaPipe, and Pygame.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

##  Features

- **Hand Gesture Control**: Move snake using index finger position
- **Pause/Resume**: Make a fist gesture to pause and resume game
- **Smooth Motion**: Real-time hand position smoothing for fluid gameplay
- **Collision Detection**: Wall and self-collision detection
- **Score System**: Points for eating food, high score tracking
- **Difficulty Scaling**: Speed increases with snake length
- **Real-time Detection**: 60 FPS hand tracking via MediaPipe

## Screenshots 
<img width="500" height="350" alt="image" src="https://github.com/user-attachments/assets/77fff342-ad6b-4db7-bf5b-901fd5d6386e" />
<img width="500" height="350" alt="image" src="https://github.com/user-attachments/assets/db8df624-e5db-4902-b718-bb92a56f4b5f" />
<img width="500" height="350" alt="image" src="https://github.com/user-attachments/assets/c82a19dd-77ff-46de-a951-0caf83f38d1a" />

## 📋 System Requirements

### Minimum
- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **RAM**: 4GB
- **Webcam**: Standard USB or built-in camera
- **CPU**: Intel i5 / AMD Ryzen 5 or equivalent

### Recommended
- **Python**: 3.10+
- **RAM**: 8GB+
- **CPU**: Intel i7 / AMD Ryzen 7 or better
- **GPU**: NVIDIA GPU for faster MediaPipe processing

##  Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Ishika-guptaa25/Gesture-Snake.git
cd Gesture-Snake
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Game
```bash
python snake_game.py
```

## How to Play

### Controls
| Action | Gesture |
|--------|---------|
| **Move Up** | Move hand up above snake head |
| **Move Down** | Move hand down below snake head |
| **Move Left** | Move hand left of snake head |
| **Move Right** | Move hand right of snake head |
| **Pause/Resume** | Close hand into a fist |
| **Start Game** | Press SPACE key |
| **Restart** | Press SPACE key (after game over) |
| **Quit** | Press 'q' key |

### Gameplay Tips
1. **Smooth Movements**: Make gradual hand movements for better control
2. **Keep Hand Visible**: Ensure your hand is within the webcam frame
3. **Distance**: Stand about 1-2 meters from the camera
4. **Lighting**: Good lighting conditions improve detection accuracy
5. **Calibration**: Let the tracker detect your hand for 1-2 seconds before playing


## Troubleshooting

### Webcam Not Detected
```bash
# Check available cameras
python -c "import cv2; print(cv2.getBuildInformation())"

# Test camera connection
python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
```

### Low FPS / Lag
- Reduce window size in config.py
- Lower HAND_DETECTION_CONFIDENCE
- Close other applications
- Update graphics drivers

### Hand Not Detected
- Ensure good lighting conditions
- Keep entire hand visible in frame
- Reduce background complexity
- Increase HAND_DETECTION_CONFIDENCE gradually

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| opencv-python | 4.8.1.78 | Computer vision & webcam access |
| mediapipe | 0.10.9 | Hand detection & tracking |
| pygame | 2.5.2 | Game engine & rendering |
| numpy | 1.24.3 | Numerical computations |








