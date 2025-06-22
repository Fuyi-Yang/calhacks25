# utils/latex_renderer.py
import subprocess
import os
import tempfile

class LatexRenderer:
    """A utility to compile Asymptote code."""

    @staticmethod
    def compile_asymptote(asy_code: str, output_dir: str, filename_base: str) -> bool:
        """
        Compiles a string of Asymptote code into a TeX file.
        
        Note: Requires the 'asy' command-line tool to be installed.
        
        Args:
            asy_code: The Asymptote code as a string.
            output_dir: The directory to save the output files.
            filename_base: The base name for the output file (e.g., 'figure1').
            
        Returns:
            True if compilation was successful, False otherwise.
        """
        print(f"Attempting to render {filename_base}.asy...")
        
        # Asymptote works best when run from the target directory
        original_cwd = os.getcwd()
        asy_filepath = os.path.join(output_dir, f"{filename_base}.asy")
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            with open(asy_filepath, "w") as f:
                f.write(asy_code)

            os.chdir(output_dir)
            
            # Run asymptote, which will produce a .tex file for inclusion
            result = subprocess.run(
                ['asy', '-f', 'pdf', f'{filename_base}.asy'],
                capture_output=True,
                text=True,
                check=True # Raises CalledProcessError on non-zero exit codes
            )
            print(f"Successfully rendered {filename_base}.pdf.")
            return True
        except FileNotFoundError:
            print("\n---")
            print("ERROR: The 'asy' command was not found.")
            print("Please install Asymptote and ensure it is in your system's PATH.")
            print("---\n")
            return False
        except subprocess.CalledProcessError as e:
            print(f"Failed to compile {filename_base}.asy.")
            print(f"Stderr: {e.stderr}")
            return False
        finally:
            os.chdir(original_cwd) # Always change back to the original directory