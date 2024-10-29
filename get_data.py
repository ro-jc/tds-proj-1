import requests
import time
import csv
import json
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
import re

class GitHubAPI:
    def __init__(self, access_token: str):
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {access_token}"
        }
        self.base_url = "https://api.github.com"
    
    def _make_request(self, url: str, params: Dict = None) -> Dict:
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 403:
            wait_time = int(response.headers.get('X-RateLimit-Reset', 0)) - int(time.time())
            print(f"Rate limit exceeded. Wait for {wait_time} seconds.")
            return {}
            
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.json())
            return {}
        
        time.sleep(0.5)
        return response.json()
    
    def get_user_repos(self, username: str) -> List[Dict]:
        repos_url = f"{self.base_url}/users/{username}/repos"
        params = {"sort": "pushed", "per_page": 500}
        
        all_repos = []
        page = 1
        
        while True:
            params["page"] = page
            repos = self._make_request(repos_url, params)
            
            if not repos:
                break
                
            all_repos.extend(repos)
            page += 1
            
            if len(repos) < 500:
                break
                
        return all_repos
    
    def search_mumbai_users(self, min_followers: int = 50, max_results: int = 1000) -> List[Dict]:
        search_url = f"{self.base_url}/search/users"
        
        all_users = []
        page = 1
        per_page = 100
        
        while len(all_users) < max_results:
            params = {
                "q": f"location:Mumbai followers:>={min_followers}",
                "per_page": per_page,
                "page": page
            }
            
            data = self._make_request(search_url, params)
            if not data:
                break
                
            users = data.get("items", [])
            if not users:
                break
                
            all_users.extend(users)
            page += 1
            
        return all_users[:max_results]
    
    def get_user_details(self, username: str) -> Dict:
        user_url = f"{self.base_url}/users/{username}"
        return self._make_request(user_url)

def clean_company_name(company: str) -> str:
    if company:
        company = company.strip()
        if company.startswith("@"):
            company = company[1:]
        return company.upper()
    return ""

def save_data(token: str):
    github = GitHubAPI(token)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Get users and their data
    users = github.search_mumbai_users(min_followers=50)
    print(f"Found {len(users)} users in Mumbai with 50+ followers")
    
    users_data = []
    repos_data = []
    
    for user in users:
        username = user["login"]
        print(f"Processing user: {username}")
        
        # Get detailed user information
        user_details = github.get_user_details(username)
        if user_details:
            users_data.append({
                "login": user_details["login"],
                "name": user_details["name"],
                "company": clean_company_name(user_details["company"]),
                "location": user_details["location"],
                "email": user_details["email"],
                "hireable": str(user_details["hireable"]),
                "bio": user_details["bio"],
                "public_repos": user_details["public_repos"],
                "followers": user_details["followers"],
                "following": user_details["following"],
                "created_at": user_details["created_at"]
            })
            
            # Get user's repositories
            repos = github.get_user_repos(username)
            for repo in repos:
                repos_data.append({
                    "login": username,
                    "full_name": repo["full_name"],
                    "created_at": repo["created_at"],
                    "stargazers_count": repo["stargazers_count"],
                    "watchers_count": repo["watchers_count"],
                    "language": repo["language"],
                    "has_projects": str(repo["has_projects"]),
                    "has_wiki": str(repo["has_wiki"]),
                    "license_name": repo["license"]["name"] if repo["license"] else ""
                })
    
    # Save users.csv
    if users_data:
        users_df = pd.DataFrame(users_data)
        users_df.to_csv('users.csv', index=False)
    
    # Save repositories.csv
    if repos_data:
        repos_df = pd.DataFrame(repos_data)
        repos_df.to_csv('repositories.csv', index=False)
    
    print(f"Data collection completed. Files saved: users.csv, repositories.csv")
    
    # Optional: Save raw data for analysis
    with open('raw_data.json', 'w') as f:
        json.dump({
            'users': users_data,
            'repositories': repos_data
        }, f, indent=2)


if __name__ == "__main__":
    # Replace with your GitHub personal access token
    token = open('.token.txt').read().strip()
    save_data(token)
