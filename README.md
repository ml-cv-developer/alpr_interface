### Packages

        sudo apt-get update
        sudo apt-get install -y openalpr openalpr-daemon openalpr-utils libopenalpr-dev python3-openalpr
        sudo apt-get install openalpr-utils
        
        sudo apt-get install -y python3-pip
        sudo pip3 install opencv-python
        sudo pip3 install fuzzywuzzy
        sudo pip3 install python-Levenshtein
        sudo pip3 install kivy
        sudo pip3 install pygame
        sudo pip3 install mysql-connector-python
        
        
In case of Ubuntu18.04, please use this link for openalpr

        https://gist.github.com/braitsch/ee5434f91744026abb6c099f98e67613
        
If Kivy isn't installed, please use this link

        https://gist.github.com/rodnaxel/822fae7e8414dcb7616e068a69103060
        
### Run script

- Register License Plate

        python3 main.py  register  user_name  plate_number
        
    For example
    
        python3 main.py  register  Aleksa  SH62548

- Check image or video file

        python3 main.py  check  engine_type  file_name
    
    `engine_type` is the type of ALPR engine. Can be one of the 'local' and 'service'
    
        engine_type: local  : Will use openAlPR enigne can run without Internet
                     service: Will use online service api
        
    For example
    
        python3 main.py check local 1.avi
        python3 main.py check service 1.jpg
        
- Check multi-cameras

        python3 main.py  check  engine_type  camera
        
    engine_type is same as above.
    And in this case will read `conf/camera_list.txt` for multi camera url.
    
    For example
    
        python3 main.py  check  local  camera
        
    The detected results will be stored in `logs/result.log`
    
- Check with UI

        python3 start_ui.py
    