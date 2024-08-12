from sec_api import QueryApi, MappingApi, RenderApi
from dotenv import load_dotenv
import os
import json


load_dotenv(".env")
SEC_API_KEY = os.environ.get("SEC_API_KEY")


def get_filings(ticker, form_type, size=10, page=1):
    _from = (page - 1) * size

    queryApi = QueryApi(SEC_API_KEY)
    query_parts = []

    if ticker:
        query_parts.append(f"ticker:{ticker}")

    if form_type:
        if isinstance(form_type, str):
            query_parts.append(f'formType:"{form_type}"')
        elif isinstance(form_type, list):
            form_type_query = " AND ".join([f'formType:"{ft}"' for ft in form_type])
            query_parts.append(form_type_query)

    query = " AND ".join(query_parts)

    print(query)
    try:
        response = queryApi.get_filings(
            {
                "query": query,
                "from": str(_from),
                "size": str(size),
                "sort": [{"filedAt": {"order": "desc"}}],
            }
        )
        data = response["filings"]
        total = response["total"]
        return {"data": data, "total": total, "page": page, "size": size}
    except Exception:
        print(f"There was an error getting filings for the ticker {ticker}")
        return []


def search_company(search_text):
    mappingApi = MappingApi(SEC_API_KEY)
    try:
        return mappingApi.resolve("name", search_text)
    except Exception:
        print(f"There was an error getting company map for the text {search_text}")
        return []


def get_html(url):
    renderApi = RenderApi(SEC_API_KEY)
    return renderApi.get_filing(url)
