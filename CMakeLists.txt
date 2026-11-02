cmake_minimum_required(VERSION 3.20)
project(ConnectFour LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Download GoogleTest at configure time (needs internet the first time).
if(POLICY CMP0135)
  cmake_policy(SET CMP0135 NEW)
endif()
include(FetchContent)
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/tags/v1.15.2.zip
)
# On Windows/MSVC, link GoogleTest against the same C runtime as our code.
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
set(INSTALL_GTEST OFF CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

enable_testing()

add_executable(connect4_tests
  Connect4-Tests/ConnectFour.cpp
  Connect4-Tests/test.cpp
)
target_link_libraries(connect4_tests PRIVATE GTest::gtest_main)

include(GoogleTest)
# XML_OUTPUT_DIR: every test run through CTest saves its result in build/test-results,
# where the RedGreenGo helper reads it.
gtest_discover_tests(connect4_tests XML_OUTPUT_DIR ${CMAKE_BINARY_DIR}/test-results)
