#!/usr/bin/env python3

import pytest
import os
import tempfile
import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import sys

# Import the functions we want to test
from merge_subtitles.main import (
    find_season_number, 
    find_episode_number, 
    process_file, 
    find_matching_pairs,
    main
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def create_test_files():
    """Helper fixture to create test files."""
    def _create_files(temp_dir, files):
        """Create mock files in temp_dir.
        
        Args:
            temp_dir: Directory to create files in
            files: List of filenames to create
        """
        for filename in files:
            filepath = Path(temp_dir) / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(f"Mock content for {filename}")
        
        return [str(Path(temp_dir) / f) for f in files]
    
    return _create_files


class TestEpisodeNumberDetection:
    """Test episode and season number detection functions."""
    
    def test_find_season_number_from_series(self):
        assert find_season_number("/path/to/Series 1", "episode.mp4") == 1
        assert find_season_number("/path/to/Series 10", "episode.mp4") == 10
    
    def test_find_season_number_from_season(self):
        assert find_season_number("/path/to/Season 2", "episode.mp4") == 2
        assert find_season_number("/path/to/season 3", "episode.mp4") == 3
    
    def test_find_season_number_no_match(self):
        assert find_season_number("/path/to/Movies/", "episode.mp4") is None
        assert find_season_number("/path/to/Random Folder/", "episode.mp4") is None
    
    def test_find_episode_number_e_format(self):
        assert find_episode_number("episode_e1.mp4") == 1
        assert find_episode_number("show_e12.mp4") == 12
    
    def test_find_episode_number_ep_format(self):
        assert find_episode_number("episode_ep1.mp4") == 1
        assert find_episode_number("show_ep 12.mp4") == 12
    
    def test_find_episode_number_episode_format(self):
        assert find_episode_number("episode1.mp4") == 1
        assert find_episode_number("episode 12.mp4") == 12
    
    def test_find_episode_number_dot_format(self):
        assert find_episode_number("1.Something.mp4") == 1
        assert find_episode_number("12.Another Episode.mp4") == 12
    
    def test_find_episode_number_no_match(self):
        assert find_episode_number("random_file.mp4") is None
        assert find_episode_number("no_numbers_here.mp4") is None


class TestProcessFile:
    """Test the process_file function."""
    
    @patch('subprocess.run')
    def test_process_file_success(self, mock_run, temp_dir, create_test_files):
        # Create test files
        files = create_test_files(temp_dir, ["test.mp4", "test.srt"])
        mp4_path, srt_path = files
        
        # Mock successful FFmpeg execution
        mock_run.return_value = MagicMock(returncode=0)
        
        result = process_file(mp4_path, srt_path, dry_run=False)
        
        assert result is True
        mock_run.assert_called_once()
        
        # Verify FFmpeg command structure
        args = mock_run.call_args[0][0]
        assert args[0] == 'ffmpeg'
        assert mp4_path in args
        assert srt_path in args
        assert '-c' in args and 'copy' in args
    
    def test_process_file_missing_mp4(self, temp_dir, create_test_files):
        # Only create SRT file
        files = create_test_files(temp_dir, ["test.srt"])
        srt_path = files[0]
        mp4_path = str(Path(temp_dir) / "nonexistent.mp4")
        
        result = process_file(mp4_path, srt_path, dry_run=False)
        
        assert result is False
    
    def test_process_file_missing_srt(self, temp_dir, create_test_files):
        # Only create MP4 file
        files = create_test_files(temp_dir, ["test.mp4"])
        mp4_path = files[0]
        srt_path = str(Path(temp_dir) / "nonexistent.srt")
        
        result = process_file(mp4_path, srt_path, dry_run=False)
        
        assert result is False
    
    def test_process_file_dry_run(self, temp_dir, create_test_files):
        # Create test files
        files = create_test_files(temp_dir, ["test.mp4", "test.srt"])
        mp4_path, srt_path = files
        
        with patch('subprocess.run') as mock_run:
            result = process_file(mp4_path, srt_path, dry_run=True)
            
            assert result is True
            mock_run.assert_not_called()  # Should not run FFmpeg in dry run mode
    
    @patch('subprocess.run')
    def test_process_file_with_episode_numbers(self, mock_run, temp_dir, create_test_files):
        # Create test files in a season directory
        season_dir = Path(temp_dir) / "Season 1"
        season_dir.mkdir()
        files = create_test_files(str(season_dir), ["episode_e05.mp4", "episode_e05.srt"])
        mp4_path, srt_path = files
        
        mock_run.return_value = MagicMock(returncode=0)
        
        result = process_file(mp4_path, srt_path, add_episode_numbers=True, dry_run=False)
        
        assert result is True
        
        # Check that output filename includes season/episode info
        args = mock_run.call_args[0][0]
        output_path = args[-1]  # Last argument is output path
        assert "s01e05" in output_path
    
    @patch('subprocess.run')
    def test_process_file_archive_after_processing(self, mock_run, temp_dir, create_test_files):
        # Create test files
        files = create_test_files(temp_dir, ["test.mp4", "test.srt"])
        mp4_path, srt_path = files
        
        mock_run.return_value = MagicMock(returncode=0)
        
        result = process_file(mp4_path, srt_path, archive_after=True, dry_run=False)
        
        assert result is True
        
        # Check that archive directory was created and files were moved
        archive_dir = Path(temp_dir) / "archive"
        assert archive_dir.exists()
        assert (archive_dir / "test.mp4").exists()
        assert (archive_dir / "test.srt").exists()
        
        # Original files should be moved (not exist in original location)
        assert not Path(mp4_path).exists()
        assert not Path(srt_path).exists()
    
    @patch('subprocess.run')
    def test_process_file_ffmpeg_error(self, mock_run, temp_dir, create_test_files):
        # Create test files
        files = create_test_files(temp_dir, ["test.mp4", "test.srt"])
        mp4_path, srt_path = files
        
        # Mock FFmpeg failure
        mock_run.side_effect = subprocess.CalledProcessError(1, 'ffmpeg', stderr="FFmpeg error")
        
        result = process_file(mp4_path, srt_path, dry_run=False)
        
        assert result is False


class TestFindMatchingPairs:
    """Test the find_matching_pairs function."""
    
    def test_find_matching_pairs_single_match(self, temp_dir, create_test_files):
        # Create matching MP4/SRT pair
        create_test_files(temp_dir, ["episode1.mp4", "episode1.srt"])
        
        os.chdir(temp_dir)
        pairs = find_matching_pairs("episode1")
        
        assert len(pairs) == 1
        assert pairs[0][0].endswith("episode1.mp4")
        assert pairs[0][1].endswith("episode1.srt")
    
    def test_find_matching_pairs_multiple_matches(self, temp_dir, create_test_files):
        # Create multiple matching pairs
        create_test_files(temp_dir, [
            "episode1.mp4", "episode1.srt",
            "episode2.mp4", "episode2.srt",
            "episode3.mp4", "episode3.srt"
        ])
        
        os.chdir(temp_dir)
        pairs = find_matching_pairs("episode*")
        
        assert len(pairs) == 3
        
        # Sort pairs for consistent testing
        pairs.sort(key=lambda x: x[0])
        
        for i, (mp4, srt) in enumerate(pairs, 1):
            assert mp4.endswith(f"episode{i}.mp4")
            assert srt.endswith(f"episode{i}.srt")
    
    def test_find_matching_pairs_orphan_files(self, temp_dir, create_test_files):
        # Create files with missing pairs
        create_test_files(temp_dir, [
            "episode1.mp4", "episode1.srt",  # Complete pair
            "episode2.mp4",                   # MP4 without SRT
            "episode3.srt"                    # SRT without MP4
        ])
        
        os.chdir(temp_dir)
        pairs = find_matching_pairs("episode*")
        
        # Should only find the complete pair
        assert len(pairs) == 1
        assert pairs[0][0].endswith("episode1.mp4")
        assert pairs[0][1].endswith("episode1.srt")
    
    def test_find_matching_pairs_no_matches(self, temp_dir):
        os.chdir(temp_dir)
        pairs = find_matching_pairs("nonexistent*")
        
        assert len(pairs) == 0


class TestMainFunction:
    """Test the main function with various command line arguments."""
    
    @patch('subprocess.run')
    def test_main_single_file_processing(self, mock_run, temp_dir, create_test_files):
        # Create test files
        create_test_files(temp_dir, ["movie.mp4", "movie.srt"])
        
        # Mock FFmpeg availability check and processing
        mock_run.side_effect = [
            MagicMock(returncode=0),  # FFmpeg version check
            MagicMock(returncode=0)   # Actual processing
        ]
        
        os.chdir(temp_dir)
        
        with patch('argparse.ArgumentParser.parse_args') as mock_args:
            # Create a proper mock args object with string attributes
            args_mock = MagicMock()
            args_mock.name = 'movie'
            args_mock.add_episode_numbers = False
            args_mock.archive_after_processing = False
            args_mock.dry_run = False
            mock_args.return_value = args_mock
            
            # Should not raise SystemExit for successful processing
            main()
        
        # Verify FFmpeg was called twice (version check + processing)
        assert mock_run.call_count == 2
    
    @patch('subprocess.run')
    def test_main_wildcard_processing(self, mock_run, temp_dir, create_test_files):
        # Create test files
        create_test_files(temp_dir, [
            "episode1.mp4", "episode1.srt",
            "episode2.mp4", "episode2.srt"
        ])
        
        # Mock FFmpeg availability and processing
        mock_run.side_effect = [
            MagicMock(returncode=0),  # FFmpeg version check
            MagicMock(returncode=0),  # First file processing
            MagicMock(returncode=0)   # Second file processing
        ]
        
        os.chdir(temp_dir)
        
        with patch('argparse.ArgumentParser.parse_args') as mock_args:
            # Create a proper mock args object with string attributes
            args_mock = MagicMock()
            args_mock.name = 'episode*'
            args_mock.add_episode_numbers = False
            args_mock.archive_after_processing = False
            args_mock.dry_run = False
            mock_args.return_value = args_mock
            
            main()
        
        # Verify FFmpeg was called for version check + 2 file processings
        assert mock_run.call_count == 3
    
    @patch('subprocess.run')
    def test_main_archive_after_processing(self, mock_run, temp_dir, create_test_files):
        # Create test files
        create_test_files(temp_dir, ["movie.mp4", "movie.srt"])
        
        # Mock FFmpeg availability check and processing
        mock_run.side_effect = [
            MagicMock(returncode=0),  # FFmpeg version check
            MagicMock(returncode=0)   # Actual processing
        ]
        
        os.chdir(temp_dir)
        
        with patch('argparse.ArgumentParser.parse_args') as mock_args:
            # Create a proper mock args object with archive flag enabled
            args_mock = MagicMock()
            args_mock.name = 'movie'
            args_mock.add_episode_numbers = False
            args_mock.archive_after_processing = True  # Enable archiving
            args_mock.dry_run = False
            mock_args.return_value = args_mock
            
            main()
        
        # Verify that archive directory was created and files were moved
        archive_dir = Path(temp_dir) / "archive"
        assert archive_dir.exists()
        assert (archive_dir / "movie.mp4").exists()
        assert (archive_dir / "movie.srt").exists()
        
        # Original files should be moved (not exist in original location)
        assert not (Path(temp_dir) / "movie.mp4").exists()
        assert not (Path(temp_dir) / "movie.srt").exists()
        
        # Verify FFmpeg was called twice (version check + processing)
        assert mock_run.call_count == 2
    
    def test_main_dry_run(self, temp_dir, create_test_files):
        # Create test files
        create_test_files(temp_dir, ["movie.mp4", "movie.srt"])
        
        os.chdir(temp_dir)
        
        with patch('argparse.ArgumentParser.parse_args') as mock_args:
            # Create a proper mock args object with string attributes
            args_mock = MagicMock()
            args_mock.name = 'movie'
            args_mock.add_episode_numbers = False
            args_mock.archive_after_processing = False
            args_mock.dry_run = True
            mock_args.return_value = args_mock
            
            with patch('subprocess.run') as mock_run:
                main()
                
                # In dry run, FFmpeg should not be called at all
                mock_run.assert_not_called()
    
    @patch('subprocess.run')
    def test_main_ffmpeg_not_available(self, mock_run, temp_dir):
        # Mock FFmpeg not being available
        mock_run.side_effect = FileNotFoundError("FFmpeg not found")
        
        os.chdir(temp_dir)
        
        with patch('argparse.ArgumentParser.parse_args') as mock_args:
            # Create a proper mock args object with string attributes
            args_mock = MagicMock()
            args_mock.name = 'movie'
            args_mock.add_episode_numbers = False
            args_mock.archive_after_processing = False
            args_mock.dry_run = False
            mock_args.return_value = args_mock
            
            # Should exit with status 1 when FFmpeg is not available
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
    
    @patch('subprocess.run')
    def test_main_no_matching_files_wildcard(self, mock_run, temp_dir):
        # Mock FFmpeg availability
        mock_run.return_value = MagicMock(returncode=0)
        
        os.chdir(temp_dir)
        
        with patch('argparse.ArgumentParser.parse_args') as mock_args:
            # Create a proper mock args object with string attributes
            args_mock = MagicMock()
            args_mock.name = 'nonexistent*'
            args_mock.add_episode_numbers = False
            args_mock.archive_after_processing = False
            args_mock.dry_run = False
            mock_args.return_value = args_mock
            
            # Should exit with status 1 when no matching files found
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1


if __name__ == "__main__":
    pytest.main([__file__])