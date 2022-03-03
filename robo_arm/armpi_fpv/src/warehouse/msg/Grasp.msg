# 夹取时的姿态和位置: Attitude and position when gripping
warehouse/Pose grasp_pos

# 接近时的距离和方向: Distance and direction when approaching
geometry_msgs/Vector3 grasp_approach

# 撤离时的距离和方向: Distance and direction for evacuation
geometry_msgs/Vector3 grasp_retreat

# 抬高高度: Raise the height
float64 up

# 夹取时夹持器姿态: Gripper attitude when gripping
int16 grasp_posture

# 夹取前夹持器姿态: Gripper attitude before gripping
int16 pre_grasp_posture

