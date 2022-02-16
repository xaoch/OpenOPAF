import numpy as np
import cv2
import math
import mediapipe as mp

class GeometricGazeExtractor:

    MAX_RIGHT = -45
    MAX_LEFT = 45
    MAX_UP = - 30
    MAX_DOWN = 25

    def fixAngles(self,value):
        if (value>0):
            value =value - 180
        else:
            value= value + 180
        return value

    def gaze(self,keypoints,image,type):
        size = image.shape
        if (type=="face"):
            nose_x = keypoints[1].x * size[1]
            nose_y = keypoints[1].y * size[0]
            leye_x = keypoints[130].x * size[1]
            leye_y = keypoints[130].y * size[0]
            reye_x = keypoints[359].x * size[1]
            reye_y = keypoints[359].y * size[0]
            lear_x = keypoints[127].x * size[1]
            lear_y = keypoints[127].y * size[0]
            rear_x = keypoints[356].x * size[1]
            rear_y = keypoints[356].y * size[0]
            lmouth_x = keypoints[57].x * size[1]
            lmouth_y = keypoints[57].y * size[0]
            rmouth_x = keypoints[287].x * size[1]
            rmouth_y = keypoints[287].y * size[0]
        else:
            nose_x = keypoints[0].x * size[1]
            nose_y = keypoints[0].y * size[0]
            leye_x = keypoints[3].x * size[1]
            leye_y = keypoints[3].y * size[0]
            reye_x = keypoints[6].x * size[1]
            reye_y = keypoints[6].y * size[0]
            lear_x = keypoints[7].x * size[1]
            lear_y = keypoints[7].y * size[0]
            rear_x = keypoints[8].x * size[1]
            rear_y = keypoints[8].y * size[0]
            lmouth_x = keypoints[9].x * size[1]
            lmouth_y = keypoints[9].y * size[0]
            rmouth_x = keypoints[10].x * size[1]
            rmouth_y = keypoints[10].y * size[0]

        image_points = np.array([
            (nose_x, nose_y),  # Nose tip
            (leye_x, leye_y),  # Left eye left corner
            (reye_x, reye_y),  # Right eye right corner
            (lear_x, lear_y),  # Left ear
            (rear_x, rear_y),  # Rigth ear
            (lmouth_x, lmouth_y),  # Left Mouth corner
            (rmouth_x, rmouth_y)  # Right mouth corner
        ], dtype="double")

        if (type=="face"):
            back=False
        else:
            mp_holistic = mp.solutions.holistic
            ls = keypoints[mp_holistic.PoseLandmark.LEFT_SHOULDER]
            rs = keypoints[mp_holistic.PoseLandmark.RIGHT_SHOULDER]
            if (ls.x < rs.x):
                back=True
            else:
                back=False
        if back:
            return "Back"
        else:
            (pitch, yaw, roll) = self.getRotation(image_points,image)
            if (yaw>self.MAX_LEFT):
                return "Left"
            elif (yaw<self.MAX_RIGHT):
                return "Right"
            elif (pitch<self.MAX_UP):
                return "Up"
            elif (pitch>self.MAX_DOWN):
                return "Down"
            else:
                return "Front"

    def getRotation(self,image_points,image):
        size = image.shape
        model_points = np.array([
            (0.0, 0.0, 0.0),  # Nose tip
            (-225.0, 170.0, -135.0),  # Left eye left corner
            (225.0, 170.0, -135.0),  # Right eye right corner
            (-250, 100, -200),  # Left ear
            (250,100,-200),     # Rigth ear
            (-150.0, -150.0, -125.0),  # Left Mouth corner
            (150.0, -150.0, -125.0)  # Right mouth corner
        ])

        # Camera internals

        focal_length = size[1]
        center = (size[1] / 2, size[0] / 2)
        camera_matrix = np.array(
            [[focal_length, 0, center[0]],
             [0, focal_length, center[1]],
             [0, 0, 1]], dtype="double"
        )

        dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
        (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix,
                                                                      dist_coeffs, flags=cv2.cv2.SOLVEPNP_ITERATIVE)

        # Show Image
        (nose_end_point2D, jacobian) = cv2.projectPoints(np.array([(0.0, 0.0, 1000.0)]), rotation_vector,
                                                         translation_vector, camera_matrix, dist_coeffs)

        for p in image_points:
            cv2.circle(image, (int(p[0]), int(p[1])), 3, (0, 0, 255), -1)

        p1 = (int(image_points[0][0]), int(image_points[0][1]))
        p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))

        cv2.line(image, p1, p2, (255, 0, 0), 2)

        # Display image
        #cv2.imshow("Output", image)
        #cv2.waitKey(0)


        rvec_matrix = cv2.Rodrigues(rotation_vector)[0]
        proj_matrix = np.hstack((rvec_matrix, translation_vector))
        eulerAngles = cv2.decomposeProjectionMatrix(proj_matrix)[6]

        pitch = eulerAngles[0]
        yaw = eulerAngles[1]
        roll = eulerAngles[2]
        pitch = self.fixAngles(pitch)
        roll = self.fixAngles(roll)

        return (pitch, yaw, roll)
