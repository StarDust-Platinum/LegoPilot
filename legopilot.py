from buildhat import Motor

# Constant Define
GEAR_POSITION_P = 0
GEAR_POSITION_R = 1
GEAR_POSITION_D = 2

# Variable Initialization
gear = GEAR_POSITION_P

# Motor Initialization
steer_motor = Motor('A')
drive_motor = Motor('B')
steer_motor.run_to_position(0)



from picamera2 import Picamera2
import cv2

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
camera.start()

def generate_frames():
    while True:
        frame = camera.capture_array()
        ret, buffer = cv2.imencode('.jpg', cv2.rotate(frame, cv2.ROTATE_180))
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



from flask import Flask, url_for, request, render_template, redirect, Response
from flask_bootstrap import Bootstrap5

app = Flask(__name__)

bootstrap = Bootstrap5(app)

@app.route('/')
def index():
    return render_template('legopilot.html')


@app.route('/change-gear')
def change_gear_to_p():
    global gear
    gear = int(request.args.get('gear', GEAR_POSITION_P))
    return redirect(url_for("index"))


@app.route('/steering')
def steer():
    steer_angle = int(request.args.get('angle', 0))
    if steer_angle > 60:
        steer_angle = 60
    if steer_angle < -60:
        steer_angle = -60 
    steer_motor.run_to_position(steer_angle)
    return redirect(url_for("index"))


@app.route('/accelerator')
def accelerator():
    global gear
    speed = int(request.args.get('speed', 100))
    if gear==GEAR_POSITION_D:
        drive_motor.start(speed)
    elif gear==GEAR_POSITION_R:
        drive_motor.start(-speed)
    return redirect(url_for("index"))
    

@app.route('/brake')
def brake():
    drive_motor.stop()
    return redirect(url_for("index"))


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__=="__main__":
    app.run(host='0.0.0.0', port=5000)
