# -*- coding: utf-8 -*- 
"""::

  _    _           _            __ _               
 | |  | |         | |          / _| |              
 | |__| |_   _  __| |_ __ ___ | |_| | _____      __
 |  __  | | | |/ _` | '__/ _ \|  _| |/ _ \ \ /\ / /
 | |  | | |_| | (_| | | | (_) | | | | (_) \ V  V / 
 |_|  |_|\__, |\__,_|_|  \___/|_| |_|\___/ \_/\_/  
          __/ |                                    
         |___/

This module includes functions and classes to pilot hydroflow.

Usage:
======

Insert here the description of the module


License
=======

Copyright (C) <1998 – 2024> <Université catholique de Louvain (UCLouvain), Belgique> 
	
List of the contributors to the development of Watlab: see AUTHORS file.
Description and complete License: see LICENSE file.
	
This program (Watlab) is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program (see COPYING file).  If not, 
see <http://www.gnu.org/licenses/>.

"""
import rasterio 
import numpy as np 
from scipy.interpolate import griddata
from pandas import to_datetime
import os
import pandas as pd
from netCDF4 import Dataset

def extract_values_from_tif(tif_file):
    """_summary_

    :param tif_file: _description_
    :type tif_file: _type_
    :return: _description_
    :rtype: _type_
    """
    with rasterio.open(tif_file) as dataset:
                image_data = dataset.read()
                transform = dataset.transform
                # Get the x and y coordinates of the top-left corner of the image
                x_origin = transform.c
                y_origin = transform.f
                # Get the x and y coordinates of the bottom-right corner of the image
                x_end = x_origin + (dataset.width * transform.a) + transform.a
                y_end = y_origin + (dataset.height * transform.e) + transform.e
                x_coords, y_coords = np.meshgrid(np.linspace(x_origin, x_end, dataset.width), np.linspace(y_origin, y_end, dataset.height))
                data = image_data[0]
            
    tif_points_coordinates = np.column_stack((x_coords.flatten(), y_coords.flatten()))
    tif_points_data = data.flatten()
    return tif_points_coordinates, tif_points_data

def interpolate_points(known_points_coordinates,known_points_data,desired_points,interpolation_method='nearest'):
    """_summary_

    :param known_points_coordinates: _description_
    :type known_points_coordinates: _type_
    :param known_points_data: _description_
    :type known_points_data: _type_
    :param desired_points: _description_
    :type desired_points: _type_
    :return: _description_
    :rtype: _type_
    """
    desired_points_x,  desired_points_y  = desired_points[:,0], desired_points[:,1]
    mesh_points = np.column_stack((desired_points_x.flatten(), desired_points_y.flatten()))
    return griddata(known_points_coordinates, known_points_data, mesh_points, method=interpolation_method)

def generate_sourceterm_id():
    """Génère un numéro incrémental à chaque appel."""
    count = 0
    while True:
        yield count
        count += 1

def parse_date(date_string):
    try:
        return to_datetime(date_string, format='mixed')
    except:
        raise ValueError("The date string is not in the correct format. Please provide a date string in the format 'YYYY-MM-DD HH:MM'")


def post_processed_gauge(pic_path_template, time_step, variable_names, node_index, output_file_path):
    """
    Process gauge data for one or multiple variables.

    :param pic_path_template: Template for file paths.
    :type pic_path_template: str
    :param time_step: Time step between files.
    :type time_step: int
    :param variable_names: List of variable names to extract.
    :type variable_names: list of str
    :param node_index: Index of the node to extract data for.
    :type node_index: int
    :param output_file_path: Path to save the output CSV file.
    :type output_file_path: str
    """
    time_second = 0
    time_hundreds = 0
    data = {var: [] for var in variable_names}
    time = []

    while os.path.exists(pic_path_template.format(time_second, time_hundreds)):
        file = pic_path_template.format(time_second, time_hundreds)
        file_data = pd.read_csv(file, sep='\s+')
        for var in variable_names:
            data[var].append(file_data[var][node_index])
        time.append(time_second)
        time_second += time_step

    gauge_data = {"time": time}
    for var in variable_names:
        gauge_data[var] = data[var]

    output_df = pd.DataFrame(gauge_data)
    output_df.to_csv(output_file_path, index=False)
  
def select_postprocessing_variable(data, variable_name, manning_values=None):
        """
        Selects the variable to plot based on the variable_name.
        :param data: The data extracted from the picture file.
        :type data: np.ndarray or pd.DataFrame  
        :param variable_name: The name of the variable to plot. 
        :type variable_name: str
        :return: The variable to plot.
        """
        match variable_name:
            case "h" | "height":
                variable = data["h"].values
            case "zb":
                variable = data["zb"].values   
            case "zw":
                variable = data["zb"].values + data["h"].values  # zw = zb + h
            case "V" | "velocity":
                variable = np.sqrt(data["qx"].values**2 + data["qy"].values**2)/ data["h"].values  # V = sqrt(qx^2 + qy^2) / h                                
            case "qx":
                variable = data["qx"].values
            case "qy":
                variable = data["qy"].values
            case "Fr" | "Froude":
                # Froude number: Fr = V / sqrt(g * h)
                variable = np.sqrt(data["qx"].values**2 + data["qy"].values**2) / data["h"].values / np.sqrt(9.81*data["h"].values)   
            case "Shear stress" | "tau":
                velocity = np.sqrt(data["qx"].values**2 + data["qy"].values**2) / (data["h"].values) 
                Sf = manning_values**2 * velocity**2 / (data["h"].values**(4/3))
                variable = 9.81 * data["h"].values * Sf * 1000 # tau = rho * g * h * Sf
            case _:
                if hasattr(data, "columns") and variable_name in data.columns:
                    variable = data[variable_name].values
                else:
                    raise ValueError(f"Unknown variable_name: {variable_name}")
        return variable

def post_processed_maximal_values(pic_path_template, time_step, output_file_name, variable_names=None,manning_values=None):    
    """
    Process and extract the maximal values of specified variables from a series of pictures files over time.
    :param pic_path_template: Template path to the pictures files, with placeholders for time formatting.
    :type pic_path_template: str
    :param time_step: Time step increment (in seconds) between consecutive files.
    :param output_file_name: Name of the output CSV file to save the maximal values.
    :param variable_names: List of variable names to extract and process. If None, all variables are extracted.
    :param manning_values: Optional Manning values to be used in variable selection.
    :type manning_values: list or None
    :return: None. The function writes the maximal values to the specified output file.
    :rtype: None
    """
    time_second = 0
    time_hundreds = 00
    data= pd.read_csv(pic_path_template.format(time_second, time_hundreds), sep='\s+')
    
    overall_max = {
        "x": data["x"].values,
        "y": data["y"].values,
        "zb": data["zb"].values
    }
    for var in variable_names:
        overall_max[var] = np.zeros(len(data))
    
    while os.path.exists(pic_path_template.format(time_second, time_hundreds)):
        data = pd.read_csv(pic_path_template.format(time_second, time_hundreds), sep='\s+')
        for var in variable_names:
            variable = select_postprocessing_variable(data,variable_name=var, manning_values=manning_values)
            overall_max[var] = np.maximum(overall_max[var], variable)
        time_second += time_step
        print(f"Processed time: {time_second} seconds")

    pd.DataFrame(overall_max).to_csv(output_file_name, index=False, sep='\t')
    return overall_max

def create_netcdf_mesh(output_file, nodes_file, cells_file, EPSG_CODE="25831"):
    nodes = np.loadtxt(nodes_file, skiprows=1) 
    triangles = np.loadtxt(cells_file, dtype=int, skiprows=1)[:, 1:]  
    
    n_nodes = nodes.shape[0]
    n_faces = triangles.shape[0]
    max_face_nodes = triangles.shape[1]

    ncfile = Dataset(output_file, mode="w", format="NETCDF4")
    ncfile.createDimension("nodes", n_nodes)
    ncfile.createDimension("faces", n_faces)
    ncfile.createDimension("max_face_nodes", max_face_nodes)

    mesh_var = ncfile.createVariable("mesh", "i4")
    mesh_var.setncattr("cf_role", "mesh_topology")
    mesh_var.setncattr("topology_dimension", 2)
    mesh_var.setncattr("node_coordinates", "x y")
    mesh_var.setncattr("face_node_connectivity", "connectivity")
    
    scr = ncfile.createVariable("scr", "i4")
    scr.grid_mapping_name = "latitude_longitude"
    scr.epsg_code = "EPSG:" + EPSG_CODE

    x_var = ncfile.createVariable("x", "f8", ("nodes",))
    y_var = ncfile.createVariable("y", "f8", ("nodes",))
    zb_var = ncfile.createVariable("zb", "f8", ("nodes",))

    x_var.standard_name = "X coordinates"    
    y_var.standard_name = "Y coordinates"
    x_var.grid_mapping = "scr"
    y_var.grid_mapping = "scr"
        
    x_var[:] = nodes[:, 0]
    y_var[:] = nodes[:, 1]
    zb_var[:] = nodes[:, 2]

    connectivity = ncfile.createVariable("connectivity", "i4", ("faces", "max_face_nodes"))
    connectivity.setncattr("long_name", "Face to node connectivity")
    connectivity.setncattr("start_index", 0)  # 0-based indexing
    connectivity[:, :] = triangles
    return ncfile 
    
def generate_netcdf_file_from_picture(nodes_file, cells_file, friction_values, pic_path_template, output_file,max_time, time_step, EPSG_CODE="25831",initial_time=0):
    """Generate a NetCDF file from mesh and field data.
    :param nodes_file: Path to the file containing node coordinates.
    :type nodes_file: str
    :param cells_file: Path to the file containing mesh connectivity (triangles).
    :type cells_file: str
    :param manning_values: Path to the file containing Manning's n values or a list of values.
    :type manning_values: str or list
    :param pic_path_template: template for the picture file paths, with placeholders for time formatting.
    :type pic_path_template: str    
    :param output_file: Path to the output NetCDF file.
    :type output_file: str
    :param max_time: Maximum time for the simulation in seconds.
    :type max_time: int
    :param time_step: Time step for the simulation in seconds.
    :type time_step: int
    """

    manning_values = np.loadtxt(friction_values)

    ncfile = create_netcdf_mesh(output_file, nodes_file, cells_file, EPSG_CODE=EPSG_CODE)
    
    n_timesteps = int(max_time/time_step)  # number of files/timesteps
    ncfile.createDimension("time", n_timesteps)
    time_var = ncfile.createVariable("time", "f8", ("time",))
    time_var[:] = np.arange(initial_time, max_time, time_step)  # time in seconds
  
    h_var = ncfile.createVariable("h", "f8", ("time", "faces"))
    h_var.setncattr("location", "face")
    h_var.setncattr("units", "m")
    h_var.setncattr("standard_name", "Water depth")

    u_var = ncfile.createVariable("u_velocity", "f8", ("time", "faces"))
    u_var.setncattr("location", "face")
    u_var.setncattr("units", "m/s")

    v_var = ncfile.createVariable("v_velocity", "f8", ("time", "faces"))
    v_var.setncattr("location", "face")
    v_var.setncattr("units", "m/s")
    
    
    velocity_var = ncfile.createVariable("velocity", "f8", ("time", "faces"))
    velocity_var.setncattr("location", "face")
    velocity_var.setncattr("units", "m/s")

    shear_stress_var = ncfile.createVariable("shear_stress", "f8", ("time", "faces"))
    shear_stress_var.setncattr("location", "face")
    shear_stress_var.setncattr("units", "Pa")
     
    # Field values
    time_second = 0
    t_index = 0 
    
    while time_second < max_time:
        data = pd.read_csv(pic_path_template.format(time_second, 0), sep=r'\s+')
        
        h = data["h"].values
        qx = data["qx"].values
        qy = data["qy"].values

        u_velocity = qx / h
        v_velocity = qy / h

        velocity = np.sqrt(qx**2 + qy**2) / h
        velocity = np.nan_to_num(velocity, nan=0.0)  
        
        Sf = manning_values**2 * velocity**2 / (h**(4/3))
        shear_stress = 9.81 * h * Sf * 1000  # in Pascals
        shear_stress = np.nan_to_num(shear_stress, nan=0.0)  

        h_var[t_index, :] = h
        u_var[t_index, :] = u_velocity
        v_var[t_index, :] = v_velocity
        velocity_var[t_index, :] = velocity
        
        shear_stress_var[t_index, :] = shear_stress
        time_second += time_step
        t_index += 1

    ncfile.sync()
    ncfile.close()
    print("✅ NetCDF file 'output.nc' created successfully.")
