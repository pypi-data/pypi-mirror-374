"""
Tests for filename generation functions in the app module.
"""

from ai_subtitle_translator.app import generate_translation_filename


class TestGenerateTranslationFilename:
    """Test the generate_translation_filename function."""

    def test_basic_srt_file(self):
        """Test basic SRT file without language code."""
        result = generate_translation_filename("movie.srt")
        assert result == "movie.en-zh.ass"

    def test_with_existing_language_code(self):
        """Test SRT file with existing language code."""
        result = generate_translation_filename("movie.en.srt")
        assert result == "movie.en-zh.ass"

    def test_different_existing_language_codes(self):
        """Test SRT files with different existing language codes."""
        test_cases = [
            ("movie.zh.srt", "movie.en-zh.ass"),
            ("movie.fr.srt", "movie.en-zh.ass"),
            ("movie.es.srt", "movie.en-zh.ass"),
            ("movie.de.srt", "movie.en-zh.ass"),
            ("movie.eng.srt", "movie.en-zh.ass"),
            ("movie.chs.srt", "movie.en-zh.ass"),
        ]
        for input_file, expected in test_cases:
            result = generate_translation_filename(input_file)
            assert result == expected

    def test_filename_with_dots_in_title(self):
        """Test the problematic case with dots in the title."""
        input_file = "tick, tick. BOOM! (2021) WEBDL-2160p.en.srt"
        expected = "tick, tick. BOOM! (2021) WEBDL-2160p.en-zh.ass"
        result = generate_translation_filename(input_file)
        assert result == expected

    def test_complex_filenames_with_dots(self):
        """Test various complex filenames with dots."""
        test_cases = [
            ("Mr. & Mrs. Smith (2005).en.srt", "Mr. & Mrs. Smith (2005).en-zh.ass"),
            ("St. Elmo's Fire (1985).srt", "St. Elmo's Fire (1985).en-zh.ass"),
            (
                "A.I. Artificial Intelligence (2001).srt",
                "A.I. Artificial Intelligence (2001).en-zh.ass",
            ),
            ("U.S. Marshals (1998).fr.srt", "U.S. Marshals (1998).en-zh.ass"),
            (
                "L.A. Confidential (1997).WEBDL-1080p.en.srt",
                "L.A. Confidential (1997).WEBDL-1080p.en-zh.ass",
            ),
        ]
        for input_file, expected in test_cases:
            result = generate_translation_filename(input_file)
            assert result == expected

    def test_custom_languages(self):
        """Test with custom source and target languages."""
        input_file = "movie.en.srt"

        # Test different target languages
        assert (
            generate_translation_filename(input_file, "en", "fr") == "movie.en-fr.ass"
        )
        assert (
            generate_translation_filename(input_file, "en", "es") == "movie.en-es.ass"
        )
        assert (
            generate_translation_filename(input_file, "en", "de") == "movie.en-de.ass"
        )

        # Test different source languages
        assert (
            generate_translation_filename(input_file, "zh", "en") == "movie.zh-en.ass"
        )
        assert (
            generate_translation_filename(input_file, "fr", "en") == "movie.fr-en.ass"
        )

    def test_no_extension_file(self):
        """Test file without extension."""
        result = generate_translation_filename("movie")
        assert result == "movie.en-zh.ass"

    def test_non_subtitle_extension(self):
        """Test files with non-subtitle extensions."""
        test_cases = [
            ("movie.txt", "movie.txt.en-zh.ass"),
            ("readme.md", "readme.md.en-zh.ass"),
            ("data.json", "data.json.en-zh.ass"),
        ]
        for input_file, expected in test_cases:
            result = generate_translation_filename(input_file)
            assert result == expected

    def test_case_insensitive_extensions(self):
        """Test case insensitive extension handling."""
        test_cases = [
            ("movie.SRT", "movie.en-zh.ass"),
            ("movie.ASS", "movie.en-zh.ass"),
            ("movie.VTT", "movie.en-zh.ass"),
            ("movie.EN.SRT", "movie.en-zh.ass"),
        ]
        for input_file, expected in test_cases:
            result = generate_translation_filename(input_file)
            assert result == expected

    def test_multiple_language_codes_in_filename(self):
        """Test filenames that might have multiple language-like patterns."""
        test_cases = [
            ("movie.v2.en.srt", "movie.v2.en-zh.ass"),
            ("series.s01e01.en.srt", "series.s01e01.en-zh.ass"),
            ("film.2023.fr.srt", "film.2023.en-zh.ass"),
        ]
        for input_file, expected in test_cases:
            result = generate_translation_filename(input_file)
            assert result == expected

    def test_path_with_directories(self):
        """Test that function works with full paths."""
        input_path = "/media/subtitles/tick, tick. BOOM! (2021) WEBDL-2160p.en.srt"
        expected = "tick, tick. BOOM! (2021) WEBDL-2160p.en-zh.ass"
        result = generate_translation_filename(input_path)
        assert result == expected

    def test_edge_cases(self):
        """Test various edge cases."""
        test_cases = [
            ("", ".en-zh.ass"),  # Empty filename
            (".", ".en-zh.ass"),  # Just a dot
            ("..srt", "..en-zh.ass"),  # Double dot with extension
            ("movie.", "movie..en-zh.ass"),  # Trailing dot
            ("movie..srt", "movie..en-zh.ass"),  # Double dot before extension
        ]
        for input_file, expected in test_cases:
            result = generate_translation_filename(input_file)
            assert result == expected

    def test_preserves_special_characters(self):
        """Test that special characters in filename are preserved."""
        test_cases = [
            ("movie (2023).srt", "movie (2023).en-zh.ass"),
            ("movie [PROPER].srt", "movie [PROPER].en-zh.ass"),
            ("movie & sequel.srt", "movie & sequel.en-zh.ass"),
            ("movie's title.srt", "movie's title.en-zh.ass"),
            ("movie-title.srt", "movie-title.en-zh.ass"),
            ("movie_title.srt", "movie_title.en-zh.ass"),
        ]
        for input_file, expected in test_cases:
            result = generate_translation_filename(input_file)
            assert result == expected
