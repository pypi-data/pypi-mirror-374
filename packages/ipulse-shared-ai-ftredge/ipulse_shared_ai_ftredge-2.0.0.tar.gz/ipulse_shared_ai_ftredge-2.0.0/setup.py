from setuptools import setup, find_packages

setup(
    name='ipulse_shared_ai_ftredge',
    version='2.0.0',
    package_dir={'': 'src'},  # Specify the source directory
    packages=find_packages(where='src'),  # Look for packages in 'src'
    install_requires=[
        # List your dependencies here
        'pydantic[email]~=2.5',
        'python-dateutil~=2.8',
        'pytest~=7.1',
        'pandas==2.2.1',
        'ipulse_shared_base_ftredge~=12.2.0',
    ],
    author='russlan.ramdowar',
    description='Shared AI models for the Pulse platform project. Using AI for financial advisory and investment management.',
    url='https://github.com/TheFutureEdge/ipulse_shared_ai',
)