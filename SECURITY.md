# Security Policy - Palma OS

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in Palma OS, please report it responsibly:

1. **DO NOT** create a public GitHub issue
2. Email security concerns to: security@palmaos.id (or maintainer email)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

| Action | Timeframe |
|--------|-----------|
| Acknowledgment | 48 hours |
| Initial Assessment | 7 days |
| Fix Implementation | 30 days |
| Public Disclosure | After fix released |

## Security Measures

### Application Security

- **Static Analysis**: All code scanned with Bandit before merge
- **Dependency Scanning**: Safety checks for known vulnerabilities
- **Input Validation**: All user inputs sanitized
- **SQL Injection Prevention**: Parameterized queries only

### System Security

- **Palma Guard**: Built-in USB security tool
  - Auto-blocks autorun.inf
  - USB drive scanning
  - Quarantine for threats
  
- **Minimal Attack Surface**: 
  - No unnecessary services
  - Firewall enabled by default
  - No telemetry or data collection

### Data Security

- **Local-First**: All data stored locally, no cloud sync
- **Encryption**: Support for encrypted home directories
- **Backup**: Integrated backup tool (Gudang Benih)

## Security Hardening

Palma OS includes these hardening measures:

1. **AppArmor** profiles for sensitive apps
2. **Automatic security updates** (optional)
3. **Secure boot** support (UEFI)
4. **Password policies** enforced

## Compliance

This project aims to comply with:

- **ISO/IEC 27001** - Information Security Management
- **OWASP** - Secure Development Guidelines
- **CIS Benchmarks** - Ubuntu hardening

## Third-Party Dependencies

All dependencies are:
- Sourced from official repositories
- Verified with checksums
- Listed in Software Bill of Materials (SBOM)

---

*Last Updated: 2026-02-01*
