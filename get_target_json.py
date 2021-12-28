
from loguru import logger
import os
import gzip
import json
import hashlib
import csv
from mpire import WorkerPool
from glob import glob


logger.add("get_sentence.log")

edits_tsv_list = glob("/mnt/spellcheck_data/data/c4dataset/edits_tsv/*")
dataset_dir = "/home/parth.chudasama/data_mnt/c4/en"
target_path = "/home/parth.chudasama/data_mnt/target_data"


def get_target(edits_tsv_path):
    logger.info(f"Loading C4_200M target sentence hashes from {edits_tsv_path}")
    target_file = "target_sentencs_" + edits_tsv_path.split("-",1)[-1]
    remaining_hashes = set()
    with open(edits_tsv_path) as edits_tsv_reader:
        for tsv_line in edits_tsv_reader:
            remaining_hashes.add(tsv_line.split("\t", 1)[0])
    for file_json in os.listdir(dataset_dir):
        if not (file_json.endswith('.json.gz') and 'train' in file_json):
            continue
        dataset_file = os.path.join(dataset_dir, file_json)
        with gzip.open(dataset_file, 'r') as f_in, open(os.path.join(target_path, target_file), "a") as tsv:
            writer = csv.writer(tsv, delimiter='\t', lineterminator='\n')
            for num_done_examples, example in enumerate(f_in):
                example = json.loads(example)
                for line in example["text"].split("\n"):
                    line_md5 = hashlib.md5(line.encode("utf-8")).hexdigest()
                    if line_md5 in remaining_hashes:
                        writer.writerow([line_md5, line])
                        remaining_hashes.remove(line_md5)
            if not remaining_hashes:
                    break
            logger.info(f"Done {edits_tsv_path}")
                

                        

with WorkerPool(n_jobs=os.cpu_count()) as pool:
    category_data = pool.map(get_target, edits_tsv_list, progress_bar=True)
