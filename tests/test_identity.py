"""Tests for the Identity Governance module."""

from identity import (
    IdentityRegistry,
    MachineIdentity,
    SignedAction,
    generate_key,
    sign,
    verify_signature,
)


def test_generate_key_length():
    key = generate_key()
    assert len(key) == 64
    assert all(c in "0123456789abcdef" for c in key)


def test_sign_and_verify_roundtrip():
    key = generate_key()
    msg = {"action": "test", "value": 42}
    sig = sign(key, msg)
    assert verify_signature(key, msg, sig) is True


def test_signature_fails_on_tamper():
    key = generate_key()
    msg = {"action": "test", "value": 42}
    sig = sign(key, msg)
    msg["value"] = 999
    assert verify_signature(key, msg, sig) is False


def test_signature_fails_with_wrong_key():
    key1 = generate_key()
    key2 = generate_key()
    msg = {"x": 1}
    sig = sign(key1, msg)
    assert verify_signature(key2, msg, sig) is False


def test_register_identity():
    reg = IdentityRegistry(path=":memory:")
    ident = reg.register(name="TestAgent", role="worker")
    assert isinstance(ident, MachineIdentity)
    assert ident.name == "TestAgent"
    assert ident.identity_id.startswith("id:")
    assert ident.active is True
    assert len(reg.identities()) == 1


def test_sign_action_creates_signed_action():
    reg = IdentityRegistry(path=":memory:")
    ident = reg.register(name="A", role="r")
    action = reg.sign_action(ident.identity_id, "test", {"k": "v"})
    assert isinstance(action, SignedAction)
    assert action.action == "test"
    assert len(action.signature) == 64


def test_verify_action():
    reg = IdentityRegistry(path=":memory:")
    ident = reg.register(name="A", role="r")
    action = reg.sign_action(ident.identity_id, "test")
    assert reg.verify_action(action) is True


def test_verify_action_after_tamper():
    reg = IdentityRegistry(path=":memory:")
    ident = reg.register(name="A", role="r")
    action = reg.sign_action(ident.identity_id, "test", {"x": 1})
    action.payload["x"] = 999
    assert reg.verify_action(action) is False


def test_revoked_identity_cannot_sign():
    reg = IdentityRegistry(path=":memory:")
    ident = reg.register(name="A", role="r")
    reg.revoke(ident.identity_id)
    try:
        reg.sign_action(ident.identity_id, "anything")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_verify_all():
    reg = IdentityRegistry(path=":memory:")
    ident = reg.register(name="A", role="r")
    reg.sign_action(ident.identity_id, "a")
    reg.sign_action(ident.identity_id, "b")
    reg.sign_action(ident.identity_id, "c")
    assert reg.verify_all() is True


def test_flush_and_load_roundtrip(tmp_path):
    path = str(tmp_path / "identities.jsonl")
    reg = IdentityRegistry(path=path)
    ident = reg.register(name="Persist", role="tester")
    reg.sign_action(ident.identity_id, "act", {"x": 1})
    reg.flush()

    loaded = IdentityRegistry.load(path)
    assert len(loaded.identities()) == 1
    assert len(loaded.actions()) == 1
    assert loaded.verify_all() is True


def test_unknown_identity_raises():
    reg = IdentityRegistry(path=":memory:")
    try:
        reg.sign_action("id:doesnotexist", "test")
        assert False, "Expected ValueError"
    except ValueError:
        pass
