import time

result = []
def getMem():
    data = {}
    f = open('/proc/meminfo')
    TotalMem = int(f.readline().split()[1])
    FreeMem = int(f.readline().split()[1])
    BufferMem = int(f.readline().split()[1])
    CacheMem = int(f.readline().split()[1])
    used = round((TotalMem-FreeMem-BufferMem-CacheMem)/round(TotalMem,4)*100,2)
    data[int(time.time())]= [int(time.time())*1000,used]
    result.append(data)
    return result



#while True:
#    print getMem()
#    time.sleep(1)
