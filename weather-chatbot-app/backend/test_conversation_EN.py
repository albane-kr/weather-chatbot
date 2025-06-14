from app import get_agent_executor
import datetime
import time

test_cases = [
    {
        "prompt": "Hello! My name is Albane. What's your name?",
    },
    {
        "prompt": "Can you tell me what the weather is like today in Bettembourg?",
    },
    {
        "prompt": "What about tomorrow? I want to go running and need to know if I should take an umbrella.",
    },
    {
        "prompt": "Do you remember my name?",
    },
    {
        "prompt": "What's the weather like in Esch-sur-Alzette tomorrow?",
    },
    {
        "prompt": "Thank you! Have you ever visited Luxembourg?",
    },
    {
        "prompt": "What will the weather be like in Differdange this weekend?",
    },
    {
        "prompt": "Can you give me the weather for Dudelange for the next 24 hours?",
    },
    {
        "prompt": "What's your favorite food?",
    },
    {
        "prompt": "Will it rain in Wiltz tomorrow?",
    },
    
    {
        "prompt": "What is the weather in Germany today?",
    },
    {
        "prompt": "Thank you very much for your help rAIny, you're very nice!",
    },
]

results_path = "test_conversation_results.txt"

with open(results_path, "a", encoding="utf-8") as f:
    f.write(f"\n\n=== Test in EN - Run at {datetime.datetime.now()} ===\n")
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