from flask import Blueprint, render_template, session, redirect, url_for, Flask, request, Response, send_from_directory,jsonify
from flask_login import login_required, current_user
from application import db
from application.forms import NewPresentationForm, PresentationFileForm, StopForm
import uuid
from werkzeug.utils import secure_filename
import os
from application.analyzer.Controller import Controller
import pandas as pd
from time import sleep
from imutils.video import VideoStream
import threading
import datetime
import imutils
import cv2
import mediapipe as mp
import numpy as np
import json
import plotly
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from application.scorer.gazeScorer import gazeScorer
from application.scorer.postureScorer import postureScorer
from application.scorer.volumeScorer import volumeScorer
from application.scorer.filledPausesScorer import filledPausesScorer
from application.scorer.articulationRateScorer import articulationRateScorer
from application.scorer.slideFontSizeScorer import slideFontSizeScorer
from application.scorer.slideTextLenghtScorer import slideTextLengthScorer
from .models import Presentation
import logging
import csv


logging.basicConfig(filename='opaf.log', level=logging.DEBUG)
logging.info('Started')

main = Blueprint('main', __name__)

controllerObject=None
outputFrame = None
lock = threading.Lock()
vs=None
stopStreaming=False
t=None

def captureFrame():
    global vs, outputFrame, lock, stopStreaming
    mp_drawing = mp.solutions.drawing_utils
    mp_holistic = mp.solutions.holistic
    holistic_detector = mp_holistic.Holistic(smooth_landmarks=True, min_detection_confidence=0.9,
                                                       min_tracking_confidence=0.9)
    app = Flask(__name__)
    images_dir = os.path.join(app.root_path, 'static', 'assets','images')
    okimage=cv2.imread(os.path.join(images_dir, 'ok.png'))
    notokimage=cv2.imread(os.path.join(images_dir, 'notok.png'))
    while True:
        if (stopStreaming):
            break
        # read the next frame from the video stream, resize it,
        # convert the frame to grayscale, and blur it
        frame = vs.read()
        #frame = imutils.resize(frame, width=400)
        # grab the current timestamp and draw it on the frame
        timestamp = datetime.datetime.now()
        frame.flags.writeable = False
        results = holistic_detector.process(frame)
        frame.flags.writeable = True
        mp_drawing.draw_landmarks(
            frame, results.face_landmarks, mp_holistic.FACE_CONNECTIONS)
        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
        face_landmarks = results.face_landmarks
        pose_landmarks = results.pose_landmarks
        frame = image_overlay(frame, notokimage, 0, 0)
        if (face_landmarks is not None):
            face_keypoints = face_landmarks.landmark
            if (face_keypoints is not None):
                if (pose_landmarks is not None):
                    pose_keypoints = pose_landmarks.landmark
                    if (pose_keypoints is not None):
                        lhip = pose_keypoints[23]
                        rhip = pose_keypoints[24]
                        if(lhip.visibility>0.8 and rhip.visibility>0.8):
                            frame=image_overlay(frame,okimage,0,0)

        cv2.putText(frame, timestamp.strftime(
            "%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
        with lock:
            outputFrame = frame.copy()




def calculateSummary(audioData, videoData, presData):
    audioDict={}
    videoDict={}
    presDict={}

    if videoData is not None:
        gScorer = gazeScorer(videoData)
        pScorer = postureScorer(videoData)
        gazeScore = gScorer.score()
        gazeValue = "Excellent"
        gazeStyle = "style5"
        gazeRecommendation = ""
        gazeTimeline = gScorer.timeline()
        if gazeScore < 4:
            gazeValue = "Good"
            gazeStyle = "style3"
            gazeRecommendation = "<li><i><b>Make eye contact with the audience.</b></i> Your purpose is to communicate with your audience, and people listen more if they feel you are talking directly to them. As you speak, let your eyes settle on one person for several seconds before moving on to somebody else. You do not have to make eye contact with everybody, but make sure you connect with all areas of the audience equally.</li>"
        if gazeScore < 2:
            gazeValue = "To Improve"
            gazeStyle = "style1"
            gazeRecommendation = "<li><i><b>Make eye contact with the audience.</b></i> Your purpose is to communicate with your audience, and people listen more if they feel you are talking directly to them. As you speak, let your eyes settle on one person for several seconds before moving on to somebody else. You do not have to make eye contact with everybody, but make sure you connect with all areas of the audience equally.</li> <li><i><b>Avoid reading from the screen.</b></i> First, if you are reading from the screen, you are not making eye contact with your audience. Second, if you put it on your slide, it is because you wanted them to read it, not you.</li>"

        postureScore = pScorer.score()
        postureValue = "Excellent"
        postureStyle = "style5"
        postureRecommedation = ""
        postureTimeline =pScorer.timeline()

        if postureScore < 4:
            postureValue = "Good"
            postureStyle = "style3"
            postureRecommendation = "<li><i><b>Open Posture</b></i> A speaker should not cross his hands or legs because the audience might perceive it as the unwillingness to communicate.  You should not present your back to the audience.</li> "

        if postureScore < 2:
            postureValue = "To Improve"
            postureStyle = "style1"
            postureRecommendation = "<li><i><b>Open Posture</b></i> A speaker should not cross his hands or legs because the audience might perceive it as the unwillingness to communicate. You should not present your back to the audience.</li> <i><b>Open Gestures</b></i> A speaker should use their hands to communicate with the audience.</li>"
        videoDict = {
            "gazeScore": gazeScore,
            "gazeValue": gazeValue,
            "gazeStyle": gazeStyle,
            "gazeRecommendation": gazeRecommendation,
            "gazeTimeline": gazeTimeline,
            "postureScore": postureScore,
            "postureValue": postureValue,
            "postureStyle": postureStyle,
            "postureRecommendation": postureRecommedation,
            "postureTimeline": postureTimeline
        }

    if audioData is not None:
        vScorer = volumeScorer(audioData)
        fpScorer = filledPausesScorer(audioData)
        aScorer = articulationRateScorer(audioData)
        volumeScore = vScorer.score()
        volumeValue = "Excellent"
        volumeStyle = "style5"
        volumeRecommendation = ""
        if volumeScore < 4:
            volumeValue = "Good"
            volumeStyle = "style3"
            volumeRecommendation = "<li><i><b>Increase the volume of your voice.</b></i> Your first goal is to be comfortably heard by everyone in the audience. If they cannot hear your voice, then you cannot deliver a message to them."

        if volumeScore < 2:
            volumeValue = "To Improve"
            volumeStyle = "style1"
            volumeRecommendation = "<li><i><b>Increase the volume of your voice.</b></i> Your first goal is to be comfortably heard by everyone in the audience. If they cannot hear your voice, then you cannot deliver a message to them. <li><i><b>Start loud.</b></i> It’s not a strict rule, but generally a Excellent idea to open a notch louder than average. It grabs attention and demonstrates enthusiasm.</li> <li><i><b>Finish loud.</b></i> Also not a rule, but speaking louder helps create a rousing, confident finish. This is especially true in a persuasive or motivational speech.</li>"
        volumeTimeline=vScorer.timeline()

        fpScore = fpScorer.score()
        fpValue = "Excellent"
        fpStyle = "style5"
        fpRecommendation = ""
        if fpScore < 4:
            fpValue = "Good"
            fpStyle = "style3"
            fpRecommendation = "<li><i><b>Avoid filler words.</b></i> Um, like, you know, and many others. To an audience, these are indications that you do not know what to say; you sound uncomfortable, so they start to feel uncomfortable as well. Speak slowly enough that you can collect your thoughts before moving ahead. If you really do not know what to say, pause silently until you do.</li>"

        if fpScore < 2:
            fpValue = "To Improve"
            fpStyle = "style1"
            fpRecommendation = "<li><i><b>Avoid filler words.</b></i> Um, like, you know, and many others. To an audience, these are indications that you do not know what to say; you sound uncomfortable, so they start to feel uncomfortable as well. Speak slowly enough that you can collect your thoughts before moving ahead. If you really do not know what to say, pause silently until you do.</li>"
        filledPausesTimeline = fpScorer.timeline()

        articulationScore = aScorer.score()

        articulationValue = "Excellent"
        articulationStyle = "style5"
        articulationRecommendation = ""
        if articulationScore < 4:
            articulationValue = "Good"
            articulationStyle = "style3"
            articulationRecommendation = "<li><i><b>Don’t speak as fast as you do in conversation.</b></i> You might speak as many as 400 words a minute in a lively conversation, but your audience needs you to slow down to 140-160 words a minute. It takes work to develop a slower presenting style, but you’ll be a more effective speaker.</li>"

        if articulationScore < 2:
            articulationValue = "To Improve"
            articulationStyle = "style1"
            articulationRecommendation = "<li><i><b>Don’t speak as fast as you do in conversation.</b></i> You might speak as many as 400 words a minute in a lively conversation, but your audience needs you to slow down to 140-160 words a minute. It takes work to develop a slower presenting style, but you’ll be a more effective speaker.</li>"
        articulationTimeline = aScorer.timeline()
        audioDict={
            "volumeScore": volumeScore,
            "volumeValue": volumeValue,
            "volumeStyle": volumeStyle,
            "volumeRecommendation": volumeRecommendation,
            "volumeTimeline": volumeTimeline,
            "articulationScore": articulationScore,
            "articulationValue": articulationValue,
            "articulationStyle": articulationStyle,
            "articulationRecommendation": articulationRecommendation,
            "articulationTimeline": articulationTimeline,
            "fpScore": fpScore,
            "fpValue": fpValue,
            "fpStyle": fpStyle,
            "fpRecommendation": fpRecommendation,
            "fpTimeline": filledPausesTimeline
        }

    if presData is not None:
        sfsScorer = slideFontSizeScorer(presData)
        stlScorer = slideTextLengthScorer(presData)
        slideFontSizeScore = sfsScorer.score()
        slideFontSizeValue = "Excellent"
        slideFontSizeStyle = "style5"
        slideFontSizeRecommendation = ""
        if slideFontSizeScore < 4:
            slideFontSizeValue = "Good"
            slideFontSizeStyle = "style3"
            slideFontSizeRecommendation = "<li><i><b>Use a large font.</b></i> As a general rule, avoid text smaller than 18 point.</li>"

        if slideFontSizeScore < 2:
            slideFontSizeValue = "To Improve"
            slideFontSizeStyle = "style1"
            slideFontSizeRecommendation = "<li><i><b>Use a large font.</b></i> As a general rule, avoid text smaller than 18 point.</li><li><i><b>Avoid long texts.</b></i>Put no more than 8 lines of text on any slide.</li>"
        slidesTimeline= sfsScorer.timeline()
        slideTextLengthScore = stlScorer.score()
        slideTextLengthValue = "Excellent"
        slideTextLengthStyle = "style5"
        slideTextLengthRecommendation = ""
        if slideTextLengthScore < 4:
            slideTextLengthValue = "Good"
            slideTextLengthStyle = "style3"
            slideTextLengthRecommendation = "<li><i><b>Try to reduce the length of the text in the slides.</b></i> As a general rule, do not use more than 4 single lines.</li>"

        if slideTextLengthScore < 2:
            slideTextLengthValue = "To Improve"
            slideTextLengthStyle = "style1"
            slideTextLengthRecommendation = "<li><i><b>Reduce the amount of text in the slides, the public should not read the slides, but listen to you</b></i> As a general rule, do not use more than 4 single lines.</li>"

        presDict = {
            "slideFontSizeScore": slideFontSizeScore,
            "slideFontSizeValue": slideFontSizeValue,
            "slideFontSizeStyle": slideFontSizeStyle,
            "slideFontSizeRecommendation": slideFontSizeRecommendation,
            "slideTextLengthScore": slideTextLengthScore,
            "slideTextLengthValue": slideTextLengthValue,
            "slideTextLengthStyle": slideTextLengthStyle,
            "slideTextLengthRecommendation": slideTextLengthRecommendation,
            "slidesTimeline": slidesTimeline
        }
    audioDict.update(videoDict)
    audioDict.update(presDict)
    summary=audioDict
    return summary

def createGraphDashboard(x,y,name):
    fig = go.Figure()
    fig.update_layout(width=int(1500))
    fig.add_hrect(y0=4, y1=5, line_width=0, fillcolor="blue", opacity=0.2)
    fig.add_hrect(y0=2, y1=4, line_width=0, fillcolor="purple", opacity=0.2)
    fig.add_hrect(y0=0, y1=2, line_width=0, fillcolor="red", opacity=0.2)
    fig.add_scattergl(x=x, y=y, line={"color": "black"}, marker={"size": 12}, name=name)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def readData(file):
    lines = list(csv.reader(open(file)))
    header, values = lines[0], lines[1:]
    data = {h: v for h, v in zip(header, zip(*values))}
    df = pd.DataFrame.from_dict(data)
    df = df.apply(pd.to_numeric,errors='coerce')
    return df

def generateReport(presId,includePresentation):
    if presId is None:
        presId=session["presId"]
    app = Flask(__name__)
    uploads_dir = os.path.join(app.root_path, 'presentations')
    path = os.path.join(uploads_dir, presId)
    dfAudio=None
    dfVideo=None
    dfSlides=None
    AudioInfo=False
    VideoInfo=False
    SlidesInfo=False
    try:
        dfAudio = readData(os.path.join(path,"Audio","result.csv"))
        AudioInfo=True
    except Exception as e:
        logging.error("Exception occurred Reading Audio Information", exc_info=True)
        print(e)
        AudioInfo=False
    try:
        dfVideo = pd.read_csv(os.path.join(path,"Video","result.csv"))
        VideoInfo=True
    except Exception as e:
        logging.error("Exception occurred in Reading Video Information", exc_info=True)
        print(e)
        VideoInfo = False
    SlidesInfo = False
    if (includePresentation):
        try:
            dfSlides = pd.read_csv(os.path.join(path, "Slides", "result.csv"))
            SlidesInfo=True
        except Exception as e:
            logging.error("Exception occurred in Reading Slides Information", exc_info=True)
            print(e)
            SlidesInfo = False
    summary=calculateSummary(dfAudio,dfVideo,dfSlides)

    graphJSONVolume = None
    graphJSONArticulation = None
    graphJSONFP = None
    if(AudioInfo):
        dfAudio['nrFP'].fillna(0)
        figVol=go.Figure()
        figVol.update_layout(width=int(1500))
        figVol.add_hrect(y0=65, y1=45, line_width=0, fillcolor="blue", opacity=0.2)
        figVol.add_hrect(y0=45, y1=35, line_width=0, fillcolor="purple", opacity=0.2)
        figVol.add_hrect(y0=35, y1=0, line_width=0, fillcolor="red", opacity=0.2)
        figVol.add_scattergl(x=dfAudio.name, y=dfAudio.power, line={"color": "black"},marker={"size":0},name="Trend")
        figVol.add_scattergl(x=dfAudio.name, y=dfAudio.power.where(dfAudio.power >= 45), line={"width":0}, marker={"size":12,"color":"blue"},name="Excellent")
        figVol.add_scattergl(x=dfAudio.name, y=dfAudio.power.where((dfAudio.power > 35) & (dfAudio.power < 45)), line={"width": 0}, marker={"size": 12, "color": "purple"}, name="Good")
        figVol.add_scattergl(x=dfAudio.name, y=dfAudio.power.where(dfAudio.power <= 35), line={"width":0}, marker={"size":12,"color":"red"},name="To Improve")

        figArt = go.Figure()
        figArt.update_layout(width=int(1500))
        figArt.add_hrect(y0=150, y1=200, line_width=0, fillcolor="purple", opacity=0.2)
        figArt.add_hrect(y0=200, y1=220, line_width=0, fillcolor="red", opacity=0.2)
        figArt.add_hrect(y0=80, y1=150, line_width=0, fillcolor="blue", opacity=0.2)
        figArt.add_hrect(y0=20, y1=80, line_width=0, fillcolor="purple", opacity=0.2)
        figArt.add_hrect(y0=20, y1=0, line_width=0, fillcolor="red", opacity=0.2)
        dfAudio.speed=dfAudio.speechrate*60/1.66
        figArt.add_scattergl(x=dfAudio.name, y=dfAudio.speed, line={"color": "black"}, marker={"size": 0}, name="Trend")
        figArt.add_scattergl(x=dfAudio.name, y=dfAudio.speed.where((dfAudio.speed >= 80) & (dfAudio.speed <= 150) ), line={"width": 0},
                             marker={"size": 12, "color": "blue"}, name="Excellent")
        figArt.add_scattergl(x=dfAudio.name, y=dfAudio.speed.where(((dfAudio.speed > 150) & (dfAudio.speed <= 200))|((dfAudio.speed >= 20)&(dfAudio.speed<80))),
                          line={"width": 0}, marker={"size": 12, "color": "purple"}, name="Good")
        figArt.add_scattergl(x=dfAudio.name, y=dfAudio.speed.where((dfAudio.speed < 20)|(dfAudio.speed > 200)), line={"width": 0},
                             marker={"size": 12, "color": "red"}, name="To Improve")

        figFP = go.Figure()
        figFP.update_layout(width=int(1500))
        figFP.add_hrect(y0=1.5, y1=5, line_width=0, fillcolor="red", opacity=0.2)
        figFP.add_hrect(y0=0.5, y1=1.5, line_width=0, fillcolor="purple", opacity=0.2)
        figFP.add_hrect(y0=0, y1=0.5, line_width=0, fillcolor="blue", opacity=0.2)
        figFP.add_scattergl(x=dfAudio.name, y=dfAudio.nrFP, line={"color": "black"}, marker={"size": 0}, name="Trend")
        figFP.add_scattergl(x=dfAudio.name, y=dfAudio.nrFP.where(dfAudio.nrFP < 1),
                             line={"width": 0},
                             marker={"size": 12, "color": "blue"}, name="Excellent")
        figFP.add_scattergl(x=dfAudio.name, y=dfAudio.nrFP.where(
            (dfAudio.nrFP > 0) & (dfAudio.nrFP < 2)),
                             line={"width": 0}, marker={"size": 12, "color": "purple"}, name="Good")
        figFP.add_scattergl(x=dfAudio.name, y=dfAudio.nrFP.where(dfAudio.nrFP > 1),
                             line={"width": 0},
                             marker={"size": 12, "color": "red"}, name="To Improve")

        graphJSONVolume = json.dumps(figVol, cls=plotly.utils.PlotlyJSONEncoder)
        graphJSONArticulation = json.dumps(figArt, cls=plotly.utils.PlotlyJSONEncoder)
        graphJSONFP = json.dumps(figFP, cls=plotly.utils.PlotlyJSONEncoder)

        maxFrameAudio=dfAudio.shape[0]*5
    if (includePresentation and SlidesInfo):
        maxSlide= dfSlides.shape[0]
    else:
        maxSlide=0
    if (VideoInfo):
        maxFrameVideo=dfVideo.shape[0]/2
    else:
        maxFrameVideo=0
    reportInfo={
        "summary":summary,
        "AudioInfo":AudioInfo,
        "VideoInfo":VideoInfo,
        "SlidesInfo":SlidesInfo,
        "maxFrameAudio":maxFrameAudio,
        "maxFrameVideo":maxFrameVideo,
        "maxSlide":maxSlide,
        "graphJSONVolume":graphJSONVolume,
        "graphJSONArticulation":graphJSONArticulation,
        "graphJSONFP":graphJSONFP
    }
    return reportInfo


@main.route('/')
@login_required
def index():
    logging.debug("Index requested")
    query=Presentation.query.filter_by(presenter=current_user.id).order_by(Presentation.date.desc()).limit(10)
    results = query.count()
    if results>0:
        presentations=query.all()
        presentations = presentations[::-1]

        presdict = [i.serialize for i in presentations]
        df=pd.DataFrame(presdict)

        figGaze = createGraphDashboard(df.id,df.gaze,"Gaze")
        figPosture = createGraphDashboard(df.id,df.posture,"Posture")
        figVolume = createGraphDashboard(df.id,df.volume,"Volume")
        figSpeed = createGraphDashboard(df.id,df.speed,"Articulation Rate")
        figFp = createGraphDashboard(df.id,df.fp,"Filled Pauses")
        figFs = createGraphDashboard(df.id, df.fs, "Font Size")
        figTl = createGraphDashboard(df.id,df.tl,"Text Length")
        logging.debug("Index information provided - At least one previous presentation")
        return render_template('index.html', name=current_user.name,figGaze=figGaze, figPosture=figPosture, figVolume=figVolume, figSpeed=figSpeed, figFp=figFp, figFs=figFs, figTl=figTl)
    else:
        logging.debug("Index information provided - No previous presentations")
        return render_template('indexEmpty.html', name=current_user.name)

@main.route('/reports')
@login_required
def reports():
    presQuery= Presentation.query.filter_by(presenter=current_user.id).order_by(Presentation.date.desc()).all()
    presentations=[i.serialize for i in presQuery]
    print(presentations)
    return render_template('reports.html', name=current_user.name,data=presentations)

@main.route('/controls')
@login_required
def controls():
    return render_template('controls.html')

@main.route('/reboot')
@login_required
def reboot():
    os.system('sudo reboot')
    return "Done"

@main.route('/shutdown')
@login_required
def shutdown():
    os.system('sudo halt')
    return "Done"

@main.route('/update')
@login_required
def update():
    os.system('git pull origin main')
    return redirect(url_for('main.controls'))

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route('/presentation',methods=['get', 'post'])
@login_required
def presentation():
    form = NewPresentationForm()
    print("Enter")
    if form.validate_on_submit():
        print("Validated")
        session["duration"] = str(form.duration.data)
        session["includePresentation"] = form.includePresentation.data
        session["presId"] = str(uuid.uuid4())
        app = Flask(__name__)
        uploads_dir = os.path.join(app.root_path, 'presentations')
        path=os.path.join(uploads_dir, session["presId"])
        os.mkdir(path)
        print(path)
        print("\nData received. Now redirecting ...")
        if (session["includePresentation"]):
            f = form.presentationFile.data
            print(f)
            filename = secure_filename(f.filename)
            session["presFile"] = filename
            app = Flask(__name__)
            uploads_dir = os.path.join(app.root_path, 'presentations')
            f.save(os.path.join(uploads_dir, session["presId"], "presentation.pptx"))
            return redirect(url_for('main.prepareRecording'))
        else:
            return redirect(url_for('main.prepareRecording'))

    return render_template('presentation.html', name=current_user.name, form=form)

@main.route('/prepareRecording', methods=['get','post'])
@login_required
def prepareRecording():
    global outputFrame, vs, t
    vs = VideoStream(src=0).start()
    stopStreaming=False
    sleep(2.0)
    t = threading.Thread(target=captureFrame)
    t.daemon = True
    t.start()
    return render_template('prepareRecording.html')

@main.route('/recording', methods=['get','post'])
@login_required
def recording():
    global controllerObject,vs, stopStreaming, t
    stopStreaming=True
    vs.stream.release()
    vs.stop()
    t.join()
    form = StopForm()
    if form.validate_on_submit():
        if controllerObject is not None:
            controllerObject.stop()
            controllerObject = None
        return redirect(url_for('main.reportWaiting'))
    else:
        if session.get("controller") is None:
            app = Flask(__name__)
            uploads_dir = os.path.join(app.root_path, 'presentations')
            path = os.path.join(uploads_dir, session["presId"])
            controllerObject = Controller(int(session["duration"])*60, session["includePresentation"], path)
            controllerObject.run()
    return render_template('recording.html',name=current_user.name, form=form,time=int(session["duration"])*60)

@main.route('/stopRecording', methods=['get','post'])
@login_required
def stoping():
    global controllerObject
    if controllerObject is not None:
        controllerObject.stop()
        controllerObject=None
        return redirect(url_for('main.reportWaiting'))

@main.route('/reportWaiting', methods=['get','post'])
@login_required
def reportWaiting():
    global controllerObject
    while(controllerObject.recordingCheck()):
        sleep(1)
    return redirect(url_for('main.report'))

@main.route('/report', methods=['get','post'])
@login_required
def report():
    presId= session["presId"]
    includePresentation=session["includePresentation"]
    #presId="7435b00d-e8f0-49b7-ba16-74ecd192dea1"
    #includePresentation=True
    reportInfo=generateReport(presId,includePresentation)

    if (includePresentation):
        new_presentation = Presentation(presId=presId,
                                        presenter=current_user.id,
                                        date=datetime.datetime.now(),
                                        gaze=int(reportInfo["summary"]["gazeScore"]),
                                        posture=int(reportInfo["summary"]["postureScore"]),
                                        volume=int(reportInfo["summary"]["volumeScore"]),
                                        speed=int(reportInfo["summary"]["articulationScore"]),
                                        fp=int(reportInfo["summary"]["fpScore"]),
                                        slides=True,
                                        fs=int(reportInfo["summary"]["slideFontSizeScore"]),
                                        tl=int(reportInfo["summary"]["slideTextLengthScore"])
                                        )
    else:
        new_presentation = Presentation(presId=presId,
                                        presenter=current_user.id,
                                        date=datetime.datetime.now(),
                                        gaze=int(reportInfo["summary"]["gazeScore"]),
                                        posture=int(reportInfo["summary"]["postureScore"]),
                                        volume=int(reportInfo["summary"]["volumeScore"]),
                                        speed=int(reportInfo["summary"]["articulationScore"]),
                                        fp=int(reportInfo["summary"]["fpScore"]),
                                        slides=False
                                        )

    db.session.add(new_presentation)
    db.session.commit()

    return render_template("report.html",
                           name=current_user.name,
                           presId=presId,
                           summary=reportInfo["summary"],
                           audioInfo=reportInfo["AudioInfo"],
                           videoInfo=reportInfo["VideoInfo"],
                           slidesInfo=reportInfo["SlidesInfo"],
                           maxFrameAudio=reportInfo["maxFrameAudio"],
                           maxFrameVideo=reportInfo["maxFrameVideo"],
                           maxSlide=reportInfo["maxSlide"],
                           includePresentation=includePresentation,
                           graphJSONVolume=reportInfo["graphJSONVolume"],
                           graphJSONArticulation=reportInfo["graphJSONArticulation"],
                           graphJSONFP=reportInfo["graphJSONFP"])

@main.route('/view_report/<presId>')
@login_required
def view_report(presId):
    presentation = Presentation.query.filter_by(presId=presId).first()
    includePresentation=presentation.slides
    reportInfo = generateReport(presId, includePresentation)
    return render_template("report.html",
                           name=current_user.name,
                           presId=presId,
                           summary=reportInfo["summary"],
                           audioInfo=reportInfo["AudioInfo"],
                           videoInfo=reportInfo["VideoInfo"],
                           slidesInfo=reportInfo["SlidesInfo"],
                           maxFrameAudio=reportInfo["maxFrameAudio"],
                           maxFrameVideo=reportInfo["maxFrameVideo"],
                           maxSlide=reportInfo["maxSlide"],
                           includePresentation=includePresentation,
                           graphJSONVolume=reportInfo["graphJSONVolume"],
                           graphJSONArticulation=reportInfo["graphJSONArticulation"],
                           graphJSONFP=reportInfo["graphJSONFP"])

@main.route('/download_report/<presId>')
@login_required
def download_report(presId):
    presentation = Presentation.query.filter_by(presId=presId).first()
    includePresentation=presentation.slides
    reportInfo = generateReport(presId, includePresentation)
    reportHtml = render_template("report_download.html",
                           name=current_user.name,
                           presId=presId,
                           summary=reportInfo["summary"],
                           audioInfo=reportInfo["AudioInfo"],
                           videoInfo=reportInfo["VideoInfo"],
                           slidesInfo=reportInfo["SlidesInfo"],
                           maxFrameAudio=reportInfo["maxFrameAudio"],
                           maxFrameVideo=reportInfo["maxFrameVideo"],
                           maxSlide=reportInfo["maxSlide"],
                           includePresentation=includePresentation,
                           graphJSONVolume=reportInfo["graphJSONVolume"],
                           graphJSONArticulation=reportInfo["graphJSONArticulation"],
                           graphJSONFP=reportInfo["graphJSONFP"])
    app = Flask(__name__)
    uploads_dir = os.path.join(app.root_path, 'presentations')
    path = os.path.join(uploads_dir, presId)
    filename = path =os.path.join(path,"index.html")
    file = open(filename, "w")
    file.write(reportHtml)
    file.close()


@main.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")


@main.route('/recordings/video/<presId>')
@login_required
def videoRecordings(presId):
    app = Flask(__name__)
    uploads_dir = os.path.join(app.root_path, 'presentations')
    path = os.path.join(uploads_dir, presId,"Video")
    return send_from_directory(path, "video.mp4")

@main.route('/recordings/image/<presId>/<image_number>')
@login_required
def slideImages(presId,image_number):
    app = Flask(__name__)
    image_number=str(image_number)
    if len(image_number)==1:
        image_number="0"+image_number
    uploads_dir = os.path.join(app.root_path, 'presentations')
    path = os.path.join(uploads_dir, presId,"Slides")
    return send_from_directory(path, "slide"+str(image_number)+".png")

@main.route('/recordings/audio/<presId>')
@login_required
def audioRecordings(presId):
    app = Flask(__name__)
    uploads_dir = os.path.join(app.root_path, 'presentations')
    path = os.path.join(uploads_dir, presId,"Audio")
    return send_from_directory(path, "audio.wav")

def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock
	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue
			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
			# ensure the frame was successfully encoded
			if not flag:
				continue
		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
			bytearray(encodedImage) + b'\r\n')

def image_overlay(background,overlay,x,y):
    background_width = background.shape[1]
    background_height = background.shape[0]

    if x >= background_width or y >= background_height:
        return background

    h, w = overlay.shape[0], overlay.shape[1]

    if x + w > background_width:
        w = background_width - x
        overlay = overlay[:, :w]

    if y + h > background_height:
        h = background_height - y
        overlay = overlay[:h]

    if overlay.shape[2] < 4:
        overlay = np.concatenate(
            [
                overlay,
                np.ones((overlay.shape[0], overlay.shape[1], 1), dtype=overlay.dtype) * 255
            ],
            axis=2,
        )

    overlay_image = overlay[..., :3]
    mask = overlay[..., 3:] / 255.0

    background[y:y + h, x:x + w] = (1.0 - mask) * background[y:y + h, x:x + w] + mask * overlay_image

    return background

