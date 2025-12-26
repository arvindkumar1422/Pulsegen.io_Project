import streamlit as st
import json
from src.crawler import Crawler
from src.extractor import Extractor
from src.visualizer import create_graph
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Pulse Module Extractor",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4F8BF9;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4F8BF9;
        color: white;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🧬 Pulse - Module Extraction AI Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Extract structured modules and submodules from any documentation URL.</div>', unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_key_status = "✅ Loaded" if os.getenv("OPENAI_API_KEY") else "❌ Not Found"
    st.info(f"API Key Status: {api_key_status}")
    if not os.getenv("OPENAI_API_KEY"):
        st.warning("Running in Mock Mode. Add OPENAI_API_KEY to .env for live extraction.")

    model_name = st.selectbox("AI Model", ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"], index=0)
    max_depth = st.slider("Crawl Depth", min_value=1, max_value=3, value=1, help="How deep to crawl links.")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This tool uses AI to analyze documentation and extract a structured hierarchy of modules.")
    
    st.markdown("---")
    st.markdown("### 📖 User Manual")
    with st.expander("How to use"):
        st.markdown("""
        1. **Enter URLs**: Paste documentation URLs in the main text area (one per line).
        2. **Configure**: 
           - Select AI Model (GPT-4o recommended).
           - Set Crawl Depth (1 = just the page, 2 = follow links once).
        3. **Start**: Click 'Start Extraction'.
        4. **Analyze**: View the extracted modules, hierarchy graph, and statistics.
        5. **Download**: Get the full report in JSON or Markdown format.
        """)
    
    st.markdown("---")
    st.info("⚠️ **Note**: Ensure you have permission to crawl the target sites. API costs apply.")

# Main input area
col1, col2 = st.columns([3, 1])
with col1:
    url_input = st.text_area("Enter Documentation URL(s) (one per line)", height=100, placeholder="https://help.instagram.com\nhttps://support.stripe.com")
with col2:
    st.markdown("<br>", unsafe_allow_html=True) # Spacer
    process_btn = st.button("🚀 Start Extraction", type="primary")

if process_btn:
    if not url_input:
        st.error("Please enter at least one URL.")
    else:
        urls = [url.strip() for url in url_input.split('\n') if url.strip()]
        
        # Progress tracking
        status_container = st.status("Processing...", expanded=True)
        
        try:
            # Step 1: Crawling
            status_container.write("🕷️ Crawling documentation pages...")
            crawler = Crawler(urls, max_depth=max_depth)
            crawler.crawl()
            content_map = crawler.get_content()
            
            if not content_map:
                status_container.update(label="Crawling failed!", state="error")
                st.error("No content could be crawled. Please check the URLs.")
                st.stop()
                
            status_container.write(f"✅ Crawled {len(content_map)} pages successfully.")
            
            # Step 2: Extraction
            status_container.write("🧠 Analyzing content with AI...")
            
            # Combine content (smart truncation could be added here)
            full_text = "\n\n".join(content_map.values())
            st.info(f"Total content length to analyze: {len(full_text)} characters")
            
            extractor = Extractor(model=model_name)
            modules = extractor.extract(full_text)
            
            status_container.update(label="Extraction Complete!", state="complete", expanded=False)
            
            if modules:
                st.success("🎉 Extraction successful!")
                
                # Metrics
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("Modules Found", len(modules))
                with m2:
                    total_subs = sum(len(m.get('Submodules', {})) for m in modules)
                    st.metric("Submodules Found", total_subs)
                with m3:
                    avg_conf = sum(m.get('confidence_score', 0) for m in modules) / len(modules) if modules else 0
                    st.metric("Avg Confidence", f"{avg_conf:.2%}")

                # Charts
                st.markdown("### 📈 Analytics")
                chart_data = {
                    "Module": [m.get('module', 'Unknown') for m in modules],
                    "Submodules Count": [len(m.get('Submodules', {})) for m in modules]
                }
                st.bar_chart(chart_data, x="Module", y="Submodules Count", color="#4F8BF9")

                # Tabs for different views
                tab1, tab2, tab3 = st.tabs(["📊 Visualization", "📑 Structured View", "💾 Export"])
                
                with tab1:
                    st.markdown("### Module Hierarchy Graph")
                    try:
                        graph = create_graph(modules)
                        st.graphviz_chart(graph, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not generate graph: {e}")

                with tab2:
                    for mod in modules:
                        with st.expander(f"📦 {mod.get('module', 'Unknown')}"):
                            st.markdown(f"**Description:** {mod.get('Description', '')}")
                            st.markdown(f"**Confidence:** {mod.get('confidence_score', 'N/A')}")
                            st.divider()
                            st.markdown("**Submodules:**")
                            for sub, desc in mod.get('Submodules', {}).items():
                                st.markdown(f"- **{sub}**: {desc}")
                
                with tab3:
                    st.markdown("### Download Reports")
                    
                    # JSON Download
                    json_data = json.dumps(modules, indent=2)
                    st.download_button(
                        label="📥 Download JSON Data",
                        data=json_data,
                        file_name="pulse_modules.json",
                        mime="application/json"
                    )
                    
                    # Markdown Report Generation
                    def generate_markdown_report(modules):
                        report = f"# Pulse Module Extraction Report\n\n"
                        report += f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        report += f"## Summary\n"
                        report += f"- **Total Modules:** {len(modules)}\n"
                        report += f"- **Total Submodules:** {sum(len(m.get('Submodules', {})) for m in modules)}\n\n"
                        report += "## Detailed Breakdown\n\n"
                        
                        for mod in modules:
                            report += f"### 📦 {mod.get('module', 'Unknown')}\n"
                            report += f"**Description:** {mod.get('Description', 'N/A')}\n\n"
                            report += f"**Confidence Score:** {mod.get('confidence_score', 'N/A')}\n\n"
                            report += "**Submodules:**\n"
                            for sub, desc in mod.get('Submodules', {}).items():
                                report += f"- **{sub}**: {desc}\n"
                            report += "\n---\n\n"
                        return report

                    md_report = generate_markdown_report(modules)
                    st.download_button(
                        label="📄 Download Full Report (Markdown)",
                        data=md_report,
                        file_name="pulse_report.md",
                        mime="text/markdown"
                    )
            else:
                st.error("Failed to extract modules. The AI model might have returned an empty result.")
                
        except Exception as e:
            status_container.update(label="An error occurred", state="error")
            st.error(f"An unexpected error occurred: {str(e)}")
            if "401" in str(e):
                st.error("Authentication Error: Please check your OpenAI API Key in .env")
            elif "429" in str(e):
                st.error("Rate Limit Error: You have exceeded your OpenAI quota.")
            elif "404" in str(e):
                st.error(f"Model Error: The model '{model_name}' does not exist or you do not have access to it.")

