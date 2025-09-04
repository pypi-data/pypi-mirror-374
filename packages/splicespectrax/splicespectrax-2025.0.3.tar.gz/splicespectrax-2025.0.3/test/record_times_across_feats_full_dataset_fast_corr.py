import pandas as pd
import time
from preprocess import *

def downsample_dataframe(df, start=1000, step=1000):
    num_rows = df.shape[0]
    downsampled_dfs = {}

    for i in range(start, num_rows + 1, step):
        downsampled_dfs[i] = df.sample(n=i, random_state=42).reset_index(drop=True)

    return downsampled_dfs


# Assuming `df` is your dataframe
full_psi = pd.read_csv("/Users/tha8tf/MyProjects/Hs_RNASeq_top_alt_junctions-PSI_EventAnnotation-367-Leucegene_88kevents.txt", sep="\t", index_col=0)
downsampled_dfs = downsample_dataframe(df=full_psi, start=1000, step=1000)

# calculate time required for each downsampled dataframe using the original and the faster algorithm
time_times = {}
cpu_times = {}


for num_rows, downsampled_df in downsampled_dfs.items():
    # read the psi file in and separate out the metadata columns from numeric PSI data
    formatted_psi_file = downsampled_df.iloc[:, 7:]
    metadata = downsampled_df.iloc[:, :7]
    metadata.index = formatted_psi_file.index
    formatted_psi_file = formatted_psi_file.dropna(how='all')
    metadata = metadata.loc[formatted_psi_file.index, :]

    st = time.time()
    metadata = variance_based_feature_selection(formatted_psi_file, metadata, fold_threshold=0.3, samples_differing=4)
    et = time.time()
    el_t = (et-st) / 60
    metadata = metadata.loc[metadata['high_variance'] == True, :]
    formatted_psi_file = formatted_psi_file.loc[metadata.index, :]

    st = time.time()
    downsampled_df = fast_intercorrelation_based_feature_selection(downsampled_df, corr_threshold=0.4, corr_n_events=10)
    et = time.time()
    time_times[num_rows] = et - st

    st = time.process_time()
    downsampled_df = fast_intercorrelation_based_feature_selection(downsampled_df, corr_threshold=0.4, corr_n_events=10)
    et = time.process_time()
    cpu_times[num_rows] = et - st

# make dataframe from the time and cpu times
time_df = pd.DataFrame.from_dict(time_times, orient='index', columns=['time'])
cpu_df = pd.DataFrame.from_dict(cpu_times, orient='index', columns=['cpu_time'])

# save the dataframes to csv
time_df.to_csv("time_times_fast_corr_setting5.csv")
cpu_df.to_csv("cpu_times_fast_corr_setting5.csv")
