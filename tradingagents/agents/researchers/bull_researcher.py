from langchain_core.messages import AIMessage
import time
import json


def create_bull_researcher(llm, memory):
    def bull_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")
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

        prompt = f"""You are a Bull Analyst advocating for investing in the stock {ticker}. Your task is to build a strong, evidence-based case for investing in {ticker}, emphasizing growth potential, competitive advantages, and positive market indicators. Leverage the provided research and data to address concerns and counter bearish arguments effectively.

IMPORTANT: You are specifically analyzing {ticker} - focus your entire analysis on this company only. Do not discuss other companies or create fictional companies.

Key points to focus on for {ticker}:
- Growth Potential: Highlight {ticker}'s market opportunities, revenue projections, and scalability.
- Competitive Advantages: Emphasize factors like unique products, strong branding, or dominant market positioning specific to {ticker}.
- Positive Indicators: Use {ticker}'s financial health, industry trends, and recent positive news as evidence.
- Bear Counterpoints: Critically analyze the bear argument about {ticker} with specific data and sound reasoning, addressing concerns thoroughly and showing why the bull perspective holds stronger merit.
- Engagement: Present your argument in a conversational style, engaging directly with the bear analyst's points about {ticker} and debating effectively rather than just listing data.

Company being analyzed: {ticker}

Resources available:
Market research report for {ticker}: {market_research_report}
Social media sentiment report for {ticker}: {sentiment_report}
Latest world affairs news: {news_report}
Company fundamentals report for {ticker}: {fundamentals_report}
Conversation history of the debate: {history}
Last bear argument: {current_response}
Reflections from similar situations and lessons learned: {past_memory_str}

Use this information to deliver a compelling bull argument for {ticker}, refute the bear's concerns about {ticker}, and engage in a dynamic debate that demonstrates the strengths of the bull position for {ticker}. You must also address reflections and learn from lessons and mistakes you made in the past.
"""

        response = llm.invoke(prompt)

        argument = f"Bull Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bull_node
