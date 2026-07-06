from setuptools import find_packages, setup

package_name = "actuation"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Oleg Vdovin",
    maintainer_email="ipgleg@gmail.com",
    description=(
        "Actuation layer: Gazebo sim backend (Phase 1) and optional "
        "real-hardware backend (Phase 5), same core/cmd interface."
    ),
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "sim_backend = actuation.sim_backend:main",
            "hardware_backend = actuation.hardware_backend:main",
        ],
    },
)
