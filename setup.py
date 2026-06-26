from setuptools import setup, find_packages

setup(
    name="pc-llm-scanner",
    version="1.0.0",
    author="Chamalka Lakshan",
    author_email="chamalkalakshan100@gmail.com",
    description="Scan PC hardware and recommend compatible local LLMs",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "rich>=13.7.0",
        "psutil>=5.9.0",
        "py-cpuinfo>=9.0.0",
        "GPUtil>=1.4.0",
    ],
    entry_points={
        "console_scripts": [
            "llm-scanner=main:main",
        ],
    },
)
