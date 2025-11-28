#pragma once

#include <cstdint>
#include <fstream>
#include <filesystem>

/**
 * Utility functions for common IO operations.
 */

/**
 * Read and return char * with given length (size) from given stream at its current position.
 * Modifies stream position.
 *
 * @param inStream stream to be read from.
 * @param size length of char * to be read.
 * @return heap-allocated string of chars that was read from inStream.
 */
char *readChars(std::istream &inStream, uint32_t size);
/**
 * Read and return string with given length (size) from given stream at its current position.
 * Modifies stream position.
 *
 * @param inStream stream to be read from.
 * @param size length of string to be read.
 * @return string that was read from inStream.
 */
std::string readString(std::istream &inStream, uint32_t size);

/**
 * Read and output array of type T from given stream at its current position.
 * Modifies stream position.
 *
 * @param inStream stream to be read from.
 * @param count array size; number of Ts to be read.
 * @param out pointer to array of Ts that is to be written to.
 */
template <typename T>
void readValueArray(std::istream &inStream, uint32_t count, T *const out) {
	inStream.read(reinterpret_cast<char *>(out), count*sizeof(T));
}
/**
 * Read and return value of type T from given stream at its current position.
 * Modifies stream position.
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
 * Specialized template function that first reads length integer and then reads char * with that length.
 *
 * @param inStream stream to be read from.
 * @return char * value that was read from inStream.
 */
template <>
char *readValue<char *>(std::istream &inStream);
/**
 * Read and return string value from given stream at its current position.
 * Specialized template function that first reads length integer and then reads string with that length.
 *
 * @param inStream stream to be read from.
 * @return string value that was read from inStream.
 */
template <>
std::string readValue<std::string>(std::istream &inStream);

/**
 * Modify the given file path to be unique;
 * if the given file already exists, append " (n)" to the filename.
 *
 * @param path path to target file.
 */
void getUniquePath(std::filesystem::path &path);
