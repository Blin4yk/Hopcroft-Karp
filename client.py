# import requests

# tasks = ['C1', 'C2', 'C3', 'C4']

# try:
#     response = requests.post('http://localhost:5000/assign_tasks')
#     response.raise_for_status()  # Проверка успешности запроса
#     assignments = response.json()

#     for task, server in assignments.items():
#         if task in tasks:
#             print(f"Task {task} assigned to Server {server}")
# except requests.exceptions.RequestException as e:
#     print(f"An error occurred: {e}")


# import requests

# tasks = ['C1', 'C2', 'C3', 'C4']

# try:
#     response = requests.post('http://localhost:5000/assign_tasks')
#     response.raise_for_status()  # Проверка успешности запроса
#     assignments = response.json()

#     for task, server in assignments.items():
#         if task in tasks:
#             print(f"Task {task} assigned to Server {server}")

#     # Запрос на получение визуализации графа
#     img_response = requests.get('http://localhost:5000/visualize_graph')
#     if img_response.status_code == 200:
#         with open('graph.png', 'wb') as f:
#             f.write(img_response.content)
#         print("Graph visualization saved as 'graph.png'")
#     else:
#         print(f"Failed to get graph visualization: {img_response.status_code}")
# except requests.exceptions.RequestException as e:
#     print(f"An error occurred: {e}")







import requests

tasks = ['C1', 'C2', 'C3', 'C4']

try:
    response = requests.post('http://localhost:5000/assign_tasks')
    response.raise_for_status()  # Проверка успешности запроса
    assignments = response.json()

    for task, server in assignments.items():
        if task in tasks:
            print(f"Task {task} assigned to Server {server}")

    # Запрос на получение визуализации графа
    img_response = requests.get('http://localhost:5000/visualize_graph')
    if img_response.status_code == 200:
        with open('graph.png', 'wb') as f:
            f.write(img_response.content)
        print("Graph visualization saved as 'graph.png'")
    else:
        print(f"Failed to get graph visualization: {img_response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
