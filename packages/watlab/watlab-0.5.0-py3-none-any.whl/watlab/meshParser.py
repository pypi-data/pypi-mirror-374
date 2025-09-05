# Watlab-MeshParser General Conditions
# -----------------------------------------
# Licensed under the BSD 3-Clause License (the "License");
# you may not use this file except in compliance with the License.

# Copyright (c) <2024> <Universite catholique de Louvain (UCLouvain), Belgique>
# All rights reserved.

# Authors (all affiliate to Université catholique de Louvain (UCLouvain), Belgique) : Delpierre Nathan; Gousenbourger Pierre-Yves; Ryckmans Charles

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# *************************************************************************
# This program has dependencies on other libraries and Website depedencies which are or not under BSD license and that are commonly used with this program core libraries.

# Dependencies are as follows:

# Name					Licence type			Website				
# numpy (v1.26)			3-clauses BSD 			https://numpy.org/

# External executables
# ---------------------

# External executables are also needed for a proper execution of this program. These executables are not part of this program and have to be used according to their own license.

# External executables are (license are given for information purpose only) :
# gmsh (v4.11)	 		GNU GPL v2 or later			https://gmsh.info/


# Licences & Credits of dependencies
# ----------------------------------

# #####
# NUMPY
# #####

# Copyright (c) 2005-2023, NumPy Developers.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:

#     * Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.

#     * Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided
#        with the distribution.

#     * Neither the name of the NumPy Developers nor the names of any
#        contributors may be used to endorse or promote products derived
#        from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# -----------------------------------------------------------------------------

####################

# Copyright (C) <1998 – 2024> <Université catholique de Louvain (UCLouvain), Belgique> 
	
# List of the contributors to the development of Watlab: see AUTHORS file.
# Description and complete License: see LICENSE file.
	
# This program (Watlab) is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program (see COPYING file).  If not, 
# see <http://www.gnu.org/licenses/>.


import gmsh
import numpy as np
import warnings 

if not gmsh.is_initialized():
    gmsh.initialize()
    gmsh.option.setNumber("General.Verbosity", 2)
    

class MeshParser():
    """This class aims at extracting the information of .msh files to be 
        compatible with the Watlab philosophy.
        Mainly, the GMSH API is used to extract the data. 
        HydroFlow requires mainly informations on cells centers, nodes, regions...
        In HydroFlow, this class should not be used directly by the users? \n 
        It must be initialized by giving a path to a .msh.

    :param msh_mesh: a mesh file containg a mesh from GMSH
    :type msh_mesh: string
    """

    def __init__(self,msh_mesh):
        """Constructs a MeshParser based on a .msh file containing a mesh from GMSH.
        """
        gmsh.open(msh_mesh)
        self.__model = gmsh.model
        self.__mesh = gmsh.model.mesh

    def __parse_elements(self,elements_data,dim=3):
        """Parses the elements with gmsh get functions.
            The elements must me stored in a list of arrays as: elements_data = (array(tags),array(elements))
        """
        
        n_elem = len(elements_data[0])
        elements = elements_data[1].reshape(n_elem,dim)
        tags = elements_data[0].reshape(n_elem)
        return elements, tags

    def __sort_elements_by_tag(self,tags,elements):
        """Sorts the parsed elements by tag.

        :param tags: a n x 1 array
        :type tags: nDArray
        :param elements: a n x dim array
        :type elements: nDArray
        :return: tags and elem, sorted by tags
        :rtype: nDArray
        """
        
        idx = np.argsort(tags)
        tags = tags[idx]
        elements = elements[idx]
        return elements,tags
    
    def extract_nodes(self):
        """Extracts the nodes from the GMSH mesh
        
        :return: nodes and tags
        :rtype: nDArray
        """
        nodes, tags = self.__parse_elements(self.__mesh.getNodes(),dim=3)
        return nodes, tags
    
    def extract_cells(self):
        """Extracts the cells from the GMSH mesh 

        :raises Exception: There is no cells in the provided mesh
        :return: cells and tags_cells
        :rtype: nDArray
        """
        
        # Cells are supposed to be GMSH-elements of type 2.
        if (2 in self.__mesh.getElementTypes()):
            cells_data = self.__mesh.getElementsByType(2)
        else:
            raise Exception("There is no cells in the provided mesh")

        # Parse the result
        cells, tags_cells = self.__parse_elements(cells_data,dim=3)
        nodes,tags_nodes = self.extract_nodes()

        node_1 = nodes[cells[:,0]-1]
        node_2 = nodes[cells[:,1]-1]
        node_3 = nodes[cells[:,2]-1]

        x1 = node_1[:,0]
        y1 = node_1[:,1]
        x2 = node_2[:,0]
        y2 = node_2[:,1]
        x3 = node_3[:,0]
        y3 = node_3[:,1]
        
        # clockwise = [(x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1) < 0]
        # cells[tuple(clockwise)] = cells[tuple(clockwise)][:,::-1]

        return cells, tags_cells

    def extract_edges(self):
        """Extracts the edges' interfaces from the GMSH mesh and returns the tag of the edge

        :raises Exception: Orientations of cells cannot be different than -1 or 1
        :return: edgeNode = the nodes composing each edge oriented positively
            edgeCells = an array of the left and right cells tags
            tags = an array of the unsorted edges tags
            edgeTags = an array of the sorted edges tags
        :rtype: nDArray
        """
        
        # extract edges and cells
        celltags = self.extract_cells()[1]

        # getting edges for each elements
        self.__mesh.createEdges()
        allEdges = self.__mesh.getElementEdgeNodes(2)
        edgeTags, edgeOrientations = self.__mesh.getEdges(allEdges)

        allEdges = allEdges.reshape(len(edgeTags),2)
        # keep only unique tags and edges (they are counted twice)
        tags, tags_idx = np.unique(edgeTags,return_index=True)
        edgeNodes = np.sort(allEdges[tags_idx])

        # prepare structure for cells on the edges
        edgeCells = -np.ones(edgeNodes.shape,dtype=np.int64)
        tag_to_index = {tag: idx for idx, tag in enumerate(tags)}
        idx_cells = np.floor(np.arange(len(edgeTags))/3).astype(int)
        cell_tags = celltags[idx_cells]
        idx_edges = np.array([tag_to_index[tag] for tag in edgeTags])

        for idx_edgeNode in range(len(edgeTags)):
            # tags and orientations
            cell_tag = cell_tags[idx_edgeNode]
            edge_orientation = edgeOrientations[idx_edgeNode]
            
            idx_edge = idx_edges[idx_edgeNode]
            if edge_orientation == 1:
                if edgeCells[idx_edge,0] == -1: 
                    edgeCells[idx_edge,0] = cell_tag
                else: 
                    edgeCells[idx_edge,1] = cell_tag
                    
            elif edge_orientation == -1:
                if edgeCells[idx_edge,1] == -1: 
                    edgeCells[idx_edge,1] = cell_tag
                else: 
                    edgeCells[idx_edge,0] = cell_tag
                    
            else:
                raise Exception("Orientations cannot be different than -1 or 1")
        # returning tag, edge and left/right cells
        sorter = np.where(edgeCells[:,0]==-1)[0]

        edgeCells[sorter,:] =  edgeCells[sorter,::-1]
        edgeNodes[sorter,:] = edgeNodes[sorter,::-1]

        tags = np.array(tags).reshape(len(tags))
        return edgeNodes, edgeCells, tags, edgeTags

    def extract_physical_groups(self,dim) -> dict:
        """Extracts physical groups of dimension dim with their names.

        :param dim: a specific dimension 0,1,2
        :type dim: int
        :return: groups = a dictionnary corresponding to the entities of a physical group for a specific dimension
        :rtype: dict
        """
        
        physical_groups = self.__model.getPhysicalGroups(dim)
        groups = {}
        for group in physical_groups:
            groups[group[1]] = self.__model.getPhysicalName(dim,group[1])            

        return groups
    
    def extract_cells_by_physical_group(self,dim) -> dict:
        """Extracts the cells for each entity of a physical group and
            stacks them all in a dictionnary where the key is the physical group.

        :param dim: a specific dimension 0,1,2
        :type dim: int
        :return: a dictionnary corresponding to the cells of a specific dimension
        :rtype: dict
        """
        groups = self.extract_physical_groups(dim)
        # entities_by_group = self.extract_entities_by_physical_groups()
        elements_of_groups = {}
        for group in groups.keys():
            tags = np.array([])
            entities = self.__model.getEntitiesForPhysicalGroup(dim,group)
            for entity in entities:
                entity_element_tags = self.__mesh.getElementsByType(dim,entity)[0]
                tags = np.hstack((tags,entity_element_tags)) if tags.size else entity_element_tags

            elements_of_groups[group] = tags

        return elements_of_groups

    def extract_cells_barycenters(self):
        """Extracts the cells barycenters from the GMSH mesh

        :return: barycenters = all the barycenters of each cell of the domain
        :rtype: nDArray
        """
        return self.__mesh.getBarycenters(2,-1,False,False)