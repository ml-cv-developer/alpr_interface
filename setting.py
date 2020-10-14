# file path
REGISTER_FILE = 'register/register.csv'
LOG_FILE = 'logs/result.log'

# main setting
DRAW_ROI = True
DRAW_PLATE = True
SAVE_VIDEO = True
PANEL_WIDTH = 180
PANEL_HEIGHT = 80
PANEL_TEXT_HEIGHT = 35

# camera setting
CAMERA_LIST = [
    '../video/2.mp4'
]

RESIZE_FACTOR_LIST = [
    0.5
]

# anpr setting
ANPR_ROI_LIST = [
    [0.2, 0.2, 0.8, 1.0]
]

SKEW_FACTOR_LIST = [
    -0.4
]

ANPR_CALIB_LIST = [
    [
        '',
        'planar,384.000000,510.000000,0.000900,0.000750,0.070000,0.875000,1.000000,0.000000,0.000000',
        'planar,762.000000,574.000000,-0.000250,0.000950,-0.040000,1.215000,1.000000,0.000000,0.000000',
    ]
]
