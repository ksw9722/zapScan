import requests
import time
import argparse
import os


parser = argparse.ArgumentParser()

parser.add_argument("-u", type=str, required=True, help="scan url",metavar='[scan url]')
args = parser.parse_args()
scanUrl = args.u

headers = {
  'Accept': 'application/json',
  'X-ZAP-API-Key': 'kswtest-zap'
}

def healthCheck():
  try:
    requests.get('http://localhost:8081')
    return True
  except: 
    return False

def spiderUntilFinished(url):
  parameter = {'url':url,'scanPolicyName':'mySimpleScanner'}
  #SPIDER
  r = requests.get('http://localhost:8081/JSON/spider/action/scan/', params=parameter, headers = headers)
  spiderId = r.json()['scan']

  while True:
    r = requests.get('http://localhost:8081/JSON/spider/view/status/?scanId=%s'%spiderId, params={
    }, headers = headers)

    spiderResult = r.json()['status']
    time.sleep(0.5)
    if spiderResult=='100':
      break

def scanUntilFinished(url):
  parameter = {'url':url,'scanPolicyName':'mySimpleScanner'}
  #SPIDER
  r = requests.get('http://localhost:8081/JSON/ascan/action/scan/', params=parameter, headers = headers)
  scanId = r.json()['scan']

  while True:
    r = requests.get('http://localhost:8081/JSON/ascan/view/status/?scanId=%s'%scanId, params={
    }, headers = headers)

    scanResult = r.json()['status']
    time.sleep(0.5)
    if scanResult=='100':
      return scanId

def getScanResult(scanId):
  #get scan alert
  r = requests.get('http://localhost:8081/JSON/ascan/view/alertsIds/', params={
  'scanId': scanId
  }, headers = headers)
  alertIds = r.json()['alertsIds']
  scanResult = []
  if len(alertIds)!=0:
    
    for alert in alertIds:
      #get Detail alert  
      r = requests.get('http://localhost:8081/JSON/alert/view/alert/?id=%s'%alert, params={
      }, headers = headers)

      alert = r.json()['alert']
      scanDetail = {}
      scanDetail['name'] = alert['name']
      scanDetail['param'] = alert['param']
      scanDetail['attack'] = alert['attack']
      scanDetail['inputVector'] = alert['inputVector']
      scanDetail['url'] = alert['url']
      #print(scanDetail)
      scanResult.append(scanDetail)
  
  return scanResult

def runScan(url):
  if healthCheck()==False:
    os.system("zap.sh --daemon &")
    time.sleep(15)
  
  spiderUntilFinished(url)
  scanId = scanUntilFinished(url)
  result = getScanResult(scanId)
  print(result)


runScan(scanUrl)






