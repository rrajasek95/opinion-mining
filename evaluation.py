from data import get_annotated_examples_with_opinions
from pipeline import Pipeline

import re
from collections import defaultdict

LEXICON = [
    'pizza',
    'gnocchi',
    'bruschetta',
    'gelato',
    'lasagna'
]

def compute_accuracy(partial, error):
    if (partial + error) > 0:
        return partial / (partial + error)
    else:
        return 0

def compute_metrics(hypotheses, references):
    
    exact_matches = 0
    inexact_matches = 0

    exact_match_false_positives = 0
    exact_match_false_negatives = 0

    inexact_match_false_positives = 0
    inexact_match_false_negatives = 0

    # We can define exact and inexact variants of 
    # precision and recall
    # that allow us to capture complete and partial matches

    assert len(hypotheses) == len(references), "The lengths of hypothees and references differ!"

    for h, r in zip(hypotheses, references):
        num_current_exact_matches = 0
        num_current_inexact_matches = 0

        num_current_hypotheses_items = 0
        num_current_reference_items = 0
        for item in LEXICON:
            hypotheses_opinions = set(h[item])
            reference_opinions = set(r[item])

            num_current_hypotheses_items += len(hypotheses_opinions)
            num_current_reference_items += len(reference_opinions)

            for h_opinion in hypotheses_opinions:
                for r_opinion in reference_opinions:
                    if h_opinion == r_opinion:
                        num_current_exact_matches += 1
                    if h_opinion in r_opinion:
                        num_current_inexact_matches += 1
        exact_matches += num_current_exact_matches
        inexact_matches += num_current_inexact_matches

        exact_match_false_positives += num_current_hypotheses_items - num_current_exact_matches
        inexact_match_false_positives += num_current_hypotheses_items - num_current_inexact_matches
        
        exact_match_false_negatives += num_current_reference_items - num_current_exact_matches
        inexact_match_false_negatives += num_current_reference_items - num_current_inexact_matches

    exact_precision = 0.
    exact_recall = 0.

    inexact_precision = 0.
    inexact_recall = 0.

    exact_precision = compute_accuracy(exact_matches, exact_match_false_positives)
    exact_recall = compute_accuracy(exact_matches, exact_match_false_negatives)

    inexact_precision = compute_accuracy(inexact_matches, inexact_match_false_positives)
    inexact_recall = compute_accuracy(inexact_matches, inexact_match_false_negatives)
    
    print(f"Exact Precision {exact_precision} | Exact Recall {exact_recall}")
    print(f"Inexact Precision {inexact_precision} | Inexact Recall {inexact_recall}")
    


def prepare_references(references):
    processed_refs = []
    opinion_pattern = re.compile("\((.*?), (.*?)\)")
    for _, opinion_target_pairs in references:
        d = defaultdict(list)
        if isinstance(opinion_target_pairs, str):            
            for match in re.finditer(opinion_pattern, opinion_target_pairs):
                opinion = match.group(1)
                item = match.group(2)

                for lex_item in LEXICON:
                    if lex_item in item:
                        d[lex_item].append(opinion)
                        break
        processed_refs.append(d)

    return processed_refs

if __name__ == "__main__":
    references = get_annotated_examples_with_opinions()

    filtered_refs = []

    for i in range(len(references)):
        if i > 0 and references[i][0] == references[i - 1][0]:
            continue
        else:
            filtered_refs.append(references[i])

    texts = [ref[0] for ref in filtered_refs]
    processed_refs = prepare_references(filtered_refs)

    pipeline = Pipeline()

    hypotheses = pipeline.extract_descriptions(texts)

    compute_metrics(hypotheses, processed_refs)