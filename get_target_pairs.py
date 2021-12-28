from glob import glob
import os
from mpire import WorkerPool
from tqdm import tqdm

target_sentences_path_list = sorted(glob("/home/parth.chudasama/data_mnt/target_data/*"))
edits_tsv_path_list = sorted(glob("/mnt/spellcheck_data/data/c4dataset/edits_tsv/*"))
output_tsv_base = "/home/parth.chudasama/data_mnt/target_pairs"


def get_edits(edits_tsv_reader):
  """Generator method for the edits."""
  current_edit_md5 = None
  for edits_tsv_line in edits_tsv_reader:
    try:
      edit_md5, byte_start, byte_end, text = edits_tsv_line.strip("\n").split(
          "\t", 3)
    except ValueError:
      pass  # Skip malformed lines
    else:
      if edit_md5 != current_edit_md5:
        if current_edit_md5 is not None:
          yield current_edit_md5, current_edits
        current_edit_md5 = edit_md5
        current_edits = []
      current_edits.append((int(byte_start), int(byte_end), text))
  yield current_edit_md5, current_edits


def apply_edits(edits, target_text):
  target_bytes = target_text.encode("utf-8")
  last_byte_position = 0
  source_text = ""
  for byte_start, byte_end, replacement_text in edits:
    source_text += target_bytes[last_byte_position:byte_start].decode("utf-8")
    source_text += replacement_text
    last_byte_position = byte_end
  source_text += target_bytes[last_byte_position:].decode("utf-8")
  return source_text


def load_targets(path):
  data = {}
  with open(path) as f:
    for target_sentence_tsv_line in f:
          md5, target_text = target_sentence_tsv_line.strip("\n").split("\t", 1)
          data.update({md5:target_text})
  print("Done loading")
  return data


def make_pair(edits_path, target_path):
        output_tsv_path = os.path.join(output_tsv_base,"target_pairs_" + edits_path.split("-",1)[-1])
        print(f"Current path: {output_tsv_path}")
        target_dict = load_targets(target_path)
        with open(edits_path) as edits_tsv_reader, \
             open(output_tsv_path, "w") as output_tsv_writer:
                edits_iterator = get_edits(edits_tsv_reader)
                try:
                  for edit_md5, edits in edits_iterator:
                    try: 
                      target_text = target_dict[edit_md5]
                      try:
                        source_text = apply_edits(edits, target_text)
                      except:
                        continue
                      output_tsv_writer.write("%s\t%s\n" % (source_text, target_text))
                    except KeyError:
                      pass
                except StopIteration:
                    pass


list_path = list(zip(edits_tsv_path_list, target_sentences_path_list))

for i in tqdm(list_path):
    make_pair(i[0],i[1])





