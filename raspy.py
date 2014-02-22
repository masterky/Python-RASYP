import subprocess
import sys, os
import time
import threading 
import shutil #copy funtion 
from datetime import datetime

# Operating System = Linux

###############################
# To Implement: Gui, Module-Checker, VideoRenamer...
##########################

class _runRenamer(object):


	def __init__(self, source="", destination="", extChecker=None, maxThreads=4, keepDirectoryStructure=False):
		
		self.numFiles = self.countFiles(source)
		self.progress = 0
		self.rename(source=source, destination=destination, extChecker=extChecker, maxThreads=maxThreads, keepDirectoryStructure=keepDirectoryStructure)

	def copy(self, source, destination):
		shutil.copy(source, destination)
		self.progress = self.progress + 1


	def countFiles(self, path):
		command = []
		command.append("find")
		command.append(path)
		command.append("-type")
		command.append("f")

		#files = self.call(command, "bug")

		command2 = []
		command2.append("wc")
		command2.append("-l")
		
		p1 = subprocess.Popen(command, stdout=subprocess.PIPE)
		p2 = subprocess.Popen(command2, stdin=p1.stdout, stdout=subprocess.PIPE)
		p1.wait()
		p1.stdout.close()

		output = p2.communicate()[0]
		return int(output)

	def rename(self, source="", destination="", extChecker=None, maxThreads=4, keepDirectoryStructure=False):
		for _file in os.listdir(source):
			_file = os.path.join(source, _file)

			if os.path.isdir(_file) is True:
				print "analyse: " , _file

				if keepDirectoryStructure:
					self.rename(_file, os.path.join(destination, os.path.basename(_file)), extChecker, maxThreads, keepDirectoryStructure)
				else:
					self.rename(_file, destination, extChecker, maxThreads, keepDirectoryStructure)
			else:
				out_file = os.path.join(destination, os.path.basename(_file))
				
				if extChecker.isJPG(_file):
					jpg = JPGRenamer(_file, destination)
					out_file = jpg.getNewDestination()
				
				elif extChecker.isVideo(_file):
					print "Rename Video ", _file
					video = VideoRenamer(_file, destination)
					out_file = video.getNewDestination()

				else:
					#Copy all Files, which are no audio files
					print "Normal File Copy ", _file , " to ", out_file
				

				currentRunningInstances = 1

				if threading.activeCount() is (maxThreads+currentRunningInstances):
					
					#print "4 Threads are Running, waiting for a Thread to terminate"

					while True:
						if threading.activeCount() < (maxThreads+currentRunningInstances):
							break
						else:
							#print "Active Count: ", threading.activeCount(), " is ", (maxThreads+currentRunningInstances)
							
							time.sleep(0.01)

				#print "A Thread has finished, start a new one"
				print "Progress: ", self.progress, " Files of ", self.numFiles
				t = threading.Thread(target=self.copy, args=(_file, out_file))
				t.daemon = True
				t.start()



class ExtentionChecker(object):

	def __init__(self):
		pass
	def isJPG(self, jpgFilePath):

		if jpgFilePath.lower().endswith(".jpg"):
			return True
		else:
			return False

	def isVideo(self, videoPath):
		if self.isMOV(videoPath) or self.isMTS(videoPath) or self.isM4v(videoPath):
			 return True
		else:
			return False
	def isMOV(self, movFilePath):

		if movFilePath.lower().endswith(".mov"):
			return True
		else:
			return False
	def isMTS(self, mtsFilePath):

		if mtsFilePath.lower().endswith(".mts"):
			return True
		else:
			return False

	def isM4v(self, m4vFilePath):

		if m4vFilePath.lower().endswith(".m4v"):
			return True
		else:
			return False

class VideoRenamer(object):

	def __init__(self, source="", destination=""):
		self.source = source
		self.destination = destination
		pass


	def getNewDestination(self):
		date = self.getDate()
		imageSize = self.getImageSize()
		name = os.path.basename(self.source)[:-4]
		extention = self.source[len(self.source)-4:]
		newBaseName = "Video-" + date + "-" + imageSize + "-" + name + extention
		return os.path.join(self.destination, newBaseName)

	def getDate(self):

		jheadComamnd = []
		jheadComamnd.append("exiftool")#
		sourceSplit = self.source.split(" ")
		for i in range(0, len(sourceSplit)-1):
			if i is 0 and i is (len(sourceSplit)-1):
				jheadComamnd.append("'" + sourceSplit[i] + "'")
			elif i is 0:
				jheadComamnd.append("'" + sourceSplit[i])
			elif i is (len(sourceSplit)-1):
				jheadComamnd.append(sourceSplit[i] + "'")
			else:
				jheadComamnd.append(sourceSplit[i])

		grepCommand = []
		grepCommand.append("grep")
		grepCommand.append("'Media")
		grepCommand.append("Create")
		grepCommand.append("Date'")

		p1 = subprocess.Popen(jheadComamnd, stdout=subprocess.PIPE)
		p2 = subprocess.Popen(grepCommand, stdin=p1.stdout, stdout=subprocess.PIPE)
		p1.wait()
		p1.stdout.close()

		date = None
		try:
			tmpDate = ""
			for datePart in p2.communicate()[0].split("\n")[0].split(":")[1:]:
				tmpDate += datePart.replace(" ", "_")
				tmpDate+= "_"
			date = tmpDate[1:-1]
			pass
		except Exception, e:
			print "JPG-Data Error: ", self.source

		p2.stdout.close()
		if date is not None:
			if date != "" and date != " ":
				return date
			else:
				return None
		else:
			return None
	def getImageSize(self):

		jheadComamnd = []
		jheadComamnd.append("exiftool")
		sourceSplit = self.source.split(" ")
		for i in range(0, len(sourceSplit)-1):
			if i is 0 and i is (len(sourceSplit)-1):
				jheadComamnd.append("'" + sourceSplit[i] + "'")
			elif i is 0:
				jheadComamnd.append("'" + sourceSplit[i])
			elif i is (len(sourceSplit)-1):
				jheadComamnd.append(sourceSplit[i] + "'")
			else:
				jheadComamnd.append(sourceSplit[i])

		grepCommand = []
		grepCommand.append("grep")
		grepCommand.append("'Image")
		grepCommand.append("Size'")
		
		p1 = subprocess.Popen(jheadComamnd, stdout=subprocess.PIPE, shell=False) #### ????????????????????????????WAHHHHHHHHHHHHHHHHHHHHHYYYYYYYYYYYYYYYYYYYYYYYYYYY
		p2 = subprocess.Popen(grepCommand, stdin=p1.stdout, stdout=subprocess.PIPE, shell=False)
		p1.wait()
		p1.stdout.close()

		imageSize = None
		try:
			imageSize = p2.communicate()[0].split("\n")[0].split(":")[1][1:]
			pass
		except Exception, e:
			print "JPG-Data Error: ", self.source

		
		p2.stdout.close()

		return imageSize


	# exiftool Hagel.MOV | grep "Media Create Date"
	# Media Create Date               : 2013:01:22 13:18:02
	# exiftool Hagel.MOV | grep "Image Size"
	# Image Size                      : 1280x720
	# exiftool Hagel.MOV | grep "Media Duration"
	# Media Duration                  : 0:00:40
class JPGRenamer(object):


	def __init__(self, source="", destination=""):
		self.source = source
		self.destination = destination


	def getNewDestination(self):

		newBaseName = ""
		model = self.getModel()
		date = self.getDate()
		exposure = self.getExposureMode()
		jpgExtention = ".jpg"
		if date is not None:
			newBaseName += date
			if model is not None:
				newBaseName += "-" + model
			else:
				newBaseName+="-None"
			if exposure is not None:
				for i in range(0, 100):
					if os.path.exists(os.path.join(self.destination, (newBaseName + "_" + str(i) + jpgExtention)) ) is False:
						newBaseName+= "_" + str(i)
			
		elif model is not None:
			newBaseName = os.path.basename(self.source)[:-4] + "-" + model
		else:
			newBaseName = os.path.basename(self.source)[:-4]

		newBaseName+= jpgExtention

		newPath = os.path.join(self.destination, newBaseName)

		return newPath

	def getDate(self):

		jpgFile = self.source
		jheadComamnd = []
		jheadComamnd.append("jhead")
		jheadComamnd.append(jpgFile)

		grepCommand = []
		grepCommand.append("grep")
		grepCommand.append("Date")
		
		p1 = subprocess.Popen(jheadComamnd, stdout=subprocess.PIPE)
		p2 = subprocess.Popen(grepCommand, stdin=p1.stdout, stdout=subprocess.PIPE)
		p1.wait()
		p1.stdout.close()

		date = None
		try:
			tmpDate = ""
			for datePart in p2.communicate()[0].split("\n")[0].split(":")[1:]:
				tmpDate += datePart.replace(" ", "_")
				tmpDate+= "_"
			date = tmpDate[1:-1]
			pass
		except Exception, e:
			print "JPG-Data Error: ", self.source

		p2.stdout.close()
		if date is not None:
			if date != "" and date != " ":
				return date
			else:
				return None
		else:
			return None

	def getModDate(self):

		jpgFile = self.source
		jheadComamnd = []
		jheadComamnd.append("jhead")
		jheadComamnd.append(jpgFile)

		grepCommand = []
		grepCommand.append("grep")
		grepCommand.append("date")
		
		p1 = subprocess.Popen(jheadComamnd, stdout=subprocess.PIPE)
		p2 = subprocess.Popen(grepCommand, stdin=p1.stdout, stdout=subprocess.PIPE)
		p1.wait()
		p1.stdout.close()

		date = None
		try:
			tmpDate = ""
			for datePart in p2.communicate()[0].split("\n")[0].split(":")[1:]:
				tmpDate += datePart.replace(" ", "_")
				tmpDate+= "_"
			date = tmpDate[1:-1]
			pass
		except Exception, e:
			print "JPG-Data Error: ", self.source

		
		p2.stdout.close()

		return date

	def getExposureMode(self):

		jpgFile = self.source
		jheadComamnd = []
		jheadComamnd.append("jhead")
		jheadComamnd.append(jpgFile)

		grepCommand = []
		grepCommand.append("grep")
		grepCommand.append("\"Exposure Mode\"")
		
		p1 = subprocess.Popen(jheadComamnd, stdout=subprocess.PIPE)
		p2 = subprocess.Popen(grepCommand, stdin=p1.stdout, stdout=subprocess.PIPE)
		p1.wait()
		p1.stdout.close()

		exposure = None
		try:
			exposure = p2.communicate()[0].split("\n")[0].split(":")[1][1:]
			pass
		except Exception, e:
			#print "JPG-Data Error: ", self.source
			pass
		
		p2.stdout.close()

		return exposure

	# Model is None or Model
	def getModel(self):

		jpgFile = self.source
		jheadComamnd = []
		jheadComamnd.append("jhead")
		jheadComamnd.append(jpgFile)

		grepCommand = []
		grepCommand.append("grep")
		grepCommand.append("model")
		
		p1 = subprocess.Popen(jheadComamnd, stdout=subprocess.PIPE)
		p2 = subprocess.Popen(grepCommand, stdin=p1.stdout, stdout=subprocess.PIPE)
		p1.wait()
		p1.stdout.close()

		model = None
		try:
			model = p2.communicate()[0].split("\n")[0].split(":")[1][1:]
			pass
		except Exception, e:
			print "JPG-Data Error: ", self.source

		
		p2.stdout.close()

		return model

		
class RestoreDirectoryStructure(object):
	def __init__(self, _input, output):
		self.restore(_input, output)
	def restore(self, _input, output):
		
		for _file in os.listdir(_input):
			_file = os.path.join(_input, _file)
			if os.path.isdir(_file) is True:
				path = os.path.join(output, os.path.basename(_file))
				print "Make Dir: ", path
				if not os.path.exists(path):
					os.makedirs(path)
				self.restore(_file, path)

def checkInput(self, r_input):
		r_input = r_input.lower() #to lower case
		print r_input
		if (r_input == '') or (r_input == 'yes') or (r_input == "y"):
			return True
		else:
			return False

def start(source="", destination="", keepDirectoryStructure=False):
	if (os.path.exists(source)) is False:
			print "The given path does not exist!, Exit 0"
			sys.exit(0)
	else:
		if os.path.isdir(source) is False:
			print "The given is not a directory!, Exit 0"
			sys.exit(0)

	if (os.path.exists(destination)) is False:
		print "The given output-path does not exist!"
		if os.path.isdir(destination) is False:
			print ""
			
			_input= raw_input("Do you want to create it?[yes]")
			if self.checkInput(_input) is True:
				os.makedirs(destination)
			else:
				print "Exit 0"
				sys.exit(0)
	print "Renamer Ready to Run, Directory check complete..."
	if keepDirectoryStructure:
		print "Now Restoring Directory Structure..."
		r = RestoreDirectoryStructure(source, destination)

	r = _runRenamer(source=source, destination=destination, extChecker=ExtentionChecker(), maxThreads=4, keepDirectoryStructure=keepDirectoryStructure)




if len(sys.argv) == 3:
	start(source=sys.argv[1], destination=sys.argv[2], keepDirectoryStructure=False)
else:
	print 
	print "Please provide a Source and a Destination directory!"
	print "Execute like: "
	print "python Decoder.py /home/user/Music/ /home/user/Decoded_Music/"
	print
	print
	print "Programm will terminate"
