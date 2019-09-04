import socket
import os
import sys
import struct
import time
import datetime
import picamera
import picamera.array
from fractions import Fraction
from picamera import PiCamera

#Logging
verbose = True

#Motion Settings
threshold = 30
sensitivity = 300

#Camera Setting
testWidth = 128
testHeight = 80
nightShut = 5.5
nightISO = 800
if nightShut > 6:
    nightShut = 5.9
SECONDS2MICRO = 1000000
nightMaxShut = int(nightShut * SECONDS2MICRO)
nightMaxISO = int(nightISO)
nightSleepSec = 8

def sock_client(filepath):
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect(('10.10.1.137',6666))
    except socket.error as msg:
        print(msg)
        print(sys.exit(1))
    while True:
        #for i in range(5):
            #sleep(5)
        #filepath = '/home/pi/Desktop/zzz.jpg'
        fhead = struct.pack(b'128sl',bytes(os.path.basename(filepath),encoding='utf-8'),os.stat(filepath).st_size)
        s.send(fhead)
        print('client filepath:{0}'.format(filepath))
        fp = open(filepath,'rb')
        while 1:
            data = fp.read(1024)
            if not data:
                print('{0} file send over...'.format(filepath))
                break
            s.send(data)
        s.close()
        break
    
def userMotionCode(count):
    msgStr = "Motion Found So Do Something:..."
    camera = PiCamera()
    camera.resolution = (1920,1080)
    camera.framerate = 60

    #camera.start_preview()
    camera.capture('/home/pi/Desktop/'+str(count)+'.jpg')
    camera.close()
    #camera.stop_preview()
    showMessage("userMotionCode",msgStr)
    return

def showTime():
    rightNow = datetime.datetime.now()
    currentTime = "%04d%02d%02d-%02d:%02d:%02d"%(rightNow.year,rightNow.month,rightNow.day,rightNow.hour,rightNow.minute,rightNow.second)
    return currentTime

def showMessage(functionName,messageStr):
    if verbose:
        now = showTime()
        print("%s %s-%s "%(now,functionName,messageStr))
    return

def checkForMotion(data1,data2):
    motionDetected = False
    pixColor = 1
    pixChanges = 0
    for w in range(0,testWidth):
        for h in range(0,testHeight):
            pixDiff = abs(int(data1[h][w][pixColor]) - int(data2[h][w][pixColor]))
            if pixDiff > threshold:
                pixChanges += 1
            if pixChanges > sensitivity:
                break
        if pixChanges > sensitivity:
            break
    if pixChanges > sensitivity:
        motionDetected = True
    return motionDetected

def getStreamImage(daymode):
    isDay = daymode
    with picamera.PiCamera() as camera:
        time.sleep(.5)
        camera.resolution = (testWidth,testHeight)
        with picamera.array.PiRGBArray(camera) as stream:
            if isDay:
                camera.exposure_mode = 'auto'
                camera.awb_mode = 'auto'
            else:
                camera.framerate = Fraction(1,6)
                camera.shutter_speed = nightMaxShut
                camera.exposure_mode = 'off'
                camera.iso = nightMaxISO
                time.sleep(nightSleep)
            camera.capture(stream,format='rgb')
            camera.close()
            return stream.array
        
        
def Main():
    count = 0
    dayTime = True
    msgStr = "Checking for Motion dayTime=%s threshold=%i sensitivity=%i" % (dayTime,threshold,sensitivity)
    showMessage("Main",msgStr)
    stream1 = getStreamImage(dayTime)
    while True:
        stream2 = getStreamImage(dayTime)
        if checkForMotion(stream1,stream2):
            userMotionCode(count)
            sock_client('/home/pi/Desktop/'+str(count)+'.jpg')
            count+=1
        stream1 = stream2
        
        
    return

if __name__ == '__main__':
    try:
        Main()
    finally:
        print("")
        print("++++++++++++++++++++")
        print(" Exiting Program")
        print("++++++++++++++++++++")
        print("")