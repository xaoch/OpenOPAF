import sys
import os
from sys import platform
import argparse
import shutil
import random
import csv
from threading import Thread, Event
from time import sleep
import parselmouth
from parselmouth.praat import call, run_file
import numpy as np
import pandas as pd
import sounddevice as sd
import queue
import soundfile as sf
import subprocess
import logging

class AudioExtractor:

    stopSignal = Event()
    q = queue.Queue()

    def __init__(self, directory):
        self.directory = directory
        self.path =  directory+"/Audio"
        self.createFolders()
        self.csv_file = open(self.path + '/result.csv', mode='w')
        #self.resultFile = csv.writer(self.csv_file, delimiter=',')
        #self.resultFile.writerow(["time", "volume", "speed","filled_pauses","pitch_variation"])
        self.fs = 48000  # Sample rate
        self.interval = 5  # Duration of recording seconds

        self.minimum_pitch = 80
        self.maximum_pitch = 400
        self.time_step = 0.01
        print("Audio Thread Ready")

    def createFolders(self):
        print(self.path)
        try:
            os.mkdir(self.path)
        except:
            print("Audio Directories already created")

    def process(self,soundData, frames, time, status):
        self.q.put(soundData.copy())
        self.time=self.time+self.interval
        try:
            soundData = np.transpose(soundData)
            sound = parselmouth.Sound(soundData, sampling_frequency=self.fs)
            audioFileName=self.path + "/" + str(self.time) + ".wav"
            outputFileName=self.path + "/result.csv"
            audioDirectory = self.path + "/"
            sound.save(audioFileName, 'WAV')
            #pitch = sound.to_pitch(self.time_step, self.minimum_pitch, self.maximum_pitch)
            #mean_Hz = parselmouth.praat.call(pitch, "Get mean", 0, 0, "Hertz")
            #stdev_Hz = parselmouth.praat.call(pitch, "Get standard deviation", 0, 0, "Hertz")
            mean_Hz=0
            stdev_Hz=0
            ar=0
            sr=0
            fp=0
            power=0
            #variation = stdev_Hz / mean_Hz
            variation=0
            praatPath=os.path.join(self.path, "..","..","..","praat")
            sourcerun = os.path.join(praatPath,"processing.praat")
            executable="/usr/bin/praat"
            if self.time==0:
                append="OverWriteData"
            else:
                append="AppendData"
            command =[executable,"--run",sourcerun,audioFileName,audioDirectory,outputFileName,"None","-25","2","0.3","yes","English","1.3","Save as text file",append,"no"]
            print("Calliing praat")
            print(command)
            subprocess.run(command)
            print("Returning")
            #objects = run_file(sound, sourcerun, "./*.flac", "None", -25, 2, 0.3, "yes", "English", 1.3, "Table",
            #                   "OverWriteData", "yes", capture_output=True)
            #table = objects[0][0]

            #ar = call(table, "Get value", 1, " articulation_rate(nsyll/phonationtime)")
            #fp = call(table, "Get value", 1, " nrFP")
            #power = call(table, "Get value", 1, " Power")
            #sr = float(call(table, "Get value", 1, " speechrate(nsyll/dur)")) * 60 / 1.66
            #print("Articulation Rate: ", ar)
            #print("Words per Minute: ", sr)
            #print("Filled Pauses: ", fp)
            #print("Power: ", power)
            #print("Pitch Variation: ", variation)
            #print("Pitch mean: ", mean_Hz)
            #print("Pitch SD: ", stdev_Hz)

            # Flip the image horizontally for a later selfie-view display, and convert
            # the BGR image to RGB.
            #self.resultFile.writerow([self.time, power, sr, fp, stdev_Hz])

        except Exception as e:
            logging.error("Exception occurred in Audio Processing", exc_info=True)
            print(e)


    def extract(self):
        print("Audio Thread: starting")
        self.time = -self.interval
        #sd.default.device=11
        try:
            with sf.SoundFile(os.path.join(self.path, "audio.wav"), mode='x', samplerate=self.fs, channels=1, subtype="PCM_16") as file:
                with sd.InputStream(samplerate=self.fs, device="USB PnP Audio Device", channels=1, blocksize=self.fs*self.interval, callback=self.process):
                    while(True):
                        if self.time>=0:
                            file.write(self.q.get())
                        else:
                            self.q.get()
                        sd.sleep(1000)
                        if self.stopSignal.is_set():
                            sd.stop()
                            break
        except Exception as e:
            logging.error("Exception occurred in Initializing Audio", exc_info=True)
            print(e)
        #self.csv_file.close()
        print("Audio Thread: finishing")

    def run(self):
        self.t = Thread(target=self.extract, args=())
        self.t.start()

    def stop(self):
        self.stopSignal.set()
        self.t.join()





