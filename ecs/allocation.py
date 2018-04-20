# coding=utf-8
import copy, collections

PMNum = 0
PMName = 0
CPUNUM = 0
MEMSIZE = 0
allocatedDict = 0
averageDict = 0
averageDictCopy = 0
CPURes = 0
MEMRes = 0
reversedFlavorList = 0
VMInfos = 0
PMInfos = 0
def myFirstFitAllocate_vm(averagedict, pmInfos, vmInfos):
	global PMNum, PMName, CPUNUM, MEMSIZE, CPURes, MEMRes, VMInfos
	global averageDict, allocatedDict, averageDictCopy, reversedFlavorList
	global initialPositon
	VMInfos = vmInfos
	PMInfos = pmInfos
	averageDict = copy.copy(averagedict)
	averageDictCopy = copy.copy(averagedict)
	PMNum = 1 #所需要的物理机数量的初始值
	PMName = str(PMNum) #第一台物理机名称
	CPUNUM = PMInfos["cpuCoreNum"] #一台物理机的CPU数量
	MEMSIZE = PMInfos["memSize"] #一台物理机的MEM大小
	allocatedDict = collections.OrderedDict() #存放分配结果的字典,以数量的编号为键
	#对第一台物理机的放置情况初始化
	initialPositon = collections.OrderedDict()
	for i in range(len(VMInfos["flavorList"]) -1):
		initialPositon[VMInfos["flavorList"][i]] = 0 
	allocatedDict[PMName] = copy.copy(initialPositon) #每台物理机里面的具体结果用字典组织
	CPURes = CPUNUM #一台物理机的CPU数量剩余初始值
	MEMRes = MEMSIZE #一台物理机的MEM大小剩余初始值
	#待分配的flavor
	reversedFlavorList = VMInfos["flavorList"][::-1] #注意反后的首元素为flavorAll
	#print averageDict
	
	for i in range(1, len(reversedFlavorList)):
		# print i, reversedFlavorList[i]
		while True:
			allocateEach(i)
			if(averageDictCopy[reversedFlavorList[i]] == 0):
				break
	return allocatedDict

def allocateEach(index):
	#递归分配
	global PMNum, PMName, CPUNUM, MEMSIZE, CPURes, MEMRes, VMInfos
	global averageDict, allocatedDict, averageDictCopy, reversedFlavorList
	global initialPositon
	for flavorName in reversedFlavorList[index:]:
		flavorCPUNum = VMInfos['flavorDefine'][flavorName][0] #某种flavor所需的cpu
		flavorMEMSize = VMInfos['flavorDefine'][flavorName][1] #某种flavor所需的mem
		if(averageDict[flavorName] > 0):	
			for j in range(averageDict[flavorName]):
				if(MEMRes >= flavorMEMSize and CPURes >= flavorCPUNum):
					#表示可以存放
					averageDictCopy[flavorName] -= 1 #放了就减去1 
					allocatedDict[PMName][flavorName] += 1
					CPURes -= flavorCPUNum
					MEMRes -= flavorMEMSize
				else:
					#表示这个flavor放不下，那么需要考虑放小的flavor
					allocatingFlavorIndex =  index + 1
					if(allocatingFlavorIndex < len(reversedFlavorList)):
						#averageDict = copy.copy(averageDictCopy)
						allocateEach(allocatingFlavorIndex)
						break
					else:
						PMNum += 1 #所需要的物理机数量加1
						PMName = str(PMNum) #物理机名称
						allocatedDict[PMName] = copy.copy(initialPositon) #每台物理机里面的具体结果用字典组织
						CPURes = CPUNUM #一台物理机的CPU数量剩余初始值
						MEMRes = MEMSIZE #一台物理机的MEM大小剩余初始值
						break #某种flavor不再放置
			averageDict = copy.copy(averageDictCopy)
		else:
			continue #这种flavor数目为0,跳出执行下一个
		break #对flavorList不再循环


