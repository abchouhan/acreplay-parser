#include <iostream>
#include <sstream>
#include <filesystem>
#include <charconv>
#include <cstddef>
#include <variant>
#include <vector>
#include <spanstream>
#include <iomanip>
#include <zlib.h>

#include "UtilsIO.hpp"
#include "ACReplayParser.hpp"

std::optional<uint32_t> getCSPDataOffset(std::ifstream &inFile) {
	std::streamoff originalPos = inFile.tellg();

	// Go to the end of the file, search for target footer string
	inFile.seekg(-static_cast<std::streamoff>(POSTFIX_STR.length())-8, std::ios_base::end);
	std::string str = readString(inFile, static_cast<uint32_t>(POSTFIX_STR.length()));

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

std::vector<std::string> getDriverNames(std::ifstream &inFile, uint32_t offset, std::vector<std::string>::size_type numDrivers) {
	std::streamoff originalPos = inFile.tellg();
	inFile.seekg(offset, std::ios_base::beg);

	std::vector<std::string> names(numDrivers);

	// Skip until .ini data located (string length > 255)
	while (true) {
		uint32_t len = readValue<uint32_t>(inFile);
		if (len > 255) { break; }
		inFile.seekg(len, std::ios_base::cur);
	}

	inFile.seekg(-4, std::ios_base::cur);
	std::string ini = readValue<std::string>(inFile);

	// Find and loop through all driver name strings and add each to names vector
	std::vector<std::string>::size_type index = 0;
	size_t startIndex = ini.find(DRIVER_NAME_INI_STR);
	while (startIndex != std::string::npos && index < numDrivers) {
		startIndex += DRIVER_NAME_INI_STR.length();
		size_t endIndex = ini.find('\n', startIndex);

		// Remove single-quotes from driver name string
		std::string name = ini.substr(startIndex, endIndex-startIndex);
		if (name[0] == '\'' && name[name.length()-1] == '\'') {
			names[index] = ((name.substr(1, name.length()-2)));
		} else {
			names[index] = name;
		}
		startIndex = ini.find(DRIVER_NAME_INI_STR, startIndex+1);
		index++;
	}

	inFile.seekg(originalPos, std::ios_base::beg);
	return names;
}

// TODO look into vformat_to for formatter
void outputCarFrame(std::ostream &outStream, CarFrame const &frame) {
	int originalPrecision = static_cast<int>(outStream.precision());
	outStream << std::setprecision(std::numeric_limits<float>::max_digits10) <<
			     frame.position.x << ',' << frame.position.y << ',' << frame.position.z << ','
			  << std::setprecision(std::numeric_limits<std::float16_t>::max_digits10) <<
			     frame.rotation.x << ',' << frame.rotation.y << ',' << frame.rotation.z << ',' <<
			     frame.velocity.x << ',' << frame.velocity.y << ',' << frame.velocity.z << ','
			  << std::setprecision(std::numeric_limits<float>::max_digits10) <<
			     frame.wheelStaticPosition[0].x << ',' << frame.wheelStaticPosition[0].y << ',' << frame.wheelStaticPosition[0].z << ',' <<
				 frame.wheelStaticPosition[1].x << ',' << frame.wheelStaticPosition[1].y << ',' << frame.wheelStaticPosition[1].z << ',' <<
				 frame.wheelStaticPosition[2].x << ',' << frame.wheelStaticPosition[2].y << ',' << frame.wheelStaticPosition[2].z << ',' <<
				 frame.wheelStaticPosition[3].x << ',' << frame.wheelStaticPosition[3].y << ',' << frame.wheelStaticPosition[3].z << ','
			  << std::setprecision(std::numeric_limits<std::float16_t>::max_digits10) <<
				 frame.wheelStaticRotation[0].x << ',' << frame.wheelStaticRotation[0].y << ',' << frame.wheelStaticRotation[0].z << ',' <<
				 frame.wheelStaticRotation[1].x << ',' << frame.wheelStaticRotation[1].y << ',' << frame.wheelStaticRotation[1].z << ',' <<
				 frame.wheelStaticRotation[2].x << ',' << frame.wheelStaticRotation[2].y << ',' << frame.wheelStaticRotation[2].z << ',' <<
				 frame.wheelStaticRotation[3].x << ',' << frame.wheelStaticRotation[3].y << ',' << frame.wheelStaticRotation[3].z << ','
			  << std::setprecision(std::numeric_limits<float>::max_digits10) <<
				 frame.wheelPosition[0].x << ',' << frame.wheelPosition[0].y << ',' << frame.wheelPosition[0].z << ',' <<
				 frame.wheelPosition[1].x << ',' << frame.wheelPosition[1].y << ',' << frame.wheelPosition[1].z << ',' <<
				 frame.wheelPosition[2].x << ',' << frame.wheelPosition[2].y << ',' << frame.wheelPosition[2].z << ',' <<
				 frame.wheelPosition[3].x << ',' << frame.wheelPosition[3].y << ',' << frame.wheelPosition[3].z << ','
			  << std::setprecision(std::numeric_limits<std::float16_t>::max_digits10) <<
				 frame.wheelRotation[0].x << ',' << frame.wheelRotation[0].y << ',' << frame.wheelRotation[0].z << ',' <<
				 frame.wheelRotation[1].x << ',' << frame.wheelRotation[1].y << ',' << frame.wheelRotation[1].z << ',' <<
				 frame.wheelRotation[2].x << ',' << frame.wheelRotation[2].y << ',' << frame.wheelRotation[2].z << ',' <<
				 frame.wheelRotation[3].x << ',' << frame.wheelRotation[3].y << ',' << frame.wheelRotation[3].z << ',' <<
				 frame.wheelAngularVelocity[0] << ',' << frame.wheelAngularVelocity[1] << ',' << frame.wheelAngularVelocity[2] << ',' << frame.wheelAngularVelocity[3] << ',' <<
				 frame.slipAngle[0] << ',' << frame.slipAngle[1] << ',' << frame.slipAngle[2] << ',' << frame.slipAngle[3] << ',' <<
				 frame.slipRatio[0] << ',' << frame.slipRatio[1] << ',' << frame.slipRatio[2] << ',' << frame.slipRatio[3] << ',' <<
				 frame.ndSlip[0] << ',' << frame.ndSlip[1] << ',' << frame.ndSlip[2] << ',' << frame.ndSlip[3] << ',' <<
				 frame.load[0] << ',' << frame.load[1] << ',' << frame.load[2] << ',' << frame.load[3] << ',' <<
				+frame.tireDirt[0] << ',' << +frame.tireDirt[1] << ',' << +frame.tireDirt[2] << ',' << +frame.tireDirt[3] << ',' <<
				 frame.steerAngle << ',' << frame.bodyworkNoise << ',' << frame.drivetrainSpeed << ',' <<
			    +frame.currentLap << ',' << frame.currentLapTime << ',' << frame.lastLapTime << ',' << frame.bestLapTime << ',' <<
				+frame.fuel << ',' << +frame.fuelPerLap << ',' << frame.rpm << ',' << +frame.gear << ',' <<
				+frame.gas << ',' << +frame.brake << ',' << +frame.boost << ',' <<
				+frame.damageFrontDeformation << ',' << +frame.damageFront << ',' << +frame.damageRear << ',' << +frame.damageLeft << ',' << +frame.damageRight << ','
			  << std::setprecision(originalPrecision);

	std::print(outStream, "{:s},{:s},{:d},{:d},{:s},{:d}",
				static_cast<bool>((frame.status >> 12) & 0x1), static_cast<bool>((frame.status >> 3) & 0x1), static_cast<uint8_t>((frame.status >> 4) & 0b0011),
				frame.engineHealth, static_cast<bool>((frame.status >> 9) & 0x1), frame.dirt);
}

void readAndOutput(std::string_view inPathStr, std::string_view preferredOutPathStr, std::string_view targetDriverName) {
	if (!std::filesystem::exists(inPathStr)) {
		std::println(stderr, "File \"{:s}\" not found!", inPathStr);
		return;
	}

	std::filesystem::path inPath(inPathStr);
	std::ifstream inFile(inPath, std::ios::binary);
	inFile.seekg(0, inFile.end);
	std::streamoff fileSize = inFile.tellg();
	inFile.seekg(0, inFile.beg);
	std::println("{:s}\n{:d} bytes", inPathStr, fileSize);

	uint32_t version = readValue<uint32_t>(inFile);
	std::println("Version: {:d}", version);
	if (version != 16) {
		std::puts("Only version 16 .acreplay files are supported at this time");
		inFile.close();
		return;
	}

	// Read file header
	Header header = {
		.version = version,
		.recordingInterval =	 readValue<double>(inFile),
		.weather =				 readValue<std::string>(inFile),
		.track =				 readValue<std::string>(inFile),
		.trackConfig =			 readValue<std::string>(inFile),
		.numCars =				 readValue<uint32_t>(inFile),
		.currentRecordingIndex = readValue<uint32_t>(inFile),
		.numFrames =			 readValue<uint32_t>(inFile),
		.numTrackObjects =		 readValue<uint32_t>(inFile),
	};

	std::println(
		"Recording Interval: {} ms\n"
		"Weather: {:s}\n"
		"Track: {:s}\n"
		"Track Config: {:s}\n"
		"Number of Cars: {:d}\n"
		"Number of Frames: {:d}",
		header.recordingInterval, header.weather, header.track,
		header.trackConfig, header.numCars, header.numFrames);

	std::optional<uint32_t> cspOffset = getCSPDataOffset(inFile);
	if (cspOffset.has_value()) {
		// Print all driver names
		bool driverFound = false;
		std::vector<std::string> names = getDriverNames(inFile, cspOffset.value(), header.numCars);
		std::puts("Driver Names:");
		for (size_t i = 0; i < names.size(); i++) {
			std::print("\t{:s}", names[i]);
			if (targetDriverName == names[i]) {
				std::puts("\t<< SELECTED");
				driverFound = true;
			} else std::println();
		}

		if (!driverFound && !targetDriverName.empty()) {
			std::println("Driver \"{:s}\" was not found!", targetDriverName);
			return;
		}
	}

	// Skip sun angles and track object data
	inFile.seekg((2+2+12*header.numTrackObjects)*header.numFrames, std::ios_base::cur);

	for (uint32_t carIndex = 0; carIndex < header.numCars; carIndex++) {
		if (inFile.tellg() > fileSize) {
			std::fputs("Attempted to read beyond file size!\n", stderr);
			break;
		}

		CarHeader carHeader = {
			.carID =	  readValue<std::string>(inFile),
			.driverName = readValue<std::string>(inFile),
			.nationCode = readValue<std::string>(inFile),
			.driverTeam = readValue<std::string>(inFile),
			.carSkinID =  readValue<std::string>(inFile),
			.numFrames =  readValue<uint32_t>(inFile),
			.numWings =	  readValue<uint32_t>(inFile)
		};

		// If targetIndex is set but it is not the current iteration of the loop,
		// then setup inFile stream position to next driver
		if (!targetDriverName.empty() && targetDriverName != carHeader.driverName) {
			inFile.seekg(static_cast<std::streamoff>(20+(sizeof(CarFrame)+(20+carHeader.numWings*4))*(carHeader.numFrames-1) +
							 sizeof(CarFrame)+carHeader.numWings*4), std::ios_base::cur);
			uint32_t count = readValue<uint32_t>(inFile);
			if (count > 0) {
				inFile.seekg(count*8, std::ios_base::cur);
			}
			continue;
		}

		std::println(
			"\nCar ID: {:s}\n"
			"Driver Name: {:s}\n"
			"Nation Code: {:s}\n"
			"Driver Team: {:s}\n"
			"Car Skin ID: {:s}\n"
			"Number of Frames: {:d}\n"
			"Number of Wings: {:d}",
			carHeader.carID, carHeader.driverName, carHeader.nationCode, carHeader.driverTeam,
			carHeader.carSkinID, carHeader.numFrames, carHeader.numWings);

		inFile.seekg(20, std::ios_base::cur);

		std::vector<CarFrame> frames(carHeader.numFrames);
		for (size_t i = 0; i < static_cast<size_t>(carHeader.numFrames); i++) {
			frames[i] = readValue<CarFrame>(inFile);
			if (i < carHeader.numFrames-1) {
				inFile.seekg(20+carHeader.numWings*4, std::ios_base::cur);
			} else {
				inFile.seekg(carHeader.numWings*4, std::ios_base::cur);
				uint32_t count = readValue<uint32_t>(inFile);
				if (count > 0) {
					std::println("Extra trailing bytes: {:d}", count);
					inFile.seekg(count*8, std::ios_base::cur);
				}
			}
		}

		std::filesystem::path outPath(preferredOutPathStr);
		// Add input filename to outPath if not specified
		if (!outPath.has_filename()) {
			if (targetDriverName.empty() && header.numCars > 1) {
				outPath.replace_filename(inPath.stem().concat("_"+carHeader.driverName+"."+EXTENSION));
			} else outPath.replace_filename(inPath.stem().concat("."+EXTENSION));
			getUniquePath(outPath);
		} else {
			bool hasExtension = outPath.has_extension();
			if (targetDriverName.empty() && header.numCars > 1) {
				outPath.replace_filename(outPath.stem().concat("_"+carHeader.driverName+outPath.extension().string()));
			}
			if (!hasExtension) outPath.concat("."+EXTENSION);
			if (std::filesystem::exists(outPath)) {
				std::println("\nFile \"{:s}\" will be overwritten\n", outPath.string());
			}
		}

		std::ofstream outFile(outPath);
		outFile << "# numFrames " << carHeader.numFrames << "\n# recordingInterval " << header.recordingInterval <<
			'\n' << CarFrame::label;

		bool framesOutputted = false;

		// Read CSP extra car data
		if (cspOffset.has_value()) {
			std::streamoff originalPos = inFile.tellg();
			inFile.seekg(cspOffset.value(), std::ios_base::beg);

			int extraVersion = -1;
			uint32_t bytesPerFrame = 0;
			// Skip until extra car data located
			while (true) {
				uint32_t len = readValue<uint32_t>(inFile);
				std::streamoff resetPos = inFile.tellg();
				if (readString(inFile, static_cast<uint32_t>(EXT_PERCAR_STR.length())) == EXT_PERCAR_STR) {
					inFile.seekg(static_cast<std::streamoff>(-EXT_PERCAR_STR.length()), std::ios_base::cur);
					std::string tag = readString(inFile, len);
					size_t versionIndex = tag.find("_v")+2;
					size_t separatorIndex = tag.find(':');

					uint32_t extraCarIndex = 0;
					std::from_chars_result result1 = std::from_chars(tag.data()+versionIndex, tag.data()+separatorIndex, extraVersion);
					std::from_chars_result result2 = std::from_chars(tag.data()+separatorIndex+1, tag.data()+len, extraCarIndex);

					if (result1.ec == std::errc::invalid_argument || result2.ec == std::errc::invalid_argument) {
						std::println(stderr, "Malformed data encountered at offset {:x}", static_cast<size_t>(inFile.tellg()));
						break;
					}

					if (extraVersion > 0 && static_cast<size_t>(extraVersion) <= EXT_PERCAR_BYTES_PER_FRAME.size()) {
						bytesPerFrame = EXT_PERCAR_BYTES_PER_FRAME[static_cast<size_t>(extraVersion)-1];
					}
					if (carIndex == extraCarIndex) {
						if (bytesPerFrame > 0)   std::println("EXT_PERCAR version: {:d}", extraVersion);
						else std::println(stderr, "Unsupported EXT_PERCAR version: {:d}", extraVersion);
						break;
					}
				}
				inFile.seekg(resetPos+len, std::ios_base::beg);
			}

			// If it exists, read and output extra data
			if (extraVersion >= 0 && extraVersion <= EXT_PERCAR_VERSION_COUNT && bytesPerFrame > 0) {
				uint32_t compressedSize = readValue<uint32_t>(inFile);
				std::vector<uint8_t> compressedData(compressedSize);
				readValueArray(inFile, compressedSize, compressedData.data());

				unsigned long uncompressedSize = static_cast<unsigned long>(bytesPerFrame*header.numFrames);
				std::vector<uint8_t> uncompressedData(uncompressedSize);
				int status = uncompress(uncompressedData.data(), &uncompressedSize, compressedData.data(), compressedSize);
				if (status != Z_OK) std::println(stderr, "Decompression failed with error code {:d}", status);
				else {
					// Read uncompressed data as a stream without copying
					std::ispanstream inStreamPerCar(
						std::span<char>(reinterpret_cast<char *>(uncompressedData.data()), uncompressedSize),
						std::ios::binary);

					std::variant<CarFrameExtra_v6, CarFrameExtra_v7> extraFramesVariant{};
					switch (extraVersion) {
						default: break;
						case 6: extraFramesVariant.emplace<CarFrameExtra_v6>(); break;
						case 7: extraFramesVariant.emplace<CarFrameExtra_v7>(); break;
					}
					std::visit([&](auto const &extraFrame) {
						using T = std::decay_t<decltype(extraFrame)>;
						framesOutputted = true;
						outFile << ',' << extraFrame.label << '\n';
						std::vector<T> extraFrames(carHeader.numFrames);
						readValueArray(inStreamPerCar, carHeader.numFrames, extraFrames.data());
						for (uint32_t i = 0; i < carHeader.numFrames; i++) {
							outFile << i << ',';
							outputCarFrame(outFile, frames[i]);
							outFile << ',';
							extraFrames[i].outputData(outFile);
							outFile << '\n';
						}
					}, extraFramesVariant);
				}
			}
			inFile.seekg(originalPos, std::ios_base::beg);
		}

		if (!framesOutputted) {
			outFile << '\n';
			for (uint32_t i = 0; i < carHeader.numFrames; i++) {
				outFile << i << ',';
				outputCarFrame(outFile, frames[i]);
				outFile << '\n';
			}
		}
		outFile.close();
		std::println("{:s}\nDone!", outPath.string());
	}
	inFile.close();
}
