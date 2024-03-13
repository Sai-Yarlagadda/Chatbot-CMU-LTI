with open('rag_with_reranker_answers_testset.txt', 'r', encoding='utf-8') as f:
    pred_ans = f.read().replace('\n', ' ').split('==================')
with open('system_output_3.txt', 'w', encoding='utf-8') as f:
    for i in range(len(pred_ans)):
        print(i)
        f.write(f'{pred_ans[i].strip()}\n')
