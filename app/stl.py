import streamlit as st
import asyncio
import time
import requests
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(layout="centered", page_title="NewScrAIper")


elpais={"url":"https://elpais.com/", "name":"El Pais"}
elmundo={"url":"https://www.elmundo.es/", "name":"El Mundo"}
larazon={"url":"https://www.larazon.es/", "name":"La Razon"}
abc={"url":"https://www.abc.es/", "name":"ABC"}
bbc={"url":"https://www.bbc.com/", "name":"BBC"}
nyt={"url":"https://www.nytimes.com/", "name":"NYT"}

API_URL = "http://fastapi:8000"

newspapers= [elpais,elmundo,larazon,abc,bbc,nyt]
newspaper_urls = [newspaper["url"] for newspaper in newspapers]



with st.container():
    st.title("NewScrAIper")

    
    tab1, tab2, tab3 = st.tabs(["Create Task", "Get Task Data", "Schedule Tasks"])
    with tab1:
        st.header("Create Task")
        option = st.selectbox(
            "Select Newspaper",
            newspaper_urls,
            index=None,
            placeholder="Newspaper URL ...",
            accept_new_options=True,
        )
        d= st.date_input(
            "Select the interval dates",
            (datetime.now(), datetime.now()+timedelta(days=3)),
            min_value=datetime.now(),
            format="YYYY/MM/DD"
        )
        if st.button("New Task"):
            if option:
                try:
                    response = requests.post(f"{API_URL}/schedule/add_task", params={"url": option, "start_date": d[0], "end_date": d[1]})
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"Task: '{data['task_name']}'.\n {data['message']} ✅")
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Error endpoint: {str(e)}")
            else:
                st.warning("URL not valid")

    with tab2:
        st.header("Get Task Data")
        task_name = st.text_input("Task Name:")

        if st.button("Get Data"):
            if task_name:
                try:
                    response = requests.get(f"{API_URL}/schedule/get_task_result/{task_name}")
                    if response.status_code == 200:
                        # print("OK")
                        result = response.json()
                        # print(result)
                        if not result:
                            st.warning("No data found for this task.")
                        df = pd.DataFrame(result)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Excepcion status: {str(e)}")
            else:
                st.warning("Not valid task name")

    with tab3:
        st.header("Get Schedule Tasks")
        if "active_tasks" not in st.session_state:
            st.session_state.active_tasks = []
        if "loaded_tasks" not in st.session_state:
            st.session_state.loaded_tasks = False

        if st.button("List Schedule Tasks"):
            try:
                resp = requests.get(f"{API_URL}/schedule/list_tasks")
                resp.raise_for_status()
                st.session_state.active_tasks = resp.json()
                st.session_state.loaded_tasks = True
                st.rerun()
            except Exception as e:
                st.error(f"Error listing tasks: {e}")

        if st.session_state.loaded_tasks:
            if st.session_state.active_tasks:
                st.subheader("Schedule Tasks")
                # print(st.session_state.active_tasks)
                for task in st.session_state.active_tasks.copy():
                    task_name = task.get("task_name", "Unknown Task")
                    task_options = task.get("options", {})
                    task_schedule = task.get("schedule", "No schedule info")
                    col1, col2 = st.columns([4, 1])
                    col1.write({"task_name": task_name, "options": task_options, "schedule":task_schedule ,"last_run_at": task.get("last_run_at", "Not available")})
                    if col2.button("Cancel", key=f"cancel_{task_name}"):
                        try:
                            cancel_resp = requests.delete(f"{API_URL}/schedule/cancel_task/{task_name}")
                            cancel_resp.raise_for_status()
                            st.success(f"Task {task_name} Cancelled")
                            st.session_state.active_tasks = [
                                t for t in st.session_state.active_tasks
                                if t.get("task_name") != task_name
                            ]
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error canceling {task_name}: {e}")
            else:
                st.info("No scheduled task 😴")