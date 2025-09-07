# -*- coding: utf-8 -*-
# Copyright (c) 2025 University Medical Center Göttingen, Germany.
# All rights reserved.
#
# Patent Pending: DE 10 2024 112 939.5
# SPDX-License-Identifier: LicenseRef-Proprietary-See-LICENSE
#
# This software is licensed under a custom license. See the LICENSE file
# in the root directory for full details.
#
# **Commercial use is prohibited without a separate license.**
# Contact MBM ScienceBridge GmbH (https://sciencebridge.de/en/) for licensing.


import os.path
from typing import Union, List

import types
import numpy as np

import pandas as pd
from tqdm import tqdm as tqdm

from sarcasm.structure import Structure
from sarcasm.motion import Motion


class MultiStructureAnalysis:
    """
    Class for multi-tif-file comparison of structure.

    Parameters
    ----------
    list_files : list
        List of tif files.
    folder : str
        Path to a folder to store data and results.
    experiment : str, optional
        Name of the experiment (default is None).
    load_data : bool, optional
        Whether to load the dataframe from previous analysis from the data folder (default is False).
    **conditions : dict
        Keyword arguments with regex functions to extract information from the filename.

    Attributes
    ----------
    folder : str
        Path to the folder with data and results.
    experiment : str
        Name of the experiment.
    files : list
        List of tif files.
    conditions : dict
        Keyword arguments with regex functions to extract information from the filename.
    data : pandas.DataFrame
        DataFrame to store the structure data.
    """

    def __init__(self, list_files: List, folder: str, experiment: str = None, load_data: bool = False, **conditions):
        self.folder = folder
        self.experiment = experiment
        self.files = list_files
        self.conditions = conditions
        self.data = pd.DataFrame

        if load_data:
            self.load_data()

    def get_data(self, structure_keys=None):
        """
        Iterate files and get structure data.

        Parameters
        ----------
        structure_keys : list, optional
            List of keys to extract structure data (default is None).

        Returns
        -------
        None
        """
        self.data = []
        for i, tif_file in enumerate(tqdm(self.files)):
            try:
                sarc_obj = Structure(file_path=tif_file)
                dict_i = Export.get_structure_dict(sarc_obj, structure_keys,
                                                   experiment=self.experiment,
                                                   **self.conditions)
                self.data.append(dict_i)
            except Exception as e:
                print(f'{tif_file} failed!')
                print(repr(e))

        self.data = pd.DataFrame.from_records(self.data)
        self.save_data()

    def save_data(self):
        """
        Save the DataFrame to the data folder.

        Returns
        -------
        None
        """
        self.data.to_pickle(self.folder + 'data_structure.pd')

    def load_data(self):
        """
        Load the DataFrame from the data folder.

        Returns
        -------
        None

        Raises
        ------
        FileExistsError
            If the data file does not exist in the specified folder.
        """
        if os.path.exists(self.folder + 'data_structure.pd'):
            self.data = pd.read_pickle(self.folder + 'data_structure.pd')
        else:
            raise FileExistsError('Data from previous analysis does not exist and cannot be loaded. '
                                  'Set load_data=False.')

    def export_data(self, file_path, format='.xlsx'):
        """
        Export the DataFrame to .xlsx or .csv format.

        Parameters
        ----------
        file_path : str
            Path to the output file.
        format : str, optional
            Format of the output file ('.xlsx' or '.csv') (default is '.xlsx').

        Returns
        -------
        None
        """
        _data = self.data.applymap(Export.flatten_single)
        if format == '.xlsx':
            _data.to_excel(file_path, index=False)
        elif format == '.csv':
            _data.to_csv(file_path, index=False)
        else:
            raise ValueError('Unsupported file format')


class MultiLOIAnalysis:
    """
    Class for multi-LOI comparison.

    Parameters
    ----------
    list_lois : list
        List of tuples containing tif file paths and LOI names.
    folder : str
        Path to a folder to store data and results.
    load_data : bool, optional
        Whether to load the dataframe from previous analysis from the folder (default is False).
    **conditions : dict
        Keyword arguments with regex functions to extract information from the filename.

    Attributes
    ----------
    folder : str
        Path to the folder with data and results.
    lois : list
        List of tuples containing tif file paths and LOI names.
    conditions : dict
        Keyword arguments with regex functions to extract information from the filename.
    data : pandas.DataFrame
        DataFrame to store the motion data.
    """

    def __init__(self, list_lois, folder, load_data=False, **conditions):
        self.folder = folder
        self.lois = list_lois
        self.conditions = conditions
        self.data = None

        if load_data:
            self.load_data()

    def get_data(self, loi_keys=None):
        """
        Iterate files and get motion data.

        Parameters
        ----------
        loi_keys : list, optional
            List of keys to extract motion data (default is None).

        Returns
        -------
        None
        """
        self.data = []
        for tif_file, loi_name in tqdm(self.lois):
            try:
                motion_obj = Motion(tif_file, loi_name)
                dict_i = Export.get_motion_dict(motion_obj, loi_keys, **self.conditions)
                self.data.append(dict_i)
            except Exception as e:
                print(f'{tif_file}, {loi_name} failed!')
                print(repr(e))

        self.data = pd.DataFrame.from_records(self.data)
        self.save_data()

    def save_data(self):
        """
        Save the DataFrame to the data folder as a pandas DataFrame.

        Returns
        -------
        None
        """
        self.data.to_pickle(self.folder + 'data_motion.pd')

    def load_data(self):
        """
        Load the DataFrame from the data folder.

        Returns
        -------
        None

        Raises
        ------
        FileExistsError
            If the data file does not exist in the specified folder.
        """
        if os.path.exists(self.folder + 'data_motion.pd'):
            self.data = pd.read_pickle(self.folder + 'data_motion.pd')
        else:
            raise FileExistsError('Data from previous analysis does not exist and cannot be loaded. '
                                  'Set load_data=False.')

    def export_data(self, file_path, format='.xlsx'):
        """
        Export the DataFrame to .xlsx or .csv format.

        Parameters
        ----------
        file_path : str
            Path to the output file.
        format : str, optional
            Format of the output file ('.xlsx' or '.csv') (default is '.xlsx').

        Returns
        -------
        None
        """
        _data = self.data.applymap(Export.flatten_single)
        if format == '.xlsx':
            _data.to_excel(file_path, index=False)
        elif format == '.csv':
            _data.to_csv(file_path, index=False)
        else:
            raise ValueError('Unsupported file format')


class Export:
    """
    A class used to export structure and motion data from SarcAsM and Motion objects.

    Attributes
    ----------
    structure_keys_default : list
        Default structure keys.
    motion_keys_default : list
        Default motion keys.
    """

    structure_keys_default = ['cell_mask_area', 'cell_mask_area_ratio', 'cell_mask_intensity',
                              'domain_area_mean', 'domain_area_std', 'domain_oop_mean',
                              'domain_oop_std', 'domain_slen_mean', 'n_domains',
                              'myof_length_max', 'myof_length_mean', 'myof_length_std',
                              'myof_bending_mean', 'myof_bending_std',
                              'myof_straightness_mean', 'myof_straightness_std',
                              'sarcomere_area', 'sarcomere_area_ratio', 'sarcomere_length_mean',
                              'sarcomere_length_std', 'sarcomere_oop', 'n_zbands', 'n_mbands', 'n_vectors',
                              'z_intensity_mean', 'z_intensity_std', 'z_lat_alignment_mean',
                              'z_lat_alignment_std', 'z_lat_dist_mean', 'z_lat_dist_std', 'z_lat_length_groups_mean',
                              'z_lat_neighbors_mean', 'z_lat_neighbors_std', 'z_length_max',
                              'z_length_mean', 'z_length_std', 'z_oop', 'z_mask_area', 'z_mask_area_ratio',
                              'z_mask_intensity', 'z_straightness_mean', 'z_straightness_std']

    motion_keys_default = ['beating_rate', 'beating_rate_variability', 'contr_max', 'contr_max_avg', 'elong_max',
                           'elong_max_avg', 'equ', 'time', 'vel_contr_max', 'vel_contr_max_avg', 'vel_elong_max',
                           'vel_elong_max_avg', 'n_sarcomeres', 'n_contr', 'ratio_nans',
                           'popping_rate_contr', 'popping_rate_sarcomeres', 'popping_rate',
                           'popping_events', 'popping_dist', 'popping_tau',
                           'popping_ks_dist_pvalue', 'popping_ks_dist_statistic', 'popping_p_dist', 'popping_p_tau',
                           'popping_ks_tau_pvalue', 'popping_ks_tau_statistic', 'time_to_peak', 'time_to_peak_avg',
                           'time_contr', 'time_quiet',
                           'corr_delta_slen', 'corr_vel',
                           'corr_delta_slen_serial', 'corr_delta_slen_mutual', 'corr_vel_serial', 'corr_vel_mutual',
                           'ratio_delta_slen_mutual_serial', 'ratio_vel_mutual_serial']

    @staticmethod
    def get_structure_dict(sarc_obj, structure_keys=None, **conditions):
        """
        Create a dictionary of structure and metadata features from a SarcAsM object.

        Parameters
        ----------
        sarc_obj : SarcAsM
            Object of SarcAsM class or Motion class.
        structure_keys : list, optional
            List of structure keys (default is None).
        conditions : kwargs
            Keyword arguments to add information to the dictionary (e.g., "cell_line"= "wt", "info_xyz"=42).

        Returns
        -------
        dict
            Dictionary containing selected metadata and structure features.
        """
        metadata_dict = sarc_obj.metadata.to_dict()
        if structure_keys is None:
            structure_keys = Export.structure_keys_default
        missing_structure_keys = [key for key in structure_keys if key not in sarc_obj.data]
        if missing_structure_keys:
            print('Missing structure keys: ', missing_structure_keys)
        dict_structure_select = {key: sarc_obj.data.get(key, np.nan) for key in structure_keys}
        dict_ = {**metadata_dict, **dict_structure_select}
        for condition, value in conditions.items():
            if isinstance(value, types.FunctionType):
                dict_[condition] = value(sarc_obj.file_path)
            else:
                dict_[condition] = value
        return dict_

    @staticmethod
    def export_structure_data(file_path, sarc_obj: Union[Structure, Motion], structure_keys=None, remove_arrays=True,
                              fileformat='.xlsx'):
        """
        Export structure data to a file.

        Parameters
        ----------
        file_path : str
            Path to the output file.
        sarc_obj : SarcAsM
            Object of SarcAsM class.
        structure_keys : list, optional
            List of structure keys (default is None).
        remove_arrays : bool, optional
            If True, removes columns with array data (default is True).
        fileformat : str, optional
            Format of the output file (default is '.xlsx').
        """
        structure_dict = Export.get_structure_dict(sarc_obj, structure_keys=structure_keys)
        structure_df = pd.DataFrame(structure_dict)
        if remove_arrays:
            structure_df = Export.remove_arrays_dataframe(structure_df)
        if fileformat == '.xlsx':
            structure_df.to_excel(file_path)
        elif fileformat == '.csv':
            structure_df.to_csv(file_path)
        elif fileformat == '.xml':
            structure_df.to_xml(file_path)

    @staticmethod
    def remove_arrays_dataframe(df):
        """
        Remove columns with array data from a DataFrame.

        Parameters
        ----------
        df : pandas.DataFrame
            Input DataFrame.

        Returns
        -------
        pandas.DataFrame
            DataFrame with array columns removed.
        """
        df_reduced = df.copy()
        for key in df.keys():
            if isinstance(df[key][0], np.ndarray):
                df_reduced.drop(key, axis=1, inplace=True)
        return df_reduced

    @staticmethod
    def flatten_single(x):
        """Return the lone element if x is a 1-element list/ndarray; otherwise x."""
        if isinstance(x, (list, np.ndarray)) and len(x) == 1:
            return x[0]
        return x

    @staticmethod
    def get_motion_dict(motion_obj, loi_keys=None, concat=False, **conditions):
        """
        Create a dictionary of motion features and metadata from a Motion object.

        Parameters
        ----------
        motion_obj : Motion
            Object of Motion class for LOI analysis.
        loi_keys : list, optional
            List of LOI keys (default is None).
        concat : bool, optional
            If True, all 2D arrays will be concatenated to 1D arrays (default is False).
        conditions : kwargs
            Keyword arguments to add to the dictionary, can be any information, e.g., drug='ABC'.

        Returns
        -------
        dict
            Dictionary containing selected metadata and motion features.
        """
        metadata_dict = motion_obj.metadata.to_dict()
        if loi_keys is None:
            loi_keys = Export.motion_keys_default
        missing_loi_keys = [key for key in loi_keys if key not in motion_obj.loi_data]
        if missing_loi_keys:
            print('Missing loi keys: ', missing_loi_keys)
        dict_loi_select = {key: motion_obj.loi_data[key] if key in motion_obj.loi_data else np.nan for key in loi_keys}
        dict_ = {**metadata_dict, **dict_loi_select, 'loi_name': motion_obj.loi_name}
        for condition, value in conditions.items():
            if isinstance(value, types.FunctionType):
                dict_[condition] = value(motion_obj.file_path)
            else:
                dict_[condition] = value
        if concat:
            for key, value in dict_.items():
                if isinstance(value, np.ndarray):
                    if len(value.shape) == 2:
                        dict_[key] = np.concatenate(value)
        dict_['tif_name'] = motion_obj.file_path
        return dict_

    @staticmethod
    def export_motion_data(mot_obj: Motion, file_path, motion_keys=None, remove_arrays=True, fileformat='.xlsx'):
        """
        Export motion data to a file.

        Parameters
        ----------
        mot_obj : Motion
            Object of Motion class.
        file_path : str
            Path to the output file.
        motion_keys : list, optional
            List of motion keys (default is None).
        remove_arrays : bool, optional
            If True, removes columns with array data (default is True).
        fileformat : str, optional
            Format of the output file (default is '.xlsx').
        """
        motion_dict = Export.get_motion_dict(mot_obj, loi_keys=motion_keys)
        motion_df = pd.DataFrame(motion_dict)
        if remove_arrays:
            motion_df = Export.remove_arrays_dataframe(motion_df)
        if fileformat == '.xlsx':
            motion_df.to_excel(file_path)
        elif fileformat == '.csv':
            motion_df.to_csv(file_path)
        else:
            raise ValueError('Unsupported file format')
