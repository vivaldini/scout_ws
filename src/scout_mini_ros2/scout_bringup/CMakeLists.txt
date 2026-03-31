cmake_minimum_required(VERSION 3.8)
project(scout_bringup)

find_package(ament_cmake REQUIRED)

# Install all resource directories into the package share directory
install(DIRECTORY
  launch
  urdf
  worlds
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
