cmake_minimum_required(VERSION 3.25)
project(acreplay-parser LANGUAGES CXX)
set(NAME acrp)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(${NAME})
target_sources(${NAME}
	PRIVATE
		main.cpp
		src/ACReplayParser.cpp
		src/UtilsIO.cpp
	PUBLIC
		FILE_SET HEADERS
		BASE_DIRS include
		FILES
			include/ACReplayParser.hpp
			include/UtilsData.hpp
			include/UtilsIO.hpp
)

target_compile_options(${NAME}
	PRIVATE
		-Werror -Wall -Wextra -Wshadow -pedantic -Wpedantic
		-Wold-style-cast -Wcast-align -Wunused -Wconversion -Wsign-conversion
		-Wmisleading-indentation -Wduplicated-cond -Wnull-dereference
		-O3
		$<$<CONFIG:Debug>:-fsanitize=address,undefined>
)
target_link_options(${NAME} PRIVATE $<$<CONFIG:Debug>:-fsanitize=address,undefined>)

# Link statically if building for Windows
if (CMAKE_SYSTEM_NAME STREQUAL "Windows")
	target_link_options(${NAME} PRIVATE -static)
	target_link_libraries(${NAME} PRIVATE -lstdc++exp) # For std::print
	set(ZLIB_USE_STATIC_LIBS ON)
endif()

find_package(ZLIB REQUIRED)
target_include_directories(${NAME} PRIVATE ${ZLIB_INCLUDE_DIRS})
target_link_libraries(${NAME} PRIVATE ${ZLIB_LIBRARIES})
