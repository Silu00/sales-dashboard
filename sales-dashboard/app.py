import streamlit as st
import data_processor

st.set_page_config(page_title="Data Engineering Task 4", layout="wide")

st.title("📊 Dashboard")
st.markdown("Dashboard presents analysis for DATA1, DATA2 and DATA3 folders.")
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 24px;
        color: #0068c9;
    }
</style>
""", unsafe_allow_html=True)

def render_tab(folder_name):
    try:
        data = data_processor.process_data(folder_name)

        c1, c2, c3 = st.columns(3)
        c1.metric("Unique Real Users", data["unique_users"])
        c2.metric("Unique Author Sets", data["unique_authors"])
        c3.metric("Top Author(s)", data["top_author"])

        st.divider()

        col_left, col_right = st.columns([1, 2])

        with col_left:
            st.subheader("📅 Top 5 Days (Revenue)")
            st.dataframe(data["top_5_days"], hide_index=True, use_container_width=True)

            st.subheader("🏆 Best Buyer IDs")
            st.code(str(data["best_buyer_ids"]), language="json")
        with col_right:
            st.subheader("📈 Revenue Over Time")
            st.pyplot(data["chart_fig"])

    except Exception as e:
        st.error(f"Error processing {folder_name}: {e}")

tab1, tab2, tab3 = st.tabs(["DATA 1", "DATA 2", "DATA 3"])

with tab1:
    render_tab("DATA1")
with tab2:
    render_tab("DATA2")
with tab3:
    render_tab("DATA3")