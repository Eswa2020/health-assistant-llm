import os
import sys
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# TODO 1: Exit with sys.exit(1) and a friendly message if api_key is None.
if api_key is None:
    # This catches the case where .env doesn't exist at all, or the
    # OPENAI_API_KEY line is missing entirely — os.getenv() returns None
    # when a variable simply isn't found anywhere in the environment.
    print("ERROR: OPENAI_API_KEY not found. Did you create a .env file?")
    sys.exit(1)  # Exit code 1 signals "something went wrong" to the system —
                 # this stops the script immediately rather than continuing
                 # with a broken/missing key.

# TODO 2: Exit if api_key equals the placeholder 'sk-your-key-here'.
elif api_key == "sk-your-key-here":
    # This catches a very common mistake: someone follows the setup
    # instructions but forgets to actually replace the placeholder text
    # with their real key. Without this check, the script would "succeed"
    # even though the key is fake and any real API call would fail later.
    print("ERROR: You're still using the placeholder key. Replace it with your real OpenAI API key in .env.")
    sys.exit(1)

# TODO 3: Otherwise print 'Key loaded successfully' with the masked key.
else:
    # If we reach this point, the key exists AND isn't the placeholder —
    # so it's safe to treat it as a real, usable key.
    masked = api_key[:7] + "..." + api_key[-4:]
    print(f"Key loaded successfully: {masked}")
    print(f"Length: {len(api_key)} characters")

print("\n--- Conclusion ---")
print("This defensive version catches two common failure points before")
print("they waste time: a completely missing key, and a forgotten placeholder.")
print("By failing fast with sys.exit(1) and a clear message, the script")
print("stops immediately instead of silently continuing with bad credentials —")
print("this is the same 'fail fast, fail clearly' principle used throughout")
print("production systems to avoid confusing downstream errors.")