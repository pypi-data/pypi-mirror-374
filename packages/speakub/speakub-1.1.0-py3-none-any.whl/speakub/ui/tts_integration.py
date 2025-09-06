#!/usr/bin/env python3
"""
TTS integration for SpeakUB
"""

import asyncio
import socket
import threading
import time
from typing import TYPE_CHECKING, Optional, Tuple, Union
from speakub.utils.text_utils import correct_chinese_pronunciation

from speakub import TTS_AVAILABLE

if TYPE_CHECKING:
    from speakub.ui.app import EPUBReaderApp

if TTS_AVAILABLE:
    try:
        from speakub.tts.edge_tts_provider import EdgeTTSProvider
    except Exception:
        EdgeTTSProvider = None


class TTSIntegration:
    """Handles TTS functionality integration."""

    def __init__(self, app: "EPUBReaderApp"):
        self.app = app
        self.tts_thread: Optional[threading.Thread] = None
        self.tts_pre_synthesis_thread: Optional[threading.Thread] = None
        self.tts_lock = threading.RLock()
        # Type annotation for playlist items: (text, line_num) or (text, line_num, audio_data)
        self.tts_playlist: list[
            Union[Tuple[str, int], Tuple[str, int, Union[bytes, str]]]
        ] = []
        self.tts_playlist_index = 0
        self.tts_stop_requested = threading.Event()
        self.tts_thread_active = False
        self.last_tts_error = None

        # Event-driven synchronization objects to replace polling
        self.tts_synthesis_ready = threading.Event()
        self.tts_playback_ready = threading.Event()
        self.tts_data_available = threading.Event()

        # Network error handling
        self.network_error_occurred = False
        self.network_error_notified = False
        self.network_recovery_notified = False

    async def setup_tts(self) -> None:
        """Set up TTS engine."""
        if not TTS_AVAILABLE or EdgeTTSProvider is None:
            return
        try:
            self.app.tts_engine = EdgeTTSProvider()
            if hasattr(self.app.tts_engine, "start_async_loop"):
                self.app.tts_engine.start_async_loop()
        except Exception as e:
            self.app.tts_engine = None

    async def update_tts_progress(self) -> None:
        """Update TTS progress display."""
        try:
            from textual.widgets import Static

            # Update left component: TTS status
            status_widget = self.app.query_one("#tts-status", Static)
            status = self.app.tts_status.upper()
            smooth = " (Smooth)" if self.app.tts_smooth_mode else ""
            status_text = f"TTS: {status}{smooth}"
            status_widget.update(status_text)

            # Update center component: Progress + Vol + Speed + Pitch
            controls_widget = self.app.query_one("#tts-controls", Static)
            percent = None
            if status == "PLAYING" and self.tts_playlist:
                total, current = len(self.tts_playlist), self.tts_playlist_index
                if total > 0:
                    percent = int((current / total) * 100)
            p_disp = f"{percent}%" if percent is not None else "--"
            v_disp = f"{self.app.tts_volume}"
            s_disp = f"{self.app.tts_rate:+}"
            controls_text = f"{p_disp} | Vol: {v_disp}% | Speed: {s_disp}% | Pitch: {self.app.tts_pitch}"
            controls_widget.update(controls_text)

            # Update right component: Page info
            page_widget = self.app.query_one("#tts-page", Static)
            page_text = ""
            if self.app.viewport_content:
                info = self.app.viewport_content.get_viewport_info()
                page_text = f"Page {info['current_page'] + 1}/{info['total_pages']}"
            page_widget.update(page_text)
        except Exception:
            pass

    def prepare_tts_playlist(self) -> None:
        """Prepare TTS playlist from current content."""
        if not self.app.viewport_content:
            return
        with self.tts_lock:
            self.tts_playlist, self.tts_playlist_index = [], 0
            cursor_idx = self.app.viewport_content.get_cursor_global_position()
            para_info = self.app.viewport_content.line_to_paragraph_map.get(cursor_idx)
            if not para_info:
                for i in range(
                    cursor_idx, len(self.app.viewport_content.content_lines)
                ):
                    if self.app.viewport_content._is_content_line(
                        self.app.viewport_content.content_lines[i]
                    ):
                        para_info = self.app.viewport_content.line_to_paragraph_map.get(
                            i
                        )
                        break
                if not para_info:
                    return
            start_idx = para_info["index"]
            for p_info in self.app.viewport_content.paragraphs[start_idx:]:
                text = self.app.viewport_content.get_paragraph_text(p_info)
                if text.strip():
                    self.tts_playlist.append((text, p_info["start"]))

    def handle_tts_play_pause(self) -> None:
        """Handle TTS play/pause action."""
        with self.tts_lock:
            if self.app.tts_status == "PLAYING":
                self.stop_speaking(is_pause=True)
                self.app.tts_status = "PAUSED"
            # speakub/ui/tts_integration.py -> handle_tts_play_pause()
            elif self.app.tts_status == "PAUSED":
                if self.network_error_occurred:
                    self.reset_network_error_state()
                    # Directly call since we're already in the main thread
                    self.app.notify(
                        "Restarting TTS playback...",
                        title="TTS Resume",
                        severity="information",
                    )
                self.start_tts_thread()
            elif self.app.tts_status == "STOPPED":
                # Reset network error state if starting fresh after network error
                if self.network_error_occurred:
                    self.reset_network_error_state()
                self.prepare_tts_playlist()
                if self.tts_playlist:
                    self.start_tts_thread()
                else:
                    self.app.run_worker(
                        self._find_and_play_next_chapter_worker,
                        exclusive=True,
                        thread=True,
                    )

    def stop_speaking(self, is_pause: bool = False) -> None:
        """Stop TTS playback."""
        with self.tts_lock:
            if not self.tts_thread_active and self.app.tts_status != "PAUSED":
                if not is_pause:
                    self.app.tts_status = "STOPPED"
                return
            self.tts_stop_requested.set()
            if self.app.tts_engine and hasattr(self.app.tts_engine, "stop"):
                try:
                    self.app.tts_engine.stop()
                except Exception:
                    pass
            if self.tts_thread and self.tts_thread.is_alive():
                self.tts_thread.join(timeout=2.0)
            if (
                self.tts_pre_synthesis_thread
                and self.tts_pre_synthesis_thread.is_alive()
            ):
                self.tts_pre_synthesis_thread.join(timeout=2.0)
            self.tts_thread_active = False
            self.app.tts_status = "PAUSED" if is_pause else "STOPPED"
            if is_pause:
                if self.tts_playlist_index > 0:
                    self.tts_playlist_index -= 1
            else:
                self.tts_playlist, self.tts_playlist_index, self.last_tts_error = (
                    [],
                    0,
                    None,
                )

    def start_tts_thread(self) -> None:
        """Start TTS playback thread."""
        if self.tts_thread and self.tts_thread.is_alive():
            return
        self.tts_stop_requested.clear()
        self.app.tts_status = "PLAYING"
        if self.app.tts_smooth_mode:
            self.tts_thread = threading.Thread(
                target=self._tts_runner_parallel, daemon=True
            )
            self.tts_pre_synthesis_thread = threading.Thread(
                target=self._tts_pre_synthesis_worker, daemon=True
            )
            self.tts_thread.start()
            self.tts_pre_synthesis_thread.start()
        else:
            self.tts_thread = threading.Thread(
                target=self._tts_runner_serial, daemon=True
            )
            self.tts_thread.start()

    def speak_with_engine(self, text: str) -> None:
        """Speak text using TTS engine."""
        if not self.app.tts_engine:
            return
        try:
            # Apply Chinese pronunciation corrections before TTS
            corrected_text = correct_chinese_pronunciation(text)

            rate, volume = f"{self.app.tts_rate:+}%", f"{self.app.tts_volume - 100:+}%"
            kwargs = {"rate": rate, "volume": volume, "pitch": self.app.tts_pitch}
            if hasattr(self.app.tts_engine, "speak_text_sync"):
                self.app.tts_engine.speak_text_sync(corrected_text, **kwargs)
        except Exception as e:
            raise e

    def cleanup(self) -> None:
        """Clean up TTS resources."""
        if self.app.tts_status in ["PLAYING", "PAUSED"]:
            try:
                self.stop_speaking(is_pause=False)
            except Exception:
                pass
        if self.app.tts_widget:
            try:
                self.app.tts_widget.cleanup()
            except Exception:
                pass
        if self.app.tts_engine and hasattr(self.app.tts_engine, "stop_async_loop"):
            try:
                self.app.tts_engine.stop_async_loop()
            except Exception:
                pass

    # Private methods for TTS functionality
    def _tts_runner_serial(self) -> None:
        """Serial TTS runner."""
        with self.tts_lock:
            self.tts_thread_active = True
        try:
            while not self.tts_stop_requested.is_set():

                # At the start of each loop, check the main program's TTS status.
                # If the status is changed to PAUSED due to errors, etc., break out of the loop.
                if self.app.tts_status != "PLAYING":
                    break

                with self.tts_lock:
                    exhausted = self.tts_playlist_index >= len(self.tts_playlist)
                if exhausted:
                    if not self._tts_load_next_chapter():
                        break
                    else:
                        continue
                with self.tts_lock:
                    current_item = self.tts_playlist[self.tts_playlist_index]
                    text, line_num = current_item[0], current_item[1]
                    if self.app.viewport_content:
                        page, cursor = divmod(
                            line_num, self.app.viewport_content.viewport_height
                        )
                        self.app.viewport_content.current_page = min(
                            page, self.app.viewport_content.total_pages - 1
                        )
                        lines = len(
                            self.app.viewport_content.get_current_viewport_lines()
                        )
                        self.app.viewport_content.cursor_in_page = max(
                            0, min(cursor, lines - 1)
                        )
                        self.app.call_from_thread(self.app._update_content_display)
                if self.app.tts_engine:
                    try:
                        self.speak_with_engine(text)
                    except (
                        socket.gaierror,
                        socket.timeout,
                        ConnectionError,
                        OSError,
                    ) as e:
                        # Handle confirmed network errors - show notification and pause TTS
                        self.last_tts_error = str(e)
                        if not self.network_error_occurred:
                            self.network_error_occurred = True
                            self.network_error_notified = False
                            self.network_recovery_notified = False
                            # Start network monitoring in background
                            self.app.call_from_thread(
                                self.app.run_worker,
                                self._monitor_network_recovery,
                                exclusive=True,
                                thread=True,
                            )
                        # Show network error notification
                        if not self.network_error_notified:
                            error_msg = "Network connection interrupted, TTS paused. Press Space to continue after network recovery."
                            self.app.call_from_thread(
                                self.app.notify,
                                error_msg,
                                title="Network Error",
                                severity="warning",
                            )
                            self.network_error_notified = True
                        break  # Stop playback thread
                    except Exception as e:
                        # Handle other potential network errors with keyword matching
                        self.last_tts_error = str(e)

                        error_keywords = [
                            "network",
                            "connection",
                            "timeout",
                            "dns",
                            "host",
                            "socket",
                            "url",
                            "getaddrinfo",
                            "unreachable",
                            "nodename",
                            "servname",
                            "http",
                            "request",
                        ]
                        error_msg = str(e).lower()

                        if any(keyword in error_msg for keyword in error_keywords):
                            if not self.network_error_occurred:
                                self.network_error_occurred = True
                                self.network_error_notified = False
                                self.network_recovery_notified = False
                                # Start network monitoring in background
                                self.app.call_from_thread(
                                    self.app.run_worker,
                                    self._monitor_network_recovery,
                                    exclusive=True,
                                    thread=True,
                                )
                            # Show network error notification
                            if not self.network_error_notified:
                                error_msg = "Network connection interrupted, TTS paused. Press Space to continue after network recovery."
                                self.app.call_from_thread(
                                    self.app.notify,
                                    error_msg,
                                    title="Network Error",
                                    severity="warning",
                                )
                                self.network_error_notified = True
                            break  # Stop playback thread
                        else:
                            # Check for NoAudioReceived error (unpronounceable characters)
                            if (
                                "no audio was received" in str(e).lower()
                                or "noaudioreceived" in str(type(e).__name__).lower()
                            ):
                                # Skip unpronounceable text silently without notification
                                with self.tts_lock:
                                    self.tts_playlist_index += 1
                                continue
                            else:
                                # For other non-network errors, notify user
                                error_msg = f"TTS playback failed: {str(e)}"
                                if "timeout" in str(e).lower():
                                    error_msg = "TTS playback timed out. The service may be busy."
                                elif (
                                    "rate limit" in str(e).lower()
                                    or "quota" in str(e).lower()
                                ):
                                    error_msg = "TTS service rate limit exceeded. Please try again later."
                                else:
                                    error_msg = f"TTS playback failed: {str(e)}"
                                self.app.call_from_thread(
                                    self.app.notify,
                                    error_msg,
                                    title="TTS Playback Error",
                                    severity="error",
                                )
                                # Continue to next item instead of breaking
                                with self.tts_lock:
                                    self.tts_playlist_index += 1
                                continue
                with self.tts_lock:
                    self.tts_playlist_index += 1
        finally:
            with self.tts_lock:
                if self.app.tts_status == "PLAYING":
                    self.app.tts_status = "STOPPED"

    def _tts_load_next_chapter(self) -> bool:
        """Load next chapter for TTS."""
        with self.tts_lock:
            search_chapter = self.app.current_chapter
            while True:
                if not self.app.chapter_manager or not search_chapter:
                    return False
                next_chapter = self.app.chapter_manager.get_next_chapter(search_chapter)
                if not next_chapter:
                    return False
                try:
                    if not self.app.epub_parser or not self.app.content_renderer:
                        return False
                    html = self.app.epub_parser.read_chapter(next_chapter["src"])
                    lines = self.app.content_renderer.render_chapter(html)
                    if self.app.viewport_content:
                        temp_vp = self.app.viewport_content.__class__(
                            lines, self.app.current_viewport_height
                        )
                        new_playlist = []
                        for p in temp_vp.paragraphs:
                            text = temp_vp.get_paragraph_text(p)
                            if text.strip():
                                new_playlist.append((text, p["start"]))
                    else:
                        new_playlist = []
                    if new_playlist:
                        self.tts_playlist, self.tts_playlist_index = new_playlist, 0
                        self.app.call_from_thread(
                            self.app.run_worker,
                            self.app._load_chapter(next_chapter, from_start=True),
                        )
                        return True
                    else:
                        search_chapter = next_chapter
                except Exception:
                    return False

    def _find_and_play_next_chapter_worker(self) -> None:
        """Worker to find and play next chapter."""
        if self._tts_load_next_chapter():
            self.start_tts_thread()
        else:
            self.app.call_from_thread(
                self.app.notify, "No more content to read.", title="TTS"
            )
            self.app.tts_status = "STOPPED"

    def _tts_runner_parallel(self) -> None:
        """Parallel TTS runner."""
        with self.tts_lock:
            self.tts_thread_active = True
        try:
            while not self.tts_stop_requested.is_set():
                with self.tts_lock:
                    exhausted = self.tts_playlist_index >= len(self.tts_playlist)
                if exhausted:
                    if not self._tts_load_next_chapter():
                        break
                    else:
                        continue

                # Get current item
                with self.tts_lock:
                    if self.tts_playlist_index >= len(self.tts_playlist):
                        break
                    current_item = self.tts_playlist[self.tts_playlist_index]

                # Check if synthesis is ready or failed
                if len(current_item) == 3:
                    audio = current_item[2]

                    # Skip failed synthesis items
                    if audio == b"FAILED_SYNTHESIS":
                        with self.tts_lock:
                            self.tts_playlist_index += 1
                        continue

                    # Valid audio data - update UI before playing
                    with self.tts_lock:
                        text, line_num = current_item[0], current_item[1]
                        if self.app.viewport_content:
                            page, cursor = divmod(
                                line_num, self.app.viewport_content.viewport_height
                            )
                            self.app.viewport_content.current_page = min(
                                page, self.app.viewport_content.total_pages - 1
                            )
                            lines = len(
                                self.app.viewport_content.get_current_viewport_lines()
                            )
                            self.app.viewport_content.cursor_in_page = max(
                                0, min(cursor, lines - 1)
                            )
                            self.app.call_from_thread(self.app._update_content_display)

                    # Play audio and handle playback completion properly
                    if (
                        self.app.tts_engine
                        and hasattr(self.app.tts_engine, "_event_loop")
                        and self.app.tts_engine._event_loop
                    ):
                        try:
                            future = asyncio.run_coroutine_threadsafe(
                                self.app.tts_engine.play_audio(audio),
                                self.app.tts_engine._event_loop,
                            )
                            future.result()
                        except (
                            socket.gaierror,
                            socket.timeout,
                            ConnectionError,
                            OSError,
                        ) as e:
                            # Handle confirmed network errors in parallel playback
                            self.last_tts_error = str(e)
                            if not self.network_error_occurred:
                                self.network_error_occurred = True
                                self.network_error_notified = False
                                self.network_recovery_notified = False
                                # Start network monitoring in background
                                self.app.call_from_thread(
                                    self.app.run_worker,
                                    self._monitor_network_recovery,
                                    exclusive=True,
                                    thread=True,
                                )
                            # Show network error notification
                            if not self.network_error_notified:
                                error_msg = "Network connection interrupted, TTS paused. Press Space to continue after network recovery."
                                self.app.call_from_thread(
                                    self.app.notify,
                                    error_msg,
                                    title="Network Error",
                                    severity="warning",
                                )
                                self.network_error_notified = True
                            break  # Stop playback thread
                        except Exception as e:
                            # Handle other potential network errors with keyword matching
                            self.last_tts_error = f"Playback failed: {str(e)}"

                            error_keywords = [
                                "network",
                                "connection",
                                "timeout",
                                "dns",
                                "host",
                                "socket",
                                "url",
                                "getaddrinfo",
                                "unreachable",
                                "nodename",
                                "servname",
                                "http",
                                "request",
                            ]
                            error_msg = str(e).lower()

                            if any(keyword in error_msg for keyword in error_keywords):
                                if not self.network_error_occurred:
                                    self.network_error_occurred = True
                                    self.network_error_notified = False
                                    self.network_recovery_notified = False
                                    # Start network monitoring in background
                                    self.app.call_from_thread(
                                        self.app.run_worker,
                                        self._monitor_network_recovery,
                                        exclusive=True,
                                        thread=True,
                                    )
                                # Show network error notification
                                if not self.network_error_notified:
                                    error_msg = "Network connection interrupted, TTS paused. Press Space to continue after network recovery."
                                    self.app.call_from_thread(
                                        self.app.notify,
                                        error_msg,
                                        title="Network Error",
                                        severity="warning",
                                    )
                                    self.network_error_notified = True
                                break  # Stop playback thread
                            else:
                                # For non-network errors, notify user
                                playback_error_msg = f"TTS playback failed: {str(e)}"
                                if (
                                    "device" in str(e).lower()
                                    or "audio" in str(e).lower()
                                ):
                                    playback_error_msg = (
                                        "Audio device error. Check your audio settings."
                                    )
                                elif "format" in str(e).lower():
                                    playback_error_msg = "Audio format not supported. Try different TTS settings."
                                else:
                                    playback_error_msg = (
                                        f"TTS playback failed: {str(e)}"
                                    )
                                self.app.call_from_thread(
                                    self.app.notify,
                                    playback_error_msg,
                                    title="TTS Playback Error",
                                    severity="error",
                                )
                                # Continue to next item instead of breaking
                                with self.tts_lock:
                                    self.tts_playlist_index += 1
                                continue

                    # Only increment index after successful playback completion
                    with self.tts_lock:
                        self.tts_playlist_index += 1

                else:
                    # Synthesis not ready yet, wait for synthesis to complete
                    # Use event-driven waiting instead of polling
                    self.tts_synthesis_ready.clear()
                    # Wait for synthesis to be ready with timeout
                    synthesis_ready = self.tts_synthesis_ready.wait(timeout=0.1)
                    if not synthesis_ready:
                        # Timeout occurred, continue polling but less frequently
                        time.sleep(0.05)

        finally:
            with self.tts_lock:
                if self.app.tts_status == "PLAYING":
                    self.app.tts_status = "STOPPED"

    def _tts_pre_synthesis_worker(self) -> None:
        """Worker thread that synthesizes text ahead of time for smooth mode."""
        while not self.tts_stop_requested.is_set():
            try:
                text_to_synthesize = None
                target_index = -1
                with self.tts_lock:
                    current_idx = self.tts_playlist_index
                    limit = min(len(self.tts_playlist), current_idx + 3)
                for i in range(current_idx, limit):
                    with self.tts_lock:
                        if len(self.tts_playlist[i]) == 2:
                            text_to_synthesize = self.tts_playlist[i][0]
                            target_index = i
                            break
                if (
                    text_to_synthesize
                    and self.app.tts_engine
                    and hasattr(self.app.tts_engine, "synthesize")
                    and hasattr(self.app.tts_engine, "_event_loop")
                    and self.app.tts_engine._event_loop
                ):
                    audio_data = b"ERROR"
                    synthesis_success = False
                    try:
                        rate_str = f"{self.app.tts_rate:+}%"
                        volume_str = f"{self.app.tts_volume - 100:+}%"
                        corrected_text_to_synthesize = correct_chinese_pronunciation(
                            text_to_synthesize)
                        future = asyncio.run_coroutine_threadsafe(
                            self.app.tts_engine.synthesize(
                                corrected_text_to_synthesize,
                                rate=rate_str,
                                volume=volume_str,
                                pitch=self.app.tts_pitch,
                            ),
                            self.app.tts_engine._event_loop,
                        )
                        audio_data = future.result(timeout=60)

                        # Only mark as failed if Edge-TTS actually threw an exception
                        # Trust Edge-TTS's judgment - if it returns data, consider it successful
                        if audio_data is not None and audio_data != b"ERROR":
                            synthesis_success = True
                        else:
                            # Edge-TTS returned None or ERROR marker
                            audio_data = b"FAILED_SYNTHESIS"
                    except (
                        socket.gaierror,
                        socket.timeout,
                        ConnectionError,
                        OSError,
                    ) as e:
                        # Handle confirmed network errors in synthesis
                        self.last_tts_error = f"Synthesis failed for text: {text_to_synthesize[:50]}... Error: {str(e)}"
                        audio_data = b"FAILED_SYNTHESIS"

                        print(
                            f"DEBUG: Confirmed network error in synthesis: {type(e).__name__} - {str(e)}"
                        )

                        # Set global network error flag
                        if not self.network_error_occurred:
                            self.network_error_occurred = True
                            # Call central handler to pause TTS and notify user
                            self._handle_network_error(e, "synthesis")

                        break  # Stop synthesis worker
                    except Exception as e:
                        # Handle other potential network errors with keyword matching
                        self.last_tts_error = f"Synthesis failed for text: {text_to_synthesize[:50]}... Error: {str(e)}"
                        audio_data = b"FAILED_SYNTHESIS"

                        print(f"DEBUG: TTS Synthesis Error: {str(e)}")
                        print(f"DEBUG: Error type: {type(e).__name__}")

                        error_keywords = [
                            "network",
                            "connection",
                            "timeout",
                            "dns",
                            "host",
                            "socket",
                            "url",
                            "getaddrinfo",
                            "unreachable",
                            "nodename",
                            "servname",
                            "http",
                            "request",
                        ]
                        error_msg = str(e).lower()

                        if any(keyword in error_msg for keyword in error_keywords):
                            print(
                                "DEBUG: Network error detected via keywords in synthesis"
                            )

                            # Set global network error flag
                            if not self.network_error_occurred:
                                self.network_error_occurred = True
                                # Call central handler to pause TTS and notify user
                                self._handle_network_error(e, "synthesis")

                            break  # Stop synthesis worker
                        else:
                            # Check for NoAudioReceived error (unpronounceable characters)
                            if (
                                "no audio was received" in str(e).lower()
                                or "noaudioreceived" in str(type(e).__name__).lower()
                            ):
                                print(
                                    "DEBUG: NoAudioReceived error detected in synthesis - skipping silently"
                                )
                                # Mark as failed synthesis but don't show notification
                            else:
                                print("DEBUG: Non-network error detected in synthesis")
                                # For non-network errors, notify user
                                error_msg = f"TTS synthesis failed: {str(e)}"
                                if "timeout" in str(e).lower():
                                    error_msg = "TTS synthesis timed out. The service may be busy."
                                elif (
                                    "rate limit" in str(e).lower()
                                    or "quota" in str(e).lower()
                                ):
                                    error_msg = "TTS service rate limit exceeded. Please try again later."
                                else:
                                    error_msg = f"TTS synthesis failed: {str(e)}"
                                print(
                                    f"DEBUG: Sending synthesis error notification: {error_msg}"
                                )
                                self.app.call_from_thread(
                                    self.app.notify,
                                    error_msg,
                                    title="TTS Error",
                                    severity="error",
                                )

                    with self.tts_lock:
                        if (
                            target_index < len(self.tts_playlist)
                            and len(self.tts_playlist[target_index]) == 2
                        ):
                            item = self.tts_playlist[target_index]
                            if synthesis_success:
                                # Extend the tuple to include audio data
                                self.tts_playlist[target_index] = (
                                    item[0],
                                    item[1],
                                    audio_data,
                                )
                            else:
                                # Mark as failed but keep the text for fallback
                                self.tts_playlist[target_index] = (
                                    item[0],
                                    item[1],
                                    b"FAILED_SYNTHESIS",
                                )
                else:
                    # No work to do, wait for new data to become available
                    # Use event-driven waiting instead of polling
                    self.tts_data_available.clear()
                    # Wait for new data with timeout
                    data_available = self.tts_data_available.wait(timeout=0.2)
                    if not data_available:
                        # Timeout occurred, sleep briefly to avoid busy waiting
                        time.sleep(0.1)
            except Exception:
                time.sleep(1)

    def _handle_network_error(self, error: Exception, context: str = "") -> None:
        """Handle network error by pausing TTS and monitoring network recovery."""
        self.last_tts_error = str(error)

        # Set network error flags if not already set
        if not self.network_error_occurred:
            self.network_error_occurred = True
            self.network_error_notified = False
            self.network_recovery_notified = False

            # Start network monitoring in background
            self.app.call_from_thread(
                self.app.run_worker,
                self._monitor_network_recovery,
                exclusive=True,
                thread=True,
            )

        # Pause TTS playback and update status
        self.app.call_from_thread(self.stop_speaking, is_pause=True)
        self.app.tts_status = "PAUSED"
        self.app.call_from_thread(self.app._update_tts_progress)

        # Notify user of network error (only once)
        if not self.network_error_notified:
            error_msg = "Network connection interrupted, TTS paused. Press Space to continue after network recovery."
            self.app.call_from_thread(
                self.app.notify, error_msg, title="Network Error", severity="warning"
            )
            self.network_error_notified = True

    def _monitor_network_recovery(self) -> None:
        """Monitor network recovery and notify user when connection is restored."""
        import socket

        print("DEBUG: _monitor_network_recovery started")
        print(f"DEBUG: network_error_occurred = {self.network_error_occurred}")
        print(f"DEBUG: network_recovery_notified = {self.network_recovery_notified}")

        while self.network_error_occurred and not self.tts_stop_requested.is_set():
            print("DEBUG: Checking network connectivity...")
            try:
                # Test network connectivity by trying to connect to a reliable host
                socket.create_connection(("8.8.8.8", 53), timeout=5)
                # If we get here, network is back
                print("DEBUG: Network connection successful!")
                if not self.network_recovery_notified:
                    print("DEBUG: Sending network recovery notification")
                    self.app.call_from_thread(
                        self.app.notify,
                        "Network connection restored! Press Space to continue TTS playback.",
                        title="Network Recovery",
                        severity="information",
                    )
                    self.network_recovery_notified = True
                    self.network_error_occurred = False
                break
            except (socket.timeout, socket.error) as e:
                # Network still down, wait and try again
                print(f"DEBUG: Network check failed: {str(e)}, waiting 10 seconds...")
                time.sleep(10)  # Check every 10 seconds

        print("DEBUG: _monitor_network_recovery finished")

    def reset_network_error_state(self) -> None:
        """Reset network error state when user resumes TTS."""
        self.network_error_occurred = False
        self.network_error_notified = False
        self.network_recovery_notified = False
