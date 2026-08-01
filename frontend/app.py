import streamlit as st
import pandas as pd
import requests
import json
from PIL import Image
import io
from utils import (
    check_backend_health,
    upload_files_to_backend,
    run_extraction_pipeline,
    get_download_url
)

st.set_page_config(
    page_title="EduExtract - Academic Document Processing",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich UI styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748B;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .stProgress > div > div > div > div {
        background-color: #2563EB;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🎓 EduExtract</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Production-Grade Academic & Scientific Document Information Extraction Platform</div>', unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.title("⚙️ Engine Configuration")

# Backend Health Indicator
health = check_backend_health()
if health:
    st.sidebar.success(f"🟢 Backend Online (v{health.get('version', '1.0.0')})")
    st.sidebar.caption(f"OCR Engine: {health.get('ocr_engine', 'EasyOCR')}")
else:
    st.sidebar.error("🔴 Backend Disconnected")
    st.sidebar.caption("Ensure FastAPI backend is running at http://localhost:8000")

st.sidebar.subheader("Extraction Pipeline Modules")
enable_preprocessing = st.sidebar.checkbox("Image Preprocessing (Skew/Noise/Binarize)", value=True)
extract_text = st.sidebar.checkbox("Plain Text & Headings", value=True)
extract_tables = st.sidebar.checkbox("Table Detection & Grid Extraction", value=True)
extract_equations = st.sidebar.checkbox("Math Equations (LaTeX)", value=True)
extract_chemical = st.sidebar.checkbox("Chemical Compounds & Structures", value=True)
extract_graphs = st.sidebar.checkbox("Figures, Charts & Captions", value=True)

# Main UI Tabs
tab_upload, tab_results, tab_export = st.tabs(["📄 Upload & Preview", "📊 Extracted Information", "📥 Export & Download"])

if "upload_data" not in st.session_state:
    st.session_state["upload_data"] = None

if "extraction_result" not in st.session_state:
    st.session_state["extraction_result"] = None


# --- TAB 1: UPLOAD & PREVIEW ---
with tab_upload:
    st.subheader("1. Upload Scientific Documents")
    uploaded_files = st.file_uploader(
        "Select PDF or Image files (PNG, JPG, JPEG, TIFF)",
        type=["pdf", "png", "jpg", "jpeg", "tiff", "webp"],
        accept_multiple_files=True
    )

    if uploaded_files:
        col_prev, col_act = st.columns([1, 1])

        with col_prev:
            st.write("**Document Preview**")
            first_file = uploaded_files[0]
            if first_file.name.lower().endswith(".pdf"):
                st.info(f"📁 PDF Document selected: `{first_file.name}` ({len(first_file.getvalue()) // 1024} KB)")
            else:
                image = Image.open(first_file)
                st.image(image, caption=f"Preview: {first_file.name}", use_column_width=True)

        with col_act:
            st.write("**Process Document**")
            if st.button("🚀 Process & Extract", type="primary", use_container_width=True):
                with st.spinner("Uploading and rendering document frames..."):
                    upload_res = upload_files_to_backend(uploaded_files)

                if upload_res and "error" not in upload_res:
                    st.session_state["upload_data"] = upload_res
                    doc_id = upload_res["document_id"]
                    
                    st.success(f"Uploaded successfully! ID: `{doc_id}` ({upload_res['total_pages']} pages)")

                    # Run extraction pipeline
                    progress_bar = st.progress(0, text="Initializing extraction pipeline...")
                    progress_bar.progress(30, text="Preprocessing & running EasyOCR...")
                    
                    options = {
                        "enable_preprocessing": enable_preprocessing,
                        "extract_text": extract_text,
                        "extract_tables": extract_tables,
                        "extract_equations": extract_equations,
                        "extract_chemical": extract_chemical,
                        "extract_graphs": extract_graphs
                    }
                    
                    result = run_extraction_pipeline(doc_id, options)
                    progress_bar.progress(90, text="Structuring extracted entities...")

                    if result and "error" not in result:
                        progress_bar.progress(100, text="Extraction complete!")
                        st.session_state["extraction_result"] = result
                        st.balloons()
                        st.info("Switch to the '📊 Extracted Information' tab to view results!")
                    else:
                        st.error(f"Extraction failed: {result.get('error') if result else 'Unknown error'}")
                else:
                    st.error(f"Upload error: {upload_res.get('error') if upload_res else 'Failed'}")


# --- TAB 2: EXTRACTED INFORMATION ---
with tab_results:
    res = st.session_state.get("extraction_result")
    if not res:
        st.info("No document processed yet. Please upload and process a document in Tab 1.")
    else:
        st.subheader("Document Summary & Metrics")
        meta = res.get("metadata", {})
        
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total Pages", meta.get("total_pages", 1))
        m2.metric("Text Blocks", len(res.get("plain_text", [])))
        m3.metric("Tables Found", len(res.get("tables", [])))
        m4.metric("Equations", len(res.get("equations", [])))
        m5.metric("Chemical Entities", len(res.get("chemical_data", {}).get("compounds", [])))

        st.divider()

        sub_text, sub_table, sub_eq, sub_chem, sub_fig, sub_ref = st.tabs([
            "📝 Text & Headings",
            "📋 Tables",
            "🧮 Equations",
            "🧪 Chemical Data",
            "🖼️ Figures & Graphs",
            "📚 References"
        ])

        with sub_text:
            st.write("### Headings Outline")
            headings = res.get("headings", [])
            if headings:
                for h in headings:
                    st.write(f"**Level {h['level']}**: {h['text']} *(Page {h['page']})*")
            else:
                st.caption("No explicit headings detected.")

            st.write("### Full Extracted Text")
            text_blocks = res.get("plain_text", [])
            if text_blocks:
                full_text = "\n".join([item["text"] for item in text_blocks])
                st.text_area("Extracted Plain Text", full_text, height=300)
            else:
                st.caption("No plain text extracted.")

        with sub_table:
            tables = res.get("tables", [])
            if tables:
                for idx, tbl in enumerate(tables, 1):
                    st.write(f"#### Table {idx} (Page {tbl.get('page')}) - {tbl.get('rows')} rows × {tbl.get('cols')} cols")
                    matrix = tbl.get("matrix", [])
                    if matrix:
                        df = pd.DataFrame(matrix[1:], columns=matrix[0] if len(matrix) > 0 else None)
                        st.dataframe(df, use_container_width=True)
            else:
                st.info("No tables detected in the document.")

        with sub_eq:
            eqs = res.get("equations", [])
            if eqs:
                for idx, eq in enumerate(eqs, 1):
                    st.write(f"**Equation {idx} (Page {eq.get('page')})**:")
                    st.latex(eq.get("equation_text"))
            else:
                st.info("No mathematical equations detected.")

        with sub_chem:
            chem = res.get("chemical_data", {})
            compounds = chem.get("compounds", [])
            structures = chem.get("structures", [])

            st.write("#### Extracted Chemical Compounds & Formulas")
            if compounds:
                df_chem = pd.DataFrame(compounds)
                st.dataframe(df_chem, use_container_width=True)
            else:
                st.caption("No chemical compound names or formulas detected.")

            st.write("#### Visual Chemical Structure Diagrams")
            if structures:
                st.write(f"Identified `{len(structures)}` visual ring/bond structure diagram region(s).")
                for s in structures:
                    st.write(f"- Diagram ID: `{s['diagram_id']}` on Page {s['page']} (Estimated bonds: {s['estimated_bonds']})")
            else:
                st.caption("No visual chemical structure diagrams detected.")

        with sub_fig:
            figs = res.get("figures", [])
            if figs:
                for idx, fig in enumerate(figs, 1):
                    st.write(f"#### Figure {idx} ({fig.get('figure_type')}) - Page {fig.get('page')}")
                    st.caption(f"Caption: {fig.get('caption', 'None')}")
            else:
                st.info("No scientific figures or graphs detected.")

        with sub_ref:
            refs = res.get("references", [])
            if refs:
                for r in refs:
                    st.write(f"- {r.get('text')} *(Page {r.get('page')})*")
            else:
                st.info("No explicit references section detected.")


# --- TAB 3: EXPORT & DOWNLOAD ---
with tab_export:
    res = st.session_state.get("extraction_result")
    if not res:
        st.info("Please process a document first to download results.")
    else:
        doc_id = res.get("document_id")
        st.subheader("2. Download Extraction Results in Preferred Format")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 📄 JSON Format")
            st.caption("Complete structured tree suitable for programmatic REST API consumption.")
            json_str = json.dumps(res, indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name=f"eduextract_{doc_id}.json",
                mime="application/json",
                use_container_width=True
            )

        with col2:
            st.markdown("### 📝 Markdown Format")
            st.caption("Clean formatted document with headings, embedded Markdown tables, and LaTeX equations.")
            md_url = get_download_url(doc_id, "markdown")
            try:
                md_res = requests.get(md_url)
                md_data = md_res.text if md_res.status_code == 200 else ""
            except Exception:
                md_data = ""
            st.download_button(
                label="📥 Download Markdown",
                data=md_data,
                file_name=f"eduextract_{doc_id}.md",
                mime="text/markdown",
                use_container_width=True
            )

        with col3:
            st.markdown("### 📊 CSV Zip Archive")
            st.caption("Zip archive containing individual CSV files for every extracted table.")
            csv_url = get_download_url(doc_id, "csv")
            try:
                csv_res = requests.get(csv_url)
                csv_bytes = csv_res.content if csv_res.status_code == 200 else b""
            except Exception:
                csv_bytes = b""
            st.download_button(
                label="📥 Download CSV Archive",
                data=csv_bytes,
                file_name=f"eduextract_{doc_id}_tables.zip",
                mime="application/zip",
                use_container_width=True
            )
