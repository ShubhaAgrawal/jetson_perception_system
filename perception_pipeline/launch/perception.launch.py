from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='perception_pipeline',
            executable='camera_node',
            name='camera_node',
            output='screen'
        ),
        Node(
            package='perception_pipeline',
            executable='detection_node',
            name='detection_node',
            output='screen'
        ),
        Node(
            package='perception_pipeline',
            executable='viewer_node',
            name='viewer_node',
            output='screen'
        ),
    ])
