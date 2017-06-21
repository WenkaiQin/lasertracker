import cv2
import numpy as np

thresh_min = np.array([30,70,30])
thresh_max = np.array([70,255,255])

LIVEFEED = True;
BUFFER_SIZE = 5;

def thresh_mask(src, lowerb, upperb):

	im_h = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(im_h, lowerb, upperb)
	return mask


def find_max_index(cnt):
	max_num = 0
	max_i = -1

	for i in range(len(cnt)):
		cnt_num=len(cnt[i])
		if cnt_num > max_num:
			max_num = cnt_num
			max_i = i

	return max_i


def main():

	cap = cv2.VideoCapture(0)

	while True:

		# Capture image.
		if LIVEFEED:
			im = cap.read()[1]
		else:
			im = cv2.imread("ocharef.jpg")

		# Make mask of desired threshold.
		mask1 = thresh_mask(im, thresh_min, thresh_max)
		mask2 = np.copy(mask1)

		# Find largest contour.
		cnt = cv2.findContours(mask2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
		n = find_max_index(cnt)

		# If there is a largest contour...
		if n != -1:
			# Grab it.
			max_cnt = cnt[n]
			# Find and draw its largest hull.
			hull = cv2.convexHull(max_cnt)
			mask2[:] = 0
			cv2.drawContours(mask2, [hull], 0, (255), -1)
			cv2.drawContours(im, [hull], 0, (0,200,0), 3)
			# Find its moment and use it to calculate the region center.
			M1 = cv2.moments(max_cnt)
			cx, cy = int(M1["m10"]/M1["m00"]), int(M1["m01"]/M1["m00"])

		else:
			cx, cy = im.shape[:2];

		# Use Canny edge detection on the mask.
		mask = cv2.bitwise_and(mask1, mask1, mask=mask2)
		mask = cv2.Canny(mask2, 100, 200)

		# Draw the center of the region of interest.
		cv2.circle(im, (cx,cy), 5, (0,0,255), -1)

        # Show the results.
		cv2.imshow("Frame", im)
		cv2.imshow("Mask", mask)

		if cv2.waitKey(10) == 27:
			print "Exiting..."
			if LIVEFEED:
				cap.release()
			cv2.destroyAllWindows()
			break


if __name__ == '__main__':
	main()