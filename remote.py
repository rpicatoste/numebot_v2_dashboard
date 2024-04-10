from functools import lru_cache
import pandas as pd


def load_models_table_remote() -> pd.DataFrame:

    print('Working with public data only: No local models_table.csv.')
    model_names = pd.Series([f'RPICA_{n+1}' for n in range(10)], name='model_name')
    models_df = pd.DataFrame(index=model_names)
    models_df['start'] = pd.to_datetime('2024-03-01')

    return models_df


@lru_cache(1)
def local_running():
    """
    Decide if we are running locally
    """
    
    try:
        from numebot_v2.values import MODELS_TABLE_PATH
        return True
    except:
        return False
