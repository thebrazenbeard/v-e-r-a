from pathlib import Path
import json
import unittest

from protocol.veraport_controller_identity import (
    ControllerIdentityError,
    KeyIdDerivationUnresolved,
    PRINCIPAL_DERIVATION_CONTRACT,
    controller_key_id_from_spki_der,
    controller_principal_from_spki_der,
    recovery_controller_principal,
    rotation_controller_principal,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "protocol" / "VERAPORT_CONTROLLER_ROTATION_V2.json"

SPKI_DER_HEX = (
    "3059301306072a8648ce3d020106082a8648ce3d03010703420004"
    "6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945"
    "d898c2964fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ece"
    "cbb6406837bf51f5"
)
EXPECTED_SHA256 = "5cd252fb0ce8932436faf8ccd1040981b89ee4ad6b9fe9e2a2b7e71aacb27cd3"
EXPECTED_PRINCIPAL = "controller:" + EXPECTED_SHA256

ID_EC_PUBLIC_KEY_OID = bytes.fromhex("2a8648ce3d0201")
RSA_ENCRYPTION_OID = bytes.fromhex("2a864886f70d010101")
SECP384R1_OID = bytes.fromhex("2b81040022")


def load_contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def _tlv(tag: int, content: bytes) -> bytes:
    if len(content) >= 0x80:
        raise AssertionError("test helper only emits short-form DER")
    return bytes((tag, len(content))) + content


def _oid(value: bytes) -> bytes:
    return _tlv(0x06, value)


def _spki(algorithm_identifier: bytes, bit_string_payload: bytes) -> bytes:
    algorithm = _tlv(0x30, algorithm_identifier)
    bit_string = _tlv(0x03, b"\x00" + bit_string_payload)
    return _tlv(0x30, algorithm + bit_string)


class VeraPortControllerRotationV2Tests(unittest.TestCase):
    def test_public_spki_known_answer_vector_is_exact(self):
        spki = bytes.fromhex(SPKI_DER_HEX)
        self.assertEqual(91, len(spki))
        self.assertEqual(EXPECTED_PRINCIPAL, controller_principal_from_spki_der(spki))

        vector = load_contract()["synthetic_known_answer_vectors"][0]
        self.assertEqual(SPKI_DER_HEX, vector["spki_der_hex"])
        self.assertEqual(EXPECTED_SHA256, vector["sha256_hex"])
        self.assertEqual(EXPECTED_PRINCIPAL, vector["controller_principal"])

    def test_recovery_and_rotation_use_the_same_principal_primitive(self):
        spki = bytes.fromhex(SPKI_DER_HEX)
        self.assertEqual(EXPECTED_PRINCIPAL, recovery_controller_principal(spki))
        self.assertEqual(EXPECTED_PRINCIPAL, rotation_controller_principal(spki))

        contract = load_contract()
        self.assertEqual(
            PRINCIPAL_DERIVATION_CONTRACT,
            contract["controller_identity_derivation"]["contract_id"],
        )
        self.assertTrue(
            contract["controller_identity_derivation"][
                "recovery_and_rotation_share_exact_primitive"
            ]
        )
        self.assertEqual(
            PRINCIPAL_DERIVATION_CONTRACT,
            contract["rotation"]["new_identity"]["principal_derivation_contract"],
        )

    def test_principal_serialization_is_exact_lowercase_sha256(self):
        principal = controller_principal_from_spki_der(bytes.fromhex(SPKI_DER_HEX))
        self.assertTrue(principal.startswith("controller:"))
        self.assertEqual(principal.lower(), principal)
        self.assertEqual(64, len(principal.removeprefix("controller:")))

    def test_empty_or_non_bytes_spki_fails_closed(self):
        for bad in (b"", "not-bytes", bytearray(b"x"), None):
            with self.subTest(value=repr(bad)):
                with self.assertRaises(ControllerIdentityError):
                    controller_principal_from_spki_der(bad)  # type: ignore[arg-type]

    def test_arbitrary_truncated_and_trailing_der_fail_closed(self):
        spki = bytes.fromhex(SPKI_DER_HEX)
        for bad in (b"x", spki[:-1], spki + b"\x00"):
            with self.subTest(length=len(bad)):
                with self.assertRaises(ControllerIdentityError):
                    controller_principal_from_spki_der(bad)

    def test_non_ec_algorithm_is_rejected(self):
        rsa_algorithm = _oid(RSA_ENCRYPTION_OID) + b"\x05\x00"
        rsa_spki = _spki(rsa_algorithm, b"\x30\x00")
        with self.assertRaises(ControllerIdentityError):
            controller_principal_from_spki_der(rsa_spki)

    def test_wrong_ec_curve_is_rejected(self):
        p256_point = bytes.fromhex(SPKI_DER_HEX)[26:]
        wrong_curve_spki = _spki(
            _oid(ID_EC_PUBLIC_KEY_OID) + _oid(SECP384R1_OID),
            p256_point,
        )
        with self.assertRaisesRegex(ControllerIdentityError, "P-256"):
            controller_principal_from_spki_der(wrong_curve_spki)

    def test_off_curve_p256_point_is_rejected(self):
        spki = bytearray(bytes.fromhex(SPKI_DER_HEX))
        spki[-1] ^= 0x01
        with self.assertRaisesRegex(ControllerIdentityError, "not on the P-256 curve"):
            controller_principal_from_spki_der(bytes(spki))

    def test_key_id_validates_spki_domain_before_unresolved_gate(self):
        with self.assertRaises(ControllerIdentityError):
            controller_key_id_from_spki_der(b"x")

    def test_key_id_derivation_is_not_invented(self):
        spki = bytes.fromhex(SPKI_DER_HEX)
        with self.assertRaisesRegex(KeyIdDerivationUnresolved, "does not define"):
            controller_key_id_from_spki_der(spki)

        key_id = load_contract()["key_id_derivation"]
        self.assertEqual("UNRESOLVED_OWNING_PROTOCOL_GAP", key_id["status"])
        self.assertIn(
            "DO_NOT_ASSUME_KEY_ID_EQUALS_PRINCIPAL_DIGEST",
            key_id["forbidden_inference"],
        )

    def test_rotation_is_blocked_before_credential_effect_until_key_id_spec_exists(self):
        contract = load_contract()
        self.assertEqual(
            "BLOCKED_PENDING_OWNER_KEY_ID_SPEC_AND_PATRICK_EXACT_EFFECT_AUTHORITY",
            contract["rotation"]["availability"],
        )
        self.assertTrue(
            contract["key_id_derivation"]["operational_gate"].startswith(
                "ROTATION_OR_ENROLLMENT_MUST_STOP_BEFORE_KEY_GENERATION_OR_TRUST_MUTATION"
            )
        )

    def test_real_credential_effects_remain_protected(self):
        authority = load_contract()["authority"]
        self.assertEqual("PATRICK_EXACT_AUTHORITY_REQUIRED", authority["key_generation"])
        self.assertEqual("PATRICK_EXACT_AUTHORITY_REQUIRED", authority["trust_mutation"])
        self.assertEqual("PATRICK_EXACT_AUTHORITY_REQUIRED", authority["acl_mutation"])
        self.assertEqual("PATRICK_EXACT_AUTHORITY_REQUIRED", authority["service_restart"])
        self.assertEqual(
            "PATRICK_EXACT_AUTHORITY_REQUIRED",
            authority["old_controller_retirement"],
        )

    def test_secret_material_is_excluded_from_durable_receipts(self):
        contract = load_contract()
        self.assertIn("PRIVATE_KEY_BYTES", contract["receipts"]["never_record"])
        identity = contract["rotation"]["new_identity"]
        self.assertEqual("FORBIDDEN", identity["private_key_git"])
        self.assertEqual("FORBIDDEN", identity["private_key_bus"])
        self.assertEqual("FORBIDDEN", identity["private_key_logs"])
        self.assertEqual("FORBIDDEN", identity["private_key_screenshots"])


if __name__ == "__main__":
    unittest.main()
