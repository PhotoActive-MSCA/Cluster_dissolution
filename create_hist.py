# script_2_plot_data.py
import pandas as pd
import plotly.express as px
from pathlib import Path

print("\nStarting Script 2: Plotting and Analysis...")

# --- 1. SETUP ---
# Define the main directory where the data was saved
#TODO: Uncomment and set the correct path to your data directory
#motherdir =

# --- 2. PLOT 1: DISSOLVED RATIO HISTOGRAM ---
try:
    # Read the pre-processed file for the histogram
    hist_data_path = motherdir / 'dsdata_grouped_hist.csv'
    dsdata_grouped = pd.read_csv(hist_data_path)

    # Create bins for the initial number of 'cucas'
    dsdata_grouped['num_at_zero_bins'] = pd.cut(
        dsdata_grouped['num_at_zero'],
        bins=9,
        right=False  # Intervals are [start, end)
    )

    # Calculate the ratio of dissolved clusters for each bin
    dissolved_ratio = dsdata_grouped.groupby('num_at_zero_bins')['dissolved'].mean().reset_index()
    dissolved_ratio['num_at_zero_bins_str'] = dissolved_ratio['num_at_zero_bins'].astype(str)

    # The plot shows the inverse of the dissolved ratio, i.e., the survival ratio
    dissolved_ratio['survival_ratio'] = 1 - dissolved_ratio['dissolved']

    # Create the interactive bar chart using Plotly
    fig1 = px.bar(
        dissolved_ratio,
        x='num_at_zero_bins_str',
        y='survival_ratio',
        labels={
            "num_at_zero_bins_str": "Binned 'num_at_zero' (Initial Cluster Size)",
            "survival_ratio": "Survival Ratio"
        },
        title="Cluster Survival Ratio vs. Initial Size"
    )
    fig1.update_layout(
        xaxis_title="Initial Cluster Size (Binned)",
        yaxis_title="Survival Ratio",
        yaxis_range=[0, 1],
        xaxis={'categoryorder': 'category ascending'}
    )
    fig1.show()
    print("Displayed Plot 1: Survival Ratio Histogram.")

except FileNotFoundError:
    print(f"Error: Could not find the histogram data file at '{hist_data_path}'")
except Exception as e:
    print(f"An error occurred during Plot 1 generation: {e}")

# --- 3. PLOT 2: FRACTION OF DECLINE SCATTER PLOT ---
try:
    # Read the reduced (formerly filtered) data
    reduced_data_path = motherdir / 'dsdata_reduced.csv'
    dsdata_reduced = pd.read_csv(reduced_data_path)

    # Determine the outcome for each cluster
    # Find the 'numcuc' at the last observed frame for each cluster
    idx_of_max_frame = dsdata_reduced.groupby(['experiment', 'cluster'])['frame'].idxmax()
    last_numcuc_df = dsdata_reduced.loc[idx_of_max_frame, ['experiment', 'cluster', 'numcuc']]

    # A cluster is considered "declined" if its final 'numcuc' is <= 60
    last_numcuc_df['declined'] = (last_numcuc_df['numcuc'] <= 60).astype(int)

    # Merge the outcome back into the main reduced dataframe
    dsdata_with_outcome = pd.merge(
        dsdata_reduced,
        last_numcuc_df[['experiment', 'cluster', 'declined']],
        on=['experiment', 'cluster']
    )

    # Calculate the fraction of decline for each 'numcuc' value observed
    decline_stats = dsdata_with_outcome.groupby('numcuc')['declined'].agg(['mean', 'count']).reset_index()
    decline_stats.rename(columns={'mean': 'fraction_decline', 'count': 'observations', 'numcuc': 'cucas'}, inplace=True)

    # Create the interactive scatter plot using Plotly
    fig2 = px.scatter(
        decline_stats,
        x='cucas',
        y='fraction_decline',
        hover_data=['observations'],
        labels={
            "cucas": "Number of Cucas",
            "fraction_decline": "Fraction of Decline"
        },
        title="Fraction of Decline vs. Number of Cucas"
    )

    fig2.update_layout(
        yaxis_range=[0, 1.05]  # Y-axis from 0 to 1
    )
    fig2.update_traces(marker=dict(size=8))
    fig2.show()
    print("Displayed Plot 2: Fraction of Decline Scatter Plot.")

except FileNotFoundError:
    print(f"Error: Could not find the reduced data file at '{reduced_data_path}'")
except Exception as e:
    print(f"An error occurred during Plot 2 generation: {e}")

print("Script 2 finished.")
