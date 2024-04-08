import pandas as pd


def load_fake_dataframe():
    df = pd.DataFrame(index=[f'RPICA_{n+1}' for n in range(10)])
    df['start'] = pd.to_datetime('2024-03-01')

    return df


def local_running():
    """
    Decide if we are running locally
    """
    
    try:
        from numebot_v2.values import MODELS_TABLE_PATH
        print('Module imported correctly: Running locally')
    except:
        
        print('IN REMOTE; no models table will work')

    return False
