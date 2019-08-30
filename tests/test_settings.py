import os
import pytest

from click.testing import CliRunner
import wandb.util as util
from wandb import settings as gs
from wandb import env


def test_read_empty_settings():
    settings = gs.Settings()
    assert settings.get('default', 'foo', fallback=None) is None


def test_read_global_setting(global_wandb_settings):
    global_wandb_settings.write("[default]\nfoo = bar\n")
    global_wandb_settings.flush()

    settings = gs.Settings()
    assert settings.get('default', 'foo') == 'bar'


def test_read_local_setting(global_wandb_settings, local_wandb_settings):
    global_wandb_settings.write("[default]\nfoo = baz\n")
    global_wandb_settings.flush()

    local_wandb_settings.write("[default]\nfoo = bar\n")
    local_wandb_settings.flush()

    settings = gs.Settings()
    assert settings.get('default', 'foo') == 'bar'


def test_write_setting_globally(global_wandb_settings):
    settings = gs.Settings()
    settings.set('default', 'foo', 'bar', globally=True)

    with open(global_wandb_settings.name, "r") as f:
        data = f.read()
        assert "[default]" in data
        assert "foo = bar" in data


def test_write_setting_locally(local_wandb_settings):
    settings = gs.Settings()
    settings.set('default', 'foo', 'bar')

    with open(local_wandb_settings.name, "r") as f:
        data = f.read()
        assert "[default]" in data
        assert "foo = bar" in data


def test_items(global_wandb_settings, local_wandb_settings):
    global_wandb_settings.write("[default]\nfoo = baz\n")
    global_wandb_settings.flush()

    local_wandb_settings.write("[default]\nfoo = bar\n")
    local_wandb_settings.flush()

    settings = gs.Settings()

    assert settings.items() == {
        'section': 'default',
        'foo': 'bar',
    }


@pytest.fixture
def global_wandb_settings(tmpdir):
    os.environ[env.CONFIG_DIR] = tmpdir.strpath

    with open(os.path.join(tmpdir.strpath, 'settings'), "w+") as f:
        yield f

    del os.environ[env.CONFIG_DIR]


@pytest.fixture
def local_wandb_settings():
    with CliRunner().isolated_filesystem():
        util.mkdir_exists_ok('wandb')
        with open(os.path.join('wandb', 'settings'), 'w+') as f:
            yield f