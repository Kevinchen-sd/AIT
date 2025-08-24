import os

try:
    from dotenv import load_dotenv  # pip install python-dotenv
    load_dotenv()  # loads variables from .env into the environment
except Exception:
    # dotenv is optional; you can also export env vars via your shell
    pass

def main():
    account_key = os.environ.get("ACCOUNT_KEY")
    if not account_key:
        print("ACCOUNT_KEY is not set. Put it in your local .env file.")
    else:
        print("Loaded ACCOUNT_KEY (value hidden). Ready to call your services securely.")
    # Your app logic here

if __name__ == "__main__":
    main()
