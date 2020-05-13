import asyncio
from sys import argv
import json
from os.path import isdir, exists
from os import getcwd, mkdir, remove, name
from socket import gethostname
from datetime import datetime
from aiofile import AIOFile

#includes
from functions import *

class data:
    # HASH FOR THIS SESSION
    uid = hashes.eight_char()
        
    # ALL OF OUR DATA
    master = []

    array_handle = None
    master_handle = None

    #CONFIG
    INTERVAL_AMOUNT = 6
    INTERVAL_SECONDS = 1
    DATASET_NAME = "test1"
    
# THE MAIN SCAN PROCESS
async def main():

    cwd = getcwd()

    envDir = cwd + "/datasets"
    if not isdir(envDir):
        mkdir(envDir)   

    sesDir = cwd + "/sessions"
    if not isdir(sesDir):
        mkdir(sesDir)        
        
    dataDir = envDir + "/" + data.DATASET_NAME
    if not isdir(dataDir):
        mkdir(dataDir)

    logFile = dataDir + "/log.log"
    if not exists(logFile):
        async with AIOFile(logFile, "w+") as ff:
            await ff.write(f"[1] - {data.uid}")
            await ff.fsync()
                        
    else:
        with open(logFile, "r") as ll:
            logBffr = ll.read()
            logIndex = int(len(logBffr.split()) + 1)
        with open(logFile, "a") as li:
            li.write(f"[{str(logIndex)}] - {data.uid}")          
            
    with open(dataDir + "/master.json") as aa:
        data.master_handle = json.load(aa)

    with open(dataDir + "/avg_array.json") as ab:
        data.array_handle = json.load(ab)

    # TRAINING DATA    
    arrayRecvTrain = []
    for x in range(len(data.array_handle)):
        arrayRecvTrain.append(data.array_handle[x][0])
        
    arraySendTrain = []
    for y in range(len(data.array_handle)):    
        arraySendTrain.append(data.array_handle[y][1])
        
    if len(arraySendTrain) != len(arrayRecvTrain):
        print(f"Failed with:\narraySendTrain:\nlength of {len(arraySendTrain)}\narrayRecvTrain:\n{len(arrayRecvTrain)}")
        print("Invalid structre in dataset! Dataset must be retrained!")
        exit(1)

    training_recv_min = min(arrayRecvTrain)
    training_recv_max = max(arrayRecvTrain)
    training_recv_avg = getAvg(arrayRecvTrain)
    
    training_send_min = min(arraySendTrain)
    training_send_max = max(arraySendTrain)
    training_send_avg = getAvg(arraySendTrain)    
    
    overall_count = 0
    flags = []
    arrayRecv = []
    arraySend = []

    # WORKER
    while True:
        try:
            proc = await asyncio.create_subprocess_shell(
                f"dstat -n {str(data.INTERVAL_SECONDS)} {str(data.INTERVAL_AMOUNT)} --float",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
                )
            
            stdout, stderr = await proc.communicate()
            
            if stdout:
                output = stdout.decode("utf-8")
                
            if stderr:
                output = None
                # Unk error or you need to install dstat!
                raise stderr

            #Allow to fail with stderr
            buff = output.split()       

        except Exception as f:
            raise f
        
        # HOIST OUR CURRENT INSTANCES
        send = []
        recv = []

        # TRIM THE JUNK
        for x in range(5):
            buff.pop(0)
            
        # SORT OUT SEND/RECV VALUES IN A CSV-LIKE FORMAT
        ctl = 0
        for _ in range(data.INTERVAL_AMOUNT):
            recv.append(convertBytes(buff[ctl]))
            send.append(convertBytes(buff[ctl + 1]))
            ctl += 2

        # LIVE DATA
        arrayRecv.append(getAvg(recv))
        arraySend.append(getAvg(send))
        
        live_recv_min = min(arrayRecv)
        live_recv_max = max(arrayRecv)
        live_recv_avg = getAvg(arrayRecv)
        
        live_send_min = min(arraySend)
        live_send_max = max(arraySend)
        live_send_avg = getAvg(arraySend)

        #RECV_MAX
        if live_recv_max > training_recv_max:
            #RISE IN AVG
            if live_recv_max > training_recv_max + (training_recv_max * 0.0001):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected +0.0001 average increase @ recv_max'})
                ####
                #0.0001 Increase
                ####
            elif live_recv_max > training_recv_max + (training_recv_max * 0.001):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected +0.001 increase @ recv_max'})
                ####
                #0.001 Increase
                ####        
            elif live_recv_max > training_recv_max + (training_recv_max * 0.01):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected +0.01 increase @ recv_max'})
                ####
                #0.01 Increase
                ####
            elif live_recv_max > training_recv_max + (training_recv_max * 0.1):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected +0.1 increase @ recv_max'})
                ####
                #0.1 Increase
                ####
        elif live_recv_max < training_recv_max:
            #DROP IN AVG
            if live_recv_max < training_recv_max + (training_recv_max * 0.0001):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected -0.0001 average decrease @ recv_max'})
                ####
                #0.0001 Decrease
                ####
            elif live_recv_max < training_recv_max + (training_recv_max * 0.001):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected -0.001 decrease @ recv_max'})
                ####
                #0.001 Decrease
                ####        
            elif live_recv_max < training_recv_max + (training_recv_max * 0.01):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected -0.01 decrease @ recv_max'})
                ####
                #0.01 Decrease
                ####
            elif live_recv_max < training_recv_max + (training_recv_max * 0.1):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected -0.1 decrease @ recv_max'})
                ####
                #0.1 Decrease
                ####            


        #RECV_MIN
        elif live_recv_min > training_recv_min:
            #RISE IN AVG
            if live_recv_min > training_recv_min + (training_recv_min * 0.0001):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected +0.0001 average increase @ recv_min'})
                ####
                #0.0001 Increase
                ####
            elif live_recv_min > training_recv_min + (training_recv_min * 0.001):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected +0.001 increase @ recv_min'})
                ####
                #0.001 Increase
                ####        
            elif live_recv_min > training_recv_min + (training_recv_min * 0.01):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected +0.01 increase @ recv_min'})
                ####
                #0.01 Increase
                ####
            elif live_recv_min > training_recv_min + (training_recv_min * 0.1):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected +0.1 increase @ recv_min'})
                ####
                #0.1 Increase
                ####
        elif live_recv_max < training_recv_max:
            #DROP IN AVG
            if live_recv_min < training_recv_min + (training_recv_min * 0.0001):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected -0.0001 average decrease @ recv_min'})
                ####
                #0.0001 Decrease
                ####
            elif live_recv_min < training_recv_min + (training_recv_min * 0.001):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected -0.001 decrease @ recv_min'})
                ####
                #0.001 Decrease
                ####        
            elif live_recv_min < training_recv_min + (training_recv_min * 0.01):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected -0.01 decrease @ recv_min'})
                ####
                #0.01 Decrease
                ####
            elif live_recv_min < training_recv_min + (training_recv_min * 0.1):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected -0.1 decrease @ recv_min'})
                ####
                #0.1 Decrease
                ####        


        #SEND_MAX 
        elif live_send_max > training_send_max:
            #RISE IN AVG
            if live_send_max > training_send_max + (training_send_max * 0.0001):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected +0.0001 average increase @ recv_max'})
                ####
                #0.0001 Increase
                ####
            elif live_send_max > training_send_max + (training_send_max * 0.001):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected +0.001 increase @ recv_max'})
                ####
                #0.001 Increase
                ####        
            elif live_send_max > training_send_max + (training_send_max * 0.01):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected +0.01 increase @ recv_max'})
                ####
                #0.01 Increase
                ####
            elif live_send_max > training_send_max + (training_send_max * 0.1):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected +0.1 increase @ recv_max'})
                ####
                #0.1 Increase
                ####
        elif live_send_max < training_send_max:
            #DROP IN AVG
            if live_send_max < training_send_max + (training_send_max * 0.0001):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected -0.0001 average decrease @ recv_max'})
                ####
                #0.0001 Decrease
                ####
            elif live_send_max < training_send_max + (training_send_max * 0.001):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected -0.001 decrease @ recv_max'})
                ####
                #0.001 Decrease
                ####        
            elif live_send_max < training_send_max + (training_send_max * 0.01):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected -0.01 decrease @ recv_max'})
                ####
                #0.01 Decrease
                ####
            elif live_send_max < training_send_max + (training_send_max * 0.1):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected -0.1 decrease @ recv_max'})
                ####
                #0.1 Decrease
                ####            


        #RECV_MIN
        elif live_send_min > training_send_min:
            #RISE IN AVG
            if live_send_min > training_send_min + (training_send_min * 0.0001):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected +0.0001 average increase @ recv_min'})
                ####
                #0.0001 Increase
                ####
            elif live_send_min > training_send_min + (training_send_min * 0.001):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected +0.001 increase @ recv_min'})
                ####
                #0.001 Increase
                ####        
            elif live_send_min > training_send_min + (training_send_min * 0.01):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected +0.01 increase @ recv_min'})
                ####
                #0.01 Increase
                ####
            elif live_send_min > training_send_min + (training_send_min * 0.1):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected +0.1 increase @ recv_min'})
                ####
                #0.1 Increase
                ####
        elif live_send_max < training_send_max:
            #DROP IN AVG
            if live_send_min < training_send_min + (training_send_min * 0.0001):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected -0.0001 average decrease @ recv_min'})
                ####
                #0.0001 Decrease
                ####
            elif live_send_min < training_send_min + (training_send_min * 0.001):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected -0.001 decrease @ recv_min'})
                ####
                #0.001 Decrease
                ####        
            elif live_send_min < training_send_min + (training_send_min * 0.01):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected -0.01 decrease @ recv_min'})
                ####
                #0.01 Decrease
                ####
            elif live_send_min < training_send_min + (training_send_min * 0.1):
                flags.append({'time': str(datetime.now()), 'flag': 'Detected -0.1 decrease @ recv_min'})
                ####
                #0.1 Decrease
                ####        

        # SAVE OUR SESSION
        final = {
            'send': send,
            'recv': recv,
            'sendavg': getAvg(send),
            'recvavg': getAvg(recv),
            'flags': flags
            }

        data.master.append(final)        
        with open(sesDir + f"/session_" + data.uid + ".json", "w+") as xf:
            json.dump(data.master, xf)

        with open(sesDir + f"/flags_" + data.uid + ".json", "w+") as zf:
            json.dump(flags, zf)         

        overall_count += 1
        print("Looped!")
        print(flags)
                        

def initMainLoop():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())           
        

if "nt" in name:
    print("Windows/MAC Not Supported! Dstat, the cli tool used to collect the total network load metric, is a Linux-based tool! A Windows version can be expected in the future.")
    exit(1)
        

else:
    initMainLoop()
    
    

