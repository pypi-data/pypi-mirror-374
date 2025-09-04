from setuptools import setup, find_packages

setup(
    name="priyanshu-cli",
    version="1.0.0",
    packages=find_packages(),  # ✅ Automatically finds priyanshu_cli
    install_requires=[
        "click",
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "priyanshu-cli=priyanshu_cli.main:get_repos",
        ],
    },
    author="Priyanshu Paikra",
    description="A simple CLI tool to fetch GitHub repositories",
    keywords="cli github repositories python",
)
