import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from fuzzywuzzy import process
import google.generativeai as genai
import os

# Configure Gemini API
genai.configure(api_key='AIzaSyDuQyV6BHWspf-bNyYR9RwXPM_vklv7Ww4')
model = genai.GenerativeModel('gemini-pro')


def generate_single_company_analysis(company_data):
    """Generate comprehensive AI analysis for investment decisions"""
    high_variance = company_data['variance'] > 7
    high_sentiment = company_data['hype_score'] > 7

    status = ""
    if high_sentiment and high_variance:
        status = "**HIGH ATTENTION ALERT:** This stock shows significant social media interest with highly divided opinions. Consider this alongside technical analysis and fundamentals.\n\n"
    elif high_sentiment:
        status = "**HIGH SENTIMENT ALERT:** Strong positive sentiment detected. Validate against fundamental metrics before making investment decisions.\n\n"
    elif high_variance:
        status = "**HIGH VARIANCE ALERT:** Divided market opinions suggest careful analysis of fundamental indicators is crucial.\n\n"

    prompt = f"""
    Provide an investment analysis supplementing traditional metrics for:
    Company: {company_data['company']} ({company_data['ticker']})
    WallStreetBets Sentiment Score: {company_data['hype_score']}/10
    Opinion Variance: {min(company_data['variance'], 10)}/10

    {status}
    # Investment Analysis Supplement for {company_data['ticker']}

    ## 1. Social Sentiment Context
    - **Current Sentiment Level:** {company_data['hype_score']}/10
    - **Opinion Division:** {min(company_data['variance'], 10)}/10
    - **Market Psychology Impact:** Analyze how these metrics could affect traditional valuation

    ## 2. Investment Strategy Integration
    - How to combine this sentiment data with fundamental analysis
    - Recommended technical indicators to monitor
    - Volume and volatility expectations based on sentiment

    ## 3. Risk Management
    - Sentiment-based volatility risks
    - Position sizing considerations
    - Stop-loss placement suggestions

    ## 4. Portfolio Integration
    - Suggested portfolio allocation considering sentiment
    - Complementary positions to balance risk
    - Alternative investments in the same sector

    Focus on practical ways to use this sentiment data alongside traditional investment metrics.
    """
    response = model.generate_content(prompt)
    return response.text


def generate_comparative_analysis(company1_data, company2_data):
    """Generate portfolio balancing analysis for two companies"""
    prompt = f"""
    Provide a comparative investment analysis for portfolio balancing:

    Company 1: {company1_data['company']} ({company1_data['ticker']})
    - Sentiment Score: {company1_data['hype_score']}/10
    - Opinion Variance: {min(company1_data['variance'], 10)}/10

    Company 2: {company2_data['company']} ({company2_data['ticker']})
    - Sentiment Score: {company2_data['hype_score']}/10
    - Opinion Variance: {min(company2_data['variance'], 10)}/10

    ## 1. Correlation Analysis
    - Sentiment correlation assessment
    - Portfolio diversification potential
    - Risk-reward balance opportunities

    ## 2. Portfolio Allocation Recommendation
    - Suggested allocation ratio between these stocks
    - Risk balancing approach
    - Sector exposure considerations

    ## 3. Risk Management Strategy
    - Combined position sizing recommendations
    - Hedging opportunities
    - Stop-loss strategy for the pair

    ## 4. Supplementary Investments
    - Additional stocks to consider for balance
    - Sector ETFs for risk management
    - Alternative investments to consider

    Format as a clear investment strategy guide that combines sentiment data with traditional investment approach.
    """
    response = model.generate_content(prompt)
    return response.text


def generate_multi_company_analysis(companies_data):
    """Generate basket trading and portfolio analysis"""
    companies_info = "\n".join([
        f"Company: {data['company']} ({data['ticker']})\n"
        f"Sentiment Score: {data['hype_score']}/10\n"
        f"Opinion Variance: {min(data['variance'], 10)}/10\n"
        for data in companies_data
    ])

    prompt = f"""
    Create a comprehensive basket trading strategy for:

    {companies_info}

    ## 1. Portfolio Construction
    - Optimal allocation percentages for each stock
    - Risk-weighted portfolio balance
    - Sector diversification analysis

    ## 2. Risk Management Framework
    - Portfolio beta considerations
    - Volatility management strategy
    - Stop-loss framework for the basket

    ## 3. Additional Recommendations
    - Complementary stocks to consider
    - ETFs for sector balance
    - Alternative investments for risk management

    ## 4. Implementation Strategy
    - Entry point considerations
    - Position sizing recommendations
    - Rebalancing framework
    - Performance monitoring metrics

    Format as an actionable portfolio strategy that combines sentiment data with traditional investment metrics.
    Provide specific allocation percentages and clear risk management guidelines.
    """
    response = model.generate_content(prompt)
    return response.text

def create_square_plot(plot_df):
    """Create a square plot showing sentiment vs variance"""
    fig = go.Figure()

    # Add quadrant lines
    fig.add_hline(y=5, line=dict(color="gray", width=1, dash="dot"), opacity=0.3)
    fig.add_vline(x=5, line=dict(color="gray", width=1, dash="dot"), opacity=0.3)

    # Add scatter points
    for _, row in plot_df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['variance']],
            y=[row['hype_score']],
            mode='markers+text',
            name=row['ticker'],
            text=[row['ticker']],
            textposition='top center',
            marker=dict(size=12, symbol='circle'),
            showlegend=True
        ))

    # Update layout for square aspect ratio and clean design
    fig.update_layout(
        width=500,
        height=500,
        plot_bgcolor='white',
        title=dict(
            text='Sentiment Score vs Opinion Variance Analysis',
            x=0.5,
            y=0.95
        ),
        xaxis=dict(
            title='Opinion Variance',
            range=[0, 10],
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            title='Sentiment Score',
            range=[0, 10],
            showgrid=False,
            zeroline=False
        ),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.05
        ),
        margin=dict(l=50, r=50, t=50, b=50)
    )

    return fig


# Set page config
st.set_page_config(page_title="Social Sentiment Analyzer", page_icon="📊", layout="wide")

# Custom CSS
st.markdown("""
    <style>
        .title {
            font-family: 'Helvetica Neue', sans-serif;
            font-size: 42px;
            font-weight: bold;
            color: #1E3D59;
            text-align: center;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .subtitle {
            font-size: 18px;
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .company-card {
            background: white;
            border-radius: 8px;
            padding: 12px 18px;
            margin-bottom: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        .company-card:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .plot-container {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 20px auto;
        }
        .analysis-container {
            background: linear-gradient(135deg, #f6f8fa 0%, #e9ecef 100%);
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 20px auto;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_companies' not in st.session_state:
    st.session_state.selected_companies = []
if 'analysis_shown' not in st.session_state:
    st.session_state.analysis_shown = False

# App header
st.markdown('<div class="title">Social Sentiment Analyzer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Advanced stock analysis utilizing WallStreetBets sentiment data</div>',
    unsafe_allow_html=True
)


# Load data
@st.cache_data
def load_data():
    with open('data.json', 'r') as file:
        data = json.load(file)
    return pd.DataFrame(data)


df = load_data()

# Create columns for controls
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    search_query = st.text_input("Search companies", placeholder="Enter company name or ticker...")

with col2:
    sort_option = st.selectbox(
        "Sort by",
        ["Alphabetical (A-Z)", "Alphabetical (Z-A)",
         "Sentiment Score (High to Low)", "Sentiment Score (Low to High)"]
    )

with col3:
    items_per_page = st.selectbox("Items per page", [10, 20, 50, 100], index=1)

# Sort data
if sort_option == "Alphabetical (A-Z)":
    df = df.sort_values("company")
elif sort_option == "Alphabetical (Z-A)":
    df = df.sort_values("company", ascending=False)
elif sort_option == "Sentiment Score (High to Low)":
    df = df.sort_values("hype_score", ascending=False)
else:
    df = df.sort_values("hype_score")

# Fuzzy search
if search_query:
    choices = df['company'].tolist() + df['ticker'].tolist()
    matches = process.extract(search_query, choices, limit=len(choices))
    matched = [match[0] for match in matches if match[1] >= 60]
    df = df[df['company'].isin(matched) | df['ticker'].isin(matched)]

# Pagination
total_pages = max((len(df) - 1) // items_per_page + 1, 1)
page_number = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
start_idx = (page_number - 1) * items_per_page
end_idx = min(start_idx + items_per_page, len(df))

# Display companies
for _, row in df.iloc[start_idx:end_idx].iterrows():
    cols = st.columns([4, 1, 1])

    sentiment_color = f"rgb({int(255 * (1 - row['hype_score'] / 10))}, {int(255 * (row['hype_score'] / 10))}, 100)"

    cols[0].markdown(f"""
        <div class='company-card' style='border-left: 6px solid {sentiment_color}'>
            <span style='font-weight: 500'>{row['company']} ({row['ticker']})</span><br>
            <span style='font-size: 0.9em; color: #666;'>Sentiment: {row['hype_score']:.1f} | Variance: {min(row['variance'], 10):.1f}</span>
        </div>
    """, unsafe_allow_html=True)

    cols[1].markdown(f"""
        <div style='padding: 12px; text-align: center; font-weight: 500;'>
    Score: {row['hype_score']:.1f}
            </div>
        """, unsafe_allow_html=True)

    if cols[2].checkbox("Select", key=row['ticker'],
                        value=row['ticker'] in st.session_state.selected_companies):
        if row['ticker'] not in st.session_state.selected_companies:
            st.session_state.selected_companies.append(row['ticker'])
    elif row['ticker'] in st.session_state.selected_companies:
        st.session_state.selected_companies.remove(row['ticker'])

# Analysis section
col1, col2, col3 = st.columns([4, 1, 1])

with col2:
    if st.button("Reset", use_container_width=True):
        st.session_state.clear()
        st.rerun()

with col3:
    analyze = st.button("Analyze", use_container_width=True,
                        disabled=st.session_state.get('analysis_shown', False))

if analyze and st.session_state.selected_companies:
    st.session_state.analysis_shown = True

    # Plot visualization
    center_col1, center_col2, center_col3 = st.columns([1, 2, 1])
    with center_col2:
        plot_df = df[df['ticker'].isin(st.session_state.selected_companies)]
        fig = create_square_plot(plot_df)
        st.plotly_chart(fig, config={'displayModeBar': False})

        # Auto-scroll to plot
        st.markdown("""
                <script>
                    const plots = window.document.getElementsByClassName('plotly-graph-div');
                    if (plots.length > 0) {
                        plots[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                </script>
                """, unsafe_allow_html=True)

    # AI Analysis
    st.markdown("<div class='analysis-container'>", unsafe_allow_html=True)
    with st.spinner("Generating AI analysis..."):
        if len(st.session_state.selected_companies) == 1:
            ticker = st.session_state.selected_companies[0]
            company_data = df[df["ticker"] == ticker].iloc[0].to_dict()
            analysis = generate_single_company_analysis(company_data)
            st.markdown(analysis)

        elif len(st.session_state.selected_companies) == 2:
            ticker1, ticker2 = st.session_state.selected_companies
            company1_data = df[df["ticker"] == ticker1].iloc[0].to_dict()
            company2_data = df[df["ticker"] == ticker2].iloc[0].to_dict()
            analysis = generate_comparative_analysis(company1_data, company2_data)
            st.markdown(analysis)

        else:
            companies_data = [
                df[df["ticker"] == ticker].iloc[0].to_dict()
                for ticker in st.session_state.selected_companies
            ]
            analysis = generate_multi_company_analysis(companies_data)
            st.markdown(analysis)
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style='text-align: center; padding: 2rem; margin-top: 3rem; border-top: 1px solid #E2E8F0;'>
        <h3 style='color: #1E3D59;'>Development Team</h3>
        <div style='margin: 0.5rem 0;'>Jai Nana (Case Western '28)</div>
        <div style='margin: 0.5rem 0;'>Richard Sebek (Georgia Tech Masters '26)</div>
        <div style='margin: 0.5rem 0;'>Keval Patel (Brandeis '28)</div>
    </div>
    """, unsafe_allow_html=True)