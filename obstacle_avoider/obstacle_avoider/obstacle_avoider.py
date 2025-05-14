import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from rclpy.qos import QoSProfile, QoSReliabilityPolicy

class ObstacleAvoider(Node):
    def __init__(self):
        super().__init__('obstacle_avoider')
        self.safe_distance = 1.0  # 🔹 Stop earlier
        self.detection_angle_range = 0.8  # 🔹 Narrower angle to focus ahead (~70°)
        self.latest_scan = None
        self.moving = False

        qos = QoSProfile(depth=10)
        qos.reliability = QoSReliabilityPolicy.BEST_EFFORT

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.cmd_sub = self.create_subscription(
            Twist, '/cmd_vel_input', self.cmd_vel_cb, 10
        )

        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_cb, qos
        )

        self.timer = self.create_timer(0.002, self.timer_cb)  # 20Hz

        self.get_logger().info("✅ Obstacle Avoider Node gestart (early stop mode)")

    def scan_cb(self, msg):
        self.latest_scan = msg

    def cmd_vel_cb(self, msg):
        if self.latest_scan is None:
            self.get_logger().warn("⚠️ Geen /scan data – noodstop.")
            self.cmd_pub.publish(Twist())
            return

        if msg.linear.x > 0 and self.detect_obstacle_ahead():
            self.get_logger().warn("🛑 Obstacle gedetecteerd bij input – onmiddellijke stop.")
            self.cmd_pub.publish(Twist())
            self.moving = False
        else:
            self.cmd_pub.publish(msg)
            self.moving = True

    def timer_cb(self):
        if self.moving and self.latest_scan is not None:
            if self.detect_obstacle_ahead():
                self.get_logger().warn("🛑 Obstacle tijdens beweging – onmiddellijke stop.")
                self.cmd_pub.publish(Twist())
                self.moving = False

    def detect_obstacle_ahead(self):
        ranges = self.latest_scan.ranges
        angle_min = self.latest_scan.angle_min
        angle_increment = self.latest_scan.angle_increment

        start_angle = -self.detection_angle_range
        end_angle = self.detection_angle_range

        for i, distance in enumerate(ranges):
            angle = angle_min + i * angle_increment
            if start_angle < angle < end_angle:
                if 0.0 < distance < self.safe_distance:
                    return True  # 🚨 ANY hit → stop immediately
        return False

def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoider()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
