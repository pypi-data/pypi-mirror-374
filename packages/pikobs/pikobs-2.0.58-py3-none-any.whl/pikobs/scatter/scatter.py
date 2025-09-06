"""
Description
------------

This module allows for the computation of various statistical metrics over adjustable tiles on the globe, averaged over a specified time period. These metrics include:

- **omp (Observation minus Prediction)**: The difference between observed meteorological data and model predictions.
- **oma (Observation minus Analysis)**: The difference between observed meteorological data and the analysis field.
- **des (Density)**: The density of observations within a specified region.
- **obs (Observations)**: Recorded meteorological observations from various stations.
- **bcorr (Bias Correction)**: Applicable to radiances, it represents the bias corrections applied across different datasets.

These calculations are essential for:

1. Evaluating the quality and accuracy of meteorological observations.
2. Creating detailed maps for specific meteorological experiments.
3. Generating comparative maps to analyze differences between control experiments and evaluation experiments.

Details of Calculations for a Single Experiment
-----------------------------------------------

1. **omp (Observation minus Prediction)**:
   - Shows the difference between observed meteorological data and the model-predicted field.
   - It is crucial for understanding the performance of predictive models and identifying areas where model predictions deviate from actual observations.

   .. image:: ../../../docs/source/_static/omp1.png
      :alt: omp Plot

2. **oma (Observation minus Analysis)**:
   - Similar to the 'omp' metric, but compares observations with the analysis field rather than predictions.
   - This helps in assessing how well the analysis represents the observed data.

   .. image:: ../../../docs/source/_static/oma1.png
      :alt: oma Plot

3. **obs (Observations)**:
   - Displays recorded meteorological observations from various stations.
   - A color scale is used to highlight significant observations, aiding in the detection of patterns, anomalies, and overall trends in the data.

   .. image:: ../../../docs/source/_static/obs1.png
      :alt: obs Plot

4. **dens (Density)**:
   - Visualizes the density of observations within a specified region.
   - This metric uses a color scale to indicate variations in observation density, providing a clear picture of areas with higher and lower concentrations of data.

   .. image:: ../../../docs/source/_static/dens1.png
      :alt: dens Plot

5. **bcorr (Bias Correction of Radiances)**:
   - Depicts the bias corrections applied to radiance data across different datasets.
   - The color scale in this plot shows the magnitude and direction of bias corrections, which is essential for assessing and adjusting discrepancies in radiance data.

   .. image:: ../../../docs/source/_static/bcorr1.png
      :alt: bcorr Plot

Generate Scatter for Radiance Assimilation Analysis
****************************************************

To start an interactive session for generating scatter plots, use the following qsub command:

.. code-block:: bash

    qsub -I -X -l select=4:ncpus=80:mpiprocs=80:ompthreads=1:mem=185gb -l place=scatter -l walltime=6:0:0

Generating Scatter Plots for a Single Experiment
------------------------------------------------

To generate scatter plots for a single experiment using the `pikobs` module, use the following command format:

.. code-block:: bash

    python -c 'import pikobs; pikobs.scatter.arg_call()' \

         --path_experience_files /home/dlo001/data_maestro/ppp5/maestro_archives/E22SLT50BGCK/monitoring/banco/postalt/ \

         --experience_name E22SLT50BGCK \

         --pathwork work_to_amsua_allsky_scatter_omp_version2 \

         --datestart 2022060100 \

         --dateend 2022060200 \

         --region Monde \

         --family atms_allsky \

         --flags_criteria assimilee \

         --function omp oma obs dens bcorr \

         --boxsizex 2 \

         --boxsizey 2 \

         --projection robinson \

         --id_stn all \

         --channel all \

         --n_cpu 80

Comparative Analysis Between Control and Evaluation Experiments
---------------------------------------------------------------

This section provides an overview of how to generate comparative maps to analyze differences between control and evaluation experiments. The visual representations illustrate the functionality and significance of each metric.

1. **omp (Observation minus Prediction)**:
   - Displays the difference between average meteorological observations and model-predicted fields for the specified time period across two experiments (control and experimental).
   - This plot helps in visualizing deviations between observed data and model predictions.

   .. image:: ../../../docs/source/_static/omp2.png
      :alt: omp Plot

2. **oma (Observation minus Analysis)**:
   - Illustrates the difference between average meteorological observations and the analysis field for the specified time period in both control and experimental experiments.
   - This plot aids in understanding deviations between observed data and analyzed predictions.

   .. image:: ../../../docs/source/_static/oma2.png
      :alt: oma Plot

3. **obs (Observations)**:
   - Shows average recorded meteorological observations from stations during the specified time period for both control and experimental experiments.
   - Utilizes a color scale to highlight significant observations, facilitating pattern and anomaly detection.

   .. image:: ../../../docs/source/_static/obs2.png
      :alt: obs Plot

4. **dens (Density)**:
   - Visualizes average observation density within a defined region for the specified time period across control and experimental experiments.
   - Uses a color scale to depict variations in observation density, providing insights into spatial concentration.

   .. image:: ../../../docs/source/_static/dens2.png
      :alt: dens Plot

5. **bcorr (Bias correction of radiances)**:
   - Depicts bias corrections applied to average radiance data across different datasets for the specified time period in both control and experimental experiments.
   - Displays bias correction magnitude and direction using a color scale, aiding in data quality assessment and adjustment.

   .. image:: ../../../docs/source/_static/bcorr2.png
      :alt: bcorr Plot

Generating Comparative Scatter Plots
------------------------------------

To generate comparative scatter plots between control and evaluation experiments using the `pikobs` module, use the following command format:

.. code-block:: bash

    python -c 'import pikobs; pikobs.scatter.arg_call()' \

         --path_control_files /home/dlo001/data_maestro/ppp5/maestro_archives/E22SLT50/monitoring/banco/postalt/ \

         --control_name E22SLT50 \

         --path_experience_files /home/dlo001/data_maestro/ppp5/maestro_archives/E22SLT50BGCK/monitoring/banco/postalt/ \

         --experience_name E22SLT50BGCK \

         --pathwork work_to_amsua_allsky_scatter_omp_version2 \

         --datestart 2022060100 \

         --dateend 2022060200 \

         --region Monde \

         --family atms_allsky \

         --flags_criteria assimilee \

         --function omp oma obs dens bcorr \

         --boxsizex 2 \

         --boxsizey 2 \

         --projection robinson \

         --id_stn all \

         --channel all \

         --n_cpu 80
"""
#!/usr/bin/python3

import sqlite3
import pikobs
import re
import os
from  dask.distributed import Client
import numpy as np
import sqlite3
import os
import re
import sqlite3
from datetime import datetime, timedelta
import warnings
# Suppress all Shapely deprecation warnings
warnings.filterwarnings("ignore", ".*ShapelyDeprecationWarning.*")

# Now, import the libraries you're using
import shapely
import cartopy
def create_table_if_not_exists(cursor, extra_sw):
    """
    Create the 'serie_cardio' table if it does not already exist.

    Args:
        cursor (sqlite3.Cursor): Database cursor for executing SQL queries.
    """
    query = f"""
        CREATE TABLE IF NOT EXISTS moyenne (
            Nrej INTEGER,
            Nacc INTEGER,
            Nprofile INTEGER,
            DATE INTEGER,
            lat FLOAT,
            lon FLOAT,
            boite INTEGER,
            id_stn TEXT,
            varno INTEGER,
            vcoord FLOAT,   -- INTEGER FLOAT canal
            sumx FLOAT,
            sumy FLOAT,
            sumz FLOAT,
            sumStat FLOAT,
            sumx2 FLOAT,
            sumy2 FLOAT,
            sumz2 FLOAT,
            sumStat2 FLOAT,
            n INTEGER,
            flag INTEGER
            {extra_sw}
        ); """
    cursor.execute(query)

def combine(pathfileout: str, filememory: str, extra_sw) -> None:
    """
    Combine multiple SQLite files into a single output file.

    This function copies records from the 'moyenne' table of a source SQLite file 
    (filememory) and inserts them into the 'moyenne' table of a destination/output SQLite file (pathfileout).
    
    Args:
        pathfileout (str): Path to the output SQLite file where combined data will be stored.
        filememory  (str): Path to the source SQLite file (can be memory or disk).
        
    Returns:
        None. The result is saved directly in the specified output file.
    """
    insert_sql = f"""
        INSERT INTO moyenne(
            Nrej, Nacc, Nprofile, DATE, lat, lon, boite, id_stn, varno, vcoord, sumx, sumy, sumz, 
            sumStat, sumx2, sumy2, sumz2, sumStat2, n, flag {extra_sw}
        )
        SELECT 
            Nrej, Nacc, Nprofile, DATE, lat, lon, boite, id_stn, varno, vcoord, sumx, sumy, sumz, 
            sumStat, sumx2, sumy2, sumz2, sumStat2, n, flag {extra_sw}
        FROM this_avg_db.moyenne
    """
    # Use 'with' statement to ensure connection is properly closed
    with sqlite3.connect(pathfileout, uri=True, isolation_level=None, timeout=9999) as conn:
        try:
            # Set performance-optimized PRAGMAs, provided your application allows for non-durable writes
            conn.execute("PRAGMA journal_mode=OFF;")
            conn.execute("PRAGMA synchronous=OFF;")

            # Ensure the table exists
            create_table_if_not_exists(conn, extra_sw)

            # Attach the source SQLite database
            conn.execute(f"ATTACH DATABASE '{filememory}' AS this_avg_db;")

            # Copy data
            conn.execute(insert_sql)
            conn.commit()

            # Detach the attached database
            conn.execute("DETACH DATABASE this_avg_db;")
        except sqlite3.Error as e:
            print(f"Error combining SQLite files: {e}")
            raise

def create_and_populate_moyenne_table(
    family,
    new_db_filename: str,
    existing_db_filename: str,
    selected_region,
    selected_flags, 
    FUNCTION,
    boxsizex: float,
    boxsizey: float,
    varnos,
    channel: str,
    id_stn: str,
    interval
) -> None:
    """
    Creates an in-memory 'moyenne' table from a database, then combines it into a destination database.

    Args:
        family (Any): Family code or object for pikobs.family().
        new_db_filename (str): Destination SQLite filename.
        existing_db_filename (str): Source database filename.
        selected_region (Any): Selection for pikobs.regions().
        selected_flags (Any): Flags for selection.
        FUNCTION (Any): Function/operation to use (not used in current code!).
        boxsizex (float): Longitude box size.
        boxsizey (float): Latitude box size.
        varnos (List|str): Variable numbers as list or string.
        channel (str): Channel specification ('all', 'join', etc.).
        id_stn (str): Station ID ('all', 'join', etc.).
        interval (tuple): (min, max) value for an interval (can be None).

    Returns:
        None. Populates or appends to the target database file.
    """
    # Extract 10-digit date from filename
    date_match = re.search(r'(\d{10})', existing_db_filename)
    if not date_match:
        raise ValueError("No 10-digit sequence found in the source filename.")
    date_str = date_match.group(1)

    # Prepare in-memory SQLite file
    in_memory_db = f"file::memory:?cache=shared"

    
    with sqlite3.connect(in_memory_db, uri=True, isolation_level=None, timeout=9999999) as mem_conn:
        cursor = mem_conn.cursor()

        # Extract variables from pikobs
        FAM, VCOORD, VCOCRIT, STATB, element, VCOTYP = pikobs.family(family)
        element = ",".join(varnos) if varnos else element

        # Region, latitude, longitude and flag criteria
        LAT1, LAT2, LON1, LON2 = pikobs.regions(selected_region)
        
        LATLONCRIT = pikobs.generate_latlon_criteria(LAT1, LAT2, LON1, LON2)

        flag_criteria = pikobs.flag_criteria(selected_flags)
        STNID = f"floor(360. / {boxsizex}) * floor(lat / {boxsizey}) + floor(MIN(179.99, lon) / {boxsizex})"
        LAT = f"floor(lat / {boxsizey}) * {boxsizey} + {boxsizey} / 2."
        LON = f"floor(MIN(179.99, lon) / {boxsizex}) * {boxsizex} + {boxsizex} / 2."

        # PRAGMA for performance
        cursor.execute("PRAGMA journal_mode = OFF;")
        cursor.execute("PRAGMA journal_mode = MEMORY;")
        cursor.execute("PRAGMA synchronous = OFF;")
        cursor.execute("PRAGMA foreign_keys = OFF;")
        cursor.execute(f"ATTACH DATABASE '{existing_db_filename}' AS db;")

        # Check for existence of bias_corr column
        cursor.execute("PRAGMA table_info('DATA')")
        columns = [col[1] for col in cursor.fetchall()]
        has_bias_corr = 'BIAS_CORR' in columns
          
        cursor.execute("PRAGMA table_info('HEADER')")
        columns = [col[1] for col in cursor.fetchall()]
        WIND_COMP_METHOD = 'WIND_COMP_METHOD' in columns
        extra_sw = ', WIND_COMP_METHOD' if WIND_COMP_METHOD else ''

        
        # Define SQL for GROUP BY and SELECT fields depending on channel/id_stn
        if channel == 'join' and id_stn == 'all':
            chan_select = '"join" as Chan,'
            id_stn_select = 'id_stn as id_stn,'
            group_by = f'GROUP BY 2, 3, 4, 5, id_stn {extra_sw}'
        elif channel == 'all' and id_stn == 'join':
            chan_select = f'{VCOORD} as Chan,'
            id_stn_select = '"join" as id_stn,'
            group_by = f'GROUP BY 2, 3, 4, 5, {VCOORD} {extra_sw}'
        elif channel == 'all' and id_stn == 'all':
            chan_select = f'{VCOORD} as Chan,'
            id_stn_select = 'id_stn as id_stn,'
            group_by = f'GROUP BY 2, 3, 4, 5, id_stn, {VCOORD} {extra_sw}'
        elif channel == 'join' and id_stn == 'join':
            chan_select = '"join" as Chan,'
            id_stn_select = '"join" as id_stn,'
            group_by = f'GROUP BY 2, 3, 4, 5 {extra_sw}'
        else:
            raise ValueError("Unsupported combination of channel and id_stn")

        # Interval criteria
        interval_a, interval_b = interval
        if interval_a is None and interval_b is None:
            interval_criteria = ''
            layer_label = 'layer_all'
        else:
            interval_criteria = f'AND vcoord >= {interval_a*100} AND vcoord <= {interval_b*100}'
            layer_label = f'layerfrom{interval_a}MPato{interval_b}MPa'

        sum_bias_corr = "sum(bias_corr)" if has_bias_corr else "NULL"
        sum_bias_corr2 = "sum(bias_corr * bias_corr)" if has_bias_corr else "NULL"

        # Create table moyenne if not exists
        insert_query = f"""
            CREATE TABLE IF NOT EXISTS moyenne (
                Nrej INTEGER,
                Nacc INTEGER,
                Nprofile INTEGER,
                DATE INTEGER,
                lat FLOAT,
                lon FLOAT,
                boite INTEGER,
                id_stn TEXT,
                varno INTEGER,
                vcoord FLOAT,
                sumx FLOAT,
                sumy FLOAT,
                sumz FLOAT,
                sumStat FLOAT,
                sumx2 FLOAT,
                sumy2 FLOAT,
                sumz2 FLOAT,
                sumStat2 FLOAT,
                n INTEGER,
                flag INTEGER
                {extra_sw}
            );"""
        cursor.execute(insert_query)
        # Compose query
        insert_query = f"""
        INSERT INTO moyenne (
            DATE, lat, lon, boite, varno, vcoord, 
            sumx, sumy, sumz, sumStat, 
            sumx2, sumy2, sumz2, sumStat2, 
            n, Nrej, Nacc, Nprofile, id_stn, flag  {extra_sw}

        )
        SELECT
            {date_str},
            {LAT},
            {LON},
            {STNID},
            VARNO,
            {chan_select}
            sum(omp),
            sum(oma),
            sum(obsvalue),
            {sum_bias_corr},
            sum(omp * omp),
            sum(oma * oma),
            sum(obsvalue * obsvalue),
            {sum_bias_corr2},
            COUNT(*),
            sum(flag & 512=512),
            sum(flag & 4096-4094),
            COUNT(DISTINCT id_obs),
            {id_stn_select}
            flag
            {extra_sw}
        FROM
            db.header
        NATURAL JOIN
            db.DATA
        WHERE
            varno IN ({element}) 
            AND obsvalue IS NOT NULL
            {flag_criteria}
            {LATLONCRIT}
            {VCOCRIT}
            {interval_criteria}
        {group_by};
        """
        cursor.execute(insert_query)
        mem_conn.commit()

        # Now, merge in-memory results into the output file
        try:
            combine(new_db_filename, in_memory_db, extra_sw )
        except sqlite3.Error as error:
            print(f"Error while creating a single sqlite file: {os.path.basename(in_memory_db)} -- {error}")
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

def create_data_list(
    date_start: str,
    date_end: str,
    families: List[str],
    input_paths: List[str],
    names: List[str],
    work_path: str,
    box_size_x: float,
    box_size_y: float,
    function: str,
    flag_criteria: str,
    regions: List[Any],       # adjust type if you have a region class
    varnos: List[str],
    intervals: List[Tuple[Any, Any]],
) -> List[Dict[str, Any]]:
    """
    Builds a list of dictionaries containing all configuration info 
    for data processing at 6-hour intervals, for multiple families, 
    regions, input files, and intervals.

    Args:
        date_start (str): Start date string in format 'YYYYMMDDHH'.
        date_end (str): End date string in format 'YYYYMMDDHH'.
        families (List[str]): List of family names/codes.
        input_paths (List[str]): List of input file path prefixes.
        names (List[str]): List of dataset names.
        work_path (str): Path where output databases should be created.
        box_size_x (float): Size of the box in longitude.
        box_size_y (float): Size of the box in latitude.
        function (str): Function being applied (name/purpose).
        flag_criteria (str): Flag criteria (as a code or query substring).
        regions (List[Any]): List of region specifications.
        varnos (List[str]): List of variable numbers/codes.
        intervals (List[Tuple[Any, Any]]): List of interval tuples (min, max).

    Returns:
        List[Dict[str, Any]]: List of configuration dictionaries.
    """
    data_list = []

    dt_start = datetime.strptime(date_start, '%Y%m%d%H')
    dt_end = datetime.strptime(date_end, '%Y%m%d%H')
    delta = timedelta(hours=6)
    current_date = dt_start

    while current_date <= dt_end:
        formatted_date = current_date.strftime('%Y%m%d%H')
        # Nested loops over all combinations
        for family in families:
            for region in regions:
                for name, input_path in zip(names, input_paths):
                    for interval in intervals:
                        interval_a, interval_b = interval
                        if interval_a is None and interval_b is None:
                            layers = 'layer_all'
                        else:
                            layers = f'layer_from{interval_a}MPato{interval_b}MPa'

                        filename = f'{formatted_date}_{family}'
                        filein = f'{input_path}/{filename}'
                        db_new = (
                            f'{work_path}/{family}/scatter_{layers}_{name}_{region}_'
                            f'{date_start}_{date_end}_bx{box_size_x}_by{box_size_y}_'
                            f'{flag_criteria}_{family}.db'
                        )

                        data_dict = {
                            'family': family,
                            'filein': filein,
                            'db_new': db_new,
                            'region': region,
                            'flag_criteria': flag_criteria,
                            'function': function,
                            'boxsizex': box_size_x,
                            'boxsizey': box_size_y,
                            'varnos': varnos,
                            'interval': interval
                        }
                        data_list.append(data_dict)
        current_date += delta

    return data_list   
   
import sqlite3
import numpy as np

def get_id_stns(cursor, id_stn, WIND_COMP_METHOD):
    """Obtiene la lista de id_stn desde la base de datos."""
  #  print (id_stn, WIND_COMP_METHOD)
    if id_stn == 'all' and WIND_COMP_METHOD:
        #print ('a')
        query = "SELECT DISTINCT id_stn, WIND_COMP_METHOD FROM moyenne;"
        cursor.execute(query)
        return np.array(cursor.fetchall())

    if id_stn == 'all' and WIND_COMP_METHOD != True:
       # print ('b')
        query = "SELECT DISTINCT id_stn FROM moyenne;"
        cursor.execute(query)
        rows = cursor.fetchall()
        return np.array([[row[0], None] for row in rows])
    if id_stn == 'join' and WIND_COMP_METHOD == True:
      #  print ('c')
        query = "SELECT DISTINCT WIND_COMP_METHOD FROM moyenne;"
        cursor.execute(query)
        rows = cursor.fetchall()
        return np.array([['join',row[0]] for row in rows])


    return [('join', x) for x in [None, None]]

def fetch_vcoords(cursor, criter):
    """Obtiene las coordenadas verticales y números de variable según el criterio dado."""
    query = f"SELECT DISTINCT vcoord, varno FROM moyenne {criter} ORDER BY vcoord ASC;"
    cursor.execute(query)
    return cursor.fetchall()

def fetch_channels_varno(cursor):
    """Obtiene los números de variable de todos los canales."""
    query = "SELECT DISTINCT varno FROM moyenne ORDER BY vcoord ASC;"
    cursor.execute(query)
    return [item[0] for item in cursor.fetchall()]

def create_data_list_plot(
    date_start: str,
    date_end: str,
    families: List[str],
    namein: List[str],
    work_path: str,
    box_size_x: float,
    box_size_y: float,
    functions: List[str],
    flag_criteria: str,
    regions: List[Any],
    id_stn: str,
    channel: str,
    projections: List[str],
    intervals: List[Tuple[Any, Any]],
) -> List[Dict[str, Any]]:
    """
    Generates a list of plotting dataset configurations for different intervals,
    families, regions, functions, channels, projections, and station IDs.

    Args:
        date_start (str): Starting date as 'YYYYMMDDHH'.
        date_end (str): Ending date as 'YYYYMMDDHH'.
        families (List[str]): List of family names/codes.
        namein (List[str]): Input dataset names (should be 1 or 2).
        work_path (str): Path prefix where database files are located.
        box_size_x (float): Box size in longitude.
        box_size_y (float): Box size in latitude.
        functions (List[str]): List of function names or codes.
        flag_criteria (str): Criteria as string for filtering.
        regions (List[Any]): List of region specifications.
        id_stn (str): 'all', 'join', or specific station ID.
        channel (str): 'all' or 'join'.
        projections (List[str]): List of projections to produce.
        intervals (List[Tuple[Any, Any]]): List of interval tuples (min, max).

    Returns:
        List[Dict[str, Any]]: List of plot dataset configuration dictionaries.
    """
    data_list_plot = []

    for interval in intervals:
        interval_a, interval_b = interval
        if interval_a is None and interval_b is None:
            layers = 'layer_all'
        else:
            layers = f'layer_from{interval_a}MPato{interval_b}MPa'

        for family in families:
            for region in regions:
                for function in functions:
                    for proj in projections:
                        # Build list of database files for this config
                        fileset = [
                            f'{work_path}/{family}/scatter_{layers}_{namein[0]}_{region}_{date_start}_{date_end}_bx{box_size_x}_by{box_size_y}_{flag_criteria}_{family}.db'
                        ]
                        nameset = [namein[0]]
                        if len(namein) > 1:
                            file_b = f'{work_path}/{family}/scatter_{layers}_{namein[1]}_{region}_{date_start}_{date_end}_bx{box_size_x}_by{box_size_y}_{flag_criteria}_{family}.db'
                            fileset.append(file_b)
                            nameset.append(namein[1])

                        # Open the first file in the set and process station IDs and vcoords
                        try:
                            with sqlite3.connect(fileset[0]) as conn:
                                cursor = conn.cursor()
                                cursor.execute("PRAGMA table_info('moyenne')")
                                columns = [col[1] for col in cursor.fetchall()]
                                WIND_COMP_METHOD = 'WIND_COMP_METHOD' in columns
                                   
                                id_stns = get_id_stns(cursor, id_stn, WIND_COMP_METHOD)    # Returns List[str]
                                for idstn, WIND_COMP_METHOD  in id_stns:
                                  #  print (idstn, WIND_COMP_METHOD)
                                    where_clause = '' if id_stn == 'join' else f'WHERE id_stn = "{idstn}"'
                                    if channel == 'all':
                                        vcoords = fetch_vcoords(cursor, where_clause)  # Returns List[Tuple[Any, int]]
                                        for vcoord, varno in vcoords:
                                            data_list_plot.append({
                                                'id_stn': idstn,
                                                'vcoord': vcoord,
                                                'files_in': fileset,
                                                'varno': varno,
                                                'region': region,
                                                'function': function,
                                                'proj': proj,
                                                'interval': interval,
                                                'family': family,
                                                'WIND_COMP_METHOD':WIND_COMP_METHOD 
                                            })
                                    else:  # channel == 'join' or other
                                        channels_varnos = fetch_channels_varno(cursor)  # Returns List[int]
                                        for varno in channels_varnos:
                                            data_list_plot.append({
                                                'id_stn': idstn,
                                                'vcoord': 'join',
                                                'files_in': fileset,
                                                'varno': varno,
                                                'region': region,
                                                'function': function,
                                                'proj': proj,
                                                'interval': interval,
                                                'family': family,
                                                'WIND_COMP_METHOD':WIND_COMP_METHOD
                                            })
                        except sqlite3.Error as err:
                            print(f"Warning: Could not open or query {fileset[0]}: {err}")
    return data_list_plot
 
def make_scatter(files_in,
                 names_in,  
                 pathwork, 
                 datestart,
                 dateend,
                 regions, 
                 families, 
                 flag_criteria, 
                 fonctions, 
                 varnos,
                 boxsizex, 
                 boxsizey, 
                 projs, # Proj=='OrthoN'// Proj=='OrthoS'// Proj=='robinson' // Proj=='Europe' // Proj=='Canada' // Proj=='AmeriqueNord' // Proj=='Npolar' //  Proj=='Spolar' // Proj == 'reg'
                 mode,
                 Points,
                 id_stn,
                 channel,
                 n_cpu,
                 intervales):
   
        """
       Perform scatter plot generation based on input parameters.
   
       Args:

        files_in (list): List of input file paths.

        names_in (list): List of input file names.

        pathwork (str): Working directory.

        datestart (str): Start date in YYYYMMDDHH format.

        dateend (str): End date in YYYYMMDDHH format.

        region (str): Region parameter description.

        family (str): Family parameter description.

        flag_criteria (str): Flags criteria.

        fonction (str): Function parameter description.

        boxsizex (int): Box size in X direction.

        boxsizey (int): Box size in Y direction.

        Proj (str or list): Projection type ('cyl', 'OrthoN', 'OrthoS', etc.).

        mode (str): Mode parameter description.

        Points (str): Points parameter description.

        id_stn (str): id_stn parameter description.

        channel (str): Channel parameter description.

        n_cpu (int): Number of CPUs to use.
   
       Returns:
       
         None
        """
        for family in families:
              pikobs.delete_create_folder(pathwork, family)
          
        data_list = create_data_list(datestart,
                                       dateend, 
                                       families, 
                                       files_in,
                                       names_in,
                                       pathwork,
                                       boxsizex,
                                       boxsizey, 
                                       fonctions, 
                                       flag_criteria, 
                                       regions,
                                       varnos,
                                       intervales)
                                       
       # exit()                             
        import time
        import dask
        t0 = time.time()
       # n_cpu=1
        if n_cpu==1:
          print (f'in Serie files: {len(data_list)} used in calculating statistics for {names_in}')
          for  data_ in data_list:  
               create_and_populate_moyenne_table(data_['family'], 
                                                 data_['db_new'], 
                                                 data_['filein'],
                                                 data_['region'],
                                                 data_['flag_criteria'],
                                                 data_['fonction'],
                                                 data_['boxsizex'],
                                                 data_['boxsizey'],
                                                 data_['varnos'],
                                                 channel,
                                                 id_stn,
                                                 data_['interval'])
               
       
       
       
       
        else:
           print (f'in Paralle number of files: {len(data_list)} used in calculating statistics for {len(data_list)}  {names_in} ')
           with dask.distributed.Client(processes=True, threads_per_worker=1, 
                                              n_workers=n_cpu, 
                                              silence_logs=40) as client:
               delayed_funcs = [dask.delayed(create_and_populate_moyenne_table)(data_['family'], 
                                                 data_['db_new'], 
                                                 data_['filein'],
                                                 data_['region'],
                                                 data_['flag_criteria'],
                                                 data_['function'],
                                                 data_['boxsizex'],
                                                 data_['boxsizey'],
                                                 data_['varnos'],
                                                 channel,
                                                 id_stn,
                                                 data_['interval'])for data_ in data_list]
              # print ('close0')
               results = dask.compute(*delayed_funcs)
               
               client.close()

        tn= time.time()
        print ('Total time for statistics:',tn-t0 )  
        time.sleep(5)

        data_list_plot = create_data_list_plot(datestart,
                                             dateend, 
                                             families, 
                                             names_in,
                                             pathwork,
                                             boxsizex,
                                             boxsizey, 
                                             fonctions, 
                                             flag_criteria, 
                                             regions,
                                             id_stn,
                                             channel,
                                             projs,
                                             intervales
                                            )

        t0 = time.time()
       # n_cpu=1
        if n_cpu==1:  
         print (f'in Serie plots = {len(data_list_plot)}')
         for  data_ in data_list_plot:  
           pikobs.scatter_plot(mode, 
                               data_['region'],
                               data_['family'], 
                               data_['id_stn'], 
                               datestart,
                               dateend, 
                               Points, 
                               boxsizex,
                               boxsizey,
                               data_['proj'], 
                               pathwork,
                               flag_criteria, 
                               data_['function'],
                               data_['vcoord'],
                               data_['files_in'],
                               names_in, 
                               data_['varno'],
                               data_['interval'],
                               data_['WIND_COMP_METHOD'])
        else:
         print (f"in Paralle plots = {len(data_list_plot)}")
         time.sleep(4)
         with dask.distributed.Client(processes=True, threads_per_worker=1, 
                                          n_workers=n_cpu, 
                                          silence_logs=40) as client:
           delayed_funcs = [dask.delayed(pikobs.scatter_plot)(mode, 
                                                              data_['region'],
                                                              data_['family'], 
                                                              data_['id_stn'],
                                                              datestart,
                                                              dateend, 
                                                              Points, 
                                                              boxsizex,
                                                              boxsizey,
                                                              data_['proj'], 
                                                              pathwork,
                                                              flag_criteria, 
                                                              data_['function'],
                                                              data_['vcoord'],
                                                              data_['files_in'],
                                                              names_in, data_['varno'],
                                                              data_['interval'],
                                                              data_['WIND_COMP_METHOD'])for data_ in data_list_plot]
   
           results = dask.compute(*delayed_funcs)
           client.close()
        print ('Total time:',time.time() - t0 )  
        print (f'check: {pathwork}')
    
import argparse
import re
import argparse
import re

def parse_intervals(text):
    """Parses a string of intervals formatted as '[(,),(a,b)]' into a list of tuples."""

    # Expresión regular corregida para aceptar paréntesis vacíos y números
    pattern = r'\(\s*(\d*)\s*,\s*(\d*)\s*\)'  
    matches = re.findall(pattern, text)


    result = []
    for a, b in matches:
        val_a = int(a) if a.isdigit() else None
        val_b = int(b) if b.isdigit() else None
        result.append((val_a, val_b))

    return result

def arg_call():

    import argparse
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_control_files', default='undefined', type=str, help="Directory where input sqlite files are located")
    parser.add_argument('--control_name', default='undefined', type=str, help="Directory where input sqlite files are located")
    parser.add_argument('--path_experience_files', default='undefined', type=str, help="Directory where input sqlite files are located")
    parser.add_argument('--experience_name', default='undefined', type=str, help="Directory where input sqlite files are located")
  

    
    parser.add_argument('--pathwork', default='undefined', type=str, help="Working directory")
    parser.add_argument('--datestart', default='undefined', type=str, help="Start date")
    parser.add_argument('--dateend', default='undefined', type=str, help="End date")
    parser.add_argument('--region', nargs="+", default='undefined', type=str, help="Region")
    parser.add_argument('--family', nargs="+", default='undefined', type=str, help="Family")
    parser.add_argument('--flags_criteria', default='undefined', type=str, help="Flags criteria")
    parser.add_argument('--fonction', nargs="+", default='undefined', type=str, help="Function") 
    parser.add_argument('--varnos', nargs="+", default='undefined', type=str, help="Function")
    parser.add_argument('--boxsizex', default='undefined', type=int, help="Box size in X direction")
    parser.add_argument('--boxsizey', default='undefined', type=int, help="Box size in Y direction")
    parser.add_argument('--projection', nargs="+", default='cyl', type=str, help="Projection type (cyl, OrthoN, OrthoS, robinson, Europe, Canada, AmeriqueNord, Npolar, Spolar, reg)")
    parser.add_argument('--mode', default='SIGMA', type=str, help="Mode")
    parser.add_argument('--Points', default='OFF', type=str, help="Points")
    parser.add_argument('--id_stn', default='one_per_plot', type=str, help="id_stn") 
    parser.add_argument('--channel', default='one_per_plot', type=str, help="channel")
    parser.add_argument('--n_cpus', default=1, type=int, help="Number of CPUs")
    parser.add_argument(
    "--layer",
    type=str,
    nargs="?",
    default="[(,)]",  # Valor por defecto
    help="Lista de intervalos, ejemplo: '[(,),(700,900)]'"
)
    
    args = parser.parse_args()
    for arg in vars(args):
       print (f'--{arg} {getattr(args, arg)}')
    # Check if each argument is 'undefined'
    if args.path_control_files == 'undefined':
        files_in = [args.path_experience_files]
        names_in = [args.experience_name]
    else:    
        if args.path_experience_files == 'undefined':
            raise ValueError('You must specify --path_experience_files')
        if args.experience_name == 'undefined':
            raise ValueError('You must specify --experience_name')
        else:

            files_in = [args.path_control_files, args.path_experience_files]
            names_in = [args.control_name, args.experience_name] 
    intervals = parse_intervals(args.layer)
    args = parser.parse_args()


    if args.varnos == 'undefined':
        args.varnos = []
    if args.pathwork == 'undefined':
        raise ValueError('You must specify --pathwork')
    if args.datestart == 'undefined':
        raise ValueError('You must specify --datestart')
    if args.dateend == 'undefined':
        raise ValueError('You must specify --dateend')
    if args.region == 'undefined':
        raise ValueError('You must specify --region')
    if args.family == 'undefined':
        raise ValueError('You must specify --family')
    if args.flags_criteria == 'undefined':
        raise ValueError('You must specify --flags_criteria')
    if args.fonction == 'undefined':
        raise ValueError('You must specify --fonction')
    if args.boxsizex == 'undefined':
        raise ValueError('You must specify --boxsizex')
    if args.boxsizey == 'undefined':
        raise ValueError('You must specify --boxsizey')


    # Comment
    # Proj='cyl' // Proj=='OrthoN'// Proj=='OrthoS'// Proj=='robinson' // Proj=='Europe' // Proj=='Canada' // Proj=='AmeriqueNord' // Proj=='Npolar' //  Proj=='Spolar' // Proj == 'reg'
  

    #print("in")
    # Call your function with the arguments
    sys.exit(make_scatter(files_in,
                          names_in,    
                          args.pathwork,
                          args.datestart,
                          args.dateend,
                          args.region,
                          args.family,
                          args.flags_criteria,
                          args.fonction,
                          args.varnos,
                          args.boxsizex,
                          args.boxsizey,
                          args.projection,
                          args.mode,
                          args.Points,
                          args.id_stn,
                          args.channel,
                          args.n_cpus,
                          intervals))
