#!/usr/bin/env python3
"""
SpeakUB CLI - Entry point for the application
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from speakub.ui.app import EPUBReaderApp


def main(argv: Optional[List[str]] = None) -> None:
    """Main entry point for SpeakUB."""
    parser = argparse.ArgumentParser(description="SpeakUB")
    parser.add_argument("epub", help="Path to EPUB file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--log-file", help="Path to log file")
    args = parser.parse_args(argv)

    if args.debug and not args.log_file:
        log_dir = Path.home() / ".local/share/speakub/logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.log_file = str(log_dir / f"speakub-{ts}.log")
        print(f"Debug logging to: {args.log_file}")

    log_level = logging.DEBUG if args.debug else logging.INFO
    handlers: List[logging.Handler] = [logging.StreamHandler()]
    if args.log_file:
        handlers.append(
            logging.FileHandler(Path(args.log_file).expanduser(), encoding="utf-8")
        )
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    epub_path = Path(args.epub)
    if not epub_path.exists():
        print(f"Error: EPUB file not found: {epub_path}", file=sys.stderr)
        sys.exit(1)
    app = EPUBReaderApp(str(epub_path), debug=args.debug, log_file=args.log_file)
    app.run()


if __name__ == "__main__":
    main()
