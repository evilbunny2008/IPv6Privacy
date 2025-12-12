#!/usr/bin/python3

#
# Simple script to generate a CA PKI key pair and a server key pair acceptable bu Adguard Home and uhttpd running on OpenWRT
# TODO: Could be made more useful by accepting and reading command line arguments so multiple server certs could be issued etc
#

import datetime
import ipaddress

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID


def outputCertDetails(cert):
    print("Certificate Details:")
    print("-------------------")

    # Subject
    print("Subject:", cert.subject.rfc4514_string())

    # Issuer
    print("Issuer:", cert.issuer.rfc4514_string())

    # Serial number
    print("Serial Number:", cert.serial_number)

    # Validity
    print("Not Before:", cert.not_valid_before_utc.astimezone())
    print("Not After :", cert.not_valid_after_utc.astimezone())

    # Signature algorithm
    print("Signature Algorithm OID:", cert.signature_algorithm_oid._name)

    # Public key info
    pubkey = cert.public_key()
    print("Public Key Type:", type(pubkey).__name__)
    if hasattr(pubkey, "public_bytes"):
        print("Public Key (PEM):")
        print(pubkey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode())

    # Extensions
    if cert.extensions:
        print("\nX.509v3 Extensions:")
        for ext in cert.extensions:
            print(f"- {ext.oid._name}: {ext.value}")

utc_now = datetime.datetime.now(datetime.timezone.utc)

# Generate CA / signing key
ca_key = ec.generate_private_key(ec.SECP256R1())

with open("router_ca_ec.key", "wb") as f:
    f.write(ca_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

ca_subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, u'MyRootCA (EC SECP256R1/SHA512)')])
ca_cert = x509.CertificateBuilder()\
    .subject_name(ca_subject)\
    .issuer_name(ca_subject)\
    .public_key(ca_key.public_key())\
    .serial_number(x509.random_serial_number())\
    .not_valid_before(utc_now)\
    .not_valid_after(utc_now + datetime.timedelta(days=10000))\
    .sign(private_key=ca_key, algorithm=hashes.SHA512())

with open("router_ca_ec.crt", "wb") as f:
    f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

# Generate server key for certificate
router_key = ec.generate_private_key(ec.SECP256R1())

# Build self-signed certificate
router_subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, u'myrouter.example.com')])
router_cert = x509.CertificateBuilder()\
    .subject_name(router_subject)\
    .issuer_name(ca_subject)\
    .public_key(router_key.public_key())\
    .serial_number(x509.random_serial_number())\
    .not_valid_before(utc_now)\
    .not_valid_after(utc_now + datetime.timedelta(days=10000))\
    .add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(u'myrouter.example.com'),
            x509.IPAddress(ipaddress.IPv6Address('fd00:1234:5678:abcd::1')),
            x509.IPAddress(ipaddress.IPv4Address('192.168.0.1')),
            x509.IPAddress(ipaddress.IPv6Address('fd00:1234:5678:abce::1')),
            x509.IPAddress(ipaddress.IPv4Address('192.168.1.1')),
        ]), critical=False
    )\
    .sign(private_key=ca_key, algorithm=hashes.SHA512())

# Save certificate and keys
with open("router_ec.key", "wb") as f:
    f.write(router_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

with open("router_ec.crt", "wb") as f:
    f.write(router_cert.public_bytes(serialization.Encoding.PEM))

print("Generated:")
print("  - CA private key: router_ca_ec.key")
print("  - CA certificate: " + ca_subject.rfc4514_string())

# Check CA cert details...
with open("router_ca_ec.crt", "rb") as f:
    cert = x509.load_pem_x509_certificate(f.read(), default_backend())
    outputCertDetails(cert)

print("\n  - Router EC SECP256R1 key: router_ec.key")
print("  - Router certificate: router_ec.crt (signed by MyRootCA, DNS+IPv4+IPv6 SAN)")

# Check non-CA cert details...
with open("router_ec.crt", "rb") as f:
    cert = x509.load_pem_x509_certificate(f.read(), default_backend())
    outputCertDetails(cert)

print("\n")
