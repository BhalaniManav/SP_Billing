from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import base64
import io
import qrcode


def _extract_ref_sections():
    # Read ref.html and extract <style>, main body, and <script>
    try:
        from bs4 import BeautifulSoup  # type: ignore
    except Exception:  # pragma: no cover
        return '', '<div style="padding:20px;color:red">BeautifulSoup not available</div>', ''

    ref_path = settings.BASE_DIR / 'ref.html'
    with open(ref_path, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')

    style_tag = soup.find('style')
    css = style_tag.get_text() if style_tag else ''

    # Remove head script/style and return body innerHTML
    body = soup.find('body')
    # Remove external script tags since we'll replace with our own script via DRF
    for s in body.find_all('script'):
        s.extract()
    body_html = str(body)

    # Collect inline JS between <script> tags at bottom
    scripts = soup.find_all('script')
    js_inline = []
    for s in scripts:
        if s.get('src'):
            continue
        js_inline.append(s.get_text())
    js = '\n'.join(js_inline)

    return css, body_html, js


from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def index(request):
    css, body, js = _extract_ref_sections()
    # The JS in ref.html uses IndexedDB and hardcoded login; we will override parts via separate static JS later
    return render(request, 'core/index.html', {
        'css': css,
        'body': body,
        'js': js,
    })


def qr_base64(request):
    # GET /qr/?data=http://ip:port
    data = request.GET.get('data')
    if not data:
        return HttpResponseBadRequest('missing data')
    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode('ascii')
    return JsonResponse({'image_base64': f'data:image/png;base64,{b64}'})

@ensure_csrf_cookie
@require_POST
def login_view(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({'detail': 'Invalid credentials'}, status=400)
    login(request, user)
    return JsonResponse({'username': user.username})


@login_required
@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({'ok': True})


@login_required
def me(request):
    return JsonResponse({'username': request.user.username})

    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode('ascii')
    return JsonResponse({'image_base64': f'data:image/png;base64,{b64}'})
