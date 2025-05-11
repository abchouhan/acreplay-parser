# acreplay-parser
This software consists of two parts: a [parser](#parser) for Assetto Corsa replay (.acreplay) files, and an [addon](#addon) to import the parsed data into Blender.
A video guide is available [here](https://youtube.com/watch?v=ZBwSbNptEmM).

![Preview](https://github.com/abchouhan/acreplay-parser/assets/21346078/a9b80a66-d797-4846-9450-b21c15aa8d82)
![Cockpit](https://github.com/abchouhan/acreplay-parser/assets/21346078/0fc20366-2266-4adc-a2c3-939e418b9602)

## Parser
### Usage
- Download and extract a 'ReplayParser' file from the [Releases](https://github.com/abchouhan/acreplay-parser/releases) page
- Open an `.acreplay` file with the `acrp` executable and it will output data for each driver as `.json` files.
- Import the `.json` files into Blender with the [addon](#addon).

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
- A compiler supporting [C++23 extended floating-point types](https://en.cppreference.com/w/cpp/types/floating-point) (GCC recommended)
- [zlib](https://github.com/madler/zlib)
- CMake

In the 'Replay Parser' folder, run the following command:
```
cmake -B build -S .
```
This will create a `Makefile` in the 'build' subfolder.
<br>
Finish building the executable:
```
cmake --build build --parallel
```
The executable will be located in the 'build' subfolder.

## Addon
### Installation
- For Blender versions ≥ 4.2.0
  - Install through [Blender Extensions](https://extensions.blender.org/add-ons/acreplay-importer/)
- For Blender versions ≥ 3.0.0
  - Download the latest 'Replay Blender Importer' zip file from the [Releases](https://github.com/abchouhan/acreplay-parser/releases) page
  - In Blender go to Edit → Preferences and click 'Install', navigate to the downloaded file
  - Enable the addon

### Usage
- Open the sidebar by going to View → Sidebar, or by pressing the <kbd>N</kbd> key
- Go to the Animation tab and locate the 'AC Replay Importer' dropdown
- Click 'Import .json' and navigate to the `.json` file outputted by the [parser](#parser)
- Adjust framerate if necessary
- Assign the Chassis and Wheel slots appropriately (see [video guide](https://youtube.com/watch?v=ZBwSbNptEmM))

### Building
#### For Blender 4.2.0 and beyond
In the 'Replay Blender Importer' folder, run the following command:
```
blender --command extension build
```
This creates a zip file 'acreplay_importer-x.x.x.zip' which can be installed in Blender.
#### For Blender 3.0.0-4.1.x
See the [0.2.0 Blender 3.0.0 branch](https://github.com/abchouhan/acreplay-parser/tree/0.2.0_blender-3.0.0?tab=readme-ov-file#building-1)
