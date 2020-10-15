from openalpr import Alpr
from setting import *
import numpy as np
import time
import os
import sys
import cv2


_cur_dir = os.path.dirname(os.path.realpath(__file__))


class PlateDetect:

    def __init__(self, country='eu', region='md'):
        self.alpr = Alpr(country=country,
                         config_file=os.path.join(_cur_dir, 'conf/openalpr.ini'),
                         runtime_dir='/usr/share/openalpr/runtime_data')

        if not self.alpr.is_loaded():
            sys.exit(1)

        self.alpr.set_top_n(5)
        self.alpr.set_default_region(region)

    def destroy(self):
        self.alpr.unload()

    @staticmethod
    def draw_plate(img_crop, detect_plate_list):
        for i in range(len(detect_plate_list)):
            pts = detect_plate_list[i]['coordinates']
            cv2.line(img_crop, (pts[0]['x'], pts[0]['y']), (pts[1]['x'], pts[1]['y']), (255, 0, 0), 2)
            cv2.line(img_crop, (pts[1]['x'], pts[1]['y']), (pts[2]['x'], pts[2]['y']), (255, 0, 0), 2)
            cv2.line(img_crop, (pts[2]['x'], pts[2]['y']), (pts[3]['x'], pts[3]['y']), (255, 0, 0), 2)
            cv2.line(img_crop, (pts[3]['x'], pts[3]['y']), (pts[0]['x'], pts[0]['y']), (255, 0, 0), 2)

        return img_crop

    def detect_file(self, img_file):
        img = cv2.imread(img_file)
        return self.detect_image(img, 0)

    @staticmethod
    def __extract_result__(results_list, cam_ind, roi_x1=0, roi_y1=0):
        if results_list:
            ret_list = []
            for i in range(len(results_list)):
                pos = results_list[i]['coordinates']
                x1, y1 = pos[0]['x'], int(pos[0]['y'] - pos[0]['x'] * CAM_INFO[cam_ind][SKEW_FACTOR])
                x2, y2 = pos[1]['x'], int(pos[1]['y'] - pos[1]['x'] * CAM_INFO[cam_ind][SKEW_FACTOR])
                x3, y3 = pos[2]['x'], int(pos[2]['y'] - pos[2]['x'] * CAM_INFO[cam_ind][SKEW_FACTOR])
                x4, y4 = pos[3]['x'], int(pos[3]['y'] - pos[3]['x'] * CAM_INFO[cam_ind][SKEW_FACTOR])
                coordinate = [min(x1, x2, x3, x4) + roi_x1,
                              min(y1, y2, y3, y4) + roi_y1,
                              max(x1, x2, x3, x4) + roi_x1,
                              max(y1, y2, y3, y4) + roi_y1]

                result = {'plate': results_list[i]['plate'],
                          'confidence': results_list[i]['confidence'],
                          'coordinates': coordinate,
                          'candidates': results_list[i]['candidates'],
                          'time': time.time(),
                          'processed': False}

                ret_list.append(result)

            return ret_list

        else:
            return None

    @staticmethod
    def filter_plate(results):
        """
            Allow these format
            99 x 9999, 99 x 99999
            99 xx 999, 99 xx 9999
            99 xxx 99, 99 xxx 999
        """
        c2d_list = [
            ['Z', '2'],
            ['O', '0'],
            ['D', '0'],
            ['J', '3']
        ]

        max_confidence = 0
        result = None

        for i in range(len(results)):
            plate = results[i]['plate']

            if len(plate) != 7 and len(plate) != 8:
                continue

            str1 = plate[:2]    # 99
            str2 = plate[2]     # x
            str3 = plate[3:5]   # 99, x9, xx
            str4 = plate[5:]    # 99, 999

            # ----- check str1 -----
            for j in range(len(c2d_list)):
                str1 = str1.replace(c2d_list[j][0], c2d_list[j][1])

            if not str1.isdigit():
                continue

            # ----- check str2 -----
            for j in range(len(c2d_list)):
                str2 = str2.replace(c2d_list[j][1], c2d_list[j][0])

            if not str2.isalpha():
                continue

            # ----- check str3 -----
            if str3[0].isdigit() and str3[1].isalpha():
                continue

            # ----- check str4 -----
            for j in range(len(c2d_list)):
                str4 = str4.replace(c2d_list[j][0], c2d_list[j][1])

            if not str4.isdigit():
                continue

            if results[i]['confidence'] > max_confidence:
                max_confidence = results[i]['confidence']
                results[i]['plate'] = str1 + str2 + str3 + str4
                result = results[i]

        return result

    def detect_image(self, img, cam_ind):
        if img is None or img.shape[0] == 0:
            return None

        # ------------------ image crop using ROI -----------------------
        img_h, img_w = img.shape[:2]
        roi_x1, roi_y1 = int(img_w * CAM_INFO[cam_ind][ROI][0]), int(img_h * CAM_INFO[cam_ind][ROI][1])
        roi_x2, roi_y2 = int(img_w * CAM_INFO[cam_ind][ROI][2]), int(img_h * CAM_INFO[cam_ind][ROI][3])
        img_crop = img[roi_y1:roi_y2, roi_x1:roi_x2]

        # ----------------------- image skew ----------------------------
        pts1 = np.float32([[0, 0], [0, 100], [100, 100]])
        pts2 = np.float32([[0, 0], [0, 100], [100, 100 + CAM_INFO[cam_ind][SKEW_FACTOR] * 100]])
        matrix = cv2.getAffineTransform(pts1, pts2)
        img_crop = cv2.warpAffine(img_crop, matrix, (roi_x2 - roi_x1, roi_y2 - roi_y1))

        cv2.imwrite('temp_crop.jpg', img_crop)

        # ---------------------- using library --------------------------
        _, enc = cv2.imencode("*.bmp", img_crop)
        bytes_data = bytes((bytearray(enc)))
        results_list = []

        for i in range(len(CAM_INFO[cam_ind][ANPR_CALIB_LIST])):
            self.alpr.set_prewarp(CAM_INFO[cam_ind][ANPR_CALIB_LIST][i])
            results = self.alpr.recognize_array(bytes_data)
            if results['results']:
                ret = self.__extract_result__(results['results'], cam_ind, roi_x1, roi_y1)
                results_list += ret
                # print(ret[0]['plate'], ret[0]['confidence'])

        # ------------------ filter and regex result ---------------------
        if results_list:
            result = self.filter_plate(results_list)
            # if result is not None:
            #     print("result", result['plate'])
        else:
            result = None

        return result


if __name__ == '__main__':
    class_plate_detect = PlateDetect()
    my_ret = class_plate_detect.detect_file('../1.jpg')
    print(my_ret)
