import cv2
import numpy as np
import mediapipe as mp
from scipy.spatial import distance as dist

class LivenessDetectionService:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Eye landmarks for blink detection
        self.LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]

        # EAR threshold
        self.EAR_THRESHOLD = 0.25
        self.BLINK_FRAMES = 3

    def calculate_ear(self, eye_landmarks):
        """Calculate Eye Aspect Ratio"""
        # Vertical distances
        A = dist.euclidean(eye_landmarks[1], eye_landmarks[5])
        B = dist.euclidean(eye_landmarks[2], eye_landmarks[4])

        # Horizontal distance
        C = dist.euclidean(eye_landmarks[0], eye_landmarks[3])

        ear = (A + B) / (2.0 * C)
        return ear

    def detect_blink(self, frame):
        """
        Detect eye blink in frame using Eye Aspect Ratio.

        Args:
            frame: BGR image from OpenCV

        Returns:
            dict: {'blink_detected': bool, 'ear': float}
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return {'blink_detected': False, 'ear': None}

        landmarks = results.multi_face_landmarks[0].landmark
        h, w = frame.shape[:2]

        # Get left eye landmarks
        left_eye = [(landmarks[i].x * w, landmarks[i].y * h)
                    for i in self.LEFT_EYE_INDICES]

        # Get right eye landmarks
        right_eye = [(landmarks[i].x * w, landmarks[i].y * h)
                     for i in self.RIGHT_EYE_INDICES]

        left_ear = self.calculate_ear(left_eye)
        right_ear = self.calculate_ear(right_eye)

        avg_ear = (left_ear + right_ear) / 2.0

        blink_detected = avg_ear < self.EAR_THRESHOLD

        return {
            'blink_detected': blink_detected,
            'ear': avg_ear
        }

    def detect_head_pose(self, frame):
        """
        Detect head pose (looking left/right/up/down).

        Args:
            frame: BGR image from OpenCV

        Returns:
            dict: {'direction': str, 'angles': dict}
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return {'direction': 'unknown', 'angles': None}

        landmarks = results.multi_face_landmarks[0].landmark
        h, w = frame.shape[:2]

        # Key landmarks for pose estimation
        nose_tip = landmarks[1]
        chin = landmarks[152]
        left_eye = landmarks[33]
        right_eye = landmarks[263]

        # Calculate angles (simplified)
        nose_x = nose_tip.x * w
        chin_x = chin.x * w

        eye_center_x = ((left_eye.x + right_eye.x) / 2) * w

        # Horizontal direction
        horizontal_diff = nose_x - eye_center_x

        if abs(horizontal_diff) < 10:
            direction = 'center'
        elif horizontal_diff > 0:
            direction = 'right'
        else:
            direction = 'left'

        return {
            'direction': direction,
            'angles': {'horizontal_diff': horizontal_diff}
        }

    def verify_liveness_challenge(self, challenge_type, video_frames):
        """
        Verify user completed liveness challenge.

        Args:
            challenge_type: 'blink' or 'head_left' or 'head_right'
            video_frames: List of frames captured during challenge

        Returns:
            dict: {'success': bool, 'confidence': float, 'details': dict}
        """
        if challenge_type == 'blink':
            return self._verify_blink_challenge(video_frames)
        elif challenge_type in ['head_left', 'head_right']:
            return self._verify_head_movement(video_frames, challenge_type)
        else:
            return {'success': False, 'confidence': 0.0, 'details': {'error': 'Unknown challenge type'}}

    def _verify_blink_challenge(self, frames):
        """Verify blink was detected in frame sequence"""
        blink_count = 0
        low_ear_frames = 0

        for frame in frames:
            result = self.detect_blink(frame)
            if result['blink_detected']:
                low_ear_frames += 1
            else:
                if low_ear_frames >= self.BLINK_FRAMES:
                    blink_count += 1
                low_ear_frames = 0

        success = blink_count >= 1
        confidence = min(blink_count / 2.0, 1.0)  # Normalize

        return {
            'success': success,
            'confidence': confidence,
            'details': {'blinks_detected': blink_count}
        }

    def _verify_head_movement(self, frames, direction):
        """Verify head moved in specified direction"""
        poses = [self.detect_head_pose(frame) for frame in frames]

        target_direction = direction.replace('head_', '')
        matches = sum(1 for p in poses if p['direction'] == target_direction)

        success = matches >= len(frames) * 0.5  # At least 50% of frames
        confidence = matches / len(frames)

        return {
            'success': success,
            'confidence': confidence,
            'details': {'target': target_direction, 'matches': matches, 'total': len(frames)}
        }
