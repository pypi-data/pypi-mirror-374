#!/usr/bin/env python3

#Auteur : Pierre Koclas, May 2021
import os
import sys
import csv
from math import floor,ceil,sqrt
import matplotlib as mpl
mpl.use('Agg')
#import pylab as plt
import matplotlib.pylab as plt
import numpy as np
import matplotlib.colorbar as cbar
import matplotlib.cm as cm
import datetime
import cartopy.crs as ccrs
import cartopy.feature
#from cartopy.mpl.ticker    import LongitudeFormatter,  LatitudeFormatter
import matplotlib.colors as colors
#import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import sqlite3
from matplotlib.collections import PatchCollection
from statistics import median
import pikobs
import optparse
from mpl_toolkits.axes_grid1 import make_axes_locatable
def projectPpoly(PROJ,lat,lon,deltax,deltay,pc):
        X1,Y1  = PROJ.transform_point(lon - deltax,lat-deltay,pc )
        X2,Y2  = PROJ.transform_point(lon - deltax,lat+deltay,pc )
        X3,Y3  = PROJ.transform_point(lon + deltax,lat+deltay,pc )
        X4, Y4 = PROJ.transform_point(lon + deltax,lat-deltay,pc )
        Pt1=[ X1,Y1 ]
        Pt2=[ X2,Y2 ]
        Pt3=[ X3,Y3 ]
        Pt4=[ X4,Y4 ]
        Points4 = [ Pt1, Pt2,Pt3,Pt4 ]
           
        return Points4
def SURFLL(lat1,lat2,lon1,lon2):
#= (pi/180)R^2 |sin(lat1)-sin(lat2)| |lon1-lon2|
    R=6371.
    lat2=min(lat2,90.)
    surf=R*R*(np.pi/180.)*abs ( np.sin(lat2*np.pi/180.) - np.sin(lat1*np.pi/180.) ) *abs( lon2-lon1 )
   # if ( surf == 0.):
    # print (   ' surf=',lat1,lat2,lat2*np.pi/180.,lat1*np.pi/180.,np.sin(lat2*np.pi/180.) ,  np.sin(lat1*np.pi/180.) )
    return surf

def NPSURFLL(lat1, lat2, lon1, lon2):
    R = 6371.
    lat2 = np.minimum(lat2, 90.)
    surf = R**2 * (np.pi/180) * np.abs(np.sin(lat2*np.pi/180) - np.sin(lat1*np.pi/180)) * np.abs(lon2 - lon1)
  #  if np.any(surf == 0.):
    #    print('surf contiene valores cero')
    return surf
def SURFLL2(lat1, lat2, lon1, lon2):
    R = 6371.0
    lat2 = np.minimum(lat2, 90.0)
    surf = R * R * (np.pi / 180.0) * np.abs(np.sin(lat2 * np.pi / 180.0) - np.sin(lat1 * np.pi / 180.0)) * np.abs(lon2 - lon1)
    # Debugging print statements if surface is zero
    zero_surf_indices = (surf == 0.0)
    if np.any(zero_surf_indices):
        print('surf=', lat1[zero_surf_indices], lat2[zero_surf_indices], lat2[zero_surf_indices] * np.pi / 180.0,
              lat1[zero_surf_indices] * np.pi / 180.0,
              np.sin(lat2[zero_surf_indices] * np.pi / 180.0),
              np.sin(lat1[zero_surf_indices] * np.pi / 180.0))
    return surf

    # ---- Función para cargar datos ----
def load_data(sqlite_file, varno, id_stn, debut, final):
        import sqlalchemy
        import os, numpy as np, pandas as pd

        engine = sqlalchemy.create_engine(f"sqlite:///{sqlite_file}")
        query = f"""
        SELECT
            id_stn, varno,
            ROUND(lat/1.0)*1.0 AS lat_bin,
            vcoord AS vcoord_bin,
            SUM(sumy)*1.0/SUM(N) AS omp,
            SQRT(SUM(sumy2)*1.0/SUM(N) - POWER(SUM(sumy)*1.0/SUM(N), 2)) AS sigma,
            SUM(N) AS n_obs
        FROM moyenne
        WHERE
            varno = {varno}
            AND id_stn = '{id_stn}'
            AND sumy IS NOT NULL
            AND date BETWEEN '{debut}' AND '{final}'
        GROUP BY id_stn, varno, vcoord_bin, lat_bin
        HAVING COUNT(*) > 1
        ORDER BY vcoord_bin DESC, lat_bin
        """
        return pd.read_sql_query(query, engine)

def compute_variable_heights(unique_vals):
        if len(unique_vals) == 1:
            edges = np.array([unique_vals[0]-0.5, unique_vals[0]+0.5])
        else:
            centers = unique_vals
            mids = (centers[:-1]+centers[1:])/2.0
            edges = np.concatenate(([centers[0]-(centers[1]-centers[0])/2], mids, [centers[-1]+(centers[-1]-centers[-2])/2]))
        heights_by_val = {val: edges[i+1]-edges[i] for i, val in enumerate(unique_vals)}
        return edges, heights_by_val

def zone_plot(
    mode, region, family, id_stn, datestart, dateend, Points,
    boxsizex, boxsizey, proj, pathwork, flag_criteria,
    fonction, vcoord, filesin, namesin, varno, intervales
):
    import os, numpy as np, pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib.collections import PatchCollection
    from matplotlib import cm, colors
    import sqlalchemy
    from matplotlib.colors import ListedColormap, BoundaryNorm
    import sqlalchemy

    os.makedirs(pathwork, exist_ok=True)
    os.makedirs(os.path.join(pathwork, family), exist_ok=True)

    debut, final = datestart, dateend
    vcoord_type = 'Channel' if family != 'sw' else 'Pressure(Hpa)'
    Delt_LAT, DeltP = (2, 20) if family == 'sw' else (2, 0.5)
    tipo = 'values' if family=='sw' else 'indices'
    invertir_y = True

    # ---- Cargar primer archivo ----
    df1 = load_data(filesin[0], varno, id_stn, debut, final)

    # ---- Merge y porcentajes si hay 2 archivos ----
    if len(filesin) == 2:
        df2 = load_data(filesin[1], varno, id_stn, debut, final)
        df = pd.merge(df2, df1,
                      on=['id_stn','varno','vcoord_bin','lat_bin'],
                      suffixes=('_ctl','_exp'))
        for var in ['omp','sigma','n_obs']:
            den = df[f'{var}_ctl'].replace(0, np.nan)
            df[f'{var}_pct'] = 100 * (df[f'{var}_ctl'] - df[f'{var}_exp']) / den
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        use_percent = True
    else:
        df = df1.copy()
        use_percent = False

    if df.empty:
        print("[WARNING] No data retrieved from database.")
        return

    lat = df['lat_bin'].values
    vcrd = df['vcoord_bin'].values / 100. if family=='sw' else df['vcoord_bin'].values
    unique_vcrd = np.sort(np.unique(vcrd))

    edges_vals, heights_by_val = compute_variable_heights(unique_vcrd) if tipo=='values' else (None, None)
    variable_name, units, vcoord_type = pikobs.type_varno(varno)

    # ---- Preparar variables a graficar ----
    variables = [
        ('sigma', df['sigma_pct'].values if use_percent else df['sigma'].values,
          f'Percentage of improvement in stdomp \n relative to {namesin[0]} [%]' if use_percent else 'Standard Deviation OMP' ),
        ('n_obs', df['n_obs_pct'].values if use_percent else df['n_obs'].values,
          f'Percentage of increase in sum(dens [nobs/km²])/days \n relative to {namesin[0]} [%]'),
        ('omp', df['omp_pct'].values if use_percent else df['omp'].values,
         f'Percentage of improvement in OMP \n relative to {namesin[0]} [%]' if use_percent else f'OMP {units}')
    ]

    outdir = os.path.join(pathwork, family)
    os.makedirs(outdir, exist_ok=True)

    # ---- Loop sobre variables para graficar ----
    for name, var, label in variables:
        var = np.asarray(var).ravel()
        fig, ax = plt.subplots(figsize=(18,18))

        # ---- Colormap ----
        if use_percent:
            bounds = np.array(list(range(-100,-5,20)) + [-5,5] + list(range(20,101,20)))
            neg_colors = [cm.RdYlBu_r(x) for x in np.linspace(0.08, 0.40, len(bounds[bounds<-5]))]
            pos_colors = [cm.RdYlBu_r(x) for x in np.linspace(0.60, 0.92, len(bounds[bounds>5]))]
            blanco = (1,1,1,1)
            colores = neg_colors + [blanco] + pos_colors
            cmap = ListedColormap(colores)
            cmap.set_under('#0235ad')
            cmap.set_over('#b30000')
            norm = BoundaryNorm(bounds, cmap.N)
            boundaries =bounds
            ticks =  boundaries

        else:
            # Escala automática según datos

            if name== 'omp':  # Divergente centrado en 0
                           # Divergente centrado en cero
                   max_abs = np.nanmax(np.abs(var))
                   vmin, vmax = -max_abs, max_abs
                   N_intervals = 8
                   boundaries = np.linspace(vmin, vmax, N_intervals + 1)  # 11 valores → 10 intervalos
                   centers = (boundaries[:-1] + boundaries[1:]) / 2
               
                   # Colormap con suficientes colores para cubrir los bins + extend
                   cmap = cm.get_cmap('RdYlBu_r', N_intervals + 2)  # 10 + 2 = 12 colores
                   cmap.set_under('#0235ad')
                   cmap.set_over('#b30000')
               
                   # BoundaryNorm con extend='both'
                   norm = BoundaryNorm(boundaries, cmap.N, extend='both')
                   ticks =  boundaries
            else:
               vmin, vmax = np.nanmin(var), np.nanmax(var)
           
               # Definimos boundaries (10 intervalos por defecto)
               N_intervals = 5
               boundaries = np.linspace(vmin, vmax, N_intervals + 1)  # 11 valores → 10 intervalos
               centers = (boundaries[:-1] + boundaries[1:]) / 2
           
               # Colormap con suficientes colores para cubrir los bins + extend
               cmap = cm.get_cmap('jet', N_intervals + 2)  # 10 + 2 = 12 colores
               cmap.set_under('#0235ad')
               cmap.set_over('#b30000')
           
               # BoundaryNorm con extend='both'
               norm = BoundaryNorm(boundaries, cmap.N, extend='both')
               ticks =  boundaries
        mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
        colors_vec = mappable.to_rgba(var)

        # ---- Crear rectángulos ----
        rects = []
        for i, vi in enumerate(var):
            if not np.isnan(vi):
                if tipo=='indices':
                    y_center = int(np.argwhere(unique_vcrd==vcrd[i])[0]) if vcrd[i] in unique_vcrd else i
                    y_height = 1.0
                else:
                    y_center = vcrd[i]
                    key = y_center if y_center in heights_by_val else unique_vcrd[np.argmin(np.abs(unique_vcrd-vcrd[i]))]
                    y_height = heights_by_val[key]
                rects.append(Rectangle((lat[i]-Delt_LAT/2, y_center-y_height/2),
                                       Delt_LAT, y_height,
                                       facecolor=colors_vec[i], edgecolor=colors_vec[i]))
        ax.add_collection(PatchCollection(rects, match_original=True))

        # ---- Configurar ejes ----
        ax.set_xlim(lat.min()-Delt_LAT/2, lat.max()+Delt_LAT/2)
        if tipo=='indices':
            N = len(unique_vcrd)
            ax.set_ylim(N-0.5, -0.5)
            ax.set_yticks(np.arange(N))
            ax.set_yticklabels([f"{v:.0f}" for v in unique_vcrd], fontsize=20)
        else:
            ax.set_ylim(vcrd.max(), vcrd.min())

        ax.set_xlabel('Latitude', fontsize=24)
        ax.set_ylabel(vcoord_type, fontsize=24)
        if len(namesin)==1:
           ax.set_title(f'{name} in {namesin[0]} from {datestart} to {dateend}, varno={varno}, id_stn={id_stn}', fontsize=24, pad=30)
        else:
          ax.set_title(f'Diff {namesin[0]} - {namesin[1]} \n from {datestart} to {dateend}, {variable_name} {units},  id_stn={id_stn}', fontsize=24, pad=40)
    
        ax.tick_params(axis='x', labelsize=22)
        ax.tick_params(axis='y', labelsize=22)
        ax.grid(True, axis='x', alpha=0.3)
        ax.grid(True, axis='y', alpha=0.4)
        ax.set_xlim(-90, 90)       # Latitud fija
        ax.set_ylim(1000, 0)   
        # ---- Colorbar ----
        cax = fig.add_axes([0.91, 0.15, 0.02, 0.7])
        cb = fig.colorbar(mappable, cax=cax, extend='both', boundaries=boundaries, ticks=ticks)
        cb = fig.colorbar(mappable, cax=cax, extend='both' if use_percent else 'neither')
        cb.set_label(label, fontsize=20)
        if use_percent:
            cb.set_ticks([-100, -80, -60, -40, -20, -5, 5, 20, 40, 60, 80, 100])
        cb.ax.tick_params(labelsize=17)

        # ---- Guardar figura ----
        output_file = os.path.join(outdir, f'1scatterplot_{"_".join(namesin)}_{name}_var{varno}_{id_stn}.png')
        plt.savefig(output_file, dpi=600, format='png', bbox_inches='tight', pad_inches=0.5)
        plt.close(fig)

def zone_plot2(
    mode,
    region,
    family,
    id_stn,
    datestart,
    dateend,
    Points,
    boxsizex,
    boxsizey,
    proj,
    pathwork,
    flag_criteria,
    fonction,
    vcoord,
    filesin,
    namesin,
    varno,
    intervales
):
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib.collections import PatchCollection
    from matplotlib import cm, colors, colorbar
    import numpy as np
    import sqlalchemy
    import os
    from matplotlib.colors import ListedColormap, BoundaryNorm

    method = 1
    vcoord_type = 'Channel'
    if family == 'sw':
        vcoord_type = 'Pressure(Hpa)'

    debut = datestart
    final = dateend
    sqlite_files = filesin
    os.makedirs(pathwork, exist_ok=True)
    os.makedirs(os.path.join(pathwork, family), exist_ok=True)

    def load_data(sqlite_file):
        engine = sqlalchemy.create_engine(f"sqlite:///{sqlite_file}")
        query = f"""
        SELECT
            id_stn, varno,
            vcoord AS vcoord_bin,
            round(lat/1.0)*1.0 AS lat_bin,
            SUM(sumy)*1.0/SUM(N) AS omp,
            SQRT(SUM(sumy2)*1.0/SUM(N) - POWER(SUM(sumy)*1.0/SUM(N), 2)) AS sigma,
            SUM(N) AS n_obs
        FROM moyenne
        WHERE
            varno = {varno}
            AND id_stn = '{id_stn}'
            AND sumy IS NOT NULL
            AND date BETWEEN '{debut}' AND '{final}'
        GROUP BY id_stn, varno, vcoord_bin, lat_bin
        HAVING COUNT(*) > 1
        ORDER BY vcoord_bin DESC, lat_bin
        """
        return pd.read_sql_query(query, engine)

    # Datos del primer archivo
    df1 = load_data(sqlite_files[0], varno, id_stn, debut, final)

    # Colormap personalizado (modo 'tints' sin blanco central, muy claro cerca de 0)
    def custom_div_cbar(bounds,
                        mode='tints',
                        blanco=(1,1,1,1),
                        over_color='#e600c7',
                        under_color='#0235ad'):
        M = len(bounds) - 1
        if M <= 0:
            raise ValueError("bounds debe tener al menos 2 valores")

        if mode == 'white2':
            if M % 2 != 0:
                raise ValueError("Para 'white2' usa número PAR de bins (p.ej., -100..100 paso 10).")
            N_neg = M // 2 - 1
            N_pos = M // 2 - 1
            center_slots = 2
            neg_samples = np.linspace(0.08, 0.40, max(N_neg, 0))
            pos_samples = np.linspace(0.60, 0.92, max(N_pos, 0))
            neg_colors = [cm.RdYlBu_r(x) for x in neg_samples] if N_neg > 0 else []
            pos_colors = [cm.RdYlBu_r(x) for x in pos_samples] if N_pos > 0 else []
            colors_list = neg_colors + [blanco]*center_slots + pos_colors
        elif mode == 'tints':
         #   if M % 2 != 0:
            print (bounds)
         #       raise ValueError("Para 'tints' usa número PAR de bins (p.ej., -100..100 paso 10).")
            N_neg = M // 2 - 1
            N_pos = M // 2 - 1
            center_slots = 2
            neg_samples = np.linspace(0.10, 0.49, N_neg)
            pos_samples = np.linspace(0.51, 0.90, N_pos)
            neg_colors = [cm.RdYlBu_r(x) for x in neg_samples]
            pos_colors = [cm.RdYlBu_r(x) for x in pos_samples]
            colors_list = neg_colors + [blanco]*center_slots + pos_colors

        else:
            raise ValueError("mode debe ser 'tints' o 'white2'.")

        cmap = ListedColormap(colors_list)
        cmap.set_over(over_color)
        cmap.set_under(under_color)
        cmap.set_bad((0.85, 0.85, 0.85, 1.0))
        norm = BoundaryNorm(bounds, ncolors=cmap.N, clip=False)
        return cmap, norm
    print (namesin)

    # Preparar datos, colormaps y bounds
    if len(sqlite_files) == 2:
        # Merge y porcentajes
        df2 = load_data(sqlite_files[1], varno, id_stn, debut, final)
        df = pd.merge(
            df2, df1,
            on=['id_stn', 'varno', 'vcoord_bin', 'lat_bin'],
            suffixes=('_ctl', '_exp')
        )

        # Diferencias absolutas (por si quieres guardar)
        df['omp']   = (df['omp_ctl'].abs() - df['omp_exp'].abs())*100/df['omp_ctl'].abs()
        df['sigma'] = (df['sigma_ctl'].abs() - df['sigma_exp'].abs())*100/df['sigma_ctl']
        df['n_obs'] = (df['n_obs_ctl'] - df['n_obs_exp'])*100/df['n_obs_ctl']
        # Porcentajes respecto al control (sin recortar para ver triángulos)
        for var in ['omp', 'sigma', 'n_obs']:
            den = df[f'{var}_ctl'].replace(0, np.nan)
            df[f'{var}_pct'] = 100 * (df[f'{var}_ctl'] - df[f'{var}_exp']) / den
        df.replace([np.inf, -np.inf], np.nan, inplace=True)

        # Límites y colormaps [-100..100] paso 10


        bounds = np.array(
        list(range(-100, -5, 20)) +   # valores negativos hasta -5
        [-5, 5] +                     # rango blanco [-5,5]
        list(range(20, 101, 20))      # valores positivos desde 20 hasta 100
    )
        y = bounds
        
        # Colores negativos
        neg_colors = [cm.RdYlBu_r(x) for x in np.linspace(0.08, 0.40, len(bounds[bounds < -5]))]
        
        # Color blanco para [-5,5]
        blanco = (1.0, 1.0, 1.0, 1.0)
        
        # Colores positivos
        pos_colors = [cm.RdYlBu_r(x) for x in np.linspace(0.60, 0.92, len(bounds[bounds > 5]))]
        
        # Concatenar colores
        colores = neg_colors + [blanco] + pos_colors
        
        # Crear cmap y norm
        cmap = colors.ListedColormap(colores)
        cmap.set_under('#0235ad')
        cmap.set_over('#b30000')
        norm = colors.BoundaryNorm(bounds, cmap.N)
        
        # Asignar a cada variable como antes
        cmap_omp   = cmap
        cmap_sigma = cmap
        cmap_nobs  = cmap
        norm_omp   = norm
        norm_sigma = norm
        norm_nobs  = norm
        bounds_omp = bounds_sigma = bounds_nobs = bounds
        print (bounds)
        use_percent = True
    else:
        # Un solo archivo: original (no porcentajes)
        df = df1.copy()

        bounds_omp = np.round(np.linspace(df['omp'].min(), df['omp'].max(), 6),2)
        
        
        bounds_sigma = np.round(np.linspace(df['sigma'].min(), df['sigma'].max(), 6),2)

        bounds_nobs =  np.linspace(df['n_obs'].min(), df['n_obs'].max(), 10, dtype=int)
        # Reutilizamos el mismo constructor de cmap

        print (bounds_omp)
        print (bounds_sigma)
        print (bounds_nobs)
       # cmap_omp,   norm_omp   = custom_div_cbar(bounds_omp, mode='tints')
       # cmap_sigma, norm_sigma = custom_div_cbar(bounds_sigma, mode='tints')
        # Para n_obs no simétrico, usa jet o un cmap secuencial si prefieres
        cmap_sigma  = cm.get_cmap('jet', len(bounds_sigma) - 1)
    
        norm_sigma = BoundaryNorm(bounds_sigma, cmap_sigma.N)

        cmap_omp  = cm.get_cmap('jet', len(bounds_omp) - 1)
        cmap_omp .set_under('#0235ad')
        cmap_omp .set_over('#b30000')

        norm_omp = BoundaryNorm(bounds_omp, cmap_omp.N)


        cmap_nobs = cm.get_cmap('jet', len(bounds_nobs) - 1)
        norm_nobs = BoundaryNorm(bounds_nobs, cmap_nobs.N)
        use_percent = False

    if df.empty:
        print("[WARNING] No data retrieved from database.")
        return

    variable_name, units, vcoord_type = pikobs.type_varno(varno)
    print(variable_name, units, vcoord_type)

    lat = df['lat_bin'].values
    vcrd = df['vcoord_bin'].values / 100. if family == 'sw' else df['vcoord_bin'].values

    # Datos a graficar (porcentaje si hay 2 archivos)
    if use_percent:
        omp = df['omp_pct'].values
        sigma = df['sigma_pct'].values
        n_obs = df['n_obs_pct'].values
        label_sigma = f'Percentage increase in stdomp \n relative to {namesin[0]} [%]'
        label_omp = f'Percentage of improvement in OMP \n relative to {namesin[0]} [%]'
        label_nobs = f'Percentage of increase in sum(dens [nobs/km²])/days \n relative to {namesin[0]} [%]'

    else:
        omp = df['omp'].values
        sigma = df['sigma'].values
        n_obs = df['n_obs'].values
        label_sigma = 'Standard Deviation'
        label_omp = 'O - P (Bias)'
        label_nobs = 'Number Of Observations'

    Delt_LAT, DeltP = (2, 20) if family == 'sw' else (2, 0.5)

    variables = [
        ('sigma', sigma, label_sigma, cmap_sigma, norm_sigma, bounds_sigma),
        ('nobs',  n_obs,  label_nobs,  cmap_nobs,  norm_nobs,  bounds_nobs),
        ('omp',     omp,   label_omp,   cmap_omp,   norm_omp,   bounds_omp)
    ]

    # Arrays 1D
    lat = np.asarray(lat).ravel()
    vcrd = np.asarray(vcrd).ravel()

    # X-lims (latitud)
    lat_min = np.min(lat) - Delt_LAT / 2.0
    lat_max = np.max(lat) + Delt_LAT / 2.0

    # Canales únicos e índice para modo 'indices'
    unique_vcrd = np.sort(np.unique(vcrd))
    vcrd_to_idx = {val: idx for idx, val in enumerate(unique_vcrd)}
    vcrd_idx = np.array([vcrd_to_idx[val] for val in vcrd])

    # Alturas variables (modo 'values')
    def compute_variable_heights(unique_vals):
        if len(unique_vals) == 1:
            edges = np.array([unique_vals[0] - 0.5, unique_vals[0] + 0.5])
        else:
            centers = unique_vals
            mids = (centers[:-1] + centers[1:]) / 2.0
            first_edge = centers[0] - (centers[1] - centers[0]) / 2.0
            last_edge = centers[-1] + (centers[-1] - centers[-2]) / 2.0
            edges = np.concatenate(([first_edge], mids, [last_edge]))
        heights = edges[1:] - edges[:-1]
        heights_by_val = {val: heights[i] for i, val in enumerate(unique_vals)}
        return edges, heights_by_val

    if family == 'sw':
        tipo = 'values'
        y_limits = (0, 1000)
        invertir_y = True
        DeltP_val = None
        y_major_step = 100
        y_minor_step = 10
        edges_vals, heights_by_val = compute_variable_heights(unique_vcrd)
    else:
        tipo = 'indices'
        invertir_y = True
        y_limits = None
        DeltP_val = 1.0
        y_major_step = None
        y_minor_step = None
        edges_vals, heights_by_val = None, None

    outdir = os.path.join(pathwork, family)
    os.makedirs(outdir, exist_ok=True)

    for name, var, label, cmap, norm, bounds in variables:
        var = np.asarray(var).ravel()
        if var.shape[0] != lat.shape[0]:
            raise ValueError(f"var '{name}' tiene longitud {var.shape[0]} y no coincide con lat ({lat.shape[0]}).")

        fig, ax = plt.subplots(figsize=(18, 18))
        ax.set_xlim(lat_min, lat_max)

        # Mapeo de colores consistente (incluye under/over y NaN)
        mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
        mappable.set_array([])  # para colorbar
        colors_vec = mappable.to_rgba(var)

        # Crear rectángulos
        rects = []
        for i in range(len(var)):
            vi = var[i]
            if not np.isnan(vi):
                FC = colors_vec[i]
                if tipo == 'indices':
                    y_center = int(vcrd_idx[i])
                    y_height = 1.0
                else:
                    y_center = vcrd[i]
                    if DeltP_val is None and heights_by_val is not None:
                        key = y_center
                        if key not in heights_by_val:
                            idx_near = int(np.argmin(np.abs(unique_vcrd - y_center)))
                            key = unique_vcrd[idx_near]
                        y_height = float(heights_by_val[key])
                    else:
                        y_height = float(DeltP_val)

                rects.append(Rectangle(
                    (lat[i] - Delt_LAT / 2.0, y_center - y_height / 2.0),
                    Delt_LAT, y_height,
                    facecolor=FC, edgecolor=FC
                ))

        ax.add_collection(PatchCollection(rects, match_original=True))

        # Eje Y y rejilla
        if tipo == 'indices':
            N = len(unique_vcrd)
            pad = 0.5
            ymin, ymax = -0.5 - pad, N - 0.5 + pad
            ax.set_ylim((ymax, ymin) if invertir_y else (ymin, ymax))
            ax.set_yticks(np.arange(N))
            ax.set_yticklabels([f"{v:.0f}" for v in unique_vcrd], fontsize=20)
            ax.set_yticks(np.arange(-0.5, N + 0.5, 1.0), minor=True)
            ax.grid(False)
            ax.grid(True, axis='y', which='minor', color='k', linewidth=0.8)
            ax.grid(True, axis='x', which='major', color='k', alpha=0.3)
            ax.set_ylabel(vcoord_type)
        else:
            if y_limits is not None:
                ymin, ymax = y_limits
            else:
                if edges_vals is not None:
                    ymin, ymax = float(edges_vals[0]), float(edges_vals[-1])
                else:
                    ymin = float(np.nanmin(vcrd) - 0.5 * (1.0 if DeltP_val is None else DeltP_val))
                    ymax = float(np.nanmax(vcrd) + 0.5 * (1.0 if DeltP_val is None else DeltP_val))
            ax.set_ylim((ymax, ymin) if invertir_y else (ymin, ymax))

            import matplotlib.ticker as mticker
            if y_major_step is None or y_minor_step is None:
                span = abs(ymax - ymin)
                if y_major_step is None:
                    y_major_step = 100 if span >= 800 else 50 if span >= 300 else 10
                if y_minor_step is None:
                    y_minor_step = max(y_major_step / 5.0, 1)
                    
            ax.yaxis.set_major_locator(mticker.MultipleLocator(y_major_step))
            ax.yaxis.set_minor_locator(mticker.MultipleLocator(y_minor_step))
            ax.grid(True, axis='y', which='major', color='k', alpha=0.4)
            ax.grid(True, axis='x', which='major', color='k', alpha=0.3)
            ax.set_ylabel(vcoord_type, fontsize=24)
            ax.tick_params(axis='x', labelsize=22)
            ax.tick_params(axis='y', labelsize=22)

        ax.set_xlabel('Latitude', fontsize=24)
        ax.set_title(f'Pressure vs Latitude  from {datestart} to {dateend},\nvarno={varno}, id_stn={id_stn}', fontsize=24)


        # Barra de color (con triángulos si hay 2 archivos/porcentaje)
        cax = fig.add_axes([0.91, 0.15, 0.02, 0.7])
        print (bounds)

        cb = fig.colorbar(
            mappable, cmap=cmap,
            cax=cax,
            boundaries=bounds,
            orientation='vertical',
            extend='both' if use_percent else 'neither'
        )
        cb.ax.tick_params(labelsize=17) 
        cb.set_label(label, fontsize=20)
        if use_percent:
            cb.set_ticks([-100,  -80,  -60,  -40,  -20,   -5,    5,   20,   40,   60,   80,  100])

        # Guardado
        output_file = os.path.join(outdir, f'1scatterplot_{"_".join(namesin)}_{name}_var{varno}_{id_stn}.png')
        plt.savefig(output_file, dpi=600, format='png', bbox_inches='tight', pad_inches=0.5)
        plt.close(fig)

