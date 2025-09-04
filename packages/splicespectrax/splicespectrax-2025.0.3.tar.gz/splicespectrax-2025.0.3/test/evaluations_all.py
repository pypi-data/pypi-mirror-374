import os
import pandas as pd
import numpy as np
from sklearn.metrics import f1_score

ground_truth_file = "/Users/tha8tf/MyProjects/Leucegene-positive-controls-F1.xlsx"
real_clusters = pd.read_excel(ground_truth_file, header=0, index_col=0)



main_folders = ["/Users/tha8tf/MyProjects/testsOncosplice/all_evals/all_defaults_rank_None_force_broad_off", "/Users/tha8tf/MyProjects/testsOncosplice/all_evals/all_defaults_rank_None_force_broad_on", "all_defaults_rank_30_force_broad_off", "all_defaults_rank_30_force_broad_on"]
# main_folders = ["force_broad_on_rank_30_efficient", "force_broad_on_rank_30_og_code"]
results = []  # To store F1 scores

for main_folder in main_folders:
    for round_folder in ["Round1", "Round2", "Round3"]:
        round_clusters_file = os.path.join(main_folder, round_folder, "round_clusters.txt")
        round_clusters = pd.read_csv(round_clusters_file, sep="\t", index_col=0)  # Adjust the separator if needed
        round_clusters = round_clusters.loc[real_clusters.index, :]

        round_results = []  # To store F1 scores for the current round

        for k in range(np.shape(real_clusters)[1]):
            for i in range(np.shape(round_clusters)[1]):
                y_true = real_clusters.iloc[:, k]
                y_pred = round_clusters.iloc[:, i]
                f1 = f1_score(y_true, y_pred)
                print(f"F1 Score for {real_clusters.columns.values[k]} vs. {round_clusters.columns.values[i]}: {f1}")

                round_results.append({
                    "Ground_Truth": real_clusters.columns.values[k],
                    "Generated_Cluster": round_clusters.columns.values[i],
                    "Round": round_folder,
                    "F1_Score": f1
                })

        results.append(round_results)


# Save the F1 scores to a CSV file in the main folder
output_file = "f1_scores_results.csv"
output_df = pd.DataFrame([result for round_result in results for result in round_result])
output_df.to_csv(os.path.join(main_folders[1], output_file), index=False)