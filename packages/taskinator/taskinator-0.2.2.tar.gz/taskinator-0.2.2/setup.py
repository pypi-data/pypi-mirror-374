from setuptools import setup, find_packages

setup(
    name="taskinator",
    version="0.2.2",
    description="A Python CLI task management tool for software development projects. Heavily inspired by claude-task-master",
    author="Steve Smahnuk",
    author_email="ssmashnuk@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.7.0",
        "pydantic>=2.5.2",
        "anthropic>=0.18.1",
        "openai>=1.13.3",
        "python-dotenv>=1.0.0",
        "filelock>=3.12.0",
        "litellm>=1.68.1",
        "caldav>=1.3.0",
        "tomli>=2.0.1",
    ],
    extras_require={
        "dev": [
            "black>=23.12.0",
            "isort>=5.12.0",
            "mypy>=1.7.1",
            "pytest>=7.4.3",
            "pytest-bdd>=7.1.1",
            "flake8>=6.1.0",
        ],
        "azure": [
            "azure-devops>=7.1.0",  # For Azure DevOps integration
        ],
        "gitlab": [
            "python-gitlab>=4.4.0",  # For GitLab integration
        ],
    },
    entry_points={
        "console_scripts": [
            "taskinator=taskinator.__main__:app",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
)
