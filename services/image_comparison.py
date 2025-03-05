import face_recognition
import cv2
import numpy as np

class ImageComparison:
    def __init__(self):
        pass

    def align_face(self, image_rgb):
        """Align face using eye landmarks to correct rotation."""
        face_landmarks_list = face_recognition.face_landmarks(image_rgb)
        if len(face_landmarks_list) == 0:
            return image_rgb  # No face detected, return original

        face_landmarks = face_landmarks_list[0]
        left_eye = np.array(face_landmarks['left_eye']).mean(axis=0)
        right_eye = np.array(face_landmarks['right_eye']).mean(axis=0)

        delta_x = right_eye[0] - left_eye[0]
        delta_y = right_eye[1] - left_eye[1]
        angle = np.degrees(np.arctan2(delta_y, delta_x))

        eye_center = (int((left_eye[0] + right_eye[0]) // 2), int((left_eye[1] + right_eye[1]) // 2))
        rot_matrix = cv2.getRotationMatrix2D(eye_center, angle, scale=1.0)
        return cv2.warpAffine(image_rgb, rot_matrix, (image_rgb.shape[1], image_rgb.shape[0]))

    def normalize_lighting(self, image_rgb):
        """Apply histogram equalization to improve contrast in face regions."""
        image_yuv = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2YUV)
        image_yuv[:, :, 0] = cv2.equalizeHist(image_yuv[:, :, 0])  # Equalize Y channel (brightness)
        return cv2.cvtColor(image_yuv, cv2.COLOR_YUV2RGB)

    async def compare_faces(self, image1_path: str, image2_path: str):
        image1 = cv2.imread(image1_path)
        image2 = cv2.imread(image2_path)

        image1_rgb = self.align_face(cv2.cvtColor(image1, cv2.COLOR_BGR2RGB))
        image2_rgb = self.align_face(cv2.cvtColor(image2, cv2.COLOR_BGR2RGB))

        image1_rgb = self.normalize_lighting(image1_rgb)
        image2_rgb = self.normalize_lighting(image2_rgb)

        image1_faces = face_recognition.face_locations(image1_rgb, model="cnn")
        image2_faces = face_recognition.face_locations(image2_rgb, model="cnn")

        if len(image1_faces) != 1 or len(image2_faces) != 1:
            raise ValueError("Each image must contain exactly one face.")

        image1_encodings = face_recognition.face_encodings(image1_rgb, image1_faces, num_jitters=10)
        image2_encodings = face_recognition.face_encodings(image2_rgb, image2_faces, num_jitters=10)

        face_distances = [face_recognition.face_distance(image1_encodings, enc)[0] for enc in image2_encodings]
        min_distance = min(face_distances)

        # Adjust threshold dynamically
        match_threshold = 0.65 if min_distance > 0.5 else 0.6
        is_match = min_distance < match_threshold

        similarity_percentage = (1 - min_distance) * 100

        print(f"Face Distance: {min_distance:.4f}")
        print(f"Face Similarity: {similarity_percentage:.2f}%")
        print("Match: ✅" if is_match else "Match: ❌")

        return {"match": bool(is_match), "similarity": similarity_percentage, "face_distance": min_distance}
