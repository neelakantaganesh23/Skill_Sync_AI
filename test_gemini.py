# Gemini API Key Test Script
# Simple test to verify your Gemini API key works

import google.generativeai as genai

def test_gemini_api(api_key):
    """Test if Gemini API key is working"""
    
    try:
        # Configure the API key
        genai.configure(api_key=api_key)
        
        # Initialize the model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Send a simple test prompt
        print("Testing Gemini API...")
        response = model.generate_content("Say 'Hello! Your API key is working correctly.'")
        
        # Print the response
        print("✅ SUCCESS!")
        print(f"Response: {response.text}")
        return True
        
    except Exception as e:
        print("❌ FAILED!")
        print(f"Error: {str(e)}")
        
        # Common error messages and solutions
        if "API_KEY_INVALID" in str(e):
            print("\n💡 Solution: Check if your API key is correct")
        elif "PERMISSION_DENIED" in str(e):
            print("\n💡 Solution: Make sure Generative AI API is enabled in your Google Cloud project")
        elif "QUOTA_EXCEEDED" in str(e):
            print("\n💡 Solution: You've exceeded your API quota limit")
        else:
            print("\n💡 Solution: Check your internet connection and API key")
        
        return False

# Test your API key
if __name__ == "__main__":
    # Replace with your actual API key
    API_KEY = ""
    
    if API_KEY == "your-gemini-api-key-here":
        print("⚠️  Please replace 'your-gemini-api-key-here' with your actual API key")
    else:
        test_gemini_api(API_KEY)

# Alternative: Test with user input
def test_with_input():
    """Test API key with user input"""
    api_key = input("Enter your Gemini API key: ").strip()
    if api_key:
        test_gemini_api(api_key)
    else:
        print("No API key provided!")

# Uncomment the line below to test with manual input
# test_with_input()