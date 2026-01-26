import cv2
import numpy as np
import pygame  # FIX: Top par import kiya taaki _display_combined_view mein crash na ho
from game import SnakeGame
from hand_tracker import HandTracker


class SnakeGameApp:
    """Main application controller"""

    def __init__(self):
        """Initialize the application"""
        self.game = SnakeGame()
        self.hand_tracker = HandTracker()
        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            raise RuntimeError("Cannot open webcam. Please check your camera connection.")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.running = True
        self.pause_gesture_cooldown = 0

    def run(self):
        """Main game loop"""
        print("Starting Snake Game...")
        print("Controls:")
        print("  - Move hand to control snake direction")
        print("  - Make a fist to pause/resume")
        print("  - Press SPACE to start/restart")
        print("  - Press 'q' to quit")

        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Failed to read frame from webcam")
                    break

                frame = cv2.flip(frame, 1)

                # Detect hand position
                hand_pos, is_detected = self.hand_tracker.detect_hand(frame)
                smoothed_pos = self.hand_tracker.get_smoothed_position()

                # Detect pause gesture (closed fist)
                is_fist = self.hand_tracker.detect_fist_gesture(frame)

                # Handle pause gesture with cooldown
                if is_fist and self.pause_gesture_cooldown <= 0:
                    self.game.toggle_pause()
                    self.pause_gesture_cooldown = 30

                # FIX: Cooldown ko negative hone se bachaya
                if self.pause_gesture_cooldown > 0:
                    self.pause_gesture_cooldown -= 1

                # Update game with smoothed hand position
                if smoothed_pos:
                    self.game.update_direction(smoothed_pos)

                self.game.update()
                self.game.draw()

                # Draw hand tracking visualization
                frame = self.hand_tracker.draw_hand_landmarks(frame)

                if is_detected and smoothed_pos:
                    cv2.circle(frame, smoothed_pos, 8, (0, 255, 0), -1)
                    cv2.circle(frame, smoothed_pos, 10, (0, 255, 0), 2)

                # Add status information
                status = self.game.state.name
                # FIX: state.value ki jagah direct Enum comparison bhi use kar sakte hain
                color = (0, 255, 0) if "PLAYING" in status else (0, 165, 255)
                cv2.putText(frame, f"State: {status}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                cv2.putText(frame, f"Score: {self.game.score}", (10, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                # Display combined view
                self._display_combined_view(frame)

                # Handle keyboard input
                self._handle_keyboard_input()

                self.game.clock.tick(self.game.config.FPS)

        except Exception as e:
            print(f"Error occurred: {e}")
            import traceback
            traceback.print_exc()

        finally:
            self.cleanup()

    def _display_combined_view(self, webcam_frame):
        """Display webcam and game side by side"""
        try:
            # FIX: Safe Pygame to OpenCV conversion
            game_surface = self.game.screen
            game_array = pygame.surfarray.array3d(game_surface)

            # Rotate and flip to match OpenCV's coordinate system
            game_array = np.rot90(game_array, 3)
            game_array = np.fliplr(game_array)
            game_frame = cv2.cvtColor(game_array, cv2.COLOR_RGB2BGR)

            # Resize frames to match height
            h_cam, w_cam = webcam_frame.shape[:2]
            h_game, w_game = game_frame.shape[:2]

            if h_cam != h_game:
                game_frame = cv2.resize(game_frame, (int(w_game * (h_cam / h_game)), h_cam))

            # Combine horizontally
            combined = np.hstack([webcam_frame, game_frame])
            cv2.imshow("Snake Game - Hand Gesture Control", combined)

        except Exception as e:
            print(f"Display error: {e}")

    def _handle_keyboard_input(self):
        """Handle keyboard input"""
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            self.running = False
        elif key == ord(' '):
            # 0: MENU, 3: GAME_OVER (Check snake_game logic for exact values)
            if self.game.state.value == 0:
                self.game.start_game()
            elif self.game.state.value == 3:
                self.game.reset_game()
                self.game.start_game()

    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up...")
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        self.game.cleanup()


if __name__ == "__main__":
    try:
        app = SnakeGameApp()
        app.run()
    except Exception as e:
        print(f"Fatal Error: {e}")