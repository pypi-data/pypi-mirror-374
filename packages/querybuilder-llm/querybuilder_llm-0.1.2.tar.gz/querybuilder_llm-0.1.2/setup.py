from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name="querybuilder-llm",
    version="0.1.2",
    packages=find_packages(),
    install_requires=["requests"],
    author="Manoj Shetty K",
    description="A pip package to generate SQL/Mongo queries from natural language using an LLM API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
)
