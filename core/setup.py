from setuptools import find_packages, setup

package_name = "core"

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
    maintainer="AffectGuard-HRI maintainers",
    maintainer_email="ipgleg@gmail.com",
    description=(
        "Policy engine (cognitive/arbitration layer) and safety envelope. "
        "Phase 1: stub node publishing movement commands on a timer."
    ),
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "policy_engine_stub = core.policy_engine_stub:main",
        ],
    },
)
