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

# Starting with EDWAR
This core version is based on three modules: Loaders, Parsers and Savers. User specifies which modules to use in a given configuration. 
The following command lets install the configuration file needed.
```ruby
edwar.install.structure_cfg()
```
After the installation, the system automatically asks some information, structured in several data fields: [device selection](#dev), [input collection](#read) and 
[output  collection](#proc).

![DIAGRAM_STEPS](https://user-images.githubusercontent.com/17572800/88675164-f041f300-d0ea-11ea-9885-c365e874ef42.png)

The system can be configurated for several devices, each one with its own files, Loaders and Parsers. Initially there is a default configuration for E4 and
Everion devices. If the user wants to edit the configuration for a specific device, this command must be used:
```ruby
edwar.configure.devices()
```
The steps followed in installation will be repeated.
Finally, user can execute the system with the given configuration:
```ruby
edwar.Run(device='my_device', path='path_to_data_files').my_saver_module()
```
The supermodule Run interconects all modules according th the following schema:


![general_structure1](https://user-images.githubusercontent.com/17572800/87205868-b3af8280-c308-11ea-9c8f-95d100f4343e.png)

<a name="dev"></a>
# Device Configuration
In the first configuration step system requests the device name. According to each device, different data files and variables will be used, 
so a specific Loader module is required. In this core version, Loaders to read data from E4 and Everion devices can be used.
If the Loader needed is not listed, leave it blank. It will be declared as parameter in the run function.
In the next steps, [variables](#read) and [features](#proc) must be declared for this device.

<a name="read"></a>
# Data Reading
For each device, system asks for the input data, so file names must be given. Every Loader gives facilities to introduce this data, so it is important to know what expects each Loader before introducing the file names. The file path is not relevant, it will be 
specified in the run function parameters. For each file, the Loader needs the name of the signals in each column. The order is important. In accelerometry file, for example, the variables are x, y, z, not y, x, z or z, y, x. The name of the variables must coincide with the Parser modules input name. Otherwise the Parser will not recognize the signal. 
These inputs are descibe in [Data Processing](#proc)

### E4
E4 structures the data in several CSV files with the name of the signal as name of file (EDA.csv, IBI.csv...).
For the E4 Loader, only the name of the file must be introduced, with no extension (ACC.csv -> ACC). 

### Everion
Everion file name are long, so the user must introduce only a part, the signal name preferably. For example, for the following IBI file:
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
*TEMP*| `TEMPparser`| *TEMP*





