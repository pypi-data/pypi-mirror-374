"""
Command-line interface for jyutping-transcriber.

This module provides CLI commands for transcribing text, managing data,
and controlling the transcriber behavior.
"""

import argparse
import logging
import sys
from typing import Optional

from . import transcribe, warmup, clear_cache
from .data_builder import build_mapping_data, get_cached_data_path


def cmd_transcribe(args: argparse.Namespace) -> None:
    """Handle the transcribe command."""
    try:
        result = transcribe(args.text)
        if result:
            print(result)
        else:
            print("⚠️  Could not transcribe the input text. Please check if it's valid Jyutping.", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"❌ Transcription failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_build_data(args: argparse.Namespace) -> None:
    """Handle the build-data command."""
    try:
        # Set up logging for CLI feedback during data building
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        
        data_path = get_cached_data_path()
        print("🔄 Rebuilding Jyutping mapping data...")
        build_mapping_data(str(data_path))
        print(f"✅ Data built successfully: {data_path}")
    except Exception as e:
        print(f"❌ Failed to build data: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_clear_cache(args: argparse.Namespace) -> None:
    """Handle the clear-cache command."""
    try:
        clear_cache()
        print("✅ Cache cleared successfully")
    except Exception as e:
        print(f"❌ Failed to clear cache: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_warmup(args: argparse.Namespace) -> None:
    """Handle the warmup command."""
    try:
        # Set up logging for CLI feedback during warmup
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        
        print("🔥 Warming up transcriber...")
        warmup()
        print("✅ Transcriber warmed up and ready!")
    except Exception as e:
        print(f"❌ Failed to warm up transcriber: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_info(args: argparse.Namespace) -> None:
    """Handle the info command."""
    from . import __version__
    
    print(f"Jyutping Transcriber v{__version__}")
    print("Convert Jyutping romanization to Traditional Chinese characters")
    print()
    
    # Check if data exists
    data_path = get_cached_data_path()
    if data_path.exists():
        try:
            import json
            with open(data_path, 'r') as f:
                data = json.load(f)
            print(f"📊 Cached data: {len(data):,} entries")
            print(f"📁 Cache location: {data_path}")
        except Exception:
            print("⚠️  Cached data exists but appears corrupted")
            print(f"📁 Cache location: {data_path}")
    else:
        print("ℹ️  No cached data found - will be built on first use")
        print(f"📁 Cache location: {data_path}")


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="jyutping-transcriber",
        description="Convert Jyutping romanization to Traditional Chinese characters",
        epilog="Examples:\n"
               "  jyutping-transcriber transcribe 'ngo5oi3nei5'     # Transcribe text\n"
               "  jyutping-transcriber warmup                       # Pre-load data\n"
               "  jyutping-transcriber build-data                   # Rebuild data cache\n"
               "  jyutping-transcriber clear-cache                  # Clear cached data",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands', metavar='COMMAND')
    
    # Transcribe command
    transcribe_parser = subparsers.add_parser(
        'transcribe', 
        help='Transcribe Jyutping text to Chinese characters',
        description='Convert a Jyutping romanization string to Traditional Chinese characters.'
    )
    transcribe_parser.add_argument(
        'text', 
        help='Jyutping text to transcribe (e.g., "ngo5oi3nei5")'
    )
    transcribe_parser.set_defaults(func=cmd_transcribe)
    
    # Build data command
    build_parser = subparsers.add_parser(
        'build-data',
        help='Build/rebuild the mapping data cache',
        description='Download fresh data from online sources and rebuild the mapping cache.'
    )
    build_parser.set_defaults(func=cmd_build_data)
    
    # Clear cache command
    clear_parser = subparsers.add_parser(
        'clear-cache',
        help='Clear the cached mapping data',
        description='Remove cached data. Next transcription will rebuild from online sources.'
    )
    clear_parser.set_defaults(func=cmd_clear_cache)
    
    # Warmup command
    warmup_parser = subparsers.add_parser(
        'warmup',
        help='Pre-initialize the transcriber',
        description='Load the transcriber and data into memory for faster subsequent operations.'
    )
    warmup_parser.set_defaults(func=cmd_warmup)
    
    # Info command
    info_parser = subparsers.add_parser(
        'info',
        help='Show information about the transcriber and cached data',
        description='Display version information, cache status, and data statistics.'
    )
    info_parser.set_defaults(func=cmd_info)
    
    return parser


def main() -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command is None:
        # No subcommand provided, show help
        parser.print_help()
        sys.exit(1)
    
    # Execute the appropriate command function
    args.func(args)


if __name__ == "__main__":
    main()
