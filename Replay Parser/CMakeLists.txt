cmake_minimum_required(VERSION 3.25)
project(acrp)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(SOURCE_FILES
	main.cpp
	src/ACReplayParser.cpp
	src/UtilsIO.cpp)

add_executable(${PROJECT_NAME} ${SOURCE_FILES})
