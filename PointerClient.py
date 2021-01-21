import socket
import pyautogui
import time 
import numpy as np

HOST = "192.168.128.1"  # The server's hostname or IP address
PORT = 80            # The port used by the server

QUEUE_SIZE = 8
SENSITIVITY = 128
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0
pyautogui.MINIMUM_SLEEP = 0.0

print('Program Start', end='')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print('\rConnected to device', end='')
    s.settimeout(1) # timeout 1s
    q = []
    button0 = 0
    pointing = 0
    mouse = 0
    mode = [0, 0]
    position = pyautogui.position()
    positionTime = time.perf_counter()
    Time = time.perf_counter()
    print('\rMode: pointer      ', end='')

    while True:
        try:
            #s.sendall(b'Hello, world')
            #print('Received', repr(data))
            s.sendall(b'Button')
            button1 = int(s.recv(1024))
            if button0 == 1 and button1 == 0:
                ##print('fall')
                mode[0] += 1
                if mouse == 1:
                    pyautogui.mouseUp(None, None)
                elif mouse == 0:
                    pointing = 0
                elif mouse == 2:
                    pyautogui.click(None, None)
            elif button0 == 0 and button1 == 1:
                ##print('rise')
                mode[1] += 1
                if mouse == 1:
                    pyautogui.mouseDown(position)
                elif mouse == 0:
                    pointing = 1
            if time.perf_counter() - positionTime > 0.1:
                position = pyautogui.position()
            #print(Time)
            if mode == [3, 3]:
                print('\a', end='')
                mouse = (mouse + 1) % 3
                mode = [0, 0]
                if mouse == 1:
                    print('\rMode: mouse        ', end='')
                elif mouse == 0:
                    print('\rMode: pointer      ', end='')
                elif mouse == 2:
                    print('\rMode: presentation ', end='')
            elif mode == [0, 0]:
                Time = time.perf_counter()
            elif time.perf_counter() - Time > 1:
                mode = [0, 0]
                Time = time.perf_counter()
                #print('zero')
            button0 = button1
            #print('Button is:', 'ON' if button1 else 'Off', end='\t')
            s.sendall(b'IMU')
            data = s.recv(1024)
            #print('Angle is:', end=' ')#, repr(data))
            #print('angle is', data.decode('utf-8'))
            ypr = [float(x) for x in data.decode('utf-8').split(' ')]
            #print(ypr)


            q.append(ypr)
            if len(q) > QUEUE_SIZE:
                q.pop(0)
            #print(q)
            if len(q) == QUEUE_SIZE:
                h, _ = np.polyfit(range(QUEUE_SIZE),np.array(q)[:,0],1)
                v, _ = np.polyfit(range(QUEUE_SIZE),np.array(q)[:,2],1)
                #r = np.mean(np.array(q)[:,1])
                #print(r)
                if abs(h) < 0.01 or abs(h) > 8:
                    h = 0
                if abs(v) < 0.01 or abs(v) > 8:
                    v = 0
                ##print('speed  %.2f' %h, ', %.2f' %v)
                if pointing or mouse == 1:
                    pyautogui.moveRel(
                        SENSITIVITY * h, -1 * SENSITIVITY * v, 0,
                        pyautogui.easeOutQuad)

        #time.sleep(0.01)
        except KeyboardInterrupt:
            print('\b\b    ')
            print('Finish')
            exit()
        except:
            pass
