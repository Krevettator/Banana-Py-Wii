import cwiid
import time
from time import strftime
import sys
import os

def print_there(x, y, text):
	sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
	sys.stdout.flush()

def wii_status(x):
	return {
		cwiid.EXT_NONE:'none',
		cwiid.EXT_NUNCHUK:'Nunchuk',
		cwiid.EXT_CLASSIC:'Classic controller',
		cwiid.EXT_BALANCE:'Balance board',
		cwiid.EXT_MOTIONPLUS:'MotionPlus'
		}.get(x)

def callback(mesg_list, time):
	global wii
	global sortie
	global rows
	# print_there(rows-2,1,"[" + strftime("%H:%M") + "] ")
	for mesg in mesg_list:
		if mesg[0] == cwiid.MESG_STATUS:
			print "Statut: Batterie %d Extension " % mesg[1]['battery'], wii_status(mesg)
		elif mesg[0] == cwiid.MESG_BTN:
			print_there(rows-2,2,'Button Report: %.4X' % mesg[1])
			if(mesg[1] & cwiid.BTN_HOME):
				status = True

		elif mesg[0] == cwiid.MESG_ACC:
			# print_there(rows-2,2,'Acc Report: x=%d, y=%d, z=%d' % (mesg[1][cwiid.X], mesg[1][cwiid.Y], mesg[1][cwiid.Z]))
			k = int(mesg[1][cwiid.X] * columns / 250)
			print_there(rows-1,k * "*",(columns-k) * " ")

		elif mesg[0] == cwiid.MESG_IR:
			valid_src = False
			print 'IR Report: ',
			for src in mesg[1]:
				if src:
					valid_src = True
					print src['pos'],

				if not valid_src:
					print 'no sources detected'
				else:
					print

		elif mesg[0] == cwiid.MESG_NUNCHUK:
			print ('Nunchuk Report: btns=%.2X stick=%r ' + \
				   'acc.x=%d acc.y=%d acc.z=%d') % \
				  (mesg[1]['buttons'], mesg[1]['stick'],
				   mesg[1]['acc'][wii.X], mesg[1]['acc'][wii.Y],
				   mesg[1]['acc'][wii.Z])
		elif mesg[0] == cwiid.MESG_CLASSIC:
			print ('Classic Report: btns=%.4X l_stick=%r ' + \
				   'r_stick=%r l=%d r=%d') % \
				  (mesg[1]['buttons'], mesg[1]['l_stick'],
			   mesg[1]['r_stick'], mesg[1]['l'], mesg[1]['r'])
		elif mesg[0] ==  cwiid.MESG_BALANCE:
			print ('Balance Report: right_top=%d right_bottom=%d ' + \
				   'left_top=%d left_bottom=%d') % \
				  (mesg[1]['right_top'], mesg[1]['right_bottom'],
				   mesg[1]['left_top'], mesg[1]['left_bottom'])
		elif mesg[0] == cwiid.MESG_MOTIONPLUS:
			print 'MotionPlus Report: angle_rate=(%d,%d,%d)' % \
				  mesg[1]['angle_rate']
		elif mesg[0] ==  cwiid.MESG_ERROR:
			print "Error message received"
			global wiimote
			wii.close()
			exit(-1)
		else:
			print 'Unknown Report'

# a few settings
button_delay = 0.2
max_try = 3
rows, columns = os.popen('stty size', 'r').read().split()
columns = int(columns)
rows = int(rows)
sortie = False

# connect to wiimote
status = True
n = 0
global wii
while (status):
    status = False
    try:
		# ajouter l'addresse pour accelerer
        wii = cwiid.Wiimote();
    except RuntimeError:
        print "Connexion Wiimote... zut manque  (",n,")"
        status = True
    n = n+1
    if(n >= max_try):
        print "Wiimote introuvable... Au revoir"
        quit()
print "Wiimote connectee ! Youpi!"

# setup callback
wii.mesg_callback = callback

# Enable tracking mode -> buttons
wii.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC
wii.enable(cwiid.FLAG_MESG_IFC)

# Wait
while ( not sortie ):
	n = 0
	for w in range(columns):
		n += 1
		print_there(rows,1,("*" * n))
		time.sleep(.2)
	for w in range(columns):
		n = columns - w
		print_there(rows,1,("*"*n + "_"*w))
		time.sleep(.2)

wii.close()
