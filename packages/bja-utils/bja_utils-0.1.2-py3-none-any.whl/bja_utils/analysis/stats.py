import pandas as pd

def get_statsmodels_linear_model_results(fitted_model, terms_to_ignore=None):
    """
    Returns a DataFrame with 4 results from each linear model for each level of the covariates:
        1. Effect size
        2. p-value
        3. Confidence interval (2.5%, low)
        4. Confidence interval (97.5%, high)

    The returned df can be added to a list for concatenation into a final long-form dataframe of all features.
    """

    results = []
    for variable, value in fitted_model.params.items():
        if terms_to_ignore is not None and variable in terms_to_ignore:
            continue
        results.append({'type': 'effectsize', 'variable': variable, 'value': value})

    for variable, value in fitted_model.pvalues.items():
        if terms_to_ignore is not None and variable in terms_to_ignore:
            continue
        results.append({'type': 'pval', 'variable': variable, 'value': value})

    ci = fitted_model.conf_int()
    for variable, value in ci[0].items():
        if terms_to_ignore is not None and variable in terms_to_ignore:
            continue
        results.append({'type': 'ci_low', 'variable': variable, 'value': value})
    for variable, value in ci[1].items():
        if terms_to_ignore is not None and variable in terms_to_ignore:
            continue
        results.append({'type': 'ci_high', 'variable': variable, 'value': value})

    return pd.DataFrame(results)