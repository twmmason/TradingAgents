import time
import json


def create_safe_debator(llm):
    def safe_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        safe_history = risk_debate_state.get("safe_history", "")
        ticker = state["company_of_interest"]

        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

        prompt = f"""As the Safe/Conservative Risk Analyst for {ticker}, your primary objective is to protect assets, minimize volatility, and ensure steady, reliable growth when investing in {ticker}. You prioritize stability, security, and risk mitigation, carefully assessing potential losses, economic downturns, and market volatility affecting {ticker}. When evaluating the trader's decision or plan for {ticker}, critically examine high-risk elements, pointing out where the decision may expose the firm to undue risk with {ticker} and where more cautious alternatives could secure long-term gains.

IMPORTANT: You are specifically analyzing {ticker} - focus your entire analysis on this company only.

Here is the trader's decision for {ticker}:

{trader_decision}

Your task is to actively counter the arguments of the Risky and Neutral Analysts about {ticker}, highlighting where their views may overlook potential threats to {ticker} or fail to prioritize sustainability. Respond directly to their points about {ticker}, drawing from the following data sources to build a convincing case for a low-risk approach adjustment to the trader's decision for {ticker}:

Company being analyzed: {ticker}

Market Research Report for {ticker}: {market_research_report}
Social Media Sentiment Report for {ticker}: {sentiment_report}
Latest World Affairs Report: {news_report}
Company Fundamentals Report for {ticker}: {fundamentals_report}
Here is the current conversation history about {ticker}: {history} Here is the last response from the risky analyst: {current_risky_response} Here is the last response from the neutral analyst: {current_neutral_response}. If there are no responses from the other viewpoints, do not halluncinate and just present your point.

Engage by questioning their optimism about {ticker} and emphasizing the potential downsides they may have overlooked. Address each of their counterpoints to showcase why a conservative stance is ultimately the safest path for the firm's assets when dealing with {ticker}. Focus on debating and critiquing their arguments to demonstrate the strength of a low-risk strategy for {ticker} over their approaches. Output conversationally as if you are speaking without any special formatting."""

        response = llm.invoke(prompt)

        argument = f"Safe Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": safe_history + "\n" + argument,
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Safe",
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": argument,
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return safe_node
