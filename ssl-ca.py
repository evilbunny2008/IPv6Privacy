#!/usr/bin/python3

#
# Simple script to generate a CA PKI key pair acceptable by Adguard Home and uhttpd running on OpenWRT
# Note: Adguard doesn't currectly accept/recognise ED25519/X25519 certificates and keys...
#

import datetime
import ipaddress
import os
import sys

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

#
# Default file names for the CA PKI key pair, if you change either make sure to update ssl-server.py as well
#
ca_file_crt = "ca_ec.crt"
ca_file_key = "ca_ec.key"

#
# Nothing else needs configuring below this line
#

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

if os.path.exists(ca_file_crt):
    ca_cert = None
    with open(ca_file_crt, "rb") as f:
        ca_cert = x509.load_pem_x509_certificate(f.read(), default_backend())

    if not ca_cert:
        os.remove(ca_file_crt)

if os.path.exists(ca_file_key):
    ca_key = None
    with open(ca_file_key, "rb") as f:
        ca_key = serialization.load_pem_private_key(f.read(), password=None)

    if not ca_key:
        os.remove(ca_file_key)

if os.path.exists(ca_file_crt) and os.path.exists(ca_file_key):
    print(f"{ca_file_key} and {ca_file_crt} already exists, you don't need to create new ones, did you mean to run ssl-server.py instead?")
    sys.exit()

utc_now = datetime.datetime.now(datetime.timezone.utc)

if not os.path.exists(ca_file_key):
    # Generate CA / signing key
    ca_key = ec.generate_private_key(ec.SECP256R1())

    with open(ca_file_key, "wb") as f:
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

with open(ca_file_crt, "wb") as f:
    f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

print("Generated:")
print(f"  - CA private key: {ca_file_key}")
print(f"  - CA certificate: {ca_file_crt} Subject: " + ca_subject.rfc4514_string())

# Read the CA cert from disk and check details are all good...
with open(ca_file_crt, "rb") as f:
    cert = x509.load_pem_x509_certificate(f.read(), default_backend())
    outputCertDetails(cert)
