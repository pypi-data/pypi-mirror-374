Watlab is Python-API dedicated to hydraulics simulations. The Python-API allows you to drive the different solvers available in the toolbox.
The following prerequisites are mandatory to use Watlab:

1. A working version of Python
2. Some basic knowledge on Python scripting
3. A mesh made with [GMSH](http://gmsh.info/bin/Windows/) (see also our [website](https://sites.uclouvain.be/hydraulics-group/watlab)).


## Get Watlab

Watlab is supported on Python 3.11 or later.

Watlab installation is complicated by its (weak) dependency to the libgdal package. On Linux and MacOS, installation is included in the resterio installer. On Windows, one needs to install GDAL first.

If necessary, you can download the installers here:

- Download [gdal 3.4.3 for Windows](https://sites.uclouvain.be/hydraulics-group/watlab/_downloads/36e8b3bb4c1d9baac4703d0b297b2132/GDAL-3.4.3-cp311-cp311-win_amd64.whl) (for Win_AMD64; for another version, see [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal>)).


Install GDAL before you install watlab. On Windows hit :

```
python -m pip install GDAL-3.4.3-cp311-cp311-wind_amd64.whl
python -m pip install watlab
```

On Linux and Mac, hit:

```
sudo apt update
sudo apt install libglu1
sudo apt install libxcursor1
sudo apt install libxft2
sudo apt install libxinerama1
python -m pip install watlab
```


## Run Watlab (for the impatients)

In order to test your Watlab instance, create a folder somewhere in your computer (say in `~/usr/myWatlab/`) and unzip [this archive](https://sites.uclouvain.be/hydraulics-group/watlab/_downloads/a686ec9a86cb0bf629c3318ac2d64a62/watlab-first-script.zip).

Open the Conda prompt and activate your newly created `watlab` environment:

```
conda activate watlab
```

Then run the script with

```
python .\watlab-first-script.python
```

If you see the following pictures then it worked!

<figure>
    <img src="https://sites.uclouvain.be/hydraulics-group/watlab/_images/first-script-output-1.png"
         alt="A first script output"
         width=380>
</figure>

<figure>
    <img src="https://sites.uclouvain.be/hydraulics-group/watlab/_images/first-script-output-2.png"
         alt="A second script output"
         width=380>
</figure>


## License

This source code is not yet placed under open source licence. Meanwhile, this code is the property of Prof. Sandra Soares-Frazão.
GPL-3 open source copyright to come.

Please copy the following text in your LICENCE file while using Watlab as a subpackage of your work.

```
Watlab - Copyright (C) <1998 – 2024> <Université catholique de Louvain (UCLouvain), Belgique> 

This program (Watlab) is free software: you can redistribute it and/or modify it under the terms 
of the GNU General Public License as published by the Free Software Foundation, either version 3 
of the License, or (at your option) any later version.
   
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program (see COPYING file).  If not, 
see <http://www.gnu.org/licenses/>.
```

## Development team

The development team is composed of the members of the GCE lab of Hydraulics, from UCLouvain. The contributors are:

- [Nathan Delpierre](nathan.delpierre@uclouvain.be>)
- [Pierre-Yves Gousenbourger](pierre-yves.gousenbourger@uclouvain.be)
- [Robin Meurice](robin.meurice@uclouvain.be)
- [Martin Petitjean](martin.petitjean@uclouvain.be)
- [Charles Ryckmans](charles.ryckmans@uclouvain.be)
- [Sandra Soares-Frazão](sandra.soares-frazao@uclouvain.be) (first contributor)
- Catherine Swartenbroeckx
- Sylvie Van Emelen
- Mirjana Velickovic
- [Jiangtao Yang](jiangtao.yang@uclouvain.be)
