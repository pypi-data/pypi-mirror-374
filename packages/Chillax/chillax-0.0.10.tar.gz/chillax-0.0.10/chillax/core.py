import google.generativeai as genai

class Chillax:

    model = None

    @staticmethod
    def setAPIKey(api: str):
        if not api:
            raise RuntimeError(
                "API key not found. Please enter the correct API key.")
        genai.configure(api_key=api)
        Chillax.model = genai.GenerativeModel("gemini-1.5-flash")

    def __getattr__(self, name: str):
        def wrapper(*args, **kwargs):
            if not Chillax.model:
                raise RuntimeError("Model not initialized. Call setAPIKey first.")
            prompt = f"Perform `{name}` with args={args}, kwargs={kwargs} , just give the answer do not explain"
            return Chillax.model.generate_content(prompt).text
        return wrapper

chillax = Chillax()
