cmake_minimum_required(VERSION 3.8)
set (CMAKE_CXX_STANDARD 11)
set (CMAKE_USE_RELATIVE_PATHS TRUE)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/Modules/")

#find cppzmq wrapper, installed by make of cppzmq
find_package(cppzmq)
find_package( OpenCV HINTS /usr/local/Cellar/opencv3/HEAD-f109c01 )
find_package( OpenCV REQUIRED )
find_package(dlib REQUIRED)
find_package(TBB REQUIRED)
find_package( Boost 1.5.9 REQUIRED COMPONENTS filesystem system)

include_directories(${OpenCV_INCLUDE_DIRS} )
include_directories(${cppzmq_INCLUDE_DIR})
include_directories(${dlib_INCLUDE_DIRS})
include_directories(${TBB_ROOT_DIR}/include)
include_directories(${Boost_INCLUDE_DIRS})
include_directories(${Boost_INCLUDE_DIRS}/boost)
include_directories('/usr/local/include/SimpleAmqpClient')
include_directories('/usr/local/include/msgpack')
include_directories ("./include")

LINK_DIRECTORIES(${Boost_LIBRARY_DIRS})

add_executable(facial_features facial_features.cpp)

target_link_libraries(facial_features LandmarkDetector)
target_link_libraries(facial_features FaceAnalyser)
target_link_libraries(facial_features ${dlib_LIBS})
target_link_libraries(facial_features ${TBB_LIBRARIES})
target_link_libraries(facial_features ${Boost_LIBRARIES})
target_link_libraries(facial_features ${cppzmq_LIBRARY})
target_link_libraries(facial_features SimpleAmqpClient)
#target_link_libraries(facial_features msgpack)
target_link_libraries(facial_features ${OpenCV_LIBS})
