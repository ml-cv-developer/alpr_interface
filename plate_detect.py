from openalpr import Alpr
import os
import sys
import cv2


_cur_dir = os.path.dirname(os.path.realpath(__file__))


class PlateDetect:

    def __init__(self, country='eu', region='md', debug=True):
        self.debug = debug
        self.alpr = Alpr(country=country,
                         config_file=os.path.join(_cur_dir, 'conf/openalpr.ini'),
                         runtime_dir='/usr/share/openalpr/runtime_data')

        if not self.alpr.is_loaded():
            sys.exit(1)

        self.alpr.set_top_n(5)
        self.alpr.set_default_region(region)

        self.anpr_calib_list = [
            '',
            'planar,1280.000000,660.000000,-0.000150,-0.000150,-0.090000,1.000000,1.000000,0.000000,0.000000',
            'planar,1280.000000,660.000000,-0.000600,-0.000200,-0.150000,0.995000,1.000000,0.000000,0.000000',
            'planar,1280.000000,680.000000,0.000200,-0.000500,-0.040000,1.000000,1.000000,0.000000,0.000000',
            # 'planar,1280.000000,680.000000,-0.000550,0.000000,-0.050000,0.895000,1.000000,0.000000,0.000000',
            # 'planar,1280.000000,680.000000,-0.000000,0.000000,0.080000,0.990000,1.030000,0.000000,0.000000',
            # 'planar,1280.000000,680.000000,-0.000200,0.000000,0.100000,0.870000,1.000000,0.000000,0.000000',
        ]

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
        return self.detect_image(img)

    def detect_image(self, img):
        if img is None or img.shape[0] == 0:
            return None

        _, enc = cv2.imencode("*.bmp", img)
        bytes_data = bytes((bytearray(enc)))
        results_list = []

        for i in range(len(self.anpr_calib_list)):
            self.alpr.set_prewarp(self.anpr_calib_list[i])
            results = self.alpr.recognize_array(bytes_data)
            if results['results']:
                results_list = results['results']
                break

        if results_list:
            pos = results_list[0]['coordinates']
            coordinate = [min(pos[0]['x'], pos[1]['x'], pos[2]['x'], pos[3]['x']),
                          min(pos[0]['y'], pos[1]['y'], pos[2]['y'], pos[3]['y']),
                          max(pos[0]['x'], pos[1]['x'], pos[2]['x'], pos[3]['x']),
                          max(pos[0]['y'], pos[1]['y'], pos[2]['y'], pos[3]['y'])]

            return {'plate': results_list[0]['plate'],
                    'confidence': results_list[0]['confidence'],
                    'coordinates': coordinate,
                    'candidates': results_list[0]['candidates']}

        return None


if __name__ == '__main__':
    class_plate_detect = PlateDetect()
    ret = class_plate_detect.detect_file('../1.jpg')
    print(ret)
