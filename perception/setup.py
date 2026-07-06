from setuptools import find_packages, setup

package_name = "perception"

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
        "Phase 2: video/audio emotion recognition nodes and confidence-weighted fusion."
    ),
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "video_emotion_node = perception.video_emotion_node:main",
            "audio_emotion_node = perception.audio_emotion_node:main",
            "fusion_node = perception.fusion_node:main",
        ],
    },
)
