#ifndef UTILSIO_H
#define UTILSIO_H

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <cstdint>
#include <type_traits>

/**
 * Utility functions for common IO operations.
 * Some implementations included due to template use.
 */

/**
 * Read and return char * from given file at its current position in the stream.
 *
 * @param inFile file to be read from.
 * @param size length of char * to be read.
 * @return string of chars that was read from inFile.
 */
char *readChars(std::ifstream &inFile, uint32_t size);
/**
 * Read and return string from given file at its current position in the stream.
 *
 * @param inFile file to be read from.
 * @param size length of string to be read.
 * @return string that was read from inFile.
 */
std::string readString(std::ifstream &inFile, uint32_t size);

/**
 * Read and return value of type T from given file at its current position in the stream.
 *
 * @param inFile file to be read from.
 * @return value of type T that was read from inFile.
 */
template <typename T>
T readValue(std::ifstream &inFile) {
	T var;
	inFile.read(reinterpret_cast<char*>(&var), sizeof(var));
	return var;
}
/**
 * Read and return char * value from given file at its current position in the stream.
 * Specialized template function that first reads int for char * length and then reads char *.
 *
 * @param inFile file to be read from.
 * @return char * value that was read from inFile.
 */
template <>
char *readValue<char *>(std::ifstream &inFile);
/**
 * Read and return string value from given file at its current position in the stream.
 * Specialized template function that first reads int for string length and then reads string.
 *
 * @param inFile file to be read from.
 * @return string value that was read from inFile.
 */
template <>
std::string readValue<std::string>(std::ifstream &inFile);

/**
 * Determine whether type T is a string/char *, or not.
 */
template<typename T>
struct isStringType {
    static bool const value = std::is_same<T, char *>::value || std::is_same<T, std::string>::value;
};

/**
 * Read and print value of generic type T from given inFile at its current position in the stream.
 *
 * @param inFile file to be read from.
 * @param prefix string to be prefixed before the target value.
 */
template <typename T>
std::enable_if_t<!isStringType<T>::value, void> printValue(std::ifstream &inFile, std::string prefix) {
	T var;
	inFile.read(reinterpret_cast<char*>(&var), sizeof(var));
	std::cout << prefix << var << std::endl;
}
/**
 * Read and print string value from given inFile at its current position in the stream.
 * Overloaded function that first reads int for string length and then reads string.
 *
 * @param inFile file to be read from.
 * @param prefix string to be prefixed before the target value.
 */
template <typename T>
std::enable_if_t<isStringType<T>::value, void> printValue(std::ifstream &inFile, std::string prefix) {
	uint32_t stringSize;
	inFile.read(reinterpret_cast<char*>(&stringSize), sizeof(stringSize));
	char *chars = readChars(inFile, stringSize);
	std::cout << prefix << chars << std::endl;
	delete[] chars;
}

/**
 * Return an output stream of a file with the given path.
 * If it already exists, make a new file with the same name with an appended "(n)".
 *
 * @param path path to target file.
 * @param extension extension of target file.
 * @return output stream to a new file.
 */
std::ofstream getOutStreamFromPath(std::string path, std::string extension);

/**
 * Overloaded function for base case of outputting vector to file.
 * Generally shouldn't be called explicitly.
 *
 * @param outFile file to write to.
 * @param val value to be outputted.
 */
template <typename T>
void outputVectorToFile(std::ofstream &outFile, T val) {
	if (!std::is_fundamental<T>::value) return;

	if (typeid(T) == typeid(uint8_t) || typeid(T) == typeid(int8_t)) {
		outFile << +val;
	} else {
		outFile << val;
	}
}
/**
 * Output given numerical n-dimensional vector (with n > 1) to given outFile with JSON syntax.
 *
 * @param outFile file to write to.
 * @param vec vector to be outputted.
 * @param name string to be prefixed before the vec's output value.
 */
template <typename T>
void outputVectorToFile(std::ofstream &outFile, std::vector<T> vec, std::string name = "", bool endWithComma = true) {
	if (!name.empty()) {
		outFile << "\"" << name << "\": [";
	} else {
		outFile << "[";
	}
	for (unsigned long i = 0; i < vec.size(); i++) {
		outputVectorToFile(outFile, vec[i]);
		if (i < vec.size()-1) outFile << ", ";
	}
	outFile << "]";
	if (!name.empty()) {
		if (endWithComma) outFile << ", ";
		outFile << std::endl;
	}
}

#endif
