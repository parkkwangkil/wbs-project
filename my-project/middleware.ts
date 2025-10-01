import { NextResponse } from 'next/server';

const backendBase = process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000';

export function middleware(req: Request) {
  const url = new URL(req.url);

  // Allow Next internal assets and common static files to pass through
  if (
    url.pathname.startsWith('/_next') ||
    url.pathname.startsWith('/favicon') ||
    url.pathname === '/robots.txt' ||
    url.pathname === '/google33eba2ec6f8eb1b8.html'
  ) {
    return NextResponse.next();
  }

  // Django Admin 및 로그인 처리
  if (url.pathname.startsWith('/static/admin/') || 
      url.pathname.startsWith('/admin/') || 
      url.pathname.startsWith('/accounts/')) {
    const dest = `${backendBase}${url.pathname}${url.search}`;
    const response = NextResponse.rewrite(dest);
    
    // 로그인 관련 헤더 설정
    response.headers.set('X-Frame-Options', 'SAMEORIGIN');
    response.headers.set('X-Content-Type-Options', 'nosniff');
    response.headers.set('X-Forwarded-Proto', 'https');
    response.headers.set('X-Forwarded-Host', url.host);
    
    return response;
  }

  const dest = `${backendBase}${url.pathname}${url.search}`;
  return NextResponse.rewrite(dest);
}

export const config = {
  matcher: ['/((?!_next|favicon\\.ico|robots\\.txt|google33eba2ec6f8eb1b8\\.html).*)'],
};


