# Third-party notices

The root [MIT license](LICENSE) covers this project's original contributions.
It does not replace the licenses of imported data, downloaded models, or
installed dependencies. This repository does not distribute `.kokoro-env` or
the downloaded speech-model weights.

## Vocabulary data included in this repository

`assessments/vocabulary.json` is adapted from the French vocabulary in
[Language-Learning-decks](https://github.com/vbvss199/Language-Learning-decks/tree/main/french).
Its source metadata records the selection of 4,000 usable entries ranked by
the source's word-frequency field. The project stores selected fields, gender
information, and learner familiarity alongside the imported data. Dataset CEFR
labels and meanings are learning aids, not an official TEF vocabulary list.

The [upstream license](https://github.com/vbvss199/Language-Learning-decks/blob/main/LICENSE)
is reproduced below. Keep this notice with copies of the adapted vocabulary.

```text
MIT License

Copyright (c) 2025 GENERAL NEURO

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Audio components installed separately

- [kokoro-mlx](https://github.com/gabrimatic/kokoro-mlx) provides the MLX
  inference implementation under its [MIT license](https://github.com/gabrimatic/kokoro-mlx/blob/main/LICENSE).
- The default model is [mlx-community/Kokoro-82M-bf16](https://huggingface.co/mlx-community/Kokoro-82M-bf16),
  whose model card specifies Apache-2.0. See also the
  [original Kokoro model](https://huggingface.co/hexgrad/Kokoro-82M).
- MLX, Misaki, SoundFile, eSpeak NG, and other resolved packages retain their
  own licenses. In particular, eSpeak NG is not covered by this project's MIT
  grant; see its [COPYING file](https://github.com/espeak-ng/espeak-ng/blob/master/COPYING).
  Inspect installed package notices before redistributing a bundled runtime.

External assistant applications and services are supplied separately and remain
subject to their providers' terms. This is an independent learning project, not
an official OpenAI, TEF, or Canadian immigration product.
