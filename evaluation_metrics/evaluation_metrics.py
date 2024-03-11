from langchain.evaluation import ExactMatchStringEvaluator
import string

def exact_match(generated_answers_path, correct_answers_path):
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
        print(f'generated_Answer is : {gen_answers[i]}')
        print(f'given answer is: {corr_answers[i]}')
        m = int(scores['score'])
        print(f'scores is {m}')
        print('============================')
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
    for i in range(len(reference)):

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
    print(generated_answers[176])
    print(len(correct_answers))
    with open('comp-genanswers-corranswers.txt', 'w') as file:
        for i in range(len(generated_answers)):
            if i==176:
                break
            gen_answer_set = set(generated_answers[i])
            correct_answer_set = set(correct_answers[i])
            precision_val = precision(correct_answer_set, gen_answer_set)
            recall_val = recall(correct_answer_set, gen_answer_set)

            try:
                f1score = (2 * float(precision_val) * float(recall_val)) / (float(precision_val) + float(recall_val))
            except:
                f1score = 0

            file.write(f'The precision val is {precision_val}\n')
            file.write(f'The recall val is {recall_val}\n')
            file.write(f'generated_Answer is : {generated_answers[i]}\ngiven answer is: {correct_answers[i]}\nf1score is {f1score}\n===========\n')
            final_f1+=f1score
    return final_f1/len(correct_answers)

if __name__ == '__main__':
    generated_answers_path = 'rag_with_reranker_answers.txt'
    correct_answers_path = 'answers.txt'

    '''exact_match_score = exact_match(generated_answers_path,
                                    correct_answers_path)
    
    f1_score = f1(correct_answers_path, generated_answers_path)'''

    f1_score = f1('answers.txt', 'rag_with_reranker_answers.txt')
    #print(exact_match_score)
    print(f1_score)


'''generated_answers_file = 'rag_with_reranker_answers.txt'
with open(generated_answers_file, 'r') as generated_answers_file:
        gen_answers = generated_answers_file.read().split('==================')
for x, i in enumerate(gen_answers):
    print(x)
    print(i)'''
