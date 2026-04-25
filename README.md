# Scout Mini ROS 2 (Jazzy) Simulation

This repository provides a ROS 2 Jazzy simulation environment for the Scout Mini mobile robot using Gazebo Harmonic.

![Gazebo environment - Scout Mini - ROS 2 Jazzy](https://github.com/vivaldini/scout_ws/blob/main/Docs/scout_sim.png)

## Features

- 4-wheel skid-steering robot (DiffDrive plugin)
- 2D LiDAR sensor (`/scan`)
- IMU sensor (`/imu/data`)
- Wheel odometry (`/odom`)
- Full ROS 2 ↔ Gazebo bridge (starts automatically with each launch)
- Realistic mesh model of Scout Mini

## Requirements

- ROS 2 Jazzy
- Gazebo Harmonic (gz sim)

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

sudo apt update
sudo apt install ros-jazzy-rosidl-default-generators -y

sudo apt update
sudo apt install ros-jazzy-ament-lint-auto ros-jazzy-ament-lint-common -y
```

## Installation

Clone the repository:

```bash
cd ~/
git clone https://github.com/vivaldini/scout_ws.git
```

Build the workspace:

```bash
cd ~/scout_ws
colcon build
source install/setup.bash
```

> **Note:** Run `colcon build` again and re-source after every `git pull` to pick up new changes.

---

## Simulation Environments

The ROS 2 ↔ Gazebo bridge starts **automatically** with every launch — you do not need to run it separately.

---

### Week 4 — Introduction: Open World

A flat open environment for getting familiar with the robot, sensors, and teleoperation.

![Week 4 - Open World](https://github.com/vivaldini/scout_ws/blob/main/Docs/scout_world.png)

```bash
ros2 launch scout_sim scout_sim.launch.py
```

---

### Week 5 — Competition: DC Environment with Obstacles

An indoor corridor with boxes and barriers. Used for the Week 5 navigation competition.

![Week 5 - DC Environment](https://github.com/vivaldini/scout_ws/blob/main/Docs/dc_world.png)

```bash
ros2 launch scout_sim scout_sim_dc.launch.py
```

---

### Week 6 — Maze Challenge

A large maze environment. Used for the Week 6 challenge.

![Week 6 - Maze](https://github.com/vivaldini/scout_ws/blob/main/Docs/maze_world.png)

```bash
ros2 launch scout_sim scout_sim_maze.launch.py
```

---

## ROS Topics

After launching any simulation, the following topics are available:

| Topic | Type | Direction |
|-------|------|-----------|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | ROS → Gazebo (velocity commands) |
| `/odom` | `nav_msgs/msg/Odometry` | Gazebo → ROS (wheel odometry) |
| `/scan` | `sensor_msgs/msg/LaserScan` | Gazebo → ROS (2D LiDAR) |
| `/imu/data` | `sensor_msgs/msg/Imu` | Gazebo → ROS (IMU) |
| `/tf` | `tf2_msgs/msg/TFMessage` | Gazebo → ROS (transforms) |
| `/joint_states` | `sensor_msgs/msg/JointState` | Gazebo → ROS (wheel joints) |
| `/clock` | `rosgraph_msgs/msg/Clock` | Gazebo → ROS (sim time) |

## Teleoperation

Control the robot manually using the keyboard:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```
