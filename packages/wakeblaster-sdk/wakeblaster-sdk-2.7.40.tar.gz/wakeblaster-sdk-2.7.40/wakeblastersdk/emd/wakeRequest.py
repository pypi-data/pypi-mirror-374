# -*- coding: utf-8 -*-

import zipfile
from xml.dom.minidom import parseString


def ReadAttribute(node, key, default=None):
    if key in node.attributes.keys():
        return node.attributes[key].value
    return default


class JobInfo:
    def __init__(self, node):
        self.jobId = None
        self.clientInformationName = None
        self.clientInformationVersion = None
        self.clientInformationUserName = None
        self.coorSysType = None
        self.coorSys = None
        self.Parse(node)

    def Parse(self, node):
        jobIdNode = node.getElementsByTagName('JobId')[0]
        self.jobId = jobIdNode.firstChild.nodeValue
        clientInformationNode = node.getElementsByTagName('ClientInformation')[0]
        self.clientInformationName = ReadAttribute(clientInformationNode, 'name')
        self.clientInformationVersion = ReadAttribute(clientInformationNode, 'version')
        self.clientInformationUserName = ReadAttribute(clientInformationNode, 'userName')
        coorSysNode = node.getElementsByTagName('CoorSys')[0]
        self.coorSysType = ReadAttribute(coorSysNode, 'type')
        self.coorSys = coorSysNode.firstChild.nodeValue


class Farm:
    def __init__(self, request, node):
        # Public
        self.rsfData = None
        self.turbulencesData = None

        # Private
        self.request = request
        self.scenarioFile = None
        self.rsfFile = None
        self.turbulencesFile = None
        self.Parse(node)

    def Parse(self, node):
        try:
            resourceNode = node.getElementsByTagName('Resource')[0]
            self.rsfFile = ReadAttribute(resourceNode, 'file')
        except:
            self.rsfFile = None
        scenariosNode = node.getElementsByTagName('Scenarios')[0]
        self.scenarioFile = ReadAttribute(scenariosNode, 'file')
        turbulence_nodes = node.getElementsByTagName('Turbulences')
        if turbulence_nodes:
            turbulencesNode = turbulence_nodes[0]
            self.turbulencesFile = ReadAttribute(turbulencesNode, 'file')
        else:
            self.turbulencesFile = None

    def ProcessFile(self, filename, fileContent):
        if filename == self.rsfFile:
            self.rsfData = fileContent
        if filename == self.turbulencesFile:
            self.turbulencesData = fileContent


class Mode:
    def __init__(self, turbineType, node):
        # Public
        self.id = None
        self.ctCurve = None
        self.airDensity = None
        self.stationaryThrustCoefficient = None

        # Private
        self.turbineType = turbineType
        self.ctFile = None
        self.Parse(node)

    def Parse(self, node):
        self.id = ReadAttribute(node, 'id')
        self.airDensity = float(ReadAttribute(node, 'airDensity', '1.225'))
        self.stationaryThrustCoefficient = float(ReadAttribute(node, 'stationaryThrustCoefficient', '0.05'))
        self.ctFile = ReadAttribute(node, 'ctFile')
        self.ctCurve = []

    def ProcessFile(self, filename, fileContent):
        if filename == self.ctFile:
            lines = fileContent.split('\n')
            headerLine = True
            for line in lines:
                line = line.strip()
                if headerLine:
                    headerLine = False
                else:
                    elements = line.split(' ')
                    if len(elements) == 2:
                        self.ctCurve.append([float(x) for x in elements])


class TurbineType:
    def __init__(self, request, node):
        # Public
        self.id = None
        self.HubHeight = None
        self.RotorDiameter = None
        self.CutIn = None
        self.CutOut = None
        self.Modes = {}

        # Private
        self.defaultMode = None
        self.request = request
        self.Parse(node)

    def GetCTCurve(self, modeId=None):
        if modeId is None:
            modeId = self.defaultMode
        return self.Modes[modeId].ctCurve

    def Parse(self, node):
        self.id = ReadAttribute(node, 'id')
        hubHeightNode = node.getElementsByTagName('HubHeight')[0]
        self.HubHeight = float(hubHeightNode.firstChild.nodeValue)
        rotorDiameterNode = node.getElementsByTagName('RotorDiameter')[0]
        self.RotorDiameter = float(rotorDiameterNode.firstChild.nodeValue)
        cutInNode = node.getElementsByTagName('CutIn')[0]
        self.CutIn = float(cutInNode.firstChild.nodeValue)
        cutOutNode = node.getElementsByTagName('CutOut')[0]
        self.CutOut = float(cutOutNode.firstChild.nodeValue)
        modesNode = node.getElementsByTagName('Modes')[0]
        self.defaultMode = ReadAttribute(modesNode, 'defaultMode')
        for modeNode in modesNode.getElementsByTagName('Mode'):
            mode = Mode(self, modeNode)
            self.Modes[mode.id] = mode

    def ProcessFile(self, filename, fileContent):
        for modeId, mode in self.Modes.items():
            mode.ProcessFile(filename, fileContent)


class Parameter:
    def __init__(self, request, node):
        # Public
        self.type = None
        self.data = []

        # Private
        self.col = None
        self.index = None
        self.Parse(node)

    def Parse(self, node):
        self.col = ReadAttribute(node, 'col')
        self.type = ReadAttribute(node, 'type')

    def ProcessHeader(self, headerElements):
        self.index = headerElements.index(self.col)

    def ProcessLine(self, lineElements):
        if self.index < len(lineElements):
            self.data.append(lineElements[self.index])


class Instance:
    def __init__(self, request, node):
        self.id = None
        self.Parameters = []
        self.x = None
        self.y = None
        self.z = None

        # Private
        self.request = request
        self.scenarioFile = request.Farm.scenarioFile
        self.Parse(node)

    def Parse(self, node):
        self.id = ReadAttribute(node, 'id')
        self.x = float(ReadAttribute(node, 'x'))
        self.y = float(ReadAttribute(node, 'y'))
        self.z = float(ReadAttribute(node, 'z'))
        for parameterNode in node.getElementsByTagName('Parameter'):
            self.Parameters.append(Parameter(self, parameterNode))

    def ProcessFile(self, filename, fileContent):
        if filename == self.scenarioFile:
            lines = fileContent.split('\n')
            headerLine = True
            for line in lines:
                line = line.strip()
                if line == '':
                    continue
                elements = line.split(' ')
                if headerLine:
                    for parameter in self.Parameters:
                        parameter.ProcessHeader(elements)
                    headerLine = False
                else:
                    for parameter in self.Parameters:
                        parameter.ProcessLine(elements)


class Turbine(Instance):
    def __init__(self, request, node):
        self.Type = None
        super().__init__(request, node)

    def GetCTCurve(self, modeId=None):
        return self.Type.GetCTCurve(modeId)

    def Parse(self, node):
        super().Parse(node)

        typeId = ReadAttribute(node, 'type')
        self.Type = self.request.TurbineTypes[typeId]


class Reference(Instance):
    def __init__(self, request, node):
        self.height = None
        super().__init__(request, node)

    def Parse(self, node):
        super().Parse(node)
        self.height = float(ReadAttribute(node, 'height'))


class CalculationConfiguration:
    def __init__(self, name, filename):
        self.name = name
        self.contents = None
        self.filename = filename

    def ProcessFile(self, filename, fileContents):
        if filename == self.filename:
            self.contents = fileContents


class Configuration:
    def __init__(self):
        self._settings = {}

    def Parse(self, node):
        for setting_node in node.getElementsByTagName('Setting'):
            self._settings[ReadAttribute(setting_node, 'name')] = ReadAttribute(setting_node, 'value')

    @property
    def is_time_varying(self):
        return self._settings.get('ScenariosMode') == 'TimeVarying'


class WakeReqFile():
    def __init__(self):
        self.path = ''
        self.xmlDom = None
        self.JobInfo = None
        self.Farm = None
        self.CalculationConfigurations = []
        self.Configuration = {}
        self.TurbineTypes = {}
        self.Turbines = []
        self.Reference = None

    def Load(self,path):
        self.path = path
        with zipfile.ZipFile(self.path, "r") as z:
            xmlData = z.read('WakeRequest.xml')
            self.xmlDom = parseString(xmlData)
            self.Parse(self.xmlDom)
            for name in z.namelist():
                fileContent = z.read(name).decode('utf8')
                self.Reference.ProcessFile(name, fileContent)
                for turbine in self.Turbines:
                    turbine.ProcessFile(name, fileContent)
                for turbineId, turbineType in self.TurbineTypes.items():
                    turbineType.ProcessFile(name, fileContent)
                self.Farm.ProcessFile(name, fileContent)
                for calculation_configuration in self.CalculationConfigurations:
                    calculation_configuration.ProcessFile(name, fileContent)

    def Parse(self, zipFile):
        mainNode = self.xmlDom.getElementsByTagName('WakeRequest')[0]

        self.JobInfo = JobInfo(mainNode.getElementsByTagName('JobInfo')[0])
        self.Farm = Farm(self, mainNode.getElementsByTagName('Farm')[0])

        referenceNode = mainNode.getElementsByTagName('Reference')[0]
        self.Reference = Reference(self, referenceNode)

        turbineTypesNode = mainNode.getElementsByTagName('TurbineTypes')[0]
        for turbineTypeNode in turbineTypesNode.getElementsByTagName('TurbineType'):
            turbineType = TurbineType(self, turbineTypeNode)
            self.TurbineTypes[turbineType.id] = turbineType

        turbinesNode = mainNode.getElementsByTagName('Turbines')[0]
        for turbineNode in turbinesNode.getElementsByTagName('Turbine'):
            self.Turbines.append(Turbine(self, turbineNode))

        calculationConfigurationsNode = mainNode.getElementsByTagName('CalculationConfigurations')[0]
        for calculationConfigurationNode in calculationConfigurationsNode.getElementsByTagName('CalculationConfiguration'):
            self.CalculationConfigurations.append(
                CalculationConfiguration(
                    ReadAttribute(calculationConfigurationNode, 'model'),
                    calculationConfigurationNode.firstChild.nodeValue
                )
            )

        self.Configuration = Configuration()
        config_nodes = mainNode.getElementsByTagName('Configuration')
        if len(config_nodes) > 0:
            self.Configuration.Parse(mainNode.getElementsByTagName('Configuration')[0])


def LoadWakeReqFile(path):
    retVal = WakeReqFile()
    retVal.Load(path)
    return retVal

if __name__ == '__main__':
    request = LoadWakeReqFile('..\\xsd\\examples\\request.wakeReq')    
    