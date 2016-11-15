# This file was generated automatically by rootbeer.
# The rootbeer tool is vailable at code-int.ornl.gov/s7o/rootbeer

cmake_minimum_required(VERSION 2.6)
project(coca)
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} $ENV{CMAKE_SOURCE_DIR})
include(FindROOT)

include(CheckIncludeFile)

include(CheckCXXCompilerFlag)
CHECK_CXX_COMPILER_FLAG("-std=c++14" COMPILER_SUPPORTS_CXX14)
CHECK_CXX_COMPILER_FLAG("-std=c++11" COMPILER_SUPPORTS_CXX11)
CHECK_CXX_COMPILER_FLAG("-std=c++0x" COMPILER_SUPPORTS_CXX0X)
if(COMPILER_SUPPORTS_CXX14)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14")
elseif(COMPILER_SUPPORTS_CXX11)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
elseif(COMPILER_SUPPORTS_CXX0X)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")
else()
  message(STATUS "The compiler ${CMAKE_CXX_COMPILER} has no C++11 support. Please use a different C++ compiler.")
endif()

set(INCLUDE_DIRECTORIES
${ROOT_INCLUDE_DIR}
${CMAKE_SOURCE_DIR}
)

set(INCLUDE_DIRECTORIES ${INCLUDE_DIRECTORIES}
"/Users/s7o/github/fmt/install/include"
"/usr/local/Cellar/python/2.7.11/Frameworks/Python.framework/Versions/2.7/include/python2.7"
)
include_directories( ${INCLUDE_DIRECTORIES})
set( SOURCES
PV.cc
)

set( HEADERS
coca/PV.h
)

set(LINKDEF rootbeer_auto_LinkDef.h)
set(DICTIONARY ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}Dict.cxx)
set(PCMFILE ${CMAKE_CURRENT_BINARY_DIR}/lib${PROJECT_NAME}_rdict.pcm)
set(RMAPFILE ${CMAKE_CURRENT_BINARY_DIR}/lib${PROJECT_NAME}.rootmap)
ROOT_GENERATE_DICTIONARY("${HEADERS}" "${LINKDEF}" "${DICTIONARY}" "${INCLUDE_DIRECTORIES}" "${PROJECT_NAME}")
SET(SOURCES ${HEADERS} ${SOURCES} ${DICTIONARY})

add_library(${PROJECT_NAME} SHARED ${SOURCES})
set_target_properties(${PROJECT_NAME} PROPERTIES SUFFIX ".so")
target_link_libraries(${PROJECT_NAME} ${ROOT_LIBRARIES})

target_link_libraries(${PROJECT_NAME} ${ROOT_LIBRARIES})

target_link_libraries(${PROJECT_NAME} /usr/local/Cellar/python/2.7.11/Frameworks/Python.framework/Versions/2.7/lib/libpython2.7.dylib)
macro(INSTALL_HEADERS_WITH_DIRECTORY HEADER_LIST DESTINATION)
  foreach(HEADER ${HEADER_LIST})
    get_filename_component(DIR ${HEADER} PATH)
    install(FILES ${HEADER} DESTINATION ${DESTINATION}/${DIR})
  endforeach(HEADER)
endmacro(INSTALL_HEADERS_WITH_DIRECTORY)

install(TARGETS ${PROJECT_NAME} DESTINATION ${CMAKE_INSTALL_PREFIX}/lib)
INSTALL_HEADERS_WITH_DIRECTORY("${HEADERS}" ${CMAKE_INSTALL_PREFIX}/include)
install(FILES ${PCMFILE} DESTINATION ${CMAKE_INSTALL_PREFIX}/lib)
install(FILES ${RMAPFILE} DESTINATION ${CMAKE_INSTALL_PREFIX}/lib)
