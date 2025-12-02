from base64 import b64encode
from io import StringIO
import os
from sys import path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import streamlit as st

path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analyser import WhatsAppAnalyzer

st.set_page_config('WhatsApp Chat Analyzer (Web)', layout='wide')

st.title('WhatsApp Chat Analyzer - Web UI')
st.markdown('Upload your WhatsApp exported `.txt` (without media) and view analytics in-browser. All analysis runs locally in your browser/server — nothing leaves your machine.')

uploaded = st.file_uploader('Upload WhatsApp .txt file', type=['txt'])

with st.sidebar:
    st.header("Options")
    save_png = st.checkbox("Also save PNGs to disk (output/)", value=False)
    download_zip = st.checkbox("Show Download ZIP button", value=True)
    min_doubletext_threshold = st.number_input("Min double-text length to show", min_value=2, max_value=20, value=2)

if uploaded is not None:
    try:
        raw_bytes = uploaded.read()
        text = raw_bytes.decode("utf-8")
    except Exception:
        text = uploaded.getvalue().decode("utf-8")

    buffer = StringIO(text)
    output_dir = 'output' if save_png else None

    analyzer = WhatsAppAnalyzer(buffer, output_dir)

    try:
        analyzer.parse_chat()
    except Exception as e:
        st.error(f'Failed to parse chat: {e}')
        st.stop()

    st.success('Chat parsed successfully!')

    tabs = st.tabs([
        "Summary", "Response Time", "Heatmap", "Volume", "Activity",
        "Initiators", "Double Text", "Message Length", "Emoji", "Questions", "Gaps", "Streak"
    ])

    with tabs[0]:
        st.header('Summary')
        fig, stats = analyzer.generate_summary_stats()
        st.pyplot(fig)
        st.table(stats)

    with tabs[1]:
        st.header("Response Time Percentiles")
        fig = analyzer.plot_response_time_percentiles()
        if fig: st.pyplot(fig)

    with tabs[2]:
        st.header("Response Time Heatmap")
        fig = analyzer.plot_response_time_heatmap()
        if fig:
            st.pyplot(fig)

    with tabs[3]:
        st.header("Message Volume")
        fig = analyzer.plot_message_volume()
        if fig: st.pyplot(fig)

    with tabs[4]:
        st.header("Activity Patterns")
        fig = analyzer.plot_activity_patterns()
        if fig: st.pyplot(fig)

    with tabs[5]:
        st.header("Conversation Initiators")
        fig = analyzer.plot_conversation_initiators()
        if fig: st.pyplot(fig)

    with tabs[6]:
        st.header("Double Text Frequency")
        fig = analyzer.plot_double_text_frequency()
        if fig: st.pyplot(fig)

    with tabs[7]:
        st.header("Message Length Analysis")
        fig = analyzer.plot_message_length_analysis()
        if fig: st.pyplot(fig)

    with tabs[8]:
        st.header("Emoji Analysis")
        fig = analyzer.plot_emoji_analysis()
        if fig: st.pyplot(fig)

    with tabs[9]:
        st.header("Question Frequency")
        fig = analyzer.plot_question_frequency()
        if fig: st.pyplot(fig)

    with tabs[10]:
        st.header("Conversation Gaps")
        fig = analyzer.plot_conversation_gaps()
        if fig: st.pyplot(fig)

    with tabs[11]:
        st.header("Daily Streak")
        fig = analyzer.plot_daily_streak()
        if fig: st.pyplot(fig)

    if download_zip and output_dir:
        if st.button("Download all PNGs as ZIP"):
            with TemporaryDirectory() as tmpdir:
                zip_path = os.path.join(tmpdir, 'charts.zip')
                with ZipFile(zip_path,'w') as zfp:
                    for fname in os.listdir(output_dir):
                        if fname.lower().endswith('.png'): zfp.write(os.path.join(output_dir, fname), arcname=fname)
                with open(zip_path, 'rb') as fp: b64 = b64encode(fp.read()).decode()
                href = f'<a href="data:application/zip;base64,{b64}" download="whatsapp_charts.zip">Download ZIP</a>'
                st.markdown(href, unsafe_allow_html=True)
