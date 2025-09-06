# import altanalyze3.components.oncosplice.main_functions as oc
import spectra.main_functions as oc


psi_file_path = '~/psi_matrix.txt'

psi, metadata = oc.read_psi_file(psi_file_path, n_metadata_cols=11)

variable_features, psi, metadata = oc.oncosplice_feature_selection(psi, metadata,
                                                                   fold_threshold=0.2, samples_differing=4,
                                                                   corr_threshold_intercorr=0.2, corr_n_events=10,
                                                                   corr_threshold=0.8, write_files=False, savedir=None)

final_clusters, de_results = oc.oncosplice(psi=psi, metadata=metadata, variable_features=variable_features,
                                           pca_corr_threshold=0.4, npcs=30, rank='k30', force_broad='on', min_group_size=5,
                                           dPSI=0.1, dPSI_p_val=0.05, min_differential_events=100,
                                           top_n_differential_events=150, conservation='stringent', depletion_corr_threshold=0.4,
                                           speed='og', n_rounds=3, write_files=False, savedir=None)

