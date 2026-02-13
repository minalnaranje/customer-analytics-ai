import streamlit as st
import pandas as pd
import openai
import json
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Load API key from environment
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    st.error("⚠️ OpenAI API key not found in .env file")
    st.stop()

# Page config
st.set_page_config(
    page_title="Customer Analytics AI",
    page_icon="🎯",
    layout="wide"
)

# Title and description
st.title("🎯 Customer Analytics Intelligence")
st.markdown("**AI-powered strategic recommendations from your customer data**")

# Sidebar - About
with st.sidebar:
    st.header("About")
    st.markdown("""
    Upload your customer CSV and get instant strategic recommendations.
    
    **What it does:**
    - Analyzes customer segmentation
    - Identifies business opportunities
    - Generates prioritized recommendations
    
    **Who it's for:**
    - Small business teams
    - Product managers
    - Marketing strategists
    
    **Tech Stack:**
    - Streamlit
    - n8n workflow automation
    - OpenAI GPT-3.5-Turbo
    - Python/Pandas
    
    **Created by:** Minal Naranje  
    📧 naranje.m@northeastern.edu  
    🔗 [Portfolio](https://yourportfolio.com)
    """)

# Main content
st.header("📊 Upload Your Data")

st.markdown("Upload your merged customer data CSV:")

uploaded_file = st.file_uploader(
    "📊 Customer Analytics Data",
    type=['csv'],
    help="Merged CSV containing customer, product, and demographic data"
)

# Example data format
with st.expander("📋 See Expected CSV Format"):
    st.markdown("""
    Your CSV should include these columns:
    - `customer_id`, `age`, `gender`, `country`, `loyalty_tier`
    - `product_id`, `category`, `brand`, `base_price`
    - `country_population`, `country_facebook_percent`
    - `is_premium`
    """)

# Process button
if uploaded_file:
    if st.button("🚀 Generate Recommendations", type="primary"):
        
        with st.spinner("Analyzing customer data..."):
            
            try:
                # Read merged CSV
                df = pd.read_csv(uploaded_file)
                
                # Validate data
                if len(df) == 0:
                    st.error("CSV file is empty!")
                    st.stop()
                
                st.success(f"✅ Loaded {len(df)} customer records")
                
                # Aggregate metrics
                total_records = len(df)
                
                # Loyalty distribution
                if 'loyalty_tier' in df.columns:
                    loyalty_dist = df['loyalty_tier'].value_counts().to_dict()
                else:
                    loyalty_dist = {}
                
                # Premium ratio
                if 'is_premium' in df.columns:
                    premium_ratio = df['is_premium'].mean()
                else:
                    premium_ratio = 0
                
                # Top countries
                if 'country' in df.columns:
                    top_countries = df['country'].value_counts().head(3).to_dict()
                else:
                    top_countries = {}
                
                # Average price
                if 'base_price' in df.columns:
                    avg_price = df['base_price'].mean()
                else:
                    avg_price = 0
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Customers", total_records)
                with col2:
                    st.metric("Premium Ratio", f"{premium_ratio*100:.1f}%")
                with col3:
                    if loyalty_dist:
                        st.metric("Top Tier", max(loyalty_dist, key=loyalty_dist.get))
                with col4:
                    st.metric("Avg Price", f"${avg_price:.2f}")
                
                # Show loyalty distribution
                if loyalty_dist:
                    st.subheader("📊 Loyalty Distribution")
                    st.bar_chart(loyalty_dist)
                
                # Prepare prompt for OpenAI
                prompt = f"""Analyze this customer data and provide 3 strategic recommendations.

DATA:
- Total Customers: {total_records}
- Loyalty Tiers: {json.dumps(loyalty_dist)}
- Premium Ratio: {premium_ratio:.2%}
- Top Countries: {json.dumps(top_countries)}
- Average Price: ${avg_price:.2f}

Respond in JSON format only:
{{
  "recommendations": [
    {{
      "priority": "High|Medium|Low",
      "action": "specific action to take",
      "target": "which customer segment",
      "expected_impact": "quantified outcome",
      "rationale": "why this works"
    }}
  ]
}}"""
                
                # Call OpenAI
                st.info("🤖 Generating AI recommendations...")
                
                client = openai.OpenAI(api_key=api_key)
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                
                # Parse response
                ai_response = response.choices[0].message.content
                
                # Clean response (remove markdown if present)
                ai_response = ai_response.strip()
                if ai_response.startswith("```json"):
                    ai_response = ai_response.replace("```json", "").replace("```", "")
                
                recommendations = json.loads(ai_response)
                
                # Display recommendations
                st.success("✅ Analysis Complete!")
                st.header("🎯 Strategic Recommendations")
                
                for i, rec in enumerate(recommendations.get('recommendations', []), 1):
                    priority = rec.get('priority', 'Medium')
                    
                    # Color based on priority
                    if priority == 'High':
                        color = "🔴"
                        bg_color = "#ffebee"
                        border_color = "#e74c3c"
                    elif priority == 'Medium':
                        color = "🟡"
                        bg_color = "#fff8e1"
                        border_color = "#f39c12"
                    else:
                        color = "🔵"
                        bg_color = "#e3f2fd"
                        border_color = "#3498db"
                    
                    with st.container():
                     st.markdown(f"""
    <div style="background-color: {bg_color}; padding: 20px; border-radius: 10px; margin: 10px 0; border-left: 4px solid {border_color}; color: #000000;">
    <h3 style="color: #000000;">{color} Recommendation {i}: {rec.get('action', 'N/A')}</h3>
    <p style="color: #000000;"><strong>Priority:</strong> {priority}</p>
    <p style="color: #000000;"><strong>Target:</strong> {rec.get('target', 'N/A')}</p>
    <p style="color: #000000;"><strong>Expected Impact:</strong> {rec.get('expected_impact', 'N/A')}</p>
    <p style="color: #000000;"><strong>Why:</strong> {rec.get('rationale', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)
                
                # Download report
                st.divider()
                
                # Generate HTML report
                html_report = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Customer Analytics Report</title>
    <style>
        body {{ font-family: Arial; padding: 40px; background: #f5f5f5; }}
        .header {{ background: #667eea; color: white; padding: 30px; border-radius: 10px; }}
        .metric {{ display: inline-block; margin: 20px; }}
        .rec {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #667eea; }}
        .high {{ border-left-color: #e74c3c; }}
        .medium {{ border-left-color: #f39c12; }}
        .low {{ border-left-color: #3498db; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Customer Analytics Report</h1>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
    
    <h2>📊 Key Metrics</h2>
    <div class="metric"><strong>Total Customers:</strong> {total_records}</div>
    <div class="metric"><strong>Premium Ratio:</strong> {premium_ratio*100:.1f}%</div>
    
    <h2>🎯 Strategic Recommendations</h2>
    {"".join([f'''
    <div class="rec {rec.get('priority', 'medium').lower()}">
        <h3>{i}. {rec.get('action', 'N/A')}</h3>
        <p><strong>Priority:</strong> {rec.get('priority', 'N/A')}</p>
        <p><strong>Target:</strong> {rec.get('target', 'N/A')}</p>
        <p><strong>Impact:</strong> {rec.get('expected_impact', 'N/A')}</p>
        <p><strong>Rationale:</strong> {rec.get('rationale', 'N/A')}</p>
    </div>
    ''' for i, rec in enumerate(recommendations.get('recommendations', []), 1)])}
    
</body>
</html>
"""
                
                st.download_button(
                    label="📥 Download HTML Report",
                    data=html_report,
                    file_name=f"customer_analysis_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html"
                )
                
            except json.JSONDecodeError as e:
                st.error(f"❌ Failed to parse AI response: {e}")
                st.code(ai_response)
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.exception(e)

else:
    st.info("👆 Upload your merged customer data CSV to get started")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>Built with Streamlit + OpenAI GPT-3.5-Turbo</p>
    <p>Processing time: ~2 seconds per analysis | Cost: $0.0015 per request</p>
</div>
""", unsafe_allow_html=True)