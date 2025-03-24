
import socket
import serial
import subprocess
import atexit
import threading
import time
import http.server
import socketserver
import os
import pigpio
import json
from time import sleep
from subprocess import DEVNULL, STDOUT, check_call

print("|   ---   ***   INTELLIFAN   ***  ---   |")

print("Starting Pigpiod...")
subprocess.run(("sudo killall pigpiod").split(" "))
sleep(1)
subprocess.run(("sudo pigpiod -m").split(" "))
sleep(1)
print("Removing old camera...")

subprocess.run(("sudo pkill -f libcamera").split(" "))
subprocess.run(("sudo pkill -f socat").split(" "))
subprocess.run(("sudo pkill -f PersonDetection").split(" "))
subprocess.run(("sudo pkill -f HandDetection").split(" "))

subprocess.run(("sudo fuser -k 1234/udp 12345/udp").split(" "))
subprocess.run(("sudo fuser -k 8000/tcp 1234/tcp").split(" "))
sleep(1)


pi = pigpio.pi()

pi.write(24, 0)

#GPIO.setmode(GPIO.BOARD)

fan_speed = 1;
person_angle = 0;
angle_time = 0;
angle_timeout = 2;

lower_bound = 35000
upper_bound = 135000

fan_target_angle = 85000
fan_angle = fan_target_angle

turn = 0

childprocs = [];

server_command = ""

hand_addr = None;
person_addr = None;
run_person_detection = False;

servo_interval = 0.05
time_store = 1.5
angle_amount = int(time_store / servo_interval)
previous_fan_angles = []
person_delay = 0.5
person_list = {}
gesture_mode = True


def run_detection():

    #global fan_angle
    global turn
    global person_angle
    global angle_time
    global fan_angle
    global lower_bound
    global upper_bound
    global person_list

    print("Running person application...")
    proc = subprocess.Popen(["./YoloX_Track"], stdout=subprocess.PIPE);

    not_list = [-1,-1,-1]

    target_person = None

    while True:
        line = proc.stdout.readline();
        if not line:
            break;

        if run_person_detection:
            data = line.rstrip().decode("utf-8")
            points = data.split(" ");

            print(data)

            t = time.time()
            if t - not_list[1] > 3.5:
                not_list[2] = -1

            person_keys = list(person_list.keys())

            for i in range(0, len(person_keys)):
                key = person_keys[i]

                if t - person_list[key][1] > 0.5:

                    if target_person != None and person_list[key][2] == target_person[2]:
                        target_person = None

                    del person_list[key]
            person_keys = list(person_list.keys())

            curr_fan_angle = 90 * (fan_angle - lower_bound) / (upper_bound - lower_bound)

            if data.startswith("data"):
                x1 = float(points[1])
                y1 = float(points[2])
                x2 = float(points[3])
                y2 = float(points[4])
                c = int(points[5])

                center = (x1 + x2/2, y1 + y2/2)
                angle_time = time.time()

                curr_angle = 90 * (fan_angle - lower_bound) / (upper_bound - lower_bound) - ((center[0] - 320) / 640) * 60;

                person_list[c] = [curr_angle, angle_time, c]

                if target_person == None and (c != not_list[2]):
                    target_person = person_list[c];
                    turn = 0

                if target_person != None and target_person[2] == c:
                    person_angle = (center[0] - 320) / 640
                    target_person[1] = angle_time

            if turn != 0 and target_person != None:

                if not_list[2] == -1:
                    not_list = target_person;
                    print("Set not_list")

                found = None
                dist = None

                print("Finding new...")
                print(turn)

                for i in range(0, len(person_keys)):

                    print(person_keys)

                    key = person_keys[i]

                    if key == not_list[2]:
                        print("Skip")
                        continue

                    if ( (turn == 1 and (person_list[key][0] > curr_fan_angle))
                        or (turn == -1 and (person_list[key][0] < curr_fan_angle)) ):

                        my_dist = abs(person_list[key][0] - curr_fan_angle)

                        if found == None:
                            found = person_list[key]
                            dist = my_dist
                        else:
                            if my_dist < dist:
                                dist = my_dist
                                found = person_list[key]

                if found != None:
                    print("Found!")
                    print(found)
                    target_person = found
                    turn = 0

gesture_data = "None";

def read_gestures():
    global gesture_data
    global gesture_mode
    global fan_speed
    global turn
    global server_command
    global run_person_detection

    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)  # Change to the correct port

    print("Reading UART data...")
    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()  # Read and decode line
        #print("Gesture")
        #print(line)
        if line and line[0] != ".":
            gesture_data = line + " " + str(round(time.time() * 1000));
            gesture = gesture_data.split(" ")[0];

            print(gesture);

            if gesture_mode:

                if gesture == "SwipeLeft":
                    fan_speed = 1
                    turn = 0
                if gesture == "SwipeRight":
                    fan_speed = 0
                    turn = 0
                    run_person_detection = False;
                if gesture == "Push" and fan_speed:
                    run_person_detection = not run_person_detection
                    turn = 0
                if gesture == "SwipeDown":
                    turn = -1
                if gesture == "SwipeUp":
                    turn = 1;

                fan_speed = max(fan_speed, 0);
                fan_speed = min(fan_speed, 1);

        sleep(0.25)

def control_servo():

    global turn;
    global person_angle
    global previous_fan_angles
    global angle_time
    global fan_angle
    global fan_target_angle
    global lower_bound
    global upper_bound

    PIN = 18
    FREQ = 50

    smooth_increment = 0.15
    linear_increment = 35000 * servo_interval

    equal = 0
    equal_stop = 0.2 / servo_interval

    while True:

        if fan_speed != 0:
            equal_cond = abs(fan_angle - fan_target_angle) < 0.05 * linear_increment

            if run_person_detection:


                #print("Timeout?")
                #print((time.time() - angle_time))
                #print((time.time() - angle_time) < angle_timeout)
                if turn == 0:
                    if (len(previous_fan_angles) == angle_amount) and (time.time() - angle_time < angle_timeout):
                        if person_angle != -1:
                            old_angle = previous_fan_angles[angle_amount - int(person_delay / servo_interval)]
                            fan_target_angle = (old_angle - (60 * person_angle) * (upper_bound - lower_bound) / 90)
                            fan_target_angle = int(fan_target_angle)
                            fan_target_angle = max(lower_bound, min(fan_target_angle, upper_bound))
                        person_angle = -1

                    else:
                        fan_target_angle = fan_angle
                else:

                    if equal_cond and (fan_target_angle == upper_bound or fan_target_angle == lower_bound):
                        turn *= -1;

                    if turn == 1:
                        fan_target_angle = upper_bound
                    else:
                        fan_target_angle = lower_bound

            else:

                if turn == -1:
                    fan_target_angle -= 20000;
                if turn == 1:
                    fan_target_angle += 20000;

                fan_target_angle = int(fan_target_angle)
                fan_target_angle = max(lower_bound, min(fan_target_angle, upper_bound))

                turn = 0


            initial = fan_angle <= fan_target_angle

            if not equal_cond:
                if run_person_detection:
                    if turn == 0:
                        fan_angle = int(fan_angle + (fan_target_angle - fan_angle) * smooth_increment)
                    else:
                        if turn == 1:
                            print("Yes")
                            fan_angle = fan_angle + linear_increment
                        if turn == -1:
                            fan_angle = fan_angle - linear_increment

                else:
                    if fan_angle < fan_target_angle:
                        fan_angle = fan_angle + linear_increment
                    elif fan_angle > fan_target_angle:
                        fan_angle = fan_angle - linear_increment

            next_initial = fan_angle <= fan_target_angle

            if initial != next_initial:
                fan_angle = fan_target_angle

            fan_angle = max(lower_bound, min(fan_angle, upper_bound))

            if equal_cond:
                equal+=1
            else:
                equal=0

            if equal > equal_stop:
                #print("Equal stop")
                pi.hardware_PWM(PIN, 0, int(fan_angle))
            else:
                #print("Equal no")
                #print(fan_angle)
                #print(fan_target_angle)
                pi.hardware_PWM(PIN, FREQ, int(fan_angle))

            previous_fan_angles.append(fan_angle)

            if len(previous_fan_angles) > angle_amount:
                previous_fan_angles = previous_fan_angles[1:]

        sleep(servo_interval)

def control_led():

    pi.set_mode(24, pigpio.OUTPUT)

    while True:

        if fan_speed != 0:
            if run_person_detection:

                speed = 0.5

                t = time.time();
                t = (t % speed) / speed

                if t < 0.5:
                    pi.write(24,1)
                else:
                    pi.write(24,0)

            else:
                pi.write(24,1)
        else:
            pi.write(24,0)

        sleep(0.1)


def is_port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) != 0

def http_server():

    PORT = 8000
    DIRECTORY = "."



    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=DIRECTORY, **kwargs)
        def do_GET(self):

            #print("Received")
            #print(self.path)

            if self.path == "/gesture":
                self.send_response(200)
                self.send_header("Context-type", "text/plain")
                self.end_headers()
                self.wfile.write(str.encode(gesture_data))
            elif self.path == "/people":
                self.send_response(200)
                self.send_header("Context-type", "text/plain")
                self.end_headers()
                self.wfile.write(str.encode(json.dumps(person_list)))
            elif self.path == "/mode":
                self.send_response(200)
                self.send_header("Context-type", "text/plain")
                self.end_headers()
                self.wfile.write(str.encode(str(int(gesture_mode))))
            elif self.path == "/tracking":
                self.send_response(200)
                self.send_header("Context-type", "text/plain")
                self.end_headers()
                self.wfile.write(str.encode(str(int(run_person_detection))))
            elif self.path == "/speed":
                self.send_response(200)
                self.send_header("Context-type", "text/plain")
                self.end_headers()
                self.wfile.write(str.encode(str(int(fan_speed * 10))))
            else:
                super().do_GET()

        def do_POST(self):

            global gesture_mode
            global run_person_detection
            global fan_speed
            global turn

            print("Received post")
            print(self.path)

            content_length = int(self.headers.get('Content-Length', 0))  # Get the length of the data
            post_data = self.rfile.read(content_length).decode('utf-8')  # Read and decode the data

            value = int(post_data)

            if self.path == "/turn":
                turn = value;

            if self.path == "/mode":

                print("Change mode")

                if value == 0:
                    gesture_mode = False
                else:
                    gesture_mode = True

            if self.path == "/tracking":

                print("Change tracking")

                print(value)

                if value == 0:
                    print("Disable detection")
                    run_person_detection = False
                else:
                    print("Enable detection")
                    run_person_detection = True

            if self.path == "/speed":

                speed = value / 10
                fan_speed = speed
                print("Fan speed")
                print(fan_speed)


        def log_message(self, format, *args):
            pass;

    class ReuseAddrTCPServer(socketserver.TCPServer):
        def server_bind(self):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            super().server_bind()

    while True:
        try:
            with ReuseAddrTCPServer(("", PORT), CustomHandler) as httpd:
                print("Serving at http://localhost:" + str(PORT))
                httpd.serve_forever()
        except Exception as e:
            subprocess.run(("ss state time-wait sport = 49200 -K").split(" "))
            print("Socket in use...")
            time.sleep(5)
            continue


def control_fan():

    global run_person_detection
    global turn

    pi.set_mode(23, pigpio.OUTPUT)
    pi.set_PWM_frequency(23,600)

    #pi.write(23, 1)

    #GPIO.setup(12, GPIO.OUT)  # Set pin 3 as an output



    last_zero = time.time()
    full_buffer = 1

    while True:

        #if fan_speed != 0:
        #    pi.write(23, 1)
            #GPIO.output(12, 1)


        to_use_speed = fan_speed

        if fan_speed != 0:
            to_use_speed = min(to_use_speed+0.3, 1)
            if time.time() - last_zero < full_buffer:
                to_use_speed = 1
                print("Do full buffer")
        else:
            last_zero = time.time()

        pi.set_PWM_dutycycle(23, int((to_use_speed ** 0.4) * 255))
            #pi.hardware_PWM(23, FREQ, int(fan_angle))
        #else:
        #    pi.write(23, 0)
            #GPIO.output(12, 0)

        sleep(0.15)


detection = threading.Thread( target=run_detection )
gestures = threading.Thread( target=read_gestures)
fan = threading.Thread(target=control_fan)
servo = threading.Thread(target=control_servo)
led = threading.Thread(target=control_led)
server = threading.Thread(target=http_server)


server.start()
gestures.start()
fan.start()
servo.start()
detection.start()
led.start()


while True:
    sleep(0.5)

pi.stop()
