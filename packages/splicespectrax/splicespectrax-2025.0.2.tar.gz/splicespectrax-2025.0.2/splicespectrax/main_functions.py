from spectra.round_wrapper import *
from spectra.preprocess import *
from spectra.remove_redundancy import *
from spectra.feature_selection import *
from spectra.median_impute import *
from spectra.visualizations import *
import os
import argparse
import time
import matplotlib.pyplot as plt
import warnings

plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['font.family'] = 'Arial'


def read_psi_file(psi_file_path, n_metadata_cols):
    # read the psi file in and separate out the metadata columns from numeric PSI data
    psi, metadata = format_psi_matrix(psi_file_path, n=n_metadata_cols)
    metadata.index = psi.index
    psi = psi.dropna(how='all')
    metadata = metadata.loc[psi.index, :]

    return psi, metadata


def oncosplice_feature_selection(psi, metadata, fold_threshold, samples_differing, corr_threshold_intercorr, corr_n_events, corr_threshold, speed, write_files=True, savedir=None):
    # variance based feature selection
    metadata = variance_based_feature_selection(psi, metadata, fold_threshold=fold_threshold, samples_differing=samples_differing)

    metadata = metadata.loc[metadata['high_variance'] == True, :]
    psi = psi.loc[metadata.index, :]

    # inter-feature correlation module

    if speed == "yes":
        psi = fast_intercorrelation_based_feature_selection(psi, corr_threshold=corr_threshold_intercorr, corr_n_events=corr_n_events)

    else:
        print(
            "beginning intercorrelated based feature selection. This may take a while if input PSI file has more than 30,000 events (typical time 1 hour)...")
        psi = intercorrelation_based_feature_selection(psi, corr_threshold=corr_threshold_intercorr, corr_n_events=corr_n_events)

    psi = intercorrelation_based_feature_selection(psi, corr_threshold=corr_threshold_intercorr, corr_n_events=corr_n_events)

    metadata = metadata.loc[psi.index, :]

    # Find the non-redundant splicing events
    list_of_events = remove_redundant_splicing_events(psi, corr_threshold, metadata)
    list_of_events = list(set(list_of_events))

    # write the essential files out for future assessments
    variable_features = pd.DataFrame(list_of_events, columns=["EventID"])

    if write_files:
        variable_features.to_csv(os.path.join(savedir, "list_of_non_redundant_events.txt"), sep="\t")
        metadata.to_csv(os.path.join(savedir, "final_metadata.txt"), sep="\t")

    return variable_features, psi, metadata


def oncosplice(psi, metadata, variable_features, pca_corr_threshold, npcs, rank, force_broad, min_group_size, dPSI, dPSI_p_val, min_differential_events, top_n_differential_events, conservation, depletion_corr_threshold, speed, n_rounds, write_files, savedir):

    if rank == "k30":
        rank = 30
    else:
        rank = None
    print("NMF Rank used:")
    print(rank)

    if force_broad == "on":
        rank1 = 2
    else:
        rank1 = rank
    print("Force broad used:")
    print(rank1)

    print("number of rounds to iterate through:")
    print(n_rounds)

    # impute the psi matrix for certain downstream steps
    # formatted_psi_file_imp, metadata_imp = format_psi_matrix(imputed_psi_file_path)
    psi_imp = median_impute(psi)
    psi_imp.index = psi.index

    list_of_events = variable_features['EventID'].to_list()

    # Subset the PSI matrix to only the non-redundant events
    psi_0 = psi.loc[list_of_events, :]
    psi_imp_0 = psi_imp.loc[list_of_events, :]

    # Initialize an empty dictionaries to store DEG dataframes,
    final_clusters_dict = {}
    depleted_psi_file_after_round_imp_dict = {}
    depleted_psi_file_after_round_dict = {}
    deg_results_all_dict = {}

    print("Number of PCs used for feature selection")
    print(npcs)

    if write_files:
        os.chdir(savedir)

    # feature selection prior to Round 1

    pca_events_round = get_events_from_pca(psi_imp, psi, list_of_events, corr_threshold=pca_corr_threshold, n_components=npcs)

    print("STARING ROUND 1...")
    print("Number of events prior to entering ROUND 1: ")
    print(len(psi_0.index))

    # Round 1 OncoSplice
    final_clusters_i, depleted_psi_file_after_round_imp_i, depleted_psi_file_after_round_i, deg_results_all_i = round_wrapper(
        filename="Round1", full_psi_file=psi_0, full_imputed_psi_file=psi_imp_0, metadata=metadata,
        highly_variable_events=pca_events_round, rank=rank1, min_group_size=min_group_size, dPSI=dPSI, dPSI_p_val=dPSI_p_val,
        min_differential_events=min_differential_events, top_n_differential_events=top_n_differential_events, conservation=conservation, strictness="tough",
        depletion_corr_threshold=depletion_corr_threshold, write_files=write_files, speed_corr=speed)

    # Round i OncoSplice (tough)
    depleted_events_round_i = depleted_psi_file_after_round_i.index.to_list()

    print("Number of events removed after ROUND 1: ")
    print(len(psi_0.index) - len(depleted_psi_file_after_round_i.index))

    deg_results_all_i['cluster'] = 'R1_' + deg_results_all_i['cluster']
    # Add a meaninful prefix to all column names
    prefix = "R1_C"
    final_clusters_i = final_clusters_i.rename(columns=lambda x: prefix + str(x))

    # store the mandatory round 1 outputs in respective dictionaries
    key = "Round1"
    final_clusters_dict[key] = final_clusters_i
    # depleted_psi_file_after_round_imp_dict[key] = depleted_psi_file_after_round_imp_i
    # depleted_psi_file_after_round_dict[key] = depleted_psi_file_after_round_i
    deg_results_all_dict[key] = deg_results_all_i

    for round_j in range(2, n_rounds+1):

        # feature selection prior to Round J
        pca_events_round_j = get_events_from_pca(psi_imp, psi, depleted_events_round_i,
                                                 corr_threshold=pca_corr_threshold, n_components=npcs)

        print(f"STARING ROUND {round_j}...")
        print(f"Number of events prior to entering ROUND {round_j}: ")
        print(len(depleted_psi_file_after_round_i.index))

        # Round 2 Oncosplice
        final_clusters_j, depleted_psi_file_after_round_imp_j, depleted_psi_file_after_round_j, deg_results_all_j = round_wrapper(
            filename=f"Round{round_j}", full_psi_file=depleted_psi_file_after_round_i,
            full_imputed_psi_file=depleted_psi_file_after_round_imp_i, highly_variable_events=pca_events_round_j, metadata=metadata, rank=rank,
            min_group_size=min_group_size, dPSI=dPSI, dPSI_p_val=dPSI_p_val, min_differential_events=min_differential_events,
            top_n_differential_events=top_n_differential_events, conservation=conservation, strictness="tough",
            depletion_corr_threshold=depletion_corr_threshold, write_files=write_files, speed_corr=speed)

        # Round 3 OncoSplice
        depleted_events_round_j = depleted_psi_file_after_round_j.index.to_list()
        print(f"Number of events removed after ROUND {round_j}: ")
        print(len(depleted_psi_file_after_round_i.index) - len(depleted_psi_file_after_round_j.index))

        deg_results_all_j['cluster'] = f'R{round_j}_' + deg_results_all_j['cluster']
        # Add a meaninful prefix to all column names
        prefix = f"R{round_j}_C"
        final_clusters_j = final_clusters_j.rename(columns=lambda x: prefix + str(x))

        # store the outputs in respective dictionaries
        key = f"Round{round_j}"
        final_clusters_dict[key] = final_clusters_j
        # depleted_psi_file_after_round_imp_dict[key] = depleted_psi_file_after_round_imp_j
        # depleted_psi_file_after_round_dict[key] = depleted_psi_file_after_round_j
        deg_results_all_dict[key] = deg_results_all_j

        # reset vars for next round
        depleted_events_round_i = depleted_events_round_j
        depleted_psi_file_after_round_i = depleted_psi_file_after_round_j
        depleted_psi_file_after_round_imp_i = depleted_psi_file_after_round_imp_j

        if len(depleted_psi_file_after_round_i) < top_n_differential_events:
            warnings.warn(f"Less than 50 splicing events pending after round {round_j}. Halting further iterative clustering process...")
            break


    # final outputs
    final_clusters_all_rounds = pd.concat(final_clusters_dict.values(), axis=1)

    de_results_all_rounds = pd.concat(deg_results_all_dict.values(), axis=0, ignore_index=True)

    # Grouping by cluster assignment and type of feature, and counting occurrences
    grouped_de_df_event_annotation = de_results_all_rounds.groupby(['cluster', 'EventAnnotation']).size().unstack(fill_value=0)

    # Calculating percentage of each type of feature in each cluster
    grouped_event_annotation_percentage = grouped_de_df_event_annotation.div(grouped_de_df_event_annotation.sum(axis=1), axis=0) * 100

    # Grouping by cluster assignment and type of feature, and counting occurrences
    grouped_de_df_event_direction = de_results_all_rounds.groupby(['cluster', 'event_direction'])['ClusterID'].nunique().unstack(
        fill_value=0)

    # Calculating percentage of each type of feature in each cluster
    grouped_direction_annotation_percentage = grouped_de_df_event_direction.div(grouped_de_df_event_direction.sum(axis=1), axis=0) * 100


    if write_files:
        path = os.path.join(savedir, "FinalResults")
        os.mkdir(path)
        os.chdir(path)
        # Define color palette for the types of features
        colors = sns.color_palette("Set1")

        final_clusters_all_rounds.to_csv("MergedResults.txt", sep="\t")
        grouped_de_df_event_annotation.to_csv("event_annotations_numbers.txt", sep='\t')
        grouped_event_annotation_percentage.to_csv("event_annotations_percentage.txt", sep='\t')
        grouped_de_df_event_direction.to_csv("event_direction_numbers.txt", sep='\t')
        grouped_direction_annotation_percentage.to_csv("event_direction_percentage.txt", sep='\t')

        # Plotting horizontal stacked bar graph
        plt.figure(figsize=(10, 6))
        grouped_event_annotation_percentage.plot(kind='barh', stacked=True, color=colors)
        plt.title('Percentage of Features in Each Type by Cluster Assignment')
        plt.ylabel('Cluster Assignment')
        plt.xlabel('Percentage')
        plt.legend(title='Event Annotation')
        plt.tight_layout()  # Adjust layout to fit cleanly in PDF
        file_path = os.path.join(path, "event_annotations_percentage.pdf")
        plt.savefig(file_path, format='pdf', bbox_inches='tight')

        plt.figure(figsize=(10, 6))
        grouped_de_df_event_annotation.plot(kind='barh', stacked=True, color=colors)
        plt.title('Number of Features in Each Type by Cluster Assignment')
        plt.ylabel('Cluster Assignment')
        plt.xlabel('Number of Features')
        plt.legend(title='Event Annotation')
        plt.tight_layout()  # Adjust layout to fit cleanly in PDF
        file_path = os.path.join(path, "event_annotations_numbers.pdf")
        plt.savefig(file_path, format='pdf', bbox_inches='tight')

        # Plotting horizontal stacked bar graph
        plt.figure(figsize=(10, 6))
        grouped_direction_annotation_percentage.plot(kind='barh', stacked=True, color=colors)
        plt.title('Percentage of Cluster IDs in Each Type by Cluster/Group Assignment')
        plt.ylabel('Cluster Assignment')
        plt.xlabel('Percentage')
        plt.legend(title='Event Annotation')
        plt.tight_layout()  # Adjust layout to fit cleanly in PDF
        file_path = os.path.join(path, "event_direction_percentage.pdf")
        plt.savefig(file_path, format='pdf', bbox_inches='tight')

        plt.figure(figsize=(10, 6))
        grouped_de_df_event_direction.plot(kind='barh', stacked=True, color=colors)
        plt.title('Number of ClusterID in Each Type by Cluster Assignment')
        plt.ylabel('Cluster Assignment')
        plt.xlabel('Number of Features')
        plt.legend(title='Event Annotation')
        plt.tight_layout()  # Adjust layout to fit cleanly in PDF
        file_path = os.path.join(path, "event_direction_numbers.pdf")
        plt.savefig(file_path, format='pdf', bbox_inches='tight')

    return final_clusters_all_rounds, de_results_all_rounds


