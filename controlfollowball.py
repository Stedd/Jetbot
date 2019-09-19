import scipy.io
X_max = 720
Y_max = 540

#import line vel_function
leftline = scipy.io.loadmat('/home/jetbot/state_of_art_Software/calibration_files/lineleft.mat')
rightline = scipy.io.loadmat('/home/jetbot/state_of_art_Software/calibration_files/lineright.mat')
vel_leftline = leftline['lineleft']
vel_rightline = rightline['lineright']
#import ball vel function
leftball = scipy.io.loadmat('/home/jetbot/state_of_art_Software/calibration_files/ballleft.mat')
rightball = scipy.io.loadmat('/home/jetbot/state_of_art_Software/calibration_files/ballright.mat')
vel_leftball = leftball['ballleft']
vel_rightball = rightball['ballright']





def followball(x,y,x_old):
    if x == int(X_max/2) and y == int(Y_max-100):   #nothing found
        print("Lost my line")
        if x_old < X_max/2: #lost it to the left
            left = 0
            right = 50
        else:
            left = 50
            right = 0
    else:
        left = vel_leftball[x,y]
        right = vel_rightball[x,y]
    return left,right

def followline(x,y,x_old):
    if x == int(X_max/2) and y == int(Y_max-100):   #nothing found
        print("Lost my line")
        if x_old < X_max/2: #lost it to the left
            left = 0
            right = 50
        else:
            left = 50
            right = 0
    else:
        left = vel_leftline[x,y]
        right = vel_rightline[x,y]
    return left,right
