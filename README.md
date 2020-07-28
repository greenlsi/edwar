![logoEDWAR](https://user-images.githubusercontent.com/17572800/87205571-0c325000-c308-11ea-89d9-c6f3bf6598af.png)
#### signal Error Detection for WBSN And data Recovery.
Edwar is a system based on several
modules that allows processing of data collected by different 
devices such as [E4](https://www.empatica.com/en-eu/research/e4/) or 
[Everion](https://www.biovotion.com/everion/).

The processing focuses on features extraction, but it can include signal error
detection, and signal correction or reconstruction. This core version allows working with
electrodermal activity (EDA), interbeat intervals (IBI), accelerometry (ACC) and temperature (TEMP).

The results can be saved as an output variable, CSV files or in a data base. To contribute, visit the wiki.

# Configuring EDWAR
This core version is based on three modules: Loaders, Parsers and Savers. User specifies which modules to use in 
the structure file. This file can be generated with the following code:
```ruby
edwar.install.structure_cfg()
```
After the installation, the system asks some information. 
The user must introduce several data fields. The first field is the device name the name of the device, the Loader module needed, the files and variables to read and the Parsers and features to employ.
The system can be configurated for several devices, each one with its own files, Loaders and Parsers. Initially there is a default configuration for E4 and
Everion devices. If the user wants to edit the configuration for a specific device, this command must be used:
```ruby
edwar.configure.devices()
```
Finally, user can execute the system with the given configuration:
```ruby
edwar.Run(device='my_device', path='path_to_data_files').my_saver_module()
```
The supermodule Run interconects all modules according th the following schema:


![general_structure1](https://user-images.githubusercontent.com/17572800/87205868-b3af8280-c308-11ea-9c8f-95d100f4343e.png)


<a name="read"></a>
# Data Reading
Currently, data can be read from E4 and Everion devices. In the structure configuration, file names must be given. The path to the file is not relevant, it will be 
specified in the Run supermodule parameters. For each file, the Loader needs the name of the signals in each column. The order is important. In accelerometry file, for example, the variables are x, y, z, not y, x, z or z, y, x. The name of the variables must coincide with the Parsers input name. Otherwise the Parser will not recognize the signal. 
These inputs are descibe in [Data Processing](#proc)

### E4
E4 structures the data in several CSV files with the name of the signal as name of file (EDA.csv, IBI.csv...).
For the E4 Loader, only the name of the file must be introduced, with no extension (ACC.csv -> ACC). 

### Everion
Everion file name are long, so the user must introduce only a part, the signal name. For example, for the following IBI file:
bop_1533550392847_IBI_5b2cc93e71b0710100a724db_1533160800_1533247259.csv -> IBI

Everion files have several columns with IDs, timestamps, quality of measure... The Loader reads the variable values and timestamps columns. The variable name
must be the one expected from the Parser. In case of sweating signal, Everion calls it GSR (Galvanic Skin Response), others use SC (Skin Conductivity), but the Parser module expects a variable called EDA.


<a name="proc"></a>
# Data Processing
There are 4 Parsers. The following table describes the input variables and the output features calculated in each Parser.

Input Variable | Parser | Output
:---: | :---: | :---:
*EDA* | `EDAparser` | *EDA, ERROR, SCL, SCR, SNMA*
*IBI* | `IBIparser` | *IBI, ERROR, HR*
*ACC* | `ACCparser` | *HAND, ACT*





