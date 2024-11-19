from googlesearch import search

def check_fake_news_on_google(text):
    # Recherche Google
    query = f'"{text}"'
    st.write(f"Recherche sur Google pour : {text}")

    # Effectuer la recherche Google
    results = list(search(query, num_results=5))  # Limiter à 5 résultats
    if results:
        st.write("Voici les résultats trouvés sur Google :")
        for url in results:
            st.write(f"- {url}")

        # Concaténer les descriptions des résultats pour OpenAI
        combined_results = "\n".join(results)

        # Indiquer si des sources fiables sont présentes
        trusted_sources = [
            "france24.com", "minnpost.com", "factcheck.org", "snopes.com",
            "afp.com", "lemonde.fr/verification", "reuters.com/fact-check"
        ]
        if any(any(source in url for source in trusted_sources) for url in results):
            st.success("Warning : The verification sources already dealt with it.")
        else:
            st.info("Aucune source de vérification détectée.")

        return combined_results
    else:
        st.write("Aucun résultat trouvé.")
        return ""