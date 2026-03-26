import os

from typing import List, Optional

from pydantic import BaseModel, Field

from pydantic_ai import Agent, ToolOutput
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

class NewsItem(BaseModel):
    content: str = Field(
        description="A concise, objective 2-3 sentence summary of the story. If this is an update, explicitly mention what new information has emerged."
    )
    is_update: bool = Field(
        description="Set to True ONLY if this story provides new, material developments to an event already mentioned in the 'Previous Summaries'."
    )

class SummaryResponse(BaseModel):
    major_news: List[NewsItem] = Field(
        description="The 1 to 5 most impactful, high-priority news articles. Limit to maximum 5 items."
    )
    minor_news: List[NewsItem] = Field(
        description="Secondary, niche, or lower-priority news articles. Omit entirely if they offer no new value. Limit to maximum 5 items."
    )
    narrative_summary: str = Field(
        description="A cohesive 2-3 sentence overarching synthesis of the current overall news cycle, highlighting key themes from both major and minor news."
    )
    no_new_developments: bool = Field(
        description="Set to True ONLY if all incoming articles are redundant, repeating previously summarized information with no new material updates."
    )

class NewsSummarizer:
    def __init__(
        self, api_key, 
        model="openai/gpt-5-nano",
        base_url="https://openrouter.ai/api/v1"):

        self.or_model = OpenRouterModel(
            model,
            provider=OpenRouterProvider(api_key=api_key),
        )
        
    def summarize_article_list(self, articles: str, previous_summaries: str = None) -> SummaryResponse:
        system_prompt = (
            "You are an elite, objective news editor. Your objective is to process incoming news, "
            "triage it by importance, and synthesize a structured briefing.\n\n"
            "CRITICAL RULES:\n"
            "1. STRICT DEDUPLICATION: Compare incoming articles against 'Previous Summaries'. Completely ignore incoming articles that repeat established facts.\n"
            "2. MATERIAL UPDATES: If an incoming article contains a *material new development* to a previously covered story, include it, set `is_update=True`, and focus the summary ONLY on what has changed.\n"
            "3. TRIAGE: Distinguish carefully between 'major' (broad impact, global/national importance) and 'minor' (localized, niche, or secondary impact) news.\n"
            "4. NOTHING NEW: If the incoming batch yields absolutely no new stories or material updates, set `no_new_developments=True` and leave the lists empty.\n"
            "5. TONE: Maintain a strict, neutral journalistic tone."
        )

        user_prompt = f"""
Please analyze the incoming news against our existing coverage.

<previous_summaries>
{previous_summaries if previous_summaries else "None. This is the first batch of news."}
</previous_summaries>

<incoming_articles>
{articles}
</incoming_articles>

Generate the updated structured news summary based on the rules provided.
"""

        try:
            agent = Agent(
                self.or_model,
                instructions=system_prompt,
                output_type=[ 
                    ToolOutput(SummaryResponse, name='return_summaries'),
                ],
            )
            return agent.run_sync(user_prompt).output
        except Exception as e:
            print(f"Extraction Error: {e}")
            return None

    def format_to_markdown(self, data: SummaryResponse) -> str:
        """Input the data class into a template for consistent output."""
        if data.no_new_developments:
            return "No significant new developments since the last summary."

        output = []
        
        if data.major_news:
            output.append("### 🔴 Major News:")
            for item in data.major_news:
                prefix = "[UPDATE] " if item.is_update else ""
                output.append(f"- {prefix}{item.content}")

        if data.minor_news:
            output.append("\n### 🟡 Minor News:")
            for item in data.minor_news:
                prefix = "[UPDATE] " if item.is_update else ""
                output.append(f"- {prefix}{item.content}")

        if data.narrative_summary:
            output.append("\n### Summary:")
            output.append(data.narrative_summary)

        return "\n".join(output)
        