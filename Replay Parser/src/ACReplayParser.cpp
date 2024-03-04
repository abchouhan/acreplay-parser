#include "../include/UtilsIO.h"
#include "../include/ACReplayParser.h"
#include <cstdint>

std::vector<std::string> getDriverNames(std::ifstream &inFile) {
	int originalPos = inFile.tellg();
	std::vector<std::string> names;

	inFile.seekg(-31, std::ios_base::end);
	std::string str = readString(inFile, 23);

	if (str == "__AC_SHADERS_PATCH_v1__") {
		// Setup stream position to read .ini metadata
		int32_t extraDataStartOffset = readValue<int32_t>(inFile);
		if (readValue<int32_t>(inFile) == 1) {
			inFile.seekg(extraDataStartOffset, std::ios_base::beg);
			while (true) {
				int32_t len = readValue<int32_t>(inFile);
				if (len > 255) {
					break;
				}
				inFile.seekg(len, std::ios_base::cur);
			}
			inFile.seekg(-4, std::ios_base::cur);
			std::string ini = readValue<std::string>(inFile);

			// Find and loop through all driver name strings and add each to names vector
			std::string substring = "DRIVER_NAME=";
			size_t startIndex = ini.find(substring, 0);
			while (startIndex != std::string::npos) {
				startIndex += substring.length();
				size_t endIndex = ini.find("\n", startIndex);

				// Remove single-quotes from driver name string
				std::string name = ini.substr(startIndex, endIndex-startIndex);
				if (name[0] == '\'' && name[name.length()-1] == '\'') {
					names.push_back((name.substr(1, name.length()-2)));
				} else {
					names.push_back(name);
				}
				startIndex = ini.find(substring, startIndex+1);
			}
		}
	}
	inFile.seekg(originalPos, std::ios_base::beg);
	return names;
}

void readAndOutput(std::string inPath, std::string outPath, std::string targetDriverName) {
	std::ifstream inFile(inPath, std::ios::binary);

	if (!inFile) {
		std::cerr << "File \'" << inPath << "\' not found!" << std::endl;
		return;
	} else {
		std::cout << inPath << std::endl;
	}

	int32_t version = readValue<int32_t>(inFile);
	std::cout << "Version: " << version << std::endl;
	if (version != 16) {
		std::cerr << "Only version 16 .acreplay files are supported at this time." << std::endl;
		return;
	}

	double recordingIntervalMs = readValue<double>(inFile);
	std::cout << "Recording Interval: " << recordingIntervalMs << " ms" << std::endl;
	std::cout << "Recording Quality (FPS): " << 1000.0 / recordingIntervalMs << " Hz" << std::endl;

	printValue<std::string>(inFile, "Weather ID: ");
	printValue<std::string>(inFile, "Track ID: ");
	printValue<std::string>(inFile, "Track Config: ");

	int32_t numCars = readValue<int32_t>(inFile);
	std::cout << "Number of Cars: " << numCars << std::endl;
	inFile.seekg(4, std::ios_base::cur);

	// Print all driver names and track target driver's index in the file
	int targetIndex = -1;
	bool driverFound = false;
	std::cout << "Driver Names: " << std::endl;
	std::vector<std::string> names = getDriverNames(inFile);
	for (unsigned long i = 0; i < names.size(); i++) {
		if (targetDriverName == names[i]) {
			std::cout << "\t" << names[i] << "\t<< SELECTED" << std::endl;
			targetIndex = i;
			driverFound = true;
		} else {
			std::cout << "\t" << names[i] << std::endl;
		}
	}

	if (!driverFound && !targetDriverName.empty() && targetDriverName != "all") {
		std::cout << "Driver \"" << targetDriverName << "\" was not found!" << std::endl;
		return;
	}

	int32_t numFrames = readValue<int32_t>(inFile);
	std::cout << "Number of Frames: " << numFrames << std::endl;

	int32_t numTrackObjects = readValue<int32_t>(inFile);
	std::cout << "Number of Track Objects: " << numTrackObjects << std::endl;

	// Skip sun angles and track object data
	inFile.seekg((2 + 2 + 12 * numTrackObjects) * numFrames, std::ios_base::cur);

	for (int c = 0; c < numCars; c++) {
		// If targetIndex is set and has already been handled by the loop, then break
		if (targetIndex >= 0 && c > targetIndex) break;

		std::string carId				= readValue<std::string>(inFile);
		std::string driverName			= readValue<std::string>(inFile);
		std::string nationCode			= readValue<std::string>(inFile);
		std::string driverTeam			= readValue<std::string>(inFile);
		std::string carSkinId			= readValue<std::string>(inFile);
		int32_t frames					= readValue<int32_t>(inFile);
		int32_t bufferIncrementValue	= readValue<int32_t>(inFile);

		// If targetIndex is set but it is not the current iteration of the loop,
		// then setup inFile stream position to next driver
		if (c != targetIndex && targetIndex > -1) {
			inFile.seekg(20+(255+(21+bufferIncrementValue*4))*(frames-1)+(255+(5+bufferIncrementValue*4)), std::ios_base::cur);
			continue;
		}

		std::cout << "\nCar ID: " << carId << std::endl;
		std::cout << "Driver Name: " << driverName << std::endl;
		std::cout << "Nation Code: " << nationCode << std::endl;
		std::cout << "Driver Team: " << driverTeam << std::endl;
		std::cout << "Car Skin ID: " << carSkinId << std::endl;

		inFile.seekg(20, std::ios_base::cur);

		// Allocate space for variables for each frame
		std::vector<float> x(frames);						// X, Y (up), Z positions for vehicle body
		std::vector<float> y(frames);
		std::vector<float> z(frames);
		std::vector<std::float16_t> rotX(frames);			// X, Y, Z euler angle rotations for vehicle body in radians
		std::vector<std::float16_t> rotY(frames);
		std::vector<std::float16_t> rotZ(frames);
		// Wheel data are 2D vectors with indexes 0: front left wheel, 1: front right wheel, 2: rear left wheel, 3: rear right wheel
		std::vector<std::vector<float>> wheelX(4, std::vector<float> (frames));							// X, Y (up), Z positions for each wheel
		std::vector<std::vector<float>> wheelY(4, std::vector<float> (frames));
		std::vector<std::vector<float>> wheelZ(4, std::vector<float> (frames));
		std::vector<std::vector<std::float16_t>> wheelRotX(4, std::vector<std::float16_t> (frames));	// X, Y, Z euler angle rotations for each wheel in radians
		std::vector<std::vector<std::float16_t>> wheelRotY(4, std::vector<std::float16_t> (frames));
		std::vector<std::vector<std::float16_t>> wheelRotZ(4, std::vector<std::float16_t> (frames));

		// Modifies the wheel rotation along the X-axis for smooth movement
		std::vector<std::vector<std::float16_t>> wheelRotXModifier(4, std::vector<std::float16_t> (frames));

		std::vector<std::float16_t> speedX(frames);			// Speed along the X-axis in m/s
		std::vector<std::float16_t> speedZ(frames);			// Speed along the Z-axis in m/s
		std::vector<std::float16_t> rpm(frames);			// Engine RPM
		std::vector<std::float16_t> steering(frames);		// Steering wheel rotation in degrees

		std::vector<uint8_t> fuel(frames);					// Fuel amount from 0 to 255
		std::vector<uint8_t> gear(frames);					// 0: reverse, 1: neutral, 2: 1st gear, 3: 2nd gear, etc.
		std::vector<std::float16_t> damageFront(frames);	// Damage to the front of the vehicle
		std::vector<std::float16_t> damageRear(frames);		// Damage to the rear  of the vehicle
		std::vector<uint8_t> gas(frames);					// 0 (gas   pedal not pressed) to 255 (gas   pedal fully pressed)
		std::vector<uint8_t> brake(frames);					// 0 (brake pedal not pressed) to 255 (brake pedal fully pressed)
		std::vector<uint8_t> headlights(frames);			// 0: off, 1: on
		std::vector<uint8_t> boost(frames);					// Boost (turbo) amount from 0 to 255
		uint8_t temp;

		for (int i = 0; i < frames; i++) {
			x[i] =  readValue<float>(inFile);
			y[i] =  readValue<float>(inFile);
			z[i] = -readValue<float>(inFile);
			rotY[i] = -readValue<std::float16_t>(inFile);
			rotX[i] = -readValue<std::float16_t>(inFile);
			rotZ[i] =  readValue<std::float16_t>(inFile);

			inFile.seekg(2, std::ios_base::cur);
			inFile.seekg(48, std::ios_base::cur); // Skip brake disc positions

			// Read wheel data for four wheels
			for (int j = 0; j < 4; j++) {
				wheelRotY[j][i] = -readValue<std::float16_t>(inFile);
				inFile.seekg(2, std::ios_base::cur);
				wheelRotZ[j][i] =  readValue<std::float16_t>(inFile);
			}
			for (int j = 0; j < 4; j++) {
				wheelX[j][i] =  readValue<float>(inFile);
				wheelY[j][i] =  readValue<float>(inFile);
				wheelZ[j][i] = -readValue<float>(inFile);
			}
			for (int j = 0; j < 4; j++) {
				inFile.seekg(2, std::ios_base::cur);
				wheelRotX[j][i]			= -readValue<std::float16_t>(inFile);
				wheelRotXModifier[j][i] = -readValue<std::float16_t>(inFile);
			}
			speedZ[i] = -readValue<std::float16_t>(inFile);
			inFile.seekg(2, std::ios_base::cur);
			speedX[i] = -readValue<std::float16_t>(inFile);
			rpm[i] = readValue<std::float16_t>(inFile);
			inFile.seekg(4*10, std::ios_base::cur);
			steering[i] = -readValue<std::float16_t>(inFile);
			inFile.seekg(2+4*4, std::ios_base::cur);
			fuel[i] = readValue<uint8_t>(inFile);
			inFile.seekg(1, std::ios_base::cur);
			gear[i] = readValue<uint8_t>(inFile);
			inFile.seekg(5, std::ios_base::cur);
			damageRear[i]  = readValue<std::float16_t>(inFile);
			damageFront[i] = readValue<std::float16_t>(inFile);
			gas[i]	 = readValue<uint8_t>(inFile);
			brake[i] = readValue<uint8_t>(inFile);
			inFile.seekg(2, std::ios_base::cur);
			temp = readValue<uint8_t>(inFile);
			headlights[i] = (temp & 0x04) >> 2;
			inFile.seekg(5, std::ios_base::cur);
			boost[i] = readValue<uint8_t>(inFile);
			if (i < frames-1) {
				inFile.seekg(21+bufferIncrementValue*4, std::ios_base::cur);
			} else {
				inFile.seekg(5+bufferIncrementValue*4, std::ios_base::cur);
			}
		}

		std::stringstream out;
		out << outPath;
		// Add input filename to out if not specified
		if (outPath.empty() || outPath.find_last_of("/\\") == outPath.length()-1) {
			out << inPath.substr(0, inPath.find_last_of('.')).substr(inPath.find_last_of("/\\") + 1);
		}
		if (targetDriverName.empty()) out << "_" << driverName;
		out << ".json";

		std::ofstream outFile = getOutStreamFromPath(out.str(), ".json");

		outFile << "{" << std::endl;
		outFile << "\"numFrames\": " << frames << "," << std::endl;
		outFile << "\"recordingInterval\": " << recordingIntervalMs << "," << std::endl;
		outputVectorToFile(outFile, x, "x");
		outputVectorToFile(outFile, y, "y");
		outputVectorToFile(outFile, z, "z");
		outputVectorToFile(outFile, rotX, "rotX");
		outputVectorToFile(outFile, rotY, "rotY");
		outputVectorToFile(outFile, rotZ, "rotZ");
		outputVectorToFile(outFile, wheelX, "wheelX");
		outputVectorToFile(outFile, wheelY, "wheelY");
		outputVectorToFile(outFile, wheelZ, "wheelZ");
		outputVectorToFile(outFile, wheelRotX, "wheelRotX");
		outputVectorToFile(outFile, wheelRotY, "wheelRotY");
		outputVectorToFile(outFile, wheelRotZ, "wheelRotZ");
		outputVectorToFile(outFile, wheelRotXModifier, "wheelRotXModifier");
		outputVectorToFile(outFile, speedX, "speedX");
		outputVectorToFile(outFile, speedZ, "speedZ");
		outputVectorToFile(outFile, rpm, "rpm");
		outputVectorToFile(outFile, steering, "steering");
		outputVectorToFile(outFile, fuel, "fuel");
		outputVectorToFile(outFile, gear, "gear");
		outputVectorToFile(outFile, damageFront, "damageFront");
		outputVectorToFile(outFile, damageRear, "damageRear");
		outputVectorToFile(outFile, gas, "gas");
		outputVectorToFile(outFile, brake, "brake");
		outputVectorToFile(outFile, headlights, "headlights");
		outputVectorToFile(outFile, boost, "boost", false);
		outFile << "}" << std::endl;

		outFile.close();
		std::cout << "Done!" << std::endl;
	}
	inFile.close();
}
