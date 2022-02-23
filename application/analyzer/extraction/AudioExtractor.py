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

class AudioExtractor:

    stopSignal = Event()
    q = queue.Queue()

    def __init__(self, directory):
        self.directory = directory
        self.path =  directory+"/Audio"
        self.createFolders()
        self.csv_file = open(self.path + '/result.csv', mode='w')
        self.resultFile = csv.writer(self.csv_file, delimiter=',')
        self.resultFile.writerow(["time", "volume", "speed","filled_pauses","pitch_variation"])
        self.fs = 44100  # Sample rate
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

    def process(self,soundData, outdata, frames, time, status):
        self.q.put(soundData.copy())
        self.time=self.time+self.interval
        try:
            soundData = np.transpose(soundData)
            sound = parselmouth.Sound(soundData, sampling_frequency=self.fs)
            pitch = sound.to_pitch(self.time_step, self.minimum_pitch, self.maximum_pitch)
            mean_Hz = parselmouth.praat.call(pitch, "Get mean", 0, 0, "Hertz")
            stdev_Hz = parselmouth.praat.call(pitch, "Get standard deviation", 0, 0, "Hertz")
            variation = stdev_Hz / mean_Hz
            sourcerun = "praat/syllablenucleiv3.praat"
            objects = run_file(sound, sourcerun, "./*.flac", "None", -25, 2, 0.3, "yes", "English", 1.3, "Table",
                               "OverWriteData", "yes", capture_output=True)
            table = objects[0][0]

            ar = call(table, "Get value", 1, " articulation_rate(nsyll/phonationtime)")
            fp = call(table, "Get value", 1, " nrFP")
            pow = call(table, "Get value", 1, " Power")
            sr = float(call(table, "Get value", 1, " speechrate(nsyll/dur)")) * 60 / 1.66
            print("Articulation Rate: ", ar)
            print("Words per Minute: ", sr)
            print("Filled Pauses: ", fp)
            print("Power: ", pow)
            print("Pitch Variation: ", variation)
            print("Pitch mean: ", mean_Hz)
            print("Pitch SD: ", stdev_Hz)

            # Flip the image horizontally for a later selfie-view display, and convert
            # the BGR image to RGB.
            self.resultFile.writerow([self.time, pow, sr, fp, stdev_Hz])
            sound.save(self.path + "/" + str(self.time) + ".wav", 'WAV')
            outdata[:] = soundData
        except Exception as e:
            print(e)


    def extract(self):
        print("Audio Thread: starting")
        self.time = -5
        with sf.SoundFile(os.path.join(self.path, "audio.wav"), mode='x', samplerate=self.fs, channels=1, subtype="PCM_16") as file:
            with sd.Stream(samplerate=self.fs, channels=1, blocksize=44100*5, callback=self.process):
                while(True):
                    if self.time>=0:
                        file.write(self.q.get())
                    else:
                        self.q.get()
                    sd.sleep(1000)
                    if self.stopSignal.is_set():
                        sd.stop()
                        break
        self.csv_file.close()
        print("Audio Thread: finishing")

    def run(self):
        self.t = Thread(target=self.extract, args=())
        self.t.start()

    def stop(self):
        self.stopSignal.set()
        self.t.join()





