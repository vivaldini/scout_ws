#!/usr/bin/env python3
"""
move_square.py
==============
Scout Mini – Open-loop square trajectory demo.

Autonomous Mobile Robots Course · UFSCar 2025
Teaching Assistant: Milad

Theory
------
The robot executes 4 forward + turn cycles using open-loop timing.
Because the Scout Mini is a skid-steering platform, the actual turning
angle is sensitive to surface friction and wheel slip. On smooth surfaces
the time-based approach works well; on rough terrain, closed-loop control
with odometry feedback would be required.

Kinematic parameters used
--------------------------
  v   = linear velocity  [m/s]   → geometry_msgs/Twist.linear.x
  ω   = angular velocity [rad/s] → geometry_msgs/Twist.angular.z
  t_d = side_length / v           straight-line duration
  t_θ = (π/2) / ω                 90° turn duration

Usage
-----
  ros2 run scout_control move_square
  ros2 run scout_control move_square --ros-args -p side_length:=1.5 -p linear_speed:=0.4
"""

import math
import time

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from geometry_msgs.msg import Twist


class MoveSquare(Node):
    """Open-loop square trajectory node for the Scout Mini robot."""

    def __init__(self) -> None:
        super().__init__('move_square')

        # ── ROS2 parameters (overridable at runtime) ──────────────────────
        self.declare_parameter('side_length',   1.0)   # metres
        self.declare_parameter('linear_speed',  0.3)   # m/s
        self.declare_parameter('angular_speed', 0.5)   # rad/s
        self.declare_parameter('pause_between', 0.5)   # seconds

        self.side_length   = self.get_parameter('side_length').value
        self.linear_speed  = self.get_parameter('linear_speed').value
        self.angular_speed = self.get_parameter('angular_speed').value
        self.pause_between = self.get_parameter('pause_between').value

        # ── Publisher ──────────────────────────────────────────────────────
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.get_logger().info(
            f'MoveSquare ready: side={self.side_length} m, '
            f'v={self.linear_speed} m/s, ω={self.angular_speed} rad/s'
        )

        self.move_square()

    # ──────────────────────────────────────────────────────────────────────
    def _publish_for(self, linear_x: float, angular_z: float, duration: float) -> None:
        """Publish a constant Twist command at 10 Hz for `duration` seconds."""
        msg = Twist()
        msg.linear.x  = linear_x
        msg.angular.z = angular_z

        end_time = time.time() + duration
        while time.time() < end_time:
            self.pub.publish(msg)
            rclpy.spin_once(self, timeout_sec=0.1)

    def stop(self) -> None:
        """Publish a zero-velocity command to halt the robot."""
        self.pub.publish(Twist())
        self.get_logger().info('Robot stopped.')

    def move_square(self) -> None:
        """Execute the 4-sided square trajectory."""
        t_straight = self.side_length / self.linear_speed
        t_turn     = (math.pi / 2.0) / self.angular_speed

        self.get_logger().info(
            f'Starting square: t_straight={t_straight:.2f}s, t_turn={t_turn:.2f}s'
        )

        try:
            for side in range(4):
                # ── Straight segment ──────────────────────────────────────
                self.get_logger().info(f'[Side {side + 1}/4] Moving forward…')
                self._publish_for(self.linear_speed, 0.0, t_straight)

                self.stop()
                time.sleep(self.pause_between)

                # ── 90° counter-clockwise turn ────────────────────────────
                self.get_logger().info(f'[Corner {side + 1}/4] Turning 90°…')
                self._publish_for(0.0, self.angular_speed, t_turn)

                self.stop()
                time.sleep(self.pause_between)

            self.get_logger().info('Square trajectory complete!')

        except KeyboardInterrupt:
            self.stop()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MoveSquare()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
