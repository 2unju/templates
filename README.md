# Sreamlit Templates
## Spinner with Modal
![image](https://github.com/2unju/streamlit-templates/assets/77797199/b7e0d214-b936-42c6-9773-ed920e257b60)
![image](https://github.com/2unju/streamlit-templates/assets/77797199/60077f4a-1801-44ca-a996-7c90ed5c949c)
### requirements
- 패키지 버전
```
streamlit == 1.34.0
streamlit-modal == 0.1.2
```
- streamlit-modal의 Modal.container 수정
```python
with st.container():
    _container = st.container()
    
    # title, close_button = _container.columns([0.9, 0.1])
    # if self.title:
    #     with title:
    #         st.markdown(self.title)
    # with close_button:
    #     close_ = st.button('X', key=f'{self.key}-close')
    #     if close_:
    #         self.close()
    
    # _container.divider()
```