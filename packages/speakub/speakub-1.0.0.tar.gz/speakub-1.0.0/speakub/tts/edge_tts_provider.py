#!/usr/bin/env python3
"""
Edge-TTS Provider - Microsoft Edge TTS implementation.
"""

import asyncio
import tempfile
from typing import Any, Dict, List, Optional

try:
    import edge_tts

    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

from speakub.tts.audio_player import AudioPlayer
from speakub.tts.engine import TTSEngine, TTSState


class EdgeTTSProvider(TTSEngine):
    """Microsoft Edge TTS provider."""

    DEFAULT_VOICES = {
        "en-US": "en-US-AriaNeural",
        "zh-CN": "zh-CN-XiaoxiaoNeural",
        "zh-TW": "zh-TW-HsiaoChenNeural",
        "ja-JP": "ja-JP-NanamiNeural",
        "ko-KR": "ko-KR-SunHiNeural",
    }

    def __init__(self):
        """Initialize Edge TTS provider."""
        super().__init__()

        if not EDGE_TTS_AVAILABLE:
            raise ImportError(
                "edge-tts package not installed. Install with: pip install edge-tts"
            )

        self.audio_player = AudioPlayer()
        self._voices_cache: Optional[List[Dict[str, Any]]] = None
        self._current_voice = self.DEFAULT_VOICES.get("zh-TW", "zh-TW-HsiaoChenNeural")

        # Set up audio player callbacks
        self.audio_player.on_state_changed = self._on_audio_state_changed
        self.audio_player.on_position_changed = self._update_position
        self.audio_player.on_error = self._report_error

    def _on_audio_state_changed(self, player_state: str) -> None:
        """Handle audio player state changes."""
        state_mapping = {
            "playing": TTSState.PLAYING,
            "paused": TTSState.PAUSED,
            "stopped": TTSState.STOPPED,
            "finished": TTSState.IDLE,
            "error": TTSState.ERROR,
        }

        if player_state in state_mapping:
            self._change_state(state_mapping[player_state])

    async def synthesize(self, text: str, voice: str = "default", **kwargs) -> bytes:
        """
        Synthesize text using Edge TTS.
        """
        if not EDGE_TTS_AVAILABLE:
            raise RuntimeError("Edge TTS not available")

        if voice == "default":
            voice = self._current_voice

        rate = kwargs.get("rate", "+0%")
        pitch = kwargs.get("pitch", "+0Hz")
        volume = kwargs.get("volume", "+0%")

        communicate = edge_tts.Communicate(
            text=text, voice=voice, rate=rate, pitch=pitch, volume=volume
        )

        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]

        return audio_data

    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available Edge TTS voices.
        """
        if not EDGE_TTS_AVAILABLE:
            return []

        if self._voices_cache is None:
            try:
                voices = await edge_tts.list_voices()
                self._voices_cache = []

                for voice in voices:
                    voice_info = {
                        "name": voice.get("Name", ""),
                        "short_name": voice.get("ShortName", ""),
                        "gender": voice.get("Gender", ""),
                        "locale": voice.get("Locale", ""),
                        "display_name": voice.get(
                            "DisplayName", voice.get("FriendlyName", "")
                        ),
                        "local_name": voice.get(
                            "LocalName", voice.get("ShortName", "")
                        ),
                        "style_list": voice.get("StyleList", []),
                        "sample_rate_hertz": voice.get("SampleRateHertz", 24000),
                        "voice_type": voice.get("VoiceType", "Neural"),
                    }
                    self._voices_cache.append(voice_info)

            except Exception as e:
                print(f"DEBUG: Failed to get voices: {e}")
                import traceback

                traceback.print_exc()
                self._report_error(f"Failed to get voices: {e}")
                return []

        return self._voices_cache or []

    def get_voices_by_language(self, language: str) -> List[Dict[str, Any]]:
        """
        Get voices for a specific language.
        """
        if not self._voices_cache:
            # Don't try to fetch voices synchronously in test environment
            # Just return empty list and let caller handle it
            return []

        return [
            voice
            for voice in (self._voices_cache or [])
            if voice["locale"].startswith(language)
        ]

    def set_voice(self, voice_name: str) -> bool:
        """
        Set the current voice.
        """
        if not voice_name:
            return False

        # Check if it's a valid voice name format (contains language-region-voice pattern)
        # or if it's in our default voices
        if voice_name in self.DEFAULT_VOICES.values():
            self._current_voice = voice_name
            return True

        # Check for valid voice name pattern: xx-XX-Name format
        import re

        if re.match(r"^[a-z]{2}-[A-Z]{2}-[A-Za-z]+Neural$", voice_name):
            self._current_voice = voice_name
            return True

        return False

    def get_current_voice(self) -> str:
        """Get the currently selected voice."""
        return self._current_voice

    # ***** START OF FIX *****
    # This method is now async and will wait for playback to finish.
    async def play_audio(self, audio_data: bytes) -> None:
        """
        Play audio data using the audio player and wait for completion.
        """
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_file.flush()

            self.audio_player.load_file(temp_file.name)

            # Run the blocking play_and_wait in a separate thread
            # so it doesn't block the main asyncio event loop.
            await asyncio.to_thread(self.audio_player.play_and_wait)

    # ***** END OF FIX *****

    def pause(self) -> None:
        """Pause audio playback."""
        self.audio_player.pause()

    def resume(self) -> None:
        """Resume audio playback."""
        self.audio_player.resume()

    def stop(self) -> None:
        """Stop audio playback."""
        self.audio_player.stop()

    def seek(self, position: int) -> None:
        """
        Seek to position in audio.
        """
        self.audio_player.seek(position)

    def set_volume(self, volume: float) -> None:
        """
        Set playback volume.
        """
        self.audio_player.set_volume(volume)

    def get_volume(self) -> float:
        """Get current volume level."""
        return self.audio_player.get_volume()

    def set_speed(self, speed: float) -> None:
        """
        Set playback speed.
        """
        self.audio_player.set_speed(speed)

    def get_speed(self) -> float:
        """Get current playback speed."""
        return self.audio_player.get_speed()

    def set_pitch(self, pitch: str) -> None:
        """
        Set TTS pitch.

        Args:
            pitch: Pitch value (e.g., "+10Hz", "-5Hz", "+0Hz")
        """
        # Pitch is used during synthesis, not playback
        # This is a placeholder for future implementation
        pass

    def get_pitch(self) -> str:
        """Get current TTS pitch."""
        # Return default pitch since it's synthesis-time parameter
        return "+0Hz"
