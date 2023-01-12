############################################################
##### Author: Mark Baas
##### Version: 0.1.0
##### Use case: Do intensive TA on historic candlestick data 
##### 		 	without worrying about exceeding rate limits
############################################################

import requests, sys, os, ast, time, statistics, math
from datetime import datetime, timedelta
from decimal import *

#markets = ['BTCUSDT', 'BTCUSDT', 'MATICUSDT', 'RUNEUSDT', 'ADAUSDT', 'AVAXUSDT', 'YFIUSDT', 'ALGOUSDT']
markets = ['BTCUSDT']
timeframe = "1h"
candles = 1000
look_back = 1
filepath = "/path_to_your_local_data_folder/" + str( timeframe ) + "/03-22/"

def organize_market_data( candle_data, candle_closes, candle_opens, candle_dates, candle_highs, candle_lows, candle_volume ):
	market_data = {}
	market_data['closes'] = candle_closes
	market_data['opens'] = candle_opens
	market_data['highs'] = candle_highs
	market_data['lows'] = candle_lows
	market_data['dates'] = candle_dates
	market_data['volume'] = candle_volume
	return market_data

def get_market_data( market, timeframe, candles, scan_date, look_back ):
	historic_date = ""
	## if look_back is enabled, look for historical candle data, otherwise take the most recent x candles
	if look_back:
		historic_date = "&startTime=" + str( scan_date )
	candle_data, candle_closes, candle_opens, candle_dates, candle_highs, candle_lows, candle_volume = ( [] for i in range( 7 ) )
	x = 0
	url = "https://api.binance.com/api/v1/klines?symbol=" + market + "&interval=" + timeframe + "&limit=" + str( candles ) + str( historic_date )
	candle_data = requests.get( url ).json()
	while x < len( candle_data ):
		candle_closes.append( float( candle_data[x][4] ) )
		candle_opens.append( float( candle_data[x][1] ) )
		candle_highs.append( float( candle_data[x][2] ) )
		candle_lows.append( float(candle_data[x][3] ) )
		candle_dates.append( int( candle_data[x][0] / 1000 ) )
		candle_volume.append( float( candle_data[x][5] ) )
		x+=1
	return organize_market_data( candle_data, candle_closes, candle_opens, candle_dates, candle_highs, candle_lows, candle_volume )

## add your telegram token and group chat ID to have notifications sent upon completion
def send_notification( text ):
	token = "telegram_token"
	chat_id = "telegram_group_chat_id"
	url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + "&parse_mode=markdownv2&text=" + text 
	results = requests.get(url_req)

for market in markets:
	scan_date = 1648704010000
	file_location = filepath + str( market ) + ".txt"
	while scan_date > 1646025610000:
		print("getting data for " + str( market ) )
		if os.path.exists( file_location ):
			f = open( file_location, "r" )
			file_contents = f.read()
			f.close()
			market_data = get_market_data( market, timeframe, candles, scan_date, look_back )
			temp, temp_closes, temp_opens, temp_highs, temp_lows, temp_dates, temp_volume = ( [] for i in range( 7 ) )
			result = {}
			if file_contents:
				old_market_data = ast.literal_eval( file_contents )
				temp_closes += old_market_data['closes']
				temp_opens = old_market_data['opens']
				temp_highs = old_market_data['highs']
				temp_lows = old_market_data['lows']
				temp_dates = old_market_data['dates']
				temp_volume = old_market_data['volume']
			temp_closes += market_data['closes']
			temp_opens += market_data['opens']
			temp_highs += market_data['highs']
			temp_lows += market_data['lows']
			temp_dates += market_data['dates']
			temp_volume += market_data['volume']
			result['closes'] = temp_closes
			result['opens'] = temp_opens
			result['highs'] = temp_highs
			result['lows'] = temp_lows
			result['dates'] = temp_dates
			result['volume'] = temp_volume
			f = open( file_location, "w+" )
			f.write( str( result ) )
			f.close()
			print( "written data for " + str(market) + " from " + str(datetime.fromtimestamp( market_data['dates'][0] ).strftime("%Y-%m-%d %H:%M")) + " until " + str(datetime.fromtimestamp( market_data['dates'][-1] ).strftime("%Y-%m-%d %H:%M")) )
			print( str( market_data['dates'][0] ) + " until " + str( market_data['dates'][-1] ) )
			time.sleep(2)
			if timeframe == "1m":
				scan_date -= 60000000
			elif timeframe == "3m":
				scan_date -= 180000000
			elif timeframe == "5m":
				scan_date -= 300000000
			elif timeframe == "15m":
				scan_date -= 900000000
			elif timeframe == "1h":
				scan_date -= 3600000000
		else:
			print("No file found for " + str( market ) )
			break
	print( "putting things in order..." )
	f = open( file_location, "r" )
	file_contents = f.read()
	f.close()
	final_output = {}
	dates, closes, opens, highs, lows, volume = ( [] for i in range( 6 ) )
	all_data = ast.literal_eval( file_contents )
	zipped = zip( all_data['dates'], all_data['closes'], all_data['opens'], all_data['highs'], all_data['lows'], all_data['volume'] )
	zipped = sorted(zipped)
	for output in zipped:
		dates.append( output[0] )
		closes.append( output[1] )
		opens.append( output[2] )
		highs.append( output[3] )
		lows.append( output[4] )
		volume.append( output[5] )
	final_output['dates'] = dates
	final_output['closes'] = closes
	final_output['opens'] = opens
	final_output['highs'] = highs
	final_output['lows'] = lows
	final_output['volume'] = volume
	f = open( file_location, "w+" )
	f.write( str( final_output ) )
	f.close()
#send_notification( "finished " )















