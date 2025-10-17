#include <iostream>
#include <spanstream>
#include <sstream>
#include <zlib.h>

#include "../include/UtilsIO.hpp"
#include "../include/ACReplayParser.hpp"

std::optional<uint32_t> getCSPDataOffset(std::ifstream &inFile) {
	size_t originalPos = inFile.tellg();

	// Go to the end of the file, search for target footer string
	inFile.seekg(-POSTFIX_STR.length()-8, std::ios_base::end);
	std::string str = readString(inFile, POSTFIX_STR.length());

	if (str == POSTFIX_STR) {
		uint32_t offset = readValue<uint32_t>(inFile);
		if (readValue<uint32_t>(inFile) == 1) { // Version 1
			inFile.seekg(originalPos, std::ios_base::beg);
			return offset;
		}
	}
	inFile.seekg(originalPos, std::ios_base::beg);
	return {};
}

std::vector<std::string> getDriverNames(std::ifstream &inFile, uint32_t offset, int numDrivers) {
	size_t originalPos = inFile.tellg();
	inFile.seekg(offset, std::ios_base::beg);

	std::vector<std::string> names;
	names.reserve(numDrivers);

	// Skip until .ini data located (string length > 255)
	while (true) {
		uint32_t len = readValue<uint32_t>(inFile);
		if (len > 255) { break; }
		inFile.seekg(len, std::ios_base::cur);
	}

	inFile.seekg(-4, std::ios_base::cur);
	std::string ini = readValue<std::string>(inFile);

	// Find and loop through all driver name strings and add each to names vector
	int index = 0;
	size_t startIndex = ini.find(DRIVER_NAME_INI_STR);
	while (startIndex != std::string::npos && index < numDrivers) {
		startIndex += DRIVER_NAME_INI_STR.length();
		size_t endIndex = ini.find("\n", startIndex);

		// Remove single-quotes from driver name string
		std::string name = ini.substr(startIndex, endIndex-startIndex);
		if (name[0] == '\'' && name[name.length()-1] == '\'') {
			names.push_back((name.substr(1, name.length()-2)));
		} else {
			names.push_back(name);
		}
		startIndex = ini.find(DRIVER_NAME_INI_STR, startIndex+1);
		index++;
	}

	inFile.seekg(originalPos, std::ios_base::beg);
	return names;
}

// TODO: Not ideal to use addresses to iterate over the frames
void outputCarFrames(std::ostream &outStream, CarFrame *frames, uint32_t numFrames) {
	unsigned int stride = sizeof(CarFrame);

	outputToFile<float>(outStream, &(frames[0].position.x), stride, numFrames, "x");
	outputToFile<float>(outStream, &(frames[0].position.y), stride, numFrames, "y");
	outputToFile<float>(outStream, &(frames[0].position.z), stride, numFrames, "z");
	outputToFile<std::float16_t>(outStream, &(frames[0].rotation.x), stride, numFrames, "rotX");
	outputToFile<std::float16_t>(outStream, &(frames[0].rotation.y), stride, numFrames, "rotY");
	outputToFile<std::float16_t>(outStream, &(frames[0].rotation.z), stride, numFrames, "rotZ");

	unsigned int interArrayStride = (std::ptrdiff_t)&(frames[0].wheelStaticPosition[1].x)-(std::ptrdiff_t)&(frames[0].wheelStaticPosition[0].x);
	outputArrayToFile<float>(outStream, &(frames[0].wheelStaticPosition[0].x), 4, interArrayStride, stride, numFrames, "wheelStaticX");

	interArrayStride = (std::ptrdiff_t)&(frames[0].wheelStaticPosition[1].y)-(std::ptrdiff_t)&(frames[0].wheelStaticPosition[0].y);
	outputArrayToFile<float>(outStream, &(frames[0].wheelStaticPosition[0].y), 4, interArrayStride, stride, numFrames, "wheelStaticY");

	interArrayStride = (std::ptrdiff_t)&(frames[0].wheelStaticPosition[1].z)-(std::ptrdiff_t)&(frames[0].wheelStaticPosition[0].z);
	outputArrayToFile<float>(outStream, &(frames[0].wheelStaticPosition[0].z), 4, interArrayStride, stride, numFrames, "wheelStaticZ");

	interArrayStride = (std::ptrdiff_t)&(frames[0].wheelStaticRotation[1].x)-(std::ptrdiff_t)&(frames[0].wheelStaticRotation[0].x);
	outputArrayToFile<std::float16_t>(outStream, &(frames[0].wheelStaticRotation[0].x), 4, interArrayStride, stride, numFrames, "wheelStaticRotX");

	interArrayStride = (std::ptrdiff_t)&(frames[0].wheelStaticRotation[1].y)-(std::ptrdiff_t)&(frames[0].wheelStaticRotation[0].y);
	outputArrayToFile<std::float16_t>(outStream, &(frames[0].wheelStaticRotation[0].y), 4, interArrayStride, stride, numFrames, "wheelStaticRotY");

	interArrayStride = (std::ptrdiff_t)&(frames[0].wheelStaticRotation[1].z)-(std::ptrdiff_t)&(frames[0].wheelStaticRotation[0].z);
	outputArrayToFile<std::float16_t>(outStream, &(frames[0].wheelStaticRotation[0].z), 4, interArrayStride, stride, numFrames, "wheelStaticRotZ");

	interArrayStride = (std::ptrdiff_t)&(frames[0].wheelPosition[1].x)-(std::ptrdiff_t)&(frames[0].wheelPosition[0].x);
	outputArrayToFile<float>(outStream, &(frames[0].wheelPosition[0].x), 4, interArrayStride, stride, numFrames, "wheelX");

	interArrayStride = (std::ptrdiff_t)&(frames[0].wheelPosition[1].y)-(std::ptrdiff_t)&(frames[0].wheelPosition[0].y);
	outputArrayToFile<float>(outStream, &(frames[0].wheelPosition[0].y), 4, interArrayStride, stride, numFrames, "wheelY");

	interArrayStride = (std::ptrdiff_t)&(frames[0].wheelPosition[1].z)-(std::ptrdiff_t)&(frames[0].wheelPosition[0].z);
	outputArrayToFile<float>(outStream, &(frames[0].wheelPosition[0].z), 4, interArrayStride, stride, numFrames, "wheelZ");

	interArrayStride = (std::ptrdiff_t)&(frames[0].wheelRotation[1].x)-(std::ptrdiff_t)&(frames[0].wheelRotation[0].x);
	outputArrayToFile<std::float16_t>(outStream, &(frames[0].wheelRotation[0].x), 4, interArrayStride, stride, numFrames, "wheelRotX");

	interArrayStride = (std::ptrdiff_t)&(frames[0].wheelRotation[1].y)-(std::ptrdiff_t)&(frames[0].wheelRotation[0].y);
	outputArrayToFile<std::float16_t>(outStream, &(frames[0].wheelRotation[0].y), 4, interArrayStride, stride, numFrames, "wheelRotY");

	interArrayStride = (std::ptrdiff_t)&(frames[0].wheelRotation[1].z)-(std::ptrdiff_t)&(frames[0].wheelRotation[0].z);
	outputArrayToFile<std::float16_t>(outStream, &(frames[0].wheelRotation[0].z), 4, interArrayStride, stride, numFrames, "wheelRotZ");

	outputToFile<std::float16_t>(outStream, &(frames[0].velocity.x), stride, numFrames, "velocityX");
	outputToFile<std::float16_t>(outStream, &(frames[0].velocity.y), stride, numFrames, "velocityY");
	outputToFile<std::float16_t>(outStream, &(frames[0].velocity.z), stride, numFrames, "velocityZ");

	outputToFile<std::float16_t>(outStream, &(frames[0].rpm), stride, numFrames, "rpm");

	interArrayStride = (std::ptrdiff_t)&(frames[0].wheelAngularVelocity[1])-(std::ptrdiff_t)&(frames[0].wheelAngularVelocity[0]);
	outputArrayToFile<std::float16_t>(outStream, &(frames[0].wheelAngularVelocity[0]), 4, interArrayStride, stride, numFrames, "wheelAngularVelocity");
	interArrayStride = (std::ptrdiff_t)&(frames[0].slipAngle[1])-(std::ptrdiff_t)&(frames[0].slipAngle[0]);
	outputArrayToFile<std::float16_t>(outStream, &(frames[0].slipAngle[0]), 4, interArrayStride, stride, numFrames, "slipAngle");
	interArrayStride = (std::ptrdiff_t)&(frames[0].slipRatio[1])-(std::ptrdiff_t)&(frames[0].slipRatio[0]);
	outputArrayToFile<std::float16_t>(outStream, &(frames[0].slipRatio[0]), 4, interArrayStride, stride, numFrames, "slipRatio");
	interArrayStride = (std::ptrdiff_t)&(frames[0].ndSlip[1])-(std::ptrdiff_t)&(frames[0].ndSlip[0]);
	outputArrayToFile<std::float16_t>(outStream, &(frames[0].ndSlip[0]), 4, interArrayStride, stride, numFrames, "ndSlip");
	interArrayStride = (std::ptrdiff_t)&(frames[0].load[1])-(std::ptrdiff_t)&(frames[0].load[0]);
	outputArrayToFile<std::float16_t>(outStream, &(frames[0].load[0]), 4, interArrayStride, stride, numFrames, "load");

	outputToFile<std::float16_t>(outStream, &(frames[0].steerAngle), stride, numFrames, "steerAngle");
	outputToFile<std::float16_t>(outStream, &(frames[0].bodyworkNoise), stride, numFrames, "bodyworkNoise");
	outputToFile<std::float16_t>(outStream, &(frames[0].drivetrainSpeed), stride, numFrames, "drivetrainSpeed");
	outputToFile<uint32_t>(outStream, &(frames[0].currentLapTime), stride, numFrames, "currentLapTime");
	outputToFile<uint32_t>(outStream, &(frames[0].lastLapTime), stride, numFrames, "lastLapTime");
	outputToFile<uint32_t>(outStream, &(frames[0].bestLapTime), stride, numFrames, "bestLapTime");
	outputToFile<uint8_t>(outStream, &(frames[0].fuel), stride, numFrames, "fuel");
	outputToFile<uint8_t>(outStream, &(frames[0].fuelPerLap), stride, numFrames, "fuelPerLap");
	outputToFile<uint8_t>(outStream, &(frames[0].gear), stride, numFrames, "gear");

	interArrayStride = (std::ptrdiff_t)&(frames[0].tireDirt[1])-(std::ptrdiff_t)&(frames[0].tireDirt[0]);
	outputArrayToFile<uint8_t>(outStream, &(frames[0].tireDirt[0]), 4, interArrayStride, stride, numFrames, "tireDirt");

	outputToFile<uint8_t>(outStream, &(frames[0].damageFrontDeformation), stride, numFrames, "damageFrontDeformation");
	outputToFile<uint8_t>(outStream, &(frames[0].damageRear), stride, numFrames, "damageRear");
	outputToFile<uint8_t>(outStream, &(frames[0].damageLeft), stride, numFrames, "damageLeft");
	outputToFile<uint8_t>(outStream, &(frames[0].damageRight), stride, numFrames, "damageRight");
	outputToFile<uint8_t>(outStream, &(frames[0].damageFront), stride, numFrames, "damageFront");
	outputToFile<uint8_t>(outStream, &(frames[0].gas), stride, numFrames, "gas");
	outputToFile<uint8_t>(outStream, &(frames[0].brake), stride, numFrames, "brake");
	outputToFile<uint8_t>(outStream, &(frames[0].currentLap), stride, numFrames, "currentLap");

	outStream << "\"horn\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 3) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"cameraDir\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << +(uint8_t)((frames[i].status >> 4) & 0b0011);
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"gearboxBeingDamaged\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 9) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"lights\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 12) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n";

	outputToFile<uint8_t>(outStream, &(frames[0].dirt), stride, numFrames, "dirt");
	outputToFile<uint8_t>(outStream, &(frames[0].engineHealth), stride, numFrames, "engineHealth");
	outputToFile<uint8_t>(outStream, &(frames[0].boost), stride, numFrames, "boost", false);
}
void outputExtraCarFrames_v6(std::ostream &outStream, CarFrameExtra_v6 *frames, uint32_t numFrames) {
	unsigned int stride = sizeof(CarFrameExtra_v6);

	outputToFile<uint8_t>(outStream, &(frames[0].wipers), stride, numFrames, "wipers");
	outStream << "\"turnSignals\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << +(uint8_t)(frames[i].status & 0b0111);
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"lowBeams\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 3) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"extraOptionA\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 4) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"extraOptionB\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 5) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"extraOptionC\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 6) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"extraOptionD\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 7) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"extraOptionE\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 10) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"extraOptionF\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 11) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"extraOptionG\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 12) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"extraOptionH\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 13) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"extraOptionI\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 14) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"extraOptionJ\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 15) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n";
	outputToFile<uint8_t>(outStream, &(frames[0].handbrake), stride, numFrames, "handbrake");
	outputToFile<uint8_t>(outStream, &(frames[0].clutch), stride, numFrames, "clutch", false);
}
void outputExtraCarFrames_v7(std::ostream &outStream, CarFrameExtra_v7 *frames, uint32_t numFrames) {
	// Need to compute size of CarFrame manually due to use of bit-fields
	unsigned int stride = (std::ptrdiff_t)&(frames[1])-(std::ptrdiff_t)&(frames[0]);

	outputToFile<uint8_t>(outStream, &(frames[0].wipers), stride, numFrames, "wipers");
	outStream << "\"turnSignals\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << +(uint8_t)(frames[i].status & 0b0111);
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"lowBeams\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 3) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"extraOptionA\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 4) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"extraOptionB\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 5) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"extraOptionC\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 6) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"extraOptionD\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 7) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"extraOptionE\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 10) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"extraOptionF\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 11) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"extraOptionG\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 12) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"extraOptionH\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 13) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"extraOptionI\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 14) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n\"extraOptionJ\": [";
	for (int i = 0; i < numFrames; i++) {
		outStream << (((frames[i].status >> 15) & 0x1) ? "true" : "false");
		if (i < numFrames-1) outStream << ", ";
	}
	outStream << "],\n";
	outputToFile<uint8_t>(outStream, &(frames[0].handbrake), stride, numFrames, "handbrake");
	outputToFile<uint8_t>(outStream, &(frames[0].clutch), stride, numFrames, "clutch", false);
}

void readAndOutput(std::string const inPath, std::string_view const outPath, std::string_view const targetDriverName) {
	std::ifstream inFile(inPath, std::ios::binary);

	if (!inFile) {
		std::cerr << "File \'" << inPath << "\' not found!" << std::endl;
		return;
	} else {
		std::cout << inPath << std::endl;
	}

	uint32_t version = readValue<uint32_t>(inFile);
	std::cout << "Version: " << version << std::endl;
	if (version != 16) {
		std::cerr << "Only version 16 .acreplay files are supported at this time" << std::endl;
		return;
	}

	// Read file header
	Header header = {
		.version = version,
		.recordingInterval =		readValue<double>(inFile),
		.weather =					readValue<std::string>(inFile),
		.track =					readValue<std::string>(inFile),
		.trackConfig =				readValue<std::string>(inFile),
		.numCars =					readValue<uint32_t>(inFile),
		.currentRecordingIndex =	readValue<uint32_t>(inFile),
		.numFrames =				readValue<uint32_t>(inFile),
		.numTrackObjects =			readValue<uint32_t>(inFile),
	};

	std::cout << "Recording Interval: " << header.recordingInterval << " ms" << std::endl;
	std::cout << "Weather: " << header.weather << std::endl;
	std::cout << "Track: " << header.track << std::endl;
	std::cout << "Track Config: " << header.trackConfig << std::endl;
	std::cout << "Number of Cars: " << header.numCars << std::endl;
	std::cout << "Number of Frames: " << header.numFrames << std::endl;

	std::optional<uint32_t> cspOffset = getCSPDataOffset(inFile);
	if (cspOffset.has_value()) {
		// Print all driver names
		bool driverFound = false;
		std::cout << "Driver Names: " << std::endl;
		std::vector<std::string> names = getDriverNames(inFile, cspOffset.value(), header.numCars);
		for (size_t i = 0; i < names.size(); i++) {
			if (targetDriverName == names[i]) {
				std::cout << "\t" << names[i] << "\t<< SELECTED" << std::endl;
				driverFound = true;
			} else {
				std::cout << "\t" << names[i] << std::endl;
			}
		}

		if (!driverFound && !targetDriverName.empty()) {
			std::cout << "Driver \"" << targetDriverName << "\" was not found!" << std::endl;
			return;
		}
	}

	// Skip sun angles and track object data
	inFile.seekg((2 + 2 + 12 * header.numTrackObjects) * header.numFrames, std::ios_base::cur);

	for (int c = 0; c < header.numCars; c++) {
		CarHeader carHeader = {
			.carID =		readValue<std::string>(inFile),
			.driverName =	readValue<std::string>(inFile),
			.nationCode =	readValue<std::string>(inFile),
			.driverTeam =	readValue<std::string>(inFile),
			.carSkinID =	readValue<std::string>(inFile),
			.numFrames =	readValue<uint32_t>(inFile),
			.numWings =		readValue<uint32_t>(inFile)
		};

		// If targetIndex is set but it is not the current iteration of the loop,
		// then setup inFile stream position to next driver
		if (!targetDriverName.empty() && targetDriverName != carHeader.driverName) {
			inFile.seekg(20+(255+(21+carHeader.numWings*4))*(carHeader.numFrames-1)
				+ (255+(5+carHeader.numWings*4)), std::ios_base::cur);
			continue;
		}

		std::cout << "\nCar ID: " << carHeader.carID << std::endl;
		std::cout << "Driver Name: " << carHeader.driverName << std::endl;
		std::cout << "Nation Code: " << carHeader.nationCode << std::endl;
		std::cout << "Driver Team: " << carHeader.driverTeam << std::endl;
		std::cout << "Car Skin ID: " << carHeader.carSkinID << std::endl;

		inFile.seekg(20, std::ios_base::cur);

		CarFrame *frames = new CarFrame[carHeader.numFrames];
		for (int i = 0; i < carHeader.numFrames; i++) {
			CarFrame frame = readValue<CarFrame>(inFile);
			frames[i] = frame;
			if (i < carHeader.numFrames-1) {
				inFile.seekg(20+carHeader.numWings*4, std::ios_base::cur);
			} else {
				inFile.seekg(4+carHeader.numWings*4, std::ios_base::cur);
			}
		}

		std::stringstream out;
		out << outPath;
		// Add input filename to out if not specified
		if (outPath.empty() || outPath.find_last_of("/\\") == outPath.length()-1) {
			out << inPath.substr(0, inPath.find_last_of('.')).substr(inPath.find_last_of("/\\") + 1);
		}
		if (targetDriverName.empty()) out << "_" << carHeader.driverName;
		out << ".json";

		std::ofstream outFile = getOutStreamFromPath(out.str(), ".json");
		outFile << "{" << std::endl;
		outFile << "\"numFrames\": " << carHeader.numFrames << "," << std::endl;
		outFile << "\"recordingInterval\": " << header.recordingInterval << "," << std::endl;
		outputCarFrames(outFile, frames, carHeader.numFrames);
		delete[] frames;

		// Read CSP extra car data
		if (cspOffset.has_value()) {
			size_t originalPos = inFile.tellg();
			inFile.seekg(cspOffset.value(), std::ios_base::beg);

			int version = -1;
			uint32_t bytesPerFrame = 0;
			// Skip until extra car data located
			while (true) {
				uint32_t len = readValue<uint32_t>(inFile);
				size_t resetPos = inFile.tellg();
				if (readString(inFile, EXT_PERCAR_STR.length()) == EXT_PERCAR_STR) {
					inFile.seekg(-EXT_PERCAR_STR.length(), std::ios_base::cur);
					std::string tag = readString(inFile, len);
					int versionIndex = tag.find("_v")+2;
					int separatorIndex = tag.find(":");

					std::string versionStr = tag.substr(versionIndex, separatorIndex-versionIndex);
					std::string carIndexStr = tag.substr(separatorIndex+1, len-separatorIndex-1);
					try {
						version = std::stoi(versionStr);
						int carIndex = std::stoi(carIndexStr);
						if (version > 0 && version <= EXT_PERCAR_BYTES_PER_FRAME.size()) {
							bytesPerFrame = EXT_PERCAR_BYTES_PER_FRAME[version-1];
						}
						if (c == carIndex) {
							if (bytesPerFrame == 0) {
								std::cerr << "Unsupported EXT_PERCAR version: " << version << std::endl;
							}
							break;
						}
					} catch (...) {
						std::cerr << "Malformed data encountered at offset " <<
							std::hex << inFile.tellg() << std::dec <<
						std::endl;
						break;
					}
				}
				inFile.seekg(resetPos+len, std::ios_base::beg);
			}

			// If it exists, read and output extra data
			if (version >= 0 && version <= EXT_PERCAR_VERSION_COUNT && bytesPerFrame > 0) {
				uint32_t compressedSize = readValue<uint32_t>(inFile);
				uint8_t *compressedData = new uint8_t[compressedSize];
				readValueArray(inFile, compressedSize, compressedData);

				unsigned long uncompressedSize = bytesPerFrame*header.numFrames;
				uint8_t *uncompressedData = new uint8_t[uncompressedSize];
				int status = uncompress(uncompressedData, &uncompressedSize, compressedData, compressedSize);
				if (status != Z_OK) {
					std::cerr << "Decompression failed with error code " << status << std::endl;
				}

				// Read uncompressed data as a stream without copying
				std::ispanstream inStreamPerCar(
					std::span<char>(reinterpret_cast<char *>(uncompressedData), uncompressedSize),
					std::ios::binary);

				switch (version) {
					default: break;
					case 6: {
						CarFrameExtra_v6 *extraFrames = new CarFrameExtra_v6[carHeader.numFrames];
						readValueArray(inStreamPerCar, carHeader.numFrames, extraFrames);
						outFile << ", ";
						outputExtraCarFrames_v6(outFile, extraFrames, carHeader.numFrames);
						delete[] extraFrames;
						break;
					}
					case 7: {
						CarFrameExtra_v7 *extraFrames = new CarFrameExtra_v7[carHeader.numFrames];
						readValueArray(inStreamPerCar, carHeader.numFrames, extraFrames);
						outFile << ", ";
						outputExtraCarFrames_v7(outFile, extraFrames, carHeader.numFrames);
						delete[] extraFrames;
						break;
					}
				}
				delete[] uncompressedData;
				delete[] compressedData;
			}
			inFile.seekg(originalPos, std::ios_base::beg);
		}
		outFile << "}" << std::endl;
		outFile.close();
		std::cout << "Done!" << std::endl;
	}
	inFile.close();
}
