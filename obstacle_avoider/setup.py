from setuptools import setup

package_name = 'obstacle_avoider'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='dogan',
    maintainer_email='mehmet.schepens@student.ehb.be',
    description='Obstacle avoidance using LaserScan and blocking unsafe cmd_vel',
    license='MIT',
    entry_points={
        'console_scripts': [
            'obstacle_avoider = obstacle_avoider.obstacle_avoider:main',
        ],
    },
)
