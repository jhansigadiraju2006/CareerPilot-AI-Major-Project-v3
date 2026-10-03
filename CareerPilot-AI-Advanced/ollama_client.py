from config import MODEL
def generate(prompt,system=''):
    try:
        import ollama
        r=ollama.generate(model=MODEL,prompt=prompt,system=system)
        return r.get('response','').strip(),True
    except Exception:return '',False
