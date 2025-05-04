#pragma once

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <cstdint>

/**
 * Utility functions for common IO operations.
 * Some implementations included due to template use.
 */

/**
 * Read and return char * from given stream at its current position.
 *
 * @param inStream stream to be read from.
 * @param size length of char * to be read.
 * @return heap-allocated string of chars that was read from inStream.
 */
char *readChars(std::istream &inStream, uint32_t size);
/**
 * Read and return string from given stream at its current position.
 *
 * @param inStream stream to be read from.
 * @param size length of string to be read.
 * @return string that was read from inStream.
 */
std::string readString(std::istream &inStream, uint32_t size);

/**
 * Read and output array of type T from given stream at its current position.
 *
 * @param inStream stream to be read from.
 * @param count number of Ts to be read.
 * @param out pointer to array of Ts that is to be written to.
 */
template <typename T>
void readValueArray(std::istream &inStream, uint32_t count, T *const out) {
	inStream.read(reinterpret_cast<char *>(out), count*sizeof(T));
}
/**
 * Read and return value of type T from given stream at its current position.
 *
 * @param inStream stream to be read from.
 * @return value of type T that was read from inStream.
 */
template <typename T>
T readValue(std::istream &inStream) {
	T var;
	inStream.read(reinterpret_cast<char *>(&var), sizeof(var));
	return var;
}
/**
 * Read and return char * value from given stream at its current position.
 * Specialized template function that first reads int for char * length and then reads char *.
 *
 * @param inStream stream to be read from.
 * @return char * value that was read from inStream.
 */
template <>
char *readValue<char *>(std::istream &inStream);
/**
 * Read and return string value from given stream at its current position.
 * Specialized template function that first reads int for string length and then reads string.
 *
 * @param inStream stream to be read from.
 * @return string value that was read from inStream.
 */
template <>
std::string readValue<std::string>(std::istream &inStream);

/**
 * Determine whether type T is a string/char *, or not.
 */
template<typename T>
struct isStringType {
    static bool const value = std::is_same<T, char *>::value || std::is_same<T, std::string>::value;
};

/**
 * Read and print value of generic type T from given inStream at its current position.
 *
 * @param inStream stream to be read from.
 * @param prefix string to be prefixed before the target value.
 */
template <typename T>
std::enable_if_t<!isStringType<T>::value, void> printValue(std::istream &inStream, std::string_view prefix) {
	T var;
	inStream.read(reinterpret_cast<char *>(&var), sizeof(var));
	std::cout << prefix << var << std::endl;
}
/**
 * Read and print string value from given inStream at its current position.
 * Overloaded function that first reads int for string length and then reads string.
 *
 * @param inStream stream to be read from.
 * @param prefix string to be prefixed before the target value.
 */
template <typename T>
std::enable_if_t<isStringType<T>::value, void> printValue(std::istream &inStream, std::string_view prefix) {
	uint32_t stringSize;
	inStream.read(reinterpret_cast<char *>(&stringSize), sizeof(stringSize));
	char *chars = readChars(inStream, stringSize);
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
std::ofstream getOutStreamFromPath(std::string path, std::string_view extension);

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
void outputVectorToFile(std::ofstream &outFile, std::vector<T> const &vec, std::string_view name = "", bool endWithComma = true) {
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

template <typename T>
void outputToFile(std::ostream &outStream, void *offset, size_t stride, size_t count, std::string_view name = "", bool endWithComma = true) {
	if (!name.empty()) {
		outStream << "\"" << name << "\": [";
	} else {
		outStream << "[";
	}
	if (typeid(T) == typeid(uint8_t) || typeid(T) == typeid(int8_t)) {
		for (size_t i = 0; i < stride*count; i += stride) {
			outStream << +*(T *)((uint8_t *)offset+i);
			if (i+stride < stride*count) outStream << ", ";
		}
	} else {
		for (size_t i = 0; i < stride*count; i += stride) {
			outStream << *(T *)((uint8_t *)offset+i);
			if (i+stride < stride*count) outStream << ", ";
		}
	}

	outStream << "]";
	if (endWithComma) outStream << ", ";
	outStream << std::endl;
}

template <typename T>
void outputArrayToFile(std::ostream &outStream, void *offset, int elements, size_t interArrayStride, size_t stride, size_t count, std::string_view name = "", bool endWithComma = true) {
	if (!name.empty()) {
		outStream << "\"" << name << "\": [";
	} else {
		outStream << "[";
	}

	for (int i = 0; i < elements; i++) {
		if (i < elements-1) outputToFile<T>(outStream, (uint8_t *)offset+i*interArrayStride, stride, count);
		else outputToFile<T>(outStream, (uint8_t *)offset+i*interArrayStride, stride, count, "", false);
	}

	outStream << "]";
	if (endWithComma) outStream << ", ";
	outStream << std::endl;
}
