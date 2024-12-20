# Install script for directory: C:/Users/natha/Alabama/Senior Design/radar_sdk/examples/c/BGT60ATR24C

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "C:/Program Files (x86)/rdk")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("C:/Users/natha/Alabama/Senior Design/radar_sdk/sdk/build/examples/c/BGT60ATR24C/common/cmake_install.cmake")
  include("C:/Users/natha/Alabama/Senior Design/radar_sdk/sdk/build/examples/c/BGT60ATR24C/continuous_wave/cmake_install.cmake")
  include("C:/Users/natha/Alabama/Senior Design/radar_sdk/sdk/build/examples/c/BGT60ATR24C/motion_angle/cmake_install.cmake")
  include("C:/Users/natha/Alabama/Senior Design/radar_sdk/sdk/build/examples/c/BGT60ATR24C/presence_detection/cmake_install.cmake")
  include("C:/Users/natha/Alabama/Senior Design/radar_sdk/sdk/build/examples/c/BGT60ATR24C/range_doppler_map/cmake_install.cmake")
  include("C:/Users/natha/Alabama/Senior Design/radar_sdk/sdk/build/examples/c/BGT60ATR24C/raw_data/cmake_install.cmake")
  include("C:/Users/natha/Alabama/Senior Design/radar_sdk/sdk/build/examples/c/BGT60ATR24C/segmentation/cmake_install.cmake")

endif()

