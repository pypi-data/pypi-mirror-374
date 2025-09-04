import numpy as np

def ScoS(y_true, y_pred, method="linear", factor=1):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    pred_range = max(max(y_true), max(y_pred)) - min(min(y_true), min(y_pred))
    
    diff = np.abs(y_true - y_pred)

    if method == "linear":
        weighted = diff
        score_max = pred_range
    elif method == "quadratic":
        weighted = diff**2
        score_max = pred_range**2
    elif method == "sqrt":
        weighted = diff**0.5
        score_max = pred_range**0.5
    elif method == "custom":
        weighted = diff**factor
        score_max = pred_range**factor
    else:
        raise ValueError(f'Method "{method}" is not supported, please choose between "linear", "quadratic", "sqrt" or "custom"')
    
    score = weighted.mean()

    normal_score = score/score_max

    goodness_score = 1 - normal_score
    
    return goodness_score # from 0 (worst predictions) to 1 (perfect)
