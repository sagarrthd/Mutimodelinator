"""Example prompts for each generation mode."""

# ==================== IMAGE PROMPTS ====================
IMAGE_PROMPTS = {
    "landscapes": [
        "A serene mountain landscape with snow-capped peaks at sunrise, golden light, photorealistic, national geographic style",
        "Misty forest with tall pine trees and moss-covered ground, moody lighting, cinematic",
        "Desert dunes with surreal purple sky and floating crystals, fantasy art",
        "Tropical waterfall cascading into emerald lagoon, lush vegetation, humid atmosphere",
    ],
    "architecture": [
        "Futuristic cyberpunk city street with neon signs, flying cars, detailed, ultra realistic, 4K",
        "Medieval stone castle perched on cliff overlooking misty valley, dramatic architecture",
        "Minimalist Scandinavian interior design, white walls, natural light, sleek furniture",
        "Japanese pagoda temple surrounded by cherry blossoms, peaceful, traditional aesthetic",
    ],
    "fantasy": [
        "Dragon perched on mountain of gold coins, breathing fire, epic fantasy art",
        "Enchanted forest with glowing mushrooms and magical creatures, ethereal lighting",
        "Underwater city with bioluminescent architecture and exotic alien creatures",
        "Portal to another dimension with swirling colors and cosmic energy",
    ],
    "abstract": [
        "Abstract geometric patterns with iridescent colors and chrome metallic surfaces, modern art",
        "Swirling liquid ink mixing in water, vibrant colors, macro photography",
        "Particle system creating a face, digital art, glitch aesthetics",
        "Fractal patterns zooming infinitely, mathematical beauty, surreal colors",
    ],
    "people": [
        "Portrait of elegant woman with flowing hair, warm lighting, oil painting style, renaissance",
        "Group of people laughing together at outdoor cafe, warm golden hour light, candid moment",
        "Fashion model in avant-garde outfit, professional photo shoot lighting, editorial style",
        "Child playing in rain puddles, joyful expression, soft natural lighting, lifestyle photography",
    ],
    "animals": [
        "Majestic lion with flowing mane against sunset, powerful, wildlife photography, high quality",
        "Hummingbird hovering near vibrant flowers, macro photography, sharp details, iridescent colors",
        "Pack of wolves running through snowy forest, dynamic motion, dramatic lighting",
        "Sleeping cat on cozy blanket, soft warm lighting, peaceful, cat photography",
    ],
}

# ==================== AUDIO PROMPTS ====================
AUDIO_PROMPTS = {
    "music": [
        "Epic orchestral music with dramatic strings, french horns, and powerful drums, cinematic",
        "Calm ambient electronic music with slow synthesizers and relaxing pad sounds",
        "Upbeat pop music with catchy melody, modern production, energetic drums and bass",
        "Lo-fi hip hop beats with vinyl crackle, chill vibes, perfect for studying",
        "Classical piano concerto with emotional melody and rich orchestral backing",
        "Jazz ensemble with saxophone, upright bass, and drums in intimate club setting",
    ],
    "speech": [
        "Professional narrator voice reading news headline with dramatic emphasis",
        "Enthusiastic motivational speaker with energetic voice giving inspiring talk",
        "Calm meditation guide with soothing voice, whispering, relaxing tone",
        "Comedy podcast host with expressive voice, funny tone, entertaining delivery",
    ],
    "nature": [
        "Relaxing nature sounds with gentle rain on leaves, distant thunder, peaceful atmosphere",
        "Ocean waves crashing on beach with seagulls calling, coastal ambiance",
        "Forest ambiance with bird songs, rustling leaves, and distant wind sounds",
        "Summer day with crickets chirping, breeze rustling, and distant thunder",
    ],
    "sci-fi": [
        "Futuristic spaceship alert sounds with beeping synthesizers and electronic tones",
        "Alien conversation with strange vocal effects and otherworldly soundscape",
        "Laser sounds and sci-fi special effects, futuristic tone",
        "Robot voice with mechanical sounds and digital tones",
    ],
}

# ==================== VIDEO PROMPTS ====================
VIDEO_PROMPTS = {
    "abstract": [
        "Abstract particles flowing and morphing into geometric shapes, smooth motion, vibrant colors",
        "Swirling galaxy with stars and nebula clouds, cosmic beauty, slow rotation",
        "Liquid ink mixing in water creating intricate patterns, slow motion macro shot",
        "Kaleidoscope patterns morphing and rotating, hypnotic, colorful animation",
    ],
    "nature": [
        "Ocean waves crashing on sunny beach with seagulls flying, peaceful coastal scene",
        "Waterfall cascading into emerald pool with mist, morning light, serene",
        "Forest walk with dappled sunlight through trees, peaceful ambiance, hiking trail",
        "Sunset over mountains with clouds moving across sky, time-lapse effect",
    ],
    "objects": [
        "Rotating golden sphere with reflective surface on dark background, glossy material",
        "Ancient golden artifacts slowly rotating on dark museum background, museum lighting",
        "Mechanical clockwork gears spinning in synchronization, detailed engineering",
        "Crystal geode rotating slowly showing internal structure, rainbow reflections",
    ],
    "science": [
        "Molecular structure animating and rotating, showing atomic bonds and structure",
        "DNA double helix rotating slowly in blue light, scientific visualization",
        "Coral reef ecosystem with fish swimming, colorful underwater life, peaceful",
        "Human organ visualization with blood flow animation, medical illustration",
    ],
    "music": [
        "Sound waves visualizing music with geometric patterns responding to beat",
        "Equalizer bars jumping to music rhythm, colorful visualization, modern design",
        "Concert stage with lighting effects responding to music, dynamic light show",
        "Audio frequency spectrum analyzer with colors responding to sound",
    ],
}

# ==================== NEGATIVE PROMPTS ====================
NEGATIVE_PROMPTS = {
    "image": "blurry, low quality, distorted, ugly, bad anatomy, worst quality, artifacts, watermark, text, logo, embedded text, duplicate, meme, gross",
    "video": "static, jerky motion, inconsistent lighting, blurry, low quality, artifacts",
}

# ==================== PROMPT TIPS ====================
PROMPT_TIPS = {
    "image": {
        "do": [
            "Be specific: 'oil painting of X in style of Y'",
            "Include lighting: 'golden hour light', 'dramatic shadows'",
            "Add quality hints: '4K', 'ultra detailed', 'photorealistic'",
            "Use artistic styles: 'Renaissance', 'Impressionist', 'Cyberpunk'",
            "Include materials: 'silk fabric', 'marble stone', 'chrome metal'",
        ],
        "dont": [
            "Use negative words in prompt (use negative prompt instead)",
            "Ask for copyrighted characters (use style instead)",
            "Be vague: 'a person' (specify age, clothing, activity)",
            "Request impossible physics (leverage negative prompt)",
        ],
    },
    "audio": {
        "do": [
            "Specify mood: 'calm', 'energetic', 'melancholic'",
            "Name instruments: 'piano', 'saxophone', 'drums'",
            "Set context: 'coffee shop ambiance', 'concert hall'",
            "Include tempo: 'slow', 'moderate', 'fast'",
        ],
        "dont": [
            "Ask for vocals/singing (use speech synthesis instead)",
            "Expect specific recognizable songs",
            "Use overly complex descriptions",
        ],
    },
    "video": {
        "do": [
            "Describe camera motion: 'rotating', 'zooming', 'panning'",
            "Specify pacing: 'slow and smooth', 'dynamic motion'",
            "Include lighting: 'neon glow', 'natural sunlight'",
            "Set scale: 'macro', 'wide landscape', 'close-up'",
        ],
        "dont": [
            "Request specific actors or copyrighted content",
            "Expect perfect synchronization (use multiple generations)",
        ],
    },
}

if __name__ == "__main__":
    # Print all available examples
    print("=== IMAGE PROMPTS ===")
    for category, prompts in IMAGE_PROMPTS.items():
        print(f"\n{category.upper()}:")
        for prompt in prompts:
            print(f"  • {prompt}")

    print("\n=== AUDIO PROMPTS ===")
    for category, prompts in AUDIO_PROMPTS.items():
        print(f"\n{category.upper()}:")
        for prompt in prompts:
            print(f"  • {prompt}")

    print("\n=== VIDEO PROMPTS ===")
    for category, prompts in VIDEO_PROMPTS.items():
        print(f"\n{category.upper()}:")
        for prompt in prompts:
            print(f"  • {prompt}")
