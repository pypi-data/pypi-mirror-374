# merge-subtitles

A Python command-line tool that merges MP4 video files with SRT subtitle files into MKV format using FFmpeg.

## Features

- Merge MP4 videos with SRT subtitles into MKV containers
- Process single files or multiple files using wildcards
- Automatically extract and add season/episode numbers to output filenames
- Archive original files after processing
- Dry-run mode to preview operations
- Intelligent episode/season number detection from directory names and filenames

## Prerequisites

- Python 3.6+
- FFmpeg installed and available in your PATH

### Installing FFmpeg

**macOS (using Homebrew):**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

## Installation

### From PyPI (Recommended)

```bash
pip install merge-subtitles
```

### From Source

1. Clone this repository:
   ```bash
   git clone https://github.com/lorenzowood/merge-subtitles.git
   cd merge-subtitles
   ```

2. Install the package:
   ```bash
   pip install .
   ```

### Development Installation

For development, install in editable mode:
```bash
git clone https://github.com/lorenzowood/merge-subtitles.git
cd merge-subtitles
pip install -e ".[dev]"
```

## Development

### Running Tests

Install test dependencies:
```bash
pip install -r requirements-dev.txt
```

Run the test suite:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=merge-subtitles
```

The test suite includes:
- Unit tests for episode/season number detection
- Integration tests for file processing with mocked FFmpeg calls
- Tests for all command-line options (--dry-run, --add-episode-numbers, --archive-after-processing)
- Tests for error handling and edge cases

## Usage

### Basic Usage

Process a single file pair:
```bash
merge-subtitles "movie_name"
```
This will look for `movie_name.mp4` and `movie_name.srt` and create `movie_name.mkv`.

### Process Multiple Files

Use wildcards to process multiple files:
```bash
merge-subtitles "*"
```

It's important to use quotation marks to prevent the shell from expanding the wildcard. When used with a wildcard, it looks for matching pairs of MP4 and SRT files and then works through those.

### Options

- `--add-episode-numbers`: Add season/episode numbers to output filenames
- `--archive-after-processing`: Move original files to an `archive/` directory
- `--dry-run`: Show what would be done without actually processing files

### Examples

```bash
# Process all episodes and add episode numbers
merge-subtitles "episode_*" --add-episode-numbers

# Process files and archive originals
merge-subtitles "movie" --archive-after-processing

# Preview what would happen
merge-subtitles "season_*" --dry-run --add-episode-numbers
```

## Episode Number Detection

The tool can automatically detect season and episode numbers from:

**Directory names:**
- `Series 1/`, `Season 2/`, etc.

**File names:**
- `e1`, `e12` (episode numbers)
- `ep1`, `ep 12`
- `episode1`, `episode 12`
- `1.`, `12.` (number followed by period)

When both season and episode numbers are detected, output files will be named:
```
original_name - s01e01.mkv
```

If you use the `--add-episode-numbers` switch, any files where it can't detect the season or episode number will be named:
```
original_name - MISSING EPISODE NUMBER.mkv
```

## Output

- Creates MKV files with embedded SRT subtitles
- Preserves video and audio streams (copy mode for efficiency)
- Subtitle track is set to SRT format

## Error Handling

- Checks for FFmpeg availability before processing
- Validates input file existence
- Reports processing errors with FFmpeg output
- Continues processing remaining files if one fails

## License

[MIT](https://opensource.org/licenses/MIT)

## Contributing

Feel free to submit issues and pull requests.