# Reference (https://github.com/neubig/util-scripts/blob/master/paired-bootstrap.py)

import numpy as np
import collections
import re
import string


def eval_preproc(data):
  ''' Preprocess into the appropriate format for a particular evaluation type '''
  
  return data.strip()

def normalize_answer(s):
  """Lower text and remove punctuation, articles and extra whitespace."""
  def remove_articles(text):
    regex = re.compile(r'\b(a|an|the)\b', re.UNICODE)
    return re.sub(regex, ' ', text)
  def white_space_fix(text):
    return ' '.join(text.split())
  def remove_punc(text):
    exclude = set(string.punctuation)
    return ''.join(ch for ch in text if ch not in exclude)
  def lower(text):
    #print(text)
    return text.lower()
  return white_space_fix(remove_articles(remove_punc(lower(s))))

def get_tokens(s):
  if not s: return []
  return normalize_answer(s).split()

def eval_measure(a_gold, a_pred):
  ''' Evaluation measure
  
  This takes in gold labels and system outputs and evaluates their
  accuracy. It computes the F1 score

  :param gold: the correct labels
  :param sys: the system outputs
  :param eval_type: The type of evaluation to do (acc, pearson, bleu, bleu_detok)
  '''

  gold_toks = get_tokens(a_gold)
  pred_toks = get_tokens(a_pred)
  common = collections.Counter(gold_toks) & collections.Counter(pred_toks)

  if not common:
    f1 = 0
    precision = 0
    recall = 0

  else:
    num_same = sum(common.values())
    if len(gold_toks) == 0 or len(pred_toks) == 0:
        # If either is no-answer, then F1 is 1 if they agree, 0 otherwise
        return int(gold_toks == pred_toks)
    if num_same == 0:
        return 0
    precision = 1.0 * num_same / len(pred_toks)
    recall = 1.0 * num_same / len(gold_toks)
    f1 = (2 * precision * recall) / (precision + recall)

  return f1

  #return int(normalize_answer(a_gold) == normalize_answer(a_pred))

def eval_with_paired_bootstrap(gold, sys1, sys2,
                               num_samples=10000, sample_ratio=0.5):
  ''' Evaluate with paired boostrap

  This compares two systems, performing a significance tests with
  paired bootstrap resampling to compare the accuracy of the two systems.
  
  :param gold: The correct labels
  :param sys1: The output of system 1
  :param sys2: The output of system 2
  :param num_samples: The number of bootstrap samples to take
  :param sample_ratio: The ratio of samples to take every time
  :param eval_type: The type of evaluation to do (acc, pearson, bleu, bleu_detok)
  '''

  print(len(gold))
  sys1 = sys1[:-1]
  sys2 = sys2[:-1]
  print(len(sys1))
  print(len(sys2))
  #print(sys1)
  assert(len(gold) == len(sys1))
  assert(len(gold) == len(sys2))
  
  
  # Preprocess the data appropriately for they type of eval
  gold = [eval_preproc(x) for x in gold]
  sys1 = [eval_preproc(x) for x in sys1]
  sys2 = [eval_preproc(x) for x in sys2]

  sys1_scores = []
  sys2_scores = []
  wins = [0, 0, 0]
  n = len(gold)
  ids = list(range(n))

  for _ in range(num_samples):
    # Subsample the gold and system outputs
    reduced_ids = np.random.choice(ids,int(len(ids)*sample_ratio),replace=True)
    reduced_gold = [gold[i] for i in reduced_ids]
    reduced_sys1 = [sys1[i] for i in reduced_ids]
    reduced_sys2 = [sys2[i] for i in reduced_ids]
    # Calculate accuracy on the reduced sample and save stats
    sys1_score_temp = 0
    sys2_score_temp = 0
    for i in range(len(reduced_gold)):
      sys1_score_temp += eval_measure(reduced_gold[i], reduced_sys1[i])
      sys2_score_temp += eval_measure(reduced_gold[i], reduced_sys2[i])
    #sys1_score = eval_measure(reduced_gold, reduced_sys1)
    #sys2_score = eval_measure(reduced_gold, reduced_sys2)
    sys1_score = sys1_score_temp / len(reduced_gold)
    sys2_score = sys2_score_temp / len(reduced_gold)
    if sys1_score > sys2_score:
      wins[0] += 1
    elif sys1_score < sys2_score:
      wins[1] += 1
    else:
      wins[2] += 1
    sys1_scores.append(sys1_score)
    sys2_scores.append(sys2_score)

  # Print win stats
  wins = [x/float(num_samples) for x in wins]
  print('Win ratio: sys1=%.3f, sys2=%.3f, tie=%.3f' % (wins[0], wins[1], wins[2]))
  if wins[0] > wins[1]:
    print('(sys1 is superior with p value p=%.3f)\n' % (1-wins[0]))
  elif wins[1] > wins[0]:
    print('(sys2 is superior with p value p=%.3f)\n' % (1-wins[1]))

  # Print system stats
  sys1_scores.sort()
  sys2_scores.sort()
  print('sys1 mean=%.3f, median=%.3f, 95%% confidence interval=[%.3f, %.3f]' %
          (np.mean(sys1_scores), np.median(sys1_scores), sys1_scores[int(num_samples * 0.025)], sys1_scores[int(num_samples * 0.975)]))
  print('sys2 mean=%.3f, median=%.3f, 95%% confidence interval=[%.3f, %.3f]' %
          (np.mean(sys2_scores), np.median(sys2_scores), sys2_scores[int(num_samples * 0.025)], sys2_scores[int(num_samples * 0.975)]))

if __name__ == "__main__":
  # execute only if run as a script
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('gold', help='File of the correct answers')
  parser.add_argument('sys1', help='File of the answers for system 1')
  parser.add_argument('sys2', help='File of the answers for system 2')
  parser.add_argument('--num_samples', help='Number of samples to use', type=int, default=10000)
  args = parser.parse_args()
  
  with open(args.gold, 'r', encoding='utf-8') as f:
    gold = f.readlines()
  with open(args.sys1, 'r', encoding='utf-8') as f:
    sys1 = f.read().replace('\n', ' ').split('==================')
  with open(args.sys2, 'r', encoding='utf-8') as f:
    sys2 = f.read().replace('\n', ' ').split('==================')
  eval_with_paired_bootstrap(gold, sys1, sys2, num_samples=args.num_samples)
