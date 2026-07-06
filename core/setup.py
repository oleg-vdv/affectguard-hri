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
    maintainer="Oleg Vdovin",
    maintainer_email="ipgleg@gmail.com",
    description=(
        "Policy engine (cognitive/arbitration layer) and safety envelope. "
        "Phase 3: rule-based policy engine with an enforced safety envelope."
    ),
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "policy_engine = core.policy_engine:main",
        ],
    },
)
