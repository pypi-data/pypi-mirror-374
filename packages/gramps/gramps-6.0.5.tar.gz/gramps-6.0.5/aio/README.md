The files in this directory are used to build the Gramps Windows AIO (All In One) installer.

To build AIO for the master branch :

1. Install MSYS2
    * Download MSYS2 from <https://www.msys2.org/> .
    * Install with default options. 
    * From the Start menu, run "MSYS2 MINGW64"
    * Upgrade system : ` pacman -Syuu --noconfirm `  (twice if the first run closes msys2).

2. Install Git, if not already installed
```
pacman -S git --noconfirm
```

3. Download Gramps sources from github :

```
git clone https://github.com/gramps-project/gramps.git
```

4. Build AIO :

```
cd gramps/aio
./build.sh
```
To capture the full output of the build, use `./build.sh >& build_log.txt`

The resulting AIO installer is in `gramps/aio/mingw64/src/GrampsAIO-[appversion]-[appbuild]-[hash]_win64.exe`

The python virtual environment created during build (`c:\msys64\tmp\grampspythonenv\bin\python.exe` by default) can then be configured in Visual Studio Code and used to debug etc.

To delete the python virtual environment at the end of the build, call ```./build.sh true```. This can be useful when testing the build script.