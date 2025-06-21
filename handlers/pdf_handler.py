import os

import fitz
import google.generativeai as genai
from PIL import Image

class PDFHandler:
    """Handles PDF operations like text and image extraction."""

    def __init__(self, filepath: str):
        """
        Initializes the handler with a path to a PDF file.

        Args:
            filepath: The path to the PDF file.
        """
        try:
            self.doc = fitz.open(filepath)
        except Exception as e:
            print(f"Error opening PDF {filepath}: {e}")
            raise
        print(f"PDF '{filepath}' loaded successfully with {len(self.doc)} pages.")

        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.pdf_model = genai.GenerativeModel("gemini-2.5-pro")
        self.uploaded = genai.upload_file(filepath)
        print("uploaded successfully, my goat")

    def get_pages_as_images(self) -> list[Image.Image]:
        """Converts each page of the PDF into a PIL Image."""
        images = []
        for page_num in range(len(self.doc)):
            page = self.doc.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
        print("Converted all PDF pages to images.")
        return images

    @staticmethod
    def convert_image_to_pdf(image_path: str, output_pdf_path: str) -> None:
        """
        Converts a single image file to a single-page PDF.

        Args:
            image_path: Path to the input image.
            output_pdf_path: Path to save the output PDF.
        """
        try:
            with Image.open(image_path) as image:
                # Ensure image is in a format that can be saved as PDF
                if image.mode == 'RGBA':
                    image = image.convert('RGB')
                image.save(output_pdf_path, "PDF", resolution=100.0)
                print(f"Image '{image_path}' converted to PDF '{output_pdf_path}'.")
        except Exception as e:
            print(f"Failed to convert image to PDF: {e}")
            raise
