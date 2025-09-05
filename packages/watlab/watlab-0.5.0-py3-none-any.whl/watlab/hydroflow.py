"""::
.---.  .---.   ____     __  ______     .-------.        ,-----.     ________   .---.       ,-----.    .--.      .--. 
|   |  |_ _|   \   \   /  /|    _ `''. |  _ _   \     .'  .-,  '.  |        |  | ,_|     .'  .-,  '.  |  |_     |  | 
|   |  ( ' )    \  _. /  ' | _ | ) _  \| ( ' )  |    / ,-.|  \ _ \ |   .----',-./  )    / ,-.|  \ _ \ | _( )_   |  | 
|   '-(_{;}_)    _( )_ .'  |( ''_'  ) ||(_ o _) /   ;  \  '_ /  | :|  _|____ \  '_ '`) ;  \  '_ /  | :|(_ o _)  |  | 
|      (_,_) ___(_ o _)'   | . (_) `. || (_,_).' __ |  _`,/ \ _/  ||_( )_   | > (_)  ) |  _`,/ \ _/  || (_,_) \ |  | 
| _ _--.   ||   |(_,_)'    |(_    ._) '|  |\ \  |  |: (  '\_/ \   ;(_ o._)__|(  .  .-' : (  '\_/ \   ;|  |/    \|  | 
|( ' ) |   ||   `-'  /     |  (_.\.' / |  | \ `'   / \ `"/  \  ) / |(_,_)     `-'`-'|___\ `"/  \  ) / |  '  /\  `  | 
(_{;}_)|   | \      /      |       .'  |  |  \    /   '. \_/``".'  |   |       |        \'. \_/``".'  |    /  \    | 
'(_,_) '---'  `-..-'       '-----'`    ''-'   `'-'      '-----'    '---'       `--------`  '-----'    `---'    `---`

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

# Metadata
__authors__ = "Pierre-Yves Gousenbourger, Sandra Soares-Frazao, Robin Meurice, Charles Ryckmans, Nathan Delpierre, Martin Petitjean"
__contact__ = "pierre-yves.gousenbourger@uclouvain.be"
__copyright__ = "MIT"
__date__ = "2022-09-05"
__version__= "0.3.0"

# internal modules

# external modules contained in requirements.txt
import numpy as np
import os
import sys
from scipy.interpolate import griddata
import subprocess
import shlex
import pandas as pd
from typing import Callable, Union
from .watlab import Mesh, WatlabExport, WatlabModel, _INPUT_NAME, _MESHCHECKER_EDGES_FILE
from .utils import *
import json

_HYDROFLOW_NAME = "hydroflow"
#%%% A name for hydroflow executable
if sys.platform == "win32":
    _HYDROFLOW_EXECUTABLE = _HYDROFLOW_NAME+"-win.exe"
    _HYDROFLOW_PARALLEL_EXECUTABLE = _HYDROFLOW_NAME+"-parallel-win.exe"
elif sys.platform == "darwin":
    _HYDROFLOW_EXECUTABLE = _HYDROFLOW_NAME+"-darwin"
    _HYDROFLOW_PARALLEL_EXECUTABLE = _HYDROFLOW_NAME+"-parallel-darwin"
elif sys.platform == "linux" or sys.platform == "linux2":
    _HYDROFLOW_EXECUTABLE = _HYDROFLOW_NAME+"-linux"
    _HYDROFLOW_PARALLEL_EXECUTABLE = _HYDROFLOW_NAME+"-parallel-linux"
#%%% Corresponds to the initial conditions variables
_INITIAL_WATER_LEVEL = "initial_water_level"
_INITIAL_WATER_DISCHARGE = "initial_water_discharge"
_BEDROCK_LEVEL = "bedrock_level"
_FRICTION_COEFFICIENTS = "friction_coefficients"
#%%% Corresponds to the boundary conditions variables
_TRANSMISSIVE_BOUNDARIES = "transmissive_edges"
_WALL_BOUNDARIES ="wall_edges"
_BOUNDARY_WATER_LEVEL = "boundary_water_level"
_BOUNDARY_WATER_DISCHARGE = "boundary_water_discharge"
_BOUNDARY_HYDROGRAPH = "boundary_hydrograph"
_BOUNDARY_LIMNIGRAM = "boundary_limnigram"
#%%% Corresponds to the source terms variables
_RAINFALL_SOURCE_TERM = "rainfall"
_HYETOCELLS_FILE = "hyetocells.txt"
_HYETOGRAMS_FILE = "hyetograms.txt"

_INFILTRATION_SOURCE_TERM = "infiltration"
_INFILTRATION_FILE = "infiltration.txt" 
_INFILTRACELLS_FILE = "infiltracells.txt"
_INITIAL_INFILTRATION = "initial_infiltration"
_INITIAL_INFILTRATION_FILE = "initial_infiltration.txt"
##### Default values for IO folders
##### Default values for generated files
_FIXED_BED_FILE ="fixed_bed.txt"
_FRICTION_FILE = "friction_values.txt"

# path to hydroflow
_dir_path_to_executable = os.path.join(os.path.dirname(__file__),"bin")
_root_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def get_hydroflow_path():
    """
    Returns
    --------
    String
    Path of the hydroflow.exe folder
    """
    return _dir_path_to_executable


def _compile_code(isParallel=False):
    """
        Compiles the C++ code using g++.
    The compilation is done using the following command:
        g++ -O3 -fopenmp -pthread -o hydroflow src/hydroflow/*.cpp src/hydroflow/writer/*.cpp src/hydroflow/interfaces/*.cpp src/hydroflow/utils/*.cpp src/hydroflow/physicalmodels/*.cpp -std=c++20
    The compilation is done in the directory where the C++ code is located.
    The compilation is done using the subprocess module.
    The subprocess module is used to run the g++ command.
    The shlex module is used to split the command into a list of strings.
    The cwd parameter of the subprocess module is used to specify the directory 
        where the compilation is done.
    """
    relpath = os.path.relpath(_dir_path_to_executable,_root_path).replace('\\','/')
    src_files =  'src/hydroflow/*.cpp src/hydroflow/writer/*.cpp src/hydroflow/interfaces/*.cpp src/hydroflow/utils/*.cpp src/hydroflow/physicalmodels/*.cpp src/hydroflow/utils/Reader.cpp'
    compiler_opt = '-O3 -fopenmp -pthread' if isParallel else ''
    compile_cmd = f"g++ {compiler_opt} -o {relpath}/{_HYDROFLOW_EXECUTABLE} {src_files} -std=c++20 -static"
    
    try:
        subprocess.run(shlex.split(compile_cmd),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=_root_path,
                        text=True, 
                        check=True)
        print("The code has been successfully compiled: the executable has been generated.")
        if isParallel: print("(Parallel version)")
    except subprocess.CalledProcessError as e:
        print("There were compiling errors, the code can not be run:")
        print("Error:", e.stderr)
    
class HydroflowModel(WatlabModel):
    """
    Hydrodynamic simulation model. 
    The simulation model is made of a physical Mesh and is linked to the Export class \n
    This class must be used to design your problem by providing a solver, initial and boundary conditions. 
    The function solve() is used to launch the simulation by calling the C++ solver. 
    """
    def __init__(self,mesh: Mesh):
        """Builder of the Model class. 
        To build a Model object, only a Mesh object is needed. 

        :param mesh: the mesh object describing the physical environment of the problem
        :type mesh: Mesh
        :param export: the export object that will be employed to export the related model data. 
        :type export: HydroflowExport object
        :param initial_conditions_keys: the list of the initial conditions keys that can be employed in the HydroflowModel
        :type initial_conditions_keys: list
        :param boundary_conditions_keys: the list of the boundary conditions keys that can be employed in the HydroflowModel
        :type boundary_conditions_keys: list
        """
        WatlabModel.__init__(self,mesh)
        self.export = HydroflowExport(self._mesh,self)
        #Main parameters of the simulation
        self.__Cfl = 0.90
        #Algorithm parameters
        self._physical_model = "Hydroflow"
        self.__flux_scheme = "LHLLC" # self.__FLUX_SCHEME
        self.__flux_order = 1
        self.__slope_limiter = 0
        #Hydrodynamic part: initialization
        self.__is_fixed_bed_level = 0
        self.__is_friction = 0
        self.__is_sediments = 0
        self.__is_rainfall = 0
        self.__is_infiltration = 0
        self.__is_init_infiltration = 0
        self.__zero_depth_value = 0.0001
        self.initial_conditions_keys.extend([_INITIAL_WATER_LEVEL, _INITIAL_WATER_DISCHARGE, _BEDROCK_LEVEL, _FRICTION_COEFFICIENTS, _RAINFALL_SOURCE_TERM, _INFILTRATION_SOURCE_TERM, _INITIAL_INFILTRATION])
        self.boundary_conditions_keys.extend([_TRANSMISSIVE_BOUNDARIES, _BOUNDARY_WATER_LEVEL, _BOUNDARY_WATER_DISCHARGE, _BOUNDARY_HYDROGRAPH, _BOUNDARY_LIMNIGRAM,_WALL_BOUNDARIES])
        self.id_generator = generate_sourceterm_id()
    
    def export_data(self) -> None: 
        """ 
        Calls the export class to export the needed files in the input folder
        Please inspect the input folder to see the designed problem.
        Informations about initial conditions, nodes, edges or eventual gauges places are included
        """
        self.export.export()

    def solve(self,display=True,isParallel=False) -> None:
        """
        Calls the C++ executable of meshchecker if the parameter meshchecking of mesh is set to True
        Calls the C++ executable and solve the current designed model
        """
        if (self._mesh.meshchecking):
            self._launch_meshchecker(display,isParallel=isParallel)
        self.__launch_code(display,isParallel=isParallel)

    def resume_simulation(self,pic_file,display=True,isParallel=False,isSameMesh=True):
        """Allows the user to restart a simulation from a former pic.txt file.

        :param pic_file: pic.txt file used as initial conditions for the simulation
        :type pic_file: string
        :param display: if True shows the cpp outputed informations, defaults to True
        :type display: bool, optional
        :param isParallel: if True the parallel version of the code is used, defaults to False
        :type isParallel: bool, optional
        :param isSameMesh: if True no interpolation is performed. Initial conditions are not interpolated, defaults to True
        :type isSameMesh: bool, optional
        """
        data = np.loadtxt(pic_file,skiprows=1)
        regions = list(self._mesh.regions.values())
        h_pic, qx_pic, qy_pic = data[:,3], data[:,4], data[:,5]

        if isSameMesh : 
            h_water, qx, qy = h_pic, qx_pic, qy_pic
        else: 
            x_coord_pic,y_coord_pic = data[:,0], data[:,1]
            old_points = np.column_stack((x_coord_pic.flatten(), y_coord_pic.flatten()))  
            X_barycenters, Y_barycenters = self._mesh.get_cells_barycenters()[:,0], self._mesh.get_cells_barycenters()[:,1]
            new_points = np.column_stack((X_barycenters, Y_barycenters))
            
            nearest_grid_h = griddata(old_points, h_pic, new_points, method='nearest')
            h_water = griddata(old_points, h_pic, new_points, method='linear')
            h_water[np.isnan(h_water)] = nearest_grid_h[np.isnan(h_water)]

            nearest_grid_qx = griddata(old_points, qx_pic, new_points, method='nearest')
            qx = griddata(old_points, qx_pic, new_points, method='linear')
            qx[np.isnan(qx)] = nearest_grid_qx[np.isnan(qx)] 
            nearest_grid_qy = griddata(old_points, qy_pic, new_points, method='nearest')
            qy = griddata(old_points, qy_pic, new_points, method='linear')
            qy[np.isnan(qy)] = nearest_grid_qy[np.isnan(qy)] 
            qx[h_water<10**-1], qy[h_water<10**-1] = 0, 0
            
        discharges = np.column_stack((qx,qy))
        for region in regions:
            region_tag = self._mesh.get_region_by_name(region) if isinstance(region,str) else region
            indexes = [self._mesh.tag_to_indexes.get(tag) for tag in self._mesh.region_cells[region_tag]]
            self.set_initial_water_height(str(region),h_water[indexes].tolist())
            self.set_initial_water_discharge(str(region),discharges[indexes].tolist())
        self.export_data()
        if display: print("Input Files Generated")
        self.solve(display,isParallel=isParallel)

    def set_initial_cumulative_infiltration_from_picture(self,pic_file, isSameMesh=True):
        """Allows the user to set the initial cumulative infiltration from a former pic.txt file.

        :param pic_file: pic.txt file used as initial conditions for the simulation
        :type pic_file: string
        :param isSameMesh: if True no interpolation is performed. Initial conditions are not interpolated, defaults to True
        :type isSameMesh: bool, optional
        """
        data = np.loadtxt(pic_file, skiprows=1, usecols=(6))
        regions = list(self._mesh.regions.values())
        f_pic = data

        if isSameMesh : 
            f = f_pic
        else: 
            x_coord_pic,y_coord_pic = data[:,0], data[:,1]
            old_points = np.column_stack((x_coord_pic.flatten(), y_coord_pic.flatten()))  
            X_barycenters, Y_barycenters = self._mesh.get_cells_barycenters()[:,0], self._mesh.get_cells_barycenters()[:,1]
            new_points = np.column_stack((X_barycenters, Y_barycenters))

            nearest_grid_f = griddata(old_points, f_pic, new_points, method='nearest')
            f = griddata(old_points, f_pic, new_points, method='linear')
            f[np.isnan(f)] = nearest_grid_f[np.isnan(f)]
            f[f<0] = 0
            
        for region in regions:
            region_tag = self._mesh.get_region_by_name(region) if isinstance(region,str) else region
            indexes = [self._mesh.tag_to_indexes.get(tag) for tag in self._mesh.region_cells[region_tag]]
            self.set_initial_cumulative_infiltration(str(region),f[indexes].tolist())
        
        # if display: print("Input Files Generated")
        # self.solve(display,isParallel=isParallel)


    ##############################################
    #                                            #
    # Specific properties should be written here #
    #                                            #
    ##############################################
    
    @property
    def Cfl_number(self):
        """Convergence condition by Courant-Friedrichs-Lewy
            Must always be below 1

        :getter: Returns Courant-Friedrichs-Lewy number
        :setter: Sets Courant-Friedrichs-Lewy number
        :type: float
        """
        return self.__Cfl 

    @Cfl_number.setter    
    def Cfl_number(self,Cfl):
        self.__Cfl = Cfl
    
    @property
    def zero_depth_value(self):
        """
        Convergence condition by Courant-Friedrichs-Lewy
            Must always be below 1

        :getter: Returns Courant-Friedrichs-Lewy number
        :setter: Sets Courant-Friedrichs-Lewy number
        :type: float
        """
        return self.__zero_depth_value

    @zero_depth_value.setter    
    def zero_depth_value(self,zero_depth_value):
        self.__zero_depth_value = zero_depth_value
        
    @property
    def flux_scheme(self):
        """Scheme used to compute the fluxes at the interfaces of the mesh
            FOR THE MOMENT ONLY HLLC AVAILABLE

        :getter: returns the flux scheme
        :setter: Sets scheme used to compute the fluxes at the interfaces of each edge (HLLC, Roe or other)
        :type: string
        """
        return self.__flux_scheme

    @flux_scheme.setter
    def flux_scheme(self,flux_scheme):
        self.__flux_scheme = flux_scheme
    
    @property
    def flux_order(self):
        """order used to compute the fluxes

        :getter: returns the order used to compute the fluxes
        :setter: Sets the order used to compute the fluxes (1 or 2)
        :type: int (default : 1)
        """
        return self.__flux_order

    @flux_order.setter
    def flux_order(self,flux_order):
        self.__flux_order = flux_order
    
    @property
    def slope_limiter(self):
        """ This function assigns slope_limiter

        :getter: returns the slope_limiter
        :setter: 1 or 2 ???
        :type: int (default : 0)
        """
        return self.__slope_limiter

    @slope_limiter.setter
    def slope_limiter(self,slope_limiter):
        self.__slope_limiter = slope_limiter

    @property 
    def is_fixed_bed_level(self):
        """Indicates to the c++ code if there is a fixed bed level
        :return: 0 or 1 
        :rtype: Boolean of type int (0,1)
        """
        return self.__is_fixed_bed_level

    @property
    def is_friction(self):
        """Indicates to the c++ code if there is friction to be considered

        :return: 0 or 1 
        :rtype: Boolean of type int (0,1)
        """
        return self.__is_friction

    @property
    def is_sediments(self):
        """Indicates to the c++ code if there is sediments to be considered

        :return: 0 or 1 
        :rtype: Boolean of type int (0,1)
        """
        return self.__is_sediments  
    
    @property
    def is_rainfall(self):
        """Indicates to the c++ code if there is rainfall to be considered

        :return: 0 or 1 
        :rtype: Boolean of type int (0,1)
        """
        return self.__is_rainfall
    
    @property
    def is_infiltration(self):
        """Indicates to the c++ code if there is infiltration to be considered

        :return: 0 or 1 
        :rtype: Boolean of type int (0,1)
        """
        return self.__is_infiltration
     
    @property
    def is_init_infiltration(self):
        """
        Indicates to the c++ code if there is initial cumulative infiltration to be considered
        
        :return: 0 or 1
        :rtype: Boolean of type int (0,1)
        """
        return self.__is_init_infiltration
    
    #############################################
    #                                           #
    # Initial conditions should be written here #
    #                                           #
    #############################################    
    def set_initial_water_height(self,regions,water_heights):
        """Sets the initial water height to the cells in the domain.    
           If only one value is given, all cells will get the same value.

        :param regions: the regions names (string) or the regions tags (int)
        :type regions: string or int
        :param water_heights: the values to be given to the cells in the correspondant region. 
        :type water_heights: float or list
        """
        tags = []
        def __initial_water_height(tags,water_heights,region):
            region_indexes = [self._mesh.tag_to_indexes.get(tag) for tag in tags]
            initial_conditions = self.get_initial_conditions()
            if _BEDROCK_LEVEL in initial_conditions.keys():
                bedrock_level = np.asarray(initial_conditions[_BEDROCK_LEVEL][1])[region_indexes]
            else:
                bedrock_level = self._mesh.get_cells_barycenters()[region_indexes,2]
            #evaluate water levels, since water levels are the initial condition                
            if isinstance(water_heights,(int, float)) : water_levels = water_heights*np.ones(len(region_indexes))+bedrock_level
            else:                                       water_levels = water_heights+bedrock_level
            self._set_initial_conditions(region,water_levels.tolist(),_INITIAL_WATER_LEVEL)
            
        if isinstance(regions,list) or isinstance(regions,tuple):
            for index,region in enumerate(regions): 
                tags = self._mesh.region_cells[self._mesh.get_region_by_name(region)] 
                __initial_water_height(tags,water_heights[index],region)
        else:  
            tags = self._mesh.region_cells[self._mesh.get_region_by_name(regions)] 
            __initial_water_height(tags,water_heights,regions)      
        
    def set_initial_water_level(self,regions,water_levels):
        """Sets the initial water levels to the cells in the domain.
           
        If only one value is given, all cells will get the same value.

        :param regions: the regions names (string) or the regions tags (int)
        :type regions: string or int
        :param water_levels: the values to be given to the cells in the correspondant region. 
        :type water_levels: float or list
        """
        self._set_initial_conditions(regions,water_levels, _INITIAL_WATER_LEVEL)
    
    def set_initial_water_discharge(self,regions,discharges):
        """Sets the initial water levels to the cells in the domain.
        
        If only one value is given, all cells will get the same value.

        :param regions: the regions names (string) or the regions tags (int)
        :type regions: string or int
        :param discharges: the values to be given to the cells in the correspondint region. 
                           Each entry must be composed of two elements (discharge x and discharge y).
        :type discharges: List
        """
        self._set_initial_conditions(regions,discharges,_INITIAL_WATER_DISCHARGE)
        
    def set_bedrock_level(self,regions:str|int|list,bedrock_levels: Union[float, list, Callable[[float, float], float]]):
        """Sets the initial bedrock level to the cells in the domain. Either a constant value or a function can be provided.

        :param regions: the regions names (string) or the regions tags (int)
        :type regions: list(string, int), string or int
        :param bedrock_levels: the values to be given to the cells in the corresponding region.
        :type bedrock_levels: float or list
        """
        self.__is_fixed_bed_level = 1
        if bedrock_levels is None:
            raise Exception("You must provide a value or a function to set the bedrock level")
        self._set_initial_conditions(regions,bedrock_levels,_BEDROCK_LEVEL)
    
    def set_friction_coefficient(self,regions,friction_coefficients):
        """Sets the friction coefficients associated to each cell in the domain.
        
        If only one value is given, all cells will get the same value.

        :param regions: the regions names (string) or the regions tags (int)
        :type regions: string or int
        :param friction_coefficients: the values to be given to the cells in the corresponding region. 
        :type friction_coefficients: float or list or .tif file 
        """
        self.__is_friction = 1 
        self._set_initial_conditions(regions,friction_coefficients,_FRICTION_COEFFICIENTS)

    def set_initial_cumulative_infiltration(self,regions, Ft):
        """Sets the initial cumulative infiltration to the cells in the domain.
        
        If only one value is given, all cells will get the same value.

        :param regions: the regions names (string) or the regions tags (int)
        :type regions: string or int
        :param Ft: the values to be given to the cells in the corresponding region. 
        :type Ft: float or list
        """
        self.__is_init_infiltration = 1
        self._set_initial_conditions(regions,Ft,_INITIAL_INFILTRATION)

    def set_rainfall_intensity(self,regions,hyetogram, units="mm/h", dt:int=60):
        """Set a given rainfall intensity to the cells of given regions.
        
        :param regions: the regions names (string) or the regions tags (int)
        :type regions: list(string, int), string or int
        :param hyetogram: the values to be given to the cells in the corresponding region. Could be a constant value for the duration of the simulation or a list of tuples (time, intensity)
        :type hyetogram: float or list(tuple)
        :param units: the units of the hyetogram, defaults to "mm/h". Supported units are "mm/h" and "m/s"
        :type units: string
        :param dt: the time step to use for the hyetogram in seconds, defaults to 60. 
        If it is bigger than the smallest time step of the hyetogram, it will be set to the smallest time step of the hyetogram
        :type dt: int, optional
        """
        # Check if negative values are present in the hyetogram
        if units not in ["mm/h", "m/s"]:
            raise ValueError("The units must be 'mm/h' or 'm/s'")
        self.__is_rainfall = 1
        hyetogram = self.__hyetogram_format(hyetogram)
        # Check if the hyetogram is empty
        if len(hyetogram["values"]) == 0:
            raise ValueError("The hyetogram is empty, please provide a valid hyetogram")
        if any(i[1] < 0 for i in hyetogram["values"]):
            raise ValueError("The hyetogram contains negative values, please provide a valid hyetogram")
        if (units == "mm/h"):
            # Modification of the hyetogram to be in m/s
            hyetogram["values"] = [(i[0], i[1]/3600/1000) for i in hyetogram["values"]]
        if (dt > self.__max_dt(hyetogram) and dt > 0 and self.__max_dt(hyetogram) != -1):
            # print(f"[Rainfall] dt > smallest step, setting to {self.__max_dt(hyetogram)}")
            dt = self.__max_dt(hyetogram)
        elif dt <= 0:
            raise ValueError("dt must be positive")
        hyetogram["dt"] = dt
        # Check if the time of the last value of the hyetogram is lower than the simulation time
        if self.ending_time > hyetogram["values"][-1][0] and len(hyetogram["values"]) > 1 and hyetogram["values"][-1][1] != 0:
            print(f"[WARNING] The simulation time end after the hyetogram set to the region(s) \"{regions}\". " + \
                  "A good practice is to have the hyetogram last value equals to the simulation time.")
        self._set_source_term(regions,hyetogram, hyetogram["id"], _RAINFALL_SOURCE_TERM)

    def __hyetogram_format(self, hyetogram_raw):
        nid = next(self.id_generator)
        hyetogram = {
            "type": "hyetogram",
            "id": nid,
        }
        if isinstance(hyetogram_raw, (float, int)):
            hyetogram["steps"] = 1
            hyetogram["values"] = [(0, hyetogram_raw)]
        elif isinstance(hyetogram_raw, (tuple,list)):
            # Check if the list is composed of tuples of two elements, who are both numbers
            if all(isinstance(i, (tuple,list)) and len(i) == 2 and all(isinstance(j, (float, int)) for j in i) for i in hyetogram_raw):
                hyetogram["steps"] = len(hyetogram_raw)
                hyetogram["values"] = hyetogram_raw
            else:
                raise ValueError(f"The hyetogram must be a float or a list of tuples (time, intensity), given: {hyetogram_raw}")
        else:
            raise ValueError(f"The hyetogram must be a float or a list of tuples (time, intensity), given: {hyetogram_raw}")
        return hyetogram
    
    def __max_dt(self, hyetogram):
        if hyetogram["steps"] == 1:
            return -1
        return min([hyetogram["values"][i+1][0] - hyetogram["values"][i][0] for i in range(hyetogram["steps"]-1)])

    def set_rainfall_intensity_from_spw_file(self,regions,hyetogram_path:str, dt=60, initial_time="1970-01-01 00:00"):
        """Set a given hyetogram to the cells of given regions using a SPW file. Units are extracted from the file.

        :param regions: the regions names (string) or the regions tags (int)
        :type regions: list(string, int), string or int
        :param hyetogram_path: the path to the SPW file (in xlsx format)
        :type hyetogram_path: string
        :param dt: the time step to use for the hyetogram in seconds, defaults to 60
        :type dt: int, optional
        :param initial_time: the initial time of the simulation, defaults to "1970-01-01 00:00"
        :type initial_time: string
        """
        initial_time = parse_date(initial_time)
        df_hyetogram = pd.read_excel(hyetogram_path)

        df_hyetogram = [(i[0], i[1]) for i in df_hyetogram.values]
        file_unit = df_hyetogram[5][1] # The unit is in the 6th row

        if file_unit == "millimeter":
            units = "mm/h"
        elif file_unit == "meter":
            units = "m/s"
        else:
            raise ValueError(f"Unknown unit {file_unit}")
        
        df_hyetogram = np.array([(i[0], float(i[1])) for i in df_hyetogram if not str(i[0]).startswith("#")])
        df_hyetogram[:,0] = parse_date(df_hyetogram[:,0])
        start_time = df_hyetogram[0][0]

        initial_time = start_time if start_time >= initial_time else initial_time

        if initial_time not in df_hyetogram[:,0]: # we need to create the start of the hyetogram
            last_value = df_hyetogram[df_hyetogram[:,0] < initial_time][-1]
            last_value = [initial_time, last_value[1]]
            df_hyetogram = df_hyetogram[df_hyetogram[:,0] >= initial_time]
            df_hyetogram = np.concatenate((np.array([last_value]), df_hyetogram), axis=0)
        else:
            df_hyetogram = df_hyetogram[df_hyetogram[:,0] >= initial_time]
        df_hyetogram = [(i[0], i[1]) for i in df_hyetogram if i[0] >= initial_time]
        
        df_hyetogram = [(int(i[0].timestamp()-initial_time.timestamp()), i[1]) for i in df_hyetogram]
        self.set_rainfall_intensity(regions, df_hyetogram, units=units, dt=dt)

    def set_rainfall_intensity_from_csv_file(self,regions:str|int|list,hyetogram_path, units,dt=60, initial_time="1970-01-01 00:00"):
        """Set a given hyetogram to the cells of given regions using a standardized CSV file.
        
        :param regions: the regions names (string) or the regions tags (int)
        :type regions: list(string, int), string or int 
        :param hyetogram_path: the path to the CSV file
        :type hyetogram_path: string
        :param units: the units of the hyetogram, defaults to "mm/h". Supported units are "mm/h" and "m/s"
        :type units: string
        :param dt: the time step to use for the hyetogram in seconds, defaults to 60
        :type dt: int, optional
        :param initial_time: the initial time of the simulation, defaults to "1970-01-01 00:00"
        :type initial_time: string
        """
        initial_time = parse_date(initial_time)
        df_hyetogram = pd.read_csv(hyetogram_path)
        if "Time" not in df_hyetogram.columns or "Intensity" not in df_hyetogram.columns:
            raise ValueError("The CSV file must have 'Time' and 'Intensity' columns")
        
        df_hyetogram["Time"] = parse_date(df_hyetogram["Time"])
        
        start_time = df_hyetogram["Time"][0]
        initial_time = start_time if start_time >= initial_time else initial_time

        if initial_time not in df_hyetogram["Time"].values: # we need to create the start of the hyetogram
            last_value = df_hyetogram[df_hyetogram["Time"] < initial_time].iloc[-1]
            last_value = [initial_time, last_value["Intensity"]]
            df_hyetogram = df_hyetogram[df_hyetogram["Time"] >= initial_time]
            df_hyetogram = pd.concat([pd.DataFrame([last_value], columns=["Time", "Intensity"]), df_hyetogram], ignore_index=True)
        else:
            df_hyetogram = df_hyetogram[df_hyetogram["Time"] >= initial_time]
        df_hyetogram = df_hyetogram[["Time", "Intensity"]].values.tolist()

        df_hyetogram = [(int(i[0].timestamp()-initial_time.timestamp()), i[1]) for i in df_hyetogram]
        self.set_rainfall_intensity(regions, df_hyetogram, units=units, dt=dt)

    def __infiltration_format(self, type, parameters):
        nid = next(self.id_generator)
        infiltration = {
            "type": type,
            "id": nid,
            "parameters": parameters
        }
        return infiltration
    
    def set_infiltration(self, regions:str|int|list, type:str, parameters:list):
        """
        Set a given infiltration model to the cells of given regions.

        You are not supposed to call this function directly, but rather use a specific infiltration model.
        """
        self.__is_infiltration = 1
        infiltration = self.__infiltration_format(type, parameters)
        self._set_source_term(regions, infiltration, infiltration["id"], _INFILTRATION_SOURCE_TERM)

    def set_green_ampt_infiltration_model(self, regions:str|int|list, Ks:float, Psi:float, hum_init:float, hum_sat:float, Ho:float, ds:float):
        """Set the Green-Ampt infiltration model to the cells of given regions.

        :param regions: the regions names (string) or the regions tags (int) on which the infiltration model is applied
        :type regions: list(string, int), string or int

        :param Ks: The saturated hydraulic conductivity. Must be positive.
        :type Ks: float [m/s]

        :param Psi: The average suction head at the wetting front. Must be positive.
        :type Psi: float [m]

        :param hum_init: The initial water content
        :type hum_init: float [m3/m3]

        :param hum_sat: The saturated water content. Must be greater than hum_init and less than 1
        :type hum_sat: float [m3/m3]

        :param Ho: Maximal storage capacity of the soil, expressed in water equivalent. Theoretically corresponds to the soil depth times the average porosity. Must be positive.
        :type Ho: float [m]

        :param ds: Coefficient of exponential emptying of the infiltrated layer, simulating the drainage of the soil. 
                   A value of 1 leads to a daily drainage rate of 63% (=1-exp(-1)) and a hourly drainage rate of 4% (=1-exp(-1/24)).
                   Should be between 0 (no drainage) and infinity (instantaneous drainage). Must be positive.
        :type ds: float [1/day]
        """
        if Ks < 0:
            raise ValueError("Ks must be positive")
        if Psi < 0:
            raise ValueError("Psi must be positive")
        if hum_init > hum_sat or hum_init < 0 or hum_sat > 1:
            raise ValueError("The initial water content must be between 0 and the saturated water content")
        if Ho < 0:
            raise ValueError("Ho must be positive")
        if ds < 0:
            raise ValueError("ds must be positive")
        ds = ds / 86400 # Convert to 1/s

        self.set_infiltration(regions, "GreenAmpt", [Ks, Psi, hum_init, hum_sat, Ho, ds])

    def set_horton_infiltration_model(self, regions:str|int|list, f0:float, fc:float, k:float, S:float, ds:float):
        """Set the Horton infiltration model to the cells of given regions.

        :param regions: the regions names (string) or the regions tags (int) on which the infiltration model is applied
        :type regions: list(string, int), string or int
        :param f0: Initial infiltration capacity. Must be positive and greater than fc.
        :type f0: float [m/s]
        :param fc: Final infiltration capacity. Must be positive and lower than f0.
        :type fc: float [m/s]
        :param k: Coefficient of exponential decay of the infiltration capacity. Must be positive.
        :type k: float [1/m]
        :param S: Maximal storage capacity of the soil, expressed in water equivalent. Theoretically corresponds to the soil depth times the average porosity. Must be positive.
        :type S: float [m]
        :param ds: Coefficient of exponential emptying of the infiltrated layer, simulating the drainage of the soil. 
                   A value of 1 leads to a daily drainage rate of 63% (=1-exp(-1)) and a hourly drainage rate of 4% (=1-exp(-1/24)).
                   Should be between 0 (no drainage) and infinity (instantaneous drainage). Must be positive.
        :type ds: float [1/day]
        """
        if f0 < 0:
            raise ValueError("f0 must be positive")
        if fc < 0:
            raise ValueError("fc must be positive")
        if fc > f0:
            raise ValueError("fc must be lower than f0")
        if k < 0:
            raise ValueError("k must be positive")
        if S < 0:
            raise ValueError("S must be positive")
        if ds < 0:
            raise ValueError("ds must be positive")
        ds = ds / 86400
        self.set_infiltration(regions, "Horton", [f0, fc, k, S, ds])
        
        
    
    ##############################################
    #                                            #
    # Boundary conditions should be written here #
    #                                            #
    ##############################################
    def set_wall_boundaries(self,boundaries):
        """Defines which edges behave like wall interfaces.


        :param boundaries: the boundary names (string) or the boundary tags (int)
                           where the edges behave like wall interfaces.
        :type boundaries: string or int
        """
        # fictive value for transmissive boundaries
        values = True if isinstance(boundaries,str) else [True]*np.size(boundaries)
        self._set_boundary_conditions(boundaries,values,_WALL_BOUNDARIES)
        
    def set_transmissive_boundaries(self,boundaries):
        """Defines which edges behave like a transmissive interfaces.


        :param boundaries: the boundary names (string) or the boundary tags (int)
                           where the edges behave like transmissive interfaces.
        :type boundaries: string or int
        """
        # fictive value for transmissive boundaries
        values = True if isinstance(boundaries,str) else [True]*np.size(boundaries)
        self._set_boundary_conditions(boundaries,values,_TRANSMISSIVE_BOUNDARIES)

    def set_boundary_water_level(self,boundaries,water_levels):
        """Defines the imposed water level at edges of the boundaries.
        
        :param boundaries: the boundary names (string) or the boundary tags (int)
        :type boundaries: string or tag
        :param water_levels: the values to be given to the edges in the corresponding boundary.
        :type water_levels: float or list
        """
        self._set_boundary_conditions(boundaries,water_levels,_BOUNDARY_WATER_LEVEL)
        
    def __corrected_water_discharge(self,boundary,water_discharge):
        boundary_length = self._mesh.get_boundary_length(boundary)
        return -water_discharge/boundary_length
        
    def set_boundary_water_discharge(self,boundaries,water_discharges):
        """Defines the imposed water discharge through the edges of the boundaries.
        You must introduce the total discharge. Positive value flows in the system
        
        :param boundaries: the boundary names (string) or the boundary tags (int)
        :type boundaries: string or int
        :param water_discharges: the values to be given to the edges in the corresponding boundary.
        :type water_discharges: float or list
        """ 
        if isinstance(boundaries,list) or isinstance(boundaries,tuple):
            for i,boundary in enumerate(boundaries):
                water_discharge = self.__corrected_water_discharge(boundary,water_discharges[i])
                self._set_boundary_conditions(boundary,water_discharge,_BOUNDARY_WATER_DISCHARGE)
        else:
            self._set_boundary_conditions(boundaries,self.__corrected_water_discharge(boundaries,water_discharges),_BOUNDARY_WATER_DISCHARGE)
        
    def set_boundary_hydrograph(self,boundaries,hydrograph_paths, linear_discharge_correction=True, initial_hydrogram_correct = False):
        """
        Sets a hydrograph type of boundary condition.
        This method assigns time-varying discharge (hydrograph) boundary conditions to the specified 
        boundaries in the model. It supports various input formats including Excel files, text files,
        and numpy arrays/lists. 
    
        Your input file must be organized as follows:
        
        For Excel files, the first two columns will be interpreted as time and discharge values.
        For text files or arrays, data should be structured as two columns: time (s) and discharge.
        :param boundaries: The boundary names (string) or the boundary tags (int). Can be a single 
                          boundary or a list/tuple of boundaries.
        :type boundaries: str, int, list, tuple
        :param hydrograph_paths: The paths of the hydrographs associated with the boundaries.
                                If boundaries is a list/tuple, this should be a list of corresponding
                                hydrograph paths. Can be file paths (Excel or txt) or 2D arrays/lists
                                with time and discharge values.
        :type hydrograph_paths: str, list, numpy.ndarray
        :param linear_discharge_correction: Whether to divide the discharge by the length of the boundary.
                                           Default is True.
        :type linear_discharge_correction: bool
        :param initial_hydrogram_correct: Whether to apply initial hydrograph correction.
        :type initial_hydrogram_correct: bool
        :raises ValueError: If the hydrograph format is not supported.
        :return: None
        """
        
        def __correct_excel_hydrograph(hydrograph_path,boundary, hydrograph_corrected_name):
            hydrograph_corrected = pd.read_excel(hydrograph_path,usecols=[0,1])
            time_name, discharge_name = hydrograph_corrected.columns.values
            hydrograph_corrected[time_name] = pd.to_datetime(hydrograph_corrected[time_name], format='%d-%m-%y %H:%M')
            hydrograph_corrected['Time (s)'] = round((hydrograph_corrected[time_name] - hydrograph_corrected[time_name].iloc[0]).dt.total_seconds()).astype(int)
            if linear_discharge_correction:
                hydrograph_corrected[discharge_name] = self.__corrected_water_discharge(boundary,hydrograph_corrected[discharge_name])
            with open(hydrograph_corrected_name, "w") as f:
                f.write(str(len(hydrograph_corrected)) + "\n")
            hydrograph_corrected[['Time (s)', discharge_name]].to_csv(hydrograph_corrected_name, sep='\t', header=False, index=False, mode='a')
        
        def __correct_array_hydrograph(data, boundary, hydrograph_corrected_name):
            if linear_discharge_correction:
                data[:,1] = self.__corrected_water_discharge(boundary, data[:,1])
            with open(hydrograph_corrected_name, "w") as f:
                f.write(str(len(data)) + "\n")
            with open(hydrograph_corrected_name,'ab') as f:
                np.savetxt(f,data, delimiter=" ", fmt="%1.6f")

        def __process_hydrograph(boundary, hydrograph_path):
            if isinstance(hydrograph_path, (np.ndarray, list)) and np.array(hydrograph_path).ndim == 2 and np.array(hydrograph_path).shape[1] == 2:
                data = np.array(hydrograph_path)
                hydrograph_corrected_name = f"hydrograph_{str(boundary).replace(' ', '_')}_corrected.txt"
                __correct_array_hydrograph(data, boundary, hydrograph_corrected_name)
                self._set_boundary_conditions(boundary, hydrograph_corrected_name, _BOUNDARY_HYDROGRAPH)
            
            elif isinstance(hydrograph_path, str) and hydrograph_path.endswith('xlsx'):
                hydrograph_corrected_name = hydrograph_path.split(".")[0] + "_corrected.txt"
                __correct_excel_hydrograph(hydrograph_path, boundary, hydrograph_corrected_name)
                self._set_boundary_conditions(boundary, hydrograph_corrected_name, _BOUNDARY_HYDROGRAPH)
                
            elif isinstance(hydrograph_path, str) and hydrograph_path.endswith('txt') and initial_hydrogram_correct == False: 
                hydrograph_corrected_name = hydrograph_path.split(".")[0] + "_corrected.txt"
                data = np.loadtxt(hydrograph_path)
                __correct_array_hydrograph(data, boundary, hydrograph_corrected_name)
                self._set_boundary_conditions(boundary, hydrograph_corrected_name, _BOUNDARY_HYDROGRAPH)
            
            elif isinstance(hydrograph_path, str) and hydrograph_path.endswith('txt') and initial_hydrogram_correct: 
                self._set_boundary_conditions(boundary, hydrograph_path, _BOUNDARY_HYDROGRAPH)
                
            elif hydrograph_path:
                self._set_boundary_conditions(boundary, hydrograph_path, _BOUNDARY_HYDROGRAPH)
                raise ValueError(f"Unsupported hydrograph format for {hydrograph_path}")


        if isinstance(boundaries, list) or isinstance(boundaries, tuple): 
            for i, boundary in enumerate(boundaries):
                __process_hydrograph(boundary, hydrograph_paths[i])
        else:
            __process_hydrograph(boundaries, hydrograph_paths)

    def set_boundary_limnigram(self,boundaries,limnigram_paths):
        """Sets a limnigram type of boundary condition
        
        :param boundaries: the boundary names (string) or the boundary tags (int)
        :type boundaries: string or int
        :param limnigram_paths: the paths of the limnigrams associated to the edges 
                                in the corresponding boundary.
        :type limnigram_paths: string or list
        """
        self._set_boundary_conditions(boundaries,limnigram_paths,_BOUNDARY_LIMNIGRAM)

    def get_boundary_conditions(self):
        """Returns the boundary conditions in a dictionary"""
       
        conditions = self.get_conditions(self.boundary_conditions_keys)
        keys = conditions.keys()
        if _TRANSMISSIVE_BOUNDARIES in keys:
            conditions[_TRANSMISSIVE_BOUNDARIES] = conditions[_TRANSMISSIVE_BOUNDARIES][0]
        if _WALL_BOUNDARIES in keys:
            conditions[_WALL_BOUNDARIES] = conditions[_WALL_BOUNDARIES][0]
        return conditions
    
    def __launch_code(self,display=True,isParallel=False):
        """
        This function launches the Hydroflow code.
        It first checks if the Hydroflow code exists in the Hydroflow folder.
        If it does not exist, it compiles the code.
        Then, it launches the Hydroflow code.
        The Hydroflow code is launched with the following input:
        - the path to the data.txt file
        # """
        if isParallel : 
            EXEC_NAME = _HYDROFLOW_PARALLEL_EXECUTABLE
        else :
            EXEC_NAME = _HYDROFLOW_EXECUTABLE

        if os.path.exists(os.path.join(_dir_path_to_executable,EXEC_NAME)):
            if display: print(EXEC_NAME + " exists")
        else:
            if display: print("The code is being compiled...")
            _compile_code(isParallel=isParallel)
            
        if display: print("Launching the executable ...")  
        
        data_file_path = self.export.data_file_path
        executable_cmd = os.path.join(_dir_path_to_executable, EXEC_NAME)

        args = [executable_cmd, '-f', data_file_path]
        
        process = subprocess.Popen(args, 
                                   stdout = subprocess.PIPE, 
                                   stderr = subprocess.STDOUT,
                                   cwd = self._current_path)
        if display:
            for c in iter(lambda: process.stdout.readline(1), b""):
                sys.stdout.buffer.write(c)
                sys.stdout.flush()
        process.wait()

class HydroflowExport(WatlabExport):
    """Exports the input files
    
    :param mesh: a mesh object from the hydroflow lib
    :type mesh: mesh
    :param model: a model object
    :type model: model
    """
    # Class variables 

    def __init__(self, mesh: Mesh, model: HydroflowModel):
        """
        Constructs the Mesh object based on an .msh file.
        """
        WatlabExport.__init__(self,mesh,model)
        self.boundary_conditions_code =  {
            _TRANSMISSIVE_BOUNDARIES : -2,
            _BOUNDARY_WATER_LEVEL : -4, 
            _BOUNDARY_WATER_DISCHARGE : -3,
            _BOUNDARY_HYDROGRAPH : -33,
            _BOUNDARY_LIMNIGRAM : -44,
            _WALL_BOUNDARIES : -5}
        self.model = model

    def export(self):
        """Export all .txt files in the input folder:
        
        :return: self.__NODES_NAME, self.__CELLS_NAME, self.__EDGES_NAME, self.__INITIAL_CONDITIONS_NAME, self.__FRICTION_NAME
            self.__BOUNDARY_NAME, self.__PICTURE_NAME, self.__DATA_NAME, self.__SEDIMENT_LEVEL_NAME
        :rtype: .txt    
        """
        os.makedirs(self._INPUT_FOLDER_PATH,exist_ok=True)
        os.makedirs(self._OUTPUT_FOLDER_PATH,exist_ok=True)
        #Basic Watlab exports 
        self._export_watlab_basic_data()
        #Adapted exports for Hydroflow
        self._export_hydrodynamics_data()
        self._export_sources()
        self.__export_data()
    
    def _export_hydrodynamics_data(self):
        """A private function that exports the boundary conditions, the initial conditions, the friction coeff., the bedrock levels and the rainfall intensities.
        """
        self._export_edges()
        self._export_initial_conditions()
        self._export_friction()
        self._export_bedrock_level()
        self._export_hyetocells()
        self._export_infiltracells() # C'est vraiment mal fait faut changer cette logique
        self._export_initial_infiltration()
    
    @property
    def friction_file_path(self):
        return os.path.join(self.input_folder_name,_FRICTION_FILE)
    
    @property
    def fixed_bedrock_level_path(self):
        return os.path.join(self.input_folder_name,_FIXED_BED_FILE)
    
    @property
    def hyetocells_file_path(self):
        return os.path.join(self.input_folder_name,_HYETOCELLS_FILE)
    
    @property
    def hyetograms_file_path(self):
        return os.path.join(self.input_folder_name,_HYETOGRAMS_FILE)
    
    @property
    def infiltracells_file_path(self):
        return os.path.join(self.input_folder_name,_INFILTRACELLS_FILE)
    
    @property
    def infiltration_file_path(self):
        return os.path.join(self.input_folder_name,_INFILTRATION_FILE)
    
    @property
    def initial_infiltration_file_path(self):
        return os.path.join(self.input_folder_name,_INITIAL_INFILTRATION_FILE)
    
    
    def _export_edges(self):
        """Exports the edges from the GSMH mesh to a file.

        :return: A text file containing the number of edges, the corresponding nodes and if requested, 
            the left and right adjacent cells.
            First line: n_edges
            Each following line is formatted as [left_cell_tag, right_cell_tag, node_tag_1, node_tag_2, boundary_condition_code, value_boundary_condition (double or string)].
        :rtype: .txt
        """
        if (self._mesh.meshchecking):
            output_path = os.path.join(self.input_folder_name,_MESHCHECKER_EDGES_FILE)
        else:
            output_path = self.edges_file_path
        f = open(output_path,'w')
        f.write(str(self._mesh.nEdges)+'\n')
        f.close()

        # preparing output
        fmt = '%d', '%d', '%d', '%d', '%s', '%s'
        tags,edge_nodes,edge_cells = self._mesh.edges
        edge_cells[edge_cells != -1] = [self._mesh.tag_to_indexes.get(tag) for tag in edge_cells[edge_cells != -1]]

        output = np.hstack((edge_cells,edge_nodes-1))

        used_boundary_conditions = self.model.get_boundary_conditions().keys()
        bc_value =  np.empty(len(tags),dtype=object)
        bc_code =  -np.ones(len(tags),dtype=int)
        bc_value[:] = np.nan

        ### due to reordering, index <-> tag has changed
        tag_to_indices = {tag: index for index, tag in enumerate(tags)}

        for condition in used_boundary_conditions: 
            if condition == _TRANSMISSIVE_BOUNDARIES or condition == _WALL_BOUNDARIES:
                condition_edge = np.asarray(self.model.get_boundary_conditions()[condition])
                indices = [tag_to_indices[tg] for tg in condition_edge]
                # output[indices,1] = self.boundary_conditions_code[condition]
            else:   
                condition_edge = np.asarray(self.model.get_boundary_conditions()[condition][0])
                indices = [tag_to_indices[tg] for tg in condition_edge]
                condition_value = np.asarray(self.model.get_boundary_conditions()[condition][1])
                # output[indices,1] = self.boundary_conditions_code[condition]
                bc_value[indices] = condition_value
            bc_code[indices] = self.boundary_conditions_code[condition]
            
        output = pd.DataFrame(output)
        output['bc_code'] = bc_code
        output['bc_valeur'] = bc_value
        output.fillna(value='', inplace=True)

        with open(output_path,'ab') as f:
            np.savetxt(f,output.values, delimiter=" ", fmt=fmt)

    def _export_initial_conditions(self):
        """Exports the water and discharge initial conditions to a file."""
        fmt = '%1.6f','%1.6f','%1.6f'
        initial_conditions = self.model.get_initial_conditions()
        initial_export_conditions = np.zeros((self._mesh.nCells,3))

        if _INITIAL_WATER_LEVEL not in initial_conditions:
            pass 
        else:
            water_level = np.array([initial_conditions[_INITIAL_WATER_LEVEL][1]]).T
            water_level_cells_tags = initial_conditions[_INITIAL_WATER_LEVEL][0]
            water_level_cells_index = [self._mesh.tag_to_indexes.get(tag) for tag in water_level_cells_tags]
            initial_export_conditions[water_level_cells_index,0] = water_level.reshape(len(water_level),)

        if _INITIAL_WATER_DISCHARGE not in initial_conditions:
            pass 
        else:
            discharge = np.array(initial_conditions[_INITIAL_WATER_DISCHARGE][1])
            discharge_cells_tags = initial_conditions[_INITIAL_WATER_DISCHARGE][0]
            discharge_cells_index  = [self._mesh.tag_to_indexes.get(tag) for tag in discharge_cells_tags]
            initial_export_conditions[discharge_cells_index,1:3] = discharge.reshape(len(discharge),2)
            
        np.savetxt(self.initial_conditions_file_path,initial_export_conditions, delimiter=" ", fmt=fmt)
    
    def _export_sources(self):
        """Exports the sources data to files."""
        sources = self.model.source_terms
        for source in sources:
            path = self.__source_file_path(source)
            if path is None:
                raise ValueError(f"Source {source} is not recognized. Cannot export.")
            source_data = sources[source]
            with open(path,'w') as f:
                f.write(f"{len(source_data)}\n") # reset the file and write the number of elements
            if source == _RAINFALL_SOURCE_TERM:
                for s in source_data:
                    with open(path,'a') as f:
                        f.write(f"{s['id']} {s['steps']} {s['dt']}\n")
                        for step in s['values']:
                            f.write(f"{step[0]} {step[1]}\n")
            elif source == _INFILTRATION_SOURCE_TERM:
                for s in source_data:
                    with open(path,'a') as f:
                        f.write(f"{s['id']} {s['type']}\n")
                        for param in s['parameters']:
                            f.write(f"{param} ")
                        f.write("\n")

    def __source_file_path(self,source):          
        if source == _RAINFALL_SOURCE_TERM:
            return self.hyetograms_file_path
        elif source == _INFILTRATION_SOURCE_TERM:
            return self.infiltration_file_path
        else:
            return None

    def _export_friction(self):
        """Exports the friction coefficients to a file.
            Those coefficients are retrieved from the `initial_conditions` dictionary using the key specified in `self.model_variables_dic["FRICTION_COEFFICIENTS"]`. 
            If this key is not present in the dictionary, the function does nothing.
        
        :return: an array is saved to a file with the filename being the concatenation of the folder path, INPUT_NAME, and get_FRICTION_NAME. The output format is specified using the `fmt` variable.
        :rtype: .txt
        """
        self._export_cell_data(_FRICTION_COEFFICIENTS,self.friction_file_path)
    
    def _export_bedrock_level(self):
        """Exports the initial bedrock level to a file.
            The initial bedrock level is retrieved from the `initial_conditions` dictionary using the key specified in `self._model_variables_dic["BEDROCK_LEVEL"]`. 
            If this key is not present in the dictionary, the function does nothing.

        :return: an array is saved to a file with the filename being the concatenation of the folder path, INPUT_NAME, and BEDROCK_NAME. 
            The output format is specified using the `fmt` variable.
        :rtype: .txt
        """
        self._export_cell_data(_BEDROCK_LEVEL,self.fixed_bedrock_level_path)

    def _export_hyetocells(self):
        """
        Exports the hyetocells to a file.

        The hyetocells are retrieved from the `initial_conditions` dictionary using the key specified in `self.model_variables_dic["HYETOCELLS"]`. 
        If this key is not present in the dictionary, the function does nothing.
        """
        self._export_cell_binding(_RAINFALL_SOURCE_TERM,self.hyetocells_file_path)

    def _export_infiltracells(self):
        """
        Exports the infiltracells to a file.

        The infiltracells are retrieved from the `initial_conditions` dictionary using the key specified in `self.model_variables_dic["INFILTRACELLS"]`. 
        If this key is not present in the dictionary, the function does nothing.
        """
        self._export_cell_binding(_INFILTRATION_SOURCE_TERM,self.infiltracells_file_path)

    def _export_initial_infiltration(self):
        """
        Exports the initial infiltration to a file.

        The initial infiltration is retrieved from the `initial_conditions` dictionary using the key specified in `self.model_variables_dic["INITIAL_INFILTRATION"]`. 
        If this key is not present in the dictionary, the function does nothing.
        """
        self._export_cell_data(_INITIAL_INFILTRATION,self.initial_infiltration_file_path)

    def __export_data(self,write=True):
        """Generates a json file where the informations about the model and the mesh are summarized
            This function will delete the EDGES_NAME file if existing and clean all the pics in the Output folder.

        :return: A json file containing the parameters of the simulation
        :rtype: .json (write=True) or dictionnary with the parameters of the simulation (write=False)
        """
        input_data = {  'name' : self.model.name,
                        't0' : self.model.starting_time,
                        'tend' : self.model.ending_time,
                        'CFL' : self.model.Cfl_number,
                        'mesh' : 
                        {
                            'nodes' : self.nodes_file_path,
                            'cells' : self.cells_file_path,
                            'edges' : self.edges_file_path 
                        },
                        'model':
                        {
                            'name': self.model.physical_model,
                            'flux scheme': self.model.flux_scheme,
                            # 'reconstruction order': self.model.flux_order, #currently unused
                            'conditions' : {
                                'initial conditions' : self.initial_conditions_file_path    
                            
                            },
                            'sources' : {},
                        },
                        'extensions' : {},
                        'output' :
                        {
                            'folder': os.path.normcase(self._OUTPUT_FOLDER_NAME+"/"),
                            'time step enveloppe of results': self.model.time_step_enveloppe
                        }
                    }
        
        # if self.model.flux_order==2 : input_data['model']['slope limiter'] = self.model.slope_limiter
        if self.model.zero_depth_value != 0.0001 : input_data['model']['zero depth value'] = self.model.zero_depth_value
        if self.model.is_fixed_bed_level : input_data['model']['conditions']['fixed bed level'] = self.fixed_bedrock_level_path
        if self.model.is_friction : input_data['model']['conditions']['friction'] = self.friction_file_path
        if self.model.is_rainfall : 
            input_data['model']['sources']['hyetocells'] = self.hyetocells_file_path
            input_data['model']['sources']['rainfall'] = self.hyetograms_file_path
        if self.model.is_infiltration :
            input_data['model']['sources']['infiltracells'] = self.infiltracells_file_path
            input_data['model']['sources']['infiltration'] = self.infiltration_file_path
        if self.model.is_init_infiltration : 
            input_data['model']['sources']['initial infiltration'] = self.initial_infiltration_file_path

        if self.model.is_picture : input_data['output']['snapshots of flow'] = self.pictures_file_path
        if self.model.is_gauge : input_data['output']['gauges'] = self.gauge_file_path
        if self.model.is_discharge_measurement_section : input_data['output']['discharges'] = self.discharge_measurement_section_file_path
        
        #If write it will create data.json, if not it will return dictionnary with data to be completed by the sediflow,...
        if (write):
            input_data = {key: value for key, value in input_data.items() if value not in [{}]} #Clean extensions: {} before printinf if no extensions used by the simulation
            with open(self.data_file_path, 'w') as f:
                json.dump(input_data,f,indent=3)
        else :
            return input_data
# %%
