# Python Pokédex

A Pokédex application developed in Python 3.11.14 using the **Kivy** framework for building cross-platform graphical user interfaces, with data dynamically fetched from the **PokeAPI**—a free and comprehensive RESTful API for Pokémon game data.

## Description

This project is a desktop Pokédex application that allows users to search, browse, and view detailed information about Pokémon species. It leverages the **Kivy** framework—an open-source Python library for rapid development of applications that make use of innovative user interfaces, including multi-touch apps—to create an interactive and visually engaging experience. All Pokémon data is retrieved in real-time from the **PokeAPI**, a reliable and extensive public API that provides structured information on Pokémon games, species, moves, types, and more.

## Main Technologies

- **Python 3.11.14**
- **Kivy** – Cross-platform Python framework for GUI development
- **PokeAPI** – RESTful API for Pokémon game data
- **Requests** – HTTP library for API communication
- **Pillow** – Image processing support
- **PyGlet** & **Arcade** – Multimedia and game libraries (used by Kivy dependencies)
- **Pymunk** – Physics engine (optional, for advanced interactions)
- **UV** – Fast Python package installer and resolver

## Installation and Usage

### Prerequisites

- Python 3.11.14 installed on your system
- [UV](https://docs.astral.sh/uv/) installed (modern Python package manager)

### Running the Application

1. **Clone the repository**
   ```bash
   git clone https://github.com/danielmgmora/pokedex-kivy-python.git
   cd pokedex-kivy-python

2. **Create and activate a virtual environment with UV**
    ```bash
    # Create virtual environment
    uv venv
    
    # Activate (Windows)
    .venv\Scripts\activate
    
    # Activate (Linux/macOS)
    source .venv/bin/activate

3. **Install dependencies with UV**
    ```bash
    uv pip install -r requirements.txt

4. **Run the main application**
    ```bash
    python main.py

## Building Executables

To create standalone executables for different operating systems, you can use PyInstaller. Note that building for each OS typically requires running the build process on that specific OS (or using cross-compilation tools).

### Installation and Setup for Building

1. **Install PyInstaller with UV**
    ```bash
    uv pip install pyinstaller

2. **Ensure all dependencies are installed**
    ```bash
    uv pip install -r requirements.txt

### Building for Different Platforms

1. Windows
    ```bash
    pyinstaller --onefile --windowed --name "PythonPokedex" main.py

2. Linux
    ```bash
    pyinstaller --onefile --name "python-pokedex" main.py

3. macOS 
    ```bash
    pyinstaller --onefile --windowed --name "PythonPokedex" main.py

## Platform-Specific Notes

### Windows:
- The executable will be created in the dist folder
- You might need to install Microsoft Visual C++ Redistributable on target machines

#### Linux:
- Ensure all dependencies are installed on the target system
- You may need to use --add-data flag for resource files

#### macOS:
- You may need to codesign the app for distribution
- Consider using --osx-bundle-identifier for proper app bundling

## Advanced PyInstaller Configuration

- For a more robust build configuration, create a .spec file:
    ```bash
    pyinstaller --onefile --windowed --add-data "assets:assets" --icon="icon.ico" main.py

- Then modify the generated .spec file to include Kivy dependencies properly:
    ```python
    # -*- mode: python ; coding: utf-8 -*-

    a = Analysis(['main.py'],
                 pathex=[],
                 binaries=[],
                 datas=[('assets', 'assets')],  # Include assets folder
                 hiddenimports=['kivy', 'requests', 'PIL'],  # Explicitly import modules
                 hookspath=[],
                 runtime_hooks=[],
                 excludes=[],
                 win_no_prefer_redirects=False,
                 win_private_assemblies=False,
                 cipher=None,
                 noarchive=False)
    pyz = PYZ(a.pure, a.zipped_data,
                 cipher=None)
    
    exe = EXE(pyz,
              a.scripts,
              [],
              exclude_binaries=True,
              name='PythonPokedex',
              debug=False,
              bootloader_ignore_signals=False,
              strip=False,
              upx=True,
              console=False,  # Set to True for debugging
              icon='icon.ico')
    
    coll = COLLECT(exe,
                   a.binaries,
                   a.zipfiles,
                   a.datas,
                   strip=False,
                   upx=True,
                   upx_exclude=[],
                   name='PythonPokedex')

## Alternative: Using Buildozer (for Android/iOS)

- For mobile platforms, consider using Buildozer:
    ```bash
    # Install Buildozer with UV
    uv pip install buildozer
    
    # Initialize buildozer.spec
    buildozer init
    
    # Edit buildozer.spec with your configuration
    # Then build for Android
    buildozer android debug
    
    # Or for iOS (requires macOS and Xcode)
    buildozer ios debug

# Troubleshooting

## Common Issues

1. **Missing dependencies:** Ensure all packages in requirements.txt are installed with UV
2. **Kivy installation problems:** Refer to [Kivy's official documentation]((https://kivy.org/doc/stable/gettingstarted/installation.html))
3. **API rate limiting:** PokeAPI has rate limits; consider implementing caching
4. **Executable size:** PyInstaller bundles many files; use UPX compression to reduce size
5. **UV environment issues:** Make sure you're using the correct Python version with uv python --version

## Getting Help

If you encounter issues:

- Check the logs/ directory for error logs
- Ensure your Python version matches (3.11.14)
- Verify all dependencies are correctly installed with uv pip list
- Check UV's virtual environment is activated

## Development with UV

- This project uses UV for fast and reliable dependency management. Key UV commands:
    ```bash
    # Create new virtual environment
    uv venv
    
    # Install dependencies
    uv pip install -r requirements.txt
    
    # Add new dependency
    uv pip install package-name
    
    # Update all dependencies
    uv pip compile --upgrade requirements.txt
    
    # Sync environment
    uv pip sync requirements.txt

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](https://license/) file for details.

Pokémon data disclaimer: This application uses data from the [PokeAPI](https://pokeapi.co/). Pokémon and Pokémon character names are trademarks of Nintendo. This project is not affiliated with, endorsed, or sponsored by Nintendo, The Pokémon Company, or PokeAPI.

## Acknowledgments
- [Kivy Team](https://kivy.org/) for the excellent GUI framework
- [PokeAPI](https://pokeapi.co/) for providing comprehensive Pokémon data
- [UV Project](https://docs.astral.sh/uv/) for the fast Python package manager
- All contributors and testers of this project
