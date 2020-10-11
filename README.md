### Packages

        sudo apt-get update
        sudo apt-get install -y openalpr openalpr-daemon openalpr-utils libopenalpr-dev python3-openalpr
        sudo apt-get install openalpr-utils
        
        sudo apt-get install -y python3-pip
        sudo pip3 install opencv-python
        sudo pip3 install fuzzywuzzy
        
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
    