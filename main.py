from setting import CAMERA_LIST
import engine
import func
import logging
import cv2
import sys


if __name__ == '__main__':
    # in_args = ['register',
    #            'Filic',
    #            'B58BPS']
    # in_args = ['check',
    #            'local',
    #            'camera']
    in_args = ['check',
               'local',
               '../video/2.mp4']
    # in_args = ['check',
    #            'local',
    #            '../image/1.png']

    for arg_ind in range(1, len(sys.argv)):
        in_args[arg_ind - 1] = sys.argv[arg_ind]

    run_mode = in_args[0]
    engine_type = in_args[1]
    label = in_args[2]

    if run_mode == 'register':
        engine.register(in_args[1], in_args[2])
    elif run_mode == 'check':
        class_plate = engine.PlateRecognition(engine_type)
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
