from setuptools import setup, find_packages

setup(
    name="signal_ICT_StudentName_EnrollmentNo",   # <-- replace this
    version="0.1.0",
    description="Basic signals and operations package for Signals & Systems demo",
    author="StudentName",
    author_email="student@example.com",
    packages=find_packages(),
    install_requires=["numpy", "matplotlib"],
    python_requires=">=3.8",
)
