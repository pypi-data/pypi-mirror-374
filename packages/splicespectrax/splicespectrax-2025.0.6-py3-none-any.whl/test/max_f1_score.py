import pandas as pd
import os

# Define the path to your directory containing the folders
directory_path = '/data/salomonis2/LabFiles/Kairavee/oncosplice-KT/AltAnalyze3-Oncosplice/clean_evals/runs_version2_7k_events/'

# Define the order of mutations
mutation_order = ['MLL_fusions', 'U2AF1-S34_variants', 'CBFB-MYH11_fusions', 'PML-RARA_fusions', 'U2AF1-Q157_variants', 'ZRSR2_variants', 'RUNX1_fusions', 'SF3B1_variants', 'SRSF2-P95-Deletion', "no_mutation"]  # Provide your specific order

# Initialize an empty dictionary to store max F1 scores for each mutation
max_f1_scores = {}

all_folders = os.listdir(directory_path)
all_folders.remove('.DS_Store')

# Iterate over each folder in the directory
for folder in all_folders:
    folder_path = os.path.join(directory_path, folder)

    # Check if the current item is a directory
    if os.path.isdir(folder_path):
        file_path = os.path.join(folder_path, "f1_scores_results_nomutations_removed1.csv")

        # Check if the file "f1_scores.csv" exists in the current folder
        if os.path.exists(file_path):
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path)

            # Iterate over each unique mutation in the first column
            for mutation in df['Ground_Truth'].unique():
                # Find the maximum F1 score for the current mutation
                max_f1 = df[df['Ground_Truth'] == mutation]['F1_Score'].max()

                # Update the dictionary with the maximum F1 score for the current mutation
                max_f1_scores[mutation] = max_f1

# Create a DataFrame to store the final results
    final_df = pd.DataFrame(columns=['mutation', 'max_f1'])
    df_path = os.path.join(folder_path, "final_max_f1_scores_no_mutations.csv")
# Populate the DataFrame with the mutations and their corresponding maximum F1 values
    for mutation in mutation_order:
        if mutation in max_f1_scores:
            final_df = final_df.append({'mutation': mutation, 'max_f1': max_f1_scores[mutation]}, ignore_index=True)
            # Write the DataFrame to a CSV file named "final_max_f1_scores.csv"
            final_df.to_csv(df_path, index=False)

