#include "../include/UtilsIO.h"

char *readChars(std::ifstream &inFile, uint32_t size) {
	char *ret = new char[size+1];
	inFile.read(ret, size);
	ret[size] = '\0';
	return ret;
}

std::string readString(std::ifstream &inFile, uint32_t size) {
	char *chars = readChars(inFile, size);
	std::string ret = chars;
	delete[] chars;
	return ret;
}

template <>
char *readValue<char *>(std::ifstream &inFile) {
	uint32_t size;
	inFile.read(reinterpret_cast<char*>(&size), sizeof(size));
	return readChars(inFile, size);
}

template <>
std::string readValue<std::string>(std::ifstream &inFile) {
	uint32_t size;
	inFile.read(reinterpret_cast<char*>(&size), sizeof(size));
	return readString(inFile, size);
}

std::ofstream getOutStreamFromPath(std::string path, std::string extension) {
	std::ofstream outFile(path, std::ofstream::out|std::ios::in);
	std::string newPath = path;

	int i = 2;
	while (outFile) {
		outFile.close();
		std::stringstream outDuplicate;
		outDuplicate << path.substr(0, path.length()-extension.length()) << " (" << i << ")" << extension;
		newPath = outDuplicate.str();
		outFile.open(newPath, std::ofstream::out|std::ios::in);
		i++;
	}

	outFile.close();
	outFile.open(newPath);
	return outFile;
}
