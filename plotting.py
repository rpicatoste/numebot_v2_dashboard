from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict

# Generate a consistent color map
colors = px.colors.qualitative.Plotly  # Plotly default qualitative colors


def plot_model_performances(perf_dfs: Dict[str, pd.DataFrame]):

    all_models = [key for key in perf_dfs.keys()]
    model_color_map = {model_name: colors[i % len(colors)] 
                       for i, model_name in enumerate(all_models)}

    # Create subplot structure
    fig = make_subplots(rows=3, cols=1, 
                        row_heights=[3,1,1],
                        shared_xaxes=True)

    date_col = 'roundResolveTime'
    
    # PLOT NORMALIZED PAYOUT
    plot_col = 'payout_norm'
    row = 1

    # Iterate over sw_versions to plot uptime traces for the first subplot
    for model_name, model_df in perf_dfs.items():
        fig.add_trace(
            go.Scatter(
                x=model_df[date_col],
                y=model_df[plot_col],
                mode='lines+markers',
                name=f'{model_name}',
                line=dict(color=model_color_map[model_name])
            ),
            row=row, col=1
        )

    # Horizontal red dashed line at 0 
    fig.add_hline(y=0, line=dict(color="Red", width=1, dash="dash"), row=row, col=1)
    # Add a vertical red line for the current time with a "Now" label at the top
    current_time = datetime.now()
    fig.add_vline(x=current_time, line=dict(color="Red", width=3), row=row, col=1)
    fig.add_annotation(x=current_time, y=1, yref="paper", text="Now", showarrow=False,
                       xanchor="center", yanchor="bottom", font=dict(color="Red"), yshift=10)

    # PLOT CORR
    plot_col = 'corr20V2'
    row = 2

    for model_name, model_df in perf_dfs.items():
        fig.add_trace(
            go.Scatter(
                x=model_df[date_col],
                y=model_df[plot_col],
                mode='lines+markers',
                name=f'{model_name}',
                showlegend=False,
                line=dict(color=model_color_map[model_name])
            ),
            row=row, col=1
        )
    fig.add_vline(x=current_time, line=dict(color="Red", width=3), row=row, col=1)
    fig.add_hline(y=0, line=dict(color="Red", width=1, dash="dash"), row=row, col=1)

    # PLOT MMC
    plot_col = 'mmc'
    row = 3

    for model_name, model_df in perf_dfs.items():
        fig.add_trace(
            go.Scatter(
                x=model_df[date_col],
                y=model_df[plot_col],
                mode='lines+markers',
                name=f'{model_name}',
                showlegend=False,
                line=dict(color=model_color_map[model_name])
            ),
            row=row, col=1
        )
    fig.add_hline(y=0, line=dict(color="Red", width=1, dash="dash"), row=row, col=1)
    fig.add_vline(x=current_time, line=dict(color="Red", width=3), row=row, col=1)

    # COMMON
    # Layout adjustments
    fig.update_layout(
        title=f'Models performances',

        yaxis_title='Normalized payout',
        yaxis2_title='Corr20v2',
        yaxis3_title='MMC',

        xaxis=dict(showgrid=True),
        xaxis2=dict(showgrid=True),
        xaxis3=dict(showgrid=True),
        
        xaxis3_tickangle=-20,  # Rotate x-axis labels

        legend=dict(x=1.05, y=1),  # Place legend to the right
        height=900  # Set the height of the figure
    )
    
    return fig
