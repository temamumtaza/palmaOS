# Palma OS Build Environment
FROM ubuntu:24.04

LABEL maintainer="Palma OS Team"
LABEL description="Build environment for Palma OS ISO"

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    debootstrap \
    squashfs-tools \
    xorriso \
    grub-pc-bin \
    grub-efi-amd64-bin \
    mtools \
    dosfstools \
    isolinux \
    syslinux-utils \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy build scripts
COPY build/ /build/build/
COPY apps/ /build/apps/
COPY themes/ /build/themes/
COPY assets/ /build/assets/

# Make build script executable
RUN chmod +x /build/build/build.sh

# Entry point
ENTRYPOINT ["/build/build/build.sh"]
