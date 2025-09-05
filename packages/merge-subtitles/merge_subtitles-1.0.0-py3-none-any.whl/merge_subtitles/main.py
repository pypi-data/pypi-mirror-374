#!/usr/bin/env python3

import os
import sys
import glob
import re
import subprocess
import argparse
from pathlib import Path

def find_season_number(directory_path, filename):
    """Extract season number from directory name or return None."""
    dir_name = os.path.basename(directory_path).lower()
    # Look for "series N" or "season N" patterns
    season_match = re.search(r'(?:series|season)\s*(\d+)', dir_name)
    if season_match:
        return int(season_match.group(1))
    
    return None

def find_episode_number(filename):
    """Extract episode number from filename or return None."""
    name_lower = filename.lower()
    
    # Try various episode number patterns
    patterns = [
        r'e(\d+)',           # e1, e12
        r'ep\s*(\d+)',       # ep1, ep 12
        r'episode\s*(\d+)',  # episode1, episode 12
        r'(\d+)\.',          # 1., 12.
    ]
    
    for pattern in patterns:
        match = re.search(pattern, name_lower)
        if match:
            return int(match.group(1))
    
    return None

def process_file(mp4_path, srt_path, add_episode_numbers=False, archive_after=False, dry_run=False):
    """Process a single MP4/SRT pair."""
    mp4_file = Path(mp4_path)
    srt_file = Path(srt_path)
    
    if not mp4_file.exists():
        print(f"Error: {mp4_path} not found")
        return False
    
    if not srt_file.exists():
        print(f"Error: {srt_path} not found")
        return False
    
    # Determine output filename
    base_name = mp4_file.stem
    output_name = base_name
    
    if add_episode_numbers:
        season_num = find_season_number(str(mp4_file.parent.resolve()), base_name)
        episode_num = find_episode_number(base_name)
        
        if season_num is not None and episode_num is not None:
            output_name = f"{output_name} - s{season_num:02d}e{episode_num:02d}"
        else:
            output_name = f"{output_name} - MISSING EPISODE NUMBER"
    
    output_path = mp4_file.parent / f"{output_name}.mkv"
    
    # Run FFmpeg command
    cmd = [
        'ffmpeg',
        '-i', str(mp4_file),
        '-i', str(srt_file),
        '-c', 'copy',
        '-c:s', 'srt',
        str(output_path)
    ]
    
    if dry_run:
        print(f"[DRY RUN] Would process: {mp4_file.name} + {srt_file.name} -> {output_path.name}")
    else:
        print(f"Processing: {mp4_file.name} + {srt_file.name} -> {output_path.name}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"Successfully created: {output_path.name}")
        except subprocess.CalledProcessError as e:
            print(f"Error running FFmpeg: {e}")
            print(f"FFmpeg output: {e.stderr}")
            return False
        
        # Archive files if requested
        if archive_after:
            archive_dir = mp4_file.parent / "archive"
            archive_dir.mkdir(exist_ok=True)
            
            try:
                mp4_file.rename(archive_dir / mp4_file.name)
                srt_file.rename(archive_dir / srt_file.name)
                print(f"Archived: {mp4_file.name} and {srt_file.name}")
            except Exception as e:
                print(f"Error archiving files: {e}")
                return False
    
    return True

def find_matching_pairs(pattern):
    """Find all MP4/SRT pairs matching the given pattern."""
    pairs = []
    
    # Get all MP4 files matching the pattern
    mp4_files = glob.glob(f"{pattern}.mp4")
    
    for mp4_file in mp4_files:
        base_name = os.path.splitext(mp4_file)[0]
        srt_file = f"{base_name}.srt"
        
        if os.path.exists(srt_file):
            pairs.append((mp4_file, srt_file))
    
    return pairs

def main():
    parser = argparse.ArgumentParser(description='Merge MP4 files with SRT subtitles into MKV format')
    parser.add_argument('name', help='Base name or wildcard pattern for files to process')
    parser.add_argument('--add-episode-numbers', action='store_true',
                      help='Add season/episode numbers to output filenames')
    parser.add_argument('--archive-after-processing', action='store_true',
                      help='Move original files to archive directory after processing')
    parser.add_argument('--dry-run', action='store_true',
                      help='Show what would be done without actually processing files')
    
    args = parser.parse_args()
    
    # Check if FFmpeg is available (skip for dry run)
    if not args.dry_run:
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: FFmpeg not found. Please install FFmpeg.")
            sys.exit(1)
    
    # Determine if we're processing a single file or multiple files
    if '*' in args.name or '?' in args.name:
        # Wildcard processing
        pairs = find_matching_pairs(args.name)
        
        if not pairs:
            print(f"No matching MP4/SRT pairs found for pattern: {args.name}")
            sys.exit(1)
        
        print(f"{'[DRY RUN] ' if args.dry_run else ''}Found {len(pairs)} matching pairs:")
        for mp4_path, srt_path in pairs:
            print(f"  {os.path.basename(mp4_path)} + {os.path.basename(srt_path)}")
        print()
        
        success_count = 0
        for mp4_path, srt_path in pairs:
            if process_file(mp4_path, srt_path, args.add_episode_numbers, 
                          args.archive_after_processing, args.dry_run):
                success_count += 1
        
        if args.dry_run:
            print(f"\n[DRY RUN] Would process {success_count}/{len(pairs)} files.")
        else:
            print(f"\nProcessed {success_count}/{len(pairs)} files successfully.")
        
    else:
        # Single file processing
        mp4_path = f"{args.name}.mp4"
        srt_path = f"{args.name}.srt"
        
        if not process_file(mp4_path, srt_path, args.add_episode_numbers, 
                          args.archive_after_processing, args.dry_run):
            if not args.dry_run:
                sys.exit(1)

if __name__ == "__main__":
    main()