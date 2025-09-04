from setuptools import setup, find_packages

setup(
    name="ashraf-camera",
    version="1.0.0",
    author="Ashraf",
    description="Library to take screenshots or photos using simple commands",
    packages=find_packages(),
    install_requires=[
        "opencv-python",
        "pyautogui"
    ],
    python_requires=">=3.7",
)
