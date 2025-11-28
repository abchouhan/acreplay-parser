#include <vector>
#include <print>
#include <cstring>

#include "ACReplayParser.hpp"

int noInputError() {
	std::fputs("An input file is required.\nUse --help for a list of all options.\n", stderr);
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
			std::puts(
				"Assetto Corsa Replay Parser 0.3.0\n"
				"Usage: acrp [OPTIONS] [INPUT FILE(S)]\n\nwith options:\n"
				"-o, --output PATH\n\tOutput path with optional file name.\n"
				"\tDefault is \"<input-filename>.csv\" in the directory of the executable.\n\n"
				"--driver-name NAME\n\tName of driver whose car is to be parsed.\n"
				"\tParses all cars if unspecified.\n"
				"\t<driver-name> is concatenated to the file name if unspecified.");
            return EXIT_SUCCESS;
        } else if (strcmp(argv[i], "-o") == 0 || strcmp(argv[i], "--output") == 0) {
            if (i+1 < argc) {
                outPath = argv[++i];
            } else {
				std::fputs("--output option requires one argument.\n", stderr);
                return EXIT_FAILURE;
            }
        } else if (strcmp(argv[i], "--driver-name") == 0) {
            if (i+1 < argc) {
                targetDriverName = argv[++i];
            } else {
				std::fputs("--driver-name option requires one argument.\n", stderr);
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
			std::puts("-----------------------------");
        }
    }
    return EXIT_SUCCESS;
}
