import cv2
import numpy as np
import logging
logging.basicConfig(level=logging.DEBUG,
                    format=' %(asctime)s - %(levelname)s - %(message)s')


def process(frame):
    numCubes = 0
    cubeCentres = []

    logging.debug('Processing Start')
    # cv2.imshow("true", frame)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #cv2.imshow("HSV image", hsv)

    #gray = cv2.cvtColor(hsv, cv2.COLOR_BGR2GRAY)
    ##cv2.imshow("gray", gray)

    #ret,thresh_image = cv2.threshold(gray,180,255,cv2.THRESH_OTSU)
    ##cv2.namedWindow("Image after Thresholding",cv2.WINDOW_NORMAL)
    # Creating a Named window to display image
    ##cv2.imshow("Image after Thresholding",thresh_image)

    lower = np.array([40, 100, 130])
    higher = np.array([85, 170, 250])

    lower_green = np.array([40, 90, 110])
    higher_green = np.array([95, 200, 250])

    mask = cv2.inRange(frame, lower_green, higher_green)
    mask_hsv = cv2.inRange(hsv, lower, higher)

    mask_sum = cv2.addWeighted(mask, 0.5, mask_hsv, 0.5, 0)

    res = cv2.bitwise_and(frame, frame, mask=mask_hsv)
    #cv2.imshow("res", res)

    gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    #cv2.imshow("gray", gray)

    noise_removal = cv2.bilateralFilter(gray, 9, 75, 75)
    #cv2.namedWindow("Noise Removed Image",cv2.WINDOW_NORMAL)
    # Creating a Named window to display image
    #cv2.imshow("Noise Removed Image",noise_removal)

    # Applying Canny Edge detection
    canny_image = cv2.Canny(mask_hsv, 210, 255)
    #cv2.namedWindow("Image after applying Canny",cv2.WINDOW_NORMAL)
    # Creating a Named window to display image
    #cv2.imshow("Image after applying Canny",canny_image)
    # Display Image
    canny_image = cv2.convertScaleAbs(canny_image)

    noise_removal2 = cv2.blur(canny_image, (5, 5))
    #cv2.namedWindow("Noise Removed Image",cv2.WINDOW_NORMAL)
    # Creating a Named window to display image
    #cv2.imshow("Noise Removed Image2",noise_removal2)

    '''
    indices = np.where(canny_image != [0])
    coordinates = zip(indices[0], indices[1])

    print('coordinates')
    '''

    # dilation to strengthen the edges
    kernel = np.ones((3, 3), np.uint8)
    # Creating the kernel for dilation
    dilated_image = cv2.dilate(noise_removal2, kernel, iterations=1)
    #cv2.namedWindow("Dilation", cv2.WINDOW_NORMAL)
    # Creating a Named window to display image
    #cv2.imshow("Dilation", dilated_image)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    erosion = cv2.erode(dilated_image, kernel, iterations=1)
    #cv2.imshow('erosion', erosion)

    # Displaying Image
    _, contours, h = cv2.findContours(dilated_image, 1, 2)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]
    pt = (180, 3 * frame.shape[0] // 4)
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.05*cv2.arcLength(cnt, True), True)
        M = cv2.moments(cnt)
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        if len(approx) == 6 or len(approx) == 7:
            print(
                "Cube", 'Timestamp: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()), (cx, cy))
            cv2.drawContours(frame, [cnt], -1, (255, 0, 0), 3)
            cv2.putText(frame, 'Cube (%s,%s)'.format(cx, cy), pt,
                        cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 2, [0, 255, 255], 2)
            cv2.circle(frame, (cx, cy), 7, (255, 255, 255), -1)
            file.write("{},{}\n".format(datetime.datetime.now(), "Cube"))
        else:
            print("NOCUBE")

    #cv2.namedWindow("Shape", cv2.WINDOW_NORMAL)
    # cv2.imshow('Shape',frame)

    #corners    = cv2.goodFeaturesToTrack(mask_sum,6,0.06,25)
    #corners    = np.float32(corners)
    # for    item in    corners:
        #x,y    = item[0]
        # cv2.circle(erosion,(x,y),10,255,-1)
    #cv2.namedWindow("Corners", cv2.WINDOW_NORMAL)
    # cv2.imshow("Corners",erosion)
    return numCubes, cubeCentres


def videoProcess(feed=0):
    cap = cv2.VideoCapture(feed)
    while (cap.isOpened()):
        ret, frame = cap.read()
        numCubes, cubeCenters = process(frame)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if cv2.waitKey(int(fps)) & 0xff == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


def imageProcess():
    img = cv2.imread('7.png')
    numCubes, cubeCenters = process(img)
    while True:
        if cv2.waitKey(0) & 0xff == ord('q'):
            break


if __name__ == '__main__':
    logging.debug('Script Start')
    # feed = 'cubevideo2.mp4'
    videoProcess()
    # imageProcess()
    logging.debug('Script End')
