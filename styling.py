import pandas as pd


def style_models_table_for_showing(models_df: pd.DataFrame):
    colored_cols = ['val_sharpe', 'val_corr_mean', 'val_mmc_mean',
                    'res_corr_mean', 'res_mmc_mean', 'res_payout_norm_mean', 'unres_payout_norm_mean',]

    reversed_color_cols = ['val_max_drawdown', 'val_corr_std', 'val_mmc_std',
                           'res_corr_std', 'res_mmc_std', 'res_payout_norm_std', 'unres_payout_norm_std',]

    hide_cols = [
        'res_corr_mean', 'res_mmc_mean', 
        'res_corr_std', 'res_mmc_std',
    ]

    show_cols = [col for col in models_df.columns if col not in hide_cols]
    colored_cols = [col for col in colored_cols if col in show_cols]
    reversed_color_cols = [col for col in reversed_color_cols if col in show_cols]

    # Rename cols
    renaming = {
        'unres_payout_norm_mean': 'Unres Payout mean',
        'unres_payout_norm_std': 'Unres Payout std',
        'res_payout_norm_mean': 'Res Payout mean',
        'res_payout_norm_std': 'Res Payout std',
    }
    models_df.rename(renaming, axis='columns', inplace=True)
    show_cols = [renaming.get(col, col) for col in show_cols]
    colored_cols = [renaming.get(col, col) for col in colored_cols]
    reversed_color_cols = [renaming.get(col, col) for col in reversed_color_cols]

    cmap = 'YlGn' # 'RdYlBu_r'
    styled_df = models_df[show_cols].style\
                    .background_gradient(cmap=cmap, subset=colored_cols)\
                    .background_gradient(cmap=cmap+'_r', subset=reversed_color_cols)

    return styled_df
