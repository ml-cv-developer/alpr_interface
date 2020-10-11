import json
import cv2
import os


class GetPlateServer:

    def __init__(self):
        # self.token = "f755a7a9718067f27471bc0ffe875cf88af8a6b1"
        # self.token = "68d6949276385f885283efaca64feb41cbb97f13"
        self.token = "c698b560b1966a08b8b21abe2354e8f5297f5e1a "
        self.server_url = "https://api.platerecognizer.com/v1/plate-reader"

    def detect_image(self, img):
        img_file = 'temp_plate_recognizer.jpg'
        cv2.imwrite(img_file, img)
        return self.detect_file(img_file)

    def detect_file(self, file_img):
        req = """curl -F "upload=@{}" -H "Authorization: Token {}" {}""".format(file_img, self.token, self.server_url)
        result = os.popen(req).read()

        try:
            result = json.loads(result)
            ret = result['results'][0]
            ret_dict = {'plate': ret['plate'],
                        'confidence': ret['score'],
                        'coordinates': [ret['box']['xmin'], ret['box']['ymin'], ret['box']['xmax'], ret['box']['ymax']],
                        'candidates': ret['candidates']}

            return ret_dict

        except:
            return None


if __name__ == '__main__':
    class_get_server = GetPlateServer()
    plate_ret = class_get_server.detect_file('../1.jpg')
    print(plate_ret)
