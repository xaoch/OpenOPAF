import sys
import cv2
import mediapipe as mp
import os
from sys import platform
import argparse
import shutil
import random
import csv
from threading import Thread, Event
from time import sleep
import application.analyzer.extraction.GeometricGazeExtractor as gge
import application.analyzer.extraction.GeometricBodyPostureExtractor as gbpe
import time
from imutils.video import VideoStream
import threading

class VideoExtractor:

    stopSignal = Event()

    videoWidth=640
    videoHeight=480
    frame=None
    lock = threading.Lock()

    def captureFrame(self):
        while True:
            if (stopCapturing):
                break
            # read the next frame from the video stream, resize it,
            # convert the frame to grayscale, and blur it
            frame = self.cam.read()
            # frame = imutils.resize(frame, width=400)
            # grab the current timestamp and draw it on the frame
            with self.lock:
                self.frame = frame.copy()

    def __init__(self, directory):
        self.directory = directory
        self.path =  directory+"/Video"
        self.frame_rate = 2
        print("Trying to open camera")
        #self.cam = VideoStream(src=0).start()
        self.cam = cv2.VideoCapture(0)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.videoWidth)  # width
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.videoHeight)  # Height
        #self.cam.set(cv2.CAP_PROP_FPS, self.frame_rate)
        #print(self.cam)
        print("Camera Open")
        self.createFolders()
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_holistic = mp.solutions.holistic
        self.holistic_detector = self.mp_holistic.Holistic(smooth_landmarks=True,min_detection_confidence=0.9, min_tracking_confidence=0.9)
        self.frameNumber = 0
        self.lastGaze = "None"
        self.lastBodyPosture = "None"
        fourcc = cv2.VideoWriter_fourcc(*'H264')
        self.videoFile = cv2.VideoWriter(self.path + '/video.mp4', fourcc, self.frame_rate, (self.videoWidth, self.videoHeight))
        self.csv_file = open(self.path + '/result.csv', mode='w')
        self.resultFile = csv.writer(self.csv_file, delimiter=',')
        self.resultFile.writerow(["frame", "gaze", "posture"])

        print("Video Thread Ready")



    def createFolders(self):
        print(self.path)
        try:
            os.mkdir(self.path)
            os.mkdir(self.path + "/Front")
            os.mkdir(self.path + "/Up")
            os.mkdir(self.path + "/Down")
            os.mkdir(self.path + "/Right")
            os.mkdir(self.path + "/Left")
            os.mkdir(self.path + "/Back")

            os.mkdir(self.path + "/Open")
            os.mkdir(self.path + "/Closed_Torso_Back")
            os.mkdir(self.path + "/Closed_Torse_Side")
            os.mkdir(self.path + "/Closed_Hands_Inside")
            os.mkdir(self.path + "/Hands_Pockets")
            os.mkdir(self.path + "/Hands_Back")
            os.mkdir(self.path + "/Hands_Face")
        except:
            print("Video Directories already created")

    def getHeadRectangle(self,keypoints):
        nose_x = keypoints[1].x * self.videoHeight
        nose_y = keypoints[1].y * self.videoWidth
        top_y = keypoints[10].y * self.videoHeight
        bottom_y = keypoints[152].y * self.videoHeight
        left_x= keypoints[234].x * self.videoWidth
        right_x = keypoints[454].x * self.videoWidth
        height=abs(top_y-bottom_y)
        width=abs(left_x-right_x)

        normalizer=abs(top_y-bottom_y)

        if nose_y == 0:
            return 0, 0, 0, 0
        else:
            x = left_x-normalizer
            y = top_y-normalizer
            if (x<0):
                x=0
            if (y<0):
                y=0
            width= width + normalizer
            height=height+normalizer
            if (x+ width>self.videoWidth):
                width=self.videoWidth-x
            if (y+height>self.videoHeight):
                height=self.videoHeight-y
            return x, y, width, height

    def getHeadRectangleFromPosture(self,keypoints):
        nose_x = keypoints[0].x * self.videoWidth
        nose_y = keypoints[0].y * self.videoHeight
        lshoulder_y = keypoints[12].y * self.videoHeight

        normalizer = (lshoulder_y - nose_y)
        if nose_y == 0:
            return 0, 0, 0, 0
        else:
            x = nose_x - normalizer
            y = nose_y - normalizer
            width = normalizer * 2
            height = normalizer * 2
            return x, y, width, height

    def extract(self):
        print("Video Thread: starting")
        prev = 0
        while self.cam.isOpened():
            time_elapsed = time.time() - prev
            if time_elapsed > 1. / self.frame_rate:
                prev = time.time()
                success, image = self.cam.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    # If loading a video, use 'break' instead of 'continue'.
                    continue
            else:
                continue
            # Flip the image horizontally for a later selfie-view display, and convert
            # the BGR image to RGB.
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            self.frameNumber = self.frameNumber + 1
            print(self.frameNumber)

            image.flags.writeable = False
            results = self.holistic_detector.process(image)

            image.flags.writeable = True

            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            face_landmarks = results.face_landmarks
            pose_landmarks = results.pose_landmarks

            gazeExtractor = gge.GeometricGazeExtractor()
            bodyPostureExtractor = gbpe.GeometricBodyPostureExtractor()
            gaze="None"
            bodyPosture="None"

            if (face_landmarks is not None):
                face_keypoints = face_landmarks.landmark

                if(face_keypoints is not None):
                    headx,heady,headw,headh = self.getHeadRectangle(face_keypoints)
                    head_height=headh

                    gaze=gazeExtractor.gaze(face_keypoints,image,"face")

            else:
                if (pose_landmarks is not None):
                    pose_keypoints = pose_landmarks.landmark
                    if (pose_keypoints is not None):
                        headx, heady, headw, headh = self.getHeadRectangleFromPosture(pose_keypoints)
                        gaze=gazeExtractor.gaze(pose_keypoints,image,"posture")

            print("Gaze: ", gaze)

            if (pose_landmarks is not None):
                pose_keypoints = pose_landmarks.landmark
                if (pose_keypoints is not None):
                    bodyPosture=bodyPostureExtractor.bodyPosture(pose_keypoints,image)

            print("Body Posture: ", bodyPosture)


            self.resultFile.writerow([self.frameNumber, gaze, bodyPosture])
            if (pose_landmarks is not None):
                pose_keypoints = pose_landmarks.landmark
                if (pose_keypoints is not None):
                    self.captureGazeImages(self.frameNumber,image, gaze, self.lastGaze, headx, heady, headw, headh)
                    #print("Head: ",headx,",",heady,",",headw,",",headh)
                    self.captureBodyPostureImages(self.frameNumber, image, bodyPosture, self.lastBodyPosture)
            self.lastGaze=gaze
            self.lastBodyPosture=bodyPosture

            self.mp_drawing.draw_landmarks(image, pose_landmarks, self.mp_holistic.POSE_CONNECTIONS)
            cv2.putText(image, gaze, (10, image.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
            cv2.putText(image, bodyPosture, (10, image.shape[0] - 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
            cv2.putText(image, str(self.frameNumber), (10, image.shape[0] - 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)

            #self.mp_drawing.draw_landmarks(image, face_landmarks, self.mp_holistic.FACE_CONNECTIONS)
            #cv2.imshow('MediaPipe Holistic', image)
            if cv2.waitKey(5) & 0xFF == 27:
                break
            self.videoFile.write(image)
            if self.stopSignal.is_set():
                break
        self.csv_file.close()
        self.videoFile.release()
        self.cam.release()
        print("Video Thread: finishing")


    def captureGazeImages(self, frameNumber, img, gaze, lastGaze, x, y, width, height):
        # Mode 0 Face, Mode 1 Pose
        x = int(x)
        y = int(y)
        width = int(width)
        height = int(height)
        if gaze == "None":
            return
        if gaze == lastGaze:
            return
        if (height > 1 and width > 1):
            img = img[y:y + height, x:x + width]
            imgheight, imgwidth, channels = img.shape
            if imgheight > 0 and imgwidth > 0:
                img = cv2.resize(img, (200, 200))
                cv2.imwrite(self.path + "/" + gaze + "/img_" + str(frameNumber) + ".jpg", img)


    def captureBodyPostureImages(self,frameNumber, img, posture, lastPosture):
        if posture == "None":
            return
        if posture == lastPosture:
            return
        cv2.imwrite(self.path + "/" + posture + "/img_" + str(frameNumber) + ".jpg", img)


    def run(self):
        self.t = Thread(target=self.extract, args=())
        self.daemon = True
        self.t.start()

    def stop(self):
        self.stopSignal.set()
        self.t.join()





