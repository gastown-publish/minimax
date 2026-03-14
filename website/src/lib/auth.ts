import {
  CognitoIdentityProviderClient,
  InitiateAuthCommand,
  SignUpCommand,
  ConfirmSignUpCommand,
  GetUserCommand,
  GlobalSignOutCommand,
} from "@aws-sdk/client-cognito-identity-provider";

const REGION = "us-east-1";
const CLIENT_ID = process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID || "";

const client = new CognitoIdentityProviderClient({ region: REGION });

export interface AuthUser {
  email: string;
  sub: string;
  accessToken: string;
  idToken: string;
  refreshToken: string;
}

const STORAGE_KEY = "minimax_auth";

function saveTokens(user: AuthUser): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
  // Set cross-subdomain cookie so app.minimax.villamarket.ai can read auth
  const encoded = encodeURIComponent(JSON.stringify({ email: user.email, sub: user.sub, accessToken: user.accessToken, idToken: user.idToken }));
  document.cookie = `minimax_auth=${encoded}; domain=.villamarket.ai; path=/; max-age=86400; secure; samesite=lax`;
}

export function getStoredUser(): AuthUser | null {
  if (typeof window === "undefined") return null;
  const stored = localStorage.getItem(STORAGE_KEY);
  if (!stored) return null;
  try {
    const user = JSON.parse(stored) as AuthUser;
    // Ensure cross-subdomain cookie exists (handles sessions created before cookie code was added)
    if (user && !document.cookie.includes("minimax_auth=")) {
      const encoded = encodeURIComponent(JSON.stringify({ email: user.email, sub: user.sub, accessToken: user.accessToken, idToken: user.idToken }));
      document.cookie = `minimax_auth=${encoded}; domain=.villamarket.ai; path=/; max-age=86400; secure; samesite=lax`;
    }
    return user;
  } catch {
    return null;
  }
}

export function clearAuth(): void {
  localStorage.removeItem(STORAGE_KEY);
  document.cookie = "minimax_auth=; domain=.villamarket.ai; path=/; max-age=0; secure; samesite=lax";
}

export function getAccessToken(): string | null {
  return getStoredUser()?.accessToken ?? null;
}

export function getIdToken(): string | null {
  return getStoredUser()?.idToken ?? null;
}

export async function signUp(email: string, password: string): Promise<void> {
  await client.send(
    new SignUpCommand({
      ClientId: CLIENT_ID,
      Username: email,
      Password: password,
      UserAttributes: [{ Name: "email", Value: email }],
    })
  );
}

export async function confirmSignUp(email: string, code: string): Promise<void> {
  await client.send(
    new ConfirmSignUpCommand({
      ClientId: CLIENT_ID,
      Username: email,
      ConfirmationCode: code,
    })
  );
}

export async function signIn(email: string, password: string): Promise<AuthUser> {
  const resp = await client.send(
    new InitiateAuthCommand({
      ClientId: CLIENT_ID,
      AuthFlow: "USER_PASSWORD_AUTH",
      AuthParameters: {
        USERNAME: email,
        PASSWORD: password,
      },
    })
  );

  if (resp.ChallengeName) {
    throw new Error(`Auth challenge: ${resp.ChallengeName}`);
  }

  const result = resp.AuthenticationResult!;
  const userResp = await client.send(
    new GetUserCommand({ AccessToken: result.AccessToken! })
  );

  const sub = userResp.UserAttributes?.find((a) => a.Name === "sub")?.Value || "";
  const userEmail = userResp.UserAttributes?.find((a) => a.Name === "email")?.Value || email;

  const user: AuthUser = {
    email: userEmail,
    sub,
    accessToken: result.AccessToken!,
    idToken: result.IdToken!,
    refreshToken: result.RefreshToken!,
  };

  saveTokens(user);
  return user;
}

export async function refreshSession(): Promise<AuthUser | null> {
  const stored = getStoredUser();
  if (!stored?.refreshToken) return null;

  try {
    const resp = await client.send(
      new InitiateAuthCommand({
        ClientId: CLIENT_ID,
        AuthFlow: "REFRESH_TOKEN_AUTH",
        AuthParameters: {
          REFRESH_TOKEN: stored.refreshToken,
        },
      })
    );

    const result = resp.AuthenticationResult!;
    const user: AuthUser = {
      ...stored,
      accessToken: result.AccessToken!,
      idToken: result.IdToken || stored.idToken,
    };

    saveTokens(user);
    return user;
  } catch {
    clearAuth();
    return null;
  }
}

export async function signOut(): Promise<void> {
  const stored = getStoredUser();
  if (stored?.accessToken) {
    try {
      await client.send(
        new GlobalSignOutCommand({ AccessToken: stored.accessToken })
      );
    } catch {
      // Ignore errors during sign out
    }
  }
  clearAuth();
}

// Google OAuth — redirect flow
export function signInWithGoogle(): void {
  const domain = process.env.NEXT_PUBLIC_COGNITO_DOMAIN || "";
  const redirectUri = `${window.location.origin}/login`;
  const url = `https://${domain}/oauth2/authorize?response_type=code&client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(redirectUri)}&identity_provider=Google&scope=openid+email+profile`;
  window.location.href = url;
}

// Apple OAuth — redirect flow
export function signInWithApple(): void {
  const domain = process.env.NEXT_PUBLIC_COGNITO_DOMAIN || "";
  const redirectUri = `${window.location.origin}/login`;
  const url = `https://${domain}/oauth2/authorize?response_type=code&client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(redirectUri)}&identity_provider=SignInWithApple&scope=openid+email+profile`;
  window.location.href = url;
}

// Decode JWT payload without verification (tokens come from Cognito over HTTPS)
function decodeJwtPayload(token: string): Record<string, unknown> {
  const base64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
  return JSON.parse(atob(base64));
}

// Exchange OAuth code for tokens
export async function exchangeCode(code: string): Promise<AuthUser> {
  const domain = process.env.NEXT_PUBLIC_COGNITO_DOMAIN || "";
  const redirectUri = `${window.location.origin}/login`;

  const resp = await fetch(`https://${domain}/oauth2/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "authorization_code",
      code,
      client_id: CLIENT_ID,
      redirect_uri: redirectUri,
    }),
  });

  const data = await resp.json();
  if (!resp.ok) throw new Error(data.error || "Token exchange failed");

  // Parse ID token for user claims (OAuth access tokens lack aws.cognito.signin.user.admin scope)
  const claims = decodeJwtPayload(data.id_token);

  const user: AuthUser = {
    email: (claims.email as string) || "",
    sub: (claims.sub as string) || "",
    accessToken: data.access_token,
    idToken: data.id_token,
    refreshToken: data.refresh_token,
  };

  saveTokens(user);
  return user;
}
