from langchain.evaluation import ExactMatchStringEvaluator

def exact_match(generated_answers_path, correct_answers_path):
    """This is a function that calculates the exact match of 
    generated answer and correct answers"""

    evaluator = ExactMatchStringEvaluator(ignore_case=True, ignore_punctuation=True)
    with open(generated_answers, 'r') as generated_answers:
        gen_answers = generated_answers.readlines()
    
    with open(correct_answers, 'r') as correct_answers:
        corr_answers = correct_answers.readlines()
    
    exact_match_scores = 0

    for i in range(len(gen_answers)):
        scores = evaluator.evaluate_strings(
            prediction=gen_answers[i],
            reference=corr_answers[i],
        )
        exact_match_scores += int(scores['score'])

    return exact_match_scores

def precision(reference, test):
    """
    Calculate the precision based on the generated answer and the correct answer
    """
    if not hasattr(reference, "intersection") or not hasattr(test, "intersection"):
        raise TypeError("reference and test should be sets")

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

    if len(reference) == 0:
        return None
    else:
        return len(reference.intersection(test)) / len(reference)

def F1score(generated_answers_path, correct_answers_path):
    """
    Calculating the F1 score based on precision and recall
    F1 = (2 * precision_val * recall_val) / (precision_val + recall_val)
    """

    with open(generated_answers_path, 'r') as file:
        generated_answers = file.readlines()
    
    with open(correct_answers_path, 'r') as file:
        correct_answers = file.readlines()
    
    for i in range(len(generated_answers)):
        gen_answer_set = set(generated_answers[i])
        correct_answer_set = set(correct_answers[i])
        precision_val = precision(gen_answer_set, correct_answer_set)
        recall_val = recall(gen_answer_set, correct_answer_set)
        F1score = (2 * precision_val * recall_val) / (precision_val + recall_val)
        return F1score

if __name__ == '__main__':
    generated_answers_path = 'path to generated answers'
    correct_answers_path = 'path to correct answers'

    exact_match_score = exact_match(generated_answers_path,
                                    correct_answers_path)
    
    f1_score = F1score(generated_answers_path, correct_answers_path)
