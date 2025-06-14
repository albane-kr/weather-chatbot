from app import get_agent_executor
import datetime
import time

test_cases = [
    {
        "prompt": "Hallo! Ich heiße Albane. Wie heißt du?",
    },
    {
        "prompt": "Kannst du mir sagen, wie das Wetter heute in Bettembourg ist?",
    },
    {
        "prompt": "Wie sieht es morgen aus? Ich möchte joggen gehen und wissen, ob ich einen Regenschirm brauche.",
    },
    {
        "prompt": "Weißt du noch, wie ich heiße?",
    },
    {
        "prompt": "Wie ist das Wetter morgen in Esch-sur-Alzette?",
    },
    {
        "prompt": "Danke! Warst du schon mal in Luxemburg?",
    },
    {
        "prompt": "Wie wird das Wetter am Wochenende in Differdingen?",
    },
    {
        "prompt": "Kannst du mir das Wetter für Dudelange für die nächsten 24 Stunden geben?",
    },
    {
        "prompt": "Was ist dein Lieblingsessen?",
    },
    {
        "prompt": "Wird es morgen in Wiltz regnen?",
    },
    
    {
        "prompt": "Wie ist das Wetter heute in Deutschland?",
    },
    {
        "prompt": "Vielen Dank für deine Hilfe rAIny, du bist sehr nett!",
    },
]

results_path = "test_conversation_results.txt"

with open(results_path, "a", encoding="utf-8") as f:
    f.write(f"\n\n=== Test in DE - Run at {datetime.datetime.now()} ===\n")
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

print(f"Test results appended to {results_path}")