import json
import os


class ExtractorPrompts:
    def __init__(self, prompt_file=None):
        """
        Initialize ExtractorPrompts with optional custom prompt file.
        
        Args:
            prompt_file (str, optional): Path to JSON file containing custom prompts
        """
        self.suffix_descriptor = """Summarize it in 1-2 paragraphs only"""

        self.video_descriptor = f"""Act like you are a expert video descriptor.

Your primary function is to analyze and describe the visual and auditory content of
a provided video. Your descriptions must be accurate, comprehensive, and objective,
capturing the essence of the video while avoiding subjective interpretations or
emotional language. The goal is to provide a clear and concise summary that enables
users to understand the video's content without having to watch it.

{self.suffix_descriptor}
"""
            
        self.image_descriptor = f"""Act like you are an expert image descriptor.

Your primary function is to analyze and describe the visual content of a provided image.
Your descriptions must be accurate, comprehensive, and objective, capturing the essence
of the image while avoiding subjective interpretations or emotional language. The goal
is to provide a clear and concise summary that enables users to understand the image's
content without having to see it.

{self.suffix_descriptor}
"""
            
        self.audio_descriptor = f"""Act like you are an expert audio descriptor.

Your primary function is to analyze and describe the auditory content of a provided
audio file. Your descriptions must be accurate, comprehensive, and objective, capturing
the essence of the audio while avoiding subjective interpretations or emotional
language. The goal is to provide a clear and concise summary that enables users to
understand the audio's content without having to listen to it.

{self.suffix_descriptor}
"""
        
        # Load custom prompts if file is provided
        if prompt_file and os.path.exists(prompt_file):
            self._load_custom_prompts(prompt_file)

    def _load_custom_prompts(self, prompt_file):
        """
        Load custom prompts from a JSON file.
        
        Args:
            prompt_file (str): Path to JSON file containing custom prompts
        """
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                custom_prompts = json.load(f)
            
            # Use custom prompts or fall back to defaults
            if "video_descriptor" in custom_prompts:
                self.video_descriptor = custom_prompts.get('video_descriptor')
            
            if "image_descriptor" in custom_prompts:
                self.image_descriptor = custom_prompts.get('image_descriptor')
            
            if "audio_descriptor" in custom_prompts:
                self.audio_descriptor = custom_prompts.get('audio_descriptor')
        except Exception as e:
            # Fall back to default prompts if there's an error loading the file
            print(f"Warning: Failed to load custom prompts from {prompt_file}: {e}")