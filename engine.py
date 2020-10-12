from setting import *
from fuzzywuzzy import fuzz
import numpy as np
import func
import logging
import _thread as thread
import time
import cv2
import os


if not os.path.isdir('logs'):
    os.mkdir('logs')
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(message)s')


def register(user_name, plate_name):
    folder_name = os.path.split(REGISTER_FILE)[0]
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)

    new_line = '{},{}\n'.format(user_name, plate_name)
    func.append_text(REGISTER_FILE, new_line)


class PlateRecognition:

    def __init__(self, engine='local'):
        if engine == 'service':
            from get_anpr_server import GetPlateServer
            self.class_engine = GetPlateServer()
        else:
            from plate_detect import PlateDetect
            self.class_engine = PlateDetect()

        self.register_plates = func.load_csv(REGISTER_FILE)
        self.frames = []
        self.result_img = []
        self.buffer_plate_info = []
        self.buffer_plate_img = []
        self.prev_time = 0

    @staticmethod
    def draw_plate(img, plate_dict, user_name=''):
        if plate_dict is None:
            return img
        else:
            pos = plate_dict['coordinates']
            cv2.rectangle(img, (pos[0], pos[1]), (pos[2], pos[3]), (0, 0, 255), 2)
            if user_name == '':
                draw_text = plate_dict['plate'].upper()
            else:
                draw_text = user_name
            cv2.putText(img, draw_text, (pos[0], pos[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        return img

    def draw_plate_ui(self, img):
        if img is None:
            return None

        img_h, img_w = img.shape[:2]
        img_new = np.zeros((img_h + 10, img_w + PANEL_WIDTH + 20, 3), dtype=np.uint8)
        img_new[:] = (196, 114, 68)

        # ----- draw main frame and background -----
        img_new[5:img_h+5, 5:img_w+5] = img
        cv2.rectangle(img_new, (5, 5), (img_w + 5, img_h + 5), (255, 155, 155))

        list_size = int(img_h / (PANEL_HEIGHT + PANEL_TEXT_HEIGHT))
        space = int((img_h - (PANEL_HEIGHT + PANEL_TEXT_HEIGHT) * list_size) / (list_size - 1))
        distance = PANEL_HEIGHT + PANEL_TEXT_HEIGHT + space
        px1, px2 = img_w + 10, img_w + PANEL_WIDTH + 10

        for i in range(list_size):
            y1 = PANEL_HEIGHT + 5 + i * distance
            y2 = PANEL_TEXT_HEIGHT + PANEL_HEIGHT + 5 + i * distance
            cv2.rectangle(img_new, (px1, 5 + i * distance), (px2, y1), (165, 100, 50), -1)
            cv2.rectangle(img_new, (px1, y1), (px2, y2), (150, 80, 40), -1)
            cv2.rectangle(img_new, (px1, 5 + i * distance), (px2, y1), (255, 155, 155))
            cv2.rectangle(img_new, (px1, y1), (px2, y2), (255, 155, 155))

        # ----- draw detected plate result -----
        for i in range(min(list_size, len(self.buffer_plate_info))):
            y1 = PANEL_HEIGHT + 5 + i * distance
            y2 = PANEL_TEXT_HEIGHT + PANEL_HEIGHT - 5 + i * distance
            str_plate = self.buffer_plate_info[i]['plate']
            img_new[5 + i * distance:y1, px1:px2] = self.buffer_plate_img[i]
            cv2.putText(img_new, str_plate, (px1 + 30, y2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        return img_new

    def check_user(self, plate_dict):
        if plate_dict is None:
            return ''

        opt_score = 0
        opt_user = ''
        for i in range(len(self.register_plates)):
            score = fuzz.ratio(plate_dict['plate'], self.register_plates[i][1])
            if score > opt_score:
                opt_score = score
                opt_user = self.register_plates[i][0]

        if opt_score > 85:
            return opt_user
        else:
            return ''

    def process_image_file(self, img_file):
        return self.class_engine.detect_file(img_file)

    def process_image(self, img):
        return self.class_engine.detect_image(img)

    def process_video_file(self, vid_file):
        cap = cv2.VideoCapture(vid_file)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            plate = self.class_engine.detect_image(frame)
            user_name = self.check_user(plate)
            img_draw = self.draw_plate(frame, plate, user_name)

            if plate is not None:
                if user_name == '':
                    logging.info("Plate License is {}".format(plate['plate']))
                else:
                    logging.info("Plate License is {}, User is {}".format(plate['plate'], user_name))

            cv2.imshow('frame', img_draw)
            if cv2.waitKey(10) == ord('q'):
                break

    def update_plate_buffer(self, frame, plate):
        if plate is not None:
            plate_pos = plate['coordinates']
            plate_x1 = int((plate_pos[0] + plate_pos[2] - PANEL_WIDTH) / 2)
            plate_y1 = int((plate_pos[1] + plate_pos[3] - PANEL_HEIGHT) / 2)
            img_plate = frame[plate_y1:plate_y1 + PANEL_HEIGHT, plate_x1:plate_x1 + PANEL_WIDTH]

            if len(self.buffer_plate_info) > 0:
                prev_plate = self.buffer_plate_info[0]['plate']
            else:
                prev_plate = ''

            # compare plate with the previous result
            score = fuzz.ratio(plate['plate'], prev_plate)
            if score > 85 or (plate['time'] - self.prev_time < 2 and score > 65):
                if plate['confidence'] > self.buffer_plate_info[0]['confidence']:
                    if len(self.buffer_plate_info) > 1 and plate['plate'] == self.buffer_plate_info[1]['plate']:
                        self.buffer_plate_info.pop(0)
                        self.buffer_plate_img.pop(0)
                    else:
                        self.buffer_plate_img[0] = img_plate
                        self.buffer_plate_info[0] = plate

                    self.prev_time = plate['time']
            else:
                self.buffer_plate_img.insert(0, img_plate)
                self.buffer_plate_info.insert(0, plate)
                self.prev_time = plate['time']

                if len(self.buffer_plate_info) >= 20:
                    self.buffer_plate_img.pop(-1)
                    self.buffer_plate_info.pop(-1)

    def _thread_read_camera(self, camera_source, camera_ind):
        cap = cv2.VideoCapture(camera_source)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            self.frames[camera_ind] = frame
            time.sleep(0.04)

    def _thread_detect_plate(self, camera_source, camera_ind):
        while True:
            frame = self.frames[camera_ind]
            plate = self.class_engine.detect_image(frame)
            self.update_plate_buffer(frame, plate)
            user_name = self.check_user(plate)
            # self.result_img[camera_ind] = self.draw_plate(frame, plate, user_name)
            self.result_img[camera_ind] = self.draw_plate_ui(frame)

            if plate is not None:
                if user_name == '':
                    logging.info("Camera: {}, Plate License: {}".format(camera_source, plate['plate']))
                else:
                    logging.info("Camera: {}, Plate License: {}, User is {}".
                                 format(camera_source, plate['plate'], user_name))

            time.sleep(0.01)

    def process_cameras(self, camera_list):

        for i in range(len(camera_list)):
            self.frames.append(None)
            self.result_img.append(None)
            thread.start_new_thread(self._thread_read_camera, (camera_list[i], i))
            thread.start_new_thread(self._thread_detect_plate, (camera_list[i], i))

        saver = None

        while True:
            for cam_ind in range(len(camera_list)):
                if self.result_img[cam_ind] is not None:
                    # img = self.frames[cam_ind]
                    img = self.result_img[cam_ind]
                    cv2.imshow(camera_list[cam_ind], img)

                    if SAVE_VIDEO:
                        if saver is None:
                            h, w = img.shape[:2]
                            fourcc = cv2.VideoWriter_fourcc(*'MPEG')
                            saver = cv2.VideoWriter('result{}.avi'.format(cam_ind), fourcc, 30, (w, h))
                        else:
                            saver.write(img)

            if cv2.waitKey(30) == ord('q'):
                break

        saver.release()
        cv2.destroyAllWindows()
