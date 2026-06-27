from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, Command
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.conditions import IfCondition

def launch_setup(context, *args, **kwargs):
    use_sim_time = LaunchConfiguration('use_sim_time')
    world_mode = LaunchConfiguration('world').perform(context)
    teleop_mode = LaunchConfiguration('teleop').perform(context)
    path_to_urdf = get_package_share_path('sim_pkg') / 'urdfs' / 'robot.urdf.xacro'
    world = get_package_share_path('sim_pkg') / 'worlds' / f'{world_mode}.sdf'
    gz_ros_bridge = get_package_share_path('sim_pkg') / 'config' / 'gz_ros_bridge.yaml'
    ekf_config_path = get_package_share_path('sim_pkg') / 'config' / 'ekf.yaml'
    joystick_config_file = get_package_share_path('sim_pkg')/'config'/'joystick.yaml'
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': ParameterValue(
                Command(['xacro ', str(path_to_urdf)]), value_type=str
            ),
            'use_sim_time': use_sim_time
        }]
    )

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [str(get_package_share_path('ros_gz_sim') / 'launch' / 'gz_sim.launch.py')]
        ),
        launch_arguments={"gz_args": [" -r -v 4 ", str(world)]}.items(), 
    )

    robot_spawner = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic", "/robot_description",
            "-x", "0", "-y", "0", "-z", "1.0",
        ],
        output="screen",
        parameters=[{'use_sim_time': use_sim_time}]
    )

    gz_ros_bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '--ros-args',
            '-p',
            f'config_file:={str(gz_ros_bridge)}',
        ],
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[
            str(ekf_config_path),
            {'use_sim_time': use_sim_time}
        ],
        condition=IfCondition(LaunchConfiguration('ekf'))
    )
    if teleop_mode == 'keyboard':
        teleop_node = Node(
            package='teleop_twist_keyboard',
            executable='teleop_twist_keyboard',
            name='teleop_keyboard_node',
            remappings=[('/cmd_vel', '/diff_drive_controller/cmd_vel')],
            parameters=[{'stamped': False}],
            prefix='gnome-terminal --'  # this launches new terminal window to control the robot using keyboard

        )
        return [robot_state_publisher_node, gz_sim, robot_spawner, gz_ros_bridge_node, ekf_node, teleop_node]
    
    elif teleop_mode == 'joystick':
        joy_node = Node(
            package='joy',
            executable='joy_node',
            parameters=[joystick_config_file],
        )
        # Node for sending commands to robot
        teleop_node = Node(
            package='teleop_twist_joy',
            executable='teleop_node',
            name='teleop_node',
            parameters=[joystick_config_file],
            remappings=[('/cmd_vel', '/diff_drive_controller/cmd_vel')]
        )
        return [robot_state_publisher_node, gz_sim, robot_spawner, gz_ros_bridge_node, ekf_node, joy_node, teleop_node]
    else:
        raise ValueError(
            f"Invalid mode '{teleop_mode}'. "
            f"Use 'keyboard' or 'joystick'."
        )

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time', 
            default_value='true'),
        DeclareLaunchArgument(
            'world', 
            default_value='warehouse', 
            description='modes: simple, warehouse'),
        DeclareLaunchArgument(
            'teleop', 
            default_value='keyboard', 
            description='modes: keyboard, joystick'),
        DeclareLaunchArgument(
            'ekf',
            default_value='true',
            description='If EKF node should be started.',
),
        OpaqueFunction(function=launch_setup)
    ])