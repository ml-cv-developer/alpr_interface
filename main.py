
from fuzzywuzzy import fuzz
import func
import logging
import _thread as thread
import time
import cv2
import sys
import os


REGISTER_FILE = 'register/register.csv'
CAMERA_LIST = 'conf/camera_list.txt'
if not os.path.isdir('logs'):
    os.mkdir('logs')
logging.basicConfig(filename='logs/result.log', level=logging.INFO, format='%(asctime)s %(message)s')


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
            user_name = class_plate.check_user(plate)
            img_draw = self.draw_plate(frame, plate, user_name)

            if plate is not None:
                if user_name == '':
                    logging.info("Plate License is {}".format(plate['plate']))
                else:
                    logging.info("Plate License is {}, User is {}".format(plate['plate'], user_name))

            cv2.imshow('frame', img_draw)
            if cv2.waitKey(10) == ord('q'):
                break

    def _thread_read_camera(self, camera_source, camera_ind):
        cap = cv2.VideoCapture(camera_source)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            self.frames[camera_ind] = frame
            time.sleep(0.03)

    def _thread_detect_plate(self, camera_source, camera_ind):
        while True:
            frame = self.frames[camera_ind]
            plate = self.class_engine.detect_image(frame)
            user_name = class_plate.check_user(plate)
            self.result_img[camera_ind] = self.draw_plate(frame, plate, user_name)

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

        while True:
            for cam_ind in range(len(camera_list)):
                if self.result_img[cam_ind] is not None:
                    # cv2.imshow(camera_list[cam_ind], self.result_img[cam_ind])
                    cv2.imshow(camera_list[cam_ind], self.frames[cam_ind])

            if cv2.waitKey(10) == ord('q'):
                break


if __name__ == '__main__':
    # in_args = ['register',
    #            'Filic',
    #            'B58BPS']
    # in_args = ['check',
    #            'local',
    #            '../2.avi']
    # in_args = ['check',
    #            'local',
    #            'camera']
    in_args = ['check',
               'local',
               '../1.png']

    for arg_ind in range(1, len(sys.argv)):
        in_args[arg_ind - 1] = sys.argv[arg_ind]

    run_mode = in_args[0]
    engine_type = in_args[1]
    label = in_args[2]

    if run_mode == 'register':
        register(in_args[1], in_args[2])
    elif run_mode == 'check':
        class_plate = PlateRecognition(engine_type)
        if label.lower()[-4:] in ['.jpg', '.bmp', '.png', 'jpeg']:
            img_org = cv2.imread(label)
            plate_result = class_plate.process_image(img_org)
            user = class_plate.check_user(plate_result)
            if plate_result is None:
                pass
            elif user == '':
                logging.info("Plate License is {}".format(plate_result['plate']))
            else:
                logging.info("Plate License is {}, User is {}".format(plate_result['plate'], user))
            img_org = class_plate.draw_plate(img_org, plate_result, user)
            cv2.imshow('ret', img_org)
            cv2.waitKey(0)
        elif label.lower()[-4:] in ['.mp4', '.avi']:
            # class_plate.process_video_file(label)
            class_plate.process_cameras([label])
        elif label == 'camera':
            cam_list = func.load_text(CAMERA_LIST).splitlines()
            class_plate.process_cameras(cam_list)
