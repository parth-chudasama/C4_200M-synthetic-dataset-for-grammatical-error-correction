import spacy
from glob import glob
from tqdm import tqdm
import errant
import json
import os
from mpire import WorkerPool


annotator = errant.load('en')


def tokenize(sent):
    doc = nlp(sent)
    tok = [i.text for i in doc]
    return " ".join(tok)

target_pairs = glob("/home/parth.chudasama/data_mnt/target_pairs/*")
edit_dir = "/home/parth.chudasama/data_mnt/edits_json_data"


def get_edits(src, trg):
    src_tok, trg_tok = annotator.parse(src), annotator.parse(trg) 

    edits = annotator.annotate(src_tok, trg_tok)

    src_tok = " ".join([str(i) for i in src_tok])
    trg_tok = " ".join([str(i) for i in trg_tok])
    edit_list = []
    for item in edits:
        e_dict = {}
        e_dict['o_start'] = item.o_start
        e_dict['o_end'] =  item.o_end
        e_dict['o_str'] = item.o_str
        e_dict['e_start'] = item.c_start
        e_dict['e_end']  = item.c_end
        e_dict['repl'] = item.c_str
        e_dict['tag'] =  item.type
        edit_list.append(e_dict)
    temp = {"src": src_tok, "trg": trg_tok, "edits":edit_list}
    return temp

# for item in target_pairs[:1]:
def generate_data(target_file_path):   
    count = 0
    out_file = os.path.join(edit_dir, "edits_" +os.path.basename(target_file_path).split("_",2)[-1])
    sentences = []
    with open(target_file_path) as f:
        for line in f:
            src, trg = line.strip("\n").split("\t",1)
            sentences.append((src, trg))

    with open(f'{out_file}.jsonl', 'w') as outfile:
        for src, trg in tqdm(sentences):
            temp = get_edits(src, trg)
            json.dump(temp, outfile)
            outfile.write('\n')



# generate_data(target_pairs[0])

with WorkerPool(n_jobs=3) as pool:
    data = pool.map(generate_data, target_pairs, progress_bar=True)
