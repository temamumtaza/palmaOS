#!/bin/bash
#
# Palma OS ISO Build Script
# Based on live-build system
# Robust version with comprehensive error handling
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="palmaOS"
VERSION="1.0.0-alpha"
ARCH="amd64"
UBUNTU_CODENAME="noble"  # Ubuntu 24.04 LTS
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/output"
CONFIG_DIR="$SCRIPT_DIR/config"
CHROOT="$OUTPUT_DIR/chroot"

print_banner() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                     PALMA OS BUILDER                      ║"
    echo "║        Hidupkan Kembali, Produktifkan Indonesia          ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo "Version: $VERSION"
    echo "Architecture: $ARCH"
    echo "Base: Ubuntu $UBUNTU_CODENAME (24.04 LTS)"
    echo ""
}

check_dependencies() {
    echo -e "${YELLOW}[*] Checking dependencies...${NC}"
    
    DEPS="debootstrap squashfs-tools xorriso grub-pc-bin grub-efi-amd64-bin mtools"
    MISSING=""
    
    for dep in $DEPS; do
        if ! dpkg -l | grep -q "^ii  $dep"; then
            MISSING="$MISSING $dep"
        fi
    done
    
    if [ -n "$MISSING" ]; then
        echo -e "${RED}[!] Missing dependencies:$MISSING${NC}"
        echo "Run: sudo apt install$MISSING"
        exit 1
    fi
    
    echo -e "${GREEN}[✓] All dependencies installed${NC}"
}

# Robust mount function for chroot
mount_chroot() {
    echo -e "${YELLOW}[*] Mounting chroot filesystems...${NC}"
    
    # Create directories if not exist
    mkdir -p "$CHROOT/dev"
    mkdir -p "$CHROOT/dev/pts"
    mkdir -p "$CHROOT/proc"
    mkdir -p "$CHROOT/sys"
    mkdir -p "$CHROOT/run"
    
    # Mount in correct order with error suppression for already mounted
    mount --bind /dev "$CHROOT/dev" 2>/dev/null || true
    mount -t devpts devpts "$CHROOT/dev/pts" -o gid=5,mode=620 2>/dev/null || true
    mount -t proc proc "$CHROOT/proc" 2>/dev/null || true
    mount -t sysfs sysfs "$CHROOT/sys" 2>/dev/null || true
    mount --bind /run "$CHROOT/run" 2>/dev/null || true
    
    # Create essential device nodes if bind mount failed
    if [ ! -c "$CHROOT/dev/null" ]; then
        mknod -m 666 "$CHROOT/dev/null" c 1 3 2>/dev/null || true
    fi
    if [ ! -c "$CHROOT/dev/zero" ]; then
        mknod -m 666 "$CHROOT/dev/zero" c 1 5 2>/dev/null || true
    fi
    if [ ! -c "$CHROOT/dev/random" ]; then
        mknod -m 666 "$CHROOT/dev/random" c 1 8 2>/dev/null || true
    fi
    if [ ! -c "$CHROOT/dev/urandom" ]; then
        mknod -m 666 "$CHROOT/dev/urandom" c 1 9 2>/dev/null || true
    fi
    if [ ! -c "$CHROOT/dev/tty" ]; then
        mknod -m 666 "$CHROOT/dev/tty" c 5 0 2>/dev/null || true
    fi
    if [ ! -c "$CHROOT/dev/console" ]; then
        mknod -m 600 "$CHROOT/dev/console" c 5 1 2>/dev/null || true
    fi
    if [ ! -c "$CHROOT/dev/ptmx" ]; then
        mknod -m 666 "$CHROOT/dev/ptmx" c 5 2 2>/dev/null || true
    fi
    
    echo -e "${GREEN}[✓] Chroot filesystems mounted${NC}"
}

# Robust unmount function for chroot
umount_chroot() {
    echo -e "${YELLOW}[*] Unmounting chroot filesystems...${NC}"
    
    # Unmount in reverse order with lazy unmount
    umount -lf "$CHROOT/dev/pts" 2>/dev/null || true
    umount -lf "$CHROOT/dev" 2>/dev/null || true
    umount -lf "$CHROOT/proc" 2>/dev/null || true
    umount -lf "$CHROOT/sys" 2>/dev/null || true
    umount -lf "$CHROOT/run" 2>/dev/null || true
    
    echo -e "${GREEN}[✓] Chroot filesystems unmounted${NC}"
}

# Run command in chroot without PTY requirement
run_in_chroot() {
    DEBIAN_FRONTEND=noninteractive chroot "$CHROOT" "$@"
}

clean_build() {
    echo -e "${YELLOW}[*] Cleaning previous build...${NC}"
    
    # Unmount any existing mounts first
    umount_chroot 2>/dev/null || true
    
    rm -rf "$OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
    echo -e "${GREEN}[✓] Clean complete${NC}"
}

create_base_system() {
    echo -e "${YELLOW}[*] Creating base Ubuntu system...${NC}"
    
    debootstrap \
        --arch=$ARCH \
        --variant=minbase \
        --include=gpgv,gnupg,ca-certificates,locales \
        $UBUNTU_CODENAME \
        "$CHROOT" \
        http://archive.ubuntu.com/ubuntu
    
    echo -e "${GREEN}[✓] Base system created${NC}"
}

configure_chroot() {
    echo -e "${YELLOW}[*] Configuring chroot environment...${NC}"
    
    # Mount filesystems
    mount_chroot
    
    # Copy DNS config
    cp /etc/resolv.conf "$CHROOT/etc/resolv.conf" 2>/dev/null || true
    
    # Set hostname
    echo "palmaos" > "$CHROOT/etc/hostname"
    
    # Configure apt sources
    cat > "$CHROOT/etc/apt/sources.list" << EOF
deb http://archive.ubuntu.com/ubuntu $UBUNTU_CODENAME main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu $UBUNTU_CODENAME-updates main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu $UBUNTU_CODENAME-security main restricted universe multiverse
EOF
    
    # Set default locale
    echo "en_US.UTF-8 UTF-8" > "$CHROOT/etc/locale.gen"
    echo "id_ID.UTF-8 UTF-8" >> "$CHROOT/etc/locale.gen"
    run_in_chroot locale-gen || true
    
    # Update package lists
    run_in_chroot apt-get update || true
    
    echo -e "${GREEN}[✓] Chroot configured${NC}"
}

install_packages() {
    echo -e "${YELLOW}[*] Installing packages...${NC}"
    
    # Ensure mounts are active
    mount_chroot
    
    # Update and install packages
    run_in_chroot apt-get update || true
    
    # Install core packages in batches to avoid timeout
    echo -e "${YELLOW}[*] Installing base system packages...${NC}"
    run_in_chroot apt-get install -y --no-install-recommends \
        linux-image-generic \
        live-boot \
        systemd-sysv \
        dbus \
        sudo \
        locales \
        wget \
        curl
    
    echo -e "${YELLOW}[*] Installing desktop environment...${NC}"
    run_in_chroot apt-get install -y --no-install-recommends \
        xorg \
        xfce4 \
        xfce4-goodies \
        lightdm \
        lightdm-gtk-greeter
    
    echo -e "${YELLOW}[*] Installing network and audio...${NC}"
    run_in_chroot apt-get install -y --no-install-recommends \
        network-manager \
        network-manager-gnome \
        pulseaudio \
        pavucontrol
    
    echo -e "${YELLOW}[*] Installing applications...${NC}"
    run_in_chroot apt-get install -y --no-install-recommends \
        firefox \
        evince \
        thunar \
        mousepad \
        file-roller \
        ristretto \
        fonts-noto
    
    echo -e "${YELLOW}[*] Installing Python and development tools...${NC}"
    run_in_chroot apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-pyqt6 \
        sqlite3
    
    echo -e "${YELLOW}[*] Installing office suite (LibreOffice)...${NC}"
    run_in_chroot apt-get install -y --no-install-recommends \
        libreoffice-writer \
        libreoffice-calc \
        libreoffice-impress || echo "LibreOffice installation had issues, continuing..."
    
    # Set Indonesian locale
    run_in_chroot locale-gen id_ID.UTF-8 || true
    run_in_chroot update-locale LANG=id_ID.UTF-8 || true
    
    echo -e "${GREEN}[✓] Packages installed${NC}"
}

install_palma_apps() {
    echo -e "${YELLOW}[*] Installing Palma apps...${NC}"
    
    # Copy Palma apps to /opt/palma-apps
    mkdir -p "$CHROOT/opt/palma-apps"
    cp -r "$SCRIPT_DIR/../apps/"* "$CHROOT/opt/palma-apps/" 2>/dev/null || true
    
    # Copy desktop files
    mkdir -p "$CHROOT/usr/share/applications"
    cp "$CONFIG_DIR/desktop-files/"*.desktop "$CHROOT/usr/share/applications/" 2>/dev/null || true
    
    # Install app dependencies via pip
    run_in_chroot pip3 install --break-system-packages \
        PyQt6 \
        jinja2 \
        weasyprint \
        qrcode \
        pillow || echo "Some pip packages failed, continuing..."
    
    echo -e "${GREEN}[✓] Palma apps installed${NC}"
}

configure_desktop() {
    echo -e "${YELLOW}[*] Configuring XFCE desktop...${NC}"
    
    # Copy custom themes
    mkdir -p "$CHROOT/usr/share/themes/"
    cp -r "$SCRIPT_DIR/../themes/palma-glass" "$CHROOT/usr/share/themes/" 2>/dev/null || true
    
    # Copy wallpapers
    mkdir -p "$CHROOT/usr/share/backgrounds/palma/"
    cp "$SCRIPT_DIR/../assets/wallpapers/"* "$CHROOT/usr/share/backgrounds/palma/" 2>/dev/null || true
    
    # Create skel config
    mkdir -p "$CHROOT/etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/"
    
    echo -e "${GREEN}[✓] Desktop configured${NC}"
}

create_user() {
    echo -e "${YELLOW}[*] Creating default user...${NC}"
    
    # Create user without PTY
    run_in_chroot useradd -m -s /bin/bash -G sudo palma || true
    echo "palma:palma" | run_in_chroot chpasswd
    
    # Allow sudo without password for palma user
    echo "palma ALL=(ALL) NOPASSWD:ALL" > "$CHROOT/etc/sudoers.d/palma"
    chmod 440 "$CHROOT/etc/sudoers.d/palma"
    
    # Auto-login configuration
    mkdir -p "$CHROOT/etc/lightdm/lightdm.conf.d/"
    cat > "$CHROOT/etc/lightdm/lightdm.conf.d/autologin.conf" << EOF
[Seat:*]
autologin-user=palma
autologin-user-timeout=0
EOF
    
    echo -e "${GREEN}[✓] User created${NC}"
}

cleanup_chroot() {
    echo -e "${YELLOW}[*] Cleaning up chroot...${NC}"
    
    # Clean apt cache
    run_in_chroot apt-get clean || true
    run_in_chroot apt-get autoremove -y || true
    
    # Remove temporary files
    rm -rf "$CHROOT/tmp/"*
    rm -rf "$CHROOT/var/tmp/"*
    rm -f "$CHROOT/etc/resolv.conf"
    
    # Unmount filesystems
    umount_chroot
    
    echo -e "${GREEN}[✓] Cleanup complete${NC}"
}

create_iso() {
    echo -e "${YELLOW}[*] Creating ISO image...${NC}"
    
    ISO_DIR="$OUTPUT_DIR/iso"
    
    mkdir -p "$ISO_DIR/live"
    mkdir -p "$ISO_DIR/boot/grub"
    
    # Create squashfs
    echo -e "${YELLOW}[*] Creating squashfs (this may take a while)...${NC}"
    mksquashfs "$CHROOT" "$ISO_DIR/live/filesystem.squashfs" \
        -comp xz -Xbcj x86 -b 1M
    
    # Copy kernel and initrd
    cp "$CHROOT/boot/vmlinuz-"* "$ISO_DIR/live/vmlinuz" 2>/dev/null || {
        echo -e "${RED}[!] No kernel found, using fallback...${NC}"
        cp "$CHROOT/boot/vmlinuz" "$ISO_DIR/live/vmlinuz" 2>/dev/null || true
    }
    cp "$CHROOT/boot/initrd.img-"* "$ISO_DIR/live/initrd" 2>/dev/null || {
        echo -e "${RED}[!] No initrd found, using fallback...${NC}"
        cp "$CHROOT/boot/initrd.img" "$ISO_DIR/live/initrd" 2>/dev/null || true
    }
    
    # Create GRUB config
    cat > "$ISO_DIR/boot/grub/grub.cfg" << EOF
set timeout=5
set default=0

insmod all_video

menuentry "Palma OS Live" {
    linux /live/vmlinuz boot=live quiet splash
    initrd /live/initrd
}

menuentry "Palma OS (Safe Mode)" {
    linux /live/vmlinuz boot=live nomodeset
    initrd /live/initrd
}

menuentry "Palma OS (RAM Mode - Copy to RAM)" {
    linux /live/vmlinuz boot=live toram quiet splash
    initrd /live/initrd
}
EOF
    
    # Create ISO
    echo -e "${YELLOW}[*] Generating ISO file...${NC}"
    grub-mkrescue -o "$OUTPUT_DIR/$PROJECT_NAME-$VERSION.iso" "$ISO_DIR"
    
    # Generate checksums
    cd "$OUTPUT_DIR"
    sha256sum "$PROJECT_NAME-$VERSION.iso" > "$PROJECT_NAME-$VERSION.iso.sha256"
    
    echo -e "${GREEN}[✓] ISO created: $OUTPUT_DIR/$PROJECT_NAME-$VERSION.iso${NC}"
}

# Trap to ensure cleanup on exit
cleanup_on_exit() {
    echo -e "${YELLOW}[*] Cleaning up on exit...${NC}"
    umount_chroot 2>/dev/null || true
}
trap cleanup_on_exit EXIT

# Main execution
main() {
    print_banner
    
    if [ "$1" == "--test" ]; then
        echo -e "${YELLOW}[*] Running in test mode (dry run)${NC}"
        check_dependencies
        echo -e "${GREEN}[✓] Test passed - ready to build${NC}"
        exit 0
    fi
    
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}[!] Please run as root: sudo $0${NC}"
        exit 1
    fi
    
    # Export for chroot commands
    export DEBIAN_FRONTEND=noninteractive
    export LC_ALL=C
    
    check_dependencies
    clean_build
    create_base_system
    configure_chroot
    install_packages
    install_palma_apps
    configure_desktop
    create_user
    cleanup_chroot
    create_iso
    
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    BUILD COMPLETE!                        ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "ISO Location: $OUTPUT_DIR/$PROJECT_NAME-$VERSION.iso"
    echo "SHA256: $(cat $OUTPUT_DIR/$PROJECT_NAME-$VERSION.iso.sha256)"
    echo ""
}

main "$@"
