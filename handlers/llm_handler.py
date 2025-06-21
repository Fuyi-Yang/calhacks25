import os

import google.generativeai as genai
from PIL import Image


class GeminiLLM:
    """A handler for all interactions with the Google Gemini LLM."""

    def __init__(self):
        """Initializes the Gemini model."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        genai.configure(api_key=api_key)
        self.text_model = genai.GenerativeModel("gemini-2.5-pro")
        self.vision_model = genai.GenerativeModel("gemini-2.5-pro")

    def extract_text_to_latex(self, full_text: str, mode: str) -> str:
        """
        Uses an LLM to convert raw text into a LaTeX format.

        Args:
            full_text: The complete text extracted from the PDF.
            mode: Processing mode ('rewriting', 'summarizing', 'verbatim').

        Returns:
            A string containing the document in LaTeX format, with placeholders for figures.
        """
        print(f"Processing text in '{mode}' mode...")

        action_prompt = {
            "rewriting": "Rewrite the following text to improve clarity and flow.",
            "summarizing": "Summarize the following text concisely.",
            "verbatim": "Format the following text as-is.",
        }[mode]

        prompt = f"""
        {action_prompt}
        
        Format the output as a proper LaTeX document. Where a figure or image 
        would logically appear, insert a placeholder comment in the format:
        %%FIGURE_PLACEHOLDER_n%%, where 'n' is a sequential 1-based index.
        
        Ensure the output is only the LaTeX code, starting with \\documentclass{{article}}.
        
        TEXT:
        ---
        {full_text}
        ---
        """
        response = self.text_model.generate_content(prompt)
        print("Text to LaTeX conversion complete.")
        return response.text

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
        
        If no figures are found, return an empty list.
        """

        response = self.vision_model.generate_content([prompt] + pdf_images)
        print(f"Found descriptions: \n{response.text}")

        # Simple parsing of the numbered list response
        descriptions = [
            line.strip().split(". ", 1)[1]
            for line in response.text.split("\n")
            if ". " in line
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
        Do not include any explanations, just the raw Asymptote code.

        Description: "{description}"
        """
        response = self.text_model.generate_content(prompt)
        return response.text

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
            # We need to add the necessary package and the input command
            figure_include_code = f"""
\\begin{{figure}}[htbp]
    \\centering
    \\def\\asydir{{figures/}} % Define directory for asymptote
    \\input{{{fig_path}}}
    \\caption{{Generated Figure {i+1}.}}
    \\label{{fig:gen{i+1}}}
\\end{{figure}}
            """
            final_latex = final_latex.replace(placeholder, figure_include_code)

        # Add asymptote package to preamble if not already there
        if "\\usepackage{asymptote}" not in final_latex and figure_files:
            final_latex = final_latex.replace(
                "\\documentclass{article}",
                "\\documentclass{article}\n\\usepackage[inline]{asymptote}",
            )

        print("Merging complete.")
        return final_latex
