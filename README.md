# Summer Research Scholarship Project

This program takes a small binary phylogenetic network in extended newick format
and generates trees displayed by the network. It can open text files containing 
the network in newick format and export the generated network as image files. 

Version 1.0\
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
phylonetwork==2.1
DendroPy==4.4.0
cached_property==1.5.2
networkx==2.5
matplotlib==3.3.3
```
