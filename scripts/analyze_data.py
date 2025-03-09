import json
from collections import defaultdict
from tabulate import tabulate

with open("data/processed/cleaned_github_data.json", "r") as f:
    cleaned_data = json.load(f)

categories_count = defaultdict(int)
cg_count = defaultdict(int)
non_cg_count = defaultdict(int)

for item in cleaned_data:
    category = item["type"]
    categories_count[category] += 1
    if "chat.openai.com" in item["body"]:
        cg_count[category] += 1
    else:
        non_cg_count[category] += 1

table1_data = []
for category in categories_count:
    total = categories_count[category]
    cg = cg_count.get(category, 0)
    non_cg = non_cg_count.get(category, 0)
    percent_cg = (cg / total) * 100 if total > 0 else 0
    table1_data.append([category, cg, non_cg, total, f"{percent_cg:.1f}%"])

print("Tabela 1: Número de conversas analisadas entre ChatGPT e desenvolvedores")
print(tabulate(table1_data, headers=[
      "Categoria", "CG", "Non-CG", "Total", "% de CG"], tablefmt="pretty"))

prompt_categories_count = defaultdict(int)
for item in cleaned_data:
    prompt_categories_count[item["category"]] += 1

table2_data = [[k, v] for k, v in prompt_categories_count.items()]

print("\nTabela 2: Número de conversas de geração de código por categoria de prompt")
print(tabulate(table2_data, headers=[
      "Categoria", "Contagem"], tablefmt="pretty"))

code_usage_counts = defaultdict(int)

for item in cleaned_data:
    body = item["body"].lower()
    if "usado sem alterações" in body or "exact match" in body:
        code_usage_counts["Exact Match"] += 1
    elif "ajustado antes do uso" in body or "modificado" in body:
        code_usage_counts["Modified Code"] += 1
    elif "documentação" in body or "documentation" in body:
        code_usage_counts["Document"] += 1
    else:
        code_usage_counts["Supplementary Info"] += 1

total_code_usages = sum(code_usage_counts.values())
table3_data = []
for usage, count in code_usage_counts.items():
    proportion = (count / total_code_usages) * \
        100 if total_code_usages > 0 else 0
    table3_data.append([usage, f"{proportion:.1f}%"])

print("\nTabela 3: Proporção de usos do código gerado")
print(tabulate(table3_data, headers=[
      "Uso do Código", "Proporção"], tablefmt="pretty"))
