import requests
import json
import pandas as pd
from typing import List, Dict
import ast
import re


class CodeDatasetCollector:
    def __init__(self):
        self.github_token = None  # Set your GitHub token
        
    def collect_github_code_samples(self, language="python", limit=1000) -> List[Dict]:
        """Collect code samples from GitHub repositories"""
        samples = []
        
        # Search for Python files with different quality indicators
        quality_queries = [
            "language:python stars:>100 size:<1000",  # High quality
            "language:python TODO FIXME size:<1000",   # Needs improvement
            "language:python type:hints docstring",    # Well documented
            "language:python nested loops performance" # Performance issues
        ]
        
        for query in quality_queries:
            # GitHub API search (requires token for higher limits)
            url = f"https://api.github.com/search/code?q={query}&per_page=100"
            
            try:
                response = requests.get(url, headers={
                    'Authorization': f'token {self.github_token}' if self.github_token else None
                })
                
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('items', [])[:limit//4]:
                        samples.append({
                            'code': self._fetch_file_content(item['download_url']),
                            'quality_indicator': self._classify_quality(query),
                            'repo_stars': item.get('repository', {}).get('stargazers_count', 0),
                            'filename': item['name']
                        })
                        
            except Exception as e:
                print(f"Error fetching from GitHub: {e}")
                
        return samples
    
    def _fetch_file_content(self, url: str) -> str:
        """Fetch actual file content"""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text[:2000]  # Limit size
        except:
            pass
        return ""
    
    def _classify_quality(self, query: str) -> str:
        """Classify code quality based on search query"""
        if "stars:>100" in query:
            return "high_quality"
        elif "TODO FIXME" in query:
            return "needs_improvement"
        elif "docstring" in query:
            return "well_documented"
        elif "performance" in query:
            return "performance_issues"
        return "unknown"
    
    def create_sentiment_labels(self, code_samples: List[Dict]) -> List[Dict]:
        """Create sentiment labels based on code characteristics"""
        labeled_data = []
        
        for sample in code_samples:
            code = sample['code']
            
            # Rule-based labeling (bootstrap labels)
            sentiment_score = self._calculate_bootstrap_sentiment(code)
            
            labeled_data.append({
                'code': code,
                'sentiment_score': sentiment_score,
                'sentiment_label': 'positive' if sentiment_score > 0 else 'negative',
                'quality_features': self._extract_features(code),
                'repo_stars': sample.get('repo_stars', 0)
            })
            
        return labeled_data
    
    def _calculate_bootstrap_sentiment(self, code: str) -> float:
        """Bootstrap sentiment labels using rule-based approach"""
        score = 0.0
        
        # Positive indicators
        if re.search(r'def \w+.*:', code): score += 0.2
        if re.search(r'""".*?"""', code, re.DOTALL): score += 0.3
        if re.search(r':\s*\w+', code): score += 0.1  # Type hints
        if 'with open' in code: score += 0.2
        if any(pattern in code for pattern in ['yield', 'lambda', 'comprehension']): score += 0.3
        
        # Negative indicators  
        if re.search(r'TODO|FIXME|XXX', code): score -= 0.4
        if re.search(r'global \w+', code): score -= 0.3
        if code.count('for') > 2: score -= 0.2  # Nested loops
        if re.search(r'\d{3,}', code): score -= 0.1  # Magic numbers
        
        return max(-1.0, min(1.0, score))
    
    def _extract_features(self, code: str) -> Dict:
        """Extract features for training"""
        try:
            tree = ast.parse(code)
            
            features = {
                'num_functions': len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
                'num_classes': len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
                'has_docstrings': bool(re.search(r'""".*?"""', code, re.DOTALL)),
                'has_type_hints': bool(re.search(r':\s*\w+', code)),
                'num_comments': code.count('#'),
                'lines_of_code': len(code.split('\n')),
                'cyclomatic_complexity': self._estimate_complexity(tree)
            }
            
        except SyntaxError:
            features = {'parse_error': True}
            
        return features
    
    def _estimate_complexity(self, tree: ast.AST) -> int:
        """Estimate cyclomatic complexity"""
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                complexity += 1
        return complexity
    
    def save_dataset(self, data: List[Dict], filename: str):
        """Save dataset to file"""
        df = pd.DataFrame(data)
        df.to_json(filename, orient='records', indent=2)
        print(f"Saved {len(data)} samples to {filename}")


# Usage example
if __name__ == "__main__":
    collector = CodeDatasetCollector()
    
    # Collect samples (set GitHub token for higher limits)
    samples = collector.collect_github_code_samples(limit=500)
    
    # Create labeled dataset
    labeled_data = collector.create_sentiment_labels(samples)
    
    # Save for training
    collector.save_dataset(labeled_data, "code_sentiment_dataset.json")