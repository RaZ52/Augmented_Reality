#!/usr/bin/env python

from __future__ import print_function
import socket
from code.ar_markers.hamming.detect import detect_markers
import PIL
from PIL import Image, ImageTk
import cv2
from tkinter import *
from tkinter import simpledialog
from tkinter import Scale
import math

capture = cv2.VideoCapture(0)
radius = 20
detected_markers = {}
print(detected_markers.values())

root = Tk()
root.bind('<Escape>', lambda e: root.quit())
lmain = Label(root)
lmain.pack()
slide1 = Scale(root, from_=0, to=255, resolution=2, orient=HORIZONTAL)
slide1.set(128)
slide1.pack()

def show_frame(frame):
    # _, frame = capture.read()
    # frame = cv2.flip(frame, 1)
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = PIL.Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    # lmain.after(10, show_frame, frame)

# Determine the origin by clicking
def getorigin(eventorigin):
    global x0,y0
    x0 = eventorigin.x
    y0 = eventorigin.y

    for m_key, m_value in detected_markers.items():
         if math.sqrt((x0 - m_value[0]) ** 2 + (y0 - m_value[1]) ** 2) < radius:
                message = simpledialog.askstring("Send message", "Your message")
                if message is not None:
                    message = f"{m_key}:{message}"
                    s.sendto(message.encode('utf-8'), server)
                    data, addr = s.recvfrom(1024)
                    data = data.decode('utf-8')
                    if "OK" in data:
                            print(message)
                            print(f"OK id: {m_key}")
                    else:
                            print("ERROR")
                else:
                    print("Empty message!")
    print(x0,y0)

if __name__ == '__main__':
        host = '127.0.0.1'
        port = 5001

        server = ('127.0.0.1', 5000)

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((host, port))
        lmain.bind("<Button 1>", getorigin)

        print('Press "q" to quit')

        if capture.isOpened():  # try to get the first frame
                frame_captured, frame = capture.read()
        else:
                frame_captured = False

        while frame_captured:
                img = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                ret, img = cv2.threshold(img, slide1.get(), 255, cv2.THRESH_BINARY)
                # img = cv2.adaptiveThreshold(img, slide1.get(), cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
                markers = detect_markers(img)
                if not markers:
                        detected_markers = {}
                for marker in markers:
                        detected_markers[marker.id] = marker.center
                        # print(marker.contours)
                        try:
                                message = f"get:{marker.id}"
                                s.sendto(message.encode('utf-8'), server)
                                data, addr = s.recvfrom(1024)
                                data = data.decode('utf-8')
                                if data == 'ERROR_1' or data == 'ERROR_2' or data == 'ERROR_3':
                                    print('ERROR')
                                else:
                                    marker.highlite_marker(frame, text_color=(255, 255, 255), text=data)
                        except ConnectionResetError as e:
                                print(f"Server unavailable: {e}")
                        # print(detected_markers)

                show_frame(frame)
                root.update_idletasks()
                root.update()
                cv2.imshow('Detection frame', img)
                # cv2.imshow('Test Frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                frame_captured, frame = capture.read()

        # When everything done, release the capture
        capture.release()
        cv2.destroyAllWindows()