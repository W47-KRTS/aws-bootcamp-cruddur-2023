aws rds create-db-instance \
  --db-instance-identifier cruddur-db-instance \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version  14.6 \
  --master-username cruddurroot \
  --master-user-password Wolverine47! \
  --allocated-storage 20 \
  --availability-zone eu-north-1a \
  --backup-retention-period 0 \
  --port 5432 \
  --no-multi-az \
  --db-name cruddur \
  --storage-type gp2 \
  --publicly-accessible \
  --storage-encrypted \
  --enable-performance-insights \
  --performance-insights-retention-period 7 \
  --no-deletion-protection


sgr-01e00597d00552797q

export DB_SG_ID="sg-0276a5f5055c0d686"
gp env DB_SG_ID="sg-0276a5f5055c0d686"

export DB_SG_RULE_ID="sgr-01e00597d00552797"
gp env DB_SG_RULE_ID="sgr-01e00597d00552797"

aws ec2 modify-security-group-rules \
    --group-id $DB_SG_ID \
    --security-group-rules "SecurityGroupRuleId=$DB_SG_RULE_ID,SecurityGroupRule={IpProtocol=tcp,FromPort=5432,ToPort=5432,CidrIpv4=$GITPOD_IP/32}"

