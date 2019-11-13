print("init CV")
import cv2
import numpy as np
#for AI
print("     init AI")
import Yolov3_tiny_inference as yolo


#for AI
#Load classes
with open('calibration_files/berries_labels.txt', 'r') as f:
    classes = [line.strip() for line in f.readlines()]
    COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

# Initialize YOLO inference engine
yolov3Inference = yolo.Yolov3Inference(onnx_name='yolov3-tiny.onnx')


devmode =0


if devmode ==1:
    cv2.namedWindow('cropped_image', cv2.WINDOW_NORMAL)



def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):

    label = str(classes[class_id])

    color = COLORS[class_id]

    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)

    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

def firstImage(img):
    # blobdetector
    pass
    # get Data of BIGGEST Strawberry
    pass
    X,Area,Y = berry(img,int(720/2),int(540-100))
    #X,Area,Y = berryAI(img)
    #if found something
        #X= biggest Blob X
        #Y= biggest Blob y
    #else:
        #X = int(720/2)
        #Y = int(540-100)
        #Area = 0
        #print('didnt find anything')
    #Area = Blobarea of biggest Blob
    return X,Area,Y


def berry(img,x_old,y_old):
    if x_old-100  < 1:
        x_old = 100
    elif x_old+100 > 719:
        x_old = 620
    if y_old-100  < 1:
        y_old = 100
    elif y_old+100 > 539:
        y_old = 440
    if x_old == int(720/2): #nothing found in the last frame or first image 
        img_BGR = img       # use whole image
        x_old = 0
        y_old = 0
    else:
        img_BGR = img[y_old-100:y_old+100,x_old-100:x_old+100,:] #cut the part of the last known position of berry
    if devmode == 1:
        cv2.imshow('cropped_image',img_BGR)
    #convert to hsv
    img_HSV = cv2.cvtColor(img_BGR,cv2.COLOR_BGR2HSV)

    #mask
    #lower_red = np.array([0,120,80])
    #upper_red = np.array([8,255,255])
    #mask_red = cv2.inRange(img_HSV, lower_red, upper_red)
    #mask 1
    lower_red = np.array([0,120,80])
    upper_red = np.array([8,255,255])
    mask1 = cv2.inRange(img_HSV, lower_red, upper_red)

    #mask 2
    lower_red = np.array([175,120,80])
    upper_red = np.array([180,210,255])
    mask2 = cv2.inRange(img_HSV, lower_red, upper_red)
    mask_red = mask1 + mask2
    
    #open the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    mask= cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)
    #close the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(4,4))
    mask = cv2.morphologyEx(mask,cv2.MORPH_CLOSE,kernel)

    # calculate x,y coordinate of center
    M =cv2.moments(mask)
    if M["m00"]!= 0:
        X=int(M["m10"] /M["m00"])+x_old-100
        Y=int(M["m01"] /M["m00"])+y_old-100
    else:
        M =cv2.moments(mask_red)
        if M["m00"]!= 0:
            X=int(M["m10"] /M["m00"])+x_old-100
            Y=int(M["m01"] /M["m00"])+y_old-100
        else:
            X = int(720/2)
            Y = int(540-100)
            Area = 0
            print('didnt find anything')
    Area = M['m00']

    #dirty bugfixing: YOLO can output empty boxes
    if Area < 2:
        X = int(720/2)
        Y = int(540-100)
        Area = 0

    #extra code snippet for high strawberrys
    if Y<50:
        Area = Area*1.2

    #extra code snippet for low strawberrys
    if Y in range(300,400) and X in range(320,400):
        Area = Area*1.2
    pass

    return X,Area,Y


def berry_old(img):
    img_BGR = img
    #convert to hsv
    img_HSV = cv2.cvtColor(img_BGR,cv2.COLOR_BGR2HSV)

    #mask 1
    lower_red = np.array([0,120,80])
    upper_red = np.array([8,255,255])
    mask_red1 = cv2.inRange(img_HSV, lower_red, upper_red)

    #mask 2
    lower_red = np.array([160,100,80])
    upper_red = np.array([180,255,255])
    mask_red2 = cv2.inRange(img_HSV, lower_red, upper_red)
    mask_red = mask_red1 + mask_red2

    #open the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    mask= cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)
    #close the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(4,4))
    mask = cv2.morphologyEx(mask,cv2.MORPH_CLOSE,kernel)

    # calculate x,ycoordinate of center
    M =cv2.moments(mask)

    if M["m00"]!= 0:
        X=int(M["m10"] /M["m00"])
        Y=int(M["m01"] /M["m00"])
    else:
        M =cv2.moments(mask_red)
        if M["m00"]!= 0:
            X=int(M["m10"] /M["m00"])
            Y=int(M["m01"] /M["m00"])
        else:
            X = int(720/2)
            Y = int(540-100)
            Area = 0
            print('didnt find anything')
    Area = M['m00']

    #dirty bugfixing: YOLO can output empty boxes
    if Area < 2:
        X = int(720/2)
        Y = int(540-100)
        Area = 0
    return X,Area,Y


def berryAI(img):
    boxes, class_ids, scores = yolov3Inference.detectBerry(img)
    #int(box[0]), int(box[1]), int(box[0]) + int(box[2]), int(box[1]) + int(box[3]))
    if boxes is not None:
        max_Area = 0
        final_x = int(720/2)
        final_y = int(540-100)
        for j in range(0, len(boxes)):
            box = boxes[j]
            class_id = class_ids[j]
            score = scores[j]
            if class_id == 0:
                #draw_prediction(img, class_id, score, int(box[0]), int(box[1]), int(box[0]) + int(box[2]), int(box[1]) + int(box[3]))
                #cropped_image = img[int(box[0]):int(box[0]+box[2]),int(box[1]):int(box[1]+box[3]),:]
                if box[2]>50 and box[3]>50:
                    cropped_image = img[int(box[1]):int(box[1]+box[3]),int(box[0]):int(box[0]+box[2]),:]
                    if devmode == 1:
                        cv2.imshow('cropped_image',cropped_image)
                    X, Area,Y = berry_old(cropped_image)
                    if Area >= max_Area:
                        max_Area = Area
                        final_x = X+int(box[0])
                        final_y = Y+int(box[1])
        X = final_x
        Y = final_y
        Area = max_Area
    else:
        X = int(720/2)
        Y = int(540-100)
        Area = 0
        print('AI says no Berrys today')
    return X,Area,Y
