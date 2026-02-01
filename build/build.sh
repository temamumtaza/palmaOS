#!/bin/bash
#
# Palma OS ISO Build Script
# Based on live-build system
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
OUTPUT_DIR="$(dirname $0)/output"
CONFIG_DIR="$(dirname $0)/config"

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

clean_build() {
    echo -e "${YELLOW}[*] Cleaning previous build...${NC}"
    rm -rf "$OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
    echo -e "${GREEN}[✓] Clean complete${NC}"
}

create_base_system() {
    echo -e "${YELLOW}[*] Creating base Ubuntu system...${NC}"
    
    CHROOT="$OUTPUT_DIR/chroot"
    
    sudo debootstrap \
        --arch=$ARCH \
        --variant=minbase \
        $UBUNTU_CODENAME \
        "$CHROOT" \
        http://archive.ubuntu.com/ubuntu
    
    echo -e "${GREEN}[✓] Base system created${NC}"
}

configure_chroot() {
    echo -e "${YELLOW}[*] Configuring chroot environment...${NC}"
    
    CHROOT="$OUTPUT_DIR/chroot"
    
    # Create essential device nodes if missing
    sudo mkdir -p "$CHROOT/dev"
    sudo mknod -m 666 "$CHROOT/dev/null" c 1 3 2>/dev/null || true
    sudo mknod -m 666 "$CHROOT/dev/zero" c 1 5 2>/dev/null || true
    sudo mknod -m 666 "$CHROOT/dev/random" c 1 8 2>/dev/null || true
    sudo mknod -m 666 "$CHROOT/dev/urandom" c 1 9 2>/dev/null || true
    sudo mknod -m 666 "$CHROOT/dev/tty" c 5 0 2>/dev/null || true
    sudo mknod -m 600 "$CHROOT/dev/console" c 5 1 2>/dev/null || true
    
    # Mount necessary filesystems
    sudo mount --bind /dev "$CHROOT/dev"
    sudo mount --bind /dev/pts "$CHROOT/dev/pts" 2>/dev/null || true
    sudo mount --bind /run "$CHROOT/run"
    sudo mount -t proc proc "$CHROOT/proc"
    sudo mount -t sysfs sysfs "$CHROOT/sys"
    
    # Copy DNS config
    sudo cp /etc/resolv.conf "$CHROOT/etc/resolv.conf"
    
    # Set hostname
    echo "palmaos" | sudo tee "$CHROOT/etc/hostname"
    
    # Configure apt sources
    sudo tee "$CHROOT/etc/apt/sources.list" > /dev/null << EOF
deb http://archive.ubuntu.com/ubuntu $UBUNTU_CODENAME main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu $UBUNTU_CODENAME-updates main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu $UBUNTU_CODENAME-security main restricted universe multiverse
EOF
    
    # Install essential packages first (gpgv for apt signature verification)
    echo -e "${YELLOW}[*] Installing essential packages...${NC}"
    sudo chroot "$CHROOT" apt-get update --allow-insecure-repositories || true
    sudo chroot "$CHROOT" apt-get install -y --allow-unauthenticated gpgv gnupg apt-transport-https ca-certificates
    
    echo -e "${GREEN}[✓] Chroot configured${NC}"
}

install_packages() {
    echo -e "${YELLOW}[*] Installing packages...${NC}"
    
    CHROOT="$OUTPUT_DIR/chroot"
    
    # Remount /dev to ensure device nodes are available
    sudo mount --bind /dev "$CHROOT/dev" 2>/dev/null || true
    sudo mount --bind /dev/pts "$CHROOT/dev/pts" 2>/dev/null || true
    
    sudo chroot "$CHROOT" apt-get update || true
    
    # Install core packages (without OnlyOffice first)
    sudo chroot "$CHROOT" apt-get install -y --no-install-recommends \
        linux-image-generic \
        live-boot \
        systemd-sysv \
        network-manager \
        xfce4 \
        xfce4-goodies \
        lightdm \
        lightdm-gtk-greeter \
        xorg \
        firefox \
        evince \
        thunar \
        mousepad \
        file-roller \
        ristretto \
        python3 \
        python3-pip \
        python3-pyqt6 \
        sqlite3 \
        fonts-noto \
        pulseaudio \
        pavucontrol \
        network-manager-gnome \
        sudo \
        locales \
        wget \
        gnupg \
        ca-certificates \
        libreoffice-writer \
        libreoffice-calc \
        libreoffice-impress
    
    # Try to install OnlyOffice (optional - requires repo)
    echo -e "${YELLOW}[*] Attempting OnlyOffice installation...${NC}"
    sudo chroot "$CHROOT" bash -c '
        wget -qO - https://download.onlyoffice.com/GPG-KEY-ONLYOFFICE | gpg --dearmor > /usr/share/keyrings/onlyoffice.gpg
        echo "deb [signed-by=/usr/share/keyrings/onlyoffice.gpg] https://download.onlyoffice.com/repo/debian squeeze main" > /etc/apt/sources.list.d/onlyoffice.list
        apt-get update
        apt-get install -y onlyoffice-desktopeditors || echo "OnlyOffice installation failed, using LibreOffice"
    ' || echo -e "${YELLOW}[!] OnlyOffice skipped, LibreOffice installed as fallback${NC}"
    
    # Set locale to Indonesian
    sudo chroot "$CHROOT" locale-gen id_ID.UTF-8
    sudo chroot "$CHROOT" update-locale LANG=id_ID.UTF-8
    
    echo -e "${GREEN}[✓] Packages installed${NC}"
}

install_palma_apps() {
    echo -e "${YELLOW}[*] Installing Palma apps...${NC}"
    
    CHROOT="$OUTPUT_DIR/chroot"
    
    # Copy Palma apps to /opt/palma-apps
    sudo mkdir -p "$CHROOT/opt/palma-apps"
    sudo cp -r "$(dirname $0)/../apps/"* "$CHROOT/opt/palma-apps/"
    
    # Copy desktop files
    sudo cp "$(dirname $0)/config/desktop-files/"*.desktop "$CHROOT/usr/share/applications/"
    
    # Install app dependencies
    sudo chroot "$CHROOT" pip3 install --break-system-packages \
        PyQt6 \
        jinja2 \
        weasyprint \
        qrcode \
        pillow
    
    echo -e "${GREEN}[✓] Palma apps installed${NC}"
}

configure_desktop() {
    echo -e "${YELLOW}[*] Configuring XFCE desktop...${NC}"
    
    CHROOT="$OUTPUT_DIR/chroot"
    
    # Copy custom themes
    sudo mkdir -p "$CHROOT/usr/share/themes/"
    sudo cp -r "$(dirname $0)/../themes/palma-glass" "$CHROOT/usr/share/themes/"
    
    # Copy wallpapers
    sudo mkdir -p "$CHROOT/usr/share/backgrounds/palma/"
    sudo cp "$(dirname $0)/../assets/wallpapers/"* "$CHROOT/usr/share/backgrounds/palma/"
    
    # Set default wallpaper and theme
    sudo mkdir -p "$CHROOT/etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/"
    
    echo -e "${GREEN}[✓] Desktop configured${NC}"
}

create_user() {
    echo -e "${YELLOW}[*] Creating default user...${NC}"
    
    CHROOT="$OUTPUT_DIR/chroot"
    
    sudo chroot "$CHROOT" useradd -m -s /bin/bash -G sudo palma
    echo "palma:palma" | sudo chroot "$CHROOT" chpasswd
    
    # Auto-login configuration
    sudo mkdir -p "$CHROOT/etc/lightdm/lightdm.conf.d/"
    sudo tee "$CHROOT/etc/lightdm/lightdm.conf.d/autologin.conf" > /dev/null << EOF
[Seat:*]
autologin-user=palma
autologin-user-timeout=0
EOF
    
    echo -e "${GREEN}[✓] User created${NC}"
}

cleanup_chroot() {
    echo -e "${YELLOW}[*] Cleaning up chroot...${NC}"
    
    CHROOT="$OUTPUT_DIR/chroot"
    
    # Clean apt cache
    sudo chroot "$CHROOT" apt-get clean
    sudo chroot "$CHROOT" apt-get autoremove -y
    
    # Unmount filesystems
    sudo chroot "$CHROOT" umount /dev/pts 2>/dev/null || true
    sudo chroot "$CHROOT" umount /sys 2>/dev/null || true
    sudo chroot "$CHROOT" umount /proc 2>/dev/null || true
    sudo umount "$CHROOT/run" 2>/dev/null || true
    sudo umount "$CHROOT/dev" 2>/dev/null || true
    
    echo -e "${GREEN}[✓] Cleanup complete${NC}"
}

create_iso() {
    echo -e "${YELLOW}[*] Creating ISO image...${NC}"
    
    CHROOT="$OUTPUT_DIR/chroot"
    ISO_DIR="$OUTPUT_DIR/iso"
    
    mkdir -p "$ISO_DIR/live"
    mkdir -p "$ISO_DIR/boot/grub"
    
    # Create squashfs
    sudo mksquashfs "$CHROOT" "$ISO_DIR/live/filesystem.squashfs" \
        -comp xz -Xbcj x86
    
    # Copy kernel and initrd
    sudo cp "$CHROOT/boot/vmlinuz-"* "$ISO_DIR/live/vmlinuz"
    sudo cp "$CHROOT/boot/initrd.img-"* "$ISO_DIR/live/initrd"
    
    # Create GRUB config
    cat > "$ISO_DIR/boot/grub/grub.cfg" << EOF
set timeout=5
set default=0

menuentry "Palma OS Live" {
    linux /live/vmlinuz boot=live quiet splash
    initrd /live/initrd
}

menuentry "Palma OS (Safe Mode)" {
    linux /live/vmlinuz boot=live nomodeset
    initrd /live/initrd
}
EOF
    
    # Create ISO
    grub-mkrescue -o "$OUTPUT_DIR/$PROJECT_NAME-$VERSION.iso" "$ISO_DIR"
    
    echo -e "${GREEN}[✓] ISO created: $OUTPUT_DIR/$PROJECT_NAME-$VERSION.iso${NC}"
}

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
    echo ""
}

main "$@"
