import asyncio
from sys import argv
import json
from os.path import isdir
from os import getcwd, mkdir, remove, name
from random import choice
from socket import gethostname

#includes
from functions import *


class data:
    # ALL OF OUR DATA
    master = []
    # AVERAGES OF EACH SCAN
    array = []

    #CONFIG
    INTERVAL_AMOUNT = 6
    INTERVAL_SECONDS = 1
    DATASET_NAME = "test1"
    PRINT_UPDATES_TO_SHELL = True
    

# THE MAIN SCAN PROCESS
async def main():
    envDir = getcwd() + "/datasets"
    if not isdir(envDir):
        mkdir(envDir)
        
    dataDir = getcwd() + "/datasets/" + data.DATASET_NAME
    if not isdir(dataDir):
        mkdir(dataDir)

        
    overall_count = 0
    # WORKER
    while True:
        try:
            # NEW THREAD FOR EFFICIANCY
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
                # Means you need to install dstat/be on a linux machine!
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
            
        # SORT OUT SEND/RECV IN A CSV-LIKE FORMAT
        ctl = 0
        for _ in range(data.INTERVAL_AMOUNT):
            recv.append(convertBytes(buff[ctl]))
            send.append(convertBytes(buff[ctl + 1]))
            ctl += 2
            
        # SAVE OUR SET OF DATA
        final = {
            'send': send,
            'recv': recv,
            'sendavg': getAvg(send),
            'recvavg': getAvg(recv)
            }

        #APPENDS FINAL DATA FROM EACH SCAN
        # If somehow failure during I/O operation,
        with open(dataDir + "/master.json.tmp", "w+") as a:
            json.dump(data.master, a)

        with open(dataDir + "/avg_array.json.tmp", "w+") as b:
            json.dump(data.master, b)

        # Appends with fingers crossed, and a backup just incase ;)
        data.master.append(final)
        
        with open(dataDir + "/master.json", "w+") as c:
            json.dump(data.master, c)

        remove(dataDir + "/master.json.tmp")

        # 2nd Append
        data.array.append([data.master[overall_count]['sendavg'], data.master[overall_count]['recvavg']])
        
        with open(dataDir + "/avg_array.json", "w+") as d:
            json.dump(data.array, d)

        remove(dataDir + "/avg_array.json.tmp")

        if data.PRINT_UPDATES_TO_SHELL:
            toys = ["|", "/", "-", "\\"]
            for x in range(len(toys)):
                print((" " * 4) + (toys[x] * 10) + "\r", end="")
                await asyncio.sleep(.5)
                
            print(
                f"Training@{gethostname()} to [dataset: {data.DATASET_NAME}]\n"
                f"Scan Count: {overall_count + 1}\n"
                f"Average Send: {data.array[overall_count][0]} bytes\n"
                f"Average Recv: {data.array[overall_count][1]} bytes\n"
                f"Metric: {data.INTERVAL_AMOUNT} checks @ 1 check per {data.INTERVAL_SECONDS} seconds\n"
                "\r", end=""
                )

        overall_count += 1    
            
            

def initMainLoop():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())           
        

if "nt" in name:
    print("Windows/MAC Not Supported! Dstat, the cli tool used to collect the total network load metric, is a Linux-based tool! A Windows version can be expected in the future.")
    exit(1)
        

else:
    initMainLoop()
    
    

