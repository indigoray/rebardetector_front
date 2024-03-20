import streamlit as st
import requests
import time

# 백엔드 API 엔드포인트 설정
BACKEND_URL = "http://changsoft1.iptime.org:8001"
#BACKEND_URL = "http://localhost:8001"

def start_processing(request_type, data=None, files=None):
    st.session_state.processing = True

    if request_type == 'url':
        response = requests.post(f"{BACKEND_URL}/upload_urls/", json=data)
    elif request_type == 'file':
        response = requests.post(f"{BACKEND_URL}/upload_files/", files=files)
    else:
        return

    if response.status_code == 200:
        request_id = response.json().get("request_id")
        st.session_state['request_id'] = request_id
        st.success(f"이미지 처리가 시작되었습니다. 요청 ID: {request_id}")
        polling_status = st.empty()
        polling_status.write("처리 중...")
        while True:
            time.sleep(2)  # Adjust polling interval as needed
            results_response = requests.get(f"{BACKEND_URL}/results/{request_id}")
            if results_response.status_code == 200:
                polling_status.success("처리 완료!")

                results = results_response.json().get("results", {})
                image_paths = results_response.json().get("images", [])
                polling_status.success("처리 완료!")

                for result, image_path in zip(results['result'], image_paths['result image']):
                    # 결과 텍스트와 이미지를 함께 표시
                    formatted_result = result.replace('\n', '<br>')
                    st.markdown(f'<pre>{formatted_result}</pre>', unsafe_allow_html=True)
                    image_url = f"{BACKEND_URL}/result_image/{image_path}"
                    st.image(image_url, caption="Detection Result")
                
                break
            elif results_response.status_code == 404:
                polling_status.write("결과가 아직 준비되지 않았습니다...")
            else:
                st.error("처리 중 오류 발생. 나중에 다시 시도해주세요.")
                break
    else:
        st.error("이미지 업로드 및 처리를 시작할 수 없습니다. 나중에 다시 시도해주세요.")
    
    st.session_state.processing = False
    st.success("처리 완료!")



st.title('AI Rebar Checking Demo')


# 처리 중 상태 관리
if 'processing' not in st.session_state:
    st.session_state.processing = False



# Section for file uploads
st.subheader("Changsoft i&i")
with st.form("my-form", clear_on_submit=True):
    uploaded_files = st.file_uploader("여러 이미지를 선택하세요", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
    submitted = st.form_submit_button("파일로 이미지 업로드 및 처리 시작!")
    if submitted :
        start_processing('file', files=[('files', (file.name, file, file.type)) for file in uploaded_files])



# 처리 중이 아닐 때에만 'Clear' 버튼 표시
if st.button('Clear'):
    # 세션 상태를 리셋하여 파일 업로더와 결과를 초기화
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    # 페이지를 새로고침하여 초기 상태로 리셋
    st.rerun()


