"""
reference: https://storageclwsprod1.blob.core.windows.net/bundles/0x6b567e1cf2e041ec80d7098f031c5c9e/contents.gz?se=2024-03-12T03%3A01%3A59Z&sp=rt&sv=2019-12-12&sr=b&rscd=inline%3B%20filename%3D%22evaluate-v2.0.py%22&rsce=gzip&rsct=text/x-python&sig=L68GoD7aDWB84B206a9jxqrn3wMvEshepkr2IEWXsQg%3D
"""
import collections
import re
import string

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
    return text.lower()
  return white_space_fix(remove_articles(remove_punc(lower(s))))

def get_tokens(s):
  if not s: return []
  return normalize_answer(s).split()

def compute_exact(a_gold, a_pred):
  return int(normalize_answer(a_gold) == normalize_answer(a_pred))

def compute_f1(a_gold, a_pred):
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

  return f1, precision, recall


if __name__ == '__main__':
  generated_answers_path = 'rag_with_reranker_with_multiquery_answers.txt'
  correct_answers_path = 'answers.txt'

  tot_f1 = tot_precision = tot_recall = exact_match =0
  with open(generated_answers_path, 'r') as f:
    pred_ans = f.read().replace('\n', '').split('==================')

  with open(correct_answers_path, 'r') as f:
    corr_ans = f.readlines()

  with open('eval_for_reranker_with_multiquery_answers.txt', 'w') as out_file:
    for i in range(len(corr_ans)):

        reference_answers = corr_ans[i].strip().split(';')
        best_f1 = 0
        best_precision_val = 0
        best_recall = 0
        for reference_answer in reference_answers:
          f1, prec, rec = compute_f1(reference_answer, str(pred_ans[i]))
          if f1 >= best_f1:
            best_f1 = f1
            best_precision_val = prec
            best_recall = rec
        f1 = best_f1
        prec = best_precision_val
        rec = best_recall

        '''f1, prec, rec = compute_f1(str(corr_ans[i]), str(pred_ans[i]))'''
        tot_f1 += f1
        tot_precision += prec
        tot_recall += rec
        ex_mtch = compute_exact(corr_ans[i], pred_ans[i])
        exact_match+=ex_mtch
        out_file.write(f'Predicted answer: {pred_ans[i]}\nCorrect answer: {corr_ans[i]}\nf1: {f1}\nPrecision: {prec}\nRecall: {rec}\nExact Match: {ex_mtch}\n===========\n')

  
  f1 = tot_f1 / len(pred_ans)
  precision = tot_precision / len(pred_ans)
  recall = tot_recall / len(pred_ans)
  print(f'Average F1: {f1}')
  print(f'Average precision: {precision}')
  print(f'Average recall: {recall}')
  print(f'Exact Match: {exact_match}')
