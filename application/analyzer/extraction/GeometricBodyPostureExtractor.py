import numpy as np
import cv2
import math
import mediapipe as mp
import matplotlib.path as mp
import logging


class GeometricBodyPostureExtractor:

   hand_occluded_threshold =0.5
   distance_hand_hip_threshold=3
   distance_hand_face_threshold=4
   distance_shoulders_threshold=5

   def ray_tracing_method(x, y, poly):

        n = len(poly)
        inside = False

        p1x, p1y = poly[0]
        for i in range(n + 1):
             p2x, p2y = poly[i % n]
             if y > min(p1y, p2y):
                  if y <= max(p1y, p2y):
                       if x <= max(p1x, p2x):
                            if p1y != p2y:
                                 xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            if p1x == p2x or x <= xints:
                                 inside = not inside
             p1x, p1y = p2x, p2y

        return inside

   def bodyPosture(self,keypoints,image):

        size = image.shape

        nose_x = keypoints[0].x * size[1]
        nose_y = keypoints[0].y * size[0]

        rshoulder_x = keypoints[12].x * size[1]
        rshoulder_y = keypoints[12].y * size[0]
        lshoulder_x = keypoints[11].x * size[1]
        lshoulder_y = keypoints[11].y * size[0]
        lhip_x = keypoints[23].x * size[1]
        lhip_y = keypoints[23].y * size[0]
        rhip_x = keypoints[24].x * size[1]
        rhip_y = keypoints[24].y * size[0]
        lwrist_x = keypoints[15].x * size[1]
        lwrist_y = keypoints[15].y * size[0]
        rwrist_x = keypoints[16].x * size[1]
        rwrist_y = keypoints[16].y * size[0]
        lindex_x = keypoints[19].x * size[1]
        lindex_y = keypoints[19].y * size[0]
        rindex_x = keypoints[20].x * size[1]
        rindex_y = keypoints[20].y * size[0]



        mhip_y = (lhip_y+rhip_y)/2
        mhip_x = (lhip_x+rhip_y)/2
        neck_x = (rshoulder_x + lshoulder_x)/2
        neck_y = (rshoulder_y + lshoulder_y) / 2
        normalizer = math.hypot(mhip_x-neck_x,mhip_y-neck_y)/10
        distance_shoulder= math.hypot(rshoulder_x-lshoulder_x, rshoulder_y-lshoulder_y)
        distance_left_hand_hip = math.hypot(lindex_x - lhip_x, lindex_y - lhip_y)
        distance_right_hand_hip = math.hypot(rindex_x - rhip_x, rindex_y - rhip_y)
        distance_left_hand_face = math.hypot(lwrist_x - nose_x, lwrist_y - nose_y)
        distance_right_hand_face = math.hypot(rwrist_x - nose_x, rwrist_y - nose_y)


        if rshoulder_x != 0 and lshoulder_x != 0 and lshoulder_x < rshoulder_x:
            return "Closed_Torso_Back"
        if rshoulder_x != 0 and lshoulder_x != 0 and lshoulder_x > rshoulder_x and distance_shoulder < normalizer*self.distance_shoulders_threshold:
            return "Closed_Torso_Side"

        polygon = [[rshoulder_x, rshoulder_y], [lshoulder_x, lshoulder_y], [lhip_x, lhip_y], [rhip_x, rhip_y]]
        torso = mp.Path(polygon)
        inside_left_wrist = torso.contains_point([lwrist_x, lwrist_y])
        inside_right_wrist = torso.contains_point([rwrist_x, rwrist_y])
        if inside_left_wrist or inside_right_wrist:
             return "Closed_Hands_Inside"

        if keypoints[15].visibility < self.hand_occluded_threshold or keypoints[16].visibility < self.hand_occluded_threshold:
             return "Hands_Back"
        if distance_left_hand_hip < normalizer * self.distance_hand_hip_threshold or distance_right_hand_hip< normalizer * self.distance_hand_hip_threshold:
             return "Hands_Pockets"
        if distance_left_hand_face < normalizer * self.distance_hand_face_threshold or distance_right_hand_face < normalizer * self.distance_hand_face_threshold:
             return "Hands_Face"

        #lwrist = Point(lwrist_x, lwrist_y)
        #rwrist = Point(rwrist_x, rwrist_y)
        #torso = Polygon([(lshoulder_x,lshoulder_y),(rshoulder_x,rshoulder_y),(lhip_x,lhip_y),(rhip_x,rhip_y)])
        #inside_left_wrist = torso.contains(lwrist)
        #inside_right_wrist = torso.contains(rwrist)

        #polygon = [[rshoulder_x, rshoulder_y],[lshoulder_x, lshoulder_y],[lhip_x, lhip_y], [rhip_x, rhip_y]]
        # torso = mp.Path(polygon)
        # inside_left_wrist = torso.contains_point([lwrist_x,lwrist_y])
        # inside_right_wrist = torso.contains_point([rwrist_x, rwrist_y])

        return "Open"