"""
.. See the NOTICE file distributed with this work for additional information
   regarding copyright ownership.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from setupagents import setup, find_packages

setup(
    name='openvre-agent-api',

    version='0.5.6',
    description='OpenVRE (previously known as MuG) Agent API',

    url='http://www.bsc.es',
    download_url='https://github.com/inab/openvre-agent-api',

    author='Laura Rodríguez, José Mª Fernández, Marco Pasi, Javier Conejero',
    author_email='',

    license='Apache-2.0',

    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'configparser', 'pytest'
    ],
    setup_requires=[
        'pytest-runner',
    ],

    tests_require=[
        'pytest',
    ],
)
