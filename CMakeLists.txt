cmake_minimum_required(VERSION 3.21)
set(CMAKE_C_STANDARD 99)
set(CMAKE_CXX_STANDARD 17)
project(sokol-samples)

if (SOKOL_USE_WGPU_DAWN)
    set(USE_DAWN_SDK ON)
endif()

# include the fips main cmake file
get_filename_component(FIPS_ROOT_DIR "../fips" ABSOLUTE)
include("${FIPS_ROOT_DIR}/cmake/fips.cmake")

fips_setup()
fips_ide_group("Imports")
fips_import_fips_imgui_imgui()
fips_import_fips_cimgui_cimgui()
fips_import_fips_imgui_dock_imgui_dock()
if (NOT FIPS_UWP)
    fips_import_fips_libmodplug_libmodplug()
endif()
fips_ide_group("")

# just suppress this pesky "missing field initializer warning" for now
if (FIPS_CLANG OR FIPS_GCC)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wno-missing-field-initializers -Wsign-conversion")
endif()

#  platform selection
add_definitions(-DSOKOL_NO_DEPRECATED)
if (FIPS_EMSCRIPTEN)
    if (FIPS_EMSCRIPTEN_USE_WEBGPU)
        set(sokol_backend SOKOL_WGPU)
        set(slang "wgsl")
    else()
        set(sokol_backend SOKOL_GLES3)
        set(slang "glsl300es")
    endif()
endif()

if (USE_SOKOL_APP)
    include_directories(libs)
    fips_ide_group("Libs")
    add_subdirectory(libs)
    fips_ide_group("Samples")
    add_subdirectory(sapp)
else()
    if (FIPS_EMSCRIPTEN)
        if (FIPS_EMSCRIPTEN_USE_WEBGPU)
            add_subdirectory(wgpu)
        else()
            add_subdirectory(html5)
        endif()
    else () # SOKOL_USE_WGPU_DAWN
        add_subdirectory(wgpu)
    endif()
endif()
