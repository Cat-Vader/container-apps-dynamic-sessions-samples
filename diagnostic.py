import os
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError
from dotenv import load_dotenv

load_dotenv()

def print_environment_variables():
    print("Azure Environment Variables:")
    print(f"AZURE_TENANT_ID: {'*' * len(os.getenv('AZURE_TENANT_ID', '')) if os.getenv('AZURE_TENANT_ID') else 'Not Set'}")
    print(f"AZURE_CLIENT_ID: {'*' * len(os.getenv('AZURE_CLIENT_ID', '')) if os.getenv('AZURE_CLIENT_ID') else 'Not Set'}")
    print(f"AZURE_CLIENT_SECRET: {'Set' if os.getenv('AZURE_CLIENT_SECRET') else 'Not Set'}")

def test_default_credential():
    print("\nTesting DefaultAzureCredential:")
    try:
        credential = DefaultAzureCredential()
        token = credential.get_token("https://management.azure.com/.default")
        print("Successfully obtained token using DefaultAzureCredential")
    except Exception as e:
        print(f"Error with DefaultAzureCredential: {str(e)}")

def test_client_secret_credential():
    print("\nTesting ClientSecretCredential:")
    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")
    
    if not all([tenant_id, client_id, client_secret]):
        print("Missing one or more required environment variables for ClientSecretCredential")
        return

    try:
        credential = ClientSecretCredential(tenant_id, client_id, client_secret)
        token = credential.get_token("https://management.azure.com/.default")
        print("Successfully obtained token using ClientSecretCredential")
    except Exception as e:
        print(f"Error with ClientSecretCredential: {str(e)}")

if __name__ == "__main__":
    print_environment_variables()
    test_default_credential()
    test_client_secret_credential()