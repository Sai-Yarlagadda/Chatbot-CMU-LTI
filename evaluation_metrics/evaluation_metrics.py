from langchain.evaluation import ExactMatchStringEvaluator
import string

def exact_match(correct_answers_path, generated_answers_path):
    """This is a function that calculates the exact match of 
    generated answer and correct answers"""

    evaluator = ExactMatchStringEvaluator(ignore_case=True, ignore_punctuation=True)
    with open(generated_answers_path, 'r') as generated_answers:
        gen_answers = generated_answers.read().split('==================\n')
    
    with open(correct_answers_path, 'r') as correct_answers:
        corr_answers = correct_answers.readlines()

    exact_match_scores = 0

    for i in range(len(gen_answers)):
        scores = evaluator.evaluate_strings(
            prediction=gen_answers[i],
            reference=corr_answers[i],
        )
        exact_match_scores += int(scores['score'])

    
    return exact_match_scores

def remove_punctuation(text):
    """
    Remove punctuations from the input text
    """
    return text.translate(str.maketrans("", "", string.punctuation))

def precision(reference, test):
    """
    Calculate the precision based on the generated answer and the correct answer
    """
    if not hasattr(reference, "intersection") or not hasattr(test, "intersection"):
        raise TypeError("reference and test should be sets")
   
    #remove punctuation 
    reference = set(remove_punctuation(word) for word in reference)
    test = set(remove_punctuation(word) for word in test)

    #remove case sensitivity
    reference = set(remove_punctuation(word.lower()) for word in reference)
    test = set(remove_punctuation(word.lower()) for word in test)

    if len(test) == 0:
        return None
    else:
        return len(reference.intersection(test)) / len(test)

def recall(reference, test):
    """
    Calculate the recall based on generated answer and the correct answer
    """
    if not hasattr(reference, "intersection") or not hasattr(test, "intersection"):
        raise TypeError("reference and test should be sets")


    #remove punctuation 
    reference = set(remove_punctuation(word) for word in reference)
    test = set(remove_punctuation(word) for word in test)

    #remove case sensitivity
    reference = set(remove_punctuation(word.lower()) for word in reference)
    test = set(remove_punctuation(word.lower()) for word in test)

    if len(reference) == 0:
        return None
    else:
        return len(reference.intersection(test)) / len(reference)


def f1(reference_path, test_path):
    """
    Calculating the F1 score based on precision and recall
    F1 = (2 * precision_val * recall_val) / (precision_val + recall_val)
    """

    with open(test_path, 'r') as file:
        generated_answers = file.read().replace('\n', '').split('==================')
    
    with open(reference_path, 'r') as file:
        correct_answers = file.readlines()

    final_f1 = 0
    final_precision = 0
    final_recall = 0

    with open('comp-genanswers-corranswers.txt', 'w') as file:
        for i in range(len(generated_answers)):
            if not generated_answers[i].strip():
                continue

            reference_answers = correct_answers[i].strip().split(';')
            best_f1_score = 0
            best_precision_val = 0
            best_recall_val = 0

            for reference_answer in reference_answers:
                gen_answer_set = set(generated_answers[i])
                correct_answer_set = set(reference_answer)

                precision_val = precision(correct_answer_set, gen_answer_set)
                recall_val = recall(correct_answer_set, gen_answer_set)

                try:
                    f1score = (2 * float(precision_val) * float(recall_val)) / (float(precision_val) + float(recall_val))
                
                except ZeroDivisionError:
                    f1score = 0

                if f1score > best_f1_score:
                    best_f1_score = f1score
                    best_precision_val = precision_val
                    best_recall_val = recall_val

            file.write(f'The best F1 score is {best_f1_score}\n')
            file.write(f'Precision: {best_precision_val}, Recall: {best_recall_val}\n')
            file.write(f'generated_Answer is : {generated_answers[i]}\ngiven answer is: {correct_answers[i]}\n===========\n')
            final_f1 += best_f1_score
            final_precision += best_precision_val
            final_recall += best_recall_val
    
    f1_score_complete_data = final_f1 / len(correct_answers)
    precision_complete_data = final_precision / len(correct_answers)
    recall_complete_data = final_recall / len(correct_answers)
    return f1_score_complete_data, precision_complete_data, recall_complete_data

if __name__ == '__main__':
    generated_answers_path = 'rag_with_reranker_answers.txt'
    correct_answers_path = 'answers.txt'

    f1_score = f1(correct_answers_path, generated_answers_path)
    print(f1_score)

if __name__ == '__main__':
    generated_answers_path = 'rag_with_reranker_answers.txt'
    correct_answers_path = 'answers.txt'

    exact_match_score = exact_match('answers.txt', 'rag_with_reranker_answers.txt')
    
    '''f1_score = f1(correct_answers_path, generated_answers_path)'''

    f1_score = f1('answers.txt', 'rag_with_reranker_answers.txt')
    print(exact_match_score)
    print(f1_score)
