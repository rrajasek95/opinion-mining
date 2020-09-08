
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

    