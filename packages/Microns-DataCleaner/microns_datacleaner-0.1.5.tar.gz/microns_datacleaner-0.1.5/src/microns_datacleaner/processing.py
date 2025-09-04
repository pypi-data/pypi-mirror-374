import numpy as np
import pandas as pd
import logging
from standard_transform import minnie_ds
from scipy.stats import circmean
from tqdm import tqdm

LAYER_CELL_TYPES = {
    'L1': ['NGC', 'BPC', 'MC', 'BC'],
    'L2/3': ['23P'],
    'L4': ['4P'],
    'L5': ['5P-IT', '5P-ET', '5P-NP'],
    'L6': ['6P-IT', '6P-CT'],
    'WM': ['Oligo', 'OPC', 'Pericyte'],
}
"""Dictionary, whose keys are LAYER_ORDER. Each element includes a list with the cell types in each layer"""

LAYER_ORDER = ['L1', 'L2/3', 'L4', 'L5', 'L6', 'WM']
"""Names of the layers."""

def merge_columns(nucleus_df, table, columns=None, method="nucleus_id", how='left'):
    """
    General function to add new columns to the nucleus table in a flexible way. 

    Parameters:
    -----------
        nucleus_df: pandas.DataFrame
             The primary DataFrame to which new columns will be added.
        table: pandas.DataFrame
            The source DataFrame from which to pull the new columns.
        columns: list[str] or None, optional
            A list of column names from `table` to merge into `nucleus_df`.
            If None (default), all columns from `table` are used.
        method: str 
            How the tables will be compared to each other. If 'nucleus_id' (default), the target_id 
            is matched to the nucleus_id. If 'functional', the session, scan and unit_id are compared. 
            If 'pt_root_id', merge by 'pt_root_id'. This last option is not adviced, unless is the only index available.
        how: str
            Equivalent to Panda's how argument for the merge function. Only 'inner' or 'left' are allowed, since the 
            new columns are always added into the nucleus table.
   
    Returns:
    --------
        pandas.DataFrame
            The merged DataFrame, containing the original columns from 'nucleus_df'
            plus the selected columns from 'table', with temporary/duplicate join
            columns removed.	
    """

    # Things must be merged into the unit/nucleus table. Any other merge is not permitted
    if how == 'right':
        raise ValueError("'how' can be only 'left' or 'inner' for this operation.")

    # When columns are not specified, insert all the columns from the second table
    if columns is None:
        columns = list(table.columns)

    # Select over which column we will match the tables 
    if method == 'nucleus_id':
        left_col  = ['nucleus_id']
        right_col = ['target_id']
    elif method == 'pt_root_id':
        left_col  = ['pt_root_id'] 
        right_col = ['pt_root_id'] 
    elif method == 'functional':
        left_col  = ['session', 'scan_idx', 'functional_unit_id']
        right_col = ['session', 'scan_idx', 'unit_id']

    # Do the merge over the columns we are interested in. 
    # Make sure that the columns we are merging over are included, even if user did not specify them 
    columns2merge = columns 
    for col in right_col:
        if not col in columns:
            columns2merge.append(col)

    # Merge the table tagging the columns that are common in both tables, to drop those of the second one
    merged = nucleus_df.merge(table[columns2merge], left_on=left_col, right_on=right_col, how=how, suffixes = ["", "_todrop"])

    # Remove those duplicates by selecting them to drop later 
    # First, in some methods one of the columns used to merge is still there and has to be taken out
    if method == 'nucleus_id':
        columns2drop = ['target_id']
    elif method == 'pt_root_id':
        columns2drop = []
    elif method == 'functional':
        columns2drop = ['unit_id']
    
    # Then the columns that were repeated in both tables are added to the drop list, so we can keep the one from the left one only
    for c in merged.columns:
        if c.endswith("_todrop"):
            columns2drop.append(c)

    # Return the resulting merged table 
    return merged.drop(columns=columns2drop)


def merge_nucleus_with_cell_types(nucleus_df, cell_type_df):
    """
    Merges the nucleus table with cell type classifications.

    Parameters:
    -----------
        nucleus_df: pandas.DataFrame
            The reference DataFrame containing nucleus IDs and positions.
        cell_type_df: pandas.DataFrame
            The DataFrame containing cell type classifications.
        
    Returns:
    --------
        pandas.DataFrame
            A new DataFrame containing the merged data.
    """
    
    # Check data validity
    if nucleus_df.empty or cell_type_df.empty:
        raise ValueError('Empty dataframe provided to merge_nucleus_with_cell_types')

    # Perform a merge of both tables and keep only the desired columns
    merged = merge_columns(nucleus_df, cell_type_df, columns=['classification_system', 'cell_type'], how='inner')
    return merged[['nucleus_id', 'pt_root_id', 'pt_position_x', 'pt_position_y', 'pt_position_z', 'classification_system', 'cell_type']]


def merge_brain_area(nucleus_df, areas):
    """
    Merges the nucleus table with brain area information.

    Parameters:
    -----------
        nucleus_df: pandas.DataFrame
            The reference DataFrame containing nucleus IDs.
        areas: pandas.DataFrame
            The DataFrame containing brain area classifications.
            
    Returns:
    --------
        pandas.DataFrame
            The 'nucleus_df' DataFrame, now enriched with a 'brain_area' column.
    """

    # Check data validity
    if nucleus_df.empty or areas.empty:
        raise ValueError('Empty dataframe provided to merge_brain_area')

    # Perform a merge of both tables 
    merged = merge_columns(nucleus_df, areas, columns=['tag'], how='inner')

    # Rename the column
    return merged.rename(columns={'tag' : 'brain_area'})


def merge_proofreading_status(nucleus_df, proofreading, version):
    """
    Merges proofreading status information into the nucleus table.

    Parameters:
    -----------
        nucleus_df: pandas.DataFrame
            The reference DataFrame containing nucleus and 'pt_root_id' information.
        proofreading: pandas.DataFrame
            A DataFrame containing proofreading strategies for 'pt_root_id'.
            Must include 'strategy_axon' and 'strategy_dendrite' columns.
        version: int
            The dataset version number. This parameter is currently unused in this
            function's logic but is included for future compatibility.
    
    Returns:
    --------
        pandas.DataFrame
            The 'nucleus_df' DataFrame, now including 'strategy_axon' and
            'strategy_dendrite' columns with NaN values filled.
    """

    # Check data validity
    if nucleus_df.empty:
        raise ValueError('Empty nucleus dataframe provided to merge_proofreading_status')

    # Perform a merge of both tables from the desired columns 
    merged = merge_columns(nucleus_df, proofreading, columns=['strategy_axon', 'strategy_dendrite'], method='pt_root_id', how='left')

    merged.loc[merged['strategy_axon'].isna(), 'strategy_axon']         = 'none'
    merged.loc[merged['strategy_dendrite'].isna(), 'strategy_dendrite'] = 'none'
    return merged


def merge_functional_properties(nucleus_df, functional, mode='best_only'):
    """
    Merges functional properties into the nucleus DataFrame using one of several modes.
    This function enriches a nucleus DataFrame with functional data. It operates
    in different modes to handle various use cases, such as selecting only the
    best-performing scan, including all scans, or simply matching functional IDs.

    Parameters:
    -----------
        nucleus_df: pandas.DataFrame
            The primary DataFrame with nucleus information.
        functional: pandas.DataFrame
            The source DataFrame containing functional properties.
        mode: str, optional
            Defines the merging strategy. If 'best_only' (default) it keeps only
             the top-performing scan. If 'all', it merges a comprehensive set of
            properties for all available scans. If 'match', it only merges the 
               functional identifiers to link nuclei to their scan info.
          
    Returns:
    --------
        pandas.DataFrame
            The nucleus DataFrame, now enriched with functional data according to the
            specified mode.
    """

    # Check data validity
    if nucleus_df.empty or functional.empty:
        raise ValueError('Warning: Empty dataframe provided to merge_functional_properties')

    match mode:
        # The functional table is assumed to be the Digital Twin. Only the best cases are taken
        case 'best_only':
            functional = functional.sort_values(by='cc_abs', ascending=False)
            functional = functional.drop_duplicates(subset='target_id', keep='first')
            functional = functional[['target_id', 'pt_root_id', 'pref_ori', 'pref_dir', 'gOSI', 'gDSI', 'cc_abs']]
            functional['tuning_type'] = 'matched'

        # The functional table is assumed to be the Digital Twin, but all scans remain
        case 'all':
            functional = functional[['target_id', 'pt_root_id', 'session', 'scan_idx', 'unit_id', 'pref_ori', 'pref_dir', 'gOSI', 'gDSI', 'cc_abs']]
            functional = functional.rename(columns = {'unit_id' : 'functional_unit_id'}) 
            functional['tuning_type'] = 'matched'


        # The functional table is assumed to be the coregistration table, and only the functional indices are saved
        case 'match':
            functional = functional[['target_id', 'pt_root_id', 'session', 'scan_idx', 'unit_id']] 
            functional = functional.rename(columns = {'unit_id' : 'functional_unit_id'}) 
            functional['tuning_type'] = 'matched'

    # The pt_root_id was needed just to filter potential pt root = 0, after we can drop
    functional = functional[functional['pt_root_id'] != 0]
    functional = functional.drop(columns=['pt_root_id'])

    # Do the merge
    return merge_columns(nucleus_df, functional, how='left')


def transform_positions(df, x_col='pt_position_x', y_col='pt_position_y', z_col='pt_position_z'):
    """
    Transforms positions from voxels to μm.
    
    Parameters:
    -----------
        df: pandas.DataFrame
            DataFrame with position columns to transform.
        x_col: str, optional
            Name of the x-coordinate column (default: 'pt_position_x').
        y_col: str, optional
            Name of the y-coordinate column (default: 'pt_position_y').
        z_col: str, optional
            Name of the z-coordinate column (default: 'pt_position_z').
    
    Returns:
    --------
        pandas.DataFrame
            DataFrame with transformed positions.
    """
    
    logging.debug("Transforming positions from voxels to micrometers.")
    if df.empty:
        logging.error("Empty dataframe provided to transform_positions")
        raise ValueError(f"Empty dataframe provided to transform_positions")
    
    # Check if required columns exist
    if not all(col in df.columns for col in [x_col, y_col, z_col]):
        logging.error(f"Required columns {x_col}, {y_col}, {z_col} not found in the dataframe.")
        raise ValueError(f"Required columns {x_col}, {y_col}, {z_col} not found in the dataframe")
    
    transformed_positions = np.empty((len(df), 3)) 
    
    for k, (x, y, z) in enumerate(tqdm(df[[x_col, y_col, z_col]].values, desc="Transform positions")):
        position = np.array([x, y, z])
        transformed = minnie_ds.transform_vx.apply(position)
        transformed_positions[k, :] = transformed
        
    df[x_col] = transformed_positions[:, 0]
    df[y_col] = transformed_positions[:, 1]
    df[z_col] = transformed_positions[:, 2]
    
    return df


def divide_volume_into_segments(cells_df, segment_size=10.0, threshold_L23 = 300):
    """
    Segments the brain volume along the y-axis and assigns a dominant cortical layer.
   
    Parameters:
    -----------
        cells_df: pandas.DataFrame
            A DataFrame containing cell information.
        segment_size: float, optional
            The size (height) of each segment along the y-axis in micrometers,
            by default 10.0.
        threshold_L23: int, optional
            The minimum number of L2/3 cells required in a segment to trigger the
            switch from assigning 'L1' to assigning 'L2/3' as the dominant layer,
            by default 300. This is key for defining the L1 boundary.
    
    Returns:
    --------
        pandas.DataFrame
            A new DataFrame where each row represents a y-axis segment. The columns
            include the start/end coordinates, cell counts for each layer, and the
            assigned 'dominant_layer' for that segment.
    """
    
    # Data validity
    if cells_df.empty:
        raise ValueError('Warning: Empty dataframe provided to divide_volume_into_segments')

    # Calculate the number of segments
    y_min, y_max = cells_df['pt_position_y'].min(), cells_df['pt_position_y'].max()
    num_segments = int(np.ceil((y_max - y_min) / segment_size))

    # Create bins for segmentation
    y_bins = np.linspace(y_min, y_max, num_segments + 1)

    segments = []

    l23_assigned = False

    # Process each segment
    for i in range(len(y_bins) - 1):
        y_start, y_end = y_bins[i], y_bins[i + 1]
        y_center = (y_start + y_end) / 2

        segment_cells = cells_df[(cells_df['pt_position_y'] >= y_start) & (cells_df['pt_position_y'] < y_end)]

        layer_counts = {}
        for layer_name, cell_types in LAYER_CELL_TYPES.items():
            layer_cells = segment_cells[segment_cells['cell_type'].isin(cell_types)]
            layer_counts[layer_name] = len(layer_cells)

        # Special logic for L1 and L2/3
        if not l23_assigned:
            # Count L2/3 cells
            l23_cells = layer_counts.get('L2/3', 0)

            # If L2/3 cells are less than threshold, assign L1
            if l23_cells < threshold_L23:
                dominant_layer = 'L1'
            else:
                # Once we exceed the threshold, assign L2/3 and set the flag
                dominant_layer = 'L2/3'
                l23_assigned = True
        elif any(layer_counts.values()):
            dominant_layer = max(layer_counts.items(), key=lambda x: x[1])[0]
        else:
            dominant_layer = 'Unknown'

        segments.append(
            {
                'y_start': y_start,
                'y_end': y_end,
                'y_center': y_center,
                'L1_cells': layer_counts.get('L1', 0),
                'L2/3_cells': layer_counts.get('L2/3', 0),
                'L4_cells': layer_counts.get('L4', 0),
                'L5_cells': layer_counts.get('L5', 0),
                'L6_cells': layer_counts.get('L6', 0),
                'WM_cells': layer_counts.get('WM', 0),
                'dominant_layer': dominant_layer,
            }
        )

    segments_df = pd.DataFrame(segments)

    return segments_df


def merge_segments_by_layer(segments_df):
    """
    Merge segments that belong to the same layer.
    This is useful for defining the final boundaries of each cortical layer.

    Parameters:
    -----------
        segments_df: pandas.DataFrame
            A DataFrame where each row is a y-axis segment.
         
    Returns:
    --------
        pandas.DataFrame
            A new DataFrame where each row represents a single, contiguous layer
            block.
    """

    if segments_df.empty:
        return segments_df

    layer_groups = {}
    current_layer = None
    start_idx = 0

    for i, row in segments_df.iterrows():
        layer = row['dominant_layer']

        if layer == 'Unknown' or layer == 'WM':  # Skip Unknown and White Matter
            continue

        if current_layer != layer:
            if current_layer is not None:
                if current_layer not in layer_groups:
                    layer_groups[current_layer] = []

                layer_groups[current_layer].append(
                    {
                        'y_start': segments_df.iloc[start_idx]['y_start'],
                        'y_end': segments_df.iloc[i - 1]['y_end'],
                    }
                )

            current_layer = layer
            start_idx = i

    # Handle the last segment
    if current_layer is not None and start_idx < len(segments_df):
        if current_layer not in layer_groups:
            layer_groups[current_layer] = []

        layer_groups[current_layer].append(
            {
                'y_start': segments_df.iloc[start_idx]['y_start'],
                'y_end': segments_df.iloc[len(segments_df) - 1]['y_end'],
            }
        )

    merged_layers = []
    for layer, regions in layer_groups.items():
        for i, region in enumerate(regions):
            merged_layers.append(
                {
                    'layer': layer,
                    'region_index': i,
                    'y_start': region['y_start'],
                    'y_end': region['y_end'],
                    'height': region['y_end'] - region['y_start'],
                }
            )

    merged_df = pd.DataFrame(merged_layers)

    return merged_df.sort_values('y_start')


def add_layer_info(neurons_df, segments):
    """
    Annotates a neuron DataFrame with layer information based on y-position.
    
    Parameters:
    -----------
        neurons_df: pandas.DataFrame
            The DataFrame containing neuron information, which will be modified
            in-place.
        segments: pandas.DataFrame
            A DataFrame defining the boundaries of each cortical layer.
         
    Returns:
    --------
        None
            This function does not return a value. It modifies the 'neurons_df'
            DataFrame directly.
    """
    
    if neurons_df.empty or segments.empty:
        print('Warning: Empty dataframe provided to add_layer_info')
        return

    for layer, ystart, yend in segments[['layer', 'y_start', 'y_end']].values:
        mask = (neurons_df['pt_position_y'] >= ystart) & (neurons_df['pt_position_y'] < yend)
        neurons_df.loc[mask, 'layer'] = layer
    return
