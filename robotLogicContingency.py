import cv2
import freenect
import skimage.measure
import serial
import time
#from PIL import Image
from skimage import color
from LBAR_Class import LBAR

# Image resizing size
size = 300,230

conf = float(sys.argv[-1])

DEBUGGING = True

# Connect to bluetooth
if DEBUGGING:
    print("Connecting")
lbar = LBAR("/dev/rfcomm0", 9600)
if DEBUGGING:
    print("Created object")
time.sleep(3)
if DEBUGGING:
    print("Connected")

print("Done now, GOOOOO")


static_frame,_ = freenect.sync_get_video()

# Direction Constants
STRAIGHT = 0
LEFT     = 7
RIGHT    = 1

DIRECTIONS = [STRAIGHT, LEFT, RIGHT]

TURN_INDICATOR = {1 :LEFT,  3 :LEFT,  5 :RIGHT,
                  7 :RIGHT, 9 :RIGHT, 11:LEFT,
                  13:LEFT,  15:RIGHT, 17:RIGHT}

DIRECTION_IMAGES = [
    {'0':[], '1':[], '7':[]}, {'0':[], '1':[], '7':[]},
    {'0':[], '1':[], '7':[]}, {'0':[], '1':[], '7':[]},
    {'0':[], '1':[], '7':[]}, {'0':[], '1':[], '7':[]},
    {'0':[], '1':[], '7':[]}, {'0':[], '1':[], '7':[]},
    {'0':[], '1':[], '7':[]}, {'0':[], '1':[], '7':[]},
    {'0':[], '1':[], '7':[]}, {'0':[], '1':[], '7':[]},
    {'0':[], '1':[], '7':[]}, {'0':[], '1':[], '7':[]},
    {'0':[], '1':[], '7':[]}, {'0':[], '1':[], '7':[]},
    {'0':[], '1':[], '7':[]}, {'0':[], '1':[], '7':[]},
    {'0':[], '1':[], '7':[]},
]

def driveForward():
    lbar.send(1)

def driveLeft():
    lbar.send(7)
    time.sleep(.5)

def driveRight():
    lbar.send(9)
    time.sleep(.5)

def turnLeft():
    lbar.send(5)
    time.sleep(.5)
    
def turnRight():
    lbar.send(6)
    time.sleep(.5)

def keywithmaxval(d): # Stack Overflow : the wolf
     """ a) Create a list of the dict's keys and values; 
         b) Return the key with the max value"""  
     v=list(d.values())
     k=list(d.keys())
     return k[v.index(max(v))]

def compare_imgs(curr_frame, end_frame):
    '''
    Return a value which represents how similar
    one image is to another from 0 to 1.
        0 represents completely dissimilar,
        1 represents the same image
    '''
    return skimage.measure.structural_similarity(curr_frame, end_frame)

def init_images():
    '''
    Get all the images for a given state and direction 
    FROM THE something lol and return it inside an array.
    '''
    for state in range(1):
        for direction in map(str, DIRECTIONS):
            if DEBUGGING:
                print("Loading images for state " + str(state)
                      + " and direction " + direction)
            _dir = "/home/acorl/Desktop/coffee_demo/rgb_frames/"
                   + str(state) + "/" + str(direction) + "/"
            
            # Loading grayscale images in the correct state and direction
            for filename in os.listdir(_dir):
                DIRECTION_IMAGES[state][direction].append(color.rgb2gray(cv2.imread(_dir + filename)))


# Did not use, wasn't accurate enough.
def mse(imageA, imageB):
    # The 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
	
    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err

def get_direction_images(state, direction):
    return DIRECTION_IMAGES[state][str(direction)]

def get_final_state_image(state, direction=0):
    '''
    Get the last image for the given state by
    getting the last image in the array
    (This assumes the images are ordered)
    '''
    return get_direction_images(state, direction)[-1]

def similar_enough(curr_frame, final_state_image, confidence_threshold=.7):
    '''Returns True if the curr_frame is similar enough to final_state_image, otherwise...'''
    conf = compare_imgs(curr_frame, final_state_image)
    return conf >= confidence_threshold
    
def get_direction(curr_frame, state):
    '''Determine which direction the current frame is most likely pointing'''
    direc_possibilities = {0:0, 1:0, 7:0}
    
    for direction in DIRECTIONS:
        if DEBUGGING:
            print("Checking images for direction:" + str(direction))
        img_directions = get_direction_images(state, direction)
        for img in img_directions:
            if similar_enough(curr_frame, img):
                direc_possibilities[direction] += 1
                
    if DEBUGGING:
        print(direc_possibilities)
    return keywithmaxval(direc_possibilities)

def rotate(direction):
    '''Direction is an integer, value given by the constants'''
    if direction == LEFT:
        turnLeft()
    else:
        turnRight()

def navigate(direction):
    '''
    Sends the commands to go straight or to correct the
    course in case the robot gets off-center.
    '''
    if DEBUGGING:
        print("Have NOT reached a state change")
        
    if direction == STRAIGHT:
        if DEBUGGING:
            print("Drive straight.")
        driveForward()
    elif direction == LEFT:
        if DEBUGGING:
            print("Looking left, drive right")
        driveRight()
    elif direction == RIGHT:
        if DEBUGGING:
            print("Looking right, drive left")
        driveLeft()
    else:
        # Freak out mode engaged
        if DEBUGGING:
            print("I don't know where to drive.")
        turnLeft()
        pass

def main():
    try:
        # Load images
        init_images()
        
        direction = 0
        state = 0 # Path state
        retrieved_final_state_image = False
        retrieving_coffee = True
        
        while retrieving_coffee:
            if DEBUGGING:
                print("Entering State: " + str(state))
                
            # Get current frame from camera
            curr_frame,_ = freenect.sync_get_video()
            
            # Scale down current frame and convert it to greyscale.
            curr_frame = cv2.cvtColor(curr_frame, cv2.COLOR_RGB2GRAY)
            curr_frame = cv2.resize(curr_frame, size)
            
            if not retrieved_final_state_image:
                if DEBUGGING:
                    print("Getting final state image.")
                final_state_image = get_final_state_image(state)
                retrieved_final_state_image = True
            
            if DEBUGGING:
                print("Entering drive loop")
            if (not state%2):
                # Check for state changes
                if (similar_enough(curr_frame, final_state_image, conf)):
                    if DEBUGGING:
                        print("Reached state change.")
                    state += 1
                    retrieved_final_state_image = False
                else:
                    direction = get_direction(curr_frame, state)
                    navigate(direction)
            else:
                # We're in a turn.
                if DEBUGGING:
                    print("We're turning")
                rotate(turn_indicator[state])
    finally:
        lbar.send(0)
            
if __name__ == "__main__":
    main()
