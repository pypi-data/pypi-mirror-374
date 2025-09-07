from setuptools import setup, find_packages

setup(
    name="ML_Automation_Tool",
    version="1.0.0",
    author="Yassine",
    author_email="your_email@example.com",
    description="Automated Machine Learning tool with GUI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ML_Automation_Tool",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "scikit-learn",
        "joblib",
        "PySimpleGUI"
    ],
    entry_points={
        "console_scripts": [
            "ml-automation-tool=ml_automation_tool.gui_main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
