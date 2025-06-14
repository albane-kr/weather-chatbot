from app import get_agent_executor
import datetime
import time

test_cases = [
    {
        "prompt": "Bonjour ! Je m'appelle Albane. Et toi, comment tu t'appelles ?",
    },
    {
        "prompt": "Peux-tu me dire quelle est la météo aujourd'hui à Bettembourg ?",
    },
    {
        "prompt": "Qu'en est-il de demain ? J'aimerais aller courir et je veux savoir si je dois prendre un parapluie.",
    },
    {
        "prompt": "Est-ce que tu te souviens de mon prénom ?",
    },
    {
        "prompt": "Quelle est la météo à Esch-sur-Alzette demain ?",
    },
    {
        "prompt": "Merci ! Et toi, tu as déjà visité le Luxembourg ?",
    },
    {
        "prompt": "Quel temps fera-t-il à Differdange ce week-end ?",
    },
    {
        "prompt": "Peux-tu me donner la météo pour Dudelange pour les prochaines 24 heures ?",
    },
    {
        "prompt": "Quel est ton plat préféré ?",
    },
    {
        "prompt": "Est-ce qu'il va pleuvoir à Wiltz demain ?",
    },
    {
        "prompt": "Quelle est la météo en Allemagne aujourd'hui ?",
    },
    {
        "prompt": "Merci beaucoup pour ton aide rAIny, tu es super sympa !",
    },
]

results_path = "test_conversation_results.txt"

with open(results_path, "w", encoding="utf-8") as f:
    f.write(f"\n\n=== Test in FR - Run at {datetime.datetime.now()} ===\n")
    for idx, case in enumerate(test_cases, 1):
        f.write(f"Test Case {idx}\n")
        f.write(f"Prompt: {case['prompt']}\n")
        try:
            agent_executor = get_agent_executor(case["prompt"], session_id="default_session")
            response = agent_executor.invoke({"input": case["prompt"]})
            output = response["output"]
            f.write(f"Output: {output}\n")
        except Exception as e:
            f.write(f"Error: {e}\n")
        f.write("-" * 40 + "\n")
        time.sleep(30)

print(f"Test results written to {results_path}")