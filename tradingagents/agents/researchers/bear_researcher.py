from langchain_core.messages import AIMessage
import time
import json


def create_bear_researcher(llm, memory):
    def bear_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bear_history = investment_debate_state.get("bear_history", "")
        ticker = state["company_of_interest"]

        current_response = investment_debate_state.get("current_response", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        
        # Handle potential memory errors gracefully
        past_memory_str = ""
        try:
            if curr_situation.strip():  # Only query memories if we have actual content
                past_memories = memory.get_memories(curr_situation, n_matches=2)
                for i, rec in enumerate(past_memories, 1):
                    past_memory_str += rec["recommendation"] + "\n\n"
        except Exception as e:
            # If memory system fails, continue without past memories
            print(f"Warning: Could not retrieve past memories: {str(e)}")
            past_memory_str = "No past memories available."

        prompt = f"""You are a Bear Analyst making the case against investing in the stock {ticker}. Your goal is to present a well-reasoned argument against investing in {ticker}, emphasizing risks, challenges, and negative indicators. Leverage the provided research and data to highlight potential downsides and counter bullish arguments effectively.

IMPORTANT: You are specifically analyzing {ticker} - focus your entire analysis on this company only. Do not discuss other companies or create fictional companies.

Key points to focus on for {ticker}:

- Risks and Challenges: Highlight factors like market saturation, financial instability, or macroeconomic threats that could hinder {ticker}'s performance.
- Competitive Weaknesses: Emphasize vulnerabilities such as weaker market positioning, declining innovation, or threats from competitors specific to {ticker}.
- Negative Indicators: Use evidence from {ticker}'s financial data, market trends, or recent adverse news to support your position.
- Bull Counterpoints: Critically analyze the bull argument about {ticker} with specific data and sound reasoning, exposing weaknesses or over-optimistic assumptions.
- Engagement: Present your argument in a conversational style, directly engaging with the bull analyst's points about {ticker} and debating effectively rather than simply listing facts.

Company being analyzed: {ticker}

Resources available:

Market research report for {ticker}: {market_research_report}
Social media sentiment report for {ticker}: {sentiment_report}
Latest world affairs news: {news_report}
Company fundamentals report for {ticker}: {fundamentals_report}
Conversation history of the debate: {history}
Last bull argument: {current_response}
Reflections from similar situations and lessons learned: {past_memory_str}

Use this information to deliver a compelling bear argument against {ticker}, refute the bull's claims about {ticker}, and engage in a dynamic debate that demonstrates the risks and weaknesses of investing in {ticker}. You must also address reflections and learn from lessons and mistakes you made in the past.
"""

        response = llm.invoke(prompt)

        argument = f"Bear Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bear_node
