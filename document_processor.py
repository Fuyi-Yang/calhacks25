# document_processor.py

import os
from handlers.llm_handler import GeminiLLM
from handlers.pdf_handler import PDFHandler
from handlers.figure_processor import FigureProcessor
from utils.latex_renderer import LatexRenderer

class DocumentProcessor:
    """Orchestrates the entire conversion process from input file to .tex output."""

    def __init__(self, input_path: str, output_dir: str, text_mode: str):
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        self.input_path = input_path
        self.output_dir = output_dir
        self.text_mode = text_mode
        self.pdf_path = ""
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.llm = GeminiLLM()
        self.renderer = LatexRenderer()

    def _prepare_pdf(self):
        """Ensures the input is a PDF, converting from image if necessary."""
        filename = os.path.basename(self.input_path)
        name, ext = os.path.splitext(filename)
        
        if ext.lower() in ['.jpg', '.jpeg', '.png']:
            print("Image file detected. Converting to PDF...")
            self.pdf_path = os.path.join(self.output_dir, f"{name}.pdf")
            PDFHandler.convert_image_to_pdf(self.input_path, self.pdf_path)
        elif ext.lower() == '.pdf':
            print("PDF file detected.")
            self.pdf_path = self.input_path
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def _validate_output(self, s):
        s = s.strip(" \n")
    
        # Check if it starts and ends with ```latex ... ```
        if s.startswith("```latex") and s.endswith("```"):
            # Extract everything between the opening line and the closing ```
            # NOTE:might have issue
            return s[8:-3].strip()
        
        # Otherwise, just return the string as-is
        return s

    def process(self):
        """Executes the full document processing workflow."""
        print("--- Starting Document Processing ---")
        self._prepare_pdf()

        # --- Text Processing Path ---
        # The LLM can process the PDF directly, which is more robust than text extraction.
        latex_template = self.llm.extract_text_to_latex(self.pdf_path, self.text_mode)
        
        # --- Figure Processing Path ---
        print("\n--- Checking for Figures ---")
        pdf_handler = PDFHandler(self.pdf_path)
        pdf_pages_as_images = pdf_handler.get_pages_as_images()
        figure_descriptions = self.llm.get_figure_descriptions(pdf_pages_as_images)
        
        generated_figure_files = []
        if figure_descriptions:
            print(f"\nFound {len(figure_descriptions)} potential figures. Starting parallel processing...")
            fig_processor = FigureProcessor(self.llm, self.renderer, self.output_dir)
            generated_figure_files = fig_processor.process_figures_in_parallel(figure_descriptions)
        else:
            print("No figures found or described. Skipping figure generation.")

        # --- Merging Path ---
        print("\n--- Finalizing LaTeX Document ---")
        final_latex_doc = self.llm.merge_latex_and_figures(latex_template, generated_figure_files)

        # --- validate output
        print("\n--- Validating LaTeX Document ---")
        val_final_latex_doc = self._validate_output(final_latex_doc)

        # --- Output ---
        output_filename = os.path.splitext(os.path.basename(self.pdf_path))[0] + ".tex"
        output_filepath = os.path.join(self.output_dir, output_filename)
        with open(output_filepath, "w", encoding='utf-8') as f:
            f.write(val_final_latex_doc)
            
        print(f"\n✅ Success! Final document saved to: {output_filepath}")
