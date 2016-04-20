import serial
import time

"""
COMMAND LIST:
-------------------------
0 HALT: stops movement,
    no arguemnts required
1 FORWARD: moves forward at a constant default speed (200m/s),
    no arguments required
2 VARIFOR: moves forward at a variable speed,
    1 arguments: desired speed (1-500mm/s)
3 BACKWARD: moves backward at a constant default speed (200mm/s),
    no arguments required
4 VARIBACK: moves backward at a variable speed,
    1 arguments: desired speed (-1 - (-500)mm/s)
5 LEFTTURN: pivots to the left at a constant speed (200mm/s),
    no arguments required
6 RIGHTTURN: pivots to the right at a constant speed (200mm/s),
    no arguments required
7 VEERLEFT: drives forward at a constant rate (200mm/s)
    and constant arc(500mm) to the left
    no arguments required
8 VARIVEERL: drives forward at a variable rate and arc to the left
    2 arguments: speed (1-500mm/s) and arc (0-2000mm)
9 VEERRIGHT: drives forward at a constant rate (200mm/s)
    and constant arc(500mm) to the right
    no arguments required
10 VARIVEERR: drives forward at a variable rate and arc to the right
    2 arguments required: speed (1-500mm/s) and arc (-1 - (-2000)mm)
11 DIRECTM: Drives each motor at an independant speed
    2 arguments: speed of left wheel and right wheel (-500 - 500mm/s)
12 POLLDATA: Polls IR sensor data from the Roomba, returns a list of
    sensor data in order from left side to right
13 SERVO: Moves the Kinect's Servo into the desired angle. Straight ahead is ~90 degrees
    1 argument: angle desired
    Give it a sec to get to its place

"""
class LBAR:
    global SINGLE_COMMANDS
    global MULTI_PART_COMMANDS
    global POLLDATA
    global SERVO
    global LPACKET
    global LFPACKET
    global LCPACKET
    global RCPACKET
    global RFPACKET
    global RPACKET
    
    SINGLE_COMMANDS = (0, 1, 3, 5, 6, 7, 9)
    MULTI_PART_COMMANDS = (2, 4, 8, 10, 11)
    POLLDATA = 12
    SERVO = 13
    LPACKET = 0
    LFPACKET = 0
    LCPACKET = 0
    RCPACKET = 0
    RFPACKET = 0
    RPACKET = 0
    
    def __init__(self, portname="/dev/rfcomm0", baud=9600):
        self.portname = portname
        self.baud = baud

        global ser
        ser = serial.Serial(self.portname, baudrate=self.baud)
        
        
    
    #Takes in the arguments for speeds and arcs and such and
    #converts each into a series of two bytes, then sends back
    #a list containing the high byte and low byte of each in
    #order
    def _getbytes(self, *args):
        arglist = []
        args = args[0]
        
        for i in range(len(args)):
            hexval = hex(args[i])[2:]
            
            if len(hexval) == 4:
                hexvalhigh = int(hexval[:2], 16)
                hexvallow = int(hexval[2:], 16)
                
            elif len(hexval) == 3:
                hexvalhigh = int ('0' + hexval[:1], 16)
                hexvallow = int(hexval[1:], 16)
            else:
                hexvalhigh = 0
                hexvallow = int(hexval, 16)
                
            arglist.append(hexvalhigh)
            arglist.append(hexvallow)
            print("HEXVALHIGH ", hexvalhigh)
            print("HEXVALLOW ", hexvallow) 
        
        return arglist
        

    #For commands in SINGLE_COMMANDS, there should
    #only be one argument, the actual command, which is then
    #sent off on its own. For MULTI_PART_COMMANDS, the arguments
    #should be the command follows by either one or two arguments.
    #single arguments should be requested speed, multi arguments
    #should either be the speed and arc, or speed of each wheel
    #for command 11
    def send(self, *args):
        
        command = args[0]
        
        
        if command in SINGLE_COMMANDS:
            ser.write(bytearray((command, 0, 0, 0, 0)))
            return 0
        
        elif command == SERVO:
            angle = args[1]
            if angle >= 0 and angle <= 180:
                ser.write(bytearray((command, angle, 0, 0, 0)))
            return 0
            
        elif command in MULTI_PART_COMMANDS:
            arglist = self._getbytes(args[1:])
            if command == 13:
                arglist = arglist[::-1]
            ser.write(bytearray(tuple([command] + arglist)))
            return 0
            
        elif command == POLLDATA:
            ser.write(bytearray((command, 0, 0, 0, 0)))
            time.sleep(.1)
            
            #This reads in the information from the roomba
            #each sensor value will come as a string 4 char's
            #long (hence reading in 4 bytes each), and the int()
            #will then convert the string into an integer
            LPACKET = int(ser.read(4))
            LFPACKET = int(ser.read(4))
            LCPACKET = int(ser.read(4))
            RCPACKET = int(ser.read(4))
            RFPACKET = int(ser.read(4))
            RPACKET = int(ser.read(4))
            
            
            return (LPACKET, LFPACKET, LCPACKET,
                         RCPACKET, RFPACKET, RPACKET)
            
            
    
