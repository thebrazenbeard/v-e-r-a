from __future__ import annotations

import hashlib


PRINCIPAL_PREFIX = "controller:"
PRINCIPAL_DERIVATION_CONTRACT = "VERAPORT_CONTROLLER_PRINCIPAL_DERIVATION_V1"

_ID_EC_PUBLIC_KEY_OID = bytes.fromhex("2a8648ce3d0201")
_PRIME256V1_OID = bytes.fromhex("2a8648ce3d030107")
_P256_P = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
_P256_B = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B


class ControllerIdentityError(ValueError):
    """Raised when controller identity material is malformed."""


class KeyIdDerivationUnresolved(RuntimeError):
    """Raised while the owning VeraPort protocol has no exact key-ID derivation."""


def _read_der_length(data: bytes, offset: int) -> tuple[int, int]:
    if offset >= len(data):
        raise ControllerIdentityError("truncated DER length")
    first = data[offset]
    offset += 1
    if first < 0x80:
        return first, offset
    count = first & 0x7F
    if count == 0:
        raise ControllerIdentityError("indefinite DER length is forbidden")
    if count > 4 or offset + count > len(data):
        raise ControllerIdentityError("invalid or truncated DER length")
    if data[offset] == 0:
        raise ControllerIdentityError("non-minimal DER length encoding")
    length = int.from_bytes(data[offset:offset + count], "big")
    if length < 0x80:
        raise ControllerIdentityError("non-minimal DER long-form length")
    return length, offset + count


def _read_der_tlv(data: bytes, offset: int, expected_tag: int) -> tuple[bytes, int]:
    if offset >= len(data) or data[offset] != expected_tag:
        raise ControllerIdentityError(f"expected DER tag 0x{expected_tag:02x}")
    length, content_offset = _read_der_length(data, offset + 1)
    end = content_offset + length
    if end > len(data):
        raise ControllerIdentityError("truncated DER value")
    return data[content_offset:end], end


def _validate_p256_point(bit_string: bytes) -> None:
    if len(bit_string) != 66 or bit_string[0] != 0:
        raise ControllerIdentityError(
            "P-256 SPKI BIT STRING must have zero unused bits and a 65-byte point"
        )
    point = bit_string[1:]
    if len(point) != 65 or point[0] != 0x04:
        raise ControllerIdentityError("P-256 public point must use uncompressed SEC1 form")
    x = int.from_bytes(point[1:33], "big")
    y = int.from_bytes(point[33:65], "big")
    if x >= _P256_P or y >= _P256_P:
        raise ControllerIdentityError("P-256 public point coordinate is out of range")
    rhs = (pow(x, 3, _P256_P) - (3 * x) + _P256_B) % _P256_P
    if pow(y, 2, _P256_P) != rhs:
        raise ControllerIdentityError("public point is not on the P-256 curve")


def _validate_p256_spki_der(spki_der: bytes) -> None:
    if type(spki_der) is not bytes or not spki_der:
        raise ControllerIdentityError("spki_der must be non-empty exact bytes")

    outer, end = _read_der_tlv(spki_der, 0, 0x30)
    if end != len(spki_der):
        raise ControllerIdentityError("trailing bytes after DER SubjectPublicKeyInfo")

    algorithm, offset = _read_der_tlv(outer, 0, 0x30)
    bit_string, outer_end = _read_der_tlv(outer, offset, 0x03)
    if outer_end != len(outer):
        raise ControllerIdentityError("unexpected fields after SPKI subjectPublicKey")

    algorithm_oid, alg_offset = _read_der_tlv(algorithm, 0, 0x06)
    curve_oid, alg_end = _read_der_tlv(algorithm, alg_offset, 0x06)
    if alg_end != len(algorithm):
        raise ControllerIdentityError("unexpected EC AlgorithmIdentifier parameters")
    if algorithm_oid != _ID_EC_PUBLIC_KEY_OID:
        raise ControllerIdentityError("SPKI algorithm must be id-ecPublicKey")
    if curve_oid != _PRIME256V1_OID:
        raise ControllerIdentityError("SPKI named curve must be P-256/secp256r1")

    _validate_p256_point(bit_string)


def controller_principal_from_spki_der(spki_der: bytes) -> str:
    """Derive the exact VeraPort controller principal from validated P-256 DER SPKI."""
    _validate_p256_spki_der(spki_der)
    digest = hashlib.sha256(spki_der).hexdigest()
    return PRINCIPAL_PREFIX + digest


def recovery_controller_principal(spki_der: bytes) -> str:
    """Recovery consumes the same exact principal primitive as rotation."""
    return controller_principal_from_spki_der(spki_der)


def rotation_controller_principal(spki_der: bytes) -> str:
    """Rotation consumes the same exact principal primitive as recovery."""
    return controller_principal_from_spki_der(spki_der)


def controller_key_id_from_spki_der(spki_der: bytes) -> str:
    """Fail closed until the owning VeraPort protocol freezes key-ID semantics."""
    _validate_p256_spki_der(spki_der)
    raise KeyIdDerivationUnresolved(
        "VeraMesh issue #15 requires a key ID derived from public SPKI but does "
        "not define its exact algorithm/encoding; rotation must stop before any "
        "credential or trust effect."
    )
