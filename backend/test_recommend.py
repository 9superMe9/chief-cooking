import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhYzYxZjUwMy1jZTI0LTQyOGMtOGZlYS1lZDdlNjE0NGM5OGYiLCJleHAiOjE3ODIyNzA4MDZ9.dWOAV2XqViAS505AMcg8pXzHyDRcG3XZ6jnzeliLvWE"

url = "http://localhost:8000/api/v1/recipes/recommend"
data = {
    "ingredients": ["鸡蛋", "番茄"],
    "preferences": {"taste": "家常", "cookingTime": 20}
}
headers = {"Authorization": f"Bearer {token}"}

response = requests.post(url, json=data, headers=headers)
print(f"Status: {response.status_code}")
print(f"Body: {response.text}")
