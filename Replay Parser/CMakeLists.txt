cmake_minimum_required(VERSION 3.25)
project(acrp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if (CMAKE_SYSTEM_NAME STREQUAL "Windows") # Link statically if building for Windows
	set(ZLIB_USE_STATIC_LIBS ON)
	add_link_options(-static)
endif()

add_link_options(-Wall -pedantic)

find_package(ZLIB REQUIRED)
include_directories(${ZLIB_INCLUDE_DIRS})

set(SOURCE_FILES
	main.cpp
	src/ACReplayParser.cpp
	src/UtilsIO.cpp)

add_executable(${PROJECT_NAME} ${SOURCE_FILES})
target_link_libraries(${PROJECT_NAME} ${ZLIB_LIBRARIES})
