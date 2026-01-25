"""
Hand tracking module using MediaPipe

File: src/vision/hand_tracker.py
Handles real-time hand detection and gesture recognition
"""

import cv2
import mediapipe as mp
import numpy as np
from collections import deque
from typing import Tuple, Optional
import math

from src.config import ConfigManager


class HandTracker:
    """Real-time hand tracking and gesture detection"""

    # MediaPipe Hand Landmarks
    WRIST = 0
    THUMB_TIP = 4
    INDEX_TIP = 8
    MIDDLE_TIP = 12
    RING_TIP = 16
    PINKY_TIP = 20
    INDEX_PIP = 6
    MIDDLE_PIP = 10
    PALM_CENTER = 9

    def __init__(self):
        """Initialize hand tracker"""
        self.config = ConfigManager.get_game_config()

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=self.config.MAX_NUM_HANDS,
            min_detection_confidence=self.config.HAND_DETECTION_CONFIDENCE,
            min_tracking_confidence=self.config.HAND_TRACKING_CONFIDENCE
        )

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        # Position smoothing
        self.position_history = deque(
            maxlen=self.config.GESTURE_SMOOTHING_WINDOW
        )

        # Hand state tracking
        self.is_hand_detected = False
        self.last_valid_position = None
        self.frame_count = 0

    def detect_hand(self, frame: np.ndarray) -> Tuple[Optional[Tuple[int, int]], bool]:
        """
        Detect hand and return index finger position

        Args:
            frame: Input video frame

        Returns:
            Tuple of (hand_position, is_detected)
        """
        h, w, c = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            landmarks = results.multi_hand_landmarks[0]

            # Get index finger tip (landmark 8)
            index_tip = landmarks.landmark[self.INDEX_TIP]
            x = int(index_tip.x * w)
            y = int(index_tip.y * h)

            # Clamp coordinates to frame bounds
            x = max(0, min(x, w - 1))
            y = max(0, min(y, h - 1))

            position = (x, y)
            self.position_history.append(position)
            self.last_valid_position = position
            self.is_hand_detected = True

            return position, True

        self.is_hand_detected = False
        return None, False

    def detect_fist_gesture(self, frame: np.ndarray) -> bool:
        """
        Detect closed fist gesture for pause/resume

        Args:
            frame: Input video frame

        Returns:
            True if fist is detected
        """
        h, w, c = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        if not results.multi_hand_landmarks:
            return False

        landmarks = results.multi_hand_landmarks[0]

        try:
            # Get relevant points
            thumb_tip = landmarks.landmark[self.THUMB_TIP]
            index_tip = landmarks.landmark[self.INDEX_TIP]
            middle_tip = landmarks.landmark[self.MIDDLE_TIP]
            ring_tip = landmarks.landmark[self.RING_TIP]
            pinky_tip = landmarks.landmark[self.PINKY_TIP]
            wrist = landmarks.landmark[self.WRIST]
            palm = landmarks.landmark[self.PALM_CENTER]

            # Calculate distances from palm center to finger tips
            def distance_3d(p1, p2):
                return math.sqrt(
                    (p1.x - p2.x)**2 +
                    (p1.y - p2.y)**2 +
                    (p1.z - p2.z)**2
                )

            # Check if all fingers are close to palm (fist)
            thumb_dist = distance_3d(thumb_tip, palm)
            index_dist = distance_3d(index_tip, palm)
            middle_dist = distance_3d(middle_tip, palm)
            ring_dist = distance_3d(ring_tip, palm)
            pinky_dist = distance_3d(pinky_tip, palm)

            avg_finger_dist = (
                thumb_dist + index_dist + middle_dist + ring_dist + pinky_dist
            ) / 5

            # Fist detected if average finger distance is below threshold
            return avg_finger_dist < self.config.FIST_CLOSED_THRESHOLD

        except Exception as e:
            print(f"Error in fist detection: {e}")
            return False

    def detect_palm_open(self, frame: np.ndarray) -> bool:
        """
        Detect open palm gesture

        Args:
            frame: Input video frame

        Returns:
            True if palm is open
        """
        h, w, c = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        if not results.multi_hand_landmarks:
            return False

        landmarks = results.multi_hand_landmarks[0]

        try:
            # Get distances between finger tips
            index_tip = landmarks.landmark[self.INDEX_TIP]
            middle_tip = landmarks.landmark[self.MIDDLE_TIP]

            def distance_2d(p1, p2):
                return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

            # Open palm has fingers spread apart
            finger_spread = distance_2d(index_tip, middle_tip)

            return finger_spread > self.config.PALM_SIZE_THRESHOLD

        except:
            return False

    def get_smoothed_position(self) -> Optional[Tuple[int, int]]:
        """
        Get smoothed hand position using moving average

        Returns:
            Smoothed position or None if not available
        """
        if not self.position_history:
            return None

        positions = list(self.position_history)
        if not positions:
            return None

        avg_x = sum(p[0] for p in positions) / len(positions)
        avg_y = sum(p[1] for p in positions) / len(positions)

        return (int(avg_x), int(avg_y))

    def draw_hand_landmarks(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw hand landmarks on frame

        Args:
            frame: Input video frame

        Returns:
            Frame with hand landmarks drawn
        """
        if not self.config.SHOW_HAND_LANDMARKS:
            return frame

        h, w, c = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )

        return frame

    def get_hand_bounding_box(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Get bounding box around detected hand

        Args:
            frame: Input video frame

        Returns:
            Tuple of (x_min, y_min, x_max, y_max) or None
        """
        h, w, c = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        if not results.multi_hand_landmarks:
            return None

        landmarks = results.multi_hand_landmarks[0]

        x_coords = [lm.x * w for lm in landmarks.landmark]
        y_coords = [lm.y * h for lm in landmarks.landmark]

        return (
            int(min(x_coords)),
            int(min(y_coords)),
            int(max(x_coords)),
            int(max(y_coords))
        )

    def reset_history(self) -> None:
        """Reset position history"""
        self.position_history.clear()

    def get_stats(self) -> dict:
        """Get tracker statistics"""
        return {
            'hand_detected': self.is_hand_detected,
            'history_size': len(self.position_history),
            'last_position': self.last_valid_position,
        }