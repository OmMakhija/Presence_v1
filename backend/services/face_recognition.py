import os
import cv2
import numpy as np
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from backend.models import db, User, FaceEmbedding
from backend.config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceRecognitionService:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.mtcnn = MTCNN(image_size=160, margin=0, keep_all=False, device=self.device)
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        self.match_threshold = Config.FACE_MATCH_THRESHOLD

    def capture_face_embeddings(self, video_source=0, duration=None, fps=None):
        """
        Capture facial embeddings from video stream.
        Migrated from register_user.py

        Args:
            video_source: Camera index or video file path
            duration: Capture duration in seconds (from Config if None)
            fps: Frames per second to capture (from Config if None)

        Returns:
            numpy.ndarray: Averaged facial embedding (128-dimensional)
        """
        duration = duration or Config.FACE_CAPTURE_DURATION
        fps = fps or Config.FACE_CAPTURE_FPS

        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            raise RuntimeError("Could not open video source")

        embeddings = []
        total_frames = duration * fps
        count = 0

        cam_fps = cap.get(cv2.CAP_PROP_FPS) or 30
        interval = int(cam_fps // fps) or 1

        while count < total_frames:
            ret, frame = cap.read()
            if not ret:
                break

            if count % interval == 0:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face = self.mtcnn(rgb)

                if face is not None:
                    with torch.no_grad():
                        emb = self.resnet(face.unsqueeze(0).to(self.device))
                        embeddings.append(emb.cpu().numpy().flatten())

            count += 1

        cap.release()

        if not embeddings:
            raise RuntimeError("No face detected during capture")

        return np.mean(embeddings, axis=0)

    def get_embedding_from_frame(self, frame):
        """
        Extract facial embedding from single frame.
        Migrated from authenticate_user.py

        Args:
            frame: BGR image from OpenCV

        Returns:
            numpy.ndarray: 128-dimensional facial embedding
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face = self.mtcnn(rgb)

        if face is None:
            raise ValueError("No face detected in frame")

        with torch.no_grad():
            emb = self.resnet(face.unsqueeze(0).to(self.device))

        return emb.cpu().numpy().flatten()

    def register_user_face(self, user_id, embedding):
        """
        Store facial embedding for a user in database.
        Replaces pickle storage from legacy scripts.

        Args:
            user_id: User database ID
            embedding: 128-dimensional numpy array

        Returns:
            FaceEmbedding: Database record
        """
        # Check if user already has embedding
        existing = FaceEmbedding.query.filter_by(user_id=user_id).first()

        if existing:
            existing.embedding = embedding
            existing.updated_at = db.func.now()
            db.session.commit()
            return existing
        else:
            face_emb = FaceEmbedding(user_id=user_id, embedding=embedding)
            db.session.add(face_emb)
            db.session.commit()
            return face_emb

    def verify_face(self, user_id, probe_embedding):
        """
        Verify a face against stored embedding for a user.
        Migrated from authenticate_user.py matching logic.

        Args:
            user_id: User database ID
            probe_embedding: 128-dimensional numpy array from captured frame

        Returns:
            tuple: (match_found: bool, distance: float)
        """
        face_record = FaceEmbedding.query.filter_by(user_id=user_id).first()

        if not face_record:
            logger.warning(f"No face record found for user {user_id}")
            return False, float('inf')

        stored_embedding = face_record.embedding
        distance = np.linalg.norm(stored_embedding - probe_embedding)

        match_found = distance < self.match_threshold
        
        logger.info(f"Face Verification: User {user_id} | Distance: {distance:.4f} | Threshold: {self.match_threshold} | Match: {match_found}")
        
        return bool(match_found), float(distance)

    def detect_multiple_faces(self, frame):
        """
        Detect if multiple faces are present in frame.
        Part of proxy detection system.

        Args:
            frame: BGR image from OpenCV

        Returns:
            int: Number of faces detected
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Use MTCNN with keep_all=True to detect all faces
        mtcnn_multi = MTCNN(image_size=160, margin=0, keep_all=True, device=self.device)
        boxes, _ = mtcnn_multi.detect(rgb)

        if boxes is None:
            return 0

        return len(boxes)
