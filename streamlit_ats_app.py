# Streamlit ATS Tool User Interface
# Complete UI for AI-powered ATS analysis

import streamlit as st
import json
import time
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
import base64

# Import your ATS tool classes (make sure the previous code is in a file called 'ats_tool.py')
try:
    from utils.ats_tool import ATSAnalyzer, save_results_to_json, load_results_from_json
except ImportError:
    st.error("Please make sure 'ats_tool.py' file is in the same directory!")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="AI-Powered ATS Tool",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .score-container {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    .success-score {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
    }
    .warning-score {
        background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .improvement-item {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #ffc107;
        margin: 0.5rem 0;
    }
    .strength-item {
        background: #d4edda;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

def create_score_gauge(score, title):
    """Create a gauge chart for scores"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 24}},
        delta = {'reference': 90, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 60], 'color': 'lightgray'},
                {'range': [60, 80], 'color': 'yellow'},
                {'range': [80, 90], 'color': 'orange'},
                {'range': [90, 100], 'color': 'green'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=400,
        font={'color': "darkblue", 'family': "Arial"}
    )
    return fig

def create_category_chart(category_scores):
    """Create a bar chart for category scores"""
    categories = list(category_scores.keys())
    scores = list(category_scores.values())
    
    fig = px.bar(
        x=categories,
        y=scores,
        title="Category Breakdown",
        labels={'x': 'Categories', 'y': 'Scores'},
        color=scores,
        color_continuous_scale='RdYlGn'
    )
    
    fig.update_layout(
        xaxis_title="Categories",
        yaxis_title="Score",
        yaxis=dict(range=[0, 100]),
        height=400
    )
    
    fig.add_hline(y=90, line_dash="dash", line_color="red", 
                  annotation_text="Target Score (90%)", annotation_position="top right")
    
    return fig

def display_results(results):
    """Display comprehensive ATS analysis results"""
    
    if results.get('status') != 'success':
        st.error(f"Analysis failed: {results.get('error_message', 'Unknown error')}")
        return
    
    ats_analysis = results.get('ats_analysis', {})
    overall_score = ats_analysis.get('overall_score', 0)
    readiness_status = ats_analysis.get('readiness_status', 'UNKNOWN')
    
    # Main score display
    st.markdown("<h2 style='text-align: center;'>📊 ATS Analysis Results</h2>", unsafe_allow_html=True)
    
    # Score container with dynamic styling
    score_class = "success-score" if overall_score >= 90 else "warning-score"
    st.markdown(f"""
    <div class="score-container {score_class}">
        <h1>{overall_score:.1f}/100</h1>
        <h3>Overall ATS Score</h3>
        <p><strong>Status: {readiness_status}</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Two columns for visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Overall score gauge
        gauge_fig = create_score_gauge(overall_score, "Overall ATS Score")
        st.plotly_chart(gauge_fig, use_container_width=True)
    
    with col2:
        # Category breakdown
        category_scores = ats_analysis.get('category_scores', {})
        if category_scores:
            category_fig = create_category_chart(category_scores)
            st.plotly_chart(category_fig, use_container_width=True)
    
    # Detailed Analysis Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Strengths & Gaps", "🎯 Improvement Plan", "📋 Detailed Analysis", "📄 Extracted Data"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ✅ Strengths")
            strengths = ats_analysis.get('strengths', [])
            if strengths:
                for strength in strengths:
                    st.markdown(f"""
                    <div class="strength-item">
                        <strong>✓</strong> {strength}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No specific strengths identified.")
        
        with col2:
            st.markdown("### ⚠️ Areas for Improvement")
            gaps = ats_analysis.get('gaps', [])
            if gaps:
                for gap in gaps:
                    st.markdown(f"""
                    <div class="improvement-item">
                        <strong>⚠</strong> {gap}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("No major gaps identified!")
        
        # Missing skills
        missing_skills = ats_analysis.get('missing_skills', [])
        if missing_skills:
            st.markdown("### 🔧 Missing Skills")
            skills_text = ", ".join(missing_skills)
            st.warning(f"Consider adding these skills: {skills_text}")
    
    with tab2:
        st.markdown("### 📈 Improvement Plan")
        improvement_plan = results.get('improvement_plan')
        
        if improvement_plan and overall_score < 90:
            # Priority Improvements
            priority_improvements = improvement_plan.get('priority_improvements', [])
            if priority_improvements:
                st.markdown("#### 🎯 Priority Improvements")
                for i, improvement in enumerate(priority_improvements, 1):
                    with st.expander(f"{i}. {improvement.get('skill', 'Unknown Skill')} - {improvement.get('time_estimate', 'TBD')}"):
                        st.write(f"**Category:** {improvement.get('category', 'N/A')}")
                        st.write(f"**Current Level:** {improvement.get('current_level', 'N/A')}")
                        st.write(f"**Target Level:** {improvement.get('target_level', 'N/A')}")
                        
                        learning_path = improvement.get('learning_path', [])
                        if learning_path:
                            st.write("**Learning Path:**")
                            for step in learning_path:
                                st.write(f"• {step}")
                        
                        resources = improvement.get('resources', [])
                        if resources:
                            st.write("**Recommended Resources:**")
                            for resource in resources:
                                st.write(f"• **{resource.get('title', 'N/A')}** - {resource.get('provider', 'N/A')} ({resource.get('duration', 'N/A')})")
            
            # Quick Wins
            quick_wins = improvement_plan.get('quick_wins', [])
            if quick_wins:
                st.markdown("#### ⚡ Quick Wins")
                for win in quick_wins:
                    st.success(f"**{win.get('action', 'N/A')}** - {win.get('time_required', 'N/A')} (Impact: {win.get('impact', 'N/A')})")
                    st.write(win.get('description', ''))
            
            # Timeline
            timeline = improvement_plan.get('timeline', {})
            if timeline:
                st.markdown("#### 📅 Timeline")
                for period, actions in timeline.items():
                    st.write(f"**{period.replace('_', ' ').title()}:**")
                    for action in actions:
                        st.write(f"• {action}")
        
        elif overall_score >= 90:
            st.success("🎉 Great job! Your resume is ATS-ready. You can proceed with interview preparation!")
        else:
            st.warning("No improvement plan generated. Please try analyzing again.")
    
    with tab3:
        st.markdown("### 📊 Detailed Analysis")
        detailed_analysis = ats_analysis.get('detailed_analysis', {})
        
        if detailed_analysis:
            for key, value in detailed_analysis.items():
                if value:
                    st.markdown(f"#### {key.replace('_', ' ').title()}")
                    st.write(value)
                    st.markdown("---")
        
        # Category scores breakdown
        st.markdown("#### Category Scores Breakdown")
        if category_scores:
            for category, score in category_scores.items():
                st.markdown(f"""
                <div class="metric-card">
                    <strong>{category.replace('_', ' ').title()}:</strong> {score}/100
                </div>
                """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### 📄 Extracted Data")
        
        # Resume data
        resume_data = results.get('resume_data', {})
        job_data = results.get('job_data', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Resume Information")
            
            # Personal info
            personal_info = resume_data.get('personal_info', {})
            if any(personal_info.values()):
                st.write("**Contact Information:**")
                for key, value in personal_info.items():
                    if value:
                        st.write(f"• {key.title()}: {value}")
            
            # Skills
            skills = resume_data.get('skills', [])
            if skills:
                st.write("**Skills:**")
                st.write(", ".join(skills))
            
            # Experience
            experiences = resume_data.get('experiences', [])
            if experiences:
                st.write("**Experience:**")
                for exp in experiences[:3]:  # Show first 3
                    st.write(f"• {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}")
        
        with col2:
            st.markdown("#### Job Requirements")
            
            st.write(f"**Position:** {job_data.get('title', 'N/A')}")
            st.write(f"**Company:** {job_data.get('company', 'N/A')}")
            st.write(f"**Experience Level:** {job_data.get('experience_level', 'N/A')}")
            
            required_skills = job_data.get('required_skills', [])
            if required_skills:
                st.write("**Required Skills:**")
                st.write(", ".join(required_skills))
            
            preferred_skills = job_data.get('preferred_skills', [])
            if preferred_skills:
                st.write("**Preferred Skills:**")
                st.write(", ".join(preferred_skills))

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown("<h1 class='main-header'>🤖 AI-Powered ATS Tool</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #666;'>Optimize your resume for Applicant Tracking Systems with AI-powered analysis</p>", unsafe_allow_html=True)
    
    # Sidebar for API key and settings
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # API Key input
        gemini_api_key = st.text_input(
            "🔑 Gemini API Key",
            type="password",
            help="Enter your Google Gemini API key",
            placeholder="Enter your API key here..."
        )
        
        if not gemini_api_key:
            st.warning("Please enter your Gemini API key to proceed.")
            st.markdown("### How to get API key:")
            st.markdown("1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)")
            st.markdown("2. Sign in with Google account")
            st.markdown("3. Click 'Create API Key'")
            st.markdown("4. Copy and paste here")
            return
        
        st.success("✅ API Key configured!")
        
        # Additional settings
        st.markdown("### 📊 Analysis Settings")
        show_detailed_scores = st.checkbox("Show detailed category scores", value=True)
        show_improvement_plan = st.checkbox("Generate improvement plan", value=True)
        
        # Export options
        st.markdown("### 💾 Export Options")
        export_format = st.selectbox("Export results as:", ["JSON", "PDF Report"])
    
    # Main content area
    if not st.session_state.analysis_complete:
        # Input section
        st.markdown("## 📄 Upload Resume & Job Description")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📎 Upload Resume (PDF)")
            uploaded_file = st.file_uploader(
                "Choose a PDF file",
                type=['pdf'],
                help="Upload your resume in PDF format"
            )
            
            if uploaded_file:
                st.success(f"✅ Resume uploaded: {uploaded_file.name}")
                
                # Show file details
                file_details = {
                    "Filename": uploaded_file.name,
                    "File size": f"{uploaded_file.size / 1024:.1f} KB",
                    "File type": uploaded_file.type
                }
                st.json(file_details)
        
        with col2:
            st.markdown("### 📝 Job Description")
            job_description = st.text_area(
                "Paste the job description here",
                height=300,
                placeholder="Paste the complete job description including required skills, responsibilities, and qualifications...",
                help="Include the complete job posting for better analysis"
            )
            
            if job_description:
                word_count = len(job_description.split())
                st.info(f"📊 Word count: {word_count} words")
        
        # Analysis button and progress
        if uploaded_file and job_description and gemini_api_key:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Analyze Resume", type="primary", use_container_width=True):
                    # Initialize analyzer
                    analyzer = ATSAnalyzer(gemini_api_key)
                    
                    # Progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        # Step 1: Initialize
                        status_text.text("🔄 Initializing analysis...")
                        progress_bar.progress(10)
                        time.sleep(1)
                        
                        # Step 2: Process resume
                        status_text.text("📄 Extracting resume data...")
                        progress_bar.progress(30)
                        
                        # Process the analysis
                        results = analyzer.process_resume_and_job(uploaded_file, job_description)
                        progress_bar.progress(60)
                        
                        # Step 3: Calculate scores
                        status_text.text("🧮 Calculating ATS scores...")
                        progress_bar.progress(80)
                        time.sleep(1)
                        
                        # Step 4: Generate recommendations
                        status_text.text("💡 Generating recommendations...")
                        progress_bar.progress(100)
                        time.sleep(1)
                        
                        # Store results
                        st.session_state.results = results
                        st.session_state.analysis_complete = True
                        
                        # Clear progress indicators
                        progress_bar.empty()
                        status_text.empty()
                        
                        # Show success message
                        st.success("🎉 Analysis completed successfully!")
                        time.sleep(1)
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")
                        progress_bar.empty()
                        status_text.empty()
        
        elif not uploaded_file or not job_description:
            st.info("👆 Please upload a resume and enter a job description to start the analysis.")
    
    else:
        # Show results
        if st.session_state.results:
            # Back button
            if st.button("← New Analysis", type="secondary"):
                st.session_state.analysis_complete = False
                st.session_state.results = None
                st.rerun()
            
            # Display results
            display_results(st.session_state.results)
            
            # Export functionality
            if st.session_state.results.get('status') == 'success':
                st.markdown("## 💾 Export Results")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📄 Download JSON Report", use_container_width=True):
                        json_str = json.dumps(st.session_state.results, indent=2)
                        st.download_button(
                            label="💾 Download JSON",
                            data=json_str,
                            file_name=f"ats_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                
                with col2:
                    if st.button("📊 Generate Summary Report", use_container_width=True):
                        # Generate a summary report
                        ats_analysis = st.session_state.results.get('ats_analysis', {})
                        summary_report = f"""
# ATS Analysis Summary Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overall Score: {ats_analysis.get('overall_score', 0):.1f}/100
Status: {ats_analysis.get('readiness_status', 'Unknown')}

## Category Scores:
{chr(10).join([f"- {k.replace('_', ' ').title()}: {v}/100" for k, v in ats_analysis.get('category_scores', {}).items()])}

## Strengths:
{chr(10).join([f"- {s}" for s in ats_analysis.get('strengths', [])])}

## Areas for Improvement:
{chr(10).join([f"- {g}" for g in ats_analysis.get('gaps', [])])}

## Missing Skills:
{', '.join(ats_analysis.get('missing_skills', []))}
                        """
                        
                        st.download_button(
                            label="📄 Download Summary",
                            data=summary_report,
                            file_name=f"ats_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )

if __name__ == "__main__":
    main()

# Requirements for Streamlit app:
# """
# pip install streamlit plotly google-generativeai PyPDF2 pdfplumber spacy nltk scikit-learn pandas numpy

# # Run the app:
# streamlit run streamlit_ats_app.py
# """
