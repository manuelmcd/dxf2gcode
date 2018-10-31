# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
#
# A docker container to build and run dxf2gcode for linux.
# To build the container - assuming you have docker installed and
# configured - from the top-level directory (containing this Dockerfile)
# run:
#   docker build -t dxf2gcode:latest .
# (Use --build-arg to set http_proxy & https_proxy if required).
#
# To run, assuming that your DXF input files are in the current
# directory:
#   xhost +localhost
#   docker run -ti --net=host -e DISPLAY \
#     -v $HOME/.Xauthority:/root/.Xauthority:rw -v $(pwd):$(pwd):rw \
#     -w $(pwd) dxf2gcode:latest
#

FROM python:3.6.7-stretch

RUN apt-get update && apt-get install -y qttools5-dev qttools5-dev-tools pstoedit poppler-utils
# Feels like I'm missing something having to make this symlink
RUN ln -s /usr/lib/x86_64-linux-gnu/qt5/bin/lrelease /usr/bin/lrelease-qt5
RUN pip install PyQt5 PyOpenGL setuptools

WORKDIR /tmp/dxf2gcode_install
ADD . .
WORKDIR source
RUN python3 make_tr.py
RUN python3 make_py_uic.py
RUN python3 st-setup.py build && python3 st-setup.py install

CMD dxf2gcode
