from models.magic_castle.magic_castle_configuration import MagicCastleConfiguration
from tests.test_helpers import *
from marshmallow.exceptions import ValidationError


def test_constructor_none():
    config = MagicCastleConfiguration()
    assert config.dump() == {}


def test_constructor_valid():
    config = MagicCastleConfiguration(
        {
            "cluster_name": "foo",
            "domain": "bar.com",
            "image": "CentOS-7-x64-2019-07",
            "nb_users": 17,
            "instances": {
                "mgmt": {"type": "p4-6gb", "count": 1},
                "login": {"type": "p4-6gb", "count": 1},
                "node": {"type": "p2-3gb", "count": 3},
            },
            "storage": {
                "type": "nfs",
                "home_size": 50,
                "project_size": 1,
                "scratch_size": 1,
            },
            "public_keys": [""],
            "guest_passwd": '1234\\56789\t "',
            "os_floating_ips": [],
        }
    )
    assert config.dump() == {
        "cluster_name": "foo",
        "domain": "bar.com",
        "image": "CentOS-7-x64-2019-07",
        "nb_users": 17,
        "instances": {
            "mgmt": {"type": "p4-6gb", "count": 1},
            "login": {"type": "p4-6gb", "count": 1},
            "node": {"type": "p2-3gb", "count": 3},
        },
        "storage": {
            "type": "nfs",
            "home_size": 50,
            "project_size": 1,
            "scratch_size": 1,
        },
        "public_keys": [""],
        "guest_passwd": '1234\\56789\t "',
        "os_floating_ips": [],
    }


def test_constructor_invalid():
    with pytest.raises(ValidationError):
        # Invalid cluster_name
        MagicCastleConfiguration(
            {
                "cluster_name": "foo!",
                "domain": "bar.com",
                "image": "CentOS-7-x64-2019-07",
                "nb_users": 17,
                "instances": {
                    "mgmt": {"type": "p4-6gb", "count": 1},
                    "login": {"type": "p4-6gb", "count": 1},
                    "node": {"type": "p2-3gb", "count": 3},
                },
                "storage": {
                    "type": "nfs",
                    "home_size": 50,
                    "project_size": 1,
                    "scratch_size": 1,
                },
                "public_keys": [""],
                "guest_passwd": '1234\\56789\t "',
                "os_floating_ips": [],
            }
        )


def test_get_from_dict_valid():
    config = MagicCastleConfiguration.get_from_dict(
        {
            "cluster_name": "foo",
            "domain": "bar.com",
            "image": "CentOS-7-x64-2019-07",
            "nb_users": 17,
            "instances": {
                "mgmt": {"type": "p4-6gb", "count": 1},
                "login": {"type": "p4-6gb", "count": 1},
                "node": {"type": "p2-3gb", "count": 3},
            },
            "storage": {
                "type": "nfs",
                "home_size": 50,
                "project_size": 1,
                "scratch_size": 1,
            },
            "public_keys": [""],
            "guest_passwd": '1234\\56789\t "',
            "os_floating_ips": [],
        }
    )
    assert config.dump() == {
        "cluster_name": "foo",
        "domain": "bar.com",
        "image": "CentOS-7-x64-2019-07",
        "nb_users": 17,
        "instances": {
            "mgmt": {"type": "p4-6gb", "count": 1},
            "login": {"type": "p4-6gb", "count": 1},
            "node": {"type": "p2-3gb", "count": 3},
        },
        "storage": {
            "type": "nfs",
            "home_size": 50,
            "project_size": 1,
            "scratch_size": 1,
        },
        "public_keys": [""],
        "guest_passwd": '1234\\56789\t "',
        "os_floating_ips": [],
    }


def test_get_from_dict_automatic_floating_ip():
    config = MagicCastleConfiguration.get_from_dict(
        {
            "cluster_name": "foo",
            "domain": "bar.com",
            "image": "CentOS-7-x64-2019-07",
            "nb_users": 17,
            "instances": {
                "mgmt": {"type": "p4-6gb", "count": 1},
                "login": {"type": "p4-6gb", "count": 1},
                "node": {"type": "p2-3gb", "count": 3},
            },
            "storage": {
                "type": "nfs",
                "home_size": 50,
                "project_size": 1,
                "scratch_size": 1,
            },
            "public_keys": [""],
            "guest_passwd": '1234\\56789\t "',
            "os_floating_ips": ["Automatic allocation"],
        }
    )
    assert config.dump() == {
        "cluster_name": "foo",
        "domain": "bar.com",
        "image": "CentOS-7-x64-2019-07",
        "nb_users": 17,
        "instances": {
            "mgmt": {"type": "p4-6gb", "count": 1},
            "login": {"type": "p4-6gb", "count": 1},
            "node": {"type": "p2-3gb", "count": 3},
        },
        "storage": {
            "type": "nfs",
            "home_size": 50,
            "project_size": 1,
            "scratch_size": 1,
        },
        "public_keys": [""],
        "guest_passwd": '1234\\56789\t "',
        "os_floating_ips": [],
    }


def test_get_from_dict_invalid_floating_ip():
    config = MagicCastleConfiguration.get_from_dict(
        {
            "cluster_name": "foo",
            "domain": "bar.com",
            "image": "CentOS-7-x64-2019-07",
            "nb_users": 17,
            "instances": {
                "mgmt": {"type": "p4-6gb", "count": 1},
                "login": {"type": "p4-6gb", "count": 1},
                "node": {"type": "p2-3gb", "count": 3},
            },
            "storage": {
                "type": "nfs",
                "home_size": 50,
                "project_size": 1,
                "scratch_size": 1,
            },
            "public_keys": [""],
            "guest_passwd": '1234\\56789\t "',
            "os_floating_ips": ["4.4.4.4"],
        }
    )
    assert config.dump() == {
        "cluster_name": "foo",
        "domain": "bar.com",
        "image": "CentOS-7-x64-2019-07",
        "nb_users": 17,
        "instances": {
            "mgmt": {"type": "p4-6gb", "count": 1},
            "login": {"type": "p4-6gb", "count": 1},
            "node": {"type": "p2-3gb", "count": 3},
        },
        "storage": {
            "type": "nfs",
            "home_size": 50,
            "project_size": 1,
            "scratch_size": 1,
        },
        "public_keys": [""],
        "guest_passwd": '1234\\56789\t "',
        "os_floating_ips": [],
    }


def test_get_from_state_file_valid():
    config = MagicCastleConfiguration.get_from_state_file(
        "missingnodes.sub.example.com"
    )
    assert config.dump() == {
        "cluster_name": "missingnodes",
        "domain": "sub.example.com",
        "image": "CentOS-7-x64-2019-07",
        "nb_users": 10,
        "instances": {
            "mgmt": {"type": "", "count": 0},
            "login": {"type": "", "count": 0},
            "node": {"type": "", "count": 0},
        },
        "storage": {
            "type": "nfs",
            "home_size": 100,
            "project_size": 50,
            "scratch_size": 50,
        },
        "public_keys": ["ssh-rsa FAKE"],
        "guest_passwd": "password-123",
        "os_floating_ips": ["100.101.102.103"],
    }


def test_get_from_state_file_not_found():
    with pytest.raises(FileNotFoundError):
        MagicCastleConfiguration.get_from_state_file("non-existing")


def test_get_from_main_tf_json_file_valid():
    config = MagicCastleConfiguration.get_from_main_tf_json_file(
        "missingnodes.sub.example.com"
    )
    assert config.dump() == {
        "cluster_name": "missingnodes",
        "domain": "sub.example.com",
        "image": "CentOS-7-x64-2019-07",
        "nb_users": 10,
        "instances": {
            "mgmt": {"type": "p4-6gb", "count": 1},
            "login": {"type": "p4-6gb", "count": 1},
            "node": {"type": "p2-3gb", "count": 1},
        },
        "storage": {
            "type": "nfs",
            "home_size": 100,
            "project_size": 50,
            "scratch_size": 50,
        },
        "public_keys": [],
        "guest_passwd": "",
        "os_floating_ips": [],
    }


def test_get_from_main_tf_json_file_not_found():
    with pytest.raises(FileNotFoundError):
        MagicCastleConfiguration.get_from_main_tf_json_file("non-existing")


def test_update_main_tf_json_file():
    modified_config = MagicCastleConfiguration.get_from_dict(
        {
            "cluster_name": "missingnodes",
            "domain": "sub.example.com",
            "image": "CentOS-7-x64-2019-07",
            "nb_users": 30,
            "instances": {
                "mgmt": {"type": "p4-6gb", "count": 1},
                "login": {"type": "p4-6gb", "count": 1},
                "node": {"type": "p2-3gb", "count": 12},
            },
            "storage": {
                "type": "nfs",
                "home_size": 400,
                "project_size": 12,
                "scratch_size": 50,
            },
            "public_keys": ["ssh-rsa FOOBAR"],
            "guest_passwd": "",
            "os_floating_ips": [],
        }
    )
    modified_config.update_main_tf_json_file()
    saved_config = MagicCastleConfiguration.get_from_main_tf_json_file(
        "missingnodes.sub.example.com"
    )
    assert saved_config.dump() == {
        "cluster_name": "missingnodes",
        "domain": "sub.example.com",
        "image": "CentOS-7-x64-2019-07",
        "nb_users": 30,
        "instances": {
            "mgmt": {"type": "p4-6gb", "count": 1},
            "login": {"type": "p4-6gb", "count": 1},
            "node": {"type": "p2-3gb", "count": 12},
        },
        "storage": {
            "type": "nfs",
            "home_size": 400,
            "project_size": 12,
            "scratch_size": 50,
        },
        "public_keys": ["ssh-rsa FOOBAR"],
        "guest_passwd": "",
        "os_floating_ips": [],
    }


def test_get_hostname():
    config = MagicCastleConfiguration(
        {
            "cluster_name": "foo",
            "domain": "bar.com",
            "image": "CentOS-7-x64-2019-07",
            "nb_users": 17,
            "instances": {
                "mgmt": {"type": "p4-6gb", "count": 1},
                "login": {"type": "p4-6gb", "count": 1},
                "node": {"type": "p2-3gb", "count": 3},
            },
            "storage": {
                "type": "nfs",
                "home_size": 50,
                "project_size": 1,
                "scratch_size": 1,
            },
            "public_keys": [""],
            "guest_passwd": '1234\\56789\t "',
            "os_floating_ips": [],
        }
    )
    assert config.get_hostname() == "foo.bar.com"
