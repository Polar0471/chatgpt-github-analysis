import json
import re
import os


def clean_and_categorize_data(data, data_type):
    cleaned_data = []
    for item in data:
        if data_type == "issues_discussions":
            node = item.get("node", {})
            body = node.get("body", "")
            title = node.get("title", "")
            url = node.get("url", "")
            created_at = node.get("createdAt", "")
            repository = node.get("repository", {})
            item_type = node.get("__typename", "UNKNOWN")
        elif data_type == "commits":
            body = item.get("commit", {}).get("message", "")
            title = ""
            url = item.get("html_url", "")
            created_at = item.get("commit", {}).get(
                "author", {}).get("date", "")
            repository = {
                "name": item.get("repository", {}).get("name", ""),
                "owner": {
                    "login": item.get("repository", {}).get("owner", {}).get("login", "")
                }
            }
            item_type = "Commit"
        elif data_type == "pull_requests":
            body = item.get("body", "")
            title = item.get("title", "")
            url = item.get("html_url", "")
            created_at = item.get("created_at", "")
            repository = {
                "name": item.get("repository", {}).get("name", ""),
                "owner": {
                    "login": item.get("user", {}).get("login", "")
                }
            }
            item_type = "PullRequest"

        if body is None:
            body = ""

        body = re.sub(
            r"(Oi|Olá|Oi,|Olá,|Obrigado|Thanks|Thank you)[.!]*", "", body, flags=re.IGNORECASE)
        body = body.strip()

        category = categorize_interaction(body)

        if body:
            cleaned_data.append({
                "title": title,
                "body": body,
                "url": url,
                "createdAt": created_at,
                "repository": repository,
                "category": category,
                "type": item_type
            })

    return cleaned_data


def categorize_interaction(text):
    if re.search(r"(melhorar|ajustar|otimizar)", text, re.IGNORECASE):
        return "Request improvements"
    elif re.search(r"(descrição|description)", text, re.IGNORECASE):
        return "Request more description"
    elif re.search(r"(instruções|instructions)", text, re.IGNORECASE):
        return "Add specific instructions"
    elif re.search(r"(perguntas|questions)", text, re.IGNORECASE):
        return "Ask questions to find correct way"
    elif re.search(r"(contexto|context)", text, re.IGNORECASE):
        return "Add more context"
    elif re.search(r"(exemplo|example)", text, re.IGNORECASE):
        return "Request examples"
    elif re.search(r"(verificação|verification)", text, re.IGNORECASE):
        return "Request verification"
    elif re.search(r"(erro|mistake|bug)", text, re.IGNORECASE):
        return "Point mistake then request fix"
    elif re.search(r"(outra geração|another generation)", text, re.IGNORECASE):
        return "Request another generation"
    else:
        return "Outros"


with open("data/raw/github_chatgpt_data.json", "r") as f:
    issues_discussions_data = json.load(f)

cleaned_issues_discussions = clean_and_categorize_data(
    issues_discussions_data, "issues_discussions")

with open("data/raw/github_commits_data.json", "r") as f:
    commits_data = json.load(f)

cleaned_commits = clean_and_categorize_data(commits_data, "commits")

with open("data/raw/github_pull_requests_data.json", "r") as f:
    pull_requests_data = json.load(f)

cleaned_pull_requests = clean_and_categorize_data(
    pull_requests_data, "pull_requests")

all_cleaned_data = cleaned_issues_discussions + \
    cleaned_commits + cleaned_pull_requests

os.makedirs("data/processed", exist_ok=True)
with open("data/processed/cleaned_github_data.json", "w") as f:
    json.dump(all_cleaned_data, f, indent=2)
print("Dados limpos salvos em 'data/processed/cleaned_github_data.json'!")
