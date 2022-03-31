import boto3
import uuid
import json
from mpire import WorkerPool
from loguru import logger
from glob import glob
import os 
import asyncio
import tqdm

sqsResource = boto3.resource('sqs')


logger.add(f"sqs_submit.log")


def write_sqs(integerList):
    queue = sqsResource.get_queue_by_name(QueueName="C4_data_process")
    entries = []

    for src, trg in integerList:
        entry =  {
            'Id': str(uuid.uuid4()),
            'MessageBody': json.dumps(
                {"src": src,
                 "trg": trg,
                 "path":path}
                )
        }

        entries.append(entry)

    # await asyncio.sleep(2)

    # print(entries)
    queue.send_messages(Entries=entries)




def split(file_name):
    count = 10
    data = []
    temp = []
    with open(file_name) as f:
        for line in f:
            if len(temp)==10:
                data.append([temp])
                temp = []
            src, trg = line.strip().split("\t")
            temp.append((src, trg))
    return data

file_list = glob("/home/parth.chudasama/data_mnt/target_pairs/*")


for item in file_list:
    path = item.rsplit("_",1)[1].split('-')[0]

    if path in ['00000','00001','00002','00003']:
        continue
    
    logger.info(f"Starting {item}")
    split_data = split(item)

    with WorkerPool(n_jobs=os.cpu_count() - 1) as pool:
        data = pool.map(write_sqs, split_data, progress_bar=True)
    