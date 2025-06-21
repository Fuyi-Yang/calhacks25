# main.py

import argparse
from dotenv import load_dotenv
from document_processor import DocumentProcessor

def main():
    """Main function to parse arguments and run the document processor."""
    # Load environment variables from .env file
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Convert an image or PDF file to a LaTeX document with generated figures.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("input_file", type=str, help="Path to the input image or PDF file.")
    parser.add_argument(
        "-o", "--output_dir", type=str, default="output",
        help="Directory to save the output .tex file and figures (default: 'output')."
    )
    parser.add_argument(
        "-m", "--mode", type=str, choices=['rewriting', 'summarizing', 'verbatim'],
        default='verbatim',
        help="The mode for processing text:\n"
             "  rewriting:   Rewrite text for clarity.\n"
             "  summarizing: Summarize the text.\n"
             "  verbatim:    Keep original text, but format it. (default)"
    )
    
    args = parser.parse_args()

    try:
        processor = DocumentProcessor(
            input_path=args.input_file,
            output_dir=args.output_dir,
            text_mode=args.mode
        )
        processor.process()
    except Exception as e:
        print(f"\nAn error occurred during processing: {e}")

if __name__ == "__main__":
    main()