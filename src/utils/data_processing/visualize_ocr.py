#!/usr/bin/env python3

import os
import json
import argparse
import logging
import base64
import tempfile
from pathlib import Path
import matplotlib.pyplot as plt
from IPython.display import Markdown, display
import numpy as np
from PIL import Image
import io

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def replace_images_in_markdown(markdown_str: str, images_dict: dict) -> str:
    """
    Replace image placeholders in markdown with base64-encoded images.

    Args:
        markdown_str: Markdown text containing image placeholders
        images_dict: Dictionary mapping image IDs to base64 strings

    Returns:
        Markdown text with images replaced by base64 data
    """
    for img_name, base64_str in images_dict.items():
        markdown_str = markdown_str.replace(
            f"![{img_name}]({img_name})", f"![{img_name}]({base64_str})"
        )
    return markdown_str

def get_combined_markdown(ocr_data: dict) -> str:
    """
    Combine OCR text and images into a single markdown document.

    Args:
        ocr_data: OCR response data containing text and images

    Returns:
        Combined markdown string with embedded images
    """
    markdowns: list[str] = []
    # Extract images from page
    for page in ocr_data.get("pages", []):
        image_data = {}
        for img in page.get("images", []):
            if "image_base64" in img:
                image_data[img["id"]] = img["image_base64"]
        
        # Replace image placeholders with actual images
        if "markdown" in page:
            markdowns.append(replace_images_in_markdown(page["markdown"], image_data))

    return "\n\n".join(markdowns)

def save_markdown_to_file(markdown_content: str, output_path: str) -> None:
    """Save markdown content to a file."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    logger.info(f"Markdown saved to: {output_path}")

def extract_images_from_ocr(ocr_data: dict, output_dir: str) -> None:
    """Extract and save images from OCR data."""
    os.makedirs(output_dir, exist_ok=True)
    
    image_count = 0
    for page_idx, page in enumerate(ocr_data.get("pages", [])):
        for img_idx, img in enumerate(page.get("images", [])):
            if "image_base64" in img:
                try:
                    # Decode base64 image
                    img_data = base64.b64decode(img["image_base64"].split(",")[-1])
                    
                    # Save image
                    img_path = os.path.join(output_dir, f"page_{page_idx+1}_img_{img_idx+1}.png")
                    with open(img_path, "wb") as f:
                        f.write(img_data)
                    
                    image_count += 1
                except Exception as e:
                    logger.error(f"Error saving image: {e}")
    
    logger.info(f"Extracted {image_count} images to {output_dir}")

def main():
    parser = argparse.ArgumentParser(description='Visualize OCR results')
    parser.add_argument('input', help='Input JSON file with OCR results')
    parser.add_argument('-o', '--output', help='Output markdown file')
    parser.add_argument('-i', '--images', help='Directory to save extracted images')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        return
    
    # Load OCR results
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            ocr_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading OCR results: {e}")
        return
    
    # Generate markdown
    markdown_content = get_combined_markdown(ocr_data)
    
    # Determine output path for markdown
    output_path = args.output
    if not output_path:
        base_name = os.path.splitext(os.path.basename(args.input))[0]
        output_path = f"{base_name}_visualization.md"
    
    # Save markdown
    save_markdown_to_file(markdown_content, output_path)
    
    # Extract images if requested
    if args.images:
        extract_images_from_ocr(ocr_data, args.images)
    
    # Print summary
    num_pages = len(ocr_data.get("pages", []))
    logger.info(f"Processed {num_pages} pages")
    logger.info(f"Markdown visualization saved to: {output_path}")

if __name__ == "__main__":
    main() 