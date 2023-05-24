import cv2





rgb = cv2.imread("rgb.png")
rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
cv2.imwrite("grey.png", rgb)

 

