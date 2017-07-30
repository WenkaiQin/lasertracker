import cv2

cap = cv2.VideoCapture(0)
readable, im = cap.read()

if readable:
	print 'readable'
else:
	print 'not readable'

while True:
	readable, im = cap.read()
	cv2.imshow('frame', im)
	key = cv2.waitKey(10)
	
	if key == ord('s'):
		fname = raw_input(' What would you like to save your image as?: ')+'.png'
		if fname == '.png':
			fname = 'image.png'
		path = 'images/'+fname
		cv2.imwrite(path, im)
		print ' Frame saved as '+path+'.'

	if key == ord('q'):
		print " Exiting..."
		break