# vica-laya runtime

Build source for `vica-laya`, the standalone program that runs the Vica Laya model. Each platform
gets one download that holds the program, the model `vica-laya.gguf` and the license files. The
downloads are published with the model on Hugging Face (`tory-labs/vica-laya`).

| Platform | GPU backend | Download | Needs on the computer |
|---|---|---|---|
| macOS arm64 | Metal | `vica-laya-macos-arm64.tar.gz` | nothing else |
| Linux x86_64 | Vulkan | `vica-laya-linux-x86_64.tar.gz` | Vulkan loader (`libvulkan.so.1`); built on Ubuntu 22.04 (glibc 2.35) |
| Windows x86_64 | Vulkan | `vica-laya-windows-x86_64.zip` | Vulkan loader (`vulkan-1.dll`, installed with GPU drivers) |

`--device auto` uses the GPU when one is available and falls back to CPU otherwise. The Windows
download carries the Microsoft Visual C++ runtime DLLs next to `vica-laya.exe`.

## Build

GitHub Actions (`.github/workflows/build.yml`) builds the three platforms, renames the published
model to `vica-laya`, and packs the downloads with `SHA256SUMS` as workflow artifacts. Pushing a `v*`
tag also attaches them to a GitHub release.

Linux and Windows builds drop OpenMP; Linux also links libstdc++ and libgcc statically. Windows keeps
the shared Visual C++ runtime because a static one changed CPU probabilities by up to 0.032. Each run
compares fixed CPU decisions and CPU speed with an upstream-style reference build; any changed
decision fails the run.

Local build (macOS; Linux and Windows flags are in the workflow matrix):

```sh
cmake -S ggmlc -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DGGMLC_ENABLE_METAL=ON -DGGML_NATIVE=OFF -DGGMLC_BUILD_EXAMPLES=ON
cmake --build build --target laya
cp build/examples/laya/laya vica-laya
```

`scripts/rename_gguf.py` gives a model GGUF the `vica-laya` name and removes local paths from its
metadata. It leaves tensors and decision settings unchanged and checks that before exiting.

## Source and licenses

`ggmlc/` is an unmodified snapshot of [ggmlc](https://github.com/monatis/ggmlc) v0.9.7, commit
`5490a13661d95add025ec1b111adbc88234a9b4f`, by monatis and contributors. ggmlc declares the MIT
License in its README and `pyproject.toml`. It includes [ggml](https://github.com/ggml-org/ggml), MIT
License, `ggmlc/third_party/ggml/LICENSE`. The runner's built-in help still uses upstream wording.
