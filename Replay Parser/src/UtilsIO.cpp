#include <sstream>

#include "../include/UtilsIO.hpp"

char *readChars(std::istream &inStream, uint32_t size) {
	char *ret = new char[size+1];
	inStream.read(ret, size);
	ret[size] = '\0';
	return ret;
}

std::string readString(std::istream &inStream, uint32_t size) {
	char *chars = readChars(inStream, size);
	std::string ret = chars;
	delete[] chars;
	return ret;
}

template <>
char *readValue<char *>(std::istream &inStream) {
	uint32_t size;
	inStream.read(reinterpret_cast<char*>(&size), sizeof(size));
	return readChars(inStream, size);
}

template <>
std::string readValue<std::string>(std::istream &inStream) {
	uint32_t size;
	inStream.read(reinterpret_cast<char*>(&size), sizeof(size));
	return readString(inStream, size);
}

std::ofstream getOutStreamFromPath(std::string path, std::string_view extension) {
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
