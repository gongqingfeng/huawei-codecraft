# coding=utf-8
import datetime, collections, random, copy, math
import allocation, mmmaco

def predict_vm(ecs_lines, input_lines, start):
    # Do your work from here#
    result = []
    if ecs_lines is None:
        print 'ecs information is none'
        return result
    if input_lines is None:
        print 'input file information is none'
        return result
    ecs_datas = deal_lines(ecs_lines, '\t')
    #input informations
    inputInfos = deal_lines(input_lines, ' ')
    PMInfos, VMInfos, DimInfos, DateInfos, DataInfos = analyzeInputInfo(inputInfos, ecs_datas)
    analyzedDatas = analyzeTrainDatas(ecs_datas, VMInfos)
    averageDict =  getAverages(analyzedDatas, VMInfos)
    analyzedDatas = removeNoise(analyzedDatas, averageDict, VMInfos)
    exponentialSmoothingDict = getExponentialSmoothing(analyzedDatas, VMInfos, DateInfos)

    allocatedDict = allocation.myFirstFitAllocate_vm(exponentialSmoothingDict, PMInfos, VMInfos)
    vmList = getVMList(exponentialSmoothingDict)
    allocatedDict = mmmaco.mmmacoAllocate_vm(allocatedDict, exponentialSmoothingDict, vmList, PMInfos, VMInfos, DimInfos, DateInfos, DataInfos, start)
    result = getResults(exponentialSmoothingDict, allocatedDict)
    print_result(result)
    return result

def print_result(array):
    print "-" * 40
    for item in array:
        print item
    print "-" * 40

def getVMList(predictDict):
    vmList = []
    #不需要统计flavorAll:predictDict.keys()如果字典不是有序的，那么keys这个列表也是乱序的，即不是按照添加的顺序
    #也就是说，下面的[:-1]并不一定把flavorAll去掉了
    keys = predictDict.keys()[:-1] 
    for key in keys:
        flavorNum = predictDict[key]
        if flavorNum == 0:
            continue
        else:
            for i in range(flavorNum):
                vmList.append(key)
    return vmList

def getResults(predictDict, allocatedDict):
    results = []
    results.append(str(predictDict["flavorAll"])) #虚拟机总数
    predictDict.pop("flavorAll") #删除虚拟机总数，便于后面好处理
    for key in predictDict: #flavor数目
        tmpStr = key + " " + str(predictDict[key])
        results.append(tmpStr)
    results.append(" ") #空行
    results.append(str(len(allocatedDict))) #物理机总数
    for i in allocatedDict:  #每个物理机
        tmpStr = i
        for j in allocatedDict[i]: #物理机的具体分配情况
           if allocatedDict[i][j]:
                tmpStr += " " + j + " " + str(allocatedDict[i][j])
        results.append(tmpStr)
    return results


def deal_lines(lines, charType):
    #文本处理函数：将按照tab和空格分割的数据提取出来，并去掉回车
    item_list = []
    for item in lines:
        item = item.strip('\r\n').split(charType)
        if charType == '\t':
            item[2] = item[2].split(' ')[0]
        if '' not in item:
            item_list.append(item)
            #print item
    return item_list


def analyzeInputInfo(inputInfos, ecs_datas):
    #physical machine informations
    PMInfos = {}
    PMInfos['cpuCoreNum'] = int(inputInfos[0][0])
    PMInfos['memSize'] = int(inputInfos[0][1])
    PMInfos['discSize'] = int(inputInfos[0][2])
    #print 'PMInfos:', PMInfos
    #virtual machine informations 
    VMInfos = {}
    VMInfos['vmFlavorNum'] = int(inputInfos[1][0])
    VMInfos['flavorList'] = [] 
    VMInfos['flavorDefine'] = {}
    for i in range(2, 2 + VMInfos['vmFlavorNum']):
        VMInfos['flavorList'].append(inputInfos[i][0])
        inputInfos[i][1] = int(inputInfos[i][1])
        inputInfos[i][2] = int(inputInfos[i][2]) / 1024
        VMInfos['flavorDefine'][inputInfos[i][0]] = inputInfos[i][1:]
    #print 'VMInfos:', VMInfos
    #dimension needs to be optimized
    DimInfos = {}
    DimInfos['dim'] = inputInfos[2 + VMInfos['vmFlavorNum']][0]
    #print 'DimInfos:', DimInfos
    #date informations
    DateInfos = {}
    DateInfos['beginTime'] = inputInfos[3 + VMInfos['vmFlavorNum']][0]
    DateInfos['endTime'] = inputInfos[4 + VMInfos['vmFlavorNum']][0]
    DateInfos['timeLength'] = calculateTimeDelta(DateInfos['beginTime'], DateInfos['endTime'])
    DataInfos = {}
    DataInfos['dataNum'] = len(ecs_datas)
    #print DateInfos['timeLength']
    return PMInfos, VMInfos, DimInfos, DateInfos, DataInfos

def analyzeTrainDatas(ecs_datas, VMInfos):
    #统计分析函数：将训练数据按天为单位，统计出一天中各个flavor的数量
    beginTrainTime = ecs_datas[0][2]
    endTrainTime = ecs_datas[-1][2]
    #print beginTrainTime, endTrainTime

    analyzedDatas = collections.OrderedDict() #统计分析后的数据，以有序字典的形式保存，键为日期，值为everyDayDatas
    days = (timeFormat(endTrainTime) - timeFormat(beginTrainTime)).days #获得训练数据的总天数
    currentAnalyzeTime = beginTrainTime #当前分析的天数，便于用来构造数据字典中的键
    for day in range(0, days + 1):
        #print currentAnalyzeTime
        everyDayDatas = {} #每天的数据，也就是analyzedDatas中日期键对应的值
        for flavor in VMInfos['flavorList']:
            everyDayDatas[flavor] = 0
        analyzedDatas[currentAnalyzeTime] = everyDayDatas
        currentAnalyzeTime = addSomeDays(currentAnalyzeTime, 1)

    for ecs in ecs_datas:
        ecsFlavor = ecs[1]
        ecsTime = ecs[2]
        if ecsFlavor in VMInfos['flavorList']:
            analyzedDatas[ecsTime][ecsFlavor] = analyzedDatas[ecsTime][ecsFlavor] + 1

    VMInfos['flavorList'].append("flavorAll") #自己创建一个flavor量，便于统计每天中所有的flavor数量
    for item in analyzedDatas:
        tmp = 0
        for i in analyzedDatas[item].values():
            tmp += i
        analyzedDatas[item]['flavorAll'] = tmp
    return analyzedDatas

def timeFormat(time):
    #时间格式化函数：格式化为python时间格式，便于进行加减操作
    timeType = '%Y-%m-%d'
    return datetime.datetime.strptime(time, timeType)

def addSomeDays(time, num):
    #天数增加函数：在之前的日期基础之上增加一
    timeType = '%Y-%m-%d'
    return (datetime.datetime.strptime(time, timeType) + datetime.timedelta(days = num)).strftime(timeType)

def addSomeNumbers(number, num):
    #序号增加函数：在之前的序号基础之上增加一
    return str(int(number) + num)

def calculateTimeDelta(beginTime, endTime):
    #计算时间间隔函数
    return (timeFormat(endTime) - timeFormat(beginTime)).days

def removeNoise(analyzedDatas, averageDict, VMInfos):
    #去除噪声
    for flavor in VMInfos['flavorList']:
        average = averageDict[flavor]
        for item in analyzedDatas:
            flavorNum = analyzedDatas[item][flavor]
            if flavorNum > (average + 3): #大于平均值+3就认为是噪声（注意着这里的平均值）
                analyzedDatas[item][flavor] /= 3
    return analyzedDatas

def exponential_smoothing(alpha, s):
    #指数平滑处理函数
    s2 = [0.0]*len(s)
    s2[0] = s[0]
    for i in range(1, len(s2)):
        s2[i] = alpha*s[i] + (1 - alpha) * s2[i - 1]
    return s2


def getPeriodicData(analyzedDatas, VMInfos, DateInfos):
    #将n天训练数据分割成m天为周期的数据
    deletedAnalyzedDatas = copy.copy(analyzedDatas)
    predicteDays = DateInfos["timeLength"]
    keys = deletedAnalyzedDatas.keys()  #获得keys，便于后面删除
    deletingDays = len(analyzedDatas) %  predicteDays
    for i in range(deletingDays):   #删除不需要统计的日期
        deletedAnalyzedDatas.pop(keys[i])
    keys = deletedAnalyzedDatas.keys() #删除后再更新
    periodicDict = collections.OrderedDict() #经过周期处理后的字典数据
    for i in range(0, len(deletedAnalyzedDatas), predicteDays):
        periodicNum = str(i / predicteDays + 1) #获得周期编号，并转化为字符串类型
        partKeys = keys[i:i + predicteDays] #获得每个周期内的keys
        periodicDict[periodicNum] = {}
        for flavorName in VMInfos["flavorList"]:
            total = 0
            for key in partKeys:
                total += deletedAnalyzedDatas[key][flavorName] #将周期内的相同flavor标签的相加
            periodicDict[periodicNum][flavorName] = total
    return periodicDict

def eachPredict(periodicDict, alpha, beta, gamma, multiple, VMInfos, flavorName):
    DOTNUM = 3 #预测一个点
    pre_day = []
    for i in range(DOTNUM):
        pre_day.append(addSomeNumbers(periodicDict.keys()[-1], i + 1))
    day = periodicDict.keys()
    number = []
    for item in periodicDict:
        number.append(periodicDict[item][flavorName]) #暂时选取一个flavor
    initial_number = copy.deepcopy(number)
    initial_number.insert(0, (initial_number[0] + initial_number[1]  + initial_number[2] ) / 3)
    initial_day = copy.deepcopy(day)
    initial_day.insert(0, '0')

    s_single = exponential_smoothing(alpha, initial_number)
    s_double = exponential_smoothing(beta, s_single)

    a_double = []
    b_double = []
    for i, j in zip(s_single, s_double):
        a_double.append(2 * i - j)
        b_double.append((alpha / (1 - alpha)) * (i - j))
    s_pre_double = [0] * len(s_double)
    for i in range(1, len(initial_day)):
        s_pre_double[i] = a_double[i - 1] + b_double[i - 1]

    insert_day = []
    for i in range(DOTNUM):
        insert_day.append(a_double[-1]+b_double[-1]*(i + 1))
    s_pre_double = s_pre_double + insert_day
    s_triple = exponential_smoothing(gamma, s_double)

    a_triple = []
    b_triple = []
    c_triple = []
    for x, y, z in zip(s_single, s_double, s_triple):
        a_triple.append(3 * x - 3 * y + z)
        b_triple.append((alpha / ( 2 * ((1 - alpha) ** 2))) * ((6 - 5 * alpha) * x -
                                           2 * ((5 - 4 * alpha) * y) + (4 - 3 * alpha) * z))
        c_triple.append(((alpha ** 2) / (2 * ((1 - alpha) ** 2))) * (x - 2 * y + z))
    s_pre_triple = [0] * len(s_triple)
    for i in range(1, len(initial_day)):
        s_pre_triple[i] = a_triple[i-1]+b_triple[i-1]*1 + c_triple[i-1]*(1**2)

    insert_day = []
    for i in range(DOTNUM):
        insert_day.append(a_triple[-1]+b_triple[-1]*(i + 1) + c_triple[-1]*((i + 1)**2))
    s_pre_triple = s_pre_triple + insert_day

    new_day = copy.deepcopy(day)
    new_day = new_day + pre_day

    #output = [new_day, s_pre_double, s_pre_triple]
    #print(output)
    #show_data(new_day, pre_day, day, number, flavorName, s_pre_double, s_pre_triple, alpha)
    #getNum = int(s_pre_triple[-1] * 1.600) #精度:0.001
    getNum = int(s_pre_triple[-1] * multiple)#精度:0.001
    if getNum < 0:
        getNum = 0
    return getNum

def getExponentialSmoothing(analyzedDatas, VMInfos, DateInfos):
    periodicDict =  getPeriodicData(analyzedDatas, VMInfos, DateInfos)
    #alpha = 0.1056  #调试精度：0.0001
    #alpha = 0.17  #调试精度： 0.1637
    #beta = 0.27  # 调试精度： 0.0001
    #gamma = 0.9  # 调试精度： 0.0001

    parameterDict = {
        # flavor名称 alpha beta  gamma
        'flavor1': [0.17, 0.27, 0.9, 1.808],
        'flavor2': [0.189, 0.29, 1.075, 1.6],
        'flavor3': [0.17, 0.27, 0.9, 1.808],
        'flavor4': [0.17, 0.27, 0.9, 1.808],
        'flavor5': [0.17, 0.27, 0.98, 1.808],
        'flavor6': [0.17, 0.27, 0.9, 1.808],
        'flavor7': [0.17, 0.27, 0.9, 1.808],
        'flavor8': [0.175, 0.27, 0.9, 1.808],
        'flavor9': [0.160, 0.27, 0.9, 1.815],
        'flavor10': [0.17, 0.27, 0.9, 1.808],
        'flavor11': [0.20, 0.27, 0.9, 1.808],
        'flavor12': [0.17, 0.27, 0.9, 1.815],
        'flavor13': [0.17, 0.27, 0.9, 1.808],
        'flavor14': [0.17, 0.27, 0.9, 1.808],
        'flavor15': [0.17, 0.27, 0.9, 1.808]
    }

    '''
    parameterDict = {
        # flavor名称 alpha beta  gamma
        'flavor1': [0.189, 0.29, 1.075, 1.6],
        'flavor2': [0.189, 0.29, 1.075, 1.6],
        'flavor3': [0.189, 0.29, 1.075, 1.6],
        'flavor4': [0.189, 0.29, 1.075, 1.6],
        'flavor5': [0.189, 0.29, 1.075, 1.6],
        'flavor6': [0.189, 0.29, 1.075, 1.6],
        'flavor7': [0.189, 0.29, 1.075, 1.6],
        'flavor8': [0.189, 0.29, 1.075, 1.6],
        'flavor9': [0.189, 0.29, 1.075, 1.6],
        'flavor10': [0.189, 0.29, 1.075, 1.6],
        'flavor11': [0.189, 0.29, 1.075, 1.6],
        'flavor12': [0.189, 0.29, 1.075, 1.6],
        'flavor13': [0.189, 0.29, 1.075, 1.6],
        'flavor14': [0.189, 0.29, 1.075, 1.6],
        'flavor15': [0.17, 0.27, 0.9, 1.808]
    }
    '''
    exponentialSmoothingDict = collections.OrderedDict()  # 注意，一定要设置成有序的字典，这样在获取keys列表时，列表才是添加键时的顺序
    total = 0
    for flavorName in VMInfos["flavorList"][:-1]:
        parameterList = parameterDict[flavorName]
        exponentialSmoothingDict[flavorName] = eachPredict(periodicDict, parameterList[0], parameterList[1],
                                                           parameterList[2], parameterList[3], VMInfos, flavorName)
        total += exponentialSmoothingDict[flavorName]
    exponentialSmoothingDict["flavorAll"] = total
    return exponentialSmoothingDict

def getAverages(analyzedDatas, VMInfos):  #除开有0的
    averageDict = collections.OrderedDict()
    for flavor in VMInfos['flavorList']:
        tmp = 0
        cnt = 0
        for item in analyzedDatas:
            flavorNum = analyzedDatas[item][flavor]
            if flavorNum:
                cnt += 1
                tmp += flavorNum
        tmp = math.ceil(tmp / float(cnt)) #采用向上取整
        averageDict[flavor] = tmp
    total = 0
    for i in averageDict.values()[:-1]:
        total += i
    averageDict["flavorAll"] = total
    return averageDict


