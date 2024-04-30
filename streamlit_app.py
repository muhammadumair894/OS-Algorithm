import streamlit as st
import random
import time

# Define the job pool
job_pool = [
    {"id": i, "arrive": random.randint(0, 50), "burst": random.randint(10, 50), "priority": random.randint(0, 10)}
    for i in range(1, 11)
]

# Define the algorithms
def fcfs(job_pool, sim_speed):
    cpu = {"job_id": None, "start": 0, "end": 0}
    queue = []
    waiting_times = []
    turnaround_times = []
    for job in job_pool:
        if not queue:
            queue.append(job)
            job["start"] = 0
            job["end"] = job["burst"]
            cpu["job_id"] = job["id"]
            cpu["end"] = job["end"]
            waiting_times.append(0)
            turnaround_times.append(job["end"] - job["arrive"])
        else:
            if job["arrive"] <= cpu["end"]:
                queue.append(job)
                job["start"] = cpu["end"]
                job["end"] = job["start"] + job["burst"]
                cpu["job_id"] = job["id"]
                cpu["end"] = job["end"]
                waiting_times.append(job["start"] - job["arrive"])
                turnaround_times.append(job["end"] - job["arrive"])
            else:
                queue.append(queue.pop(0))
                queue[-1]["start"] = cpu["end"]
                queue[-1]["end"] = queue[-1]["start"] + queue[-1]["burst"]
                cpu["job_id"] = queue[-1]["id"]
                cpu["end"] = queue[-1]["end"]
                waiting_times.append(queue[-1]["start"] - queue[-1]["arrive"])
                turnaround_times.append(queue[-1]["end"] - queue[-1]["arrive"])
    return queue, waiting_times, turnaround_times, cpu

def rr(job_pool, sim_speed, quantum):
    cpu = {"job_id": None, "start": 0, "end": 0}
    queue = sorted(job_pool, key=lambda x: x["arrive"])
    waiting_times = []
    turnaround_times = []
    remaining_times = [job["burst"] for job in job_pool]
    current_time = 0
    while queue or remaining_times:
        if queue:
            job = queue.pop(0)
            if remaining_times[job["id"] - 1] > quantum:
                cpu["job_id"] = job["id"]
                cpu["start"] = current_time
                cpu["end"] = cpu["start"] + quantum
                current_time += quantum
                remaining_times[job["id"] - 1] -= quantum
                queue.append(job)
                queue = sorted(queue, key=lambda x: x["arrive"])
            else:
                cpu["job_id"] = job["id"]
                cpu["start"] = current_time
                cpu["end"] = cpu["start"] + remaining_times[job["id"] - 1]
                current_time += remaining_times[job["id"] - 1]
                waiting_times.append(cpu["start"] - job["arrive"])
                turnaround_times.append(cpu["end"] - job["arrive"])
                remaining_times[job["id"] - 1] = 0
        else:
            time.sleep(1 / sim_speed)
            current_time += 1
    return queue, waiting_times, turnaround_times, cpu

# Define the Streamlit app
st.title("CPU Scheduler Simulator")

num_jobs = st.slider("Number of Jobs", 1, 10, 5)
algorithm = st.radio("Algorithm", ["First Come First Serve", "Round Robin"])
sim_speed = st.slider("Simulation Speed", 1, 10, 1)
quantum = st.number_input("Quantum (for Round Robin)", 10, 50, 20)

if algorithm == "First Come First Serve":
    queue, waiting_times, turnaround_times, cpu = fcfs(job_pool[:num_jobs], sim_speed)
else:
    queue, waiting_times, turnaround_times, cpu = rr(job_pool[:num_jobs], sim_speed, quantum)

st.subheader("CPU Status")
st.write(f"Job {cpu['job_id']} is currently running from {cpu['start']} to {cpu['end']}")

st.subheader("Queue")
for job in queue:
    st.write(f"Job {job['id']} arrives at {job['arrive']} and runs from {job['start']} to {job['end']}")

st.subheader("Average Waiting Time")
st.write(sum(waiting_times) / len(waiting_times))

st.subheader("Average Turnaround Time")
st.write(sum(turnaround_times) / len(turnaround_times))

st.subheader("Gantt Chart")
gantt_chart = [
    {"time": 0, "job_id": None},
    {"time": cpu["start"], "job_id": cpu["job_id"]},
    {"time": cpu["end"], "job_id": None},
]
for job in queue:
    gantt_chart.append({"time": job["start"], "job_id": job["id"]})
    gantt_chart.append({"time": job["end"], "job_id": None})
gantt_chart.append({"time": current_time, "job_id": None})

for i in range(len(gantt_chart) - 1):
    if gantt_chart[i]["job_id"] != gantt_chart[i + 1]["job_id"]:
        st.write(f"{gantt_chart[i]['time']} -- {gantt_chart[i + 1]['time']}  {gantt_chart[i]['job_id']} -> {gantt_chart[i + 1]['job_id']}")
    else:
        st.write(f"{gantt_chart[i]['time']} -- {gantt_chart[i + 1]['time']}  {gantt_chart[i]['job_id']}")
