import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

QUERY_TEMPLATE = """
{{
  search(query: "https://chat.openai.com/share/", type: {type}, first: 100, after: {cursor}) {{
    edges {{
      node {{
        ... on {node_type} {{
          title
          body
          url
          createdAt
          repository {{
            name
            owner {{
              login
            }}
          }}
        }}
      }}
    }}
    pageInfo {{
      endCursor
      hasNextPage
    }}
  }}
}}
"""


def fetch_github_data(type, node_type):
    cursor = None
    all_data = []
    has_next_page = True

    while has_next_page:
        query = QUERY_TEMPLATE.format(
            type=type, node_type=node_type, cursor=f'"{cursor}"' if cursor else "null")
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query},
            headers=HEADERS
        )

        if response.status_code != 200:
            print(f"Erro na requisição para {type}: {response.status_code}")
            print("Resposta da API:", response.text)
            break

        try:
            data = response.json()
            if "errors" in data:
                print(f"Erro na consulta GraphQL para {type}:")
                for error in data["errors"]:
                    print(error["message"])
                break

            if "data" not in data:
                print(f"Resposta inesperada para {type}:")
                print(data)
                break

            all_data.extend(data["data"]["search"]["edges"])
            page_info = data["data"]["search"]["pageInfo"]
            has_next_page = page_info["hasNextPage"]
            cursor = page_info["endCursor"]

            time.sleep(1)

        except Exception as e:
            print(f"Erro ao processar resposta para {type}: {e}")
            break

    return all_data


def fetch_commits():
    url = "https://api.github.com/search/commits"
    params = {
        "q": "https://chat.openai.com/share/",
        "per_page": 100
    }
    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code == 200:
        return response.json()["items"]
    else:
        print(f"Erro na requisição: {response.status_code}")
        print("Resposta da API:", response.text)
        return []


def fetch_pull_requests():
    url = "https://api.github.com/search/issues"
    query = "https://chat.openai.com/share/ type:pr"
    params = {
        "q": query,
        "per_page": 100,
        "page": 1
    }
    all_data = []

    while True:
        response = requests.get(url, headers=HEADERS, params=params)

        if response.status_code != 200:
            print(f"Erro na requisição: {response.status_code}")
            print("Resposta da API:", response.text)
            break

        data = response.json()
        all_data.extend(data["items"])

        if "next" in response.links:
            params["page"] += 1
            time.sleep(1)
        else:
            break

    return all_data


categories = {
    "ISSUE": "Issue",
    "DISCUSSION": "Discussion",
}

all_data = []
for type, node_type in categories.items():
    print(f"Coletando dados para {node_type}...")
    data = fetch_github_data(type, node_type)
    all_data.extend(data)

os.makedirs("data/raw", exist_ok=True)
with open("data/raw/github_chatgpt_data.json", "w") as f:
    json.dump(all_data, f, indent=2)
print("Dados de Issues e Discussions salvos em 'data/raw/github_chatgpt_data.json'!")

print("Coletando dados para Commits...")
commits = fetch_commits()

with open("data/raw/github_commits_data.json", "w") as f:
    json.dump(commits, f, indent=2)
print("Dados de Commits salvos em 'data/raw/github_commits_data.json'!")

print("Coletando dados para Pull Requests...")
pull_requests = fetch_pull_requests()

with open("data/raw/github_pull_requests_data.json", "w") as f:
    json.dump(pull_requests, f, indent=2)
print("Dados de Pull Requests salvos em 'data/raw/github_pull_requests_data.json'!")
