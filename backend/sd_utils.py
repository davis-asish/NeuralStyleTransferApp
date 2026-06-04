import torch
from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
from PIL import Image
import os
import logging

logger = logging.getLogger(__name__)

# Check device availability
def get_device():
    """Get the best available device for inference."""
    if hasattr(torch, 'cuda') and torch.cuda.is_available():
        try:
            # Test CUDA availability
            torch.cuda.init()
            device_count = torch.cuda.device_count()
            if device_count > 0:
                logger.info(f"✅ CUDA available with {device_count} device(s)")
                return "cuda"
        except Exception as e:
            logger.warning(f"CUDA initialization failed: {e}")

    # Fallback to CPU
    logger.info("⚠️ Using CPU for Stable Diffusion (GPU not available or compatible)")
    return "cpu"

DEVICE = get_device()
SD_MODEL = "stabilityai/sd-turbo"

# Global model cache to avoid reloading
_model_cache = {}

# Style presets for image-to-image transformation
STYLE_PRESETS = {
    "anime": "anime style, high quality, detailed, vibrant colors, studio ghibli inspired",
    "cartoon": "cartoon style, animated, colorful, exaggerated features, disney inspired",
    "painting": "oil painting, artistic, brush strokes, masterpiece, van gogh style",
    "sketch": "pencil sketch, black and white, detailed lines, artistic drawing",
    "cyberpunk": "cyberpunk style, neon lights, futuristic, high tech, dark atmosphere",
    "realistic": "photorealistic, high detail, natural lighting, professional photography"
}

def generate_image(prompt, output_path="static/outputs/generated.png", steps=15, scale=7.5):
    """Generate an image from a text prompt using Stable Diffusion Turbo."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Use cached model if available
    cache_key = f"generate_{SD_MODEL}"
    if cache_key not in _model_cache:
        dtype = torch.float16 if DEVICE == "cuda" else torch.float32
        pipe = StableDiffusionPipeline.from_pretrained(
            SD_MODEL,
            torch_dtype=dtype,
            safety_checker=None
        ).to(DEVICE)

        # Memory optimizations
        pipe.enable_attention_slicing()
        if DEVICE == "cuda":
            pipe.enable_vae_slicing()

        _model_cache[cache_key] = pipe
        logger.info(f"📥 Loaded and cached generation model: {SD_MODEL}")
    else:
        pipe = _model_cache[cache_key]
        logger.info(f"♻️ Using cached generation model: {SD_MODEL}")

    logger.info(f"🎨 Generating image with prompt: '{prompt}'")
    result = pipe(prompt, num_inference_steps=steps, guidance_scale=scale)
    result.images[0].save(output_path)
    logger.info(f"✅ Image generated and saved to: {output_path}")
    return output_path

def stylize_image(content_path, style_preset, output_path="static/outputs/styled.png", strength=0.75):
    """Apply style transformation to an image using img2img pipeline."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    content_image = Image.open(content_path).convert("RGB")

    if style_preset not in STYLE_PRESETS:
        raise ValueError(f"Invalid style preset: {style_preset}. Available: {list(STYLE_PRESETS.keys())}")

    style_prompt = STYLE_PRESETS[style_preset]
    logger.info(f"🎭 Applying {style_preset} style with prompt: '{style_prompt}'")

    # Use cached model if available
    cache_key = f"stylize_{SD_MODEL}"
    if cache_key not in _model_cache:
        dtype = torch.float16 if DEVICE == "cuda" else torch.float32
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            SD_MODEL,
            torch_dtype=dtype,
            safety_checker=None
        ).to(DEVICE)

        # Memory optimizations
        pipe.enable_attention_slicing()
        if DEVICE == "cuda":
            pipe.enable_vae_slicing()

        _model_cache[cache_key] = pipe
        logger.info(f"📥 Loaded and cached stylization model: {SD_MODEL}")
    else:
        pipe = _model_cache[cache_key]
        logger.info(f"♻️ Using cached stylization model: {SD_MODEL}")

    result = pipe(
        prompt=style_prompt,
        image=content_image,
        strength=strength,
        guidance_scale=7.5,
        num_inference_steps=20
    )
    result.images[0].save(output_path)
    logger.info(f"✅ Styled image saved to: {output_path}")
    return output_path
