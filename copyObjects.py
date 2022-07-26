import boto3

client_s3 = boto3.client('s3')
resource_iam = boto3.resource('iam')
destBucket = input("Enter the name of destination bucket: ")
sourceAccountNo = input("Enter the source account number: ")
sourceIAMUser = input("Enter the IAM user of source account: ")

sourceBucketList = []
bkts = input("Enter the name of source buckets separated by space: ")
bList = bkts.split()
for obj in bList:
    sourceBucketList.append(obj)

for b in sourceBucketList:
    # create policy
    client_iam = boto3.client('iam')
    client_policy = client_iam.create_policy(
        PolicyName='automation-policy-for-srcUser',
        PolicyDocument='{"Version": "2012-10-17","Statement": [{"Effect": "Allow","Action": ["s3:ListBucket",'
                       '"s3:GetObject"],"Resource": ["arn:aws:s3:::'+b+'","arn:aws:s3:::'+b+'/*"]},{"Effect": '
                                                                                            '"Allow","Action": ['
                                                                                            '"s3:ListBucket",'
                                                                                            '"s3:PutObject",'
                                                                                            '"s3:PutObjectAcl"],'
                                                                                            '"Resource": ['
                                                                                            '"arn:aws:s3:::'+destBucket+'","arn:aws:s3:::'+destBucket+'/*"]}]} '
    )

    # attach policy to user
    policyARN = client_policy['Policy']['Arn']
    user = resource_iam.User(sourceIAMUser)
    response2 = user.attach_policy(
        PolicyArn=policyARN
    )
    # list objects
    response_listObj = client_s3.list_objects(
        Bucket=b
    )
    objectList = []
    for i in range(len(response_listObj['Contents'])):
        ele = response_listObj['Contents'][i]['Key']
        objectList.append(ele)

    # copy objects
    for x in objectList:
        response_copyObject = client_s3.copy_object(
            ACL='bucket-owner-full-control',
            Bucket=destBucket,
            CopySource={'Bucket': b, 'Key': x},
            Key=x
        )
    print("Objects of", b, "copied")

    # delete user policy once objects are copied
    response_detach = client_iam.detach_user_policy(
        UserName=sourceIAMUser,
        PolicyArn='arn:aws:iam::'+sourceAccountNo+':policy/automation-policy-for-srcUser'
    )
    response_delete = client_iam.delete_policy(
        PolicyArn='arn:aws:iam::'+sourceAccountNo+':policy/automation-policy-for-srcUser'
    )