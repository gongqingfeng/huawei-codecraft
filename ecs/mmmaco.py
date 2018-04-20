# coding=utf-8
import copy, random, collections, time
def createZeros(rows, cols):
    # 创建0元素矩阵
    lines = [[0 for col in range(cols)] for row in range(rows)]
    return lines

def getShape(matrix):
    #得到矩阵的行列数
    rows = len(matrix)
    cols = len(matrix[0])
    return rows, cols

def initVMResourceMatrix(vmResourceMatrix, VMInfos, vmList):
    #Initialize the virtual hosts request resource
    rows, cols = getShape(vmResourceMatrix)
    for row in range(rows):
        flavorName = vmList[row]
        vmResourceMatrix[row][0] = row  #vm sequence number
        #test =  VMInfos['flavorDefine'][flavorName] #加这句报错
        #test =  VMInfos['flavorDefine'][flavorName][0] #加这句报错
        #以下两行在运行中出错
        vmResourceMatrix[row][1] = VMInfos['flavorDefine'][flavorName][0] #cpu number 
        vmResourceMatrix[row][2] = VMInfos['flavorDefine'][flavorName][1]  #mem size
        vmResourceMatrix[row][3] =  flavorName  #vm flavorType
    return vmResourceMatrix

def initPMRealResourceMatrix(pmRealResourceMatrix, PMInfos):
    #Initialize the physical hosts real resource
    rows, cols = getShape(pmRealResourceMatrix)
    for row in range(rows):
        pmRealResourceMatrix[row][0] = row   #pm sequence number
        pmRealResourceMatrix[row][1] = PMInfos["cpuCoreNum"]   #cpu number
        pmRealResourceMatrix[row][2] = PMInfos["memSize"]   #mem size
    return pmRealResourceMatrix

def initPMCurrentResourceMatrix(pmCurrentResourceMatrix, PMInfos):
    #Initialize the physical hosts real resource
    rows, cols = getShape(pmCurrentResourceMatrix)
    for row in range(rows):
        pmCurrentResourceMatrix[row][0] = row   #pm sequence number
        pmCurrentResourceMatrix[row][1] = copy.deepcopy(PMInfos["cpuCoreNum"])  #cpu number
        pmCurrentResourceMatrix[row][2] = copy.deepcopy(PMInfos["memSize"])   #mem size
    return pmCurrentResourceMatrix

def initVMMapMatrix(vmMapMatrix):
    #the mapping relations between virtual hosts and physical hosts
    rows, cols = getShape(vmMapMatrix)
    for row in range(rows):
        vmMapMatrix[row][0] = row   #vm sequence number
        vmMapMatrix[row][1] = 0  #display or not
        vmMapMatrix[row][2] = 0   #pm sequence number
    return vmMapMatrix

def initMatrix(totalPMNum, totalVMNum, VMInfos, PMInfos, vmList):
    #初始化各种要用到的矩阵
    vmResourceMatrix = initVMResourceMatrix(createZeros(totalVMNum, 4),  VMInfos, vmList) #initial the virtual hosts request resource
    #return 0, 0, 0, 0, 0
    pmRealResourceMatrix = initPMRealResourceMatrix(createZeros(totalPMNum, 3), PMInfos) #initial the physical hosts real resource
    pmCurrentResourceMatrix = createZeros(totalPMNum, 3) #initial the current resource in the physical host
    vmMapMatrix = createZeros(totalVMNum, 3)  #the mapping relations between virtual hosts and physical hosts
    gammaPheromoneMatrix = createZeros(totalPMNum, totalVMNum)
    return vmResourceMatrix, pmRealResourceMatrix, pmCurrentResourceMatrix, vmMapMatrix, gammaPheromoneMatrix

def initGammaPheromoneMatrix(gammaPheromoneMatrix, pheromoneGammaMax, pheromoneGammaMin):
    #Initialize pheromone concentration matrix
    rows, cols = getShape(gammaPheromoneMatrix)
    for row in range(rows):
        for col in range(cols):
            gammaPheromoneMatrix[row][col] = 0.5 * (pheromoneGammaMax + pheromoneGammaMin)
    return gammaPheromoneMatrix

def calculateVisibility(pmCurrentResourceMatrix, pmRealResourceMatrix, vmResourceMatrix):
    dimPMRealRows = getShape(pmRealResourceMatrix)[0]
    dimVMRows = getShape(vmResourceMatrix)[0]
    vis = createZeros(dimPMRealRows, dimVMRows)
    for i in range(dimPMRealRows):
        for j in range(dimVMRows):
            vis[i][j] = (pmCurrentResourceMatrix[i][1] + vmResourceMatrix[j][1]) / float(pmRealResourceMatrix[i][1])
    return vis

def calculateProbability(visibility, gammaPheromoneMatrix, pheromoneFactor, visibilityFactor, pos):
    #这里没有考虑分母，因为分母大小一样，并不影响我们比较概率的大小
    rows, cols = getShape(visibility) #visibility和gammaPheromoneMatrix维度一样
    probability = [0 for col in range(cols)]
    for col in range(cols):
        probability[col] = (visibility[pos][col] ** pheromoneFactor) * (gammaPheromoneMatrix[pos][col] ** visibilityFactor)
    return probability

def findVM(vmMapMatrix):
    rows = getShape(vmMapMatrix)[0]
    vmFoundList = []
    for row in range(rows):
        if vmMapMatrix[row][1] == 0:  #display or not
            vmFoundList.append(vmMapMatrix[row][0])
    return vmFoundList

def descendSort(vmFoundProbality):
    tmpDict = {}
    for i in range(len(vmFoundProbality[0])):
        tmpDict[vmFoundProbality[0][i]] = vmFoundProbality[1][i]
    sortedList = sorted(tmpDict.items(), reverse=True, key=lambda item:item[1])
    pro = []
    index = []
    for item in sortedList:
        pro.append(item[1])
        index.append(item[0])
    return pro, index

def findPMPosition(pmCurrentResourceMatrix, vmResourceMatrix, v_pos, p_pos, totalPMNum):
    find = False
    flag = 1
    availablePMList = range(totalPMNum) 
    while flag:
        if (pmCurrentResourceMatrix[p_pos][1] < vmResourceMatrix[v_pos][1]) or (pmCurrentResourceMatrix[p_pos][2] < vmResourceMatrix[v_pos][2]):
            availablePMList.remove(p_pos)
            if availablePMList:
                index = random.randint(0, len(availablePMList) - 1) #随机获取一个物理机
                p_pos = availablePMList[index]
            else:
                break
        else:
            find = True
            flag = 0
    pos = p_pos
    return pos, find

def updateVMMapMatrix(vmMapMatrix, maxUsageRatioBest, volatileFactor, pheromoneGammaMax, pheromoneGammaMin):
    delt = maxUsageRatioBest * 3
    rows, cols = getShape(vmMapMatrix)
    for row in range(rows):
        for col in range(cols):
            vmMapMatrix[row][col] = (1 - volatileFactor) * vmMapMatrix[row][col] + delt
            if vmMapMatrix[row][col] > pheromoneGammaMax:
                vmMapMatrix[row][col] = pheromoneGammaMax
            elif vmMapMatrix[row][col] < pheromoneGammaMin:
                vmMapMatrix[row][col] = pheromoneGammaMin
            else:
                pass
    return vmMapMatrix

def putVM2PM(vmResourceMatrix, v_pos, pmCurrentResourceMatrix, p_pos, vmMapMatrix):
    pmCurrentResourceMatrix[p_pos][1] = pmCurrentResourceMatrix[p_pos][1] - vmResourceMatrix[v_pos][1]
    pmCurrentResourceMatrix[p_pos][2] = pmCurrentResourceMatrix[p_pos][2] - vmResourceMatrix[v_pos][2]
    vmMapMatrix[v_pos][1] = 1
    vmMapMatrix[v_pos][2] = p_pos
    return pmCurrentResourceMatrix, vmMapMatrix

def calculateUsage(vmMapMatrix, totalPMNum):
    deployDict = collections.OrderedDict()
    for i in range(totalPMNum): #按物理机统计
        deployDict[i] = []
        for vmMap in vmMapMatrix:
            if vmMap[1] != 0 and vmMap[2] == i:
                deployDict[i].append(vmMap[0])
    return deployDict

def getAllocatedDict(usage, vmResourceMatrix):
    allocatedDict = collections.OrderedDict()
    keys = usage.keys()
    cnt = 0
    for key in keys:
        if usage[key]:
            cnt += 1
            keyStr = str(cnt)
            allocatedDict[keyStr] = {}
            for item in usage[key]:
                flavorName = vmResourceMatrix[item][3]
                if flavorName in allocatedDict[keyStr]: #统计flavor的数量标签若存在，加1
                    allocatedDict[keyStr][flavorName] += 1
                else:
                    allocatedDict[keyStr][flavorName] = 1
    return allocatedDict


def calculateUsageRatio(usage, vmResourceMatrix, pmRealResourceMatrix, DimInfos):
    keys = usage.keys()
    pmUsedNum = 0
    cpuOrMemUsed = 0
    cpuIndex = 1
    memIndex = 2
    if DimInfos['dim'] == 'CPU':
        index = cpuIndex
    elif DimInfos['dim'] == 'MEM':
        index = memIndex
    else:
        index = cpuIndex   #防止没有收集到这个维度的信息
    for key in keys:
        if len(usage[key]) != 0:
            pmUsedNum += 1
            for item in usage[key]: #usage[key]存放的是虚拟机的编号
                cpuOrMemUsed += vmResourceMatrix[item][index]
    usageRatio = cpuOrMemUsed / float((pmRealResourceMatrix[0][index] * pmUsedNum))
    return usageRatio

def calculateTime(start, bestAllocatedDict, dealtDict):
    end = time.time()
    exitFlag = False
    Dict = dealtDict
    if end - start > 57:
        exitFlag = True
        if bestAllocatedDict:
            Dict = bestAllocatedDict
    return exitFlag, Dict

def mmmacoAllocate_vm(dealtDict, predictDict, vmList, PMInfos, VMInfos, DimInfos, DateInfos, DataInfos, start):

    #改进的最大最小蚁群优化算法(Modified MAX-MIN Ant Colony Optimization)
    totalPMNum =  len(dealtDict) - 1 #物理主机总个数
    totalVMNum = predictDict["flavorAll"] #虚拟机总个数
    bestAllocatedDict = {}
    volatileFactor = 0.3 #挥发因子
    pheromoneFactor = 1.5 #信息素启发因子
    visibilityFactor = 0.7 #能见度启发式因子
    pheromoneG = 5 #下限因子
    antsNum = 10 #蚂蚁个数
    maxIterationTimes = 10 #最大迭代次数
    pheromoneGammaMax = 5 #信息素最大浓度
    pheromoneGammaMin = pheromoneGammaMax / pheromoneG #信息素最小浓度
    #还没出错
    vmResourceMatrix, pmRealResourceMatrix, pmCurrentResourceMatrix, vmMapMatrix, gammaPheromoneMatrix = initMatrix(totalPMNum, totalVMNum, VMInfos, PMInfos, vmList)

    gammaPheromoneMatrix = initGammaPheromoneMatrix(gammaPheromoneMatrix, pheromoneGammaMax, pheromoneGammaMin) #初始化信息素浓度矩阵
    maxUsageRatioBestList = [] #保存利用率的列表
    maxUsageRatioBest = 0   #利用率的初始值0

    for iterationTime in range(maxIterationTimes): #开始迭代
        #print "iterationTime: ", iterationTime
        for ant in range(antsNum): #蚁群开始工作
            exitFlag, returnDict  = calculateTime(start, bestAllocatedDict, dealtDict)
            if exitFlag:
                return returnDict
            find = False
            vmMapMatrix = initVMMapMatrix(vmMapMatrix) #对每一只蚂蚁的映射图都要初始化
            pmCurrentResourceMatrix = initPMCurrentResourceMatrix(pmCurrentResourceMatrix, PMInfos) #初始化所有物理机里面的空闲资源
            pos = random.randint(0, totalPMNum - 1)  #当前蚂蚁的位置：即在哪个物理机上
            #开始准备将虚拟机放置到物理主机上
            vmNum = 0 #虚拟机序号，统一序号都是从0开始
            while vmNum < totalVMNum: #直到虚拟机放完才跳出
                exitFlag, returnDict = calculateTime(start, bestAllocatedDict, dealtDict)
                if exitFlag:
                    return returnDict
                visibility = calculateVisibility(pmCurrentResourceMatrix, pmRealResourceMatrix, vmResourceMatrix) #计算能见度
                probability = calculateProbability(visibility, gammaPheromoneMatrix, pheromoneFactor,visibilityFactor, pos) #计算转移概率
                vmFoundList = findVM(vmMapMatrix) #寻找未被放置的虚拟机,并以列表返回序号
                vmFoundProbality = [vmFoundList, probability] #虚拟机与各自概率的映射列表
                pro, index = descendSort(vmFoundProbality) #按照概率从大到小排序
                vmPosition = index[0] # 虚拟机序号（位置）
                pos, find = findPMPosition(pmCurrentResourceMatrix, vmResourceMatrix, vmPosition, pos, totalPMNum) #寻找虚拟机放置位置
                if find:
                    pmCurrentResourceMatrix, vmMapMatrix = putVM2PM(vmResourceMatrix, vmPosition, pmCurrentResourceMatrix, pos, vmMapMatrix) #将虚拟机放置在物理机中
                    vmNum = vmNum + 1
                else:
                    break
            if not find:
                continue
            #得到放置情况
            usage = calculateUsage(vmMapMatrix, totalPMNum)
            allocatedDict = getAllocatedDict(usage, vmResourceMatrix)
            usageRatioBest = calculateUsageRatio(usage, vmResourceMatrix, pmRealResourceMatrix, DimInfos)
            if maxUsageRatioBest < usageRatioBest:
                maxUsageRatioBest = usageRatioBest
                bestAllocatedDict = copy.deepcopy(allocatedDict)

            #更新信息素
            maxUsageRatioBestList.append(maxUsageRatioBest)
            updateVMMapMatrix(vmMapMatrix, maxUsageRatioBest, volatileFactor,pheromoneGammaMax, pheromoneGammaMin)
            #print allocatedDict
            Sum = 0
            for key in allocatedDict:
                if allocatedDict[key] != {}:
                    Sum += 1
    if not bestAllocatedDict: #如果一次解都没找到，就用ffa的数据
       bestAllocatedDict = dealtDict
    return bestAllocatedDict
