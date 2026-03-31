#!/usr/bin/env python3
"""
sensor_reader.py
================
Scout Mini – Multi-sensor data inspection node.

Autonomous Mobile Robots Course · UFSCar 2025
Teaching Assistant: Milad

Subscribes to all Scout Mini sensor topics and logs key values.
Useful for verifying sensor health in both simulation and real robot.

Topics subscribed
-----------------
  /scan           sensor_msgs/LaserScan    – 2D LiDAR
  /imu/data       sensor_msgs/Imu          – 6-DOF IMU
  /odom           nav_msgs/Odometry        – Wheel odometry

Usage
-----
  ros2 run scout_control sensor_reader
"""

import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Imu
from nav_msgs.msg import Odometry


def quaternion_to_yaw(q) -> float:
    """Extract yaw (rotation about Z) from a geometry_msgs/Quaternion."""
    siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


class SensorReader(Node):
    """Subscribes to all Scout Mini sensor topics and logs key metrics."""

    def __init__(self) -> None:
        super().__init__('sensor_reader')

        self.create_subscription(LaserScan, '/scan',      self._lidar_cb, 10)
        self.create_subscription(Imu,       '/imu/data',  self._imu_cb,   10)
        self.create_subscription(Odometry,  '/odom',      self._odom_cb,  10)

        self.get_logger().info('SensorReader node started. Listening on /scan, /imu/data, /odom …')

    # ── Callbacks ──────────────────────────────────────────────────────────

    def _lidar_cb(self, msg: LaserScan) -> None:
        valid = [r for r in msg.ranges if msg.range_min < r < msg.range_max]
        if not valid:
            self.get_logger().warn('LiDAR: no valid ranges received.')
            return

        min_r = min(valid)
        max_r = max(valid)
        mean_r = sum(valid) / len(valid)
        n_rays = len(msg.ranges)

        self.get_logger().info(
            f'LiDAR | rays={n_rays} valid={len(valid)} '
            f'min={min_r:.2f}m mean={mean_r:.2f}m max={max_r:.2f}m'
        )

    def _imu_cb(self, msg: Imu) -> None:
        ax = msg.linear_acceleration.x
        ay = msg.linear_acceleration.y
        az = msg.linear_acceleration.z
        wx = msg.angular_velocity.x
        wy = msg.angular_velocity.y
        wz = msg.angular_velocity.z

        self.get_logger().info(
            f'IMU   | accel=({ax:+.2f},{ay:+.2f},{az:+.2f}) m/s²  '
            f'gyro=({wx:+.3f},{wy:+.3f},{wz:+.3f}) rad/s'
        )

    def _odom_cb(self, msg: Odometry) -> None:
        x   = msg.pose.pose.position.x
        y   = msg.pose.pose.position.y
        yaw = quaternion_to_yaw(msg.pose.pose.orientation)
        vx  = msg.twist.twist.linear.x
        wz  = msg.twist.twist.angular.z

        self.get_logger().info(
            f'Odom  | pos=({x:+.3f},{y:+.3f}) yaw={math.degrees(yaw):+.1f}°  '
            f'v={vx:.3f} m/s ω={wz:.3f} rad/s'
        )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = SensorReader()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
