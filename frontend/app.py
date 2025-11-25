"""Streamlit frontend application."""
import streamlit as st
import requests
import json
from typing import List, Dict

# Backend API URL
API_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Autonomous QA Agent",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'test_cases' not in st.session_state:
    st.session_state.test_cases = []
if 'selected_test_case' not in st.session_state:
    st.session_state.selected_test_case = None
if 'selected_test_cases' not in st.session_state:
    st.session_state.selected_test_cases = []
if 'generated_script' not in st.session_state:
    st.session_state.generated_script = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = "📁 Knowledge Base"


def format_test_cases_as_markdown(test_cases: List[Dict]) -> str:
    """Format test cases as markdown table."""
    if not test_cases:
        return "No test cases generated."
    
    markdown = "| Test ID | Feature | Test Scenario | Expected Result | Grounded In |\n"
    markdown += "|---------|---------|---------------|-----------------|-------------|\n"
    
    for tc in test_cases:
        grounded = ", ".join(tc.get('grounded_in', []))
        markdown += f"| {tc.get('test_id', '')} | {tc.get('feature', '')} | {tc.get('test_scenario', '')} | {tc.get('expected_result', '')} | {grounded} |\n"
    
    return markdown


def show_shimmer_loading(text: str = "Generating code..."):
    """Display shimmer loading effect."""
    st.markdown(f"""
        <div class="shimmer-box">
            <h3 class="shimmer-text">{text}</h3>
        </div>
    """, unsafe_allow_html=True)


def show_skeleton_loader(lines: int = 3):
    """Display skeleton loader with shimmer effect."""
    skeleton_html = ""
    for _ in range(lines):
        skeleton_html += '<div class="loading-skeleton"></div>'
    
    st.markdown(f'<div>{skeleton_html}</div>', unsafe_allow_html=True)


def main():
    # Custom CSS for consistent red/coral theme + shimmer effect
    st.markdown("""
        <style>
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #1e1e1e;
        }
        
        /* Primary button styling - red/coral theme */
        .stButton > button[kind="primary"] {
            background-color: #ff4b4b;
            color: white;
            border: none;
        }
        
        .stButton > button[kind="primary"]:hover {
            background-color: #ff6b6b;
        }
        
        /* Info boxes */
        .stAlert {
            background-color: #2d2d2d;
        }
        
        /* Download button */
        .stDownloadButton > button {
            background-color: #ff4b4b;
            color: white;
        }
        
        .stDownloadButton > button:hover {
            background-color: #ff6b6b;
        }
        
        /* Shimmer effect for loading states */
        @keyframes shimmer {
            0% {
                background-position: -1000px 0;
            }
            100% {
                background-position: 1000px 0;
            }
        }
        
        .shimmer-text {
            display: inline-block;
            background: linear-gradient(
                90deg,
                rgba(255, 255, 255, 0.1) 0%,
                rgba(255, 255, 255, 0.3) 50%,
                rgba(255, 255, 255, 0.1) 100%
            );
            background-size: 1000px 100%;
            animation: shimmer 2s infinite linear;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .shimmer-box {
            background: linear-gradient(
                90deg,
                rgba(255, 255, 255, 0.05) 0%,
                rgba(255, 255, 255, 0.15) 50%,
                rgba(255, 255, 255, 0.05) 100%
            );
            background-size: 1000px 100%;
            animation: shimmer 2s infinite linear;
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
        }
        
        .loading-skeleton {
            background: linear-gradient(
                90deg,
                #262730 0%,
                #3a3a45 50%,
                #262730 100%
            );
            background-size: 1000px 100%;
            animation: shimmer 1.5s infinite linear;
            border-radius: 4px;
            height: 20px;
            margin: 8px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🤖 QA Agent")
        st.markdown("")
        
        # Navigation menu with buttons
        st.markdown("**Navigation**")
        
        col1 = st.columns(1)[0]
        if st.button("📁 Knowledge Base", key="nav_kb", use_container_width=True, 
                     type="primary" if st.session_state.current_page == "📁 Knowledge Base" else "secondary"):
            st.session_state.current_page = "📁 Knowledge Base"
            st.rerun()
        
        if st.button("📋 Test Cases", key="nav_tc", use_container_width=True,
                     type="primary" if st.session_state.current_page == "📋 Test Cases" else "secondary"):
            st.session_state.current_page = "📋 Test Cases"
            st.rerun()
        
        if st.button("🤖 Selenium Scripts", key="nav_ss", use_container_width=True,
                     type="primary" if st.session_state.current_page == "🤖 Selenium Scripts" else "secondary"):
            st.session_state.current_page = "🤖 Selenium Scripts"
            st.rerun()
        
        st.markdown("---")
        
        # Clear data button in sidebar
        if st.button("🗑️ Clear All Data", key="clear_data", use_container_width=True):
            try:
                response = requests.delete(f"{API_URL}/api/clear")
                if response.status_code == 200:
                    st.session_state.test_cases = []
                    st.session_state.selected_test_case = None
                    st.session_state.selected_test_cases = []
                    st.session_state.generated_script = ""
                    st.success("✅ All data cleared")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        st.markdown("---")
        st.caption("AI-Powered Test Automation")
    
    # Get current page
    page = st.session_state.current_page
    
    # Main content area
    st.title("🤖 Autonomous QA Agent")
    st.markdown("*AI-Powered Test Case and Script Generation*")
    st.markdown("---")
    
    # Page 1: Knowledge Base
    if page == "📁 Knowledge Base":
        st.header("📁 Knowledge Base Ingestion")
        st.markdown("Upload support documents to build the knowledge base.")
        
        st.subheader("Upload Files")
        uploaded_files = st.file_uploader(
            "Choose files",
            type=['md', 'txt', 'json', 'pdf', 'html', 'htm'],
            accept_multiple_files=True,
            help="Upload product specs, UI guides, API docs, and checkout HTML"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) selected")
            for file in uploaded_files:
                st.text(f"  • {file.name}")
        
        st.divider()
        
        if st.button("🔨 Build Knowledge Base", type="primary", use_container_width=True):
            if not uploaded_files:
                st.warning("⚠️ Please upload files first")
            else:
                # Show shimmer loading effect
                loading_placeholder = st.empty()
                with loading_placeholder.container():
                    show_shimmer_loading("Building knowledge base...")
                    show_skeleton_loader(4)
                
                try:
                    # Upload files
                    files = [("files", (file.name, file, file.type)) for file in uploaded_files]
                    upload_response = requests.post(f"{API_URL}/api/upload", files=files)
                    
                    if upload_response.status_code != 200:
                        loading_placeholder.empty()
                        st.error(f"❌ Upload failed: {upload_response.json().get('detail', 'Unknown error')}")
                        return
                    
                    # Build knowledge base
                    kb_response = requests.post(f"{API_URL}/api/build_kb")
                    
                    loading_placeholder.empty()
                    if kb_response.status_code == 200:
                        result = kb_response.json()
                        upload_result = upload_response.json()
                        session = upload_result.get('session', 'unknown')
                        st.success(f"✅ {result['message']} (Session: {session})")
                    else:
                        st.error(f"❌ Error: {kb_response.json().get('detail', 'Unknown error')}")
                
                except Exception as e:
                    loading_placeholder.empty()
                    st.error(f"❌ Connection error: {e}")
    
    # Page 2: Test Cases
    elif page == "📋 Test Cases":
        st.header("📋 Test Case Generation Agent")
        st.markdown("Generate comprehensive test cases based on your query.")
        
        query = st.text_area(
            "What would you like to test?",
            height=100,
            placeholder="Example: Generate test cases for discount code functionality",
            help="Describe what you want to test"
        )
        
        if st.button("🎯 Generate Test Cases", type="primary"):
            if not query:
                st.warning("⚠️ Please enter a query")
            else:
                # Show shimmer loading effect
                loading_placeholder = st.empty()
                with loading_placeholder.container():
                    show_shimmer_loading("Generating test cases...")
                    show_skeleton_loader(5)
                
                try:
                    response = requests.post(
                        f"{API_URL}/api/generate_tests",
                        json={"query": query}
                    )
                    
                    loading_placeholder.empty()
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.test_cases = result.get('test_cases', [])
                        
                        if st.session_state.test_cases:
                            st.success(f"✅ Generated {len(st.session_state.test_cases)} test cases")
                        else:
                            st.warning("⚠️ " + result.get('message', 'No test cases generated'))
                    else:
                        st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                
                except Exception as e:
                    loading_placeholder.empty()
                    st.error(f"❌ Connection error: {e}")
        
        if st.session_state.test_cases:
            st.divider()
            
            # Display format selector
            display_format = st.radio(
                "Display Format",
                ["Markdown Table", "JSON"],
                horizontal=True
            )
            
            # Results section
            st.subheader("Generated Test Cases")
            if display_format == "Markdown Table":
                st.markdown(format_test_cases_as_markdown(st.session_state.test_cases))
            else:
                st.json(st.session_state.test_cases)
    
    # Page 3: Selenium Scripts
    elif page == "🤖 Selenium Scripts":
        st.header("🤖 Selenium Script Generation Agent")
        
        if not st.session_state.test_cases:
            st.info("ℹ️ Please generate test cases from the Test Cases tab first")
        else:
            # Test case selector for Selenium generation
            st.subheader("Select Test Cases for Script Generation")
            
            # Select All / Deselect All buttons
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✅ Select All", use_container_width=True):
                    st.session_state.selected_test_cases = list(range(len(st.session_state.test_cases)))
                    st.rerun()
            with col_b:
                if st.button("❌ Deselect All", use_container_width=True):
                    st.session_state.selected_test_cases = []
                    st.rerun()
            
            # Display checkboxes for each test case
            st.markdown("**Choose test cases:**")
            for idx, tc in enumerate(st.session_state.test_cases):
                checkbox_label = f"{tc['test_id']}: {tc['feature']}"
                is_checked = idx in st.session_state.selected_test_cases
                
                if st.checkbox(checkbox_label, value=is_checked, key=f"tc_checkbox_{idx}"):
                    if idx not in st.session_state.selected_test_cases:
                        st.session_state.selected_test_cases.append(idx)
                else:
                    if idx in st.session_state.selected_test_cases:
                        st.session_state.selected_test_cases.remove(idx)
            
            st.divider()
            
            # Generate button - only show if test cases are selected
            if st.session_state.selected_test_cases:
                st.success(f"✅ {len(st.session_state.selected_test_cases)} test case(s) selected")
                
                if st.button("🤖 Generate Selenium Scripts", type="primary", use_container_width=True):
                    # Reset script session to start a new batch
                    try:
                        requests.post(f"{API_URL}/api/reset_script_session")
                    except:
                        pass
                    
                    # Show shimmer loading effect
                    loading_placeholder = st.empty()
                    with loading_placeholder.container():
                        show_shimmer_loading(f"Generating Selenium scripts for {len(st.session_state.selected_test_cases)} test case(s)...")
                        show_skeleton_loader(6)
                    
                    try:
                        all_scripts = []
                        script_session = None
                        for idx in st.session_state.selected_test_cases:
                            tc = st.session_state.test_cases[idx]
                            response = requests.post(
                                f"{API_URL}/api/generate_script",
                                json={"test_case": tc}
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                script = result.get('script', '')
                                script_session = result.get('session', 'unknown')
                                all_scripts.append(f"# Test Case: {tc['test_id']}\n# Feature: {tc['feature']}\n\n{script}")
                            else:
                                loading_placeholder.empty()
                                st.error(f"❌ Error generating script for {tc['test_id']}")
                        
                        loading_placeholder.empty()
                        if all_scripts:
                            separator = "\n\n" + "="*80 + "\n\n"
                            st.session_state.generated_script = separator.join(all_scripts)
                            st.success(f"✅ Generated {len(all_scripts)} script(s) successfully (Session: {script_session})")
                    
                    except Exception as e:
                        loading_placeholder.empty()
                        st.error(f"❌ Connection error: {e}")
            else:
                st.warning("⚠️ Please select at least one test case to generate scripts")
            
            if st.session_state.generated_script:
                st.divider()
                st.subheader("Generated Scripts")
                
                # Display script with syntax highlighting
                st.code(st.session_state.generated_script, language='python', line_numbers=True)
                
                # Download button
                st.download_button(
                    label="📥 Download All Scripts",
                    data=st.session_state.generated_script,
                    file_name=f"test_scripts_{len(st.session_state.selected_test_cases)}_cases.py",
                    mime="text/x-python",
                    use_container_width=True
                )
        



if __name__ == "__main__":
    main()
