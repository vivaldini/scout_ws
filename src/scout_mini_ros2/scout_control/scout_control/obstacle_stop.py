#!/usr/bin/env python3
"""
obstacle_stop.py
================
Scout Mini – Reactive obstacle avoidance (safety layer).

Autonomous Mobile Robots Course · UFSCar 2025
Teaching Assistant: Milad

Behaviour
---------
Subscribes to /scan and /cmd_vel_input. Passes velocity commands through
to /cmd_vel only when the forward obstacle clearance exceeds a threshold.
When an obstacle is detected within `stop_distance`, a zero-velocity
command is published instead and a warning is logged.

This is a simple *safety layer* pattern, not a full obstacle avoidance
planner. It demonstrates reactive control and sensor-actuator integration.

Topics
------
  Subscribed : /scan           sensor_msgs/LaserScan
               /cmd_vel_input  geometry_msgs/Twist
  Published  : /cmd_vel        geometry_msgs/Twist

Parameters
----------
  stop_distance  [m]    Default: 0.5  – minimum forward clearance
  front_angle    [deg]  Default: 30   – half-angle of the forward sector

Usage
-----
  # Terminal 1: start simulation / real robot
  # Terminal 2: run this node
  ros2 run scout_control obstacle_stop
  # Terminal 3: send velocity commands to the *input* topic
  ros2 run teleop_twist_keyboard teleop_twist_keyboard \
    --ros-args --remap /cmd_vel:=/cmd_vel_input
"""

import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


class ObstacleStop(Node):
    """Passes /cmd_vel_input → /cmd_vel unless a forward obstacle is detected."""

    def __init__(self) -> None:
        super().__init__('obstacle_stop')

        self.declare_parameter('stop_distance', 0.5)   # metres
        self.declare_parameter('front_angle',  30.0)   # degrees, half-angle

        self.stop_distance = self.get_parameter('stop_distance').value
        self.front_angle   = math.radians(self.get_parameter('front_angle').value)

        self._latest_scan: LaserScan | None = None

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.create_subscription(LaserScan, '/scan',          self._scan_cb,    10)
        self.create_subscription(Twist,     '/cmd_vel_input', self._cmd_vel_cb, 10)

        self.get_logger().info(
            f'ObstacleStop ready: stop_distance={self.stop_distance} m, '
            f'front_angle=±{math.degrees(self.front_angle):.0f}°'
        )

    # ── Callbacks ──────────────────────────────────────────────────────────

    def _scan_cb(self, msg: LaserScan) -> None:
        self._latest_scan = msg

    def _cmd_vel_cb(self, msg: Twist) -> None:
        """Gate outgoing velocity commands based on forward clearance."""
        # Only check when robot is moving forward
        if msg.linear.x <= 0.0:
            self.pub.publish(msg)
            return

        if self._latest_scan is None:
            self.get_logger().warn('No LiDAR scan received yet — passing command through.')
            self.pub.publish(msg)
            return

        min_front = self._min_front_distance(self._latest_scan)

        if min_front < self.stop_distance:
            self.get_logger().warn(
                f'Obstacle at {min_front:.2f} m — blocking forward command!'
            )
            self.pub.publish(Twist())   # zero velocity
        else:
            self.pub.publish(msg)

    def _min_front_distance(self, scan: LaserScan) -> float:
        """Return minimum range in the forward sector (±front_angle from heading)."""
        valid_ranges = []
        n = len(scan.ranges)

        for i, r in enumerate(scan.ranges):
            if not (scan.range_min < r < scan.range_max):
                continue
            angle = scan.angle_min + i * scan.angle_increment
            if abs(angle) <= self.front_angle:
                valid_ranges.append(r)

        return min(valid_ranges) if valid_ranges else float('inf')


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ObstacleStop()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
