# vica-laya runtime

Build source for the `vica-laya` runner, the standalone program that runs the Vica Laya model
(`tory-labs/vica-laya` on Hugging Face). Users download the runner and the model from Hugging Face;
this repository only builds the runner.

| Platform | GPU backend | Archive |
|---|---|---|
| macOS arm64 | Metal | `vica-laya-runtime-macos-arm64.tar.gz` |
| Linux x86_64 | Vulkan | `vica-laya-runtime-linux-x86_64.tar.gz` |
| Windows x86_64 | Vulkan | `vica-laya-runtime-windows-x86_64.zip` |

`--device auto` uses the GPU when one is available and falls back to CPU otherwise.

## Build

GitHub Actions (`.github/workflows/build.yml`) builds all three platforms. Linux and Windows builds
drop OpenMP and link the C/C++ runtime statically, so they need only operating-system libraries and the
Vulkan loader, which GPU drivers install. Each run checks fixed CPU decisions and CPU speed against an
upstream-style reference build with the published model, and keeps the archives as workflow
artifacts. Pushing a `v*` tag also attaches them with `SHA256SUMS` to a GitHub release.

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
