"""::

   .-'''-.     .-''-.   ______     .-./`)  ________   .---.       ,-----.    .--.      .--. 
  / _     \  .'_ _   \ |    _ `''. \ .-.')|        |  | ,_|     .'  .-,  '.  |  |_     |  | 
 (`' )/`--' / ( ` )   '| _ | ) _  \/ `-' \|   .----',-./  )    / ,-.|  \ _ \ | _( )_   |  | 
(_ o _).   . (_ o _)  ||( ''_'  ) | `-'`"`|  _|____ \  '_ '`) ;  \  '_ /  | :|(_ o _)  |  | 
 (_,_). '. |  (_,_)___|| . (_) `. | .---. |_( )_   | > (_)  ) |  _`,/ \ _/  || (_,_) \ |  | 
.---.  \  :'  \   .---.|(_    ._) ' |   | (_ o._)__|(  .  .-' : (  '\_/ \   ;|  |/    \|  | 
\    `-'  | \  `-'    /|  (_.\.' /  |   | |(_,_)     `-'`-'|___\ `"/  \  ) / |  '  /\  `  | 
 \       /   \       / |       .'   |   | |   |       |        \'. \_/``".'  |    /  \    | 
  `-...-'     `'-..-'  '-----'`     '---' '---'       `--------`  '-----'    `---'    `---` 
This module includes functions and classes to pilot sediflow, the sediment transport module of the Watlab suite.



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
__version__= "0.0.1"

from .watlab import Mesh
from .hydroflow import HydroflowModel, HydroflowExport
import numpy as np
from scipy.interpolate import griddata
import os
import json

# Export keys
_SEDIMENTS_LEVEL_FILE = "sediments_level.txt"
_FIXED_BANK_FILE = "fixed_banks.txt"

# Conditions keys
_BOUNDARY_SEDIMENTS_DISCHARGE = "boundary_sediments_discharge"
_INITIAL_SEDIMENTS_LEVEL = "initial_sediments_level"
_FIXED_BANKS = "fixed_banks"


class SediflowModel(HydroflowModel):
    """
    Simulation model that must be employed for the sediment transport simulations. 
    The simulation model is made of a physical Mesh and is linked to the Export class \n
    This class must be used to design your problem by providing a solver, initial and boundary conditions. 
    The function solve() is used to launch the simulation by calling the C++ solver. 
    """
    def __init__(self,mesh: Mesh):
        HydroflowModel.__init__(self,mesh) 
        self.export = SediflowExport(self._mesh,self)
        self._physical_model = "Sediflow"
        self.__is_sediments = True
        self.__is_initial_sediment_level = 0
        self.__g_d50 = 0.0017
        self.__g_sed_density = 2.65
        self.__g_sed_manning = 0.0167
        self.__g_sed_porosity = 0.44
        #bank-failure tool (only if sediments)
        self.__is_bank_failure = 0
        self.__critical_emmerged_friction_angle = 87.0
        self.__critical_immerged_friction_angle = 35.0
        self.__residual_emmerged_friction_angle = 85.0
        self.__residual_immerged_friction_angle = 30.0
        # conditions
        self.initial_conditions_keys.extend([_INITIAL_SEDIMENTS_LEVEL,_FIXED_BANKS])
        self.boundary_conditions_keys.extend([_BOUNDARY_SEDIMENTS_DISCHARGE])
        
    @property
    def is_sediments(self):
        """Indicates to the c++ code if there is sediments must be considered

        :return: True or False
        :rtype: Boolean
        """
        return self.__is_sediments

    @property    
    def is_initial_sediment_level(self):
        """Indicates to the c++ code the initial level of the sediments

        :return: 0 or 1 
        :rtype: Boolean of type int (0,1)
        """
        return self.__is_initial_sediment_level

    @property
    def sediment_mean_grain_diameter(self):
        """Sediment mean grain diameter 

        :getter: returns mean diameter of the sediments grain
        :setter: sets the mean diameter of the sediments grain
        :type: float
        """
        return self.__g_d50

    @sediment_mean_grain_diameter.setter
    def sediment_mean_grain_diameter(self,g_d50):
        self.__g_d50 = g_d50

    @property
    def sediment_density(self):
        """Sediment grain density
        
        :getter: returns the density sediments grain
        :setter: sets the density of the sediments grain
        :type: float
        """
        return self.__g_sed_density

    @sediment_density.setter
    def sediment_density(self,sed_density):
        self.__g_sed_density = sed_density
    
    @property
    def sediment_friction_coefficient(self):
        """Sediment friction coefficient of Manning Type
        
        :getter: returns the sediments friction coefficient
        :setter: sets the sediments friction coefficient
        :type: float
        """
        return self.__g_sed_manning
    
    @sediment_friction_coefficient.setter
    def sediment_friction_coefficient(self,g_sed_manning):
        self.__g_sed_manning = g_sed_manning
    
    @property
    def sediment_porosity(self):
        """Sediment porosity
        
        :getter: returns the sediments porosity
        :setter: sets the sediments porosity : default 0.4
        :type: float
        """
        return self.__g_sed_porosity
    
    @sediment_porosity.setter
    def sediment_porosity(self,g_sed_porosity):
        self.__g_sed_porosity = g_sed_porosity
    
    @property
    def is_bank_failure(self):
        """Indicates to the c++ code if the bank failure module must be considered

        :return: 0 or 1 
        :rtype: Boolean of type int (0,1)
        """
        return self.__is_bank_failure
    
    @property
    def critical_emmerged_friction_angle(self):
        """ The critical emmerged friction angle has to be used with the bank failure module
            It describes the stability angle of an emmerged part of sediments
            This value has to be greater than the residual friction angle
            
        :getter: returns the value of the emmerged friction angle
        :setter: impose the emmerged friction angle
        :type: float
        """
        return self.__critical_emmerged_friction_angle
    
    @critical_emmerged_friction_angle.setter
    def critical_emmerged_friction_angle(self,phi_ce):
        self.__critical_emmerged_friction_angle = phi_ce
        self.__is_bank_failure = 1

    @property
    def critical_immerged_friction_angle(self):
        """ The critical immerged friction angle has to be used with the bank failure module
            It describes the stability angle of an immerged part of sediments
            This value has to be greater than the residual friction angle
            
        :getter: returns the value of the immerged friction angle
        :setter: impose the immerged friction angle
        :type: float
        """
        return self.__critical_immerged_friction_angle
    
    @critical_immerged_friction_angle.setter
    def critical_immerged_friction_angle(self,phi_ci):
        self.__critical_immerged_friction_angle = phi_ci
        self.__is_bank_failure = 1

    @property
    def residual_emmerged_friction_angle(self):
        """ The residual emmerged friction angle has to be used with the bank failure module
            It describes the residual stability angle of an emmerged part of sediments
            This value has to be lower than the critical friction angle
            
        :getter: returns the residual value of the emmerged friction angle
        :setter: impose the residual emmerged friction angle
        :type: float
        """
        return self.__residual_emmerged_friction_angle
    
    @residual_emmerged_friction_angle.setter
    def residual_emmerged_friction_angle(self,phi_re):
        self.__residual_emmerged_friction_angle = phi_re
        self.__is_bank_failure = 1

    @property
    def residual_immerged_friction_angle(self):
        """ The residual immerged friction angle has to be used with the bank failure module
            It describes the residual stability angle of an immerged part of sediments
            This value has to be lower than the critical friction angle
            
        :getter: returns the residual value of the immerged friction angle
        :setter: impose the residual immerged friction angle
        :type: float
        """
        return self.__residual_immerged_friction_angle
    
    @residual_immerged_friction_angle.setter
    def residual_immerged_friction_angle(self,phi_ri):
        self.__residual_immerged_friction_angle = phi_ri
        self.__is_bank_failure = 1
    
    def set_initial_sediments_level(self,region,sediment_levels=0,slope=False,x_imposed=[],y_imposed=[],z_imposed=[],level_fun=None):
        """Sets the initial sediment levels for a given region.
        If only one value is given, all cells will get the same value.

        :param regions: the regions names (string) or the regions tags (int)
        :type regions: string or int
        :param sediment_levels: The initial sediment levels to be set, defaults to 0
        :type sediment_levels: int, optional
        :param slope: Flag to indicate if the sediment levels should be set according to a slope. Defaults to False.
        :type slope: bool, optional
        :param x_imposed: List of x-coordinates for the points defining the slope. Required if slope is True., defaults to []
        :type x_imposed: list, optional
        :param y_imposed: List of y-coordinates for the points defining the slope. Required if slope is True., defaults to []
        :type y_imposed: list, optional
        :param z_imposed: List of z-coordinates (sediment levels) for the points defining the slope. Required if slope is True., defaults to []
        :type z_imposed: list, optional
        :param level_fun: function to described the sediments levels, defaults to None
        :type level_fun: function, optional
        :raises Exception: If region is a string and there is no region with the given name in the regions list.
        """
        self.__is_initial_sediment_level = 1 
        if slope == False and level_fun is None: 
            self._set_initial_conditions(region,sediment_levels,_INITIAL_SEDIMENTS_LEVEL)
        else:
            region_tag = self._mesh.get_region_by_name(region) if isinstance(region,str) else region
            if not(region_tag in list(self._mesh.regions.keys())):
                raise Exception("There is no such region in regions. Region tag: "+str(region))

            cell_tags = self._mesh.region_cells[region_tag].tolist()
            indexes = [self._mesh.tag_to_indexes.get(tag) for tag in cell_tags]

            X = self._mesh.get_cells_barycenters()[indexes,0]
            Y = self._mesh.get_cells_barycenters()[indexes,1]
            if slope == True:
                sediment_levels = griddata((x_imposed, y_imposed), z_imposed, (X, Y), method='linear').tolist()
            else:
                sediment_levels = list(map(level_fun,X,Y))
            self._set_initial_conditions(region,sediment_levels,_INITIAL_SEDIMENTS_LEVEL)
    
    def set_fixed_banks(self,regions):
        """
        IN CONSTRUCTION
        Defines if (True or False) the cell can be eroded or not.

        :param regions: (list) the regions names (string) or the regions tags (int)
        :param is_bank_fixed: (list) the values to be given to the cells in 
            the correspondint region. All the cells of the region will get the same value.
        :returns: (method)
        """
        # fictive value for fixed banks
        values = True if np.size(regions) == 1 else [True]*np.size(regions)
        self._set_initial_conditions(regions,values,_FIXED_BANKS)
    
    def set_boundary_sediments_discharge(self,boundaries,sediments_discharges):
        """Defines the imposed sediment discharge through the edges of the boundaries.
        You must introduce a negative flux and a flux/m of boundary
        
        :param boundaries: the boundary names (string) or the boundary tags (int)
        :type boundaries: string or int
        :param sediments_discharges: the values to be given to the edges in the corresponding boundary.
        :type sediments_discharges: float or list
        """
        self._set_boundary_conditions(boundaries,sediments_discharges,_BOUNDARY_SEDIMENTS_DISCHARGE)

    def get_initial_conditions(self):
        """Returns the initial conditions in a dictionary"""
        conditions = self.get_conditions(self.initial_conditions_keys)
        keys = conditions.keys()
        if _FIXED_BANKS in keys:
            conditions[_FIXED_BANKS] = conditions[_FIXED_BANKS][0]
        return conditions


class SediflowExport(HydroflowExport):
    """Exports the input files
    
    :param mesh: a mesh object from the hydroflow lib
    :type mesh: mesh
    :param model: a model object
    :type model: model
    """
    # Class variables 

    def __init__(self, mesh: Mesh, model: SediflowModel):
        """
        Constructs SedfiflowExport class based on the HydroflowExport class. 
        
        """
        HydroflowExport.__init__(self,mesh,model)
        self.boundary_conditions_code[_BOUNDARY_SEDIMENTS_DISCHARGE] = -3

    @property
    def sediments_level_file_path(self):
        return os.path.join(self.input_folder_name,_SEDIMENTS_LEVEL_FILE)

    @property
    def fixed_bank_file_path(self):
        return os.path.join(self.input_folder_name,_FIXED_BANK_FILE)
        
    def export(self):
        """Export all .txt files in the input folder:
        
        :return:
        :rtype: .txt    
        """        
        os.makedirs(self._INPUT_FOLDER_PATH,exist_ok=True)
        os.makedirs(self._OUTPUT_FOLDER_PATH,exist_ok=True)
        #Basic Watlab exports 
        self._export_watlab_basic_data()
        #Adapted exports for Hydroflow
        self._export_hydrodynamics_data()
        self._export_sediflow_data()
        self.__export_data()
    
    def _export_sediflow_data(self):
        self._export_fixed_bank()
        self._export_sediment_level()
        # self._export_sediments_parameters()
        # self._export_bank_failure_parameters()
    
    def _export_fixed_bank(self):
        """Exports the fixed bank array to a file. 
            IN DEVELOPMENT: FOR THE MOMENT 0 EVERYWHERE : TO PRECISE ?? VERIFY
        """
        initial_conditions = self.model.get_initial_conditions()
        if _FIXED_BANKS not in initial_conditions:
            return
        np.savetxt(self.fixed_bank_file_path,np.zeros(self._mesh.nCells))
        
    # def _export_sediments_parameters(self):        
    #     """Exports the sedimentological parameters in a .txt file.
    #     The output file contains:
    #         .join([str(self.__model.sediment_mean_grain_diameter), 
    #                 str(self.__model.sediment_density), 
    #                 str(self.__model.sediment_friction_coefficient), 
    #                 str(self.__model.sediment_porosity)])

    #     :return: a text file with sedimentological parameters
    #     :rtype: .txt        
    #     """
    #     if not(self.model.is_sediments): return
        
    #     sediments_parameters_export = [self.model.sediment_mean_grain_diameter, 
    #                                    self.model.sediment_density,
    #                                    self.model.sediment_friction_coefficient,
    #                                    self.model.sediment_porosity]
        
    #     fmt = '%1.6f'
    #     myfile = self.sediments_parameters_file_path
    #     np.savetxt(myfile,sediments_parameters_export, delimiter=" ", fmt=fmt, newline = " ")

    def _export_sediment_level(self):
        """Exports the initial sediment level to a file.
            The initial sediment level is retrieved from the `initial_conditions` dictionary using the key specified in `self._model_variables_dic["INITIAL_SEDIMENTS_LEVEL"]`. 
            If this key is not present in the dictionary, the function does nothing.
    
        :return: The resulting array is saved to a file with the filename being the concatenation of the folder path, INPUT_NAME, and SEDIMENT_LEVEL_NAME.
            The output format is specified using the `fmt` variable.
        :rtype: .txt
        """
        self._export_cell_data(_INITIAL_SEDIMENTS_LEVEL,self.sediments_level_file_path)

    # def _export_bank_failure_parameters(self):        
    #     """Exports the parameters for bank failure in a .txt file.
    #     The output file contains:
    #         .join([str(self.__model.critical_emmerged_friction_angle), 
    #                 str(self.__model.critical_immerged_friction_angle), 
    #                 str(self.__model.residual_emmerged_friction_angle), 
    #                 str(self.__model.residual_immerged_friction_angle)]) 

    #     :return: a text file with the parameters needed by the bank failure operator
    #     :rtype: .txt        
    #     """

    #     if not(self.model.is_sediments): return
        
    #     bank_failure_parameters_export = [self.model.critical_emmerged_friction_angle, 
    #                                    self.model.critical_immerged_friction_angle,
    #                                    self.model.residual_emmerged_friction_angle,
    #                                    self.model.residual_immerged_friction_angle]
        
    #     fmt = '%1.6f'
    #     myfile = self.bank_failure_parameters_file_path
    #     np.savetxt(myfile,bank_failure_parameters_export, delimiter=" ", fmt=fmt, newline = " ")

    def __export_data(self,write=True):
        """Generates a json file where the informations about the model and the mesh are summarized
            This function will delete the EDGES_NAME file if existing and clean all the pics in the Output folder.

        :return: A json file containing the parameters of the simulation
        :rtype: .json (write=True) or dictionnary with the parameters of the simulation (write=False)
        """
        
        # We load hydrodynamic data from HydroflowExport
        input_data = HydroflowExport._HydroflowExport__export_data(self,write=False) 

        # We add Sediflow data to the hydrodynamic's one
        input_data['model']['parameters'] = {
             'sediments mean grain diameter' : self.model.sediment_mean_grain_diameter,
             'sediments density' : self.model.sediment_density,
             'sediments friction coefficient' : self.model.sediment_friction_coefficient,
             'sediments porosity' : self.model.sediment_porosity
            }

        if self.model.is_initial_sediment_level : input_data['model']['conditions']['initial sediments level'] = self.sediments_level_file_path
        # if self.model.is_bank_failure :           #currently unused (à venir)
        #     input_data['extensions'] = {
        #         'bank failure' : {
        #         'parameters' : {
        #             'critical emmerged friction angle' : self.model.critical_emmerged_friction_angle, 
        #             'critical immerged friction angle' : self.model.critical_immerged_friction_angle,
        #             'residual emmerged friction angle' : self.model.residual_emmerged_friction_angle,
        #             'residual immerged friction angle' : self.model.residual_immerged_friction_angle,
        #             'fixed bank file' : self.fixed_bank_file_path
        #         }
        #         }
        #    }

        if (write):
            input_data = {key: value for key, value in input_data.items() if value not in [{}]} #Clean extensions: {} before printinf if no extensions used by the simulation
            with open(self.data_file_path, 'w') as f:
                json.dump(input_data,f,indent=3)
        else : 
            return input_data
        