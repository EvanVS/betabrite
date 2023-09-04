import time, os, math, json, requests, threading, itertools, serial, colorama
from datetime import datetime
from flask import Flask, jsonify, request
from flask import Response
import schedule
from bs4 import BeautifulSoup

colorama.init(autoreset=True)

clear = '\33[0m'

black = '\33[30m'
gray = '\33[90m'
red = '\33[91m'
green = '\33[92m'
yellow = '\33[93m'
blue = '\33[94m'
pink = '\33[95m'
cyan = '\33[96m'
white = '\33[97m'

# These are the codes that can be used in commands to quickly reference hex commands.
textcodes = [{"f":"<FONT_5STD>","r":"\x1a\x31"},{"f":"<FONT_5STROKE>","r":"\x1a\x32"},{"f":"<FONT_7SLIM>","r":"\x1a\x33"},{"f":"<FONT_7STROKE>","r":"\x1a\x34"},{"f":"<FONT_7SLIMFANCY>","r":"\x1a\x35"},{"f":"<FONT_7STROKEFANCY>","r":"\x1a\x36"},{"f":"<FONT_7SHADOW>","r":"\x1a\x37"},{"f":"<FONT_7WIDESTROKEFANCY>","r":"\x1a\x38"},{"f":"<FONT_7WIDESTROKE>","r":"\x1a\x39"},{"f":"<FONT_7SHADOWFANCY>","r":"\x1a\x3a"},{"f":"<FONT_5WIDE>","r":"\x1a\x3b"},{"f":"<FONT_7WIDE>","r":"\x1a\x3c"},{"f":"<FONT_7WIDEFANCY>","r":"\x1a\x3d"},{"f":"<FONT_5WIDESTROKE>","r":"\x1a\x3e"},{"f":"<COLOR_RED>","r":"\x1c\x31"},{"f":"<COLOR_GREEN>","r":"\x1c\x32"},{"f":"<COLOR_AMBER>","r":"\x1c\x33"},{"f":"<COLOR_DIMRED>","r":"\x1c\x34"},{"f":"<COLOR_DIMGREEN>","r":"\x1c\x35"},{"f":"<COLOR_BROWN>","r":"\x1c\x36"},{"f":"<COLOR_ORANGE>","r":"\x1c\x37"},{"f":"<COLOR_YELLOW>","r":"\x1c\x38"},{"f":"<COLOR_RAINBOW1>","r":"\x1c\x39"},{"f":"<COLOR_RAINBOW2>","r":"\x1c\x41"},{"f":"<COLOR_MIX>","r":"\x1c\x42"},{"f":"<COLOR_AUTO>","r":"\x1c\x43"},{"f":"<SPEED_1>","r":"\x15"},{"f":"<SPEED_2>","r":"\x16"},{"f":"<SPEED_3>","r":"\x17"},{"f":"<SPEED_4>","r":"\x18"},{"f":"<SPEED_5>","r":"\x19"},{"f":"<TEXT_NOHOLD>","r":"\x09"},{"f":"<TEXT_FIXLEFT>","r":"\x1e\x31"},{"f":"<TEXT_CALLSTRING>","r":"\x10"},{"f":"<TEXT_CALLSMALLDOTS>","r":"\x14"},{"f":"<TEXT_CLOCK>","r":"\x13"},{"f":"<TEXT_NEWLINE>","r":"\x0d"},{"f":"<TEXT_FLASHON>","r":"\x071"},{"f":"<TEXT_FLASHOFF>","r":"\x070"},{"f":"<CHR_BLOCK>","r":"\x7f"},{"f":"<MODE_ROTATE>","r":"a"},{"f":"<MODE_HOLD>","r":"b"},{"f":"<MODE_FLASH>","r":"c"},{"f":"<MODE_ROLLUP>","r":"e"},{"f":"<MODE_ROLLDOWN>","r":"f"},{"f":"<MODE_ROLLLEFT>","r":"g"},{"f":"<MODE_ROLLRIGHT>","r":"h"},{"f":"<MODE_WIPEUP>","r":"i"},{"f":"<MODE_WIPEDOWN>","r":"j"},{"f":"<MODE_WIPELEFT>","r":"k"},{"f":"<MODE_WIPERIGHT>","r":"l"},{"f":"<MODE_SCROLL>","r":"m"},{"f":"<MODE_AUTO>","r":"o"},{"f":"<MODE_ROTATECOMPRESSED>","r":"t"},{"f":"<MODE_TWINKLE>","r":"n0"},{"f":"<MODE_SPARKLE>","r":"n1"},{"f":"<MODE_SNOW>","r":"n2"},{"f":"<MODE_INTERLOCK>","r":"n3"},{"f":"<MODE_SPRAY>","r":"n6"},{"f":"<MODE_STARBURST>","r":"n7"},{"f":"<MODE_WELCOME>","r":"n8"},{"f":"<MODE_SLOTMACHINE>","r":"n9"},{"f":"<MODE_NEWSFLASH>","r":"nA"},{"f":"<MODE_TRUMPET>","r":"nB"},{"f":"<MODE_THANKYOU>","r":"nS"},{"f":"<MODE_NOSMOKING>","r":"nU"},{"f":"<MODE_DRINKDRIVE>","r":"nV"},{"f":"<MODE_FISH>","r":"nW"},{"f":"<MODE_FIREWORKS>","r":"nX"},{"f":"<MODE_BALLOONS>","r":"nY"},{"f":"<MODE_BOMB>","r":"nZ"},{"f":"<SND_LONGBEEP>","r":"\x30"},{"f":"<SND_3BEEPS>","r":"\x31"},{"f":"<ALPHA_PREAMBLE>","r":"\x00"},{"f":"<ALPHA_TYPEALL>","r":"Z00"},{"f":"<ALPHA_SOH>","r":"\x01"},{"f":"<ALPHA_STX>","r":"\x02"},{"f":"<ALPHA_ETX>","r":"\x03"},{"f":"<ALPHA_EOT>","r":"\x04"},{"f":"<ALPHA_ESC>","r":"\x1b"},{"f":"<ALPHA_CR>","r":"\x0d"},{"f":"<ALPHA_LF>","r":"\x0a"},{"f":"<DOTS_MONO>","r":"1000"},{"f":"<DOTS_3COLOR>","r":"2000"},{"f":"<DOTS_8COLOR>","r":"4000"},{"f":"<DOTC_BLACK>","r":"0"},{"f":"<DOTC_RED>","r":"1"},{"f":"<DOTC_GREEN>","r":"2"},{"f":"<DOTC_AMBER>","r":"3"},{"f":"<DOTC_DIMRED>","r":"4"},{"f":"<DOTC_DIMGREEN>","r":"5"},{"f":"<DOTC_BROWN>","r":"6"},{"f":"<DOTC_ORANGE>","r":"7"},{"f":"<DOTC_YELLOW>","r":"8"}]


# --------------- CONFIGURATION ---------------

NightMode = False
ComTypeIP = True
ComPort = 'COM0'
ComAddr = "socket://192.168.1.255:1234/?logging=debug"
OffTime = "21:30"
OnTime = "06:30"
ClockSyncTime = "04:00"

# --------------- CONFIGURATION ---------------

if ComTypeIP == True:
	comm = serial.serial_for_url(ComAddr)
else:
	comm = serial.Serial(ComPort, 9600 , writeTimeout = 0)

IcecastStationStatus = ['0  -  NO ICECAST DATA']
EASmsgResetKill = False
EASmsgResetActive = False
global wx_temperature
temperature = "N/A"

def command(data, msg = False, verb = False):
	for term in textcodes:
		data = data.replace(term["f"],term["r"])
	packet = ("\x00\x00\x00\x00\x00E\x01Z00\x62\x02"+data+"\x04")
	if verb:
		print("DATA:" + data)
	if msg:
		print(msg)
	comm.write(packet.encode("UTF-8"))
	time.sleep(.1)

def DateTimeSet():
	now = datetime.now()

	# Course Set Time
	time_24hrs = now.strftime("%H%M")
	command(f"E {time_24hrs}", "Course Time Set")

	# Set Date
	date = now.strftime("%m%d%y")
	command(f"E;{date}", "Date Set")

	# Set Day
	date_of_week = now.strftime("%w")
	date_of_week = int(date_of_week)
	date_of_week + 1
	command(f"E&{str(date_of_week)}", "Weekday Set")

DateTimeSet()

# CLEAR MEMORY
command("E$", "Memory Cleared")

# Define Files & Variables
command("E$AAU2000FF005BL00050000aBL00100000bBL00100000cBL00100000dBL00100000eBL00100000fBL00100000gBL00100000hBL00100000iBL00100000jBL00100000kBL00100000lBL00100000mBL00100000nBL00100000oBL00100000pBL00100000qBL00100000rBL00100000sBL00100000tBL00100000uBL00100000vBL00100000wBL00100000xBL30000000yBL08000000zBL30000000", "Defined Files & Variables")
# Example: .BL00100000 (File "." and size "10")

# DefaultDisplay = "AA\x1b e\x1c\x32Operational \x0d Defcon Level \x105 \x0d \x13 \x0d Indoor: \x10a \x0d Outdoor: \x10b \x0d Baro: \x10f \x1b t \x10y \x1b t \x10x"
# DefaultDisplay = "AA\x1b e\x1c\x32Operational \x0d \x13 \x0d Indoor: \x10aF"
# CLOCK => TEMPERATURES => SERVER STATS => 
#DefaultDisplay = "AA<ALPHA_ESC> <MODE_HOLD><COLOR_GREEN><TEXT_CLOCK>"
#DefaultDisplay = "AA<ALPHA_ESC> <MODE_HOLD><COLOR_GREEN><TEXT_CLOCK> <COLOR_RED>-<COLOR_GREEN> \x10bF <ALPHA_CR> <ALPHA_ESC> <MODE_ROTATECOMPRESSED> KJ7BRE Communications Center"


DefaultDisplay = "AA<ALPHA_ESC> <MODE_HOLD><COLOR_GREEN><TEXT_CLOCK> <COLOR_RED>-<COLOR_GREEN> \x10b "

# DefaultDisplay = "AA<ALPHA_ESC> <MODE_ROTATECOMPRESSED><COLOR_GREEN>DEEZ NUTS ON SALE $9.99"
#DefaultDisplay = "AA<ALPHA_ESC> <MODE_ROTATECOMPRESSED><COLOR_GREEN><TEXT_CLOCK> <COLOR_RED>-<COLOR_GREEN> Outdoor: \x10bF <COLOR_RED>-<COLOR_GREEN> KJ7BRE Communications Center"
command(DefaultDisplay, "Default Display File Text Write")

command(f"Gx\x1c\x31NO ICECAST DATA", "Default IceCast Message Defined")

# /x49/x44070502220/x0D02020/x0D02220/x0D00000/x0D00000/x0D00000/x0D00000/x0D
# 07 05



# ----------------------------------------------------------------------------------------------------


app = Flask(__name__)

@app.route('/temperature')
def temperature():
	print('Temperature API Request')
	return('{"temperature":"' + temperature + '"}')

@app.route('/test_warning')
def test_warning():
	command("A0\x1b b\x1c\x31\x071\x15SYSTEM WARNING\x070\x0d\x18\x1b t TEST MESSAGE")
	command("E(\x31")

	print('Alert Sent Successfully')
	return('Alert Sent Successfully')

@app.route('/test_advisory')
def test_advisory():
	command("A0\x1b b\x1c\x38\x071\x15SYS ADVISORY\x070\x0d\x18\x1b t TEST MESSAGE")
	command("E(\x31")

	print('Alert Sent Successfully')
	return('Alert Sent Successfully')

@app.route('/total_system_failure')
def total_system_failure():
	command("A0\x1b b\x1c\x31\x071\x15SYSTEM WARNING\x070\x0d\x18\x1b t[SERVER ATLANTIS] - NO RESPONSE -  PRIMARY INFANSTRUCTURE FAILURE")
	command("E(\x31")
	
	print('Alert Sent Successfully')
	return('Alert Sent Successfully')

@app.route('/emergency/fire')
def fire():
	command("A0\x1b b\x1c\x31\x071\x15FIRE EVACUATE")
	
	print('Alert Sent Successfully')
	return('Alert Sent Successfully')

@app.route('/offline')
def offline_ack():
	command("A0\x1b e\x1c\x31\x15- OFFLINE -\x0d\x1c\x32ACKNOWLEDGED")
	command("E(\x31")
	
	print('Alert Sent Successfully')
	return('Alert Sent Successfully')

@app.route('/clear')
def clear():
	command("A0")

	print('Alert Cleared Successfully')
	return('Alert Cleared Successfully')

@app.route('/off')
def off():
	command("A0\x1b b\x1c\x31\x1a\x31\x15.                   \x0d\x1c\x32.                   ")
	
	print('Display Blank/Off')
	return('Display Blank/Off')

@app.route('/json', methods=['GET', 'POST'])
def grafana():
	content = request.json
	
	message = content['title']
	message = message.replace("[Alerting] ", "")
	
	if content['state'] == "ok":
		command(DefaultDisplay)
	else:
		command("AA\x1b b\x1c\x31\x071\x15SYSTEM WARNING\x070\x0d\x18\x1b t"+message)
		command("E(\x31")
		
	print(content['title'] + "\n" + content['state'])
	
	print('Alert Sent Successfully')
	return('Success')

@app.route('/schedule/off')
def schedule_off():
	
	schedule.clear('night/day')
	
	print('Display Schedule Off')
	return('Display Schedule Off')

@app.route('/schedule/on')
def schedule_on():
	
	schedule.every().day.at("23:30").do(off).tag('night/day')
	schedule.every().day.at("07:00").do(clear).tag('night/day')
	
	print('Display Schedule On')
	return('Display Schedule On')

@app.route('/eas/off')
def eas_off():
	
	command(DefaultDisplay)
	
	print('EAS Message Display Off')
	return('EAS Message Display Off')

@app.route('/eas/on', methods=['GET', 'POST'])
def eas_on():
	print(request)
	if request.method == 'POST':
		requestdata = request.get_json(force=True)
		msg = requestdata['msg']
		print(msg)
		if msg != None:
			command("AA\x1c\x31\x1b t" + str(msg))
			threading.Thread(target=eas_msg_reset_timer).start()
			print('EAS Message Display On')
			return('EAS Message Display On')
		else:
			print('No EAS Message Data')
			return('No EAS Message Data')

threading.Thread(target=app.run,kwargs={'host': '192.168.1.xxx', 'port': 8080}).start()

def get_weather():
	global temperature
	try:
		# API endpoint and parameters
		url = "https://api.openweathermap.org/data/2.5/weather"
		params = {
			"q": "Portland,Oregon",
			"units": "imperial", # use imperial units for Fahrenheit
			"appid": "xxxxxxxx" # replace with your OpenWeatherMap API key
		}

		# send API request and parse response
		response = requests.get(url, params=params)
		if response.status_code == 200:
			data = response.json()

			# extract temperature from response data
			wx_temperature = round(data["main"]["temp"], 1)
			print(f"Current temperature in Milwaukie, Oregon: {wx_temperature} F")
			temperature = f"{wx_temperature}F"
			command(f"Gb{wx_temperature}F")
			return(str(wx_temperature))
		else:
			temperature = "N/A"
			command(f"GbN/A")
			return("N/A")
			
	except requests.exceptions.ConnectionError:
		temperature = "N/A"
		command(f"GbN/A")
		return("N/A")

def river_level():
	# Set the API endpoint and parameters
	url = 'https://waterservices.usgs.gov/nwis/iv/'
	params = {
		'format': 'json',
		'sites': '14211720', # USGS site number for Willamette River at Portland, OR
		'parameterCd': '00065' # USGS parameter code for gauge height in feet
	}

	# Send the API request and get the response
	response = requests.get(url, params=params)

	# Check if the request was successful
	if response.status_code == 200:
		# Parse the JSON data from the response
		data = response.json()
		# Extract the current water level from the data
		current_level = data['value']['timeSeries'][0]['values'][0]['value'][0]['value']
		time_observed = data['value']['timeSeries'][0]['values'][0]['value'][0]['dateTime']
		# Print the current water level
		print(f"At {time_observed} the water level of the Willamette River at Portland, OR is {current_level} feet.")
		command(f"Gr{current_level}ft")
	else:
		print("Error: Failed to get the water level data.")
		command("GrN/A")

def update_timer():
	while True:
		threading.Thread(target=get_weather).start()
		# time.sleep(3)
		# threading.Thread(target=get_wx_telemetry).start()
		# time.sleep(3)
		# threading.Thread(target=get_now_playing).start()
		time.sleep(500) # 15 Min

def update_timer_long():
	while True:
		threading.Thread(target=get_usa_flag).start()
		threading.Thread(target=get_defcon_level).start()
		threading.Thread(target=river_level).start()
		time.sleep(3600) # 1 Hour

def schedule_timer():
	while True:
		schedule.run_pending()
		time.sleep(1)

def eas_msg_reset_timer():
	global EASmsgResetActive
	global EASmsgResetKill
	HasBeenKilled = False
	if EASmsgResetActive == True:
		EASmsgResetKill = True
		time.sleep(3)
		EASmsgResetKill = False
	EASmsgResetActive = True
	for _ in range(120):
		time.sleep(1)
		if EASmsgResetKill == True:
			EASmsgResetKill = False
			print("Killed Existing EAS MSG Timer")
			HasBeenKilled = True
	if HasBeenKilled == True:
		EASmsgResetActive = False
		return
	else:
		eas_off()
		EASmsgResetActive = False

def fine_time_set_timer():
	TimeSet = False
	while TimeSet == False:
		if time.localtime().tm_sec == 0:
			now = datetime.now()
			time_24hrs = now.strftime("%H%M")
			command(f"E {time_24hrs}")
			TimeSet = True
			print("Fine Time Set")
	print("Fine Time Set Timer Loop Exited")


def fine_time_set_timer_thread():
	threading.Thread(target=fine_time_set_timer).start()

if NightMode:
	schedule.every().day.at(OffTime).do(off).tag('night/day')
	schedule.every().day.at(OnTime).do(clear).tag('night/day')
# schedule.every().day.at(ClockSyncTime).do(fine_time_set_timer_thread)
schedule.every().day.at("00:00").do(get_usa_flag)


threading.Thread(target=update_timer).start()
threading.Thread(target=update_timer_long).start()
threading.Thread(target=schedule_timer).start()
threading.Thread(target=fine_time_set_timer).start()
