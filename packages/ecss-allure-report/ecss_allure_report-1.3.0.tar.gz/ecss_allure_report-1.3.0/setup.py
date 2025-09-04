from setuptools import find_packages, setup

DESCRIPTION = (
    'This is the simplest module for quick generate '
    'report message for Allure and send to ECSS Chat'
)


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='ecss_allure_report',
    version='1.3.0',
    author='maxstolpovskikh',
    author_email='maximstolpovskikh@gmail.com',
    description=DESCRIPTION,
    long_description=readme(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=['requests>=2.32.3', 'ecss-chat-client>=1.0.0'],
    classifiers=[
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    keywords='ecss_chat_client',
    python_requires='>=3.12.3',
)
