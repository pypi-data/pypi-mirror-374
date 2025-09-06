# Default pricing tables. Adjust anytime without touching code elsewhere.
OPENAI_DEFAULT = [
    {"match": "gpt-4.1",     "input_full": 2.00/1_000_000,  "input_cached": 0.50/1_000_000, "output": 8.00/1_000_000},
    {"match": "gpt-4o-mini", "input_full": 0.15/1_000_000,  "input_cached": 0.075/1_000_000, "output": 0.60/1_000_000},
]

GEMINI_DEFAULT = [
    {"match": "gemini-2.5-pro",         "input_full": 1.25/1_000_000, "input_cached": 0.0, "output": 10.00/1_000_000},
    {"match": "gemini-2.5-pro-200kplus","input_full": 2.50/1_000_000, "input_cached": 0.0, "output": 15.00/1_000_000},
    {"match": "gemini-2.5-flash",       "input_full": 0.30/1_000_000, "input_cached": 0.0, "output": 2.50/1_000_000},
    {"match": "gemini-2.5-flash-lite",  "input_full": 0.10/1_000_000, "input_cached": 0.0, "output": 0.40/1_000_000},
    {"match": "gemini-2.0-flash",       "input_full": 0.10/1_000_000, "input_cached": 0.0, "output": 0.40/1_000_000},
    {"match": "gemini-2.0-flash-lite",  "input_full": 0.075/1_000_000,"input_cached": 0.0, "output": 0.30/1_000_000},
]
