import { Amplify } from 'aws-amplify';

const awsConfig = {
  Auth: {
    Cognito: {
      userPoolId: 'us-east-1_y6JcIIcp4',
      userPoolClientId: '7rr2hq5eatmd661q836rdqaraa',
      region: 'us-east-1',
      signUpVerificationMethod: 'code' as const,
      loginWith: {
        email: true,
        username: false,
        phone: false
      }
    }
  }
};

Amplify.configure(awsConfig);

export default awsConfig;
