import toml
from lambda_cache import __version__

def test_version():
    """
    Test that version in __init.py__ matches pyproject.toml file
    """
    with open('../pyproject.toml') as toml_file:
        config = toml.load(toml_file)
        version = config.get('tool').get('poetry').get('version')
    
    assert __version__ == version
    