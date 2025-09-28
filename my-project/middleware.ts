import { NextResponse } from 'next/server';

const backendBase = process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000';

export function middleware(req: Request) {
  const url = new URL(req.url);

  // Allow Next internal assets and common static files to pass through
  if (
    url.pathname.startsWith('/_next') ||
    url.pathname.startsWith('/favicon') ||
    url.pathname === '/robots.txt'
  ) {
    return NextResponse.next();
  }

  const dest = `${backendBase}${url.pathname}${url.search}`;
  return NextResponse.rewrite(dest);
}

export const config = {
  matcher: ['/((?!_next|favicon\\.ico|robots\\.txt).*)'],
};


