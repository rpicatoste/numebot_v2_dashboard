from datetime import timedelta
from typing import Dict
import numerapi
import pandas as pd
import streamlit as st
import time


from remote import local_running

interesting_cols = [
    'corr20V2',
    'mmc',
    'roundNumber',
    'payout_norm', 'payout', 'selectedStakeValue', 'roundPayoutFactor',
    'roundOpenTime', 'roundResolveTime', 'roundResolved',
]

def get_models_performances(models_df: pd.DataFrame):

    napi = numerapi.NumerAPI(verbosity="info")

    start = time.time()
    perf_dfs = {}
    for model_name, model_data in models_df.iterrows():
        perf_dfs[model_name] = get_model_performance(model_data, napi)

    delay = time.time() - start
    print(f'Time {delay:.3f} sec')
    
    return perf_dfs


@st.cache_data(ttl=900) #15 min
def get_model_performance(model_data: pd.Series, _napi: numerapi.NumerAPI):
    model_name = model_data.name

    model_perf_dict = _napi.round_model_performances(model_name.lower())
    perf_df = pd.DataFrame(model_perf_dict)

    model_start_tz = model_data['start'].tz_localize('UTC')
    filt_start = perf_df['roundOpenTime'] > (model_start_tz - timedelta(days=2))
    perf_df = perf_df[filt_start]

    perf_df['payout_norm'] = get_normalized_payout(
        corr20V2=perf_df['corr20V2'],
        mmc=perf_df['mmc'],
        round_payout_factor=perf_df['roundPayoutFactor'].astype(float)
    )
    
    return perf_df[interesting_cols]


def get_normalized_payout(
    corr20V2: pd.Series, mmc: pd.Series, round_payout_factor: pd.Series
):

    # From https://docs.numer.ai/numerai-tournament/staking
    # payout = stake * clip(payout_factor * (corr * 0.5 + mmc * 2), -0.05, 0.05) 
    payout_norm = round_payout_factor * (corr20V2 * 0.5 + mmc * 2.0)
    payout_norm = payout_norm.clip(-0.5, 0.5)

    return payout_norm


def load_models_table() -> pd.DataFrame:
    try:
        from numebot_v2.values import MODELS_TABLE_PATH
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

    except:
        print('Loading numebot failed!')
        from remote import load_fake_dataframe
        models_df = load_fake_dataframe()

    return models_df


def process_models_performances(models_df: pd.DataFrame, perf_dfs: Dict[str, pd.DataFrame]):
    
    if not local_running():
        return models_df
    
    # Put calculated cols first
    new_cols = [
        'n_res',
        'res_payout_norm_mean', 'res_payout_norm_std',
        'unres_payout_norm_mean', 'unres_payout_norm_std',
        'res_corr_mean', 'res_corr_std',
        'res_mmc_mean', 'res_mmc_std',
        'val_sharpe', 'val_max_drawdown', 'val_corr_mean', 'val_corr_std', 'val_mmc_mean', 'val_mmc_std',
    ]
    non_repeating_cols = [col for col in models_df.columns if col not in new_cols]
    ordered_cols = new_cols + non_repeating_cols
    
    for model_name, perf_df in perf_dfs.items():
        
        # Resolved rounds performance
        filt_res = perf_df['roundResolved'] & ~perf_df['corr20V2'].isna()
        
        models_df.at[model_name, 'n_res'] = filt_res.sum()
        
        res_payout_norm = get_normalized_payout(
            corr20V2=perf_df[filt_res]['corr20V2'],
            mmc=perf_df[filt_res]['mmc'],
            round_payout_factor=perf_df[filt_res]['roundPayoutFactor'].astype(float)
        )

        models_df.at[model_name, 'res_payout_norm_mean'] = res_payout_norm.mean()
        models_df.at[model_name, 'res_payout_norm_std'] = res_payout_norm.std()
        models_df.at[model_name, 'res_corr_mean'] = perf_df[filt_res]['corr20V2'].mean()
        models_df.at[model_name, 'res_corr_std'] = perf_df[filt_res]['corr20V2'].std()
        models_df.at[model_name, 'res_mmc_mean'] = perf_df[filt_res]['mmc'].mean()
        models_df.at[model_name, 'res_mmc_std'] = perf_df[filt_res]['mmc'].std()

        # Unresolved rounds performance
        filt_unres = ~perf_df['corr20V2'].isna()
        
        unres_payout_norm = get_normalized_payout(
            corr20V2=perf_df[filt_unres]['corr20V2'],
            mmc=perf_df[filt_unres]['mmc'],
            round_payout_factor=perf_df[filt_unres]['roundPayoutFactor'].astype(float)
        )

        models_df.at[model_name, 'unres_payout_norm_mean'] = unres_payout_norm.mean()
        models_df.at[model_name, 'unres_payout_norm_std'] = unres_payout_norm.std()
        models_df.at[model_name, 'unres_corr_mean'] = perf_df[filt_unres]['corr20V2'].mean()
        models_df.at[model_name, 'unres_corr_std'] = perf_df[filt_unres]['corr20V2'].std()
        models_df.at[model_name, 'unres_mmc_mean'] = perf_df[filt_unres]['mmc'].mean()
        models_df.at[model_name, 'unres_mmc_std'] = perf_df[filt_unres]['mmc'].std()


    models_df['n_res'] = models_df['n_res'].astype(int)

    return models_df[ordered_cols].copy()
