import boto3

client_s3 = boto3.client('s3')
resource_s3 = boto3.resource('s3')
destBucket = input("Enter the name of destination bucket: ")
sourceAccountNo = input("Enter the source account number: ")
sourceIAMUser = input("Enter the IAM user of source account: ")

# creating bucket
response_create = client_s3.create_bucket(
    ACL='private',
    Bucket=destBucket,
    ObjectOwnership='BucketOwnerPreferred'
)

# blocking public access to the bucket
response_block = client_s3.put_public_access_block(
    Bucket=destBucket,
    PublicAccessBlockConfiguration={
        'BlockPublicAcls': True,
        'IgnorePublicAcls': True,
        'BlockPublicPolicy': True,
        'RestrictPublicBuckets': True
    }
)

# enable versioning
versioning = resource_s3.BucketVersioning(destBucket)
versioning.enable()

# attaching policy to the bucket
response_policy = client_s3.put_bucket_policy(
    Bucket=destBucket,
    Policy='{"Version": "2012-10-17", "Id": "Policy123", "Statement": [{ "Sid": "Stmt123", "Effect": "Allow", '
           '"Principal": {"AWS": "arn:aws:iam::' + sourceAccountNo + ':user/' + sourceIAMUser + '"}, "Action": "s3:PutObject", "Resource": "arn:aws:s3:::' + destBucket + '/*", "Condition":{ '
                                                                                                                                                                          '"StringEquals":{ "s3:x-amz-acl": "bucket-owner-full-control" } } }, { "Sid": "Stmt456", "Effect": '
                                                                                                                                                                          '"Allow", "Principal": { "AWS": "arn:aws:iam::' + sourceAccountNo + ':user/' + sourceIAMUser + '" }, "Action": "s3:ListBucket", "Resource": "arn:aws:s3:::' + destBucket + '" }]} '
)
print(response_create)
