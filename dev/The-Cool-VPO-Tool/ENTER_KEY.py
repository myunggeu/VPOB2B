from pynput.keyboard import Key, Controller
import time
import datetime

counter  = 1

keyboard = Controller()
time.sleep(5)

while counter > 0:
	keyboard.press(Key.enter)
	keyboard.release(Key.enter)
	print("Times the enter key has been pressed: ", counter)
	counter += 1
	# get time stamp
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	print("TIMESTAMP: ", st)
	parsed_st = st.split(" ")
	hr_min_sec = parsed_st[1]
	#print (hr_min_sec)
	parsed_hr_min_sec = hr_min_sec.split(":")
	hour = int(parsed_hr_min_sec[0])
	if hour >= 20 or hour < 5: # if it's later than 8 pm and earlier than 6 am
		print("Later Work Hours -- Pressing ENTER key every 2 minutes" )
		print()
		time.sleep(120)

	else: 
		print("Normal Work Hours -- Pressing ENTER key every 7 seconds" )
		print()
		time.sleep(7)


# keyboard.press('a')
# keyboard.release('a')

# time.sleep(5)

# keyboard.press(Key.enter)
# keyboard.release(Key.enter)


# time.sleep(5)

# keyboard.press(Key.cmd)
# keyboard.release(Key.cmd)

