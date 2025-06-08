import os
import argparse
import logging
from pikepdf import Pdf
import tempfile

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def compress_pdf(input_path, output_path=None, quality="medium"):
    """
    Compress PDF file using pikepdf.
    
    Args:
        input_path (str): Path to input PDF file
        output_path (str): Path to output PDF file. If None, will use input_path with suffix.
        quality (str): Compression quality: 'low', 'medium', or 'high'
    
    Returns:
        str: Path to compressed PDF file
    """
    if not os.path.exists(input_path):
        logger.error(f"Input file not found: {input_path}")
        return None
    
    # Generate output path if not provided
    if output_path is None:
        filename, ext = os.path.splitext(input_path)
        output_path = f"{filename}-compressed{ext}"
    
    # Set compression parameters based on quality
    if quality == "low":
        compression_params = {"object_stream_mode": 2, "compress_streams": True, "stream_decode_level": 1}
    elif quality == "medium":
        compression_params = {"object_stream_mode": 1, "compress_streams": True, "stream_decode_level": 0}
    else:  # high
        compression_params = {"object_stream_mode": 0, "compress_streams": True, "stream_decode_level": 0}
    
    try:
        # Get original file size
        original_size = os.path.getsize(input_path) / (1024 * 1024)  # in MB
        logger.info(f"Original file size: {original_size:.2f} MB")
        
        # Create temporary file for intermediate processing
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Open and save with pikepdf (first pass compression)
        pdf = Pdf.open(input_path)
        pdf.save(temp_path, **compression_params)
        pdf.close()
        
        # Second pass with different settings
        pdf = Pdf.open(temp_path)
        pdf.save(output_path, linearize=True, **compression_params)
        pdf.close()
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # Get compressed file size
        compressed_size = os.path.getsize(output_path) / (1024 * 1024)  # in MB
        reduction = (1 - compressed_size / original_size) * 100
        
        logger.info(f"Compressed file size: {compressed_size:.2f} MB")
        logger.info(f"Size reduction: {reduction:.1f}%")
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error compressing PDF: {e}")
        # Clean up temp file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        return None

def main():
    parser = argparse.ArgumentParser(description='Compress PDF file')
    parser.add_argument('input', help='Input PDF file path')
    parser.add_argument('-o', '--output', help='Output PDF file path')
    parser.add_argument('-q', '--quality', choices=['low', 'medium', 'high'], 
                        default='medium', help='Compression quality')
    
    args = parser.parse_args()
    
    compressed_path = compress_pdf(args.input, args.output, args.quality)
    
    if compressed_path:
        logger.info(f"Compressed PDF saved to: {compressed_path}")
    else:
        logger.error("PDF compression failed")

if __name__ == "__main__":
    main() 