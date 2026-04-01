# Scout Mini ROS 2 (Jazzy) Simulation

This repository provides a ROS 2 Jazzy simulation environment for the Scout Mini mobile robot using Gazebo Harmonic.

![Gazebo environment - Scout Mini - ROS 2 Jazzy](https://github.com/vivaldini/scout_ws/blob/main/Docs/scout_sim.png)

## Features

- 4-wheel skid-steering robot (DiffDrive plugin)
- 2D LiDAR sensor (/scan)
- IMU sensor (/imu/data)
- Wheel odometry (/odom)
- Full ROS 2 ↔ Gazebo bridge
- Realistic mesh model of Scout Mini

## Requirements

- ROS 2 Jazzy
- Gazebo Harmonic (gz sim)
- ros_gz_bridge

### Install dependencies

```bash
sudo apt update
sudo apt install build-essential git cmake libasio-dev
sudo apt install ros-jazzy-ros-gz-bridge

sudo apt update
sudo apt install ros-jazzy-xacro -y

sudo apt update
sudo apt install ros-jazzy-ros-gz -y

sudo apt update
sudo apt install ros-jazzy-teleop-twist-keyboard -y
```

## Installation

```bash
cd ~/
```

Clone the repository

```bash
git clone https://github.com/vivaldini/scout_ws.git
```


Build the workspace

```bash
cd ~/scout_ws
colcon build
source install/setup.bash
```

## Running the Simulation

Launch Gazebo with the Scout Mini robot:

```bash
ros2 launch scout_sim scout_sim.launch.py
```

## ROS ↔ Gazebo Bridge

Run the bridge between Gazebo and ROS 2:

```bash
ros2 run ros_gz_bridge parameter_bridge \
/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist \
/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry \
/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan
```

## Teleoperation

Control the robot using the keyboard:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```
