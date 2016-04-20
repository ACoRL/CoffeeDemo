#import the necessary modules
import freenect
import cv2
import numpy as np
import time
import sys
import serial
from LBAR_Class import LBAR

#direction constants
STRAIGHT = 0
LEFT     = 7
RIGHT    = 1

#direction angle constants
STRAIGHT_ANGLE = 85
LEFT_ANGLE     = 55
RIGHT_ANGLE    = 115

#bluetooth connection
print("Connecting")
lbar = LBAR("/dev/rfcomm0", 9600)
print("Created object")
time.sleep(3)
print("Connected")

#function to get RGB image from kinect
def get_RGB():
    array,_ = freenect.sync_get_video()
    array = cv2.cvtColor(array,cv2.COLOR_RGB2BGR)
    return array
 
#function to get depth image from kinect
def get_depth():
    array,_ = freenect.sync_get_depth()
    array = array.astype(np.uint8)
    return array
 
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Please run again and enter state and location.")
        sys.exit(1)
    
    #retrieve program args
    state = sys.argv[1]
    location = sys.argv[2]
    
    #left is the initial direction
    directions = [LEFT, STRAIGHT, RIGHT]
    
    direction_angles = [LEFT_ANGLE, STRAIGHT_ANGLE, RIGHT_ANGLE]
    
    _dir = '/home/acorl/Desktop/coffee_demo/robot_test_data/'
    
    lbar.send(13, LEFT_ANGLE)
        
    for i in range(3):
        filename = str(state) + '_' + str(location) + '_' + str(directions[i]) + '.png'
        
        print('Direction: ' + str(directions[i]) + ' Direction angle: ' + str(direction_angles[i]))
        
        #set direction        
        lbar.send(13, direction_angles[i])
        time.sleep(3)
        
        #retrieve frames from kinect
        rgb_frame = get_RGB()
        depth_frame = get_depth()
        
        print("Saving data...")
        #save frames
        cv2.imwrite(_dir + 'rgb_data/' + filename, rgb_frame)
        cv2.imwrite(_dir + 'depth_data/' + filename, depth_frame)
        
        print('Changing direction...')

    print('Data gathering complete!')
    lbar.send(13, STRAIGHT_ANGLE)
