from setuptools import setup, find_packages

setup(
    name="roi-analytics-mcp",
    version="1.0.0",
    description="ROI Analytics MCP Server for security investment analysis",
    packages=find_packages(),
    install_requires=[
        "mcp>=1.0.0",
        "boto3>=1.34.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0"
    ],
    entry_points={
        "console_scripts": [
            "roi-analytics-mcp=server:main"
        ]
    },
    python_requires=">=3.10"
)
