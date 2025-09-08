# APK-Patchx

A powerful command-line tool for Android APK manipulation, including Frida gadget injection, APK decoding/building, and package management.

## Features

- **APK Management**: Pull, decode, build, and sign APK files
- **Frida Integration**: Inject Frida gadgets for runtime manipulation
- **Split APK Support**: Automatically merge split APKs into single files
- **Package Renaming**: Change APK package names
- **Auto-bootstrap**: Automatically downloads and manages required tools

## Installation

```bash
pip install apk_patchx
```

## Usage

### Pull APK from device
```bash
apk_patchx pull com.example.app
```

### Decode APK
```bash
apk_patchx decode app.apk
```

### Build APK from source
```bash
apk_patchx build app_src/
```

### Patch APK with Frida gadget
```bash
apk_patchx patch app.apk --arch arm64
```

### Rename APK package
```bash
apk_patchx rename app.apk com.newpackage.name
```

### Sign APK
```bash
apk_patchx sign app.apk
```

## Architecture Support

- ARM (`arm`)
- ARM64 (`arm64`) 
- x86 (`x86`)
- x86_64 (`x86_64`)

## Requirements

- Python 3.8+
- Java Runtime Environment (JRE 8+)
- ADB (for device operations)

## Tool Management

APK-Patchx automatically downloads and manages required tools in `~/.apk_patchx/tools/`:

- apktool
- Android SDK build-tools
- Platform tools (adb)
- dexpatch
- Frida gadgets

## License

MIT License - see LICENSE file for details.
