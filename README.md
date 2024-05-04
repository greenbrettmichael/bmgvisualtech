# ABOUT

BMGVisualTech website currently just starting off with a WebGL example for future content.

## How to Build

Only linux for now!

System Dependencies:
- git
- python3
- cmake
- make
- ninja

```sh
sudo apt-get install libgl1-mesa-dev libegl1-mesa-dev mesa-common-dev xorg-dev libasound-dev
sudo apt-get install ninja-build
./fips setup emscripten
python3 fips emsdk install latest
```

To configure and build with fips (will probably remove fips dependency):

```sh
./fips set config sapp-webgl2-wasm-ninja-release
./fips build

```