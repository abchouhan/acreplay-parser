#pragma once

#include "UtilsIO.hpp"
#include "UtilsData.hpp"

#include <iostream>
#include <spanstream>
#include <vector>
#include <cstdint>
#include <stdfloat>
#include <optional>
#include <zlib.h>

/**
 * Parses and outputs .acreplay files.
 */

// String present at the end of CSP .acreplay file
std::string const POSTFIX_STR = "__AC_SHADERS_PATCH_v1__";
// String present in .acreplay CSP data
std::string const DRIVER_NAME_INI_STR = "DRIVER_NAME=";

// String present in .acreplay CSP data
std::string const EXT_PERCAR_STR = "EXT_PERCAR";
int const EXT_PERCAR_VERSION_COUNT = 7;
// Number of bytes in one frame of extra car data, given its version
// A value of 0 means it is currently unknown
std::array<uint32_t, EXT_PERCAR_VERSION_COUNT> const EXT_PERCAR_BYTES_PER_FRAME = {
	/* Version 1 */ 0,
	/* Version 2 */ 0,
	/* Version 3 */ 0,
	/* Version 4 */ 0,
	/* Version 5 */ 0,//104,
	/* Version 6 */ 108,
	/* Version 7 */ 108
};

// Header of .acreplay file
struct Header {
	uint32_t version;
	double recordingInterval;
	std::string weather;
	std::string track;
	std::string trackConfig;
	uint32_t numCars;
	uint32_t currentRecordingIndex; // Usually same as numFrames
	uint32_t numFrames;
	uint32_t numTrackObjects;
};
// Header of each car
struct CarHeader {
	std::string carID;
	std::string driverName;
	std::string nationCode;
	std::string driverTeam;
	std::string carSkinID;
	uint32_t numFrames;
	uint32_t numWings; // Number of 'wings' used for game aero computations
};
// A frame of car data
struct CarFrame {
	vector3<float> position; // X, Y (up), Z positions for car body
	vectorYXZ<std::float16_t> rotation; // X, Y, Z Euler angle rotations for car body in radians
	// Positions and rotations for elements near the wheel that don't rotate, e.g. brake calipers
	// 0: front left wheel, 1: front right wheel, 2: rear left wheel, 3: rear right wheel
	std::array<vector3<float>, 4> wheelStaticPosition;
	std::array<vectorYXZ<std::float16_t>, 4> wheelStaticRotation;
	// Actual wheel positions and rotations
	std::array<vector3<float>, 4> wheelPosition;
	std::array<vectorYXZ<std::float16_t>, 4> wheelRotation;
	vector3<std::float16_t> velocity; // In m/s

	std::float16_t rpm; // Engine RPM
	std::array<std::float16_t, 4> wheelAngularVelocity;
	std::array<std::float16_t, 4> slipAngle; // Usually all 0s
	std::array<std::float16_t, 4> slipRatio; // Actual angular velocity vs. pure rolling angular velocity
	std::array<std::float16_t, 4> ndSlip;
	std::array<std::float16_t, 4> load; // Load on each wheel in Newtons
	std::float16_t steerAngle; // Steering wheel rotation in degrees
	std::float16_t bodyworkNoise; // Amount of mechanical noise (in-game audio units) the car is making
	std::float16_t drivetrainSpeed;
	// Times in milliseconds
	uint32_t currentLapTime;
	uint32_t lastLapTime;
	uint32_t bestLapTime;
	uint8_t fuel; // Fuel amount from 0 to 255
	uint8_t fuelPerLap; // Amount of fuel from 0 to 255 predicted to be used, based on average per-lap fuel consumption
	uint8_t gear; // 0: reverse, 1: neutral, 2: 1st gear, 3: 2nd gear, etc.
	std::array<uint8_t, 4> tireDirt; // Tire dirt amount from 0 to 255
	// Damage to the front of the car from 0 to 255
	// Hood + bumper deformation
	uint8_t damageFrontDeformation;
	uint8_t damageRear; // Damage to the rear of the car from 0 to 255
	uint8_t damageLeft; // Damage to the left of the car from 0 to 255
	uint8_t damageRight; // Damage to the right of the car from 0 to 255
	// Damage to the front of the car from 0 to 255
	// Windshield cracks
	uint8_t damageFront;
	uint8_t gas; // Gas pedal pressed amount from 0 to 255
	uint8_t brake; // Brake pedal pressed amount from 0 to 255
	uint8_t currentLap; // 0: 1st lap, 1: 2nd lap, etc.
	uint8_t unknown; // Usually 0

	bool : 1;
	bool : 1;
	bool unknownBool : 1;
	bool horn : 1;
	unsigned int cameraDir : 2; // Direction the in-game camera is pointing, 0: forward (default), 1: left, 2: right, 3: backward
	unsigned int unknown2 : 2;
	bool : 1;
	bool gearboxBeingDamaged : 1; // Whether the gearbox is being damaged (e.g. when changing gears without clutch)
	bool unknownBool2 : 1;
	bool unknownBool3 : 1;
	bool lights : 1; // Whether headlights, taillights, instrument lights, license plate lights are on
	bool : 1;
	bool : 1;
	bool : 1;

	uint16_t : 16; // Padding

	uint8_t dirt; // Amount of dirt on car body from 0 to 255
	uint8_t engineHealth; // Engine health from 0 to 255
	uint8_t boost; // Boost (turbo) amount from 0 to 255
};
// A frame of extra car data (CSP EXT_PERCAR)
struct CarFrameExtra_v6 {
	uint32_t : 32;
	uint16_t : 16;

	std::float16_t h;
	std::float16_t h2;
	std::float16_t h3; // 00ff
	float f;

	std::float16_t h4;
	std::float16_t h5;
	std::float16_t h6;
	std::float16_t h7;
	std::float16_t h8; // Usually 0

	std::float16_t h9;
	std::float16_t h10;
	std::float16_t h11; // 00ff
	float f2;

	std::float16_t h12;
	std::float16_t h13;

	uint32_t : 32;
	uint16_t : 16;

	std::float16_t h14;
	std::float16_t h15;
	std::float16_t h16; // 00ff
	float f3;

	std::float16_t h17;
	std::float16_t h18;

	uint32_t : 32;
	uint16_t : 16;

	std::float16_t h19;
	std::float16_t h20;
	std::float16_t h21; // 00ff
	float f4;

	std::float16_t h22;
	std::float16_t h23;

	uint32_t : 32;
	uint32_t : 32;

	uint8_t : 8;

	uint8_t wipers; // 0: off, 1: lowest speed, ..., 4: highest speed

	unsigned int turnSignals : 3; // 0: off, 1: left, 2: right, 3: only hazards, 4: hazards + extra dashboard hazard light
	bool lowBeams : 1; // 0: off (high beams), 1: on (low beams)
	bool extraOptionA : 1;
	bool extraOptionB : 1;
	bool extraOptionC : 1;
	bool extraOptionD : 1;
	bool : 1;
	bool unknownBool : 1;
	bool extraOptionE : 1;
	bool extraOptionF : 1;
	bool extraOptionG : 1;
	bool extraOptionH : 1;
	bool extraOptionI : 1;
	bool extraOptionJ : 1;

	uint8_t handbrake; // Handbrake amount from 0 to 255
	uint8_t : 8; // Usually 2

	uint8_t : 8;
	uint8_t : 8;

	std::float16_t h27; // Usually 0

	uint8_t clutch; // Clutch pedal released amount from 0 (pedal pressed) to 255 (pedal released)
	uint8_t : 8;
	uint32_t i; // Usually 0

	// Sometimes 2A2A2A2A
	std::float16_t h28;
	std::float16_t h39;
};
struct CarFrameExtra_v7 {
	uint32_t : 32;
	uint16_t : 16;

	std::float16_t h;
	std::float16_t h2;
	std::float16_t h3; // 00ff
	float f;

	std::float16_t h4;
	std::float16_t h5;
	std::float16_t h6;
	std::float16_t h7;
	std::float16_t h8; // Usually 0

	std::float16_t h9;
	std::float16_t h10;
	std::float16_t h11; // 00ff
	float f2;

	std::float16_t h12;
	std::float16_t h13;

	uint32_t : 32;
	uint16_t : 16;

	std::float16_t h14;
	std::float16_t h15;
	std::float16_t h16; // 00ff
	float f3;

	std::float16_t h17;
	std::float16_t h18;

	uint32_t : 32;
	uint16_t : 16;

	std::float16_t h19;
	std::float16_t h20;
	std::float16_t h21; // 00ff
	float f4;

	std::float16_t h22;
	std::float16_t h23;

	uint32_t : 32;
	uint32_t : 32;

	unsigned int turnSignals : 3; // 0: off, 1: left, 2: right, 3: only hazards, 4: hazards + extra dashboard hazard light
	bool lowBeams : 1; // 0: off (high beams), 1: on (low beams)
	bool extraOptionA : 1;
	bool extraOptionB : 1;
	bool extraOptionC : 1;
	bool extraOptionD : 1;
	bool : 1;
	bool unknownBool : 1;
	bool extraOptionE : 1;
	bool extraOptionF : 1;
	bool extraOptionG : 1;
	bool extraOptionH : 1;
	bool extraOptionI : 1;
	bool extraOptionJ : 1;

	uint8_t : 8;

	uint8_t wipers; // 0: off, 1: lowest speed, ..., 4: highest speed

	uint8_t handbrake; // Handbrake amount from 0 to 255
	uint8_t : 8; // Usually 2

	uint8_t clutch; // Clutch pedal released amount from 0 (pedal pressed) to 255 (pedal released)

	uint8_t : 8;
	uint8_t : 8;

	uint8_t : 8; // Usually 1
	uint8_t : 8; // Likely padding
	uint32_t i; // Usually 0

	// Sometimes 2A2A2A2A
	std::float16_t h28;
	std::float16_t h39;
};

/**
 * Get offset of the extra Custom Shaders Patch data in the given .acreplay file.
 *
 * @param inFile file to be read from. Stream position is not modified.
 * @return offset of CSP data if found.
 */
std::optional<uint32_t> getCSPDataOffset(std::ifstream &inFile);

/**
 * Get names of drivers present in the given .acreplay file.
 *
 * @param inFile file to be read from. Stream position is not modified.
 * @param numDrivers number of drivers in the file, same as the number of cars.
 * @return vector of names of drivers in the file.
 */
std::vector<std::string> getDriverNames(std::ifstream &inFile, int numDrivers);

/**
 * TODO: Use existing JSON utility
 * Parse and ouput given array of CarFrames into outStream in .json format.
 *
 * @param outStream output stream.
 * @param frames CarFrame array.
 * @param numFrames number of elements in the given CarFrame array.
 */
void outputCarFrames(std::ostream &outStream, CarFrame *frames, uint32_t numFrames);
void outputExtraCarFrames_v6(std::ostream &outStream, CarFrameExtra_v6 *frames, uint32_t numFrames);
void outputExtraCarFrames_v7(std::ostream &outStream, CarFrameExtra_v7 *frames, uint32_t numFrames);

/**
 * TODO: Use existing JSON utility
 * Parse and ouput given .acreplay file into a .json file.
 *
 * @param inPath path to input file.
 * @param outPath path to output file.
 * @param targetDriverName name of driver whose car data is to be ouputted.
 */
void readAndOutput(std::string const inPath, std::string_view const outPath = "", std::string_view const targetDriverName = "");
