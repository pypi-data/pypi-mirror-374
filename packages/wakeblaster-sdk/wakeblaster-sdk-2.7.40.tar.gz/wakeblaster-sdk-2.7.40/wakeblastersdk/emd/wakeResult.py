import zipfile
import wakeRequest
import datetime

class JobInfo:
  def __init__(self, jobId, clientInformationName, clientInformationVersion, clientInformationUserName, coorSysType, coorSys, calculationDateTime):
    self.jobId = jobId
    self.clientInformationName = clientInformationName
    self.clientInformationVersion = clientInformationVersion
    self.clientInformationUserName = clientInformationUserName
    self.coorSysType = coorSysType
    self.coorSys = coorSys
    self.calculationDateTime = calculationDateTime

class WakeResFile():
  def __init__(self, request, calculationDateTime):
    self.jobInfo = JobInfo(request.JobInfo.jobId, request.JobInfo.clientInformationName, request.JobInfo.clientInformationVersion, request.JobInfo.clientInformationUserName, request.JobInfo.coorSysType, request.JobInfo.coorSys, calculationDateTime)
    self.optimizationModelName = 'WakeBlaster'
    self.optimizationModelVersion = '0.1'
    self.results = {}
    
  def SetResults(self, results):
    self.results = results
              
  def Save(self, path):
    xmlDocument = '''<?xml version="1.0" encoding="UTF-8"?>
<WindPROWakeResult version="1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="WakeResult.xsd">
  <JobInfo>
    <JobId>%s</JobId>
    <CoorSys type="%s">%s</CoorSys>
    <ClientInformation name="%s" version="%s" userName="%s"/>
    <CalculationDateTime>%s</CalculationDateTime>
  </JobInfo>
  <WakeModel name="%s" version="%s"/>
  <Farm>
    <Scenarios file="%s"/>
  </Farm>
  <Turbines>'''%(self.jobInfo.jobId, self.jobInfo.coorSysType, self.jobInfo.coorSys, self.jobInfo.clientInformationName, self.jobInfo.clientInformationVersion, self.jobInfo.clientInformationUserName, self.jobInfo.calculationDateTime.strftime('%Y-%m-%dT%H:%M:%S'), self.optimizationModelName, self.optimizationModelVersion, 'output.csv')
    index = 0
    for wtgId, wtg in self.results.iteritems():
      xmlDocument += '''
    <Turbine id="%s">
      <Parameter col="ws%d" type="windSpeed"/>
    </Turbine>'''%(wtgId, index)
      index += 1
    xmlDocument += '''
  </Turbines>
</WindPROWakeResult>'''
    outputFileLines = []
    index = 0
    numLines = 0
    x = []
    for wtgId, wtg in self.results.iteritems():
      numLines = len(wtg)
      x.append('ws%d'%(index))
      index += 1
    outputFileLines.append(' '.join(x))
    for i in range(numLines):
      x = []
      for wtgId, wtg in self.results.iteritems():
        x.append('%f'%(wtg[i]))
      outputFileLines.append(' '.join(x))
    with zipfile.ZipFile(path, "w") as z:
      z.writestr('WakeResult.xml', xmlDocument)
      z.writestr('output.csv', '\n'.join(outputFileLines))

def SaveWakeResFile(path, request, calculationDateTime, results):
  retVal = WakeResFile(request, calculationDateTime)
  retVal.SetResults(results)
  retVal.Save(path)        

if __name__ == '__main__':
    testWakeReq = wakeRequest.LoadWakeReqFile('..\\xsd\\examples\\request.wakeReq')
    now = datetime.datetime.now() 
    resultArray = []
    for wd in range(360):
      for ws in range(30):
        resultArray.append((ws+.5)*0.9)
    results = {}
    results['wtg0'] = resultArray
    results['wtg1'] = resultArray
    results['wtg2'] = resultArray
    results['wtg3'] = resultArray
    SaveWakeResFile('test.optires', testWakeReq, now, results)
    
