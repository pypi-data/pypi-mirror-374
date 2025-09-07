from setuptools import setup
import json
from pathlib import Path

# Load base metadata from JSON
with open('config.json') as f:
    setup_args = json.load(f)

# Read long description from README for PyPI
readme_path = Path(__file__).parent / 'README.md'
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ''

# Call setup with explicit license metadata to avoid deprecated/dynamic fields
setup(
    data_files=[('ivette-client', ['config.json'])],
    license='Proprietary',
    license_files=[],
    long_description=long_description,
    long_description_content_type='text/markdown',
    **setup_args
)
