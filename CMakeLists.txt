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

# RedGreenGo: fetch the latest rgg_server.py each time CMake configures (the IDE does that
# when it opens the folder). Offline, the copy already here is kept.
option(RGG_UPDATE_HELPER "Download the latest rgg_server.py when configuring" ON)
if(RGG_UPDATE_HELPER)
  file(DOWNLOAD https://kenpower.github.io/RedGreenGoWeb/build/rgg_server.py
       ${CMAKE_BINARY_DIR}/rgg_server.py.download TIMEOUT 10 STATUS rgg_status)
  list(GET rgg_status 0 rgg_code)
  if(rgg_code EQUAL 0)
    execute_process(COMMAND ${CMAKE_COMMAND} -E copy_if_different
                    ${CMAKE_BINARY_DIR}/rgg_server.py.download ${CMAKE_SOURCE_DIR}/rgg_server.py)
  else()
    list(GET rgg_status 1 rgg_error)
    message(WARNING "RedGreenGo: couldn't update rgg_server.py (${rgg_error}); keeping the copy here")
  endif()
endif()

add_executable(connect4_tests
  Connect4-Tests/ConnectFour.cpp
  Connect4-Tests/test.cpp
)
target_link_libraries(connect4_tests PRIVATE GTest::gtest_main)

include(GoogleTest)
# XML_OUTPUT_DIR: every test run through CTest saves its result in build/test-results,
# where the RedGreenGo helper reads it.
gtest_discover_tests(connect4_tests XML_OUTPUT_DIR ${CMAKE_BINARY_DIR}/test-results)
