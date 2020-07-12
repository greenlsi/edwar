![logoEDWAR](https://user-images.githubusercontent.com/17572800/87205571-0c325000-c308-11ea-89d9-c6f3bf6598af.png)
## signal Error Detection for WBSN And data Recovery.
Edwar is a system based on several
modules that allows processing of data collected by different 
devices such as [E4](https://www.empatica.com/en-eu/research/e4/) or 
[Everion](https://www.biovotion.com/everion/).

The processing focuses on features extraction, but it can include signal error
detection, and signal correction or reconstruction. This core version allows working with
electrodermal activity (EDA), interbeat intervals (IBI), accelerometry (ACC) and temperature (TEMP).

The results can be saved as an output variable, CSV files or in a data base. To contribute, visit the wiki.

# Core EDWAR
This core version is based on three modules: Loaders, Parsers and Savers. User specifies which modules to use in 
the structure file. This file can be generated with the following code:
```ruby
edwar.install.structure_cfg()
```
The user must introduce the name of the device, the Loader module needed, the files and variables to read and the Parsers and features to employ.
The system can be configurated for several devices, each one with its own files, Loaders and Parsers. If the user wants to edit the configuration 
for a specific device, this command must be used:
```ruby
edwar.configure.devices()
```
Finally, user can execute the system with the given configuration:
```ruby
edwar.Run(device='my_device', path='path_to_data_files').my_saver_module()
```
The supermodule Run interconects all modules according th the following schema:


![general_structure1](https://user-images.githubusercontent.com/17572800/87205868-b3af8280-c308-11ea-9c8f-95d100f4343e.png)


