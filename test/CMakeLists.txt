cmake_minimum_required(VERSION 2.8)
project(bgfx_test)

#include_directories(${CMAKE_CURRENT_SOURCE_DIR})

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)

conan_basic_setup()

add_executable(bgfx_test bgfx_test.cpp)
target_link_libraries(bgfx_test ${CONAN_LIBS})
