import os
from PIL import Image
import google.generativeai as genai


class GeminiLLM:
    """A handler for all interactions with the Google Gemini LLM."""

    def __init__(self):
        """Initializes the Gemini model."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def extract_text_to_latex(self, pdf_path: str, mode: str) -> str:
        """
        Uses an LLM to convert raw text into a LaTeX format.

        Args:
            pdf_path: The path to the PDF file.
            mode: Processing mode ('rewriting', 'summarizing', 'verbatim').

        Returns:
            A string containing the document in LaTeX format, with placeholders for figures.
        """
        print(f"Processing text in '{mode}' mode...")

        action_prompt = {
            "rewriting": "Rewrite the text from the attached PDF to improve clarity and flow.",
            "summarizing": "Summarize the text from the attached PDF concisely.",
            "verbatim": "Format the text from the attached PDF as-is.",
        }[mode]

        prompt = f"""
        {action_prompt}
        
        Format the output as a proper LaTeX document. Where a figure or image 
        would logically appear, insert a placeholder comment in the format:
        %%FIGURE_PLACEHOLDER_n%%, where 'n' is a sequential 1-based index.
        
        Ensure the output is only the LaTeX code, starting with \\documentclass{{article}}.
        Make sure to include all the packages used in the LaTeX code.
        Do not include any other explanations or preamble.
        """
        
        pdf_file = genai.upload_file(path=pdf_path, display_name=os.path.basename(pdf_path))
        print(f"Uploaded '{pdf_file.display_name}' to Gemini.")

        try:
            response = self.model.generate_content([prompt, pdf_file])
            # Clean response to get only the code
            code = response.text.strip()
            if code.startswith("```latex"):
                code = code[len("```latex"):].strip()
            elif code.startswith("```"):
                code = code[len("```"):].strip()
            if code.endswith("```"):
                code = code[:-len("```")].strip()

            print("Text to LaTeX conversion complete.")
            return code
        finally:
            # Clean up the uploaded file
            genai.delete_file(pdf_file.name)
            print(f"Cleaned up uploaded file: {pdf_file.display_name}")


    def get_figure_descriptions(self, pdf_images: list[Image.Image]) -> list[str]:
        """
        Uses a vision model to find and describe figures on PDF pages.

        Args:
            pdf_images: A list of PIL Images, one for each page of the PDF.

        Returns:
            A numbered list of descriptions for each figure found.
        """
        print("Generating figure descriptions from PDF pages...")
        prompt = """
        Analyze the following page images. Identify each distinct figure, chart, or diagram.
        For each one you find, provide a detailed, one-sentence description.
        
        Format your response as a numbered list. For example:
        1. A bar chart showing quarterly profits.
        2. A diagram of the system architecture.
        
        If no figures are found, respond with "No figures found.".
        """
        
        response = self.model.generate_content([prompt] + pdf_images)
        print(f"Found descriptions: \n{response.text}")

        # Simple parsing of the numbered list response
        descriptions = [
            line.strip().split('. ', 1)[1] 
            for line in response.text.split('\n') 
            if line.strip() and '. ' in line and line.strip()[0].isdigit()
        ]
        return descriptions

    def generate_figure_code(self, description: str) -> str:
        """
        Generates Asymptote code for a figure based on its description.

        Args:
            description: The text description of the figure.

        Returns:
            A string containing Asymptote code.
        """
        print(f"Generating Asymptote code for: '{description}'")
        prompt = f"""
        Generate Asymptote code to create a vector graphic for the following description.
        The code should be self-contained and ready to compile with 'asy'.
        The output must only be the raw Asymptote code inside a code block. Do not include any explanations.

        Description: "{description}"
        """
        response = self.model.generate_content(prompt)

        # Clean response to get only the code
        code = response.text.strip()
        if code.startswith("```asy"):
            code = code[len("```asy"):].strip()
        elif code.startswith("```"):
            code = code[len("```"):].strip()
        if code.endswith("```"):
            code = code[:-len("```")].strip()
            
        return code


    def merge_latex_and_figures(
        self, latex_template: str, figure_files: list[str]
    ) -> str:
        """
        Merges the LaTeX template with generated figure files by replacing placeholders.

        Args:
            latex_template: The LaTeX document with %%FIGURE_PLACEHOLDER_n%% comments.
            figure_files: A list of file paths for the generated Asymptote .tex files.

        Returns:
            The final, complete LaTeX document as a string.
        """
        print("Merging generated text with figures...")
        final_latex = latex_template
        for i, fig_path in enumerate(figure_files):
            placeholder = f"%%FIGURE_PLACEHOLDER_{i+1}%%"

            # Asymptote generates a .tex file that can be included
            figure_include_code = f"""
\\begin{{figure}}[htbp]
    \\centering
    \\includegraphics{{{fig_path}}}
    \\caption{{Generated Figure {i+1}.}}
    \\label{{fig:gen{i+1}}}
\\end{{figure}}
"""
            final_latex = final_latex.replace(placeholder, figure_include_code.strip())

        # # Add asymptote package to preamble if not already there
        # if "\\usepackage{asymptote}" not in final_latex and figure_files:
        #     # More robustly add the package after the documentclass line
        #     doc_class_line = final_latex.split('\n')[0]
        #     final_latex = final_latex.replace(
        #         doc_class_line, 
        #         f"{doc_class_line}\n\\usepackage[inline]{{asymptote}}"
        #     )

        print("Merging complete.")
        return final_latex
