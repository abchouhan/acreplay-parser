#include "UtilsIO.hpp"

char *readChars(std::istream &inStream, uint32_t size) {
	char *c = new char[size+1];
	inStream.read(c, size);
	c[size] = '\0';
	return c;
}

std::string readString(std::istream &inStream, uint32_t size) {
	std::string str(size, '\0');
	inStream.read(str.data(), size);
	return str;
}

template <>
char *readValue<char *>(std::istream &inStream) {
	uint32_t size;
	inStream.read(reinterpret_cast<char *>(&size), sizeof(size));
	return readChars(inStream, size);
}

template <>
std::string readValue<std::string>(std::istream &inStream) {
	uint32_t size;
	inStream.read(reinterpret_cast<char *>(&size), sizeof(size));
	return readString(inStream, size);
}

void getUniquePath(std::filesystem::path &path) {
	if (!std::filesystem::exists(path)) return;

	std::string extension = path.extension().string();
	std::string filename = path.stem().string()+" (";

	unsigned int i = 2;
	while (std::filesystem::exists(path)) {
		path.replace_filename(filename+std::to_string(i)+")"+extension);
		i++;
	}
}
