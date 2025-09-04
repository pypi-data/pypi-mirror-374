import argparse
import json
import os

from dotenv import load_dotenv

from .extract import Extractor
from .provider.provider import SupportedModels
from .video_utils import cleanup_temp_files, extract_frames_and_audio


def output_result(result, output_file=None):
    """Output result to file or console."""
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
        except Exception as e:
            # If file output fails, fallback to console output
            print(json.dumps({"status": "error", "message": f"Failed to write to output file: {e}"}))

    print(json.dumps(result))


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Extract descriptions from media files."
    )
    parser.add_argument("video_path", help="Path to the video file to describe.")
    parser.add_argument(
        "--model",
        default="gemini",
        help=f"The AI model to use for extraction. Supported models: {', '.join([m.value for m in SupportedModels])}. (default: gemini)",
    )
    parser.add_argument(
        "--image-model",
        help=f"The AI model to use for image extraction. Supported models: {', '.join([m.value for m in SupportedModels])}. (default: value of --model)",
    )
    parser.add_argument(
        "--audio-model",
        help=f"The AI model to use for audio extraction. Supported models: {', '.join([m.value for m in SupportedModels])}. (default: value of --model)",
    )
    parser.add_argument(
        "--media-type",
        choices=["video", "image", "audio"],
        default="video",
        help="Type of media to process (default: video)",
    )
    parser.add_argument(
        "--output",
        help="Specify a file path to write the JSON output to instead of console.",
    )
    parser.add_argument(
        "--prompt-file",
        help="Path to a JSON file containing custom prompts for the extractor.",
    )
    args = parser.parse_args()

    try:
        extractor = Extractor(
            model=args.model, image_model=args.image_model, audio_model=args.audio_model, prompt_file=args.prompt_file
        )

        if args.media_type == "video":
            extraction_result = extractor.describe_video(args.video_path)
            # Output JSON instead of plain text
            result = {
                "status": "success",
                "media_type": "video",
                "description": extraction_result.description,
                "input_tokens": extraction_result.input_tokens,
                "output_tokens": extraction_result.output_tokens,
                "file": args.output,
            }
            output_result(result, args.output)
        elif args.media_type == "image":
            # Extract frames from video and process as image
            frame_files, _ = extract_frames_and_audio(args.video_path)

            try:
                if frame_files:
                    # Process all frames in a single request
                    extraction_result = extractor.describe_images(frame_files)
                    # Output JSON instead of plain text
                    result = {
                        "status": "success",
                        "media_type": "image",
                        "description": extraction_result.description,
                        "input_tokens": extraction_result.input_tokens,
                        "output_tokens": extraction_result.output_tokens,
                        "file": args.output,
                    }
                    output_result(result, args.output)
                else:
                    # Output error as JSON
                    result = {
                        "status": "error",
                        "message": "No frames extracted from video.",
                    }
                    output_result(result, args.output)
            finally:
                # Clean up temporary files
                cleanup_temp_files(frame_files, None)
        elif args.media_type == "audio":
            # Extract audio from video and process as audio
            _, audio_path = extract_frames_and_audio(args.video_path)

            try:
                if audio_path:
                    extraction_result = extractor.describe_audio(audio_path)
                    # Output JSON instead of plain text
                    result = {
                        "status": "success",
                        "media_type": "audio",
                        "description": extraction_result.description,
                        "input_tokens": extraction_result.input_tokens,
                        "output_tokens": extraction_result.output_tokens,
                        "file": args.output,
                    }
                    output_result(result, args.output)
                else:
                    # Output error as JSON
                    result = {
                        "status": "error",
                        "message": "No audio extracted from video.",
                    }
                    output_result(result, args.output)
            finally:
                # Clean up temporary files
                cleanup_temp_files([], audio_path)
    except ValueError as e:
        # Output error as JSON
        result = {"status": "error", "message": str(e)}
        output_result(result, args.output)
    except Exception as e:
        # Output error as JSON
        result = {"status": "error", "message": f"An unexpected error occurred: {e}"}
        output_result(result, args.output)


if __name__ == "__main__":
    main()

