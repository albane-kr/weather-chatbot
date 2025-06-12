from app import agent_executor

# For language detection
from langdetect import detect

# For BLEU score
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score
from nltk.tokenize import word_tokenize

test_cases = [
    {
        "prompt": "What's the weather like in Luxembourg?",
        "expected_language": "en",
        "reference": "Weather in Luxembourg:"
    },
    {
        "prompt": "Quel temps fait-il à Luxembourg?",
        "expected_language": "fr",
        "reference": "Météo à Luxembourg:"
    },
    {
        "prompt": "Wie ist das Wetter in Berlin?",
        "expected_language": "de",
        "reference": "Wetter in Berlin:"
    },
    {
        "prompt": "Hello, who are you?",
        "expected_language": "en",
        "reference": "I am"
    },
]

smoothie = SmoothingFunction().method4

for case in test_cases:
    print(f"\nPrompt: {case['prompt']}")
    try:
        response = agent_executor.invoke({"input": case["prompt"]})
        output = response["output"]
        print(f"Output: {output}")

        # Language detection
        try:
            detected_lang = detect(output)
            print(f"Detected language: {detected_lang} | Expected: {case['expected_language']}")
            lang_match = detected_lang == case['expected_language']
        except Exception as e:
            print(f"Language detection error: {e}")
            lang_match = False

        # BLEU score (compare to reference, very basic)
        reference = [case["reference"].split()]
        candidate = output.split()
        bleu = sentence_bleu(reference, candidate, smoothing_function=smoothie)
        print(f"BLEU score vs reference: {bleu:.2f}")

        # METEOR score (optional, for more robust evaluation)
        meteor = meteor_score([word_tokenize(case["reference"])], word_tokenize(output))
        print(f"METEOR score vs reference: {meteor:.2f}")

        # Simple pass/fail
        print(f"Language match: {'PASS' if lang_match else 'FAIL'}")
        print(f"BLEU > 0.3: {'PASS' if bleu > 0.3 else 'FAIL'}")
        print(f"METEOR > 0.5: {'PASS' if meteor > 0.5 else 'FAIL'}")

    except Exception as e:
        print(f"Error: {e}")
    print("-" * 40)