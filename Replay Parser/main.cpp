#include <iostream>
#include <cstring>

#include "include/ACReplayParser.hpp"

int noInputError() {
    std::cerr << "An input file is required." << std::endl;
    std::cerr << "Use --help for a list of all options." << std::endl;
    return EXIT_FAILURE;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
		return noInputError();
	}

	std::vector<std::string> inPaths;
	std::string outPath;
	std::string targetDriverName;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "-help") == 0 || strcmp(argv[i], "--help") == 0) {
            std::cout << "Assetto Corsa Replay Parser 0.2.0" << std::endl;
            std::cout << "Usage: acrp [OPTIONS] [INPUT FILE(S)]\n\nwith options:" << std::endl;
            std::cout << "-o, --output PATH\n\tOutput path with optional file name." << std::endl;
            std::cout << "\tDefault is \"<input-filename>.json\" in the directory of the executable." << std::endl;
            std::cout << "\t<driver-name> is concatenated to the end if all cars are to be parsed.\n" << std::endl;
            std::cout << "--driver-name NAME\n\tName of driver whose car is to be parsed." << std::endl;
            std::cout << "\tParses all cars if unspecified.\n" << std::endl;
            return EXIT_SUCCESS;
        } else if (strcmp(argv[i], "-o") == 0 || strcmp(argv[i], "--output") == 0) {
            if (i+1 < argc) {
                outPath = argv[++i];
            } else {
                std::cerr << "--output option requires one argument." << std::endl;
                return EXIT_FAILURE;
            }
        } else if (strcmp(argv[i], "--driver-name") == 0) {
            if (i+1 < argc) {
                targetDriverName = argv[++i];
            } else {
                std::cerr << "--driver-name option requires one argument." << std::endl;
                return EXIT_FAILURE;
            }
        } else {
            inPaths.push_back(argv[i]);
        }
    }

    if (inPaths.size() < 1) {
        return noInputError();
    }

	for (size_t i = 0; i < inPaths.size(); i++) {
        readAndOutput(inPaths[i], outPath, targetDriverName);
        if (i != inPaths.size()-1) {
            std::cout << "-----------------------------" << std::endl;
        }
    }
    return EXIT_SUCCESS;
}
