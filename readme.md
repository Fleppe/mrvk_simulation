# sim_pkg — MRVK Robot Simulation

A ROS 2 simulation package for the **MRVK** mobile robot, built for **ROS 2 Jazzy** and **Gazebo Harmonic** on **Ubuntu 24.04 LTS**.

The package spawns the MRVK robot inside a Gazebo world, optionally fuses odometry with IMU data through an EKF, and lets the user drive the robot from a keyboard or a joystick.

---

## Sensors

- **2D LiDAR** — modelled after the *Hokuyo UTM-30LX*
- **RGB-D camera** — modelled after the *Microsoft Kinect v2*
- **IMU** — modelled after the *ADIS 16250*
- **Wheel odometry** from the differential drive controller

---

## Requirements

| Component | Version |
|-----------|---------|
| OS | Ubuntu 24.04 LTS |
| ROS 2 | Jazzy Jalisco |
| Gazebo | Harmonic |

---
## Usage

Launch the simulation with default settings (warehouse world, keyboard teleop, EKF enabled):

```bash
ros2 launch sim_pkg sim_launch.py
```

### Launch arguments

| Argument | Default | Allowed values | Description |
|----------|---------|----------------|-------------|
| `use_sim_time` | `true` | `true` / `false` | Use Gazebo's simulated clock |
| `world` | `warehouse` | `simple`, `warehouse` | World to load in Gazebo |
| `teleop` | `keyboard` | `keyboard`, `joystick` | Input device for teleoperation |
| `ekf` | `true` | `true` / `false` | Enable EKF sensor fusion |

### Example of changing the launch argument:

```bash
ros2 launch sim_pkg sim_launch.py teleop:=joystick
```

## EKF configuration

The EKF runs on top of the `robot_localization` package and fuses:

- **Linear velocity** `vx` from the differential-drive wheel odometry
- **Yaw rate** (`ωz`) from the IMU

The fused estimate is published as the `odom → base_link` transform and on the `/odometry/filtered` topic. Parameters can be configured in `config/ekf.yaml`.

---
### Notes
- plugins for LiDAR, RGB-D camera and IMU are in world .sdf files, so if you want to change the simulation world, you must also include plugins in the file.
### Known bugs

- LiDAR visualisation
