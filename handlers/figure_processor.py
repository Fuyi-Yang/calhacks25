# handlers/figure_processor.py

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from .llm_handler import GeminiLLM
from utils.latex_renderer import LatexRenderer

class FigureProcessor:
    """Processes figure descriptions in parallel to generate and render them."""
    
    MAX_RENDER_ATTEMPTS = 3 # Reduced for quicker failure

    def __init__(self, llm_handler: GeminiLLM, renderer: LatexRenderer, output_dir: str):
        self.llm = llm_handler
        self.renderer = renderer
        self.figures_output_dir = os.path.join(output_dir, 'figures')
        os.makedirs(self.figures_output_dir, exist_ok=True)

    def _process_single_figure(self, index: int, description: str) -> str | None:
        """
        Generates and renders code for a single figure. Includes a retry loop.
        
        Returns:
            The relative path to the generated .tex file on success, otherwise None.
        """

        current_description = description
        for attempt in range(self.MAX_RENDER_ATTEMPTS):
            print(f"Processing figure {index+1}, attempt {attempt+1}...")
            # Step 1: Generate Asymptote code from description
            asy_code = self.llm.generate_figure_code(current_description)
            
            if not asy_code:
                print(f"LLM failed to generate code for figure {index+1}.")
                continue

            # Step 2: Render the generated code
            filename_base = f"figure{index+1}"

            try:
                success = self.renderer.compile_asymptote(
                    asy_code, self.figures_output_dir, filename_base
                )

                if success:
                    # On success, save the source .asy file and return the path for the .tex file
                    asy_filepath = os.path.join(self.figures_output_dir, f"{filename_base}.asy")
                    with open(asy_filepath, "w") as f:
                        f.write(asy_code) # Overwrite with the successful code
                    
                    # The path to be used in the \input command, with forward slashes for TeX
                    relative_path = os.path.join('figures', f"{filename_base}.pdf")
                    return relative_path.replace(os.sep, '/')

            except Exception as e:
                current_description = description + "\n" + asy_code + "\nError: " + str(e)
            
#            if success:
#                # On success, save the source .asy file and return the path for the .tex file
#                asy_filepath = os.path.join(self.figures_output_dir, f"{filename_base}.asy")
#                with open(asy_filepath, "w") as f:
#                    f.write(asy_code) # Overwrite with the successful code
#                
#                # The path to be used in the \input command, with forward slashes for TeX
#                relative_path = os.path.join('figures', f"{filename_base}.pdf")
#                return relative_path.replace(os.sep, '/')

        print(f"Failed to generate and render figure {index+1} after {self.MAX_RENDER_ATTEMPTS} attempts.")
        return None

    def process_figures_in_parallel(self, descriptions: list[str]) -> list[str]:
        """
        Uses a thread pool to process all figure descriptions concurrently.
        
        Args:
            descriptions: A list of figure descriptions.
        
        Returns:
            A list of file paths for successfully generated figures.
        """
        successful_figures = [None] * len(descriptions)
        
        with ThreadPoolExecutor() as executor:
            future_to_index = {
                executor.submit(self._process_single_figure, i, desc): i
                for i, desc in enumerate(descriptions)
            }
            
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result_path = future.result()
                    if result_path:
                        print(f"Successfully processed figure {index + 1}.")
                        successful_figures[index] = result_path
                    else:
                        print(f"Error processing figure {index+1}")

                except Exception as e:
                    print(f"Error processing figure {index+1}: {e}")

        # Filter out None values from failed processes and maintain order
        return [path for path in successful_figures if path is not None]
