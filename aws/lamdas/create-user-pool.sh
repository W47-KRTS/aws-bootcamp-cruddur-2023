# Create the user pool

# create user-pool
aws cognito-idp create-user-pool --pool-name "TestPool"

# create app-client
aws cognito-idp create-user-pool-client --user-pool-id eu-north-1_tpn4XlV1R --client-name "TestClient" --no-generate-secret

# list your app clients anytime using:
aws cognito-idp list-user-pool-clients --user-pool-id eu-north-1_tpn4XlV1R