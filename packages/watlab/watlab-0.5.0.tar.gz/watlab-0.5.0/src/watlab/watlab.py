"""
.--.      .--.   ____   ,---------.   .---.        ____     _______    
|  |_     |  | .'  __ `.\          \  | ,_|      .'  __ `. \  ____  \  
| _( )_   |  |/   '  \  \`--.  ,---',-./  )     /   '  \  \| |    \ |  
|(_ o _)  |  ||___|  /  |   |   \   \  '_ '`)   |___|  /  || |____/ /  
| (_,_) \ |  |   _.-`   |   :_ _:    > (_)  )      _.-`   ||   _ _ '.  
|  |/    \|  |.'   _    |   (_I_)   (  .  .-'   .'   _    ||  ( ' )  \ 
|  '  /\  `  ||  _( )_  |  (_(=)_)   `-'`-'|___ |  _( )_  || (_{;}_) | 
|    /  \    |\ (_ o _) /   (_I_)     |        \\ (_ o _) /|  (_,_)  / 
`---'    `---` '.(_,_).'    '---'     `--------` '.(_,_).' /_______.' 
This module includes the base functions and classes of the Watlab Tool. 

Usage:
======

Watlab is intended to be used by students and researchers in the field of Hydraulics engineering. 
It should be considered as a sandbox where many tools and developed methods can be employed and tested.


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

__authors__ = "Pierre-Yves Gousenbourger, Sandra Soares-Frazao, Robin Meurice, Charles Ryckmans, Nathan Delpierre, Martin Petitjean"
__contact__ = "pierre-yves.gousenbourger@uclouvain.be"
__copyright__ = "MIT"
__date__ = "2022-09-05"
__version__= "0.0.1"

from .meshParser import MeshParser
import numpy as np 
import os 
import matplotlib.tri as mtri
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import imageio
import contextily as ctx
from scipy.interpolate import griddata
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import reverse_cuthill_mckee
import pandas as pd
import sys 
import subprocess
import shlex
from .utils import interpolate_points, extract_values_from_tif, select_postprocessing_variable
from typing import Callable, Union

#Const
_MESHCHECKER_NAME = "meshchecker"
#%%% A name for meshchecker executable
if sys.platform == "win32":
    _MESHCHECKER_EXECUTABLE = _MESHCHECKER_NAME+"-win.exe"
elif sys.platform == "darwin":
    _MESHCHECKER_EXECUTABLE = _MESHCHECKER_NAME+"-darwin"
elif sys.platform == "linux" or sys.platform == "linux2":
    _MESHCHECKER_EXECUTABLE = _MESHCHECKER_NAME+"-linux"

_INPUT_NAME = "input"
_OUTPUT_NAME = "output"
_MESHCHECKER_NODES_FILE = "nodes_meshchecker.txt"
_MESHCHECKER_CELLS_FILE = "cells_meshchecker.txt"
_MESHCHECKER_EDGES_FILE = "edges_meshchecker.txt"
_NODES_FILE = "nodes.txt"
_CELLS_FILE = "cells.txt"
_PICTURE_FILE = "pictures_times.txt"
_GAUGE_FILE = "gauges.txt"
_DISCHARGE_FILE = "discharge_measurement.txt"
_DISCHARGE_OUTPUT_FILE = "discharge_measurement_output.txt"
_EDGES_FILE = "edges.txt"
_INITIAL_CONDITIONS_FILE = "initial_conditions.txt"
_DATA_FILE = "data.json"

#path to meshchecker
_dir_path_to_executable = os.path.join(os.path.dirname(__file__),"bin")
_root_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def _compile_meshchecker(isParallel=False):
        """
        Compiles the C++ code using g++.
        The compilation is done using the following command:
        g++ -O3 -fopenmp -o meshchecker src/cpp/*.cpp src/cpp/writer/*.cpp src/cpp/interfaces/*.cpp src/cpp/utils/*.cpp -std=c++20
        The compilation is done in the directory where the C++ code is located.
        The compilation is done using the subprocess module.
        The subprocess module is used to run the g++ command.
        The shlex module is used to split the command into a list of strings.
        The cwd parameter of the subprocess module is used to specify the directory 
        where the compilation is done.
        The wait() method of the subprocess module is used to wait for the 
        compilation to finish.
        """
        relpath = os.path.relpath(_dir_path_to_executable,_root_path).replace('\\','/')
        src_files = 'src/meshchecker/*.cpp src/meshchecker/mesh/*.cpp src/meshchecker/src/*.cpp src/meshchecker/utils/*.cpp'
        compiler_opt = '-O3 -fopenmp' if isParallel else ''
        compile_cmd = f"g++ {compiler_opt} -o {relpath}/{_MESHCHECKER_EXECUTABLE} {src_files} -std=c++20 -static"

        try:
            subprocess.run(shlex.split(compile_cmd),
                                        stdout=subprocess.PIPE,
                                        cwd=_root_path,
                                        text=True,
                                        stderr=subprocess.PIPE,
                                        check = True)
            print("The meshchecker code has been successfully compiled: the executable has been generated.")
            if isParallel: print("(Parallel version)")
        except subprocess.CalledProcessError as e:
            print("There were compiling errors, the code can not be run:")
            print("Error:", e.stderr)

class Mesh():
    """Mesh class is used to build the geometry of the simulation. \n 
    The class gives access to the informations of the mesh as \n
    nodes, cells, edges organization and regions. \n 
    Normally, the function are not needed for the user. 
    Except if there is a need for specific simulation topography imported from a tiff file.

    :param msh_mesh: The path to the .msh file representing the mesh.
        The file must comply with GMSH 4.10 file format
    :type msh_mesh: string
    :param nNodes: Number of nodes in the mesh
    :type nNodes: int
    :param nCells: Number of cells in the mesh
    :type nCells: int
    :param nEdges: Number of edges in the mesh
    :type nEdges: int
    """
    def __init__(self,msh_mesh,reorder=False):
        """Constructs the Mesh object based on an .msh file.
        """
        self.__parser = MeshParser(msh_mesh)
        self._nodes, self.__node_tags = self.__parser.extract_nodes()
        self.__cells, self.__cell_tags = self.__parser.extract_cells()
        self.__edge_nodes, self.__edge_cells, self.__edge_tags, self.__edgeTags_unsorted = self.__parser.extract_edges()
        self.__edges_length = self.edges_length
        self.__boundaries = self.__parser.extract_physical_groups(1)
        self.__regions = self.__parser.extract_physical_groups(2)
        self.__region_cells = self.__parser.extract_cells_by_physical_group(2)
        self.__boundary_edges = self.__parser.extract_cells_by_physical_group(1)
        self.nNodes = len(self.__node_tags)
        self.nCells = len(self.__cell_tags)
        self.nEdges = len(self.__edge_tags)
        self._cells_barycenters = np.resize(self.__parser.extract_cells_barycenters(),(self.nCells,3))
        self.__tag_to_indexes = {tag: index for tag, index in zip(self.__cell_tags,  np.arange(0,self.nCells))}
        self.__elem_type = len(self.__cells[0]) # n_nodes for each cell 
        self.__meshchecking = False
        if reorder: self.__reorder_mesh()

    @property
    def meshchecking(self):
        """ Indicates if a meshchecking is asked by the user before the use of the solver

        :return True or False
        :rtype Boolean
        """
        return self.__meshchecking
    
    @meshchecking.setter
    def meshchecking(self,meschecking):
        self.__meshchecking = meschecking
        
    @property
    def nodes(self):
        """The nodes' tags and coordinates

        :getter: _nodes_tags = list of the nodes' tags
            _nodes = list of the nodes' coordinates
        :type: nDArray
        """
        
        return self.__node_tags, self._nodes
 
    @property
    def cells(self):
        """The __cell_tags and the associated cells represented by their node_tags

        :getter: __cell_tags = list of the cells' tags
            __cells = list of the nodes describing each cell
        :type: nDArray
        """
        
        return self.__cell_tags, self.__cells

    @property
    def tag_to_indexes(self):
        """Indicates the mapping from cells' tags to cells' indexes

        :getter: __tag_to_indexes
        :type: dict{key = tag : value = index}
        """
        return self.__tag_to_indexes
    
    @property
    def edges(self):
        """The edges' tags, nodes, and cells

        :getter: edge_tags = the tags of the edges
            edge_nodes = the nodes n_0 and n_1 composing the edge, with n_0 < n_1
            edge_cells: the left cell and the right cell, with respect to the edge
            where n_0 is bottom and n_1 is top.
        :type: nDArray
        """
        return self.__edge_tags, self.__edge_nodes, self.__edge_cells

    @property
    def boundaries(self):
        """The dictionnary of boundaries

        :getter: __boundaries
        :rtype: dict{tags : names}
        """
        return self.__boundaries

    def get_boundary_by_name(self,name):
        """Returns a list of boundary edges corresponding to the tag [name] 

        :param name: name of the tag to look for
        :type name: string
        :raises Exception: There is no physical boundary named after [name]
        :return: list of the boundary edges
        :rtype: list
        """

        if (name in self.__boundaries.values()):
            return list(self.__boundaries.keys())[list(self.__boundaries.values()).index(name)]
        else: 
            raise Exception("There is no physical boundary named "+name+".")

    @property
    def regions(self):
        """The dictionnary of physical groups

        :getter: regions = the physical groups
        :type: dict{tags : names}
        """
        return self.__regions
    
    @property
    def region_cells(self):
        """The cells associated to physical group

        :getter: region_cells
        :type: dict{Physical Group : cells }
        """
        return self.__region_cells
    
    def get_region_by_name(self,name):
        """Returns the tag of the region of name [name]

        :param name: name of the tag to look for
        :type name: string

        :raise Exception: There is no physical region named after [name]
        :return: returns the tag of the region corresponding to [name]
        :rtype: list
        """
        
        if (name in self.__regions.values()):
            return list(self.__regions.keys())[list(self.__regions.values()).index(name)]
        else: 
            raise Exception("There is no physical region named "+name+".")
    
    @property
    def boundary_edges(self):
        """The edges associated to physical groups as a dictionnary

        :getter: boundary_edges
        :type: dict{physical group : edges}
        """
        return self.__boundary_edges
    
    @property
    def elem_type(self):
        """
        Returns
        -------
        Type of the elements as int 
        """
        return self.__elem_type

    def get_cells_barycenters(self):
        """Returns cells barycenters coordinates
        
        :return: cells_barycenters
        :rtype: nDArray 
        """
        return self._cells_barycenters
    
    @property
    def edges_length(self):
        """Returns the length of each edge composing the mesh

        :return: length of each mesh's edge
        :rtype: ndArray
        """
        if not hasattr(self,"__edges_length"):
            x1 = np.take(self._nodes[:,0],self.__edge_nodes[:,0].astype(np.int64)-1)
            y1 = np.take(self._nodes[:,1],self.__edge_nodes[:,0].astype(np.int64)-1)
            x2 = np.take(self._nodes[:,0],self.__edge_nodes[:,1].astype(np.int64)-1)
            y2 = np.take(self._nodes[:,1],self.__edge_nodes[:,1].astype(np.int64)-1)
            self.__edges_length = np.sqrt((x2-x1)**2+(y2-y1)**2)
        return self.__edges_length
    
    def get_boundary_length(self,boundary_name) -> float:
        """Returns the length of a boundary by name

        :param boundary_name: the name of the desired boundary
        :type boundary_name: str
        :raises Exception: this boundary name does not exist
        :return: The length in [m] of the boundary
        :rtype: float
        """
        if boundary_name not in self.boundaries.values():
            raise Exception("this boundary name does not exist")
        else: 
            key = self.get_boundary_by_name(boundary_name)
            edges = self.__boundary_edges[key] - 1 
            boundary_length = np.sum(self.edges_length[edges])
        return boundary_length
    
    def set_nodes_elevation_from_tif(self,tif_file):
        """Sets the elevation of the nodes of the mesh from a tif file.
            The z value is interpolated from the tif file and set to the corresponding nodes

        :param tif_file: path of the tif file
        :type tif_file: string
        """
        tif_points_coordinates, tif_points_elevations = extract_values_from_tif(tif_file)
        self._nodes[:,2] = interpolate_points(tif_points_coordinates,tif_points_elevations,self._nodes)
        self._cells_barycenters[:,2] = interpolate_points(self._nodes[:,0:2],self._nodes[:,2],self._cells_barycenters,interpolation_method='linear')

    def __reorder_mesh(self):

        # preprocessing
        edge_cells_idx = self.__edge_cells.copy()
        edge_cells_idx[self.__edge_cells != -1] = [self.__tag_to_indexes[tag] for tag in self.__edge_cells[self.__edge_cells != -1]]

        # build mesh dual graph
        inner_mask = edge_cells_idx[:,1] >= 0
        inner_edges = edge_cells_idx[inner_mask]
        row_ind = inner_edges.flatten()
        col_ind = inner_edges[:, [1, 0]].flatten()
        adj_matrix = csr_matrix((np.ones(len(row_ind)), (row_ind,col_ind)), shape=(self.nCells,self.nCells))
        # RCM algorithm
        perm = reverse_cuthill_mckee(adj_matrix, symmetric_mode=True)
        
        # permute cells 
        self.__cells[:] = self.__cells[perm]
        self.__cell_tags[:] = self.__cell_tags[perm]
        self._cells_barycenters[:] = self._cells_barycenters[perm]
        self.__tag_to_indexes = {tag: index for tag, index in zip(self.__cell_tags,  np.arange(0,self.nCells))}

        # Notice that only the indices of the cells are permuted, i.e. their positions in the lists
        # but their tags remain unchanged such that no modification of __region_cells is needed.
        # Only the __tag_to_indexes mapping needs to be updated.

        # renumber edges to minimize gaps between indices of left and right cells
        edge_cells_idx[self.__edge_cells != -1] = [self.__tag_to_indexes[tag] for tag in self.__edge_cells[self.__edge_cells != -1]]
        is_partial = edge_cells_idx[:, 1] == -1

        partial_edges = edge_cells_idx[is_partial]
        full_edges = edge_cells_idx[~is_partial]
        partial_idx = np.where(is_partial)[0]
        full_idx = np.where(~is_partial)[0]

        partial_order = partial_idx[np.argsort(partial_edges[:, 0])]
        full_order = full_idx[np.argsort(full_edges[:, 0])]
        perm_edges = np.concatenate((partial_order, full_order
                                     ))
        self.__edge_cells[:] = self.__edge_cells[perm_edges]
        self.__edge_nodes[:] = self.__edge_nodes[perm_edges]
        self.__edge_tags[:] = self.__edge_tags[perm_edges]
        self.__edges_length[:] = self.__edges_length[perm_edges]


class WatlabModel():
    """
    The WatlabModel class is the template model that should be used by all Watlab simulation tools. \n
    The simulation model is made of a physical Mesh and is linked to the Export class \n
    This class must be used to design your problem by providing a solver, initial and boundary conditions. 
    The function export_data() is used to export the data files describing the simulation. \n
    It has to be done before the solve(). \n
    The function solve() is used to launch the simulation by calling the C++ solver. 
    """
    def __init__(self,mesh: Mesh):
        self._current_path = os.getcwd()
        self._mesh = mesh
        self._conditions = {}
        self.__conditions_regions = {}
        self._source_terms = {}
        self.__name = "Simulation"
        self._physical_model = "Watlab"
        self.__starting_time = 0.0
        self.__ending_time = 10.0
        self.__picture_times = []
        self.__is_picture = 0
        self._gauge = []
        self._gauge_time_step = 0
        self.__is_gauge = 0
        self.__dt_enveloppe = 1.0
        self.__is_discharge_measurement_section = 0
        self.__discharge_measurement_edges = {}
        self.__discharge_measurement_time_step = 1
        self.initial_conditions_keys = []
        self.boundary_conditions_keys = []
        self.export = WatlabExport(self._mesh,self)

    def _launch_meshchecker(self, display=True,isParallel=False):
        if self._mesh.meshchecking:
            if os.path.exists(os.path.join(_dir_path_to_executable,_MESHCHECKER_EXECUTABLE)):
                if display: print(_MESHCHECKER_EXECUTABLE + " exists")
        else:
            if display: print ("MESHCHECKER must be compiled... !")
            _compile_meshchecker(isParallel=isParallel)

        if display: print("Launching the meshchecker executable ...")

        executable_cmd = os.path.join(_dir_path_to_executable, _MESHCHECKER_EXECUTABLE)
        process = subprocess.Popen(executable_cmd,
                                   stdin=subprocess.PIPE, 
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   cwd=self._current_path,
                                   universal_newlines=True,
                                   text=True)
        #Sending path to the data through stdin
        meshchecker_edges_file_path = os.path.join(self.export.input_folder_name,_MESHCHECKER_EDGES_FILE)
        meshchecker_cells_file_path = os.path.join(self.export.input_folder_name,_MESHCHECKER_CELLS_FILE)
        meshchecker_nodes_file_path = os.path.join(self.export.input_folder_name,_MESHCHECKER_NODES_FILE)

        input_data = f"{meshchecker_cells_file_path}\n{meshchecker_nodes_file_path}\n{meshchecker_edges_file_path}\n{self.export.cells_file_path}\n{self.export.nodes_file_path}\n{self.export.edges_file_path}\n"
        process.stdin.write(input_data)
        process.stdin.close()

        if display:
            for line in iter(process.stdout.readline, ""):
                sys.stdout.write('\r'+ line[:-1])
                sys.stdout.flush()
        process.wait()
        
    @property
    def name(self):
        """
        The name of the simulation.

        :getter: Returns this simulation's name
        :setter: Sets this simulation's name
        :type: string
        """
        return self.__name

    @name.setter 
    def name(self,name):
        self.__name = name 

    @property
    def physical_model(self):
        """Assigns a physical model : you must decide to use only hydrodynamics or sediments...

        :getter: returns the physical model name
        :setter: Sets Physical model name: Hydroflow, Sediflow, ...
        :type: string
        """
        return self._physical_model

    @property
    def starting_time(self):
        """Time corresponding to the beginning of the simulation

        :getter: Returns starting time of the simulation
        :setter: Sets simulation starting time
        :type: float
        """
        return self.__starting_time

    @starting_time.setter
    def starting_time(self,starting_time):
        self.__starting_time = starting_time

    @property
    def ending_time(self):
        """Time corresponding to the end of the simulation

        :getter: Returns ending time of the simulation
        :setter: Sets simulation ending time
        :type: float
        """
        return self.__ending_time

    @ending_time.setter
    def ending_time(self,ending_time):
        self.__ending_time = ending_time
    
    @property
    def is_gauge(self):
        """ 
        1 if generate a gauge was placed and 0 if not
        :getter: 1 or 0
        :rtype: boolean of type int
        """
        return self.__is_gauge
    
    @property
    def gauge(self):
        """ 
        Gauge position provided by the used with the set_gauge_function
        :getter: Array describing the position of the gauge
        :rtype: array
        """
        return self.__gauge

    @property
    def gauge_time_step(self):
        """ 
        Gauge time step recording provided by the used with the set_gauge_function
        :getter: Time step for the gauge result recording
        :rtype: float
        """
        return self.__gauge_time_step

    @property
    def time_step_enveloppe(self):
        """
        time interval dt used for the computation of the enveloppe of results 
        The enveloppe corresponds to the maximum values of height and velocities for each cell of the 
        computationnal domain  
        :getter: returns the enveloppe time step
        :setter: sets a desired enveloppe time step
        :type: float
        """
        return self.__dt_enveloppe
    
    @time_step_enveloppe.setter
    def time_step_enveloppe(self,dt_enveloppe):
        self.__dt_enveloppe = dt_enveloppe
    
    @property
    def is_picture(self):
        """
        Boolean of type int. 
        1 if pictures of results are needed,
        0 if not 
        :return: 0 or 1 
        :rtype: int
        """
        return self.__is_picture

    @property       
    def discharge_measurement_time_step(self):
        """ 
        :getter: The time-step used to measure the discharge accross the section
        :rtype: int
        """
        return self.__discharge_measurement_time_step

    @property
    def discharge_control_edges(self):
        """ 
        :getter: The edges corresponding to the chosen line
        :rtype: list of edges tags
        """
        return self.__discharge_measurement_edges
    
    @property
    def is_discharge_measurement_section(self):
        """ 
        1 if generate a discharge measurement section was placed and 0 if not
        :getter: 1 or 0
        :rtype: boolean of type int
        """
        return self.__is_discharge_measurement_section    

    @property
    def source_terms(self):
        """Returns the source terms of the model

        :return: source terms
        :rtype: dict
        """
        return self._source_terms     

    def __add_conditions(self,tags,values,region_tag,condition_type):
        """Adds the cell tags tags and their values values to the
        condition condition_type"""
        self._conditions[condition_type][0].extend(tags)
        self._conditions[condition_type][1].extend(values)
        self.__conditions_regions[condition_type].append(region_tag)

    def __replace_conditions(self,tags,values,condition_type):
        """Replace the existing initial conditions of cells (tags) with
        the values values in the condition condition_type"""
        # get
        conditions_values = np.array(self._conditions[condition_type][1],dtype=float)
        conditions_tags = self._conditions[condition_type][0]

        # replacement        
        conditions_values[np.isin(conditions_tags,tags)] = values
        self._conditions[condition_type][1] = conditions_values.tolist()

    def __create_conditions(self,tags,values,region_tag,condition_type):
        """Creates the conditions with tags, values"""
        self._conditions[condition_type] = [tags,values]
        self.__conditions_regions[condition_type] = [region_tag]

    def __update_conditions(self,tags,values,region_tag,condition_type):
        """Updates conditions corresponding to the status (add, replace, create)"""
        if condition_type in self._conditions:
            if region_tag in self.__conditions_regions[condition_type]:
                # Override the existing condition
                self.__replace_conditions(tags,values,condition_type)
            else:
                self.__add_conditions(tags,values,region_tag,condition_type)
        else:
            # brand new condition of this type ;-)
            self.__create_conditions(tags,values,region_tag,condition_type)

    def __add_source(self,tag,value,source_type):
        """Adds the cell tags tags and their values values to the
        source condition source_type"""
        self._source_terms[source_type].append(value)

    # def __replace_source(self,tag,value,source_type):
    #     """Replace the existing initial conditions of cells (tags) with
    #     the values values in the condition condition_type"""
    #     self._source_terms[source_type][tag] = value 

    def __create_source(self,tag,value,source_type):
        """Create the source terms with tag, values"""
        self._source_terms[source_type] = [value]

    def __update_source_terms(self,tag,value,source_type):
        """Updates the source terms of the model"""
        if source_type in self._source_terms:
            # if tag in self._source_terms[source_type]: 
            #     # Override the existing condition
            #     self.__replace_source(tag,value,source_type) Could be implemented but no reason to do it
            # else:
            #     self.__add_source(tag,value,source_type)
            self.__add_source(tag,value,source_type)
        else:
            # brand new source of this type ;-)
            self.__create_source(tag,value,source_type)
            
    def __set_initial_condition(self, region, value: Union[float, list, str, Callable[[float, float], float], bool], condition_type: str):
        """
        Sets the initial condition value to the cells of a specified region.
        :param region: The region name (string) or region tag (int) to set the initial condition for.
        :type region: string or int
        :param condition_type: The type of initial condition to set.
        :type condition_type: string
        :param value: The value(s) to assign as initial condition. Can be a float, a list of floats (one per cell), or a function that computes the value from cell coordinates.
        :type value: float, list(float), or function
        :raises Exception: If the specified region does not exist in the mesh.
        """        
        region_tag = self._mesh.get_region_by_name(region) if isinstance(region,str) else region
        if not(region_tag in list(self._mesh.regions.keys())):
            raise Exception("There is no such region in regions. Region tag: "+str(region))

        tags = self._mesh.region_cells[region_tag].tolist()
        indexes = [self._mesh.tag_to_indexes.get(tag) for tag in tags]
        
        if type(value)==list and len(value)==np.size(tags):
            values = value
        elif callable(value):
            X = self._mesh.get_cells_barycenters()[indexes,0]
            Y = self._mesh.get_cells_barycenters()[indexes,1]
            values = list(map(value, X, Y))
        elif isinstance(value, str) and value.lower().endswith('.tif'):
            tif_points_coordinates, values_map = extract_values_from_tif(value)
            values = interpolate_points(tif_points_coordinates, values_map, self._mesh.get_cells_barycenters()[indexes]).tolist()
        else:
            values = [value] * np.size(tags)
            
        self.__update_conditions(tags,values,region_tag,condition_type)
    
    def __set_boundary_condition(self,boundary,value,condition_type):
        """Sets the boundary condition value to the edges of a boundary.

        Parameters
        ----------
        boundary: the boundary name (string) or the boundary tag (int)
        value: the value to be given to the edges. All the edges of the boundary will get the same value.

        Returns
        -------
        tags, values: the tags of the edges of the boundary and the values associated to them.
        """
        boundary_tag = self._mesh.get_boundary_by_name(boundary) if isinstance(boundary,str) else boundary
        if not(boundary_tag in list(self._mesh.boundaries.keys())):
            raise Exception("There is no such boundary in boundaries. Boundary tag: "+str(boundary))

        tags = self._mesh.boundary_edges[boundary_tag].tolist()
        values = [value]*np.size(tags)
        
        self.__update_conditions(tags,values,boundary_tag,condition_type)

    def _set_initial_conditions(self,regions,values,condition_type):
        """Sets the initial condition values to the cells the domain.

        Parameters
        ----------
        regions (list): the regions names (string) or the regions tags (int)
        value (list): the values to be given to the cells in the correspondint region. 
                      All the cells of the region will get the same value.
        type (cst string): the type of initial condition.

        Returns
        -------
        updates the initial_conditons dictionnary with the tags of the cells and 
        the values associated to them, in the given type
        """
        if isinstance(regions,str):
            self.__set_initial_condition(regions,values,condition_type)
        else:
            for i in range(len(regions)):
                self.__set_initial_condition(regions[i],values[i],condition_type)

    def _set_boundary_conditions(self,boundaries,values,condition_type):
        """Sets the initial condition values to the edges in the domain.

        Parameters
        ----------
        boundaries (list): the boundary names (string) or the boundary tags (int)
        value (list): the values to be given to the edges in the corresponding boundary. 
                      All the edges of the boundary will get the same value.

        Returns
        -------
        tags, values: the tags of the edges and the values associated to them.
        """
        if isinstance(boundaries,str):
            self.__set_boundary_condition(boundaries,values,condition_type)
        else:
            for i in range(len(boundaries)):
                self.__set_boundary_condition(boundaries[i],values[i],condition_type)
                

    def _set_source_term(self,regions, value, tag, source_type):
        """Sets the source term values to the cells in the domain.
        :param regions: the regions names (string) or the regions tags (int)
        :type regions: list, string or int

        :param value: the values to be given to the cells in the correspondint region.
        :type value: list

        :param condition_type: the type of initial condition.
        :type condition_type: string
        """
        # Not really initial conditions but we use the same structure
        if isinstance(regions,(str, int)):
            self.__set_initial_condition(regions,tag,source_type)
        else:
            for region in regions:
                self.__set_initial_condition(region,tag, source_type)
        
        self.__update_source_terms(tag,value,source_type)
        

    def get_conditions(self,wanted_keys):
        """Returns all boundary or initial conditions imposed by the user
        
        :param wanted_keys: type of condition desired 
        :type wanted_keys: string
        :return: values of the conditions
        :rtype: key : value type 
        """
        # find which condition types are activated
        mask = np.isin(list(self._conditions.keys()),wanted_keys)
        return { condition_type: self._conditions.get(condition_type) for condition_type in np.array(list(self._conditions.keys()))[mask] }
    
    def get_source_terms(self):
        """Returns all source terms imposed by the user
        
        :return: values of the source terms
        :rtype: key : value type 
        """
        return self._source_terms
   
    def get_initial_conditions(self):
        """Returns the initial conditions in a dictionary
        
        :return: a dictionnary with the initial condition type as key and the concerned cells as values
        :rtype: key : dictionnary
        """
        conditions = self.get_conditions(self.initial_conditions_keys)        
        return conditions

    def get_boundary_conditions(self):
        """Returns the boundary conditions in a dictionary
        
        :return: a dictionnary with the initial condition type as key and the concerned cells as values
        :rtype: key : dictionnary
        """
        conditions = self.get_conditions(self.boundary_conditions_keys)
        return conditions
    
    def get_picture_times(self):
        """Provides the list of the times at which the results will be returned

        :return: list of picture times
        :rtype: ndArray
        """
        return self.__picture_times

    def set_picture_times(self,n_pic=0,dt_picture = 0, pic_array = None):
        """
        Sets the times at which pictures (outputs) should be taken based on three possible methods:
        
        1) If a time step (`dt_picture`) is provided, picture times will be set at intervals of `dt_picture` seconds.
        2) If a number of pictures (`n_pic`) is provided, picture times will be evenly distributed over the entire duration.
        3) If a list of specific picture times (`pic_array`) is provided, it will be used directly.
        
        :param n_pic: Number of desired pictures, defaults to 0. Used if no time step is provided.
        :type n_pic: int, optional
        :param dt_picture: Time step at which the pictures should be taken, defaults to 0.
        :type dt_picture: float, optional
        :param pic_array: A list of desired picture times, defaults to None.
        :type pic_array: list or numpy array, optional
        
        :raises ValueError: If no method for setting picture times is provided.
        """ 
        self.__is_picture = 1
        if dt_picture != 0:
            self.__picture_times = np.arange(self.starting_time, self.ending_time, dt_picture)
        elif n_pic > 0:
            self.__picture_times = np.linspace(self.starting_time, self.ending_time, n_pic)
        elif pic_array is not None:
            self.__picture_times = pic_array
        else:
            raise ValueError("You must provide either a time step (`dt_picture`), number of pictures (`n_pic`), or a list of picture times (`pic_array`).")
        
    def set_gauge(self, gauge_position = [], time_step =1):
        """ The method allows to put a measurement gauge at a desired place
        A gauge file will be generated in the output folder

        :param gauge_position: list [[X1,Y1,Z1],[X2,Y2,Z2]] of the chosen gauges positions, defaults to []
        :type gauge_position: list, optional
        :param time_step: time step for measurement, defaults to 1
        :type time_step: int, optional
        """
        self.__is_gauge = 1 
        self.__gauge = gauge_position 
        self.__gauge_time_step = time_step
        
    def set_discharge_measurement_section(self,section_name=None,time_step=1):
        """Tool to control the discharge across a section 

        :param section_name: string or int corresponding to the tag of the desired boundary or interior line in the mesh, defaults to None
        :type section_name: string or int , optional
        :param time_step: time step used to measure the discharge accross the section, defaults to 1
        :type time_step: int, optional
        :raises Exception: throws exception if the boundary does not exist 
        """
        if isinstance(section_name, str): section_name = [section_name]
        for section in section_name: 
            boundary_tag = self._mesh.get_boundary_by_name(section) if isinstance(section,str) else section
            if not(boundary_tag in list(self._mesh.boundaries.keys())):
                raise Exception("There is no such boundary in boundaries. Boundary tag: "+str(section))
            self.__discharge_measurement_edges[section] = self._mesh.boundary_edges[boundary_tag]
            self.__discharge_measurement_time_step = time_step
            self.__is_discharge_measurement_section = 1
            

class WatlabExport():
    """The WatlabExport class is the basic export class. \n
    It allows the user to export the nodes, cells, output times etc,.. \n
    More specific quantities such as boundary conditions, initial conditions, 
    data file should be written in specific solver file.
    
    :param mesh: a mesh object from the hydroflow lib
    :type mesh: mesh
    :param model: a model object
    :type model: model
    """
    # Class variables 
    _INPUT_FOLDER_NAME = _INPUT_NAME
    _OUTPUT_FOLDER_NAME = _OUTPUT_NAME
    _INPUT_FOLDER_PATH = os.path.join(os.getcwd(), _INPUT_FOLDER_NAME)
    _OUTPUT_FOLDER_PATH = os.path.join(os.getcwd(), _OUTPUT_FOLDER_NAME)

    def __init__(self, mesh: Mesh, model:WatlabModel):
        """Constructs the Mesh object based on an .msh file.
        """
        self._mesh = mesh
        self.model = model
        
    @property
    def output_folder_path(self):
        """The path of the output folder

        :getter: Returns the path of the output folder
        :type: string
        """
        return self._OUTPUT_FOLDER_PATH

    @property
    def output_folder_name(self):
        """The name of the output folder

        :getter: Returns the name of the output folder
        :setter: Sets the name of the output folder
        :type: string
        """
        return self._OUTPUT_FOLDER_NAME

    @output_folder_name.setter
    def output_folder_name(self,name):
        self._OUTPUT_FOLDER_NAME = name
        self._OUTPUT_FOLDER_PATH = os.path.join(os.getcwd(), self._OUTPUT_FOLDER_NAME)

    @property
    def input_folder_path(self):
        """The path of the input folder

        :getter: Returns the path of the input folder
        :type: string
        """
        return self._INPUT_FOLDER_PATH

    @property
    def input_folder_name(self):
        """The name of the input folder

        :getter: Returns the name of the input folder
        :setter: Sets the name of the input folder
        :type: string
        """
        return self._INPUT_FOLDER_NAME

    @input_folder_name.setter
    def input_folder_name(self,name):
        self._INPUT_FOLDER_NAME = name
        self._INPUT_FOLDER_PATH = os.path.join(os.getcwd(), self._INPUT_FOLDER_NAME)
    
    @property
    def meshchecker_export_file_path(self):
        return self.input_folder_name

    @property 
    def nodes_file_path(self):
        return os.path.join(self.input_folder_name,_NODES_FILE)
    
    @property 
    def cells_file_path(self):
        return os.path.join(self.input_folder_name,_CELLS_FILE)
    
    @property
    def pictures_file_path(self):
        return os.path.join(self.input_folder_name,_PICTURE_FILE)
    
    @property
    def gauge_file_path(self):
        return os.path.join(self.input_folder_name,_GAUGE_FILE)

    @property
    def discharge_measurement_section_file_path(self):
        return os.path.join(self.input_folder_name,_DISCHARGE_FILE)
    
    @property
    def edges_file_path(self):
        return os.path.join(self.input_folder_name,_EDGES_FILE)
    
    @property
    def initial_conditions_file_path(self):
        return os.path.join(self.input_folder_name,_INITIAL_CONDITIONS_FILE)

    @property 
    def data_file_path(self):
        return os.path.join(self.input_folder_name,_DATA_FILE)
    
    def _export_cell_data(self, data_key, file_path):
        """
        This private function allows to export values per cells.
        1 row = 1 cell = 1 value 
        Ex: friction coeffs, sediments levels, bedrock levels.. 
        """
        export_array = np.zeros(self._mesh.nCells)
        initial_conditions = self.model.get_initial_conditions()
        if data_key not in initial_conditions:
            return
        data_array = np.array(initial_conditions[data_key][1]).T
        data_tags = initial_conditions[data_key][0]
        data_indexes = [self._mesh.tag_to_indexes.get(tag) for tag in data_tags]
        export_array[data_indexes] = data_array
        np.savetxt(file_path, export_array, delimiter=" ", fmt='%1.6f')


    def _export_cell_binding(self, data_key, file_path):
        """
        This private function allows to export bind values for a specific source term per cells.
        1 row = 1 cell = 1 value
        Ex: rain, infiltration, ...
        """
        export_array = np.ones(self._mesh.nCells) * -1 # -1 means no binding
        initial_conditions = self.model.get_initial_conditions()
        if data_key not in initial_conditions:
            return
        data_array = np.array(initial_conditions[data_key][1]).T
        data_tags = initial_conditions[data_key][0]
        data_indexes = [self._mesh.tag_to_indexes.get(tag) for tag in data_tags]
        export_array[data_indexes] = data_array
        np.savetxt(file_path, export_array, delimiter=" ", fmt='%i')
        
    def _export_nodes(self):
        """Exports the nodes from the GSMH mesh to a file.

        :return: A text file containing the number of nodes and their coordinates.
            First line: n_nodes
            Each following line is formatted as [x_n, y_n, z_n].
        :rtype: .txt
        """
        fmt = '%1.9f', '%1.9f', '%1.9f'
        if (self._mesh.meshchecking):
            output_path = os.path.join(self.input_folder_name,_MESHCHECKER_NODES_FILE)
        else :
            output_path = self.nodes_file_path
        f = open(output_path,'w')       
        f.write(str(self._mesh.nNodes) + '\n')
        f.close()
        _,nodes = self._mesh.nodes
        with open(output_path,'ab') as f:
           np.savetxt(f,nodes, delimiter=" ", fmt=fmt)

    def _export_cells(self):
        """Exports the cells from the GSMH mesh to a file.

        :return: A text file containing the number of cells, the number of nodes for each cell and the tags of the corresponding nodes.
            First line: n_cells
            Each following line is formatted as [n_node_of_cell, node_1, node_2, node_3].
        :rtype: .txt
        """
        if (self._mesh.meshchecking):
            output_path = os.path.join(self.input_folder_name,_MESHCHECKER_CELLS_FILE)
        else:
            output_path = self.cells_file_path
        f = open(output_path ,'w')
        f.write(str(self._mesh.nCells)+'\n')
        f.close()
        fmt = '%d', '%d', '%d','%d'
        dim = self._mesh.elem_type*np.ones((self._mesh.nCells,1)) 
        _,cells_nodes = self._mesh.cells
        with open(output_path,'ab') as f:
            np.savetxt(f,np.hstack((dim,cells_nodes-1)), delimiter=" ", fmt=fmt) 
            
    def _export_pic(self):        
        """This functions create the pic.txt file and write the following information:
            n_pic
            t_pic,1
            t_pic,2
            ...
            t_pic,n_pic
        :return: a pic file
        :rtype: .txt        
        """
        f = open(self.pictures_file_path, 'w')
        f.write(str(len(self.model.get_picture_times()))+'\n')
        f.close()
        fmt = '%1.2f'
        with open(self.pictures_file_path,'ab') as f:
           np.savetxt(f,self.model.get_picture_times(), delimiter=" ", fmt=fmt)
    
    def _export_gauge(self):
        """Exports the gauge position and time step

        :return: a file composed by
            nGauges
            OutputGaugeName : default : gauge.txt
            time step of measurement
            gauge positions : [[X1,Y1,Z1],[X1,Y1,Z1]] of the chosen gauges
        :rtype: .txt
        """
        if not self.model.is_gauge:
            return
        f = open(self.gauge_file_path, 'w')
        f.write(str(len(self.model.gauge))+'\n')
        f.write(_GAUGE_FILE+'\n')  #same name is used for input gauge than for output gauges
        f.write(str(self.model.gauge_time_step)+'\n')
        f.close()
        fmt = '%1.2f'
        with open(self.gauge_file_path,'ab') as f:
           np.savetxt(f,self.model.gauge, delimiter=" ", fmt=fmt)

    def _export_discharge_measurement_section(self):
        """Exports a file containing the discharges

        :return: a file composed by 
            Number of sections : for the moment only 1
            time step of measurement
            OutputDischargeName : default : discharge.txt
            The number of edges concerned
            the edges tags
        :rtype: .txt
        """
        if not self.model.is_discharge_measurement_section:
            return
        edges_data = []
        for elements in self.model.discharge_control_edges.values():
            edges_data.extend([len(elements), *elements.tolist()])
        with open(self.discharge_measurement_section_file_path, 'w') as f:
            f.write(f"{len(self.model.discharge_control_edges)} {self.model.discharge_measurement_time_step}\n")
            f.write(_DISCHARGE_OUTPUT_FILE + '\n')
        fmt = '%i'
        with open(self.discharge_measurement_section_file_path, 'ab') as f:
            np.savetxt(f, np.asarray(edges_data), delimiter=" ", fmt=fmt)
    
    def _export_watlab_basic_data(self):
        """
        A private function that exports the basic informations of the watlab class
        """
        self._export_nodes()
        self._export_cells()
        self._export_pic()
        self._export_gauge()
        self._export_discharge_measurement_section()
    
          
class Plotter():
    """ The Plotter class provides basic tools to the user. 
        Methods that allow to plot the data accross a line, or to generate a video are available. 
        The class is intended to be used combined with the MatPlotLib library.  
    """
    def __init__(self, mesh: Mesh):
        self.__mesh = mesh
        self.__cells_nodes = self.__mesh.cells[1]-1
        self.__nodes_coord = self.__mesh.nodes[1]
        self.__triangle_organization =  mtri.Triangulation(self.__nodes_coord[:,0],self.__nodes_coord[:,1],self.__cells_nodes)
        
    def __set_value_at_node(self,values):
        """
        Since the solver is a FV solver, the unknowns are at the cell's centers. 
        --------
        This function interpolates values of the desired plotted infos at nodes
        --------- 
        In : values np array : size nCells
        """ 
        X_barycenters, Y_barycenters = self.__mesh.get_cells_barycenters()[:,0], self.__mesh.get_cells_barycenters()[:,1]
        barycenters = np.column_stack((X_barycenters.flatten(), Y_barycenters.flatten()))
        mesh_x, mesh_y = self.__mesh.nodes[1][:,0], self.__mesh.nodes[1][:,1]
        mesh_points = np.column_stack((mesh_x.flatten(), mesh_y.flatten()))
        nearest_grid = griddata(barycenters, values, mesh_points, method='nearest')
        values_at_nodes = griddata(barycenters, values, mesh_points, method='linear')
        values_at_nodes[np.isnan(values_at_nodes)] = nearest_grid[np.isnan(values_at_nodes)] 
        return values_at_nodes
    
    def __extract_data_from_picture_file(self,file):
        data = pd.read_csv(file,sep='\s+')
        return data
    
    def plot_profile_along_line(self, picture_file_path: str, variable_name: str, x_coordinate=None, y_coordinate=None, starting_coordinate=0.,new_fig=False, n_points=50, label="", manning_values=None) -> None:
        """ 
        Plots the profile of the selected variable along a line defined by given coordinate points.

        :param picture_file_path: The path to the image file containing the data to plot.
        :type picture_file_path: str
        :param x_coordinate: A list or array of x-coordinates defining the line segment. 
                             Example: [x_P1, x_P2]
        :type x_coordinate: list or np.ndarray
        :param y_coordinate: A list or array of y-coordinates defining the line segment. 
                             Example: [y_P1, y_P2]
        :type y_coordinate: list or np.ndarray
        :param starting_coordinate: The starting point of the line segment.
        :type starting_coordinate: float, optional
        :param new_fig: If True, creates a new figure for the plot. 
                        If False, plots on the current figure. Defaults to False.
        :type new_fig: bool, optional
        :param variable_name: The name of the variable to plot.
        :type variable_name: str
        :param n_points: The number of interpolation points along the line. Defaults to 50.
        :type n_points: int, optional
        :param label: The label for the plot. Defaults to an empty string "".
        :type label: str, optional
        """
        if new_fig:
            plt.figure()
        if not label:
            label=variable_name
        data = self.__extract_data_from_picture_file(picture_file_path)

        var_to_plot = select_postprocessing_variable(data, variable_name, manning_values=manning_values)   
        values_at_nodes = self.__set_value_at_node(var_to_plot)
        interpolated_plane_value = mtri.LinearTriInterpolator(self.__triangle_organization,values_at_nodes)
        x, y = np.linspace(x_coordinate[0],x_coordinate[1],n_points), np.linspace(y_coordinate[0],y_coordinate[1],n_points)
        profile_values = interpolated_plane_value(x,y)        
        abscisses = starting_coordinate + np.linspace(0,np.sqrt((x_coordinate[1]-x_coordinate[0])**2+(y_coordinate[1]-y_coordinate[0])**2),n_points)        
        plt.plot(abscisses,profile_values,label=label)
        plt.legend()
        
    def plot(self, picture_file_path, variable_name: str, opacity=1, colorbar_values=None, manning_values=None):
        """
        Plots the specified variable from the provided picture file with various customization options.

        Interaction:
        - Press 'm' to display the mesh overlay on the plot.
        - Press 'd' and left-click on two different locations to draw a line between them, 
        which will trigger a pop-up displaying a profile cut along the selected line.

        :param picture_file_path: The path to the image file to be plotted.
        :type picture_file_path: str
        :param variable_name: The name of the variable to plot. Select the desired variable in the output file. 
        :type variable_name: str (as stated in the head of the pic file)
        :param opacity: A value between 0 and 1 to set the opacity of the plot. Defaults to 1.
        :type opacity: float, optional
        :param colorbar_values: The boundary valeus for the colorbar. Defaults to None, which automatically scales based on data range.
        :type colorbar_values: list, optional
        :raises ValueError: If the contour lines are not in increasing order, a ValueError will be caught and handled internally.
        """        
        def __on_clicked(event):
            global coords_x
            global coords_y
            ix, iy = event.xdata, event.ydata
            coords_x.append(ix)
            coords_y.append(iy)
            if len(coords_x)==2:
                plt.plot(coords_x,coords_y,color='red')
                plt.draw()
                print(coords_x,coords_y)
                self.plot_profile_along_line(picture_file_path, variable_name, coords_x, coords_y,new_fig=True, n_points = 50, label=variable_name,manning_values=manning_values)
                plt.gcf().canvas.mpl_disconnect(__on_clicked)
                plt.gcf().canvas.mpl_connect('key_press_event', __on_press)
                plt.show()


        def __on_press(event):
            global coords_x
            global coords_y
            print('press', event.key)
            sys.stdout.flush()
            if event.key == 'd':
                plt.gcf().canvas.mpl_disconnect(__on_press)
                coords_x = []
                coords_y = []
                plt.gcf().canvas.mpl_connect('button_press_event', __on_clicked)
            if event.key == 'm':
                plt.triplot(self.__triangle_organization,lw=0.1)
        
        data = self.__extract_data_from_picture_file(picture_file_path)
        var_to_plot = select_postprocessing_variable(data, variable_name, manning_values=manning_values)
        plt.gcf().canvas.mpl_connect('key_press_event', __on_press)
        if colorbar_values is None:
            levels = np.linspace(min(var_to_plot), max(var_to_plot), 100)
        else: 
            levels = np.linspace(colorbar_values[0], colorbar_values[1], 100)
        values_at_nodes = self.__set_value_at_node(var_to_plot)
        values_at_nodes = np.nan_to_num(values_at_nodes, nan=0.0)  # Replace NaN with 0.0
        try : 
            TC = plt.tricontourf(self.__triangle_organization,values_at_nodes,alpha=opacity,cmap=cm.turbo,levels=levels,antialiased=True,extend="max")
            plt.gca().set_aspect('equal', adjustable='box')
            cbar= plt.colorbar(TC,location="right")
            cbar.ax.locator_params(nbins=5)
            cbar.set_label(variable_name)
            return cbar
        except ValueError:
            print("Contour lines must be increasing, error has been catched") 
    
    def show_velocities(self, picture_file_path, velocities_tags=["qx","qy"], relative_depth_tag="h", velocity_ds=1, scale=1):
        """
        Plots the velocity field on a 2D plane using quiver arrows

        :param picture_file_path: The path to the file containing the velocity data.
        :type picture_file_path: str
        :param velocities_tags: A list of keys representing the velocity components in the output file.
            The default is ["qx", "qy"] where "qx" is the x-component and "qy" is the y-component.
        :type velocities_tags: list of str, optional
        :param relative_depth_tag: The key representing the relative depth (e.g., water height) in the data file. 
            Defaults to "h".
        :type relative_depth_tag: str, optional
        :param velocity_ds: Downsampling factor for the velocity vectors. A value between 0 and 1 that determines 
            the percentage of arrows displayed. Defaults to 1 (no downsampling).
        :type velocity_ds: float, optional
        :param scale: Scale factor to adjust the length of the velocity arrows. Defaults to 1.
        :type scale: float, optional
        """
        X, Y = self.__mesh.get_cells_barycenters()[:,0], self.__mesh.get_cells_barycenters()[:,1]
        data = self.__extract_data_from_picture_file(picture_file_path)
        velocity_x, velocity_y, depth = np.asarray(data[velocities_tags[0]]),np.asarray(data[velocities_tags[1]]), np.asarray(data[relative_depth_tag])
        v_x, v_y = velocity_x/depth, velocity_y/depth
        N = int(1/velocity_ds)
        plt.quiver(X[::N],Y[::N],v_x[::N],v_y[::N],scale = scale, color= 'r')

    def plot_on_map(self, pic_path, variable_name:str, opacity=0.5, colorbar_values=None, csr=31370, manning_values=None):
        """
        Plots the specified variable on a map using a specified coordinate reference system.

        :param pic_path: The path to the image file containing the data to plot.
        :type pic_path: str
        :param variable_name: The name of the variable to plot. Select the desired variable in the output file. 
        :type variable_name: str, optional
        :param opacity: A value between 0 and 1 to set the opacity of the plot. Defaults to 0.5.
        :type opacity: float, optional
        :param colorbar_values: The boundary valeus for the colorbar. Defaults to None, which automatically scales based on data range.
        :type colorbar_values: list, optional
        :param csr: The coordinate reference system for the map. Defaults to 31370, which is used in Belgium.
        :type csr: int, optional
        """
        self.plot(pic_path, variable_name=variable_name, opacity=opacity, colorbar_values=colorbar_values, manning_values=manning_values)
        ax = plt.gca()
        ctx.add_basemap(ax, crs=csr,source=ctx.providers.OpenStreetMap.Mapnik)
    
    def create_video(self, pic_path_template, video_filename, time_step, variable_name:str, opacity=1, colorbar_values = None, csr=31370, fps=5, on_map=False, manning_values=None):
        """ Creates a video from a sequence of image files, with options to overlay data on a map.

        :param pic_path_template: The template for the file paths of the images. 
            Example: "PathToFiles/pic_{:d}_{:02d}.txt"
        :type pic_path_template: str
        :param video_filename: The name of the output video file.
        :type video_filename: str
        :param time_step: The time interval between consecutive images.
        :type time_step: int
        :param variable_name: The name of the variable to plot. Select the desired variable in the output file. 
        :type variable_name: str, optional
        :param opacity: A value between 0 and 1 to set the opacity of the plot. Defaults to 1.
        :type opacity: float, optional
        :param colorbar_values: The boundary valeus for the colorbar. Defaults to None, which automatically scales based on data range.
        :type colorbar_values: list, optional
        :param csr: The coordinate reference system for the map. Defaults to 31370, which is used in Belgium.
        :type csr: int, optional
        :param fps: Frames per second for the video. Defaults to 5.
        :type fps: int, optional
        :param on_map: If True, the images will be plotted on a map. Defaults to False.
        :type on_map: bool, optional
        """
        file_list = []
        time_second = 0
        time_hundreds = 00

        while os.path.exists(pic_path_template.format(time_second,time_hundreds)):
            file_list.append(pic_path_template.format(time_second,time_hundreds))
            time_second += time_step

        frame_list = []
        n_files = len(file_list)
        print("Building Video frames")

        for i, file in enumerate(file_list):
            if on_map:
                self.plot_on_map(file, variable_name=variable_name,colorbar_values=colorbar_values, opacity=opacity, csr=csr, manning_values=manning_values)
            else:
                self.plot(file, variable_name=variable_name,colorbar_values=colorbar_values, opacity=opacity, manning_values=manning_values)
            plt.savefig("frame_{:d}.png".format(i),dpi=300)
            plt.close()
            frame_list.append("frame_{:d}.png".format(i))
            print("Proceeding:" + str(np.around(i/n_files*100,2))+"%")

        images = []
        for filename in frame_list:
            images.append(imageio.imread(filename))

        imageio.mimsave("{}.mp4".format(video_filename), images, fps=fps)
        print("Your video is ready")
        for frame in frame_list:
            os.remove(frame)