#!/usr/bin/python

import tempfile

import pkcs11
import random, string
from pkcs11.constants import Attribute

from google.cloud import storage
from cloud_auth_pkcs.gcp.gcpcredentials import GCPCredentials

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

from cloud_auth_pkcs.gcp.gcpcredentials import GCPCredentials
from google.cloud import storage

from cloud_auth_pkcs.aws.awscredentials import AWSCredentials
from cloud_auth_pkcs.aws.awshmaccredentials import AWSHMACCredentials
import boto3

from cloud_auth_pkcs.azure.azurecredentials import AzureCredentials
from azure.storage.blob import BlobServiceClient

from .utils import loadHMAC, loadRSA
import os
import unittest

PKCS_LIB = '/usr/lib/softhsm/libsofthsm2.so'
PIN = 'mynewpin'

class TestGCP(unittest.TestCase):

  def testGCSKey(self):

    SA_EMAIL = os.getenv('CICD_SA_EMAIL')
    SA_PEM = os.getenv('CICD_SA_PEM')
    SA_PROJECT = os.getenv('CICD_SA_PROJECT')
    SA_CICD_BUCKET = os.getenv('CICD_BUCKET')

    private_key = serialization.load_pem_private_key(
          SA_PEM.encode('utf-8'),
          password=None,
          backend=default_backend()
    )

    lib = pkcs11.lib(PKCS_LIB)
    token_label = 'token1'
    key_label=''.join(random.choices(string.ascii_lowercase, k=10))
    id = 'myid'

    token = lib.get_token(token_label=token_label)


    with token.open(rw=True, user_pin=PIN) as session:
      k = loadRSA(session,key_label, id, private_key)

    pc = GCPCredentials(module=PKCS_LIB,
                          token=token_label,
                          label=key_label,
                          pin=PIN,
                          #key_id="5a4faca2018bfdbbf071293615a54fb966ba0bc6",
                          email=SA_EMAIL)

    storage_client = storage.Client(project=SA_PROJECT, credentials=pc)

    objects = storage_client.list_blobs(SA_CICD_BUCKET)
    for o in objects:
      print(o.name)


class TestAWS(unittest.TestCase):

  def testS3RolesAnywhere(self):
    CICD_AWS_CERT = os.getenv('CICD_AWS_CERT')
    CICD_AWS_PEM = os.getenv('CICD_AWS_PEM')
    CICD_AWS_REGION = os.getenv('CICD_AWS_REGION')
    CICD_AWS_TRUST_ANCHOR_ARN = os.getenv('CICD_AWS_TRUST_ANCHOR_ARN')
    CICD_AWS_ROLE_ARN = os.getenv('CICD_AWS_ROLE_ARN')
    CICD_AWS_PROFILE_ARN = os.getenv('CICD_AWS_PROFILE_ARN')

    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".pem") as tmp_file:
      tmp_file.write(CICD_AWS_CERT)
      tmp_file_cert = tmp_file.name    


    private_key = serialization.load_pem_private_key(
          CICD_AWS_PEM.encode('utf-8'),
          password=None,
          backend=default_backend()
    )

    lib = pkcs11.lib(PKCS_LIB)
    token_label = 'token1'
    key_label=''.join(random.choices(string.ascii_lowercase, k=10))
    id = 'myid'

    token = lib.get_token(token_label=token_label)


    with token.open(rw=True, user_pin=PIN) as session:
      k = loadRSA(session,key_label, id, private_key)


    pc = AWSCredentials(module=PKCS_LIB,
                        token=token_label,
                        label=key_label,
                        pin=PIN,

                        public_certificate_file=tmp_file_cert,
                        region=CICD_AWS_REGION,
                        duration_seconds=1000,
                        trust_anchor_arn=CICD_AWS_TRUST_ANCHOR_ARN,
                        session_name="foo",
                        role_arn=CICD_AWS_ROLE_ARN,
                        profile_arn=CICD_AWS_PROFILE_ARN)


    session = pc.get_session()

    s3 = session.resource('s3')

    lenbuckets=(len(list(s3.buckets.all())))
    print(list(s3.buckets.all()))
    self.assertGreaterEqual(1,lenbuckets)


  def testS3HMAC(self):

    CICD_AWS_ACCESS_KEY = os.getenv('CICD_AWS_ACCESS_KEY')
    CICD_AWS_ACCESS_SECRET = os.getenv('CICD_AWS_ACCESS_SECRET')
    CICD_AWS_HMAC_REGION = os.getenv('CICD_AWS_HMAC_REGION')
    CICD_AWS_ROLE_ARN = os.getenv('CICD_AWS_ROLE_ARN')


    lib = pkcs11.lib(PKCS_LIB)
    token_label = 'token1'
    key_label=''.join(random.choices(string.ascii_lowercase, k=10))
    id = 'myid'

    token = lib.get_token(token_label=token_label)


    with token.open(rw=True, user_pin=PIN) as session:
      k = loadHMAC(session,key_label, id, 'AWS4{}'.format(CICD_AWS_ACCESS_SECRET))

    rolesessionName = "mysession"

    pc = AWSHMACCredentials(module=PKCS_LIB,
                          token=token_label,
                          label=key_label,
                          pin=PIN,

                          access_key=CICD_AWS_ACCESS_KEY,
                          region=CICD_AWS_HMAC_REGION,
                          duration_seconds=3600,
                          role_session_name=rolesessionName,
                          assume_role_arn=CICD_AWS_ROLE_ARN,

                          get_session_token=False)

    session = pc.get_session()

    s3 = session.resource('s3')

    lenbuckets=(len(list(s3.buckets.all())))
    print(list(s3.buckets.all()))
    self.assertGreaterEqual(1,lenbuckets)


class TestAzure(unittest.TestCase):
  def testCertificateAuth(self):

    CICD_AZURE_CLIENT_PEM = os.getenv('CICD_AZURE_CLIENT_PEM')
    CICD_AZURE_CERT = os.getenv('CICD_AZURE_CERT')    
    CICD_AZURE_TENANT_ID = os.getenv('CICD_AZURE_TENANT_ID')
    CICD_AZURE_CLIENT_ID = os.getenv('CICD_AZURE_CLIENT_ID')
    CICD_AZURE_STORAGEACCOUNT = os.getenv('CICD_AZURE_STORAGEACCOUNT')
    CICD_AZURE_CONTAINER = os.getenv('CICD_AZURE_CONTAINER')

    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".pem") as tmp_file:
      tmp_file.write(CICD_AZURE_CERT)
      tmp_file_cert = tmp_file.name    


    private_key = serialization.load_pem_private_key(
          CICD_AZURE_CLIENT_PEM.encode('utf-8'),
          password=None,
          backend=default_backend()
    )

    lib = pkcs11.lib(PKCS_LIB)
    token_label = 'token1'
    key_label=''.join(random.choices(string.ascii_lowercase, k=10))
    id = 'myid'

    token = lib.get_token(token_label=token_label)


    with token.open(rw=True, user_pin=PIN) as session:
      k = loadRSA(session,key_label, id, private_key)


    pc = AzureCredentials(
        module=PKCS_LIB,
        token=token_label,
        label=key_label,
        pin=PIN,

        tenant_id=CICD_AZURE_TENANT_ID,
        client_id=CICD_AZURE_CLIENT_ID,
        certificate_path=tmp_file_cert)

    blob_service_client = BlobServiceClient(
        account_url="https://{}.blob.core.windows.net".format(CICD_AZURE_STORAGEACCOUNT),
        credential=pc
    )
    container_client = blob_service_client.get_container_client(CICD_AZURE_CONTAINER)

    blob_list = container_client.list_blobs()
    lenbuckets=(len(list(blob_list)))
    for blob in blob_list:
      print(blob.name)

    self.assertGreaterEqual(1,lenbuckets)


if __name__ == "__main__":
    unittest.main()    