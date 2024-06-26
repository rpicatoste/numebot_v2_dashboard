import streamlit as st

from data import get_models_performances, load_models_table, process_models_performances
from plotting import plot_model_performances
from styling import style_models_table_for_showing


st.set_page_config(layout="wide")

st.write("""
# Numerai central dashboard
Models and performances
""")

show_benchmarks = st.checkbox("Show benchmark models", value=False)

models_df = load_models_table(add_benchmark_models=show_benchmarks)
perf_dfs = get_models_performances(models_df)

# Calculate performances
models_df = process_models_performances(models_df, perf_dfs)

# Show table
styled_df = style_models_table_for_showing(models_df)
st.dataframe(styled_df)

# Show charts
fig = plot_model_performances(perf_dfs=perf_dfs)
st.plotly_chart(fig, use_container_width=True)
