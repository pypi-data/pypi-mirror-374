## Cloud Auth Library using PKCS-11

Python library which supports `TPPKCS-11` embedded authenticated credentials for various cloud providers.

The supported set of providers and credential types:

* `Google Cloud`
  - using [Service Account Credentials](https://cloud.google.com/iam/docs/service-account-creds) where the RSA private key is on the PKCS-11 device

* `AWS`
  - using [IAM Roles Anywhere](https://docs.aws.amazon.com/rolesanywhere/latest/userguide/introduction.html) where the RSA private key is on the PKCS-11 device
  - using [HMAC Access Keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) where the `AWS_SECRET_ACCESS_KEY` is on the PKCS-11 device

* `Azure`
  - using [Certificate Credentials](https://learn.microsoft.com/en-us/entra/identity-platform/certificate-credentials) where the RSA private key is on the PKCS-11 device

on python pypi: [https://pypi.org/project/cloud-auth-pkcs/](https://pypi.org/project/cloud-auth-pkcs/)

> This code is not affiliated with or supported by google


Also see

* [Cloud Auth Library using Trusted Platform Module (TPM)](https://github.com/salrashid123/cloud_auth_tpm)
* [PKCS-11 Credential Source for Google Cloud SDK](https://github.com/salrashid123/gcp-adc-pkcs)
* [AWS Process Credentials for Hardware Security Module (HSM) with PKCS11](https://github.com/salrashid123/aws-pkcs-process-credential)
* [PKCS 11 Samples in Go using SoftHSM](https://github.com/salrashid123/go_pkcs11)

---

### Usage

You need to first embed an RSA key into a PKCS-11 device which is described below but is out of scope of this library

The following using [SoftHSM](https://github.com/softhsm/SoftHSMv2) `/usr/lib/softhsm/libsofthsm2.so`

##### **GCPCredentials**

If the GCP RSA key is embedded in `token1` a with label `keylabel1`

```python
from google.cloud import storage
from cloud_auth_pkcs.gcp.gcpcredentials import GCPCredentials

####  pip3 install cloud_auth_pkcs[gcp]
pc = GCPCredentials(
  module='/usr/lib/softhsm/libsofthsm2.so',
  token='token1',
  label='keylabel1',
  pin='123456',

  email="jwt-access-svc-account@$PROJECT_ID.iam.gserviceaccount.com")                    

storage_client = storage.Client(project="$PROJECT_ID", credentials=pc)

buckets = storage_client.list_buckets()
for bkt in buckets:
    print(bkt.name)
```   

##### **AWSCredentials**

If the AWS RolesAnywhere RSA key is embedded in `token1` a with label `keylabel2`

```python
import boto3
from cloud_auth_pkcs.aws.awscredentials import AWSCredentials

####  pip3 install cloud_auth_pkcs[aws]
pc = AWSCredentials(
  module='/usr/lib/softhsm/libsofthsm2.so',
  token='token1',
  label='keylabel2',
  pin='123456',

  public_certificate_file="certs/alice-cert.crt",
  region="us-east-2",
  duration_seconds=1000,
  trust_anchor_arn='arn:aws:rolesanywhere:us-east-2:291738886522:trust-anchor/a545a1fc-5d86-4032-8f4c-61cdd6ff92ac',
  session_name="foo", 
  role_arn="arn:aws:iam::291738886522:role/rolesanywhere1",
  profile_arn="arn:aws:rolesanywhere:us-east-2:291738886522:profile/6f4943fb-13d4-4242-89c4-be367595c560")

session = pc.get_session()

s3 = session.resource('s3')
for bucket in s3.buckets.all():
    print(bucket.name)
```

##### **AWSHMACCredentials**

If the AWS HMAC Key is embedded in `token1` a with label `keylabel3`

```python
import boto3
from cloud_auth_pkcs.aws.awshmaccredentials import AWSHMACCredentials

####  pip3 install cloud_auth_pkcs[aws]
pc = AWSHMACCredentials(
  module='/usr/lib/softhsm/libsofthsm2.so',
  token='token1',
  label='keylabel3',
  pin='123456',

  access_key="AWS_ACCESS_KEY_ID",
  region="us-east-2",
  duration_seconds=1000,
  role_session_name="foo",
  assume_role_arn="arn:aws:iam::291738886522:role/gcpsts")

session = pc.get_session()

s3 = session.resource('s3')
for bucket in s3.buckets.all():
    print(bucket.name)
```

##### **AzureCredentials**

If the AWS HMAC Key is embedded in `token1` a with label `keylabel4`


```python
from azure.storage.blob import BlobServiceClient
from cloud_auth_pkcs.azure.azurecredentials import AzureCredentials

####  pip3 install cloud_auth_pkcs[azure]
pc = AzureCredentials(
  module='/usr/lib/softhsm/libsofthsm2.so',
  token='token1',
  label='keylabel4',
  pin='123456',

  tenant_id="45243fbe-b73f-4f7d-8213-a104a99e428e",
  client_id="cffeaee2-5617-4784-8a4b-b647efd676e1",
  certificate_path="certs/azclient.crt")

blob_service_client = BlobServiceClient(
    account_url="https://$STORAGE_ACCOUNT.blob.core.windows.net",
    credential=pc
)
container_client = blob_service_client.get_container_client('container_name')
blob_list = container_client.list_blobs()
for blob in blob_list:
    print(blob.name)
```

---

### Configuration

| Option | Description |
|:------------|-------------|
| **`module`** | Path to PKCS Module:  (required; default: ``) |
| **`token`** | Name of the PKCS TOKEN:  (required; default: ``) |
| **`label`** | Label set for the key  (required; default: ``) |
| **`pin`** | PIN for the token:  (optional; default: ``) |

##### **GCPCredentials**

| Option | Description |
|:------------|-------------|
| **`email`** | ServiceAccount email (required; default: ``) |
| **`scopes`** | Signed Jwt Scopes (optional default: `"https://www.googleapis.com/auth/cloud-platform"`) |
| **`keyid`** | ServiceAccount keyid (optional; default: ``) |
| **`expire_in`** | Token expiration in seconds (optional; default: `3600`) |

##### **AWSCredentials**

| Option | Description |
|:------------|-------------|
| **`public_certificate_file`** | Path to public x509 (required; default: ``) |
| **`region`** | AWS Region (optional default: ``) |
| **`duration_seconds`** | Duration in seconds for the token lifetime (optional; default: `3600`) |
| **`trust_anchor_arn`** | RolesAnywhere Trust anchor ARN (required; default: ``) |
| **`role_arn`** | RolesAnywhere RoleArn (required; default: ``) |
| **`profile_arn`** | RolesAnywhere Profile Arn (Required; default: ``) |
| **`session_name`** | AWS Session Name (optional; default: ``) |

##### **AWSHMACCredentials**

| Option | Description |
|:------------|-------------|
| **`region`** | AWS Region (optional default: ``) |
| **`aws_access_key_id`** | AWS_ACCESS_KEY_ID if using HMAC based credentials (required; default: ``) |
| **`duration_seconds`** | Duration in seconds for the token lifetime (optional; default: `3600`) |
| **`get_session_token`** | If using GetSessionToken (optional; default: `False`) |
| **`assume_role_arn`** | AssumeRole ARN (required if AssumeRole set; default: ``) |
| **`role_session_name`** | RoleSessionName if AssumeRole set (optional; default: ``) |

##### **AzureCredentials**

| Option | Description |
|:------------|-------------|
| **`tenant_id`** | Azure TentantID (required; default: ``) |
| **`client_id`** | Azure Application (client) ID (required; default: ``) |
| **`certificate_path`** | x509 certificate to authenticate with (required; default ``) |

---

### Setup

This demo uses [SoftHSM](https://github.com/softhsm/SoftHSMv2) but you are free to use any other PKCS-11 compliant system

```bash
apt-get -y install libsofthsm2-dev opensc

# go to the example/ folder and set the path to the softhsm config:
cd example/
rm -rf /tmp/tokens
mkdir /tmp/tokens

export SOFTHSM2_CONF=`pwd`/softhsm.conf
export MODULE="/usr/lib/softhsm/libsofthsm2.so"

## initialize
pkcs11-tool --module $MODULE --list-mechanisms --slot-index 0
pkcs11-tool --module $MODULE  --slot-index=0 \
   --init-token --label="token1" --so-pin="123456"

pkcs11-tool --module $MODULE  --label="token1" \
   --init-pin --so-pin "123456" --pin mynewpin

## print mechanisms
pkcs11-tool --module $MODULE --list-mechanisms --slot-index 0

## print slot details
pkcs11-tool --module $MODULE --list-token-slots
```

#### Using RSA Keys on PKCS

First step is to acquire the private RSA keys for whichever provider you're interested in

- `GCP`

  Uses [Service Account Self-signed JWT](https://google.aip.dev/auth/4111 ) with Scopes.
  
  Extract the service account json's private key and embed into PKCS-11.

- `AWS`

  Uses [IAM Roles Anywhere](https://docs.aws.amazon.com/rolesanywhere/latest/userguide/introduction.html) which involves using a local RSA key to authenticate

  This repo also supports `AWS HMAC Credentials` which you can embed into PKCS-11.

- `Azure`

   Uses [Azure Certificate Credentials](https://learn.microsoft.com/en-us/entra/identity-platform/certificate-credentials)


Once you have the raw RSA private key in in regular PEM format, you can use [pkcs11-tool](https://man.archlinux.org/man/pkcs11-tool.1.en) to load the key.

Each provider has its own way to create the raw RSA key and associate it with a cloud credential.  See instructions below for each provider.

#### Setup - GCP

This is an extension of GCP [google-auth-python](https://github.com/googleapis/google-auth-library-python) specifically intended to use service account credentials which are embedded inside a PCKS-11 device.

Setup a new key and download the json

```bash
export PROJECT_ID=`gcloud config get-value core/project`
export GCP_SA_EMAIL=jwt-access-svc-account@$PROJECT_ID.iam.gserviceaccount.com

gcloud iam service-accounts create jwt-access-svc-account --display-name "Test Service Account"
gcloud iam service-accounts keys create jwt-access-svc-account.json --iam-account=$GCP_SA_EMAIL

gcloud projects add-iam-policy-binding $PROJECT_ID --member=serviceAccount:$GCP_SA_EMAIL --role=roles/storage.admin

## create a test bucket
export GCP_BUCKET=gs://$PROJECT_ID-test
gcloud storage buckets create gs://$GCP_BUCKET --project=$PROJECT_ID
```

Extract the `key_id`, `email` and the raw RSA key.

```bash
cat jwt-access-svc-account.json | jq -r '.private_key' > /tmp/rsakey.pem

## convert the rsa key to DER for importing
openssl rsa -text -in /tmp/rsakey.pem
openssl rsa -in /tmp/rsakey.pem -outform DER -out /tmp/gcp_key.der
```

Import `/tmp/gcp_key.der` into the device.  Once the key is embedded into the device, you can discard the raw key 

```bash
export MODULE="/usr/lib/softhsm/libsofthsm2.so"

pkcs11-tool  --module $MODULE --pin mynewpin \
   --write-object /tmp/gcp_key.der --type privkey --id 10 --label keylabel3 --slot-index 0

pkcs11-tool --module $MODULE --list-token-slots
pkcs11-tool --module $MODULE  --list-objects --pin mynewpin
```

Now test the 
```bash
cd example/
pip3 install -r requirements-gcp.txt

python3 main_gcp.py --module="$MODULE" \
   --token="token1" --label="keylabel3" --pin="mynewpin" \
   --email="$GCP_SA_EMAIL" \
   --project_id="$GCP_PROJECT" --bucket="$GCP_BUCKET"

```

How it works:

GCP APIs allows for service account authentication using a [Self-signed JWT with scope](https://google.aip.dev/auth/4111).

What that means is if you take a private key and generate a valid JWT with in the following format, you can just send it to the service as an auth token, that simple.

```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "abcdef1234567890"
}
{
  "iss": "jwt-access-svc-account@$PROJECT_ID.iam.gserviceaccount.com",
  "sub": "jwt-access-svc-account@$PROJECT_ID.iam.gserviceaccount.com",
  "scope": "https://www.googleapis.com/auth/cloud-platform",
  "iat": 1511900000,
  "exp": 1511903600
}
```

So since we have the RSA key on the TPM, we can use the ESAPI to make it "sign" data for the JWT.

#### Setup - AWS

[AWS Roles Anywhere](https://docs.aws.amazon.com/rolesanywhere/latest/userguide/introduction.html) allows for client authentication based on digital signature from trusted private keys.

The trusted client RSA or EC key is embedded within a PKCS-11 device and that is used to sign the RolesAnywhere header values.

For a detailed example, see [AWS SDK CredentialProvider for RolesAnywhere](https://github.com/salrashid123/aws_rolesanywhere_signer?tab=readme-ov-file#setup)

The following example assumes you have setup RolesAnwwhere and the client certificate and key are available at `awsclient.key` and `awsclient.crt`

When you setup RolesAnywhere, note down the ARN for the `TrustAnchorArn`, `ProfileArn` and `RoleArn` as well as the `region`.  Ideally, the role has `AmazonS3ReadOnlyAccess` to list buckets.

Then attempt to use the credentials and specify the specific ARN values

```bash
export AWS_PEM="/path/to/awsclient.key"
export AWS_CERT="/path/to/awsclient.crt"
export AWS_REGION="us-east-2"
export AWS_TRUST_ANCHOR_ARN="arn:aws:rolesanywhere:us-east-2:redacted:trust-anchor/redacted"
export AWS_ROLE_ARN="arn:aws:iam::redacted:role/cicd-role"
export AWS_PROFILE_ARN="arn:aws:rolesanywhere:us-east-2:redacted:profileredacted"
export AWS_HMAC_REGION="us-east-1"

### convert to der and importy the key
openssl rsa -in $AWS_PEM -outform DER -out /tmp/aws_key.der

pkcs11-tool  --module $MODULE --pin mynewpin \
   --write-object /tmp/aws_key.der --type privkey --id 10 --label keylabel5 --slot-index 0

pip3 install -r requirements-aws.txt

python3 main_aws.py --module="$MODULE" \
   --token="token1" --label="keylabel5" --pin="mynewpin" \
   --public_certificate_file="$AWS_CERT" \
   --region="$AWS_REGION" --trust_anchor_arn="$AWS_TRUST_ANCHOR_ARN" \
   --role_arn="$AWS_ROLE_ARN" \
   --profile_arn="$AWS_PROFILE_ARN"
```

##### AWS HMAC

AWS supports HMAC based authentication as well. see the following for a TPM equivalent: [AWS Credentials for Hardware Security Modules and TPM based AWS_SECRET_ACCESS_KEY](https://github.com/salrashid123/aws_hmac) and specifically [AWS v4 signed request using Trusted Platform Module](https://gist.github.com/salrashid123/bca7a24e1d59567adb89fef093d8564d)

This repo includes an example setup and to use this, you need your `AWS_ACCESS_KEY_ID` `AWS_SECRET_ACCESS_KEY` and embed the secret into the PKCS device and make it perform the HMAC

```bash
### first embed the hmac key with an optional password
export AWS_ACCESS_KEY_ID=recacted
export AWS_SECRET_ACCESS_KEY=redacted

## add the AWS4 prefix to the key per the signing protocol
export secret="AWS4$AWS_SECRET_ACCESS_KEY"
echo -n $secret > hmac.key

pkcs11-tool  --module $MODULE --pin mynewpin \
   --write-object /tmp/hmac.key --type secrkey --private --sensitive \
    --usage-sign --private --id 10 --label keylabel4 --slot-index 0 \
      --mechanism SHA256-HMAC 

pip3 install -r requirements-aws.txt

python3 main_aws_hmac.py --module="$MODULE" \
   --token="token1" --label="keylabel4" --pin="mynewpin" \
   --aws_access_key_id=$AWS_ACCESS_KEY \
   --region="$AWS_HMAC_REGION" \
   --assume_role_arn="$AWS_ROLE_ARN"
```

#### Setup - Azure

Azure authentication uses an the basic [Microsoft identity platform application authentication certificate credentials](https://learn.microsoft.com/en-us/entra/identity-platform/certificate-credentials) where the variation here is that the client rsa key is on PKCS

The following example assumes you have set this up similar to

* [KMS, TPM and HSM based Azure Certificate Credentials](https://github.com/salrashid123/azsigner)

The following assumes you have configured Azure certificate based autentication and the certificate and key are available locally
```bash
export AZURE_CLIENT_ID=cffeaee2-5617-4784-8a4b-redacted
export AZURE_TENANT_ID=45243fbe-b73f-4f7d-8213-redacted
export AZURE_STORAGEACCOUNT=redacted
export AZURE_CONTAINER=redacted
export AZURE_CLIENT_PEM="/path/to/azureclient.key"
export AZURE_CERT="/path/to/azureclient.crt"

## test that you have the cert based auth working
az login --service-principal -u $CLIENT_ID -p $CERTIFICATE_PATH_COMBINED_DER --tenant=$TENANT_ID
az account get-access-token   --scope="api://$CLIENT_ID/.default"

## if the principal has access to a storage container, test that
export STORAGE_ACCOUNT=your-storage-account
export CONTAINER=your-container
export AZURE_TOKEN=$(az account get-access-token --resource https://storage.azure.com/ --query accessToken -o tsv)

curl -s --oauth2-bearer "$AZURE_TOKEN"  -H 'x-ms-version: 2017-11-09'  \
     "https://$STORAGE_ACCOUNT.blob.core.windows.net/$CONTAINER?restype=container&comp=list" | xmllint -  --format

## now you're ready to embed the key and test with the client using the embedded  key

openssl rsa -in $AZURE_CLIENT_PEM -outform DER -out /tmp/azure_key.der
pkcs11-tool  --module $MODULE --pin mynewpin \
   --write-object /tmp/azure_key.der --type privkey --id 10 --label keylabel6 --slot-index 0

pip3 install -r requirements-azure.txt

python3 main_azure.py --module="$MODULE" \
   --token="token1" --label="keylabel6" --pin="mynewpin" \
   --certificate_path="$AZURE_CERT" \
   --tenant_id="$AZURE_TENANT_ID" \
   --client_id="$AZURE_CLIENT_ID" \
   --storageaccount="$AZURE_STORAGEACCOUNT"  --container="$AZURE_CONTAINER"
```


#### Local Build

to generate the library from scratch and run local, run 

```bash
python3 setup.py sdist bdist_wheel

cd example
virtualenv env
source env/bin/activate

pip3 install ../
## depending on the variant provider
# pip3 install -r requirements-gcp.txt 
# pip3 install -r requirements-aws.txt 
# pip3 install -r requirements-azure.txt 


### to deploy/upload
# virtualenv env 
# source env/bin/activate
# python3 -m pip install --upgrade build
# python3 -m pip install --upgrade twine
# python3 -m build
# python3 -m twine upload --repository testpypi dist/*
# python3 -m twine upload  dist/*
```

