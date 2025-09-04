# CMakeLists.txt

cmake_minimum_required(VERSION 3.15)
project(vcon_py C)

# Ensure we compile as C99 (code uses classic C interfaces)
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)


include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src/vconpy/vcon)

add_executable(vcon
    ${CMAKE_CURRENT_SOURCE_DIR}/src/vconpy/vcon/Vcontacts-v1-2.c
)

if(MSVC)
    target_compile_options(vcon PRIVATE /O2)
else()
    target_compile_options(vcon PRIVATE -O3)
    target_link_libraries(vcon PRIVATE m)
endif()

# Install
include(GNUInstallDirs)

install(TARGETS vcon
        RUNTIME DESTINATION ${CMAKE_INSTALL_PREFIX}/bin
)

# Install Python module files
install(FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/src/vconpy/__init__.py
    ${CMAKE_CURRENT_SOURCE_DIR}/src/vconpy/vcontacts_wrapper.py
    DESTINATION ${CMAKE_INSTALL_PREFIX}
)