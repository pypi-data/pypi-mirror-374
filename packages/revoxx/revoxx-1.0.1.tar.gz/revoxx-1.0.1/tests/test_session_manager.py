"""Tests for SessionManager class.

Tests session creation, loading, validation, and management features.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch

from revoxx.session.manager import SessionManager
from revoxx.session.models import SessionConfig
from tests.test_config import TestAudioConfig


class TestSessionManager(unittest.TestCase):
    """Test SessionManager functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_dir = Path(self.temp_dir)
        self.settings_file = self.base_dir / "settings.json"

        # Mock find_compatible_device to always return a device for CI tests
        patcher = patch("revoxx.session.models.SessionConfig.find_compatible_device")
        self.mock_find_device = patcher.start()
        self.mock_find_device.return_value = "Mock Audio Device"
        self.addCleanup(patcher.stop)

        self.manager = SessionManager(self.settings_file)

        # Default audio config for tests
        self.audio_config = TestAudioConfig.get_default_config()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_session(self):
        """Test creating a new session."""
        # Create test script file
        script_file = self.base_dir / "test_script.txt"
        script_file.write_text('(utt_001 "Test utterance")')

        session = self.manager.create_session(
            base_dir=self.base_dir,
            speaker_name="Test",
            gender="M",
            emotion="happy",
            audio_config=self.audio_config,
            script_source=script_file,
        )

        # Check session object
        self.assertEqual(session.speaker.name, "Test")
        self.assertEqual(session.speaker.gender, "M")
        self.assertEqual(session.speaker.emotion, "happy")
        self.assertEqual(session.audio_config.sample_rate, 44100)

        # Check directory structure
        session_dir = self.base_dir / "test_happy.revoxx"
        self.assertTrue(session_dir.exists())
        self.assertTrue((session_dir / "recordings").exists())
        self.assertTrue((session_dir / "session.json").exists())

    def test_create_session_custom_name(self):
        """Test creating session with custom directory name."""
        # Create test script file
        script_file = self.base_dir / "test_script.txt"
        script_file.write_text('(utt_001 "Test utterance")')

        session = self.manager.create_session(
            base_dir=self.base_dir,
            speaker_name="Test",
            gender="F",
            emotion="neutral",
            audio_config=self.audio_config,
            script_source=script_file,
            custom_dir_name="my_custom_session",
        )

        # Check custom directory was created
        session_dir = self.base_dir / "my_custom_session.revoxx"
        self.assertTrue(session_dir.exists())
        self.assertEqual(session.session_dir, session_dir)

    def test_create_session_with_script(self):
        """Test creating session with script file."""
        # Create test script
        script_file = self.base_dir / "test_script.txt"
        script_file.write_text("Test utterance 1\nTest utterance 2")

        session = self.manager.create_session(
            base_dir=self.base_dir,
            speaker_name="Test",
            gender="M",
            emotion="angry",
            audio_config=self.audio_config,
            script_source=script_file,
        )

        # Check script was copied
        session_script = session.session_dir / "script.txt"
        self.assertTrue(session_script.exists())
        self.assertEqual(
            session_script.read_text(), "Test utterance 1\nTest utterance 2"
        )

    def test_create_session_without_script(self):
        """Test creating session without script raises error."""
        with self.assertRaises(ValueError) as context:
            self.manager.create_session(
                base_dir=self.base_dir,
                speaker_name="Test",
                gender="M",
                emotion="happy",
                audio_config=self.audio_config,
                script_source=None,
            )
        self.assertIn("Script file is required", str(context.exception))

    def test_create_session_with_nonexistent_script(self):
        """Test creating session with non-existent script raises error."""
        nonexistent_script = self.base_dir / "nonexistent.txt"

        with self.assertRaises(FileNotFoundError) as context:
            self.manager.create_session(
                base_dir=self.base_dir,
                speaker_name="Test",
                gender="M",
                emotion="happy",
                audio_config=self.audio_config,
                script_source=nonexistent_script,
            )
        self.assertIn("Script file not found", str(context.exception))

    def test_create_duplicate_session(self):
        """Test creating duplicate session raises error."""
        # Create test script file
        script_file = self.base_dir / "test_script.txt"
        script_file.write_text('(utt_001 "Test utterance")')

        # Create first session
        self.manager.create_session(
            base_dir=self.base_dir,
            speaker_name="Test",
            gender="M",
            emotion="happy",
            audio_config=self.audio_config,
            script_source=script_file,
        )

        # Try to create duplicate
        with self.assertRaises(FileExistsError):
            self.manager.create_session(
                base_dir=self.base_dir,
                speaker_name="Test",
                gender="M",
                emotion="happy",
                audio_config=self.audio_config,
                script_source=script_file,
            )

    def test_load_session(self):
        """Test loading an existing session."""
        # Create test script file
        script_file = self.base_dir / "test_script.txt"
        script_file.write_text('(utt_001 "Test utterance")')

        # Create a session first
        created = self.manager.create_session(
            base_dir=self.base_dir,
            speaker_name="LoadTest",
            gender="F",
            emotion="sad",
            audio_config=self.audio_config,
            script_source=script_file,
        )

        # Create new manager and load
        new_manager = SessionManager(self.settings_file)
        loaded = new_manager.load_session(created.session_dir)

        # Verify loaded data
        self.assertEqual(loaded.speaker.name, "LoadTest")
        self.assertEqual(loaded.speaker.emotion, "sad")
        self.assertEqual(loaded.audio_config.sample_rate, 44100)

    def test_load_nonexistent_session(self):
        """Test loading non-existent session raises error."""
        bad_dir = self.base_dir / "nonexistent.revoxx"

        with self.assertRaises(FileNotFoundError):
            self.manager.load_session(bad_dir)

    def test_load_invalid_session(self):
        """Test loading invalid session directory."""
        # Create directory without .revoxx suffix
        bad_dir = self.base_dir / "not_a_session"
        bad_dir.mkdir()

        with self.assertRaises(ValueError):
            self.manager.load_session(bad_dir)

    def test_load_session_without_script(self):
        """Test loading session without script file raises error."""
        # Create test script file for initial creation
        script_file = self.base_dir / "test_script.txt"
        script_file.write_text('(utt_001 "Test utterance")')

        # Create valid session
        session = self.manager.create_session(
            base_dir=self.base_dir,
            speaker_name="NoScript",
            gender="M",
            emotion="neutral",
            audio_config=self.audio_config,
            script_source=script_file,
        )

        # Delete the script file from session
        (session.session_dir / "script.txt").unlink()

        # Try to load session without script
        new_manager = SessionManager(self.settings_file)
        with self.assertRaises(FileNotFoundError) as context:
            new_manager.load_session(session.session_dir)
        self.assertIn("Required script file not found", str(context.exception))

    def test_find_sessions(self):
        """Test finding all sessions in directory."""
        # Create test script file
        script_file = self.base_dir / "test_script.txt"
        script_file.write_text('(utt_001 "Test utterance")')

        # Create multiple sessions
        for i, emotion in enumerate(["happy", "sad", "angry"]):
            self.manager.create_session(
                base_dir=self.base_dir,
                speaker_name=f"Speaker{i}",
                gender="M",
                emotion=emotion,
                audio_config=self.audio_config,
                script_source=script_file,
            )

        # Also create non-session directory
        (self.base_dir / "not_a_session").mkdir()

        # Find sessions
        sessions = self.manager.find_sessions(self.base_dir)

        # Should find exactly 3 sessions
        self.assertEqual(len(sessions), 3)
        self.assertTrue(all(s.name.endswith(".revoxx") for s in sessions))

    def test_recent_sessions(self):
        """Test recent sessions tracking."""
        # Create test script file
        script_file = self.base_dir / "test_script.txt"
        script_file.write_text('(utt_001 "Test utterance")')

        # Create sessions
        session1 = self.manager.create_session(
            base_dir=self.base_dir,
            speaker_name="First",
            gender="M",
            emotion="happy",
            audio_config=self.audio_config,
            script_source=script_file,
        )

        session2 = self.manager.create_session(
            base_dir=self.base_dir,
            speaker_name="Second",
            gender="F",
            emotion="sad",
            audio_config=self.audio_config,
            script_source=script_file,
        )

        # Check recent sessions
        recent = self.manager.get_recent_sessions()
        self.assertEqual(len(recent), 2)
        # Most recent should be first
        self.assertEqual(recent[0], session2.session_dir)
        self.assertEqual(recent[1], session1.session_dir)

    def test_last_session(self):
        """Test getting last used session."""
        # Initially no last session
        self.assertIsNone(self.manager.get_last_session())

        # Create test script file
        script_file = self.base_dir / "test_script.txt"
        script_file.write_text('(utt_001 "Test utterance")')

        # Create session
        session = self.manager.create_session(
            base_dir=self.base_dir,
            speaker_name="Last",
            gender="M",
            emotion="neutral",
            audio_config=self.audio_config,
            script_source=script_file,
        )

        # Should be set as last session
        last = self.manager.get_last_session()
        self.assertEqual(last, session.session_dir)

    def test_validate_session(self):
        """Test session validation."""
        # Create test script file
        script_file = self.base_dir / "test_script.txt"
        script_file.write_text('(utt_001 "Test utterance")')

        # Create valid session
        session = self.manager.create_session(
            base_dir=self.base_dir,
            speaker_name="Valid",
            gender="F",
            emotion="happy",
            audio_config=self.audio_config,
            script_source=script_file,
        )

        # Validate
        result = self.manager.validate_session(session.session_dir)
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)

        # Remove a directory
        shutil.rmtree(session.session_dir / "recordings")

        # Should have warning but still valid
        result = self.manager.validate_session(session.session_dir)
        self.assertTrue(result["valid"])
        self.assertIn("Missing recordings directory", result["warnings"])

        # Remove script file
        (session.session_dir / "script.txt").unlink()

        # Should be invalid without script
        result = self.manager.validate_session(session.session_dir)
        self.assertFalse(result["valid"])
        self.assertTrue(
            any("Required script file not found" in err for err in result["errors"])
        )

        # Restore script for next test
        (session.session_dir / "script.txt").write_text('(utt_001 "Test")')

        # Remove session.json
        (session.session_dir / "session.json").unlink()

        # Should be invalid
        result = self.manager.validate_session(session.session_dir)
        self.assertFalse(result["valid"])
        self.assertIn("Missing session.json", result["errors"])

    @patch("sounddevice.query_devices")
    def test_get_compatible_devices(self, mock_query):
        """Test finding compatible audio devices."""
        # Mock device list
        mock_query.return_value = [
            {"name": "Device1", "max_input_channels": 2, "default_samplerate": 44100},
            {"name": "Device2", "max_input_channels": 2, "default_samplerate": 44100},
            {
                "name": "Device3",
                "max_input_channels": 0,
                "default_samplerate": 44100,
            },  # Output only
            {"name": "Device4", "max_input_channels": 1, "default_samplerate": 44100},
        ]

        config = SessionConfig(
            sample_rate=44100, bit_depth=16, format="wav", channels=2
        )

        # Mock the device manager compatibility check
        with patch("revoxx.session.models.get_device_manager") as mock_get_dm:
            mock_dm = mock_get_dm.return_value
            # Only Device1 should be compatible
            mock_dm.check_device_compatibility.side_effect = (
                lambda device_name, **kwargs: device_name == "Device1"
            )

            compatible = self.manager.get_compatible_devices(config)

            # Should find Device1 (matching sample rate and channels)
            self.assertEqual(len(compatible), 1)
            self.assertEqual(compatible[0]["name"], "Device1")

    def test_recent_sessions_persistence(self):
        """Test recent sessions persist across manager instances."""
        # Create test script file
        script_file = self.base_dir / "test_script.txt"
        script_file.write_text('(utt_001 "Test utterance")')

        # Create session with first manager
        session = self.manager.create_session(
            base_dir=self.base_dir,
            speaker_name="Persist",
            gender="M",
            emotion="happy",
            audio_config=self.audio_config,
            script_source=script_file,
        )

        # Create new manager instance
        new_manager = SessionManager(self.settings_file)

        # Should see the recent session
        recent = new_manager.get_recent_sessions()
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0], session.session_dir)

        # Should see last session
        last = new_manager.get_last_session()
        self.assertEqual(last, session.session_dir)

    def test_settings_file_creation(self):
        """Test settings file is created if it doesn't exist."""
        # Create test script file
        script_file = self.base_dir / "test_script.txt"
        script_file.write_text('(utt_001 "Test utterance")')

        # Use non-existent settings file
        new_settings = self.base_dir / "subdir" / "settings.json"
        manager = SessionManager(new_settings)

        # Create session
        manager.create_session(
            base_dir=self.base_dir,
            speaker_name="Settings",
            gender="F",
            emotion="neutral",
            audio_config=self.audio_config,
            script_source=script_file,
        )

        # Settings file should be created
        self.assertTrue(new_settings.exists())

        # Should contain recent session
        with open(new_settings) as f:
            settings = json.load(f)
            self.assertIn("recent_sessions", settings)
            self.assertIn("last_session_path", settings)


if __name__ == "__main__":
    unittest.main()
