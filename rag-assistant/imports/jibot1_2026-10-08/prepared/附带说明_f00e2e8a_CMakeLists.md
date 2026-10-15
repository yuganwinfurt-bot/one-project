# CMakeLists.txt

原始来源：E:\BaiduNetdiskDownload\002-开源机械臂Jibot1（STM32）\003-源码例程\09-AI智控模块拓展代码\01-源码\ZL_AI_ZHIKONG_RoboticArm_V1.0.0.zip!/ZL_AI_ZHIKONG_RoboticArm_V1.0.0/CMakeLists.txt

# For more information about build system see
# https://docs.espressif.com/projects/esp-idf/en/latest/api-guides/build-system.html
# The following five lines of boilerplate have to be in your project's
# CMakeLists in this exact order for cmake to work correctly
cmake_minimum_required(VERSION 3.16)

set(PROJECT_VER "1.4.7")

# Add this line to disable the specific warning
add_compile_options(-Wno-missing-field-initializers)
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(xiaozhi)

