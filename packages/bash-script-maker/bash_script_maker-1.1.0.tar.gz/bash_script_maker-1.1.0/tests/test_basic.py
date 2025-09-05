"""Basic tests for Bash-Script-Maker"""

import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_import_bash_script_maker():
    """Test that bash_script_maker can be imported"""
    import bash_script_maker
    assert bash_script_maker is not None


def test_import_syntax_highlighter():
    """Test that syntax_highlighter can be imported"""
    import syntax_highlighter
    assert syntax_highlighter is not None


def test_bash_script_maker_class():
    """Test that BashScriptMaker class exists"""
    from bash_script_maker import BashScriptMaker
    assert BashScriptMaker is not None


def test_bash_script_editor_class():
    """Test that BashScriptEditor class exists"""
    from syntax_highlighter import BashScriptEditor
    assert BashScriptEditor is not None


def test_bash_autocomplete_class():
    """Test that BashAutocomplete class exists"""
    from syntax_highlighter import BashAutocomplete
    assert BashAutocomplete is not None


def test_bash_syntax_highlighter_class():
    """Test that BashSyntaxHighlighter class exists"""
    from syntax_highlighter import BashSyntaxHighlighter
    assert BashSyntaxHighlighter is not None


def test_python_version():
    """Test that Python version is 3.8+"""
    assert sys.version_info >= (3, 8)


def test_tkinter_available():
    """Test that tkinter is available"""
    try:
        import tkinter
        assert tkinter is not None
        # Test that we can create basic tkinter objects
        root = tkinter.Tk()
        root.title("Test")
        root.destroy()
    except ImportError:
        pytest.skip("tkinter not available in this environment")
    except tkinter.TclError:
        pytest.skip("tkinter available but no display available (headless environment)")


def test_main_function():
    """Test that main function exists"""
    from bash_script_maker import main
    assert callable(main)


def test_constants():
    """Test that basic constants are defined"""
    from syntax_highlighter import BashAutocomplete
    import tkinter as tk

    # Skip if tkinter is not available or no display
    try:
        root = tk.Tk()
        text_widget = tk.Text(root)
    except tk.TclError:
        pytest.skip("No display available for tkinter tests")
        return

    try:
        autocomplete = BashAutocomplete(text_widget)
        assert hasattr(autocomplete, 'bash_commands')
        assert hasattr(autocomplete, 'bash_keywords')
        assert hasattr(autocomplete, 'command_options')

        # Test that collections are not empty
        assert len(autocomplete.bash_commands) > 0
        assert len(autocomplete.bash_keywords) > 0
        assert len(autocomplete.command_options) > 0
    finally:
        root.destroy()


def test_regex_patterns():
    """Test that regex patterns are properly defined"""
    from syntax_highlighter import BashSyntaxHighlighter
    import tkinter as tk

    # Skip if tkinter is not available or no display
    try:
        root = tk.Tk()
        text_widget = tk.Text(root)
    except tk.TclError:
        pytest.skip("No display available for tkinter tests")
        return

    try:
        highlighter = BashSyntaxHighlighter(text_widget)
        assert hasattr(highlighter, 'patterns')
        assert isinstance(highlighter.patterns, dict)
        assert len(highlighter.patterns) > 0

        # Test specific patterns exist
        expected_patterns = ['comments', 'shebang', 'strings', 'variables', 'commands']
        for pattern in expected_patterns:
            assert pattern in highlighter.patterns
    finally:
        root.destroy()


def test_tab_functionality():
    """Test tab-related functionality"""
    from syntax_highlighter import BashScriptEditor
    import tkinter as tk

    # Skip if tkinter is not available or no display
    try:
        root = tk.Tk()
        text_widget = tk.Text(root)
    except tk.TclError:
        pytest.skip("No display available for tkinter tests")
        return

    try:
        editor = BashScriptEditor(text_widget)

        # Test that tab size is properly set
        assert editor.tab_size == 4

        # Test that indent keywords are defined
        assert hasattr(editor, 'indent_keywords')
        assert hasattr(editor, 'dedent_keywords')

        # Test that collections are not empty
        assert len(editor.indent_keywords) > 0
        assert len(editor.dedent_keywords) > 0
    finally:
        root.destroy()


def test_version_file():
    """Test that version file exists and contains valid version"""
    version_file = os.path.join(os.path.dirname(__file__), '..', 'VERSION')
    assert os.path.exists(version_file)

    with open(version_file, 'r') as f:
        version = f.read().strip()

    # Version should be in format x.y.z
    parts = version.split('.')
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_readme_exists():
    """Test that README.md exists"""
    readme_file = os.path.join(os.path.dirname(__file__), '..', 'README.md')
    assert os.path.exists(readme_file)
    assert os.path.getsize(readme_file) > 0


def test_setup_py_exists():
    """Test that setup.py exists"""
    setup_file = os.path.join(os.path.dirname(__file__), '..', 'setup.py')
    assert os.path.exists(setup_file)
    assert os.path.getsize(setup_file) > 0


def test_requirements_exists():
    """Test that requirements.txt exists"""
    req_file = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
    assert os.path.exists(req_file)
    assert os.path.getsize(req_file) > 0


def test_installation_scripts_exist():
    """Test that installation scripts exist"""
    scripts = ['install.sh', 'install_apt.sh', 'install_dnf.sh']
    for script in scripts:
        script_path = os.path.join(os.path.dirname(__file__), '..', script)
        assert os.path.exists(script_path)
        assert os.path.getsize(script_path) > 0
