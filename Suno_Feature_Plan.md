# Suno AI-Like Music Generation Feature

## Overview
Add a comprehensive music generation feature similar to Suno AI with state-of-the-art models for creating full songs across all genres.

## Models to Integrate

### 1. HeartMuLa (Main Model - Suno v5 competitor)
- **Repo**: `HeartMuLa/HeartMuLa-oss-3B`
- **Capabilities**: Studio-grade music with lyrics, vocals, multi-modal inputs
- **Features**: Section-level control, reference audio, text+lyrics input
- **Quality**: Comparable to Suno v5

### 2. ACE Step 1.5 (Already integrated)
- **Repo**: `ACE-Step/Ace-Step1.5`
- **Capabilities**: Commercial-grade output, fast generation
- **Features**: Cover generation, vocal-to-BGM conversion, repainting
- **Quality**: Between Suno v4.5 and v5

### 3. Stable Audio Open (Alternative)
- **Repo**: `stabilityai/stable-audio-open-small`
- **Capabilities**: High-quality stereo audio up to 47 seconds
- **Features**: Text-to-audio, music and sound effects
- **Quality**: Professional, open-weights

### 4. MusicGen (Fallback/Fast option)
- **Repo**: `facebook/musicgen-large`
- **Capabilities**: Text and melody-guided generation
- **Features**: Fast inference, melody conditioning
- **Quality**: Good baseline

## Advanced Features to Implement

### Core Features
1. **Genre Selection**: Rock, Pop, Jazz, Classical, Hip-Hop, EDM, Folk, Country, etc.
2. **Mood/Emotion**: Happy, Sad, Energetic, Calm, Aggressive, Romantic, etc.
3. **Tempo Control**: BPM slider (60-200 BPM)
4. **Duration**: 10s - 120s (2 minutes)
5. **Vocals**: Enable/Disable, Male/Female voice selection
6. **Lyrics Input**: Optional custom lyrics
7. **Instrumental Selection**: Guitar, Piano, Drums, Synth, Orchestra, etc.

### Advanced Controls
1. **Song Structure**: Intro, Verse, Chorus, Bridge, Outro (section-by-section generation)
2. **Reference Audio Upload**: Style transfer from existing track
3. **Key/Scale Selection**: C Major, D Minor, etc.
4. **Production Quality**: Lo-fi, Studio, Mastered
5. **Stem Separation**: Generate separate tracks (vocals, bass, drums, etc.)

### Creative Tools
1. **Extend**: Automatically continue a generated track
2. **Remix**: Create variations of existing audio
3. **Cover**: Generate covers in different styles
4. **Mashup**: Combine elements from multiple generations

## UI Design

### Tab Structure
```
🎵 Music Studio
├── 🎸 Quick Generate (Simple mode)
├── 🎚️ Advanced Studio (Full controls)
├── 🎼 Lyrics Generator (AI-assisted)
└── 📚 Library (Saved generations)
```

### Quick Generate Mode
- Text prompt field
- Genre dropdown
- Mood selector
- Duration slider
- Generate button

### Advanced Studio Mode
- Multi-tab interface with:
  - Composition (Genre, Tempo, Key, Structure)
  - Vocals (Enable, Gender, Lyrics)
  - Instruments (Multi-select, Mix levels)
  - Production (Quality, Effects, Mastering)
  - Reference (Upload audio for style transfer)

## Implementation Plan

### Phase 1: Core Music Generation
1. Add HeartMuLa and Stable Audio Open to config.py
2. Update audio_generator.py to handle advanced parameters
3. Create music_studio.py for specialized logic

### Phase 2: Advanced UI
1. Create dedicated Music Studio tab
2. Implement genre/mood/instrument controls
3. Add lyrics generation integration

### Phase 3: Creative Tools
1. Implement extend/remix functionality
2. Add reference audio upload and style transfer
3. Create library/history management

### Phase 4: Polish
1. Add preset templates (e.g., "Epic Orchestral Battle", "Chill Lo-fi Study")
2. Implement batch generation
3. Add export options (WAV, MP3, FLAC)
4. Create visualization (waveform, spectrogram)

## Technical Considerations

### Memory Management
- HeartMuLa requires ~12GB VRAM for 3B model
- Implement model swapping to avoid loading all models
- Add VRAM monitoring and warnings

### Performance Optimization
- Use fp16 precision
- Implement caching for frequently used models
- Add progress bars with estimated time

### Audio Quality
- Support high sample rates (44.1kHz, 48kHz)
- Implement post-processing (normalization, compression)
- Add quality presets (Draft, Standard, High, Studio)

## Expected User Experience
Users can create professional-quality music by:
1. Entering a simple prompt like "upbeat summer pop song with catchy chorus"
2. OR using advanced controls to specify every detail
3. Getting a full track in 30-120 seconds
4. Extending, remixing, or refining the output
5. Downloading in multiple formats
