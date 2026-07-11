---
name: audio-production
description: "Music and audio creation, analysis, generation, and songwriting — covers text-to-music (AudioCraft/MusicGen), song generation from lyrics+tags (HeartMuLa), audio visualization/spectrograms (songsee), songwriting craft, and Suno AI prompts."
version: 1.0.0
author: Hermes Agent (consolidated)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [audio, music, generation, spectrogram, songwriting, suno, audiocraft, heartmula]
    related_skills: []
---

# Audio Production

Umbrella skill for music/audio creation, analysis, and songwriting. Covers four sub-domains as separate sections below.

## When to use

This is the first skill to load when the user asks about:
- Generating music from text descriptions (MusicGen, AudioGen)
- Generating songs from lyrics + style tags (HeartMuLa / Suno-like)
- Visualizing audio as spectrograms, mel, chroma, MFCC (songsee)
- Writing lyrics, structuring songs, parody, or crafting Suno AI prompts
- Any combination of the above (e.g. write lyrics, generate with HeartMuLa, then visualize)

## Section overview

| Section | Tool | What it does |
|---------|------|-------------|
| **A. Text-to-Music (AudioCraft)** | MusicGen, AudioGen, EnCodec | Generate music/sound from text prompts |
| **B. Song Generation (HeartMuLa)** | HeartMuLa, HeartCodec | Generate full songs from lyrics + tags |
| **C. Audio Visualization (songsee)** | songsee CLI | Spectrograms, mel, chroma, MFCC grids |
| **D. Songwriting & Suno Prompts** | Craft guidelines + Suno metatags | Write lyrics, structure, parody, Suno prompts |

---

## A. Text-to-Music — AudioCraft (MusicGen / AudioGen)

Meta's AudioCraft for text-to-music and text-to-sound generation.

### Quick start

```bash
pip install audiocraft
```

```python
from audiocraft.models import MusicGen
import torchaudio

model = MusicGen.get_pretrained('facebook/musicgen-small')
model.set_generation_params(duration=8, top_k=250, temperature=1.0)

wav = model.generate(["happy upbeat electronic dance music with synths"])
torchaudio.save("output.wav", wav[0].cpu(), sample_rate=32000)
```

### Model variants

| Model | Size | Use Case |
|-------|------|----------|
| `musicgen-small` | 300M | Quick generation |
| `musicgen-medium` | 1.5B | Balanced quality |
| `musicgen-large` | 3.3B | Best quality |
| `musicgen-melody` | 1.5B | Melody-conditioned generation |
| `musicgen-stereo-*` | Varies | Stereo output |
| `musicgen-style` | 1.5B | Style transfer |
| `audiogen-medium` | 1.5B | Sound effects (text-to-sound) |

### Text-to-sound (AudioGen)

```python
from audiocraft.models import AudioGen
model = AudioGen.get_pretrained('facebook/audiogen-medium')
model.set_generation_params(duration=5)
wav = model.generate(["dog barking in a park with birds chirping"])
torchaudio.save("sound.wav", wav[0].cpu(), sample_rate=16000)
```

### Key generation parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `duration` | 8.0 | Length in seconds (1-120) |
| `top_k` | 250 | Sampling diversity |
| `top_p` | 0.0 | Nucleus sampling |
| `temperature` | 1.0 | Creativity |
| `cfg_coef` | 3.0 | Text adherence |

### Melody-conditioned generation

```python
model = MusicGen.get_pretrained('facebook/musicgen-melody')
model.set_generation_params(duration=30)
melody, sr = torchaudio.load("melody.wav")
wav = model.generate_with_chroma(["acoustic guitar folk song"], melody, sr)
```

### Using HuggingFace Transformers

```python
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import scipy

processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
inputs = processor(text=["80s pop track with bassy drums and synth"], padding=True, return_tensors="pt")
audio_values = model.generate(**inputs, do_sample=True, guidance_scale=3, max_new_tokens=256)
sampling_rate = model.config.audio_encoder.sampling_rate
scipy.io.wavfile.write("output.wav", rate=sampling_rate, data=audio_values[0, 0].cpu().numpy())
```

### GPU memory requirements

| Model | FP32 VRAM | FP16 VRAM |
|-------|-----------|-----------|
| musicgen-small | ~4GB | ~2GB |
| musicgen-medium | ~8GB | ~4GB |
| musicgen-large | ~16GB | ~8GB |

### Common issues

| Issue | Solution |
|-------|----------|
| CUDA OOM | Use smaller model, reduce duration |
| Poor quality | Increase cfg_coef, improve prompts |
| Audio artifacts | Try different temperature |

### Resources

- GitHub: https://github.com/facebookresearch/audiocraft
- Papers: MusicGen (arxiv.org/abs/2306.05284), AudioGen (arxiv.org/abs/2209.15352)
- HF: https://huggingface.co/facebook/musicgen-small

---

## B. Song Generation — HeartMuLa

Open-source music foundation model (Apache-2.0) for generating full songs from lyrics + tags. Comparable to Suno.

### Hardware requirements

- Minimum: 8GB VRAM with `--lazy_load true` (peaks at ~6.2GB for 3B model)
- Recommended: 16GB+ VRAM
- Multi-GPU: `--mula_device cuda:0 --codec_device cuda:1`

### Installation

```bash
git clone https://github.com/HeartMuLa/heartlib.git
cd heartlib
uv venv --python 3.10 .venv
source .venv/bin/activate
uv pip install -e .
uv pip install --upgrade datasets transformers
```

**Source patches required** (for transformers 5.x compatibility):
1. In `src/heartlib/heartmula/modeling_heartmula.py`, in `setup_caches`, add RoPE reinit after `reset_caches`
2. In `src/heartlib/pipelines/music_generation.py`, add `ignore_mismatched_sizes=True` to all `HeartCodec.from_pretrained()` calls

### Download checkpoints

```bash
cd heartlib
hf download --local-dir './ckpt' 'HeartMuLa/HeartMuLaGen'
hf download --local-dir './ckpt/HeartMuLa-oss-3B' 'HeartMuLa/HeartMuLa-oss-3B-happy-new-year'
hf download --local-dir './ckpt/HeartCodec-oss' 'HeartMuLa/HeartCodec-oss-20260123'
```

### Basic generation

```bash
cd heartlib
source .venv/bin/activate
python ./examples/run_music_generation.py \
  --model_path=./ckpt \
  --version="3B" \
  --lyrics="./assets/lyrics.txt" \
  --tags="./assets/tags.txt" \
  --save_path="./assets/output.mp3" \
  --lazy_load true
```

### Input formatting

**Tags** (comma-separated, no spaces): `piano,happy,wedding,synthesizer,romantic`

**Lyrics** (bracketed structural tags):
```
[Intro]
[Verse]
Your lyrics here...
[Chorus]
Chorus lyrics...
[Bridge]
[Outro]
```

### Key parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--max_audio_length_ms` | 240000 | Max length (240s) |
| `--topk` | 50 | Top-k sampling |
| `--temperature` | 1.0 | Sampling temperature |
| `--cfg_scale` | 1.5 | CFG scale |
| `--lazy_load` | false | Save VRAM |
| `--mula_dtype` | bfloat16 | Model dtype |
| `--codec_dtype` | float32 | Codec dtype (DO NOT use bf16) |

### Pitfalls

1. Do NOT use bf16 for HeartCodec — degrades quality
2. Tags may be ignored by the model; lyrics tend to dominate
3. Triton not available on macOS — Linux/CUDA only for GPU acceleration
4. RTX 5080 incompatibility reported upstream

### Links

- Repo: https://github.com/HeartMuLa/heartlib
- Models: https://huggingface.co/HeartMuLa
- Paper: https://arxiv.org/abs/2601.10547

---

## C. Audio Visualization — songsee

Generate spectrograms and multi-panel audio feature visualizations from audio files.

### Prerequisites

```bash
go install github.com/steipete/songsee/cmd/songsee@latest
```

Optional: `ffmpeg` for formats beyond WAV/MP3.

### Quick start

```bash
songsee track.mp3                                         # Basic spectrogram
songsee track.mp3 -o spectrogram.png                      # Save to file
songsee track.mp3 --viz spectrogram,mel,chroma,hpss,selfsim,loudness,tempogram,mfcc,flux  # Multi-panel
songsee track.mp3 --start 12.5 --duration 8 -o slice.jpg  # Time slice
cat track.mp3 | songsee - --format png -o out.png         # From stdin
```

### Visualization types

| Type | Description |
|------|-------------|
| `spectrogram` | Standard frequency spectrogram |
| `mel` | Mel-scaled spectrogram |
| `chroma` | Pitch class distribution |
| `hpss` | Harmonic/percussive separation |
| `selfsim` | Self-similarity matrix |
| `loudness` | Loudness over time |
| `tempogram` | Tempo estimation |
| `mfcc` | Mel-frequency cepstral coefficients |
| `flux` | Spectral flux (onset detection) |

### Common flags

| Flag | Description |
|------|-------------|
| `--style` | Color palette: `classic`, `magma`, `inferno`, `viridis`, `gray` |
| `--width` / `--height` | Output image dimensions |
| `--window` / `--hop` | FFT window and hop size |
| `--min-freq` / `--max-freq` | Frequency range filter |
| `--format` | Output format: `jpg` or `png` |

### Notes

- WAV and MP3 decoded natively; other formats require ffmpeg
- Output images can be inspected with vision tools for automated analysis
- Useful for comparing audio outputs, debugging synthesis, documenting pipelines

---

## D. Songwriting & Suno AI Prompts

Guidelines for writing song lyrics, structuring songs, creating parodies, and crafting effective Suno AI prompts.

### Song structure

| Pattern | Description | Genre |
|---------|-------------|-------|
| ABABCB | Verse/Chorus/Verse/Chorus/Bridge/Chorus | Most pop/rock |
| AABA | Verse/Verse/Bridge/Verse (refrain-based) | Jazz standards, ballads |
| ABAB | Verse/Chorus alternating | Simple, direct |
| AAA | Strophic, no chorus | Folk, storytelling |

Building blocks: Intro, Verse, Pre-Chorus, Chorus, Bridge, Outro

### Rhyme types

| Type | Example | Use |
|------|---------|-----|
| Perfect | lean/mean | Tight connection |
| Family | crate/braid | Looser |
| Assonance | had/glass | Same vowels |
| Consonance | scene/when | Similar endings |
| Near/slant | — | Suggests connection |

Mix them — all perfect rhymes can sound nursery-rhyme, all slant can sound lazy.

### Suno style description formula

```
Genre + Mood + Era + Instruments + Vocal Style + Production + Dynamics
```

**Bad:** `"sad rock song"`
**Good:** `"Cinematic orchestral spy thriller, 1960s Cold War era, smoky sultry female vocalist, big band jazz, brass section with trumpets and french horns, sweeping strings, minor key, vintage analog warmth"`

### Suno metatags

**Structure:** `[Intro]`, `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Bridge]`, `[Interlude]`, `[Instrumental]`, `[Outro]`
**Vocal:** `[Whispered]`, `[Spoken Word]`, `[Belted]`, `[Falsetto]`, `[Raspy]`, `[Breathy]`, `[Harmonies]`
**Dynamics:** `[High Energy]`, `[Building Energy]`, `[Explosive]`, `[Emotional Climax]`, `[Gradual swell]`
**Gender:** `[Female Vocals]`, `[Male Vocals]`
**Atmosphere:** `[Melancholic]`, `[Euphoric]`, `[Dreamy]`, `[Intimate]`, `[Dark Atmosphere]`
**SFX:** `[Vinyl Crackle]`, `[Rain]`, `[Applause]`, `[Thunder]`

### Parody adaptation

1. Map original structure (syllables per line, rhyme scheme, stressed syllables)
2. Match stressed syllables to original beats
3. On long held notes, match the VOWEL SOUND of the original
4. Monosyllabic swaps in key spots maintain rhythm
5. Keep some original lines for recognizability

### Suno workflow

1. Write concept/hook first
2. If adapting, map original structure
3. Generate raw material, then structure
4. Draft lyrics, read aloud to catch stumbles
5. Build style description painting the dynamic journey
6. Add metatags to lyrics
7. Generate 3-5 variations
8. Use Extend/Continue to build on promising sections

### Phonetic tricks for AI vocalists

- Spell words as they SOUND: "through" → "thru", "Nous" → "Noose"
- Hyphenate to guide syllables: "Re-search"
- ALL CAPS = louder
- "lo-o-o-ove" = sustained/melisma
- Spell out numbers: "24/7" → "twenty four seven"
- Space acronyms: "AI" → "A I"