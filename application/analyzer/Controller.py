import application.analyzer.extraction.VideoExtractor as ve
import application.analyzer.extraction.AudioExtractor as ae
import application.analyzer.extraction.SlidesExtractor as se
from time import sleep
from threading import Thread, Event

class Controller:

    stopSignal = Event()

    def __init__(self, time, presentation, directory):
        self.directory = directory
        self.time = time
        self.presentation = presentation
        self.videoExtractor = ve.VideoExtractor(directory)
        self.audioExtractor = ae.AudioExtractor(directory)
        if(self.presentation):
            self.slidesExtractor = se.SlidesExtractor(directory)

        self.recording=False

    def record(self):
        if not(self.recording):
            self.videoExtractor.run()
            self.audioExtractor.run()
            if(self.presentation):
                self.slidesExtractor.run()
            self.recording=True
            for i in range(0,self.time):
                if self.stopSignal.is_set():
                    break
                sleep(1)
            self.stopRecord()


    def run(self):
        self.t = Thread(target=self.record, args=())
        self.t.start()

    def stop(self):
        self.stopSignal.set()
        self.t.join()

    def stopRecord(self):
        if (self.recording):
            self.videoExtractor.stop()
            self.audioExtractor.stop()
            if (self.presentation):
                self.slidesExtractor.stop()
            self.videoExtractor.join()
            self.audioExtractor.join()
            if (self.presentation):
                self.slidesExtractor.join()
            self.recording=False
            print("End Recording")

    def recordingCheck(self):
        return(self.recording)