# file path
REGISTER_FILE = 'register/register.csv'
LOG_FILE = 'logs/result.log'

# main setting
DRAW_ROI = True
DRAW_PLATE = True
SAVE_VIDEO = True
ENABLE_DB = True
PANEL_WIDTH = 180
PANEL_HEIGHT = 80
PANEL_TEXT_HEIGHT = 35

# camera setting
CAMERA_SOURCE = 'camera_source'
RESIZE_FACTOR = 'resize_factor'
SKEW_FACTOR = 'skew_factor'
ROI = 'roi'
ANPR_CALIB_LIST = 'anpr_calib_list'

CAM_INFO = [
    {
        CAMERA_SOURCE: '../video/2.mp4',
        RESIZE_FACTOR: 1.0,
        SKEW_FACTOR: -0.4,
        ROI: [0.2, 0.4, 0.8, 0.95],
        ANPR_CALIB_LIST: [
            '',
            'planar,384.000000,510.000000,0.000900,0.000750,0.070000,0.875000,1.000000,0.000000,0.000000',
            'planar,762.000000,574.000000,-0.000250,0.000950,-0.040000,1.215000,1.000000,0.000000,0.000000',
        ],
    },
    {
        CAMERA_SOURCE: '../video/1.mp4',
        RESIZE_FACTOR: 0.5,
        SKEW_FACTOR: 0.0,
        ROI: [0.2, 0.2, 0.8, 1.0],
        ANPR_CALIB_LIST: [
            '',
            'planar,384.000000,510.000000,0.000900,0.000750,0.070000,0.875000,1.000000,0.000000,0.000000',
            'planar,762.000000,574.000000,-0.000250,0.000950,-0.040000,1.215000,1.000000,0.000000,0.000000',
        ],
    }
]
