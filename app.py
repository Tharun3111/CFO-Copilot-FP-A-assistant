"""
Streamlit app for CFO Copilot (FP&A).
Interactive Q&A interface for finance metrics.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from agent.intents import parse_question
from agent.tools import (
    revenue_vs_budget,
    gross_margin_series,
    opex_breakdown,
    ebitda_for_month,
    cash_runway_months
)


# Page config
st.set_page_config(
    page_title="CFO Copilot (FP&A)",
    page_icon="💼",
    layout="wide"
)


def main():
    """Main app entry point."""
    
    # Header
    st.title("💼 CFO Copilot (FP&A)")
    st.markdown("Ask questions about your financial data using natural language.")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        fixtures_path = st.text_input(
            "Fixtures Directory",
            value="fixtures",
            help="Path to directory containing CSV files"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Example Questions")
        st.markdown("""
        - What was June 2025 revenue vs budget?
        - Show Gross Margin % trend for last 3 months
        - Break down Opex by category for June 2025
        - What is our cash runway?
        """)
    
    # Main input
    question = st.text_input(
        "❓ Ask a finance question:",
        placeholder="e.g., What was June 2025 revenue vs budget in USD?"
    )
    
    if st.button("Ask", type="primary") or question:
        if not question:
            st.warning("Please enter a question.")
            return
        
        # Parse intent
        with st.spinner("Analyzing question..."):
            intent = parse_question(question)
        
        # Show parsed intent
        with st.expander("🔍 Parsed Intent", expanded=False):
            st.json({
                "kind": intent.kind,
                "month": intent.month,
                "lookback": intent.lookback
            })
        
        # Route to appropriate handler
        if intent.kind == 'revenue_vs_budget':
            handle_revenue_vs_budget(intent, fixtures_path)
        
        elif intent.kind == 'gm_trend':
            handle_gm_trend(intent, fixtures_path)
        
        elif intent.kind == 'opex_breakdown':
            handle_opex_breakdown(intent, fixtures_path)
        
        elif intent.kind == 'cash_runway':
            handle_cash_runway(fixtures_path)
        
        elif intent.kind == 'unknown':
            st.error("❌ Unable to understand the question.")
            st.info("""
            **Try questions like:**
            - What was [Month Year] revenue vs budget?
            - Show Gross Margin % trend for last [N] months
            - Break down Opex by category for [Month Year]
            - What is our cash runway?
            """)


def handle_revenue_vs_budget(intent, fixtures_path):
    """Handle revenue vs budget queries."""
    try:
        actual, budget, variance = revenue_vs_budget(
            fixtures_dir=fixtures_path,
            month=intent.month
        )
        
        st.success("✅ Revenue vs Budget Analysis")
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Actual Revenue",
                value=f"${actual:,.0f}",
                delta=None
            )
        
        with col2:
            st.metric(
                label="Budget Revenue",
                value=f"${budget:,.0f}",
                delta=None
            )
        
        with col3:
            delta_pct = (variance / budget * 100) if budget > 0 else 0
            st.metric(
                label="Variance",
                value=f"${variance:,.0f}",
                delta=f"{delta_pct:+.1f}%"
            )
        
        # Summary text
        status = "above" if variance > 0 else "below"
        st.markdown(f"""
        **Summary:** Actual revenue was **${abs(variance):,.0f} {status} budget** 
        ({abs(delta_pct):.1f}% {'over' if variance > 0 else 'under'}performance).
        """)
        
    except Exception as e:
        st.error(f"Error calculating revenue vs budget: {str(e)}")


def handle_gm_trend(intent, fixtures_path):
    """Handle gross margin trend queries."""
    try:
        lookback = intent.lookback or 3
        df = gross_margin_series(
            fixtures_dir=fixtures_path,
            end_month=intent.month,
            lookback=lookback
        )
        
        if df.empty:
            st.warning("No data available for the requested period.")
            return
        
        st.success(f"✅ Gross Margin % Trend (Last {lookback} Months)")
        
        # Line chart
        fig = px.line(
            df,
            x='month',
            y='gross_margin_pct',
            markers=True,
            title=f"Gross Margin % Trend"
        )
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Gross Margin %",
            yaxis_ticksuffix="%",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Latest value
        latest = df.iloc[-1]
        st.metric(
            label=f"Latest GM% ({latest['month']})",
            value=f"{latest['gross_margin_pct']:.1f}%"
        )
        
        # Data table
        with st.expander("📋 View Data"):
            st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error calculating GM trend: {str(e)}")


def handle_opex_breakdown(intent, fixtures_path):
    """Handle Opex breakdown queries."""
    try:
        if not intent.month:
            st.warning("Please specify a month for Opex breakdown.")
            return
        
        df = opex_breakdown(fixtures_dir=fixtures_path, month=intent.month)
        
        if df.empty:
            st.warning(f"No Opex data available for {intent.month}.")
            return
        
        st.success(f"✅ Operating Expenses Breakdown - {intent.month}")
        
        # Bar chart
        fig = px.bar(
            df,
            x='category',
            y='usd',
            title=f"Opex by Category ({intent.month})",
            labels={'usd': 'Amount (USD)', 'category': 'Category'}
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary metrics
        total_opex = df['usd'].sum()
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Opex", f"${total_opex:,.0f}")
        
        with col2:
            ebitda = ebitda_for_month(fixtures_dir=fixtures_path, month=intent.month)
            st.metric("EBITDA (proxy)", f"${ebitda:,.0f}")
        
        # Data table
        with st.expander("📋 View Data"):
            df_display = df.copy()
            df_display['usd'] = df_display['usd'].apply(lambda x: f"${x:,.0f}")
            st.dataframe(df_display, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error calculating Opex breakdown: {str(e)}")


def handle_cash_runway(fixtures_path):
    """Handle cash runway queries."""
    try:
        runway = cash_runway_months(fixtures_dir=fixtures_path)
        
        st.success("✅ Cash Runway Analysis")
        
        if np.isnan(runway):
            st.warning("⚠️ Insufficient data to calculate runway (need at least 4 months of cash data).")
        elif np.isinf(runway):
            st.info("📈 Cash is **increasing or stable** — runway is effectively unlimited.")
            st.metric("Cash Runway", "∞ months", delta="Positive trend")
        elif runway == 0:
            st.error("🚨 Current cash balance is zero or negative.")
            st.metric("Cash Runway", "0 months")
        else:
            st.metric(
                "Cash Runway",
                f"{runway:.1f} months",
                delta=None
            )
            
            # Color-coded status
            if runway < 3:
                st.error(f"⚠️ **Critical:** Only {runway:.1f} months of runway remaining.")
            elif runway < 6:
                st.warning(f"⚠️ **Caution:** {runway:.1f} months of runway remaining.")
            else:
                st.success(f"✅ **Healthy:** {runway:.1f} months of runway.")
        
    except Exception as e:
        st.error(f"Error calculating cash runway: {str(e)}")


if __name__ == "__main__":
    main()