FROM nvidia/cuda:11.5.1-cudnn8-devel-ubuntu20.04

RUN apt-get update && \ 
DEBIAN_FRONTEND=noninteractive apt-get install -y git cmake g++ protobuf-compiler libgoogle-glog-dev libopencv-dev libboost-all-dev libhdf5-dev libatlas-base-dev python3-dev python3-pip
RUN pip3 install numpy opencv-python

#Get openpose source files
RUN git clone https://github.com/CMU-Perceptual-Computing-Lab/openpose
WORKDIR /openpose/
RUN git submodule update --init --recursive --remote

RUN mkdir build
WORKDIR /openpose/build/

#cmake build with generator "Unix Makefiles" and build for python support
RUN cmake .. -G "Unix Makefiles" -DBUILD_PYTHON=ON 
RUN cmake --build . --config Release

#Install openpose globally
RUN make -j`nproc`
RUN make install

ENTRYPOINT [ "tail", "-f", "/dev/null" ]