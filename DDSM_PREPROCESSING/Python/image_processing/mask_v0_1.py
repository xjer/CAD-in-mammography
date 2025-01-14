'''
mask_v0_1.py
[Goal]
1. Create a function from 05_Save_AOI
2. Automate generation of images without tags into another folder
3. Tweak tresh parameters
'''

# import necessary packages

import argparse, os, glob, time
import cv2
import concurrent.futures
from tqdm import tqdm
import multiprocessing
 
# [Function] masking Images script
def maskImages(inputIM):
    # Load image
    image = cv2.imread(inputIM)
    
    # Copy original image for viewing purposes
    imageInput = image.copy()

    # Gausian blurring before finding contours
    image_Gauzz = cv2.GaussianBlur(image,(5,5),0)

    # Adding Filters 
    gray = cv2.cvtColor(image_Gauzz, cv2.COLOR_BGR2GRAY) #Added this to allow contours to work
    thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)[1]

    # Finding Contours
    contours= cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0] 
    # only need outer contours so we use RETR_EXTERNAL

    # Display contour
    imageFinal = image.copy()
    
    cv2.drawContours(image, contours, -1, (0,255,255), 3)

    # Filter Contours Area
    cntArea = [ ]
    for cnt in contours:
        cntArea.append(cv2.contourArea(cnt))

    for cntUnwanted in contours:
        if cv2.contourArea(cntUnwanted) != max(cntArea):
        # Fill unwanted contours black
            cv2.fillPoly(imageFinal, pts = [cntUnwanted], color = (0,0,0))
    
    # Prep Write file and check if UNIX or not
    if os.name == 'posix':
        toConvert_filename = inputIM.split("/").pop()
    elif os.name == 'nt':
        toConvert_filename = inputIM.split("\\").pop()
    else:
        print ("Operating System not supported: "+os.name)
        quit()
    # Write file
    #print(os.path.join(args["folder"],"Masked",toConvert_filename))
    cv2.imwrite(os.path.join(args["folder"],"Masked",toConvert_filename),imageFinal)

    '''
    # View images for troubleshooting
    import numpy as np# Display multiple images
    # view image
    numpy_viewport = np.concatenate((imageInput,image_Gauzz, image, imageFinal),axis = 1)
    cv2.imshow("Viewport", numpy_viewport)
    # Improvise waitKey to only close upon pressing esc
    k = cv2.waitKey(0)
    while k != 27:
        k = cv2.waitKey(0)
    cv2.destroyAllWindows()
    '''
    # for visualization of the loading bar
    time.sleep(0.001)

# [Function] Create necessary folder function
def chkFolder(flder_path):
    if not os.path.exists(flder_path):
        print ("Folder don't exist. Making..")
        os.makedirs(flder_path)

# construct argument parsing
argparser = argparse.ArgumentParser()
argparser.add_argument("-f", "--folder", required=True,
	help="please insert path of the folder containing the images")
args = vars(argparser.parse_args())

chkFolder(args["folder"]+"Masked")

files = glob.glob( os.path.join(args["folder"],'*.png'), recursive=True)

# An attempt at parallel processing
with concurrent.futures.ThreadPoolExecutor(multiprocessing.cpu_count()) as executor: 
    list(tqdm(executor.map(maskImages, files), total=len(files)))
    #executor.map(maskImages, files)
