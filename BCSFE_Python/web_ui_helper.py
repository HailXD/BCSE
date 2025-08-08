import json
from typing import Any

from . import parse_save
from . import helper

def read_file_string_virtual(file_path: str, create: bool = False) -> str:
    """Reads a file from the virtual file system and returns its contents as a string"""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError as err:
        if create:
            # In a web context, we can't just create files anywhere.
            # This should be handled more gracefully if needed.
            return ""
        raise Exception(f"File not found in virtual FS: {file_path}") from err
    except UnicodeDecodeError as err:
        raise Exception(f"Error reading file: {file_path}: {err}") from err

def get_country_code_web(save_data: bytes) -> str:
    """
    For the web version, we'll need to ask the user for the country code
    if it's not detectable. For now, let's default to 'en' if undetectable.
    """
    from . import patcher
    country_code = patcher.detect_game_version(save_data)
    if country_code is None:
        return "en" # Default to 'en' for now
    return country_code

def exit_editor_web():
    raise Exception("System exit called")

def parse_save_data_web(save_data_bytes: bytes, country_code: str) -> str:
    """
    Parses the save data for the web UI.
    It monkey-patches functions that don't work in a browser environment.
    """
    # Monkey-patch helper functions
    helper.read_file_string = read_file_string_virtual
    helper.get_country_code = get_country_code_web
    helper.colored_text = lambda *args, **kwargs: None # Disable colored text
    helper.exit_editor = exit_editor_web

    save_stats = parse_save.start_parse(save_data_bytes, country_code)
    
    # Convert the parsed data to a JSON string
    # We need a custom converter for bytes objects
    def default_converter(o: Any) -> Any:
        if isinstance(o, bytes):
            return o.decode('utf-8', 'ignore')
        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

    return json.dumps(save_stats, indent=4, default=default_converter)

def serialise_save_data_web(save_data_json: str) -> bytes:
    """
    Serialises the save data for the web UI.
    """
    save_stats = json.loads(save_data_json)
    
    # The serialise_save.start_serialize function will need the same monkey-patching
    # as the parsing function if it uses any of the problematic helper functions.
    # For now, we assume it doesn't for simplicity.
    
    from . import serialise_save
    save_data_bytes = serialise_save.start_serialize(save_stats)
    
    return save_data_bytes
