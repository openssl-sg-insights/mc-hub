import pytest

from mchub.models.magic_castle.cluster_status_code import ClusterStatusCode

from ..test_helpers import *  # noqa;
from ..mocks.configuration.config_mock import config_auth_saml_mock  # noqa;
from ..data import (
    NON_EXISTING_CLUSTER_CONFIGURATION,
    EXISTING_CLUSTER_CONFIGURATION,
    IGNORE_FIELDS,
    EXISTING_HOSTNAME,
    NON_EXISTING_HOSTNAME,
    EXISTING_CLUSTER_STATE,
    ALICE_HEADERS,
    BOB_HEADERS,
    CLUSTERS,
    PROGRESS_DATA,
)


# GET /api/users/me
def test_get_current_user_authentified(client):
    res = client.get(f"/api/users/me", headers=ALICE_HEADERS)
    assert res.get_json() == {
        "username": "alice",
        "usertype": "saml",
        "public_keys": ["ssh-rsa FAKE"],
    }
    res = client.get(f"/api/users/me", headers=BOB_HEADERS)
    assert res.get_json() == {
        "username": "bob12.bobby",
        "usertype": "saml",
        "public_keys": ["ssh-rsa FAKE"],
    }


# GET /api/users/me
def test_get_current_user_non_authentified(client):
    res = client.get(f"/api/users/me")
    assert res.get_json() == {"message": "You need to be authenticated."}


# GET /api/magic_castle
def test_get_all_magic_castle_names(client):
    res = client.get(f"/api/magic-castles", headers=ALICE_HEADERS)
    results = {}
    for result in res.get_json():
        for field in IGNORE_FIELDS:
            result.pop(field)
        results[result["hostname"]] = result

    clusters = [
        "buildplanning.calculquebec.cloud",
        "created.calculquebec.cloud",
        "valid1.calculquebec.cloud",
    ]
    for cluster_name in clusters:
        assert results[cluster_name] == CLUSTERS[cluster_name]

    assert res.status_code == 200


def test_query_magic_castles_local(client):
    # No authentication header at all
    res = client.get(f"/api/magic-castles")
    assert res.get_json() == {"message": "You need to be authenticated."}
    assert res.status_code != 200

    # Missing some authentication headers
    res = client.get(
        f"/api/magic-castles",
        headers={"eduPersonPrincipalName": "alice@computecanada.ca"},
    )
    assert res.get_json() == {"message": "You need to be authenticated."}
    assert res.status_code != 200


# GET /api/magic-castles/<hostname>
def test_get_state_existing(client):
    res = client.get(f"/api/magic-castles/{EXISTING_HOSTNAME}", headers=ALICE_HEADERS)
    state = res.get_json()
    for field in IGNORE_FIELDS:
        state.pop(field)
    assert state == EXISTING_CLUSTER_STATE
    assert res.status_code == 200


def test_get_state_non_existing(client):
    res = client.get(
        f"/api/magic-castles/{NON_EXISTING_HOSTNAME}", headers=ALICE_HEADERS
    )
    assert res.get_json() == {"message": "This cluster does not exist."}
    assert res.status_code != 200


def test_get_state_not_owned(client):
    res = client.get(
        f"/api/magic-castles/missingfloatingips.c3.ca", headers=ALICE_HEADERS
    )
    assert res.get_json() == {"message": "This cluster does not exist."}
    assert res.status_code != 200


# GET /api/magic-castles/<hostname>/status
@pytest.mark.skip(reason="source of truth is currently false")
def test_get_status(mocker, client):
    res = client.get(
        f"/api/magic-castles/missingfloatingips.c3.ca/status", headers=BOB_HEADERS
    )
    assert res.get_json() == PROGRESS_DATA


def test_get_status_code(client):
    res = client.get(
        f"/api/magic-castles/{NON_EXISTING_HOSTNAME}/status", headers=ALICE_HEADERS
    )
    assert res.get_json()["status"] == "not_found"

    orm = MagicCastleORM.query.filter_by(hostname=EXISTING_HOSTNAME).first()
    orm.status = ClusterStatusCode.BUILD_RUNNING
    db.session.commit()
    res = client.get(
        f"/api/magic-castles/{EXISTING_HOSTNAME}/status", headers=ALICE_HEADERS
    )
    assert res.get_json()["status"] == "build_running"

    orm = MagicCastleORM.query.filter_by(hostname=EXISTING_HOSTNAME).first()
    orm.status = ClusterStatusCode.PROVISIONING_SUCCESS
    db.session.commit()
    res = client.get(
        f"/api/magic-castles/{EXISTING_HOSTNAME}/status", headers=ALICE_HEADERS
    )
    assert res.get_json()["status"] == "provisioning_success"

    orm = MagicCastleORM.query.filter_by(hostname=EXISTING_HOSTNAME).first()
    orm.status = ClusterStatusCode.BUILD_ERROR
    db.session.commit()
    res = client.get(
        f"/api/magic-castles/{EXISTING_HOSTNAME}/status", headers=ALICE_HEADERS
    )
    assert res.get_json()["status"] == "build_error"

    orm = MagicCastleORM.query.filter_by(hostname=EXISTING_HOSTNAME).first()
    orm.status = ClusterStatusCode.DESTROY_RUNNING
    db.session.commit()
    res = client.get(
        f"/api/magic-castles/{EXISTING_HOSTNAME}/status", headers=ALICE_HEADERS
    )
    assert res.get_json()["status"] == "destroy_running"

    orm = MagicCastleORM.query.filter_by(hostname=EXISTING_HOSTNAME).first()
    orm.status = ClusterStatusCode.DESTROY_ERROR
    db.session.commit()
    res = client.get(
        f"/api/magic-castles/{EXISTING_HOSTNAME}/status", headers=ALICE_HEADERS
    )
    assert res.get_json()["status"] == "destroy_error"


# DELETE /api/magic-castles/<hostname>
def test_delete_invalid_status(client):
    res = client.delete(
        f"/api/magic-castles/{NON_EXISTING_HOSTNAME}", headers=ALICE_HEADERS
    )
    assert res.get_json() == {"message": "This cluster does not exist."}
    assert res.status_code != 200

    orm = MagicCastleORM.query.filter_by(hostname=EXISTING_HOSTNAME).first()
    orm.status = ClusterStatusCode.DESTROY_RUNNING
    db.session.commit()
    res = client.delete(
        f"/api/magic-castles/{EXISTING_HOSTNAME}", headers=ALICE_HEADERS
    )
    assert res.get_json() == {"message": "This cluster is busy."}
    assert res.status_code != 200

    orm = MagicCastleORM.query.filter_by(hostname=EXISTING_HOSTNAME).first()
    orm.status = ClusterStatusCode.BUILD_RUNNING
    db.session.commit()
    res = client.delete(
        f"/api/magic-castles/{EXISTING_HOSTNAME}", headers=ALICE_HEADERS
    )
    assert res.get_json() == {"message": "This cluster is busy."}
    assert res.status_code != 200


# PUT /api/magic-castles/<hostname>
def test_modify_invalid_status(client):
    res = client.put(
        f"/api/magic-castles/{NON_EXISTING_HOSTNAME}",
        json=NON_EXISTING_CLUSTER_CONFIGURATION,
        headers=ALICE_HEADERS,
    )
    assert res.get_json() == {"message": "This cluster does not exist."}
    assert res.status_code != 200

    orm = MagicCastleORM.query.filter_by(hostname=EXISTING_HOSTNAME).first()
    orm.status = ClusterStatusCode.BUILD_RUNNING
    db.session.commit()
    res = client.put(
        f"/api/magic-castles/{EXISTING_HOSTNAME}",
        json=EXISTING_CLUSTER_CONFIGURATION,
        headers=ALICE_HEADERS,
    )
    assert res.get_json() == {"message": "This cluster is busy."}
    assert res.status_code != 200

    orm = MagicCastleORM.query.filter_by(hostname=EXISTING_HOSTNAME).first()
    orm.status = ClusterStatusCode.DESTROY_RUNNING
    db.session.commit()
    res = client.put(
        f"/api/magic-castles/{EXISTING_HOSTNAME}",
        json=EXISTING_CLUSTER_CONFIGURATION,
        headers=ALICE_HEADERS,
    )
    assert res.get_json() == {"message": "This cluster is busy."}
    assert res.status_code != 200
