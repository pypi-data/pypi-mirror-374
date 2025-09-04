import numpy as np

def ScoS(y_true, y_pred, method="linear", factor=1):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    pred_range = len(np.unique(np.concatenate([y_true, y_pred])))

    if pred_range == 0:
        return 1
    
    diff = np.abs(y_true - y_pred)

    if method == "linear":
        weighted = diff
        factor = 1
    elif method == "quadratic":
        weighted = diff**2
        factor = 2
    elif method == "sqrt":
        weighted = diff**0.5
        factor = 0.5
    elif method == "custom":
        weighted = diff**factor
    else:
        raise ValueError(f'Method "{method}" is not supported, please choose between "linear", "quadratic", "sqrt" or "custom"')
    
    score = weighted.mean()

    normalized_score = score ** (1/factor) / pred_range

    goodness_score = 1 - normalized_score
    
    return goodness_score # from 0 (worst fit) to 1 (perfect fit)
