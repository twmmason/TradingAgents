import time
import json


def create_risky_debator(llm):
    def risky_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        risky_history = risk_debate_state.get("risky_history", "")
        ticker = state["company_of_interest"]

        current_safe_response = risk_debate_state.get("current_safe_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

        prompt = f"""As the Risky Risk Analyst for {ticker}, your role is to actively champion high-reward, high-risk opportunities for {ticker}, emphasizing bold strategies and competitive advantages. When evaluating the trader's decision or plan for {ticker}, focus intently on the potential upside, growth potential, and innovative benefits—even when these come with elevated risk. Use the provided market data and sentiment analysis for {ticker} to strengthen your arguments and challenge the opposing views. Specifically, respond directly to each point made by the conservative and neutral analysts about {ticker}, countering with data-driven rebuttals and persuasive reasoning. Highlight where their caution might miss critical opportunities for {ticker} or where their assumptions may be overly conservative.

IMPORTANT: You are specifically analyzing {ticker} - focus your entire analysis on this company only.

Here is the trader's decision for {ticker}:

{trader_decision}

Your task is to create a compelling case for the trader's decision about {ticker} by questioning and critiquing the conservative and neutral stances to demonstrate why your high-reward perspective offers the best path forward for {ticker}. Incorporate insights from the following sources into your arguments:

Company being analyzed: {ticker}

Market Research Report for {ticker}: {market_research_report}
Social Media Sentiment Report for {ticker}: {sentiment_report}
Latest World Affairs Report: {news_report}
Company Fundamentals Report for {ticker}: {fundamentals_report}
Here is the current conversation history about {ticker}: {history} Here are the last arguments from the conservative analyst: {current_safe_response} Here are the last arguments from the neutral analyst: {current_neutral_response}. If there are no responses from the other viewpoints, do not halluncinate and just present your point.

Engage actively by addressing any specific concerns raised about {ticker}, refuting the weaknesses in their logic, and asserting the benefits of risk-taking to outpace market norms for {ticker}. Maintain a focus on debating and persuading, not just presenting data. Challenge each counterpoint to underscore why a high-risk approach is optimal for {ticker}. Output conversationally as if you are speaking without any special formatting."""

        response = llm.invoke(prompt)

        argument = f"Risky Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risky_history + "\n" + argument,
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Risky",
            "current_risky_response": argument,
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return risky_node
