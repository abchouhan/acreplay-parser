# acreplay-parser
This software consists of two parts: a [parser](#parser) for .acreplay files, and an [addon](#addon) to import the parsed data into Blender.

![Preview](https://github.com/abchouhan/acreplay-parser/assets/21346078/a9b80a66-d797-4846-9450-b21c15aa8d82)
![Cockpit](https://github.com/abchouhan/acreplay-parser/assets/21346078/0fc20366-2266-4adc-a2c3-939e418b9602)

## Parser
### Usage
Open an `.acreplay` file with the `acrp` executable and it will output data for each driver as `.json` files.
<br>
The `.json` files can then be imported into Blender with the [addon](#addon).

For more advanced options use the command line:
```
acrp [OPTIONS] [INPUT FILE(S)] with options:
-o, --output PATH
    Output path with optional file name.
    Default is "<input-filename>.json" in the directory of the executable.
    <driver-name> is concatenated to the end if all cars are to be parsed.

--driver-name NAME
    Name of driver whose vehicle is to be parsed.
    Parses all cars if unspecified.
```
### Building
Requirements:
- A compiler supporting C++23
- CMake

In the 'Replay Parser' folder, run the following command:
```
mkdir build && cd build && cmake ..
```
This will create a `Makefile` in the 'build' subfolder.
<br>
Use a compiler of choice to finish building the executable. For example:
```
make
```
The executable will be located in the 'build' subfolder.

## Addon
### Installation
- Download `Replay Blender Importer.zip` from the [Releases](https://github.com/abchouhan/acreplay-parser/releases) page
- In Blender go to Edit > Preferences and click 'Install', navigate to the downloaded file
- Enable the addon

### Usage
- Open the sidebar by going to View > Sidebar, or by pressing the <kbd>N</kbd> key
- Go to the Animation tab and locate the 'AC Replay Importer' tab
- Click 'Import .json' and navigate to the `.json` file(s) outputted by the [parser](#parser)
- Adjust framerate if necessary
- Assign the Chassis and Wheel slots appropriately <!-- TODO add video -->

### Building
Simply zip up the folder to get a file structure like:
```
Replay Blender Importer.zip
└── Replay Blender Importer
    ├── __init__.py
    └── ...
```
