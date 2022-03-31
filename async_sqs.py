"""
aiobotocore SQS Producer Example
"""
import asyncio
import random
import sys

from aiobotocore.session import get_session
import botocore.exceptions
from loguru import logger

logger.add(f"sqs_submit.log")
file_name = "/home/parth.chudasama/data_mnt/target_pairs/target_pairs_00003-of-00010"


def split(file_name):
    count = 10
    data = []
    temp = []
    with open(file_name) as f:
        for line in f:
            if len(temp)==10:
                data.append(temp)
                temp = []
            src, trg = line.strip().split("\t")
            temp.append((src, trg))
    return data

async def go():
    # Boto should get credentials from ~/.aws/credentials or the environment
    session = get_session()
    count = 0
    async with session.create_client('sqs', region_name='us-west-2') as client:


        split_data = split(file_name)
        queue_url = "https://sqs.us-east-1.amazonaws.com/679792626450/C4_data_process"

        print('Putting messages on the queue')


        for item in tqdm(split_data)
            for src, trg in item:
                    entry =  {
                        'Id': str(uuid.uuid4()),
                        'MessageBody': json.dumps(
                            {"src": src,
                            "trg": trg,
                            "path":path}
                            )
                    }

                    entries.append(entry)

            try:
                count+=1
                await client.send_message_batch(
                    QueueUrl=queue_url,
                    Entries=entries
                )
                if count%100 == 0:
                    print(f'Pushed "{count}" to queue')


def main():
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(go())
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()