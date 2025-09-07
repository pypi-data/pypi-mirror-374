import contextlib
from enum import StrEnum

__all__ = (
    'AttributeOID',
    'AuthorityInformationAccessOID',
    'CRLEntryExtensionOID',
    'CertificatePoliciesOID',
    'EllipticCurveOID',
    'ExtendedKeyUsageOID',
    'ExtensionOID',
    'HashOID',
    'NameOID',
    'OCSPExtensionOID',
    'OCSPResponseType',
    'PaddingOID',
    'PublicKeyAlgorithmOID',
    'SignatureAlgorithmOID',
    'SubjectInformationAccessOID',
    'parse_oid',
)


class AttributeOID(StrEnum):
    UNSTRUCTURED_NAME = '1.2.840.113549.1.9.2'
    CHALLENGE_PASSWORD = '1.2.840.113549.1.9.7'  # noqa: S105


class AuthorityInformationAccessOID(StrEnum):
    OCSP = '1.3.6.1.5.5.7.48.1'
    CA_ISSUERS = '1.3.6.1.5.5.7.48.2'


class CRLEntryExtensionOID(StrEnum):
    CRL_REASON = '2.5.29.21'
    INVALIDITY_DATE = '2.5.29.24'
    CERTIFICATE_ISSUER = '2.5.29.29'


class CertificatePoliciesOID(StrEnum):
    CPS_QUALIFIER = '1.3.6.1.5.5.7.2.1'
    CPS_USER_NOTICE = '1.3.6.1.5.5.7.2.2'
    ANY_POLICY = '2.5.29.32.0'


class EllipticCurveOID(StrEnum):
    # cryptography's cert.public_key().curve.name is lowercase
    secp256r1 = '1.2.840.10045.3.1.7'
    secp384r1 = '1.3.132.0.34'
    secp521r1 = '1.3.132.0.35'


class ExtensionOID(StrEnum):
    MS_CERTIFICATE_TEMPLATE = '1.3.6.1.4.1.311.21.7'
    PRECERT_SIGNED_CERTIFICATE_TIMESTAMPS = '1.3.6.1.4.1.11129.2.4.2'
    PRECERT_POISON = '1.3.6.1.4.1.11129.2.4.3'
    SIGNED_CERTIFICATE_TIMESTAMPS = '1.3.6.1.4.1.11129.2.4.5'
    AUTHORITY_INFORMATION_ACCESS = '1.3.6.1.5.5.7.1.1'  # AIA
    SUBJECT_INFORMATION_ACCESS = '1.3.6.1.5.5.7.1.11'
    TLS_FEATURE = '1.3.6.1.5.5.7.1.24'
    OCSP_NO_CHECK = '1.3.6.1.5.5.7.48.1.5'
    SUBJECT_DIRECTORY_ATTRIBUTES = '2.5.29.9'
    SUBJECT_KEY_IDENTIFIER = '2.5.29.14'  # SKI
    KEY_USAGE = '2.5.29.15'  # KU
    SUBJECT_ALTERNATIVE_NAME = '2.5.29.17'  # SAN
    ISSUER_ALTERNATIVE_NAME = '2.5.29.18'
    BASIC_CONSTRAINTS = '2.5.29.19'
    CRL_NUMBER = '2.5.29.20'
    DELTA_CRL_INDICATOR = '2.5.29.27'
    ISSUING_DISTRIBUTION_POINT = '2.5.29.28'
    NAME_CONSTRAINTS = '2.5.29.30'
    CRL_DISTRIBUTION_POINTS = '2.5.29.31'
    CERTIFICATE_POLICIES = '2.5.29.32'
    POLICY_MAPPINGS = '2.5.29.33'
    AUTHORITY_KEY_IDENTIFIER = '2.5.29.35'  # AKI
    POLICY_CONSTRAINTS = '2.5.29.36'
    EXTENDED_KEY_USAGE = '2.5.29.37'  # EKI
    FRESHEST_CRL = '2.5.29.46'
    INHIBIT_ANY_POLICY = '2.5.29.54'


class ExtendedKeyUsageOID(StrEnum):
    SMARTCARD_LOGON = '1.3.6.1.4.1.311.20.2.2'
    CERTIFICATE_TRANSPARENCY = '1.3.6.1.4.1.11129.2.4.4'
    KERBEROS_PKINIT_KDC = '1.3.6.1.5.2.3.5'
    SERVER_AUTH = '1.3.6.1.5.5.7.3.1'
    CLIENT_AUTH = '1.3.6.1.5.5.7.3.2'
    CODE_SIGNING = '1.3.6.1.5.5.7.3.3'
    EMAIL_PROTECTION = '1.3.6.1.5.5.7.3.4'
    TIME_STAMPING = '1.3.6.1.5.5.7.3.8'
    OCSP_SIGNING = '1.3.6.1.5.5.7.3.9'
    IPSEC_IKE = '1.3.6.1.5.5.7.3.17'
    ANY_EXTENDED_KEY_USAGE = '2.5.29.37.0'


class HashOID(StrEnum):
    sha1 = '1.3.14.3.2.26'
    sha256 = '2.16.840.1.101.3.4.2.1'
    sha384 = '2.16.840.1.101.3.4.2.2'
    sha512 = '2.16.840.1.101.3.4.2.3'


class NameOID(StrEnum):
    USER_ID = '0.9.2342.19200300.100.1.1'
    DOMAIN_COMPONENT = '0.9.2342.19200300.100.1.25'
    INN = '1.2.643.3.131.1.1'
    OGRN = '1.2.643.100.1'
    SNILS = '1.2.643.100.3'
    EMAIL_ADDRESS = '1.2.840.113549.1.9.1'
    UNSTRUCTURED_NAME = '1.2.840.113549.1.9.2'
    JURISDICTION_LOCALITY_NAME = '1.3.6.1.4.1.311.60.2.1.1'
    JURISDICTION_STATE_OR_PROVINCE_NAME = '1.3.6.1.4.1.311.60.2.1.2'
    JURISDICTION_COUNTRY_NAME = '1.3.6.1.4.1.311.60.2.1.3'
    COMMON_NAME = '2.5.4.3'
    SURNAME = '2.5.4.4'
    SERIAL_NUMBER = '2.5.4.5'
    COUNTRY_NAME = '2.5.4.6'
    LOCALITY_NAME = '2.5.4.7'
    STATE_OR_PROVINCE_NAME = '2.5.4.8'
    STREET_ADDRESS = '2.5.4.9'
    ORGANIZATION_NAME = '2.5.4.10'
    ORGANIZATIONAL_UNIT_NAME = '2.5.4.11'
    TITLE = '2.5.4.12'
    BUSINESS_CATEGORY = '2.5.4.15'
    POSTAL_ADDRESS = '2.5.4.16'
    POSTAL_CODE = '2.5.4.17'
    GIVEN_NAME = '2.5.4.42'
    INITIALS = '2.5.4.43'
    GENERATION_QUALIFIER = '2.5.4.44'
    X500_UNIQUE_IDENTIFIER = '2.5.4.45'
    DN_QUALIFIER = '2.5.4.46'
    PSEUDONYM = '2.5.4.65'
    ORGANIZATION_IDENTIFIER = '2.5.4.97'


class OCSPExtensionOID(StrEnum):
    NONCE = '1.3.6.1.5.5.7.48.1.2'
    ACCEPTABLE_RESPONSES = '1.3.6.1.5.5.7.48.1.4'


class OCSPResponseType(StrEnum):
    OCSP = '1.3.6.1.5.5.7.48.1'
    OCSP_BASIC = '1.3.6.1.5.5.7.48.1.1'


class PaddingOID(StrEnum):
    MGF1 = '1.2.840.113549.1.1.8'

class PublicKeyAlgorithmOID(StrEnum):
    DSA = '1.2.840.10040.4.1'
    EC_PUBLIC_KEY = '1.2.840.10045.2.1'
    RSAES_PKCS1_v1_5 = '1.2.840.113549.1.1.1'
    RSASSA_PSS = '1.2.840.113549.1.1.10'
    X25519 = '1.3.101.110'
    X448 = '1.3.101.111'
    ED25519 = '1.3.101.112'
    ED448 = '1.3.101.113'

class SignatureAlgorithmOID(StrEnum):
    GOSTR3411_94_WITH_3410_2001 = '1.2.643.2.2.3'
    GOSTR3410_2012_WITH_3411_2012_256 = '1.2.643.7.1.1.3.2'
    GOSTR3410_2012_WITH_3411_2012_512 = '1.2.643.7.1.1.3.3'
    DSA_WITH_SHA1 = '1.2.840.10040.4.3'
    ECDSA_WITH_SHA1 = '1.2.840.10045.4.1'
    ECDSA_WITH_SHA224 = '1.2.840.10045.4.3.1'
    ECDSA_WITH_SHA256 = '1.2.840.10045.4.3.2'
    ECDSA_WITH_SHA384 = '1.2.840.10045.4.3.3'
    ECDSA_WITH_SHA512 = '1.2.840.10045.4.3.4'
    RSA_WITH_MD5 = '1.2.840.113549.1.1.4'
    RSA_WITH_SHA1 = '1.2.840.113549.1.1.5'
    RSASSA_PSS = '1.2.840.113549.1.1.10'
    RSA_WITH_SHA256 = '1.2.840.113549.1.1.11'
    RSA_WITH_SHA384 = '1.2.840.113549.1.1.12'
    RSA_WITH_SHA512 = '1.2.840.113549.1.1.13'
    RSA_WITH_SHA224 = '1.2.840.113549.1.1.14'
    _RSA_WITH_SHA1 = '1.3.14.3.2.29'
    ED25519 = '1.3.101.112'
    ED448 = '1.3.101.113'
    DSA_WITH_SHA224 = '2.16.840.1.101.3.4.3.1'
    DSA_WITH_SHA256 = '2.16.840.1.101.3.4.3.2'
    DSA_WITH_SHA384 = '2.16.840.1.101.3.4.3.3'
    DSA_WITH_SHA512 = '2.16.840.1.101.3.4.3.4'
    ECDSA_WITH_SHA3_224 = '2.16.840.1.101.3.4.3.9'
    ECDSA_WITH_SHA3_256 = '2.16.840.1.101.3.4.3.10'
    ECDSA_WITH_SHA3_384 = '2.16.840.1.101.3.4.3.11'
    ECDSA_WITH_SHA3_512 = '2.16.840.1.101.3.4.3.12'
    RSA_WITH_SHA3_224 = '2.16.840.1.101.3.4.3.13'
    RSA_WITH_SHA3_256 = '2.16.840.1.101.3.4.3.14'
    RSA_WITH_SHA3_384 = '2.16.840.1.101.3.4.3.15'
    RSA_WITH_SHA3_512 = '2.16.840.1.101.3.4.3.16'


class SubjectInformationAccessOID(StrEnum):
    CA_REPOSITORY = '1.3.6.1.5.5.7.48.5'


def parse_oid(value: str) -> str:
    for Enum in (
        AttributeOID,
        AuthorityInformationAccessOID,
        CRLEntryExtensionOID,
        CertificatePoliciesOID,
        EllipticCurveOID,
        ExtendedKeyUsageOID,
        ExtensionOID,
        HashOID,
        NameOID,
        OCSPExtensionOID,
        OCSPResponseType,
        PaddingOID,
        PublicKeyAlgorithmOID,
        SignatureAlgorithmOID,
        SubjectInformationAccessOID,
    ):
        with contextlib.suppress(ValueError):
            return Enum(value)
    return value
