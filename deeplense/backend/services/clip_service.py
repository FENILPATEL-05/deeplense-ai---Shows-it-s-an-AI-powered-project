import logging
import os
import torch
import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import torch.nn.functional as F

logger = logging.getLogger(__name__)

_model = None
_processor = None
_device = "cuda" if torch.cuda.is_available() else "cpu"


def _load_model():
    global _model, _processor
    if _model is None:
        logger.info("Loading CLIP model openai/clip-vit-base-patch32 on %s...", _device)
        _model = CLIPModel.from_pretrained(
            "openai/clip-vit-base-patch32",
            local_files_only=True,
        ).to(_device)
        _processor = CLIPProcessor.from_pretrained(
            "openai/clip-vit-base-patch32",
            local_files_only=True,
        )
        _model.eval()
        logger.info("CLIP model loaded successfully.")
    return _model, _processor


def preload_model():
    """Eagerly load the CLIP model at startup so first search request is fast."""
    _load_model()


def embed_text(query: str) -> list[float]:
    try:
        model, processor = _load_model()
        inputs = processor(text=[query], return_tensors="pt", padding=True, truncation=True)
        # Move to device and ensure all tensors are on the same device as the model
        inputs = {k: v.to(_device) if torch.is_tensor(v) else v for k, v in inputs.items()}
        with torch.no_grad():
            # Use text_model to get text features
            outputs = model.text_model(**inputs, output_hidden_states=False)
            # Apply text projection to get final embeddings
            text_embeds = model.text_projection(outputs.pooler_output)
            # Normalize
            text_embeds = F.normalize(text_embeds, p=2, dim=1)
        embedding = text_embeds[0].cpu().numpy().tolist()
        logger.debug("Generated text embedding with dimension: %d", len(embedding))
        return embedding
    except Exception as e:
        logger.error("Error embedding text '%s': %s", query, e)
        raise


def embed_image(image_path: str) -> list[float]:
    try:
        model, processor = _load_model()
        with Image.open(image_path).convert("RGB") as image:
            inputs = processor(images=image, return_tensors="pt")
            # Move to device and ensure all tensors are on the same device as the model
            inputs = {k: v.to(_device) if torch.is_tensor(v) else v for k, v in inputs.items()}
            with torch.no_grad():
                # Use vision_model to get image features
                outputs = model.vision_model(**inputs, output_hidden_states=False)
                # Apply vision projection to get final embeddings
                image_embeds = model.visual_projection(outputs.pooler_output)
                # Normalize
                image_embeds = F.normalize(image_embeds, p=2, dim=1)
            embedding = image_embeds[0].cpu().numpy().tolist()
        logger.debug("Generated image embedding for '%s' with dimension: %d", 
                     os.path.basename(image_path), len(embedding))
        return embedding
    except Exception as e:
        logger.error("Error embedding image '%s': %s", image_path, e)
        raise


# ============================================================================
# CLIP Zero-Shot Classification
# ============================================================================

# Define categories and tags for classification
CATEGORIES = ["animals", "nature", "people", "objects", "landscape", "urban", "food", "abstract"]

TAG_DESCRIPTIONS = {
    "outdoor": "outdoor setting, outside, open air",
    "indoor": "indoor setting, inside, interior",
    "bright": "bright lighting, well lit, sunny, high contrast",
    "dark": "dark lighting, low light, shadows, night",
    "colorful": "colorful, vibrant colors, saturated colors",
    "black&white": "black and white, monochrome, grayscale",
    "day": "daytime, daylight, during the day",
    "night": "nighttime, nightlife, evening, dark",
    "macro": "macro photography, close-up, detailed",
    "portrait": "portrait, face, headshot, person",
    "sunset": "sunset, sunrise, golden hour",
    "architecture": "architecture, building, structure",
    "street": "street, street photography, urban street",
    "wildlife": "wildlife, wild animals, nature animals",
    "vintage": "vintage, retro, old style, antique",
    "modern": "modern, contemporary, new style",
    "peaceful": "peaceful, calm, serene, quiet",
    "action": "action, dynamic, movement, motion",
}


def _get_image_embedding_tensor(image_path: str) -> torch.Tensor:
    """Get normalized image embedding as tensor for classification."""
    try:
        model, processor = _load_model()
        with Image.open(image_path).convert("RGB") as image:
            inputs = processor(images=image, return_tensors="pt")
            inputs = {k: v.to(_device) if torch.is_tensor(v) else v for k, v in inputs.items()}
            with torch.no_grad():
                outputs = model.vision_model(**inputs, output_hidden_states=False)
                image_embeds = model.visual_projection(outputs.pooler_output)
                image_embeds = F.normalize(image_embeds, p=2, dim=1)
            return image_embeds[0]
    except Exception as e:
        logger.error("Error getting image embedding tensor for '%s': %s", image_path, e)
        raise


def _get_text_embedding_tensor(text: str) -> torch.Tensor:
    """Get normalized text embedding as tensor for classification."""
    try:
        model, processor = _load_model()
        inputs = processor(text=[text], return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(_device) if torch.is_tensor(v) else v for k, v in inputs.items()}
        with torch.no_grad():
            outputs = model.text_model(**inputs, output_hidden_states=False)
            text_embeds = model.text_projection(outputs.pooler_output)
            text_embeds = F.normalize(text_embeds, p=2, dim=1)
        return text_embeds[0]
    except Exception as e:
        logger.error("Error getting text embedding tensor for '%s': %s", text, e)
        raise


def classify_image(image_path: str) -> str:
    """
    Classify image into one of the predefined categories using CLIP zero-shot classification.
    Returns the category name with highest similarity score.
    """
    try:
        image_embedding = _get_image_embedding_tensor(image_path)
        
        best_category = None
        best_score = -1.0
        
        for category in CATEGORIES:
            category_text = f"a photo of {category}"
            category_embedding = _get_text_embedding_tensor(category_text)
            
            # Cosine similarity (dot product of normalized vectors)
            score = float(torch.nn.functional.cosine_similarity(
                image_embedding.unsqueeze(0),
                category_embedding.unsqueeze(0)
            )[0])
            
            logger.debug("Category '%s' score: %.4f", category, score)
            
            if score > best_score:
                best_score = score
                best_category = category
        
        logger.info("Image '%s' classified as '%s' (score: %.4f)", 
                   os.path.basename(image_path), best_category, best_score)
        return best_category
        
    except Exception as e:
        logger.error("Error classifying image '%s': %s", image_path, e)
        return "abstract"  # Default fallback


def extract_tags(image_path: str, score_threshold: float = 0.25) -> list[str]:
    """
    Extract tags for image using CLIP zero-shot classification.
    Returns list of tags with similarity score above threshold.
    """
    try:
        image_embedding = _get_image_embedding_tensor(image_path)
        
        tags_with_scores = []
        
        for tag, description in TAG_DESCRIPTIONS.items():
            tag_embedding = _get_text_embedding_tensor(description)
            
            # Cosine similarity
            score = float(torch.nn.functional.cosine_similarity(
                image_embedding.unsqueeze(0),
                tag_embedding.unsqueeze(0)
            )[0])
            
            logger.debug("Tag '%s' score: %.4f", tag, score)
            
            if score >= score_threshold:
                tags_with_scores.append((tag, score))
        
        # Sort by score descending and return top tags
        tags_with_scores.sort(key=lambda x: x[1], reverse=True)
        tags = [tag for tag, score in tags_with_scores[:5]]  # Max 5 tags
        
        logger.info("Image '%s' extracted tags: %s", 
                   os.path.basename(image_path), tags)
        return tags
        
    except Exception as e:
        logger.error("Error extracting tags from image '%s': %s", image_path, e)
        return []  # Return empty list on error
