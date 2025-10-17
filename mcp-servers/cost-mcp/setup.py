from setuptools import setup, find_packages

setup(
    name="cost-mcp",
    version="1.0.0",
    description="Cost Analysis MCP Server for AWS security services cost monitoring",
    packages=find_packages(),
    install_requires=[
        "mcp>=1.0.0",
        "boto3>=1.34.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0"
    ],
    entry_points={
        "console_scripts": [
            "cost-mcp=server:main"
        ]
    },
    python_requires=">=3.10"
)
