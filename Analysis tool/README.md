# SiC data analysis
 Code for showing data from the SiC in space project in graphs. Some of the code is not SiC in space specific, but I 
 can not guarantee that the code will work in other cases. 

## Requirements
The code was written and tested on python 3.7 with the following packages.

    Python 3.7
    Matplotlib
    scipy

## Config file
The config file contains a number of parameters that can be set. If you would like to add any parameters, it is probably
easiest to do so in the "//Graph settings" section. Using the format
    
       key = string
      
will set a key in config[1][key] to 'string'. 

The resistor values are not yet decided at the time of writing this.

## Bugs
No known bugs. There are probably some bugs related to file paths.
It is recommended to run the unittests when something does not work. If the tests pass, but you still can't run the code
from the 'main' python file, try running the 'DataAnalysis.py' file. If that works, there is probably some weird file path
in the 'main' file or the config file itself. 

 
