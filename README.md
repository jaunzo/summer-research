# Summer Research Scholarship Project

This program takes a small binary phylogenetic network in extended newick format
and generates trees displayed by the network. It can also calculate drSPR when 
given at least 2 trees. When more than 2 trees are inputted, all trees are 
compared pairwise. It can open text files containing the network in newick 
format and export the generated network as text or image files.

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
## Contents of requirements.txt
```
networkx==2.5
phylonetwork==2.1
cached_property==1.5.2
matplotlib==3.3.3
```

## Credits
This program uses [cwhidden's rspr software package](https://github.com/cwhidden/rspr).

## 
