cmake_minimum_required(VERSION 2.8 FATAL_ERROR)
project(GA_PLUGIN)

# Find Gazebo
find_package(gazebo REQUIRED)
include_directories(${GAZEBO_INCLUDE_DIRS})
link_directories(${GAZEBO_LIBRARY_DIRS})
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${GAZEBO_CXX_FLAGS}")

# Build our plugin
add_library(simple_plug SHARED simple/simple_sub.cpp)
target_link_libraries(simple_plug ${GAZEBO_libraries})
target_compile_features(simple_plug PRIVATE cxx_std_17)
install(TARGETS simple_plug DESTINATION ${PROJECT_SOURCE_DIR}/bin)