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