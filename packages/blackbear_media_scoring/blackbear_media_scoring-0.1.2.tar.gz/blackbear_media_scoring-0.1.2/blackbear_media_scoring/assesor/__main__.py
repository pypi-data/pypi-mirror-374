import argparse
import json
import os

from dotenv import load_dotenv

from blackbear_media_scoring.assesor.assess import Assessor


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Assess text for sensitive content.")
    parser.add_argument(
        "text",
        nargs='?',
        help="The text content to be scored. Use --input-type=file to read from a file instead."
    )
    parser.add_argument(
        "--input-type",
        help="Specify 'file' to read text from a file. Provide the file path as the text argument.",
        choices=['file']
    )
    parser.add_argument(
        "--model",
        default="gemini",
        help="The LLM model to use for assessment. Supported models: gemini, openrouter (default: gemini)",
    )
    parser.add_argument(
        "--prompt-file",
        help="Path to a text file containing a custom prompt template for the assessor.",
    )
    args = parser.parse_args()

    # Validate arguments
    if args.input_type == 'file':
        if not args.text:
            print(json.dumps({"status": "error", "message": "File path must be provided when using --input-type=file"}))
            return
        if not os.path.exists(args.text):
            print(json.dumps({"status": "error", "message": f"File not found: {args.text}"}))
            return
        try:
            with open(args.text, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except Exception as e:
            print(json.dumps({"status": "error", "message": f"Error reading file: {e}"}))
            return
    else:
        if not args.text:
            print(json.dumps({"status": "error", "message": "Text content must be provided as an argument or through --input-type=file"}))
            return
        text_content = args.text

    try:
        assessor = Assessor(model=args.model, prompt_file=args.prompt_file)
        score_result = assessor.score_text(text_content)
        result = {"status": "success", **score_result.to_dict()}
        print(json.dumps(result))
    except ValueError as e:
        result = {"status": "error", "message": f"Error: {e}"}
        print(json.dumps(result))
    except Exception as e:
        result = {"status": "error", "message": f"An unexpected error occurred: {e}"}
        print(json.dumps(result))


if __name__ == "__main__":
    main()
