#ifndef ACREPLAYPARSER_H
#define ACREPLAYPARSER_H

#include <iostream>
#include <cstdint>
#include <cstring>
#include <vector>
#include <stdfloat>

/**
 * Parses and outputs .acreplay files.
 */

/**
 * Get names of drivers present in the given .acreplay file.
 *
 * @param inFile file to be read from.
 * @return vector of names of drivers in the file.
 */
std::vector<std::string> getDriverNames(std::ifstream &inFile);

/**
 * TODO: Use existing JSON utility
 * Parse and ouput given .acreplay file into a .json file.
 *
 * @param inPath path to input file.
 * @param outPath path to output file.
 * @param targetDriverName name of driver whose vehicle data is to be ouputted.
 */
void readAndOutput(std::string inPath, std::string outPath = "", std::string targetDriverName = "");

#endif
