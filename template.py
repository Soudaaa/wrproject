from metpy.plots import ctables
import pyart
import pandas as pd
from datetime import datetime
import pyart
import numpy as np
import os,glob
import tempfile
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mplcolors
from metpy.plots import ctables
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geopandas as gpd
from paramiko import SSHClient
from geopy.geocoders import Nominatim
#from pymeso import llsd
from csu_radartools import fundamentals
from pyhail import mesh_ppi, mesh_grid
import copy

shape_municipios = gpd.read_file('/home/vitorgoede/scripts/municipios_2010.shp')
VIL_const = 3.44e-6

ref_levels = [-30, -29.5, -29, -28.5, -27.5, -27, -26.5, -26, -25.5,
              -24.5, -24, -23.5, -23, -22.5, -21.5, -21, -20, -19.5, -19, -18.5,
              -18, -17.5, -17, -16.5, -16, -15.5, -15, -14.5, -14, -13.5,
              -13, -12.5, -12, -11.5, -11, -10.5, -10, -9.5, -9,
              -8.5, -8, -7.5, -7, -6.5, -6, -5.5, -5, -4.5, -4, -3.5, -3,
              -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5,
              4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5,
              11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15, 15.5, 16, 16.5,
              17, 17.5, 18, 18.5, 19, 19.5, 20, 20.5, 21, 21.5, 22, 22.5,
              23, 23.5, 24, 24.5, 25, 25.5, 26, 26.5, 27, 27.5, 28, 28.5,
              29, 29.5, 30, 30.5, 31, 31.5, 32, 32.5, 33, 33.5, 34, 34.5,
              35, 35.5, 36, 36.5, 37, 37.5, 38, 38.5, 39, 39.5, 40, 40.5,
              41, 41.5, 42, 42.5, 43, 43.5, 44, 44.5, 45, 45.5, 46, 46.5,
              47, 47.5, 48, 48.5, 49, 49.5, 50, 50.5, 51, 51.5, 52, 52.5,
              53, 53.5, 54, 54.5, 55, 55.5, 56, 56.5, 57, 57.5, 58, 58.5,
              59, 59.5, 60, 60.5, 61, 61.5, 62, 62.5, 63, 63.5, 64, 64.5,
              65, 65.5, 66, 66.5, 67, 67.5, 68, 68.5, 69, 69.5, 70, 70.5,
              71, 71.5, 72, 72.5, 73, 73.5, 74, 74.5, 75, 76, 77, 78.5,
              80, 81, 82.5, 83.5, 85, 86.5, 87.5, 89, 90, 91.5, 93]

zdr_levels = [-4.0, -3.9, -3.8, -3.7, -3.6, -3.5, -3.4, -3.3, -3.1, -3, -2.9,
              -2.8, -2.6, -2.5, -2.4, -2.3, -2.1, -2, -1.9, -1.8, -1.7,
              -1.6, -1.6, -1.5, -1.4, -1.3, -1.2, -1.1, -1, -0.9, -0.8,
              -0.7, -0.6, -0.5, -0.4, -0.3, -0.3, -0.2, -0.1, 0.1, 0.2,
              0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4,
              1.5, 1.6, 1.7, 1.8, 1.9, 2, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6,
              2.7, 2.8, 2.9, 3, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8,
              3.9, 4, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5, 5.1,
              5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6, 6.1, 6.2, 6.4,
              6.5, 6.7, 6.8, 6.9, 7, 7.1, 7.2, 7.4, 7.5, 7.6, 7.8, 7.9, 8]


#kdp_levels = [-2, -1.95, -1.9, -1.8, -1.75, -1.7, -1.65, -1.55, -1.5,
#              -1.45, -1.4, -1.3, -1.25, -1.2, -1.15, -1.05, -1, -0.95,
#              -0.9, -0.85, -0.8, -0.75, -0.7, -0.65, -0.6, -0.55, -0.5,
#              -0.45, -0.4, -0.35, -0.3, -0.25, -0.2, -0.15, -0.1, -0.05,
#              0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5,
#              0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1, 1.05,
#              1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4, 1.45, 1.5, 1.55, 1.6,
#              1.65, 1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 2, 2.05, 2.1, 2.15,
#              2.2, 2.25, 2.3, 2.35, 2.4, 2.45, 2.5, 2.55, 2.6, 2.65, 2.7,
#              2.75, 2.8, 2.85, 2.9, 2.95, 3, 3.05, 3.1, 3.2, 3.3, 3.35,
#              3.45, 3.5, 3.55, 3.6, 3.7, 3.75, 3.8, 3.85, 3.95, 4, 4.05,
#              4.1, 4.2, 4.25, 4.3, 4.35, 4.45, 4.5, 4.55, 4.6, 4.7, 4.75,
#              4.8, 4.85, 4.95, 5, 5.1, 5.2, 5.35, 5.45, 5.6, 5.7, 5.85,
#              5.95, 6.1, 6.2, 6.35, 6.45, 6.6, 6.7, 6.85, 6.95, 7.1, 7.3,
#              7.5, 7.7, 7.85, 8.05, 8.25, 8.45, 8.6, 8.8, 9, 9.25, 9.5,
#              9.75, 10]


rho_levels = [0.20, 0.225, 0.2417, 0.255, 0.2717, 0.2883, 0.3017, 
            0.3183, 0.335, 0.3517, 0.365, 0.3817, 0.3983, 0.4117,
            0.4283, 0.445, 0.4583, 0.4717, 0.4817, 0.495, 0.5083, 
            0.5217, 0.5317, 0.545, 0.5583, 0.5717, 0.5817, 0.595, 
            0.6083, 0.6217, 0.6317, 0.645, 0.655, 0.6617, 0.6683,
            0.675, 0.6783, 0.685, 0.6917, 0.6983, 0.705, 0.7117, 
            0.7183, 0.725, 0.7283, 0.735, 0.7417, 0.7483, 0.755,
            0.7617, 0.7683, 0.775, 0.7783, 0.785, 0.7917, 0.7983,
            0.805, 0.8117, 0.8183, 0.825, 0.8283, 0.835, 0.8417, 
            0.8483, 0.8517, 0.855, 0.8583, 0.8617, 0.865, 0.8683,
            0.8717, 0.875, 0.8783, 0.8817, 0.885, 0.8883, 0.8917,
            0.895, 0.8983, 0.9017, 0.905, 0.9083, 0.9117, 0.915,
            0.9183, 0.9217, 0.925, 0.9283, 0.9317, 0.935, 0.9383,
            0.9417, 0.945, 0.9483, 0.9517, 0.955, 0.9583, 0.9617,
            0.965, 0.9683, 0.9717, 0.975, 0.9783, 0.9817, 0.985, 
            0.9883, 0.9917, 0.995, 0.9983, 1.00, 1.005]

w_levels = [-0.1, 0.496, 0.991, 1.487, 1.983, 2.479, 2.974, 3.470, 3.966, 4.461,
            5.078, 5.453, 5.949, 6.644, 6.940, 7.536, 7.932, 8.427,
            8.923, 9.419, 9.914, 10.410, 10.905, 11.401, 11.897, 12.393,
            12.889, 13.384, 13.880, 14.375, 14.872, 15.367, 15.863, 16.359,
            16.854, 17.350, 17.846, 18.837, 20, 21]

ZH_Ticks = [-30, -20, -10, 0, 10, 20, 30, 40, 50, 60, 70, 90]
ZDR_Ticks = np.arange(-4, 9, 1)
KDP_Ticks = np.arange(-2, 8, 1)
RHO_Ticks = [0.20, 0.45, 0.65, 0.75, 0.85, 0.9, 0.95, 1]

shape_municipios = gpd.read_file('/home/vitorgoede/scripts/municipios_2010.shp')

dir_ctables = '/home/vitorgoede/scripts/colortable/'

def get_ctables():
    """
    reads and creates radar colormaps and their normalizations
    """
    ctables.registry.add_colortable(open(dir_ctables + 'ref.tbl', 'rt'), 'ref')
    ref_norm, ref_cmap = ctables.registry.get_with_boundaries('ref', ref_levels)

    ctables.registry.add_colortable(open(dir_ctables + 'zdr.tbl', 'rt'), 'zdr')
    zdr_norm, zdr_cmap = ctables.registry.get_with_boundaries('zdr', zdr_levels)

    ctables.registry.add_colortable(open(dir_ctables + 'kdp_table.tbl', 'rt'), 'kdp')
    kdp_norm, kdp_cmap = ctables.registry.get_with_range('kdp', -2, 7)

    ctables.registry.add_colortable(open(dir_ctables + 'rhohv.tbl', 'rt'), 'rhohv')
    rho_norm, rho_cmap = ctables.registry.get_with_boundaries('rhohv', rho_levels)

    vel_norm, vel_cmap = ctables.registry.get_with_range('NWS8bitVel', -50, 50)

    shear_norm, shear_cmap = ctables.registry.get_with_range('Carbone42', -10, 10)
        
    ctables.registry.add_colortable(open('/home/vitorgoede/scripts/colortable/w.tbl', 'rt'), 'w')
    w_norm, w_cmap = ctables.registry.get_with_range('w', -0.1, 10.1)
    
    return ref_norm, ref_cmap, zdr_norm, zdr_cmap, kdp_norm, kdp_cmap, rho_norm, rho_cmap, vel_norm, vel_cmap, shear_norm, shear_cmap, w_norm, w_cmap

ref_norm, ref_cmap, zdr_norm, zdr_cmap, kdp_norm, kdp_cmap, rho_norm, rho_cmap, vel_norm, vel_cmap, shear_norm, shear_cmap, w_norm, w_cmap = get_ctables()

def sel_radar(institution = None, radar_name = None, time = None, mode = 'nowcasting'):
    """
    Baixa os volumes pelo VPN do INPE e os salva em uma pasta temporária
    
    Parameters
    ----------
    instituition: str
        Instituição a qual pertence o radar.
    radar_name: str
        Nome do radar.
    time: date object
        objeto datetime contendo o ano, mês e dia
    mode: str
        Modo para download dos volumes.
        nowcasting: baixa os 10 volumes recentes.
        historico: baixa todos os volumes do dia.
        
    Returns
    -------
    tmp_dir: pasta temporária contendo os volumes salvos
    """    
    client = SSHClient()
    client.load_system_host_keys()
    client.connect(hostname='150.163.147.166', username='vitor.goede', password='v1t0r@Go3#')
    sftp = client.open_sftp()
    
    tmp_dir = tempfile.TemporaryDirectory()
    
    if time.month < 10:
        month = '0' + str(time.month)
    if time.month >= 10:
        month = str(time.month)
    if time.day < 10:
        day = '0' + str(time.day)
    if time.day >= 10:
        day = str(time.day)
        
    if institution == 'sdcsc':
        if radar_name == 'Chapecó':
            radar_name = 'chapeco'
            sftp.chdir(f'/oper/dboper/raw/arch/rad/{institution}/{radar_name}/volumetrico/hdf/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13137491_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13137491_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
        if radar_name == 'Lontras':
            radar_name = 'lontras'
            sftp.chdir(f'/oper/dboper/raw/arch/rad/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13227490_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13227490_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
        if radar_name == 'Araranguá':
            radar_name = 'ararangua'
            sftp.chdir(f'/oper/dboper/raw/arch/rad/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13127492_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13127492_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
            
    if institution == 'decea':
        if radar_name == 'Santiago':
            radar_name = 'santiago'
            sftp.chdir(f'/oper/radar/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13557476_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13557476_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
        if radar_name == 'Canguçu':
            radar_name = 'cangucu'
            sftp.chdir(f'/oper/radar/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13577477_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13577477_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
        if radar_name == 'Morro da Igreja':
            radar_name = 'morroigreja'
            sftp.chdir(f'/oper/radar/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13547478_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13547478_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
        if radar_name == 'São Roque':
            radar_name = 'saoroque'
            sftp.chdir(f'/oper/radar/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13537474_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13537474_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
        if radar_name == 'Pico do Couto':
            radar_name = 'picocouto'
            sftp.chdir(f'/oper/radar/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13567475_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13567475_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
        if radar_name == 'Gama':
            radar_name = 'gama'
            sftp.chdir(f'/oper/radar/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13507479_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13507479_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
            
    if institution == 'cemaden':
        if radar_name == 'Jaraguari':
            radar_name = 'jaraguari'
            sftp.chdir(f'/oper/dboper/raw/arch/rad/{institution}/{radar_name}/volumetrico/hdf/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13277482_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13277482_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
        if radar_name == 'Almenara':
            radar_name = 'almenara'
            sftp.chdir(f'/oper/dboper/raw/arch/rad/{institution}/{radar_name}/volumetrico/hdf/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13897469_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13897469_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
        if radar_name == 'Santa Tereza':
            radar_name = 'santatereza'
            sftp.chdir(f'/oper/dboper/raw/arch/rad/{institution}/{radar_name}/volumetrico/hdf/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13977487_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13977487_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
        if radar_name == 'Três Marias':
            radar_name = 'tresmarias'
            sftp.chdir(f'/oper/dboper/raw/arch/rad/{institution}/{radar_name}/volumetrico/hdf/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13477486_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13477486_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
        if radar_name == 'São Francisco':
            radar_name = 'saofrancisco'
            sftp.chdir(f'/oper/dboper/raw/arch/rad/{institution}/{radar_name}/volumetrico/hdf/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13457484_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13457484_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
        if radar_name == 'Salvador':
            radar_name = 'salvador'
            sftp.chdir(f'/oper/radar/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13467485_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13467485_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
        if radar_name == 'Maceio':
            radar_name = 'maceio'
            sftp.chdir(f'/oper/radar/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13447483_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13447483_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
        if radar_name == 'Natal':
            radar_name = 'natal'
            sftp.chdir(f'/oper/radar/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13247480_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13247480_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
        if radar_name == 'Petrolina':
            radar_name = 'petrolina'
            sftp.chdir(f'/oper/radar/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13257481_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13257481_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
            
    if institution == 'sipam':
        if radar_name == 'Belém':
            radar_name = 'belem'
            sftp.chdir(f'/oper/radar/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13507479_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13507479_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
        if radar_name == 'Boa Vista':
            radar_name = 'boavista'
            sftp.chdir(f'/oper/radar/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13507479_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13507479_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
        if radar_name == 'Cruzeiro do Sul':
            radar_name = 'cruzeirodosul'
            sftp.chdir(f'/oper/radar/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
        if radar_name == 'Macapá':
            radar_name = 'macapa'
            sftp.chdir(f'/oper/radar/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
        if radar_name == 'Manaus':
            radar_name = 'manaus'
            sftp.chdir(f'/oper/radar/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
        if radar_name == 'Porto Velho':
            radar_name = 'portovelho'
            sftp.chdir(f'/oper/radar/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
        if radar_name == 'Santarém':
            radar_name = 'santarem'
            sftp.chdir(f'/oper/radar/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
        if radar_name == 'São Luís':
            radar_name = 'saoluis'
            sftp.chdir(f'/oper/radar/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
        if radar_name == 'São Gabriel':
            radar_name = 'saogabriel'
            sftp.chdir(f'/oper/radar/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
        if radar_name == 'Tefe':
            radar_name = 'tefe'
            sftp.chdir(f'/oper/radar/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
        if radar_name == 'Tabatinga':
            radar_name = 'tabatinga'
            sftp.chdir(f'/oper/radar/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
            
    if institution == 'inea':
        if radar_name == 'Macaé':
            radar_name = 'macae'
            sftp.chdir(f'/oper/dboper/raw/arch/rad/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13997489_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13997489_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
        if radar_name == 'Guaratiba':
            radar_name = 'guaratiba'
            sftp.chdir(f'/oper/dboper/raw/arch/rad/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13957488_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13957488_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
                
    if institution == 'cemig':
        if radar_name == 'Mateus Leme':
            radar_name = 'mateusleme'
            sftp.chdir(f'/oper/dboper/raw/arch/rad/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13667493_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13667493_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
                
    if institution == 'funceme':
        if radar_name == 'Fortaleza':
            radar_name = 'fortaleza'
            sftp.chdir(f'/oper/dboper/raw/arch/rad/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13851129_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13851129_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)   
        if radar_name == 'Quixeramobim':
            radar_name = 'quixeramobim'
            sftp.chdir(f'/oper/dboper/raw/arch/rad/{institution}/{radar_name}/volumetrico/bruto/{time.year}/{month}/')
            if mode == 'nowcasting':
                list_vols = [x for x in sftp.listdir()[-10:] if x.startswith(f'R13967004_{time.year}{month}{day}')]
            if mode == 'historico':
                list_vols = [x for x in sftp.listdir() if x.startswith(f'R13967004_{time.year}{month}{day}')]
            for file in list_vols:
                sftp.get(file, tmp_dir.name + '/' + file)
            
    return tmp_dir

    
def files_df(radar_files, time_start, time_end):
    """
    Quick and easy way of creating and slicing a list of local radar files according to the desired time span.
    
    Parameters
    ----------
    
    radar_files: list of str
        list of string containing the radar files' names
    time_start: datetime obj
        datetime of the first volume
    time_end: datetime obj
        datetime of the last volume
        
    Returns
    -------
    files_list: list containing the desired radar files names
    """
    times = []
    for f in radar_files:
        if '.hdf5' in f:
            try:
                radar = pyart.aux_io.read_gamic(f)
            except:
                radar = pyart.aux_io.read_odim_h5(f)
        if '.hdf' in f:
            radar = pyart.aux_io.read_odim_h5(f)
        if '.nc' in f:
            radar = pyart.io.read(f)
        #radar.time['units'] = 'seconds since' + ' ' + datetime.strptime(radar.metadata['gamic_date'][:-5], '%Y-%m-%dT%H:%M:%S').isoformat() 
        time_begin = pyart.util.datetime_from_radar(radar)
        times.append(f'{time_begin:%Y%m%d %H:%M}')
    
    data_frame = pd.DataFrame({'files': radar_files}, index = pd.to_datetime(times))
    objects = data_frame.loc[f'{time_start:%Y%m%d %H:%M}':f'{time_end:%Y%m%d %H:%M}', :]
    files_list = objects['files'].tolist()

    return files_list

def sort_radar(radar):
    sweep_min = np.min(radar.sweep_number['data'])
    for sweep in radar.sweep_number['data']:
        sweep_slice = radar.get_slice(sweep)
        azi = radar.azimuth['data'][sweep_slice]
        if azi.shape[0] != 360:
            factor =  360 - azi.shape[0] 
            azi = np.delete(azi, np.arange(factor, 0), axis=0)
                
        ele = radar.elevation['data'][sweep_slice]
        if ele.shape[0] != 360:
            ele = np.delete(ele, np.arange(factor, 0), axis=0)

        az_idx = np.argsort(azi)
        az_sorted = azi[az_idx]
        ele_sorted = ele[az_idx]
        
        if sweep == sweep_min:
            az_final = copy.deepcopy(az_sorted[np.newaxis, :])
            ele_final = copy.deepcopy(ele_sorted[np.newaxis, :])
            idx_final = copy.deepcopy(az_idx[np.newaxis, :])
        else:
            try:
                az_final = np.concatenate([az_final, az_sorted[np.newaxis, :]])
                ele_final = np.concatenate([ele_final, ele_sorted[np.newaxis, :]])
                idx_final = np.concatenate([idx_final, az_idx[np.newaxis, :]])
            except ValueError:
                continue
                
    for fields in list(radar.fields.keys()):
        for sweep in radar.sweep_number['data']:
            field = radar.get_field(sweep, fields)
            mask = np.ma.getmask(field)
            if field.shape[0] != 360:
                factor =  360 - field.shape[0]
                mask = np.delete(mask, np.arange(factor, 0), axis=0)
                field = np.delete(field, np.arange(factor, 0), axis=0)
            mask_sorted = mask[idx_final[sweep]]
            field_sorted = field[idx_final[sweep]]
            field_sorted = np.ma.masked_array(field_sorted, mask_sorted)
            if sweep == sweep_min:
                field_final = field_sorted[np.newaxis, :]
            else:
                field_final = np.ma.concatenate([field_final, field_sorted[np.newaxis, :]])
        
        radar.fields[fields]['data'] = np.ma.vstack(field_final)
    
    radar.azimuth['data'] = az_final.flatten()
    radar.elevation['data'] = ele_final.flatten()
    radar.nrays = radar.azimuth['data'].shape[0]
    
    radar.sweep_start_ray_index['data'] = np.arange(0, radar.azimuth['data'].shape[0], 360)
    radar.sweep_end_ray_index['data'] = np.arange(359, radar.azimuth['data'].shape[0], 360)
    
    return radar

def add_instrument_parameters_odim(radar):
    
    radar.instrument_parameters = dict()
    radar.instrument_parameters= {'frequency': {'units': 's-1',
                                                'meta_group': 'instrument_parameters',
                                                'long_name': 'Radiation frequency',
                                                'data': np.array([3e8/0.10706872940063477], dtype=np.float32)},
                                  'radar_beam_width_h': {'units': 'degrees',
                                                         'meta_group': 'radar_parameters',
                                                         'long_name': 'Antenna beam width H polarization',
                                                         'data': np.array([1.0], dtype=np.float32)},
                                  'radar_beam_width_v': {'units': 'degrees',
                                                         'meta_group': 'radar_parameters',
                                                         'long_name': 'Antenna beam width V polarization',
                                                         'data': np.array([1.0], dtype=np.float32)},
                                  'pulse_width': {'units': 'seconds',
                                                  'comments': 'Pulse width',
                                                  'meta_group': 'instrument_parameters',
                                                  'long_name': 'Pulse width',
                                                  'data': np.resize([1e-6], radar.nrays)},
                                  'prt': {'units': 'seconds',
                                          'comments': 'Pulse repetition time. For staggered prt, also see prt_ratio.',
                                          'meta_group': 'instrument_parameters',
                                          'long_name': 'Pulse repetition time',
                                          'data': np.concatenate([np.resize([1/600], radar.nrays - 1245), np.resize([1/600], 784), np.resize([1/1000], 922)])},
                                  'prt_mode': {'comments': 'Pulsing mode Options are: "fixed", "staggered", "dual". Assumed "fixed" if missing.',
                                               'meta_group': 'instrument_parameters', 
                                               'long_name': 'Pulsing mode',
                                               'units': 'unitless',
                                               'data': np.array(['staggered', 'staggered', 'staggered', 'staggered', 'staggered', 'staggered',
                                                              'fixed', 'fixed', 'fixed', 'fixed'], dtype='<S9')},
                                  'prt_ratio': {'units': 'unitless',
                                                'meta_group': 'instrument_parameters',
                                                'long_name': 'Pulse repetition frequency ratio',
                                                'data': np.concatenate([np.resize([4/5], radar.nrays - 1245), np.resize([1], 784), np.resize([1], 922)])},
                                  'unambiguous_range': {'units': 'meters',
                                                        'comments': 'Unambiguous range',
                                                        'meta_group': 'instrument_parameters',
                                                        'long_name': 'Unambiguous range',
                                                        'data': np.concatenate([np.resize([240000], radar.nrays - 1245), np.resize([200000], 784), np.resize([120000], 922)])},
                                  'nyquist_velocity': {'units': 'meters_per_second',
                                                       'comments': 'Unambiguous velocity',
                                                       'meta_group': 'instrument_parameters',
                                                       'long_name': 'Nyquist velocity',
                                                       'data': np.concatenate([np.resize(fundamentals.dual_nyquist(0.10706872940063477, 480, 600), radar.nrays - 1245),
                                                                              np.resize(fundamentals.nyquist(750, 0.10706872940063477), 784),
                                                                              np.resize(fundamentals.nyquist(1000, 0.10706872940063477), 922)])}}
                                                
    
    radar.instrument_parameters['pulse_width']['data'] = radar.instrument_parameters['pulse_width']['data'].astype(np.float32)
    radar.instrument_parameters['prt']['data'] = radar.instrument_parameters['prt']['data'].astype(np.float32)
    radar.instrument_parameters['prt_ratio']['data'] = radar.instrument_parameters['prt_ratio']['data'].astype(np.float32)
    radar.instrument_parameters['unambiguous_range']['data'] = radar.instrument_parameters['unambiguous_range']['data'].astype(np.float32)
    radar.instrument_parameters['nyquist_velocity']['data'] = radar.instrument_parameters['nyquist_velocity']['data'].astype(np.float32)  

def z2r(ref):
    return 10**(ref/10)

def calc_VIL(radar, zh_name = 'corrected_reflectivity'):
    azi = [radar.azimuth['data'][x] for x in radar.iter_slice()]
    n_rays = azi[0].shape[0]
    ele = radar.fixed_angle['data']
    sort_idx = np.argsort(ele)
    n_sweeps = radar.nsweeps
    rg = radar.range['data']
    n_bins = radar.ngates

    ref_stacked = np.zeros((n_sweeps, n_rays, n_bins))
    x_stacked = np.zeros_like(ref_stacked)
    y_stacked = np.zeros_like(ref_stacked)
    z_stacked = np.zeros_like(ref_stacked)
    dz_stacked = np.zeros_like(ref_stacked)
    VIL = np.zeros((n_rays, n_bins))
    
    for i in sort_idx:
        ref_stacked[i, :, :] = radar.get_field(i, zh_name, copy = True)
        x, y, z = radar.get_gate_x_y_z(i)
        x_stacked[i, :, :] = x
        y_stacked[i, :, :] = y
        z_stacked[i, :, :] = z
    
    ref = z2r(ref_stacked)
    r = np.sqrt(x_stacked**2 + y_stacked**2)
    
    for i in range(n_sweeps):
        if i < n_sweeps - 1:
            dz_stacked[i, :, :] = z_stacked[i + 1, :, :] - z_stacked[i, :, :]
        if i == n_sweeps - 1:
            dz_stacked[i, :, :] = z_stacked[i, :, :] - z_stacked[i - 1, :, :]
            
    valid = (ref_stacked > 0)
    VIL_elements = VIL_const*(ref**(4/7))*dz_stacked
    
    for az_idx in range(n_rays):
        slice_valid = valid[:, az_idx, :]
        if not np.any(slice_valid):
            continue
        slice_VIL_elements = VIL_elements[:, az_idx, :]
        for rg_idx in range(n_bins):
            VIL_temp = 0
            sfc_rg = rg[rg_idx]
            for el_idx in range(n_sweeps):
                if not slice_valid[el_idx, rg_idx]:
                    continue
                if slice_VIL_elements[el_idx, rg_idx] == 0:
                    continue
                if el_idx == 0:
                    VIL_temp = slice_VIL_elements[el_idx, rg_idx]
                else:
                    ppi_ray_rg = r[el_idx, az_idx, :]
                    closest_idx = np.argmin(np.abs(ppi_ray_rg - sfc_rg))
                    VIL_temp += slice_VIL_elements[el_idx, closest_idx]
            if VIL_temp > 0:
                VIL[az_idx, rg_idx] = np.nansum(VIL_temp)
                
    VIL = np.ma.masked_where(ref_stacked[0] < 0, VIL)
    
    VIL_field = np.zeros_like(radar.fields[zh_name]['data'])
    VIL_field[radar.get_slice(sort_idx[0])] = VIL
    
    return VIL_field

def calc_ET(radar = None, zh_name = 'corrected_reflectivity'):
    azi = [radar.azimuth['data'][x] for x in radar.iter_slice()]
    n_rays = azi[0].shape[0]
    ele = radar.fixed_angle['data']
    sort_idx = np.argsort(ele)
    n_sweeps = radar.nsweeps
    rg = radar.range['data']
    n_bins = radar.ngates

    ref_stacked = np.zeros((n_sweeps, n_rays, n_bins))
    x_stacked = np.zeros_like(ref_stacked)
    y_stacked = np.zeros_like(ref_stacked)
    z_stacked = np.zeros_like(ref_stacked)
    ET = np.zeros((n_rays, n_bins))
    
    for i in sort_idx:
        ref_stacked[i, :, :] = radar.get_field(i, zh_name, copy = True)
        x, y, z = radar.get_gate_x_y_z(i)
        x_stacked[i, :, :] = x
        y_stacked[i, :, :] = y
        z_stacked[i, :, :] = z
    
    r = np.sqrt(x_stacked**2 + y_stacked**2)
            
    valid = (ref_stacked >= 18)
    
    for az_idx in range(n_rays):
        slice_valid = valid[:, az_idx, :]
        if not np.any(slice_valid):
            continue
        slice_ET_elements = z_stacked[:, az_idx, :]
        for rg_idx in range(n_bins):
            ET_temp = 0
            sfc_rg = rg[rg_idx]
            for el_idx in range(n_sweeps):
                if not slice_valid[el_idx, rg_idx]:
                    continue
                if slice_ET_elements[el_idx, rg_idx] == 0:
                    continue
                if el_idx == 0:
                    ET_temp = slice_ET_elements[el_idx, rg_idx]
                else:
                    ppi_ray_rg = r[el_idx, az_idx, :]
                    closest_idx = np.argmin(np.abs(ppi_ray_rg - sfc_rg))
                    ET_temp = np.nanmax(slice_ET_elements[el_idx, closest_idx])
            if ET_temp > 0:
                ET[az_idx, rg_idx] = ET_temp / 1000
                
    ET = np.ma.masked_where(ref_stacked[0] <= 0, ET)

    ET_field = np.zeros_like(radar.fields[zh_name]["data"])
    ET_field[radar.get_slice(sort_idx[0])] = ET
    
    return ET_field

def calc_VILD(radar, VIL_name = 'VIL', ET_name = 'ET'):
    return radar.fields[VIL_name]['data'] / radar.fields[ET_name]['data']

def display_decea(list_vols = None, coords = None, hgr_heights = None):
    """
    Cria displays 2x2 par os radares de polarização unica
    
    Parameteros
    -----------
    
    list_vols: list
        Lista contendo os volumes a serem plotados.
    coords: list of tuples
        coordenadas em (lon, lat) para plotar.
    hgt_heights: list of int or float
        alturas acima no nível do mar em m das isoterma de 0 °C e -20 °C
    """
    if coords is None:
        coords = np.asarray([])
    else:
        coords = coords
    for vol in list_vols:
        fig, axs = plt.subplots(2, 2, figsize = [12, 12], constrained_layout = True, subplot_kw={'projection':ccrs.PlateCarree()})
        for ax in axs.ravel():
            [ax.scatter(ll[1], ll[0], marker = 'v', s = 5, color = 'k', zorder = 10) for ll in coords]
        [ax.add_geometries(shape_municipios.geometry, linewidth = 0.25, zorder = 10, facecolor = 'None',
                           edgecolor = 'k', crs=ccrs.PlateCarree()) for ax in axs.ravel()]
        [ax.add_feature(cfeature.BORDERS.with_scale('10m')) for ax in axs.ravel()]
        fig.colorbar(cm.ScalarMappable(ref_norm, ref_cmap), ax = axs.ravel()[0], extend = 'both', ticks = ZH_Ticks,
                     orientation = 'horizontal', aspect = 30, shrink = 0.85, label = '[dBZ]', pad = 0.01)
        fig.colorbar(cm.ScalarMappable(vel_norm, vel_cmap), ax = axs.ravel()[1], extend = 'both', ticks = np.arange(-50, 60, 10),
                     orientation = 'horizontal', aspect = 30, shrink = 0.85, label = '[m/s]', pad = 0.01)
        fig.colorbar(cm.ScalarMappable(mplcolors.Normalize(0, 100), cmaps.wh_bl_gr_ye_re), ax = axs.ravel()[2],
                     extend = 'max', ticks = np.arange(0, 110, 10), orientation = 'horizontal', aspect = 30,
                     shrink = 0.85, label = '[mm]', pad = 0.01)
        fig.colorbar(cm.ScalarMappable(mplcolors.Normalize(0, 100), 'hot_r'), ax = axs.ravel()[3],
                     ticks = np.arange(0, 110, 10), orientation = 'horizontal', aspect = 30,
                     shrink = 0.85, label = '[%]', pad = 0.01)
        try:
            radar = pyart.aux_io.read_gamic(vol)
        except:
            continue
        radar = template.sort_radar(radar)
        gatefilter = pyart.filters.GateFilter(radar)
        gatefilter.exclude_masked('corrected_reflectivity')
        radar = mesh_ppi.main(radar, 'corrected_reflectivity', hgr_heights, 10, 249.5, 'mh2019_95')
        radar_time = pyart.util.datetime_from_radar(radar)
        display = pyart.graph.RadarMapDisplay(radar)
        display.plot_ppi_map('corrected_reflectivity', 0, ax=axs.ravel()[0], resolution='10m', cmap=ref_cmap,
                             norm=ref_norm, colorbar_flag = False)
        display.plot_ppi_map('corrected_velocity', 0, ax=axs.ravel()[1], resolution='10m', cmap=vel_cmap,
                             norm=vel_norm, colorbar_flag = False)
        display.plot_ppi_map('mesh_mh2019_95', 0, ax=axs.ravel()[2], resolution='10m', cmap=cmaps.wh_bl_gr_ye_re,
                             gatefilter=gatefilter, norm=mplcolors.Normalize(0, 100), colorbar_flag = False)
        display.plot_ppi_map('posh', 0, ax=axs.ravel()[3], resolution='10m', cmap='hot_r', vmin = 0, vmax = 100,
                             gatefilter=gatefilter, colorbar_flag = False)
        
        try:
            os.mkdir(f'/mnt/c/Users/User/Desktop/{radar_time:%Y%m%d}')
        except:
            pass
        
        plt.savefig(f'/mnt/c/Users/User/Desktop/{radar_time:%Y%m%d}/{radar_time:%Y%m%d_%H%M}.jpg', dpi = 300, bbox_inches = 'tight')
        plt.close('all')
        
def display_rainbow(list_vols = None, zdr_cal = None, coords = None):
    """
    Cria displays 2x2 par os radares de dupla polarização
    
    Parameteros
    -----------
    
    list_vols: list
        Lista contendo os volumes a serem plotados.
    coords: list of tuples
        coordenadas em (lon, lat) para plotar.
    """
    if coords is None:
        coords = np.asarray([])
    else:
        coords = coords
    for vol in list_vols:
        fig, axs = plt.subplots(2, 2, figsize = [12, 12], constrained_layout = True, subplot_kw={'projection':ccrs.PlateCarree()})
        for ax in axs.ravel():
            [ax.scatter(ll[1], ll[0], marker = 'v', s = 5, color = 'k', zorder = 10) for ll in coords]
        [ax.add_geometries(shape_municipios.geometry, linewidth = 0.25, zorder = 10, facecolor = 'None', edgecolor = 'k', crs=ccrs.PlateCarree()) for ax in axs.ravel()]
        [ax.add_feature(cfeature.BORDERS.with_scale('10m')) for ax in axs.ravel()]
        fig.colorbar(cm.ScalarMappable(ref_norm, ref_cmap), ax = axs.ravel()[0], extend = 'both', ticks = ZH_Ticks, orientation = 'horizontal', aspect = 30,
                     shrink = 0.85, label = '[dBZ]', pad = 0.01)
        fig.colorbar(cm.ScalarMappable(vel_norm, vel_cmap), ax = axs.ravel()[1], extend = 'both', ticks = np.arange(-50, 60, 10), orientation = 'horizontal', aspect = 30, 
                     shrink = 0.85, label = '[m/s]', pad = 0.01)
        fig.colorbar(cm.ScalarMappable(zdr_norm, zdr_cmap), ax = axs.ravel()[2], extend = 'both', ticks = ZDR_Ticks, orientation = 'horizontal', aspect = 30, 
                     shrink = 0.85, label = '[dB]', pad = 0.01)
        fig.colorbar(cm.ScalarMappable(rho_norm, rho_cmap), ax = axs.ravel()[3], extend = 'both', ticks = RHO_Ticks, orientation = 'horizontal', aspect = 30, 
                     shrink = 0.85, label = '[unitless]', pad = 0.01)

        radar = pyart.aux_io.read_gamic(vol)
        if zdr_cal is not None:
            radar.fields['corrected_differential_reflectivity']['data'] = radar.fields['corrected_differential_reflectivity']['data'] - zdr_cal
        radar = correct_vel(radar)
        #radar.time['units'] = 'seconds since' + ' ' + datetime.strptime(radar.metadata['gamic_date'][:-5], '%Y-%m-%dT%H:%M:%S').isoformat()  
        #template.correct_vel(radar, 'sdcsc')
        radar_time = pyart.util.datetime_from_radar(radar)
        #radar_time = datetime.strptime(vol[27:39], '%Y%m%d%H%M')
        display = pyart.graph.RadarMapDisplay(radar)
        
        try:
            display.plot_ppi_map('corrected_reflectivity', 0, ax=axs.ravel()[0], resolution='10m', cmap=ref_cmap, norm=ref_norm, colorbar_flag = False)
            display.plot_ppi_map('vcor_smooth', 0, ax=axs.ravel()[1], resolution='10m', cmap=vel_cmap, norm=vel_norm, colorbar_flag = False)
            display.plot_ppi_map('corrected_differential_reflectivity', 0, ax=axs.ravel()[2], resolution='10m', cmap=zdr_cmap, norm=zdr_norm, colorbar_flag = False)
            display.plot_ppi_map('cross_correlation_ratio', 0, ax=axs.ravel()[3], resolution='10m', cmap=rho_cmap, norm=rho_norm, colorbar_flag = False)
        except:
            continue
        try:
            os.mkdir(f'/mnt/c/Users/User/Desktop/{radar_time:%Y%m%d}')
        except:
            pass
        plt.savefig(f'/mnt/c/Users/User/Desktop/{radar_time:%Y%m%d}/{radar_time:%Y%m%d_%H%M}.jpg', dpi = 300, bbox_inches = 'tight')
        plt.close('all')

def display_edge(list_vols = None, coords = None):
    """
    Cria displays 2x2 par os radares de dupla polarização
    
    Parameteros
    -----------
    
    list_vols: list
        Lista contendo os volumes a serem plotados.
    coords: list of tuples
        coordenadas em (lon, lat) para plotar.
    """
    if coords is None:
        coords = np.asarray([])
    else:
        coords = coords
    for vol in list_vols:
        fig, axs = plt.subplots(2, 2, figsize = [12, 12], constrained_layout = True, subplot_kw={'projection':ccrs.PlateCarree()})
        for ax in axs.ravel():
            [ax.scatter(ll[1], ll[0], marker = 'v', s = 5, color = 'k', zorder = 10) for ll in coords]
        [ax.add_geometries(shape_municipios.geometry, linewidth = 0.25, zorder = 10, facecolor = 'None', edgecolor = 'k', crs=ccrs.PlateCarree()) for ax in axs.ravel()]
        [ax.add_feature(cfeature.BORDERS.with_scale('10m')) for ax in axs.ravel()]
        fig.colorbar(cm.ScalarMappable(ref_norm, ref_cmap), ax = axs.ravel()[0], extend = 'both', ticks = ZH_Ticks, orientation = 'horizontal', aspect = 30,
                     shrink = 0.85, label = '[dBZ]', pad = 0.01)
        fig.colorbar(cm.ScalarMappable(vel_norm, vel_cmap), ax = axs.ravel()[1], extend = 'both', ticks = np.arange(-50, 60, 10), orientation = 'horizontal', aspect = 30, 
                     shrink = 0.85, label = '[m/s]', pad = 0.01)
        fig.colorbar(cm.ScalarMappable(zdr_norm, zdr_cmap), ax = axs.ravel()[2], extend = 'both', ticks = ZDR_Ticks, orientation = 'horizontal', aspect = 30, 
                     shrink = 0.85, label = '[dB]', pad = 0.01)
        fig.colorbar(cm.ScalarMappable(rho_norm, rho_cmap), ax = axs.ravel()[3], extend = 'both', ticks = RHO_Ticks, orientation = 'horizontal', aspect = 30, 
                     shrink = 0.85, label = '[unitless]', pad = 0.01)
        try:
            radar = pyart.aux_io.read_odim_h5(vol)
        except:
            continue
            
        add_instrument_parameters_odim(radar)
        correct_vel(radar, vel_name = 'velocity_horizontal')
        #radar.time['units'] = 'seconds since' + ' ' + datetime.strptime(radar.metadata['gamic_date'][:-5], '%Y-%m-%dT%H:%M:%S').isoformat() 
        #radar.fields['velocity_horizontal']['data'] = -1 * radar.fields['velocity_horizontal']['data']
        radar_time = pyart.util.datetime_from_radar(radar)
        gatefilter = pyart.filters.GateFilter(radar)
        gatefilter.exclude_masked('reflectivity_horizontal')
        display = pyart.graph.RadarMapDisplay(radar)
        
        display.plot_ppi_map('reflectivity_horizontal', 1, ax=axs.ravel()[0], resolution='10m', cmap=ref_cmap, norm=ref_norm, gatefilter = gatefilter, colorbar_flag = False)
        display.plot_ppi_map('vcor_cmean', 1, ax=axs.ravel()[1], resolution='10m', cmap=vel_cmap, norm=vel_norm, gatefilter = gatefilter, colorbar_flag = False)
        display.plot_ppi_map('differential_reflectivity', 1, ax=axs.ravel()[2], resolution='10m', cmap=zdr_cmap, norm=zdr_norm, gatefilter = gatefilter, colorbar_flag = False)
        display.plot_ppi_map('cross_correlation_ratio', 1, ax=axs.ravel()[3], resolution='10m', cmap=rho_cmap, norm=rho_norm, gatefilter = gatefilter, colorbar_flag = False)
        try:
            os.mkdir(f'/mnt/c/Users/User/Desktop/{radar_time:%Y%m%d}')
        except:
            pass
        plt.savefig(f'/mnt/c/Users/User/Desktop/{radar_time:%Y%m%d}/{radar_time:%Y%m%d_%H%M}.jpg', dpi = 300, bbox_inches = 'tight')
        plt.close('all')

def plot_edge(vol, var1 = 'reflectivity_horizontal', var2 = 'velocity_horizontal', var3 = 'differential_reflectivty', var4 = 'cross_correlation_ratio',
              lats_lons = None, save = False, radar_name = 'Lontras'):
    
    radar = pyart.aux_io.read_odim_h5(vol)
    
    radar.instrument_parameters = dict()
    radar.instrument_parameters= {'frequency': {'units': 's-1',
                                                'meta_group': 'instrument_parameters',
                                                'long_name': 'Radiation frequency',
                                                'data': np.array([3e8/0.10706872940063477], dtype=np.float32)},
                                  'radar_beam_width_h': {'units': 'degrees',
                                                         'meta_group': 'radar_parameters',
                                                         'long_name': 'Antenna beam width H polarization',
                                                         'data': np.array([1.0], dtype=np.float32)},
                                  'radar_beam_width_v': {'units': 'degrees',
                                                         'meta_group': 'radar_parameters',
                                                         'long_name': 'Antenna beam width V polarization',
                                                         'data': np.array([1.0], dtype=np.float32)},
                                  'pulse_width': {'units': 'seconds',
                                                  'comments': 'Pulse width',
                                                  'meta_group': 'instrument_parameters',
                                                  'long_name': 'Pulse width',
                                                  'data': np.resize([1e-6], radar.nrays)},
                                  'prt': {'units': 'seconds',
                                          'comments': 'Pulse repetition time. For staggered prt, also see prt_ratio.',
                                          'meta_group': 'instrument_parameters',
                                          'long_name': 'Pulse repetition time',
                                          'data': np.concatenate([np.resize([1/600], radar.nrays - 1245), np.resize([1/600], 784), np.resize([1/1000], 922)])},
                                  'prt_mode': {'comments': 'Pulsing mode Options are: "fixed", "staggered", "dual". Assumed "fixed" if missing.',
                                               'meta_group': 'instrument_parameters', 
                                               'long_name': 'Pulsing mode',
                                               'units': 'unitless',
                                               'data': np.array(['staggered', 'staggered', 'staggered', 'staggered', 'staggered', 'staggered',
                                                              'fixed', 'fixed', 'fixed', 'fixed'], dtype='<S9')},
                                  'prt_ratio': {'units': 'unitless',
                                                'meta_group': 'instrument_parameters',
                                                'long_name': 'Pulse repetition frequency ratio',
                                                'data': np.concatenate([np.resize([4/5], radar.nrays - 1245), np.resize([1], 784), np.resize([1], 922)])},
                                  'unambiguous_range': {'units': 'meters',
                                                        'comments': 'Unambiguous range',
                                                        'meta_group': 'instrument_parameters',
                                                        'long_name': 'Unambiguous range',
                                                        'data': np.concatenate([np.resize([240000], radar.nrays - 1245), np.resize([200000], 784), np.resize([120000], 922)])},
                                  'nyquist_velocity': {'units': 'meters_per_second',
                                                       'comments': 'Unambiguous velocity',
                                                       'meta_group': 'instrument_parameters',
                                                       'long_name': 'Nyquist velocity',
                                                       'data': np.concatenate([np.resize(fundamentals.dual_nyquist(0.10706872940063477, 480, 600), radar.nrays - 1245),
                                                                              np.resize(fundamentals.nyquist(750, 0.10706872940063477), 784),
                                                                              np.resize(fundamentals.nyquist(1000, 0.10706872940063477), 922)])}}
                                                
    
    radar.instrument_parameters['pulse_width']['data'] = radar.instrument_parameters['pulse_width']['data'].astype(np.float32)
    radar.instrument_parameters['prt']['data'] = radar.instrument_parameters['prt']['data'].astype(np.float32)
    radar.instrument_parameters['prt_ratio']['data'] = radar.instrument_parameters['prt_ratio']['data'].astype(np.float32)
    radar.instrument_parameters['unambiguous_range']['data'] = radar.instrument_parameters['unambiguous_range']['data'].astype(np.float32)
    radar.instrument_parameters['nyquist_velocity']['data'] = radar.instrument_parameters['nyquist_velocity']['data'].astype(np.float32)
    
    for n, prt_mode in enumerate(radar.instrument_parameters['prt_mode']['data']):
        if prt_mode ==b'staggered':
            radar.instrument_parameters['prt_mode']['data'][n] = b'dual'
        if prt_mode ==b'fixed':
            radar.instrument_parameters['prt_mode']['data'][n] = b'fixed'
        else:
            pass
        
    radar.instrument_parameters['prt_mode']['data'] = radar.instrument_parameters['prt_mode']['data'].astype('|S5')
    radar.instrument_parameters['prt_ratio']['data'] = 1 / radar.instrument_parameters['prt_ratio']['data']
    
    radar.instrument_parameters['prf_flag'] = {'units': 'unitless',
                                           'comments': 'PRF used to collect ray. 0 for high PRF, 1 for low PRF.',
                                           'meta_group': 'instrument_parameters',
                                           'long_name': 'PRF flag',
                                           'data':np.resize(([0, 1]), radar.nrays)}
    
    radar.fields['velocity_horizontal']['data'] = -1 * radar.fields['velocity_horizontal']['data']
    
    correct_dualprf(radar=radar, two_step=True,
                     method_det='cmean', kernel_det=np.ones((11, 11)),
                     method_cor='cmean', kernel_cor=np.ones((5, 5)),
                     vel_field='velocity_horizontal', new_field='vcor_cmean', replace=True)

    radar.fields['vcor_cmean']['units'] = 'meters_per_second'
    radar.fields['vcor_cmean']['standard_name'] = 'corrected_radial_velocity_of_scatterers_away_from_instrument'
    radar.fields['vcor_cmean']['long_name'] = 'Corrected mean doppler velocity'
    radar.fields['vcor_cmean']['coordinates'] = 'elevation azimuth range'
    
    fig, axs = plt.subplots(2, 2, figsize = [12, 12], constrained_layout = True, subplot_kw={'projection':ccrs.PlateCarree()})
    [ax.add_geometries(shape_municipios.geometry, linewidth = 0.1, zorder = 10, facecolor = 'None', edgecolor = 'k', crs=ccrs.PlateCarree()) for ax in axs.ravel()]
    [ax.add_feature(cfeature.BORDERS.with_scale('10m')) for ax in axs.ravel()]

    fig.colorbar(cm.ScalarMappable(ref_norm, ref_cmap), ax = axs.ravel()[0], extend = 'both', ticks = ZH_Ticks, orientation = 'horizontal', aspect = 30,
                 shrink = 0.85, label = '[dBZ]', pad = 0.01)
    fig.colorbar(cm.ScalarMappable(vel_norm, vel_cmap), ax = axs.ravel()[1], extend = 'both', ticks = np.arange(-50, 60, 10), orientation = 'horizontal', aspect = 30,
                 shrink = 0.85, label = '[m s$^{-1}$]', pad = 0.01)
    fig.colorbar(cm.ScalarMappable(zdr_norm, zdr_cmap), ax = axs.ravel()[2], extend = 'both', ticks = ZDR_Ticks, orientation = 'horizontal', aspect = 30,
                 shrink = 0.85, label = '[dB]', pad = 0.01)
    fig.colorbar(cm.ScalarMappable(rho_norm, rho_cmap), ax = axs.ravel()[3], extend = 'both', ticks = RHO_Ticks, orientation = 'horizontal', aspect = 30,
                 shrink = 0.85, label = '[unitless]', pad = 0.01)

    if lats_lons is not None:
        [ax.set_extent([radar.longitude['data'] + lats_lons[0], radar.longitude['data'] + lats_lons[1], radar.latitude['data'] + lats_lons[2], radar.latitude['data'] + lats_lons[3]]) for ax in axs.ravel()]

    radar_time = pyart.util.datetime_from_radar(radar)

    gatefilter = pyart.filters.GateFilter(radar)
    gatefilter.exclude_masked('reflectivity_horizontal')
    #radar = mesh_ppi.main(radar, 'corrected_reflectivity', [4914.0, 7763.0], 0, 250, 'mh2019_95')

    #VIL = template.calc_VIL(radar, 'corrected_reflectivity')
    #radar.add_field('VIL', dic = {'units':'kg m$^{-2}$',
    #                               'data':VIL, 'standard_name':'Vertically_Integrated_Liquid',
    #                               'long_name':'Vertically Integrated Liquid', 
    #                               'coordinates':'elevation azimuth range'}, replace_existing=True)

    #ET = template.calc_ET(radar, 'corrected_reflectivity')
    #radar.add_field('ET', dic = {'units':'km',
    #                              'data':ET, 'standard_name':'18_dBZ_Echo_Tops',
    #                               'long_name':'18 dBZ Echo Tops', 
    #                               'coordinates':'elevation azimuth range'}, replace_existing=True)

    #VILD = template.calc_VILD(radar, 'VIL', 'ET')
    #radar.add_field('VILD', dic = {'units':'kg m$^{-3}$',
    #                               'data':VILD, 'standard_name':'VIL_Density',
    #                               'long_name':'Vertically Integrated Liquid Density', 
    #                               'coordinates':'elevation azimuth range'}, replace_existing=True)

    display = pyart.graph.RadarMapDisplay(radar)
    display.plot_ppi_map('reflectivity_horizontal', 0, ax=axs.ravel()[0], resolution='10m', cmap = ref_cmap, norm = ref_norm, ticks = ZH_Ticks, colorbar_flag = False)
    display.plot_ppi_map('vcor_cmean', 0, ax=axs.ravel()[1], resolution='10m', cmap = vel_cmap, norm = vel_norm, ticks = np.arange(-50, 60, 10), colorbar_flag = False)
    display.plot_ppi_map('differential_reflectivity', 0, ax=axs.ravel()[2], resolution='10m', cmap = zdr_cmap, norm = zdr_norm, ticks = ZDR_Ticks, colorbar_flag = False, gatefilter=gatefilter)
    display.plot_ppi_map('cross_correlation_ratio', 0, ax=axs.ravel()[3], resolution='10m', cmap = rho_cmap, norm = rho_norm, ticks = RHO_Ticks, colorbar_flag = False, gatefilter=gatefilter)
    #display.plot_ppi_map('VILD', 0, ax=axs.ravel()[2], cmap = cmaps.BkBlAqGrYeOrReViWh200_r, norm = mplcolors.Normalize(0, 10),
    #                     resolution='10m', colorbar_flag = False)
    #display.plot_ppi_map('mesh_mh2019_95', 0, ax=axs.ravel()[2], resolution='10m', cmap=cmaps.wh_bl_gr_ye_re, norm=mplcolors.Normalize(0, 100), colorbar_flag = False)
    #display.plot_ppi_map('posh', 0, ax=axs.ravel()[3], vmin = 0, vmax = 100, resolution='10m', colorbar_flag = False, cmap='hot_r')
    
    if save == True:
        plt.savefig(f'/mnt/c/Users/User/Desktop/{radar_time:%Y%m%d_%H%M%S}.png', bbox_inches = 'tight', dpi = 300)
        
def plot_rainbow(vol, var1 = 'corrected_reflectivity', var2 = 'corrected_velocity', var3 = 'corrected_differential_reflectivty', var4 = 'cross_correlation_ratio',
              lats_lons = None, save = False, radar_name = 'Chapecó'):
    
    radar = pyart.aux_io.read_gamic(vol)
    
    for n, prt_mode in enumerate(radar.instrument_parameters['prt_mode']['data']):
        if prt_mode =='staggered':
            radar.instrument_parameters['prt_mode']['data'][n] = b'dual'
        if prt_mode =='fixed':
            radar.instrument_parameters['prt_mode']['data'][n] = b'fixed'
        else:
            pass
        
    radar.instrument_parameters['prt_mode']['data'] = radar.instrument_parameters['prt_mode']['data'].astype('|S5')
    radar.instrument_parameters['prt_ratio']['data'] = 1 / radar.instrument_parameters['prt_ratio']['data']
    
    radar.instrument_parameters['prf_flag'] = {'units': 'unitless',
                                           'comments': 'PRF used to collect ray. 0 for high PRF, 1 for low PRF.',
                                           'meta_group': 'instrument_parameters',
                                           'long_name': 'PRF flag',
                                           'data':np.resize(([0, 1]), radar.nrays)}
    
    correct_dualprf(radar=radar, two_step=True,
                     method_det='cmean', kernel_det=np.ones((11, 11)),
                     method_cor='cmean', kernel_cor=np.ones((5, 5)),
                     vel_field='corrected_velocity', new_field='vcor_cmean', replace=True)

    radar.fields['vcor_cmean']['units'] = 'meters_per_second'
    radar.fields['vcor_cmean']['standard_name'] = 'corrected_radial_velocity_of_scatterers_away_from_instrument'
    radar.fields['vcor_cmean']['long_name'] = 'Corrected mean doppler velocity'
    radar.fields['vcor_cmean']['coordinates'] = 'elevation azimuth range'
    
    vel_smooth = median_filter(radar.fields['vcor_cmean']['data'], 3)
    smooth_data_ma = np.ma.masked_where(np.ma.getmask(radar.fields['vcor_cmean']['data']), vel_smooth)
    smooth_data_ma = np.ma.masked_equal(smooth_data_ma, smooth_data_ma.min())
    radar.add_field_like('vcor_cmean', 'vcor_cmean', 
                         smooth_data_ma, replace_existing = True)

    
    fig, axs = plt.subplots(2, 2, figsize = [12, 12], constrained_layout = True, subplot_kw={'projection':ccrs.PlateCarree()})
    [ax.add_geometries(shape_municipios.geometry, linewidth = 0.1, zorder = 10, facecolor = 'None', edgecolor = 'k', crs=ccrs.PlateCarree()) for ax in axs.ravel()]
    [ax.add_feature(cfeature.BORDERS.with_scale('10m')) for ax in axs.ravel()]

    fig.colorbar(cm.ScalarMappable(ref_norm, ref_cmap), ax = axs.ravel()[0], extend = 'both', ticks = ZH_Ticks, orientation = 'horizontal', aspect = 30,
                 shrink = 0.85, label = '[dBZ]', pad = 0.01)
    fig.colorbar(cm.ScalarMappable(vel_norm, vel_cmap), ax = axs.ravel()[1], extend = 'both', ticks = np.arange(-50, 60, 10), orientation = 'horizontal', aspect = 30,
                 shrink = 0.85, label = '[m s$^{-1}$]', pad = 0.01)
    fig.colorbar(cm.ScalarMappable(zdr_norm, zdr_cmap), ax = axs.ravel()[2], extend = 'both', ticks = ZDR_Ticks, orientation = 'horizontal', aspect = 30,
                 shrink = 0.85, label = '[dB]', pad = 0.01)
    fig.colorbar(cm.ScalarMappable(rho_norm, rho_cmap), ax = axs.ravel()[3], extend = 'both', ticks = RHO_Ticks, orientation = 'horizontal', aspect = 30,
                 shrink = 0.85, label = '[unitless]', pad = 0.01)

    if lats_lons is not None:
        [ax.set_extent([radar.longitude['data'] + lats_lons[0], radar.longitude['data'] + lats_lons[1], radar.latitude['data'] + lats_lons[2], radar.latitude['data'] + lats_lons[3]]) for ax in axs.ravel()]

    radar_time = pyart.util.datetime_from_radar(radar)

    #radar = mesh_ppi.main(radar, 'corrected_reflectivity', [4914.0, 7763.0], 0, 250, 'mh2019_95')

    #VIL = template.calc_VIL(radar, 'corrected_reflectivity')
    #radar.add_field('VIL', dic = {'units':'kg m$^{-2}$',
    #                               'data':VIL, 'standard_name':'Vertically_Integrated_Liquid',
    #                               'long_name':'Vertically Integrated Liquid', 
    #                               'coordinates':'elevation azimuth range'}, replace_existing=True)

    #ET = template.calc_ET(radar, 'corrected_reflectivity')
    #radar.add_field('ET', dic = {'units':'km',
    #                              'data':ET, 'standard_name':'18_dBZ_Echo_Tops',
    #                               'long_name':'18 dBZ Echo Tops', 
    #                               'coordinates':'elevation azimuth range'}, replace_existing=True)

    #VILD = template.calc_VILD(radar, 'VIL', 'ET')
    #radar.add_field('VILD', dic = {'units':'kg m$^{-3}$',
    #                               'data':VILD, 'standard_name':'VIL_Density',
    #                               'long_name':'Vertically Integrated Liquid Density', 
    #                               'coordinates':'elevation azimuth range'}, replace_existing=True)

    display = pyart.graph.RadarMapDisplay(radar)
    display.plot_ppi_map('corrected_reflectivity', 0, ax=axs.ravel()[0], resolution='10m', cmap = ref_cmap, norm = ref_norm, ticks = ZH_Ticks, colorbar_flag = False)
    display.plot_ppi_map('vcor_cmean', 0, ax=axs.ravel()[1], resolution='10m', cmap = vel_cmap, norm = vel_norm, ticks = np.arange(-50, 60, 10), colorbar_flag = False)
    display.plot_ppi_map('corrected_differential_reflectivity', 0, ax=axs.ravel()[2], resolution='10m', cmap = zdr_cmap, norm = zdr_norm, ticks = ZDR_Ticks, colorbar_flag = False)
    display.plot_ppi_map('cross_correlation_ratio', 0, ax=axs.ravel()[3], resolution='10m', cmap = rho_cmap, norm = rho_norm, ticks = RHO_Ticks, colorbar_flag = False)
    #display.plot_ppi_map('VILD', 0, ax=axs.ravel()[2], cmap = cmaps.BkBlAqGrYeOrReViWh200_r, norm = mplcolors.Normalize(0, 10),
    #                     resolution='10m', colorbar_flag = False)
    #display.plot_ppi_map('mesh_mh2019_95', 0, ax=axs.ravel()[2], resolution='10m', cmap=cmaps.wh_bl_gr_ye_re, norm=mplcolors.Normalize(0, 100), colorbar_flag = False)
    #display.plot_ppi_map('posh', 0, ax=axs.ravel()[3], vmin = 0, vmax = 100, resolution='10m', colorbar_flag = False, cmap='hot_r')
    
    if save == True:
        plt.savefig(f'/mnt/c/Users/User/Desktop/{radar_time:%Y%m%d_%H%M%S}.png', bbox_inches = 'tight', dpi = 300)