import time
import streamlit as st
from streamlit_modal import Modal

# With Modal
# site-package의 streamlit-modal > __init__.py도 함께 수정
modal = Modal(
    title="Please wait",
    key="testModal",
    max_width=500
)

if modal.is_open():
    with modal.auto_closed_container():
        with st.spinner(text="잠시만 기다려주세요..."):
            st.markdown("<p style='font-size: 14px; color: Gray;'>이 작업은 몇 분 정도 걸릴 수 있습니다.</p>",
                        unsafe_allow_html=True)
            time.sleep(5)
            modal.close()
success = False

if st.button("spinner", key="spin"):
    modal.open()