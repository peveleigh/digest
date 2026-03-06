from openai import OpenAI

class NewsSummarizer:
    def __init__(self, api_key, model="openai/gpt-4o-mini"):
        """
        Initialize with API key and preferred model.
        Model strings can be found on openrouter.ai/models
        """
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = model

    def call_model(self,prompt):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes news articles efficiently."},
                    {"role": "user", "content": prompt}
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"An error occurred: {str(e)}"

    def summarize_title_list(self, titles):
        prompt = f"""
        You are a professional news editor. Summarize the key events and trends from the past 24 hours based on the article titles provided below.

        ## Guidelines:
        - Distinguish between major headlines and minor stories; prioritize the most significant developments.
        - Do not fabricate details that are not supported or clearly implied by the titles.
        - If a story appears in multiple titles, note it as a trending/developing story.
        - Use a neutral, objective tone.
        - Keep the summary concise (aim for a few short paragraphs).

        ## Article Titles:
        {titles}

        ## 24-Hour News Summary:
        """
        return self.call_model(prompt)

    def summarize_article_list(self, articles):
        prompt = f"""
        You are a professional news editor. Summarize the key events and trends from the past 24 hours based on the news articles and format template provided below.

        ## Guidelines:
        - Distinguish between major headlines and minor stories; prioritize the most significant developments.
        - Do not fabricate details that are not supported or clearly implied by the titles.
        - If a story appears in multiple titles, note it as a trending/developing story.
        - Use a neutral, objective tone.
        - Keep the summary concise (aim for a few short paragraphs).
        - If articles contain contradictory claims, acknowledge the discrepancy rather than choosing one version.
        - Group related stories together under a single bullet point rather than listing them separately.
        - If the provided articles are insufficient to identify clear major vs. minor distinctions, state that explicitly rather than guessing.

        ## Articles:
        {articles}

        ## Format template:
        ### 📈 Developing/Trending Stories:
        - Stories appearing across multiple articles with brief synthesis

        ### 🔴 Major News:
        - **[Topic/Category]:** Most important story text
        - **[Topic/Category]:** More important news

        ### 🟡 Minor News:
        - Minor news story text

        ### Summary:
        A 2-3 sentence overview capturing the dominant narrative of the news cycle.
        """
        return self.call_model(prompt)

    def summarize_single_article(self, title, content):
        """
        Sends the article to the LLM and returns the summary.
        """
        prompt = f"""
        You are a skilled news editor. Summarize the following news article in a few sentences, capturing the key facts (who, what, when, where, why). Use a neutral, objective tone. Do not include opinions or information not present in the article.

        TITLE: {title}

        CONTENT: {content}

        SUMMARY:
        """

        return self.call_model(prompt)