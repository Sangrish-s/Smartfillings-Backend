from django.http import JsonResponse, HttpResponse
from core import search_company, get_filings, get_html, ai_analysis_from_filing
import json
import re
from urllib.parse import urlparse, urljoin


app_name = "filings"


def search(request, search_text):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        response = search_company(search_text)
        return JsonResponse(response, safe=False)
    except (ValueError, KeyError):
        return JsonResponse({"error": "Invalid request data"}, status=400)


def query(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        return _extracted_from_query(request)
    except (ValueError, KeyError):
        return JsonResponse({"error": "Invalid request data"}, status=400)


def _extracted_from_query(request):
    data = json.load(request)
    ticker = data.get("ticker")
    form_type = data.get("form_type")
    size = data.get("size")
    page = data.get("page")
    response = get_filings(ticker, form_type, size, page)
    return JsonResponse(response, safe=False)


def filing(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    url = request.GET["url"]

    try:
        html = get_html(url)
        return HttpResponse(
            replace_relative_img_paths(html, url), content_type="text/html"
        )
    except (ValueError, KeyError):
        return JsonResponse({"error": "Invalid request data"}, status=400)


def replace_relative_img_paths(html, url):
    base_url = get_base_url(url)
    img_regex = r'<img[^>]+src="([^"]+)"'

    def replace_path(match):
        image_path = match.group(1)
        if not image_path.startswith("http"):
            absolute_path = urljoin(base_url, image_path)
            return match.group().replace(image_path, absolute_path)
        return match.group()

    return re.sub(img_regex, replace_path, html)


def get_base_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path[:parsed_url.path.rfind('/') + 1]}"


def prompt(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data = json.load(request)
    url = data.get("url")
    prompt_type = data.get("prompt_type")
    form_type = data.get("form_type")
    option = data.get("option")
    min_sentences = data.get("sentences", {}).get("min", 0)
    max_sentences = data.get("sentences", {}).get("max", 0)

    try:
        html = get_html(url)
        response = ai_analysis_from_filing(
            html, prompt_type, form_type, option, min_sentences, max_sentences
        )
        return JsonResponse(response, safe=False)
    except (ValueError, KeyError):
        return JsonResponse({"error": "Invalid request data"}, status=400)
