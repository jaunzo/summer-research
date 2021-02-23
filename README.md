# Summer Research Scholarship Project

This program can generate embedded trees from a small, binary, phylogenetic 
network, calculate rooted subtree prune and regraft distance (drSPR) and 
create an rSPR graph from a small set of trees. The program accepts trees 
in Newick format and networks in extended Newick format where each tree/network 
is terminated by a semicolon. It can save output results as a text file or 
as series of images if graphics is enabled.

--------------------------------------------------------------------

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

--------------------------------------------------------------------
Python 3.8.6  

&nbsp;

## Installation requirements

This program requires Graphviz to be installed to enable graph visualisation. Instructions on how to install found [here](https://bobswift.atlassian.net/wiki/spaces/GVIZ/pages/20971549/How+to+install+Graphviz+software).  

&nbsp;

## Check Graphviz installation
The Graphviz executables must be in PATH.
To check if Graphviz is installed run the following command in Command Prompt (Windows) or Terminal (Mac)
```
dot -V
```

&nbsp;

If it is installed, the version number will be displayed. For example:
```
dot - graphviz version 2.44.1 (20200629.0846)
```

&nbsp;
## Scaling on Windows
If you have a high dpi monitor and the program is too small,
- Right click on phyloprogram.exe
- Click "Properties"
- Click the "Compatibility" tab
- Click "Change high DPI settings"
- Check option "Override high DPI scaling behaviour" and select "Application" in the
  Drop down menu
- Apply the changes 

&nbsp;
## Contents of requirements.txt
```
networkx==2.5
matplotlib==3.3.3
phylonetwork==2.1
cached_property==1.5.2
```

&nbsp;
## Capabilities
This program can draw trees of networks that have less than 7 reticulations 
and/or 10 leaves. Run the program without graph visualisation if the input 
network contains less than 10 reticulations and/or 15-20 leaves.


&nbsp;
## Credits
This program uses cwhidden's [rspr](https://github.com/cwhidden/rspr) and [spr_neighbors](https://github.com/cwhidden/spr_neighbors) software packages.

## 
