FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV SUDO_USER=root

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    ninja-build \
    git \
    sudo \
    curl \
    python3 \
    python3-pip \
    tcl-dev \
    swig \
    flex \
    bison \
    libboost-all-dev \
    libgflags-dev \
    libeigen3-dev \
    libspdlog-dev \
    libyaml-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt

RUN git clone --recursive https://github.com/ieee-ceda-datc/Robust-Design-Flow.git

RUN git -C Robust-Design-Flow submodule sync --recursive \
    && git -C Robust-Design-Flow submodule update --init --recursive

WORKDIR /opt/Robust-Design-Flow/tools/OpenROAD-flow-scripts

RUN ./setup.sh
RUN ./build_openroad.sh --local



ENV PATH="/opt/Robust-Design-Flow/tools/OpenROAD-flow-scripts/tools/install/OpenROAD/bin:\
/opt/Robust-Design-Flow/tools/OpenROAD-flow-scripts/tools/install/yosys/bin:${PATH}"

ENV LD_LIBRARY_PATH="/opt/Robust-Design-Flow/tools/OpenROAD-flow-scripts/tools/install/OpenROAD/lib:\
/opt/Robust-Design-Flow/tools/OpenROAD-flow-scripts/dependencies/lib"


ENV XDG_RUNTIME_DIR=/tmp/runtime-root

RUN python3 -m pip install --no-cache-dir --break-system-packages \
    unittest-xml-reporting \
    pyyaml

WORKDIR /workspace

