from setuptools import setup

setup(
    name="pipeline_auth",
    version="0.0.1",
    author="Greg Thole",
    packages=[
        'pipeline_auth',
    ],
    install_requires=[
        'requests==2.3.0',
        'github3.py==0.9.0',
    ],
    description="Two step client authentication class for OAuth login with "
                "the GitHub API against an application API"
)
