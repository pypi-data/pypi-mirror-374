#!/usr/bin/env python3
"""
This module handles configuration management for the EPUB reader.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

import psutil

# Set up logging
logger = logging.getLogger(__name__)

# Define the path for the configuration file
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "speakub")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Define default configuration settings
DEFAULT_CONFIG: Dict[str, Any] = {
    "language": "en",
    "voice_rate": "+20%",
    "pitch": "default",
    "volume": "default",
    "tts_enabled": True,
    "reading_speed": 200,  # Words per minute
    "theme": "default",
    "font_size": 12,
    # TTS settings for centralized configuration
    "tts": {
        "rate": 0,  # TTS rate adjustment (-100 to +100)
        "volume": 100,  # TTS volume (0-100)
        "pitch": "+0Hz",  # TTS pitch adjustment
        "smooth_mode": False,  # Smooth TTS mode enabled/disabled
    },
    # Hardware-aware cache configuration
    "cache": {
        "auto_detect_hardware": True,
        "chapter_cache_size": 50,  # Default fallback
        "width_cache_size": 1000,  # Default fallback
        "hardware_profile": "auto",  # auto, low_end, mid_range, high_end
    },
}


def load_config() -> Dict[str, Any]:
    """
    Loads the configuration from the JSON file.
    If the file doesn't exist, it creates one with default settings.

    Returns:
        Dict[str, Any]: The configuration dictionary.
    """
    if not os.path.exists(CONFIG_FILE):
        logger.debug("Configuration file not found. Creating with default settings.")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            # Merge with defaults to ensure all keys are present
            merged_config = DEFAULT_CONFIG.copy()
            merged_config.update(config)
            return merged_config
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"Error loading configuration file: {e}")
        # Fallback to default configuration
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    """
    Saves the configuration to the JSON file.

    Args:
        config (Dict[str, Any]): The configuration dictionary to save.
    """
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        logger.debug(f"Configuration saved to {CONFIG_FILE}")
    except IOError as e:
        logger.error(f"Error saving configuration file: {e}")


def detect_hardware_profile() -> str:
    """
    Detect hardware profile based on system resources.

    Returns:
        str: Hardware profile ('low_end', 'mid_range', 'high_end')
    """
    try:
        # Get system memory in GB
        memory_gb = psutil.virtual_memory().total / (1024**3)

        # Get CPU core count
        cpu_count = psutil.cpu_count(logical=True)

        # Get CPU frequency if available
        try:
            cpu_freq_info = psutil.cpu_freq()
            cpu_freq = cpu_freq_info.max if cpu_freq_info else 0
        except Exception:
            cpu_freq = 0

        logger.debug(f"Hardware detection: {cpu_count} cores, "
                     f"{memory_gb:.1f}GB RAM, {cpu_freq:.0f}MHz CPU")

        # Classification logic
        if (memory_gb is not None and memory_gb <= 4) or \
           (cpu_count is not None and cpu_count <= 2):
            return "low_end"
        elif (memory_gb is not None and memory_gb <= 8) or \
             (cpu_count is not None and cpu_count <= 4):
            return "mid_range"
        else:
            return "high_end"

    except Exception as e:
        logger.warning(f"Hardware detection failed: {e}, using mid_range as fallback")
        return "mid_range"


def get_cache_sizes_for_profile(profile: str) -> Dict[str, int]:
    """
    Get recommended cache sizes for a hardware profile.

    Args:
        profile: Hardware profile ('low_end', 'mid_range', 'high_end')

    Returns:
        Dict with chapter_cache_size and width_cache_size
    """
    profiles = {
        "low_end": {
            "chapter_cache_size": 10,  # Minimal cache for low memory
            "width_cache_size": 200,
        },
        "mid_range": {
            "chapter_cache_size": 25,  # Balanced cache
            "width_cache_size": 500,
        },
        "high_end": {
            "chapter_cache_size": 50,  # Maximum cache for performance
            "width_cache_size": 1000,
        },
    }

    return profiles.get(profile, profiles["mid_range"])


def get_adaptive_cache_config() -> Dict[str, int]:
    """
    Get adaptive cache configuration based on detected hardware.

    Returns:
        Dict with chapter_cache_size and width_cache_size
    """
    try:
        profile = detect_hardware_profile()
        cache_sizes = get_cache_sizes_for_profile(profile)
        logger.debug(f"Adaptive cache config for {profile} hardware: {cache_sizes}")
        return cache_sizes
    except Exception as e:
        logger.warning(f"Failed to get adaptive cache config: {e}, using defaults")
        return {"chapter_cache_size": 50, "width_cache_size": 1000}


def get_cache_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, int]:
    """
    Get cache configuration, either from config file or auto-detected.

    Args:
        config: Configuration dictionary (if None, loads from file)

    Returns:
        Dict with chapter_cache_size and width_cache_size
    """
    if config is None:
        config = load_config()

    cache_config = config.get("cache", {})

    # Check if auto-detection is enabled
    if cache_config.get("auto_detect_hardware", True):
        # Use hardware detection
        adaptive_config = get_adaptive_cache_config()

        # Allow manual override
        chapter_size = cache_config.get(
            "chapter_cache_size", adaptive_config["chapter_cache_size"]
        )
        width_size = cache_config.get(
            "width_cache_size", adaptive_config["width_cache_size"]
        )

        return {"chapter_cache_size": chapter_size, "width_cache_size": width_size}
    else:
        # Use manual configuration
        return {
            "chapter_cache_size": cache_config.get("chapter_cache_size", 50),
            "width_cache_size": cache_config.get("width_cache_size", 1000),
        }


def get_tts_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get TTS configuration from config file.

    Args:
        config: Configuration dictionary (if None, loads from file)

    Returns:
        Dict with TTS settings (rate, volume, pitch, smooth_mode)
    """
    if config is None:
        config = load_config()

    tts_config = config.get("tts", {})
    default_tts = DEFAULT_CONFIG["tts"]

    # Merge with defaults to ensure all keys are present
    merged_tts = default_tts.copy()
    merged_tts.update(tts_config)

    return merged_tts


def save_tts_config(tts_config: Dict[str, Any]) -> None:
    """
    Save TTS configuration to config file.

    Args:
        tts_config: TTS configuration dictionary to save
    """
    try:
        config = load_config()
        config["tts"] = tts_config
        save_config(config)
        logger.debug("TTS configuration saved")
    except Exception as e:
        logger.error(f"Error saving TTS configuration: {e}")


def validate_tts_config(tts_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize TTS configuration values.

    Args:
        tts_config: TTS configuration to validate

    Returns:
        Validated TTS configuration with sanitized values
    """
    validated = {}

    # Validate rate (-100 to +100)
    rate = tts_config.get("rate", 0)
    validated["rate"] = max(-100, min(100, rate))

    # Validate volume (0 to 100)
    volume = tts_config.get("volume", 100)
    validated["volume"] = max(0, min(100, volume))

    # Validate pitch (string format like "+0Hz", "-10Hz", etc.)
    pitch = tts_config.get("pitch", "+0Hz")
    if isinstance(pitch, str) and pitch.endswith("Hz"):
        try:
            # Extract numeric part
            pitch_value = int(pitch[:-2])
            # Clamp to reasonable range (-50 to +50)
            pitch_value = max(-50, min(50, pitch_value))
            validated["pitch"] = f"{pitch_value:+}Hz"
        except ValueError:
            validated["pitch"] = "+0Hz"
    else:
        validated["pitch"] = "+0Hz"

    # Validate smooth_mode (boolean)
    validated["smooth_mode"] = bool(tts_config.get("smooth_mode", False))

    return validated


# Define the path for the pronunciation corrections file
CORRECTIONS_FILE = os.path.join(CONFIG_DIR, "corrections.json")


def save_pronunciation_corrections(corrections: Dict[str, str]) -> None:
    """
    Save pronunciation corrections to JSON file.

    Args:
        corrections: Corrections dictionary to save
    """
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)

        # If corrections is empty, create file with instructions and examples
        if not corrections:
            instructions_content = {
                "_comment": "Chinese Pronunciation Corrections Configuration",
                "_instructions": "Add your correction rules below in format: "
                                 "'original': 'corrected'",
                "_examples": {
                    "生長": "生掌",
                    "長": "常"
                }
            }
            with open(CORRECTIONS_FILE, "w", encoding="utf-8") as f:
                json.dump(instructions_content, f, indent=4, ensure_ascii=False)
        else:
            with open(CORRECTIONS_FILE, "w", encoding="utf-8") as f:
                json.dump(corrections, f, indent=4, ensure_ascii=False)

        logger.debug(f"Pronunciation corrections saved to {CORRECTIONS_FILE}")
    except IOError as e:
        logger.error(f"Error saving pronunciation corrections file: {e}")


def load_pronunciation_corrections() -> Dict[str, str]:
    """
    Load pronunciation corrections from external JSON file.
    The file should be a JSON object (dictionary) with "original": "correction" format.
    If the file doesn't exist, creates an empty one for user customization.

    Returns:
        Dict[str, str]: Corrections dictionary.
    """
    if not os.path.exists(CORRECTIONS_FILE):
        logger.debug("Corrections file not found. Skipping pronunciation corrections.")
        return {}

    try:
        with open(CORRECTIONS_FILE, "r", encoding="utf-8") as f:
            corrections = json.load(f)
            if not isinstance(corrections, dict):
                logger.warning(
                    f"'{CORRECTIONS_FILE}' root element is not a JSON object (dict), ignored.")
                return {}

            # Validate content is string: string, exclude instruction keys
            validated_corrections = {
                k: v for k, v in corrections.items()
                if isinstance(k, str) and isinstance(v, str) and not k.startswith('_')
            }

            logger.debug("Successfully loaded "
                         f"{len(validated_corrections)} pronunciation correction "
                         f"rules from '{CORRECTIONS_FILE}'.")
            return validated_corrections

    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"Error reading or parsing '{CORRECTIONS_FILE}': {e}")
        return {}


# Example usage (for testing)
if __name__ == "__main__":
    # Test loading config
    print("Loading configuration...")
    my_config = load_config()
    print("Current config:", my_config)

    # Test modifying and saving config
    print("\nModifying configuration...")
    my_config["language"] = "fr"
    my_config["font_size"] = 14
    save_config(my_config)

    # Test reloading config
    print("\nReloading configuration...")
    reloaded_config = load_config()
    print("Reloaded config:", reloaded_config)
    assert reloaded_config["language"] == "fr"
    assert reloaded_config["font_size"] == 14

    # Restore default settings
    print("\nRestoring default configuration...")
    save_config(DEFAULT_CONFIG)
    final_config = load_config()
    print("Final config:", final_config)
    assert final_config["language"] == "en"

    print("\nConfiguration management test complete.")
