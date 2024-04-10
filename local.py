import pandas as pd 

from numebot_v2.values import MODELS_TABLE_PATH


def load_models_table_local() -> pd.DataFrame:
    models_df = pd.read_csv(MODELS_TABLE_PATH, 
                        index_col='model_name', 
                        parse_dates=['start', 'end'])

    # Function to lookup the val_sharpe value of the parent model
    def lookup_parent_sharpe(row, col):
        if row['parent'] is not None and not pd.isna(row['parent']):
            parent_sharpe = models_df.loc[models_df.index == row['parent'], col].values[0]
            return parent_sharpe
        else:
            return row[col]

    # Apply the function to correct the val_sharpe column.
    cols = ['val_sharpe', 'val_max_drawdown', 'val_corr_mean', 'val_corr_std', 'val_mmc_mean', 'val_mmc_std', ]
    for col in cols:
        models_df[col] = models_df.apply(lambda row: lookup_parent_sharpe(row, col), axis=1)

    return models_df
