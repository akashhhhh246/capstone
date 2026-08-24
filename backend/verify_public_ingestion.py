import urllib.request
import json

def test_endpoint(url, method="GET", payload=None):
    data = json.dumps(payload).encode("utf-8") if payload else None
    headers = {"Content-Type": "application/json"} if payload else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")
    except Exception as e:
        return 0, str(e)

print("==================================================", flush=True)
print("Verifying Real-Time Public Data Ingestion Layer...", flush=True)
print("==================================================", flush=True)

# 1. Data Source Status
status, data = test_endpoint("http://localhost:9207/api/v1/data-sources/status")
print(f"1. GET /api/v1/data-sources/status -> Status: {status}", flush=True)
print(f"   Response: {json.dumps(data, indent=2)}", flush=True)

# 2. Trigger GDELT Sync
status, data = test_endpoint("http://localhost:9207/api/v1/data-sources/gdelt/sync", method="POST", payload={"limit": 5})
print(f"\n2. POST /api/v1/data-sources/gdelt/sync -> Status: {status}", flush=True)
if isinstance(data, dict):
    print(f"   Ingested: {data.get('ingested')}, Skipped Duplicates: {data.get('skipped_duplicates')}", flush=True)
    if data.get("records"):
        print(f"   Sample Title: {data['records'][0].get('title')}", flush=True)
        print(f"   Classification: {data['records'][0].get('classification')}, Confidence: {data['records'][0].get('confidence')}", flush=True)
else:
    print(f"   Response: {data}", flush=True)

# 3. Trigger RSS Sync
status_rss, data_rss = test_endpoint("http://localhost:9207/api/v1/data-sources/rss/sync", method="POST", payload={"limit": 5})
print(f"\n3. POST /api/v1/data-sources/rss/sync -> Status: {status_rss}", flush=True)
if isinstance(data_rss, dict):
    print(f"   RSS Ingested: {data_rss.get('ingested')}", flush=True)

# 4. List Live Content Feed
status, data = test_endpoint("http://localhost:9207/api/v1/live-content?limit=5")
print(f"\n4. GET /api/v1/live-content -> Status: {status}", flush=True)
if isinstance(data, dict):
    print(f"   Total Live Feed Items: {data.get('total')}", flush=True)
    if data.get("items"):
        first_item = data["items"][0]
        print(f"   First Item ID: {first_item['id']}", flush=True)
        print(f"   First Item Title: {first_item['title']}", flush=True)
        print(f"   Data Origin: {first_item['data_origin']}", flush=True)
        print(f"   Detection: {first_item['classification']} (AI Prob: {first_item['ai_probability']})", flush=True)

        # 5. Seed Synthetic Simulation from this Real Article
        status_sim, data_sim = test_endpoint(f"http://localhost:9207/api/v1/live-content/{first_item['id']}/simulate-cascade", method="POST", payload={})
        print(f"\n5. POST /api/v1/live-content/{first_item['id']}/simulate-cascade -> Status: {status_sim}", flush=True)
        print(f"   Cascade Seeding Response: {json.dumps(data_sim, indent=2)}", flush=True)

print("\n==================================================", flush=True)
print("Public Data Ingestion Verification Complete!", flush=True)
print("==================================================", flush=True)
