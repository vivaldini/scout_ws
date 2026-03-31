#!/usr/bin/env python3
"""
move_circle.py
==============
Scout Mini – Constant-curvature circular trajectory demo.

Autonomous Mobile Robots Course · UFSCar 2025
Teaching Assistant: Milad

Theory
------
A circular arc is achieved by simultaneously commanding linear and angular
velocity such that the instantaneous centre of curvature (ICC) stays fixed.

For a skid-steering robot, the relationship between (v, ω) and the ICC
radius R is simply:

    R = v / ω   [metres]

So to drive a circle of radius R at speed v:
    ω = v / R   [rad/s]

Full circle duration:
    T = 2πR / v = 2π / ω   [seconds]

Usage
-----
  ros2 run scout_control move_circle
  ros2 run scout_control move_circle --ros-args -p radius:=1.5 -p linear_speed:=0.3
"""

import math
import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class MoveCircle(Node):
    """Constant-curvature circular trajectory node for the Scout Mini."""

    def __init__(self) -> None:
        super().__init__('move_circle')

        self.declare_parameter('radius',       1.0)   # metres
        self.declare_parameter('linear_speed', 0.3)   # m/s
        self.declare_parameter('loops',        1)      # number of full circles

        self.radius       = self.get_parameter('radius').value
        self.linear_speed = self.get_parameter('linear_speed').value
        self.loops        = self.get_parameter('loops').value

        self.angular_speed = self.linear_speed / self.radius          # ω = v / R
        self.period        = (2.0 * math.pi * self.radius) / self.linear_speed  # T

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.get_logger().info(
            f'MoveCircle: R={self.radius} m, v={self.linear_speed} m/s, '
            f'ω={self.angular_speed:.3f} rad/s, T={self.period:.2f} s/loop'
        )

        self.move_circle()

    def _publish_for(self, linear_x: float, angular_z: float, duration: float) -> None:
        msg = Twist()
        msg.linear.x  = linear_x
        msg.angular.z = angular_z
        end_time = time.time() + duration
        while time.time() < end_time:
            self.pub.publish(msg)
            rclpy.spin_once(self, timeout_sec=0.1)

    def stop(self) -> None:
        self.pub.publish(Twist())

    def move_circle(self) -> None:
        try:
            for i in range(self.loops):
                self.get_logger().info(f'[Loop {i + 1}/{self.loops}] Executing circle…')
                self._publish_for(self.linear_speed, self.angular_speed, self.period)
            self.stop()
            self.get_logger().info('Circle trajectory complete!')
        except KeyboardInterrupt:
            self.stop()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MoveCircle()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
