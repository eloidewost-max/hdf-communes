import { verifyToken, createClerkClient } from '@clerk/backend';

var ALLOWED_DOMAIN = 'vizzia.fr';

var PUBLIC_PATHS = ['/sign-in', '/sign-in.html'];

export var config = {
  matcher: ['/((?!_vercel|favicon\\.ico).*)'],
};

export default async function middleware(request) {
  var url = new URL(request.url);

  // Allow sign-in page through
  if (PUBLIC_PATHS.some(function(p) { return url.pathname === p; })) {
    return;
  }

  // Extract session token from Clerk cookie
  var cookieHeader = request.headers.get('cookie') || '';
  var match = cookieHeader.match(/__session=([^;]+)/);
  var token = match ? match[1] : null;

  if (!token) {
    return Response.redirect(new URL('/sign-in', request.url));
  }

  try {
    // Verify JWT signature against Clerk's JWKS
    var payload = await verifyToken(token, {
      secretKey: process.env.CLERK_SECRET_KEY,
    });

    // Check email from custom session claims (fast path, no API call)
    if (payload.email) {
      if (!payload.email.endsWith('@' + ALLOWED_DOMAIN)) {
        return accessDenied();
      }
      return; // authorized
    }

    // Fallback: fetch user from Clerk API to get email
    var clerk = createClerkClient({ secretKey: process.env.CLERK_SECRET_KEY });
    var user = await clerk.users.getUser(payload.sub);
    var primaryEmail = user.emailAddresses.find(function(e) {
      return e.id === user.primaryEmailAddressId;
    });
    var email = primaryEmail ? primaryEmail.emailAddress : '';

    if (!email.endsWith('@' + ALLOWED_DOMAIN)) {
      return accessDenied();
    }

    return; // authorized
  } catch (err) {
    // Invalid or expired token
    return Response.redirect(new URL('/sign-in', request.url));
  }
}

function accessDenied() {
  return new Response(
    '<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><title>Accès refusé</title>' +
    '<style>body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;' +
    'background:#0a0b10;color:#e2e4e9;display:flex;justify-content:center;align-items:center;' +
    'height:100vh;margin:0}div{text-align:center}h1{font-size:24px;margin-bottom:12px}' +
    'p{color:#8b8f98;margin-bottom:24px}a{color:#4ecdc4;text-decoration:none}a:hover{text-decoration:underline}</style>' +
    '</head><body><div><h1>Accès refusé</h1>' +
    '<p>Seules les adresses <strong>@vizzia.fr</strong> sont autorisées.</p>' +
    '<a href="/sign-in">Se reconnecter avec une autre adresse</a></div></body></html>',
    { status: 403, headers: { 'Content-Type': 'text/html; charset=utf-8' } }
  );
}
