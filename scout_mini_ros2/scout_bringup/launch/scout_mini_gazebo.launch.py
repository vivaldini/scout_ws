#!/usr/bin/env python3
"""
scout_mini_gazebo.launch.py
===========================
Launches the Scout Mini simulation in Gazebo Classic 11 with ROS2 Humble.

What this launch file does:
  1. Starts Gazebo Classic (gzserver + gzclient) with scout_world.world
  2. Processes the Scout Mini URDF/Xacro
  3. Starts robot_state_publisher  → publishes /robot_description and /tf
  4. Spawns the robot model into Gazebo via spawn_entity
  5. Starts joint_state_publisher  → publishes /joint_states

Architecture note:
  The skid_steer_drive Gazebo plugin handles /cmd_vel → wheel control
  and publishes /odom internally. No separate controller manager is needed
  for this simulation.

Topic summary after launch:
  /cmd_vel        ← send velocity commands here
  /odom           ← wheel odometry (published by Gazebo plugin)
  /scan           ← 2D LiDAR (published by Gazebo plugin)
  /imu/data       ← IMU (published by Gazebo plugin)
  /tf             ← odom → base_footprint (published by Gazebo plugin)
  /joint_states   ← wheel joint angles (published by robot_state_publisher)

Usage:
  ros2 launch scout_bringup scout_mini_gazebo.launch.py
  ros2 launch scout_bringup scout_mini_gazebo.launch.py world:=empty
  ros2 launch scout_bringup scout_mini_gazebo.launch.py gui:=false

Authors: Milad (TA), Autonomous Mobile Robots, UFSCar 2025
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # ── Package directories ─────────────────────────────────────────────
    pkg_scout_bringup  = get_package_share_directory('scout_bringup')
    pkg_gazebo_ros     = get_package_share_directory('gazebo_ros')

    # ── File paths ──────────────────────────────────────────────────────
    urdf_path  = os.path.join(pkg_scout_bringup, 'urdf',   'scout_mini_sim.urdf.xacro')
    world_path = os.path.join(pkg_scout_bringup, 'worlds', 'scout_world.world')

    # ── Process URDF/Xacro → XML string ────────────────────────────────
    # Command() runs xacro at launch-time, producing the robot_description
    robot_description_content = Command([
        PathJoinSubstitution([FindExecutable(name='xacro')]),
        ' ',
        urdf_path,
    ])

    # ── Launch arguments ────────────────────────────────────────────────
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time', default_value='true',
        description='Use Gazebo simulation clock')

    declare_gui = DeclareLaunchArgument(
        'gui', default_value='true',
        description='Set to false to run Gazebo headless (no GUI)')

    declare_world = DeclareLaunchArgument(
        'world', default_value=world_path,
        description='Full path to the Gazebo world file')

    declare_x = DeclareLaunchArgument('x_pose', default_value='0.0',
        description='Initial X position of the robot')
    declare_y = DeclareLaunchArgument('y_pose', default_value='0.0',
        description='Initial Y position of the robot')
    declare_z = DeclareLaunchArgument('z_pose', default_value='0.15',
        description='Initial Z position of the robot (above ground)')

    use_sim_time = LaunchConfiguration('use_sim_time')

    # ── Gazebo Classic launch ───────────────────────────────────────────
    # gzserver runs the physics simulation; gzclient opens the GUI
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'world': LaunchConfiguration('world'),
            'gui':   LaunchConfiguration('gui'),
        }.items(),
    )

    # ── Robot State Publisher ───────────────────────────────────────────
    # Reads robot_description and publishes static TF transforms
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time':       use_sim_time,
            'robot_description':  robot_description_content,
        }],
    )

    # ── Spawn entity into Gazebo ────────────────────────────────────────
    # Reads /robot_description topic and spawns the model in Gazebo.
    # Wrapped in TimerAction to wait for Gazebo to fully start.
    spawn_robot = TimerAction(
        period=3.0,  # seconds — wait for Gazebo to be ready
        actions=[
            Node(
                package='gazebo_ros',
                executable='spawn_entity.py',
                name='spawn_scout_mini',
                output='screen',
                arguments=[
                    '-entity',       'scout_mini',
                    '-topic',        '/robot_description',
                    '-x', LaunchConfiguration('x_pose'),
                    '-y', LaunchConfiguration('y_pose'),
                    '-z', LaunchConfiguration('z_pose'),
                ],
            )
        ],
    )

    return LaunchDescription([
        # Declare arguments first
        declare_use_sim_time,
        declare_gui,
        declare_world,
        declare_x,
        declare_y,
        declare_z,

        # Launch sequence
        gazebo,               # 1. Start Gazebo
        robot_state_publisher, # 2. Start RSP (publishes /robot_description)
        spawn_robot,          # 3. Spawn robot after 3s delay
    ])
