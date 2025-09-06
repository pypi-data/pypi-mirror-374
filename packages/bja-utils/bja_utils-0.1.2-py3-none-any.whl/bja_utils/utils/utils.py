def significance_size(row, cutoff=1, pval_col='p-value', l2fc_col='Log2 fold change', pval_cutoff=0.05):
    if row[pval_col] > pval_cutoff:
        return 1
    elif abs(row[l2fc_col]) < cutoff:
        return 2
    else:
        return 3


def add_suffix_to_dupes(df, colname, first_part=' [#', second_part=']'):
    """
    Adds a ` [#1]`, ` [#2] etc. to the end of a string column if duplicates are found.

    Define the format of the added string with `first_part` and `second_part`

    Returns a new Series.
    """
    return df[colname].where(~df[colname].duplicated(keep=False),
                             df[colname].astype('str') +
                             first_part +
                             (df.groupby(colname).cumcount() + 1).astype(str) +
                             second_part)

