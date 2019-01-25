import time
import dispatcher

filepath = "../../AutexysData/Nathaniel/JoeyData/schedules/run_long_bg.json" # Specifies schedule file
totalTime = 3*60*60 # 3 hours --> seconds
delayTime = 5*60  # 5 minutes --> seconds

startTime = time.time()
dispatchTime = startTime
while time.time() < startTime + totalTime:
	dispatcher.dispatch(schedule_file_path=filepath)
	print("Delaying " + str(delayTime) + " seconds")
	dispatchTime = time.time() - dispatchTime
	time.sleep(delayTime - dispatchTime)
	dispatchTime = time.time()
