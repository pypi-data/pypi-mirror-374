import requests

def search_weaviate(tapestry_id, query, alpha, distance, limit):
    url =  "https://inthepicture.org/admin/search_weaviate"

    params = {
        "tapestry_id": tapestry_id,
        "query": query,
        "alpha": alpha,
        "distance": distance,
        "limit": limit,
    }
    
    response = requests.get(url, params=params)
    try:
        resp_json = response.json()
    except Exception:
        resp_json = {}

    if response.status_code == 200 and resp_json.get("success", False):
        return resp_json
    else:
        message = resp_json.get("message", response.text)
        return {
            "success": False,
            "code": response.status_code,
            "message": message,
            "body": {}
        }

