"""
Git Inspector - Repository History and Provenance

Wraps GitPython to provide commit history, blame information,
and workspace diff detection for memory provenance tracking.
"""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

try:
    import git
    GITPYTHON_AVAILABLE = True
except ImportError:
    GITPYTHON_AVAILABLE = False
    git = None


class GitInspectorError(Exception):
    """Custom exception for Git Inspector errors"""
    pass


class GitInspector:
    """
    GitPython wrapper for repository history and provenance.
    
    Attributes:
        repo: GitPython repository object
        repo_path: Repository root path
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize with repository path.
        
        Args:
            repo_path: Path to git repository root
        
        Raises:
            GitInspectorError: If path is not a git repository
        
        Requirement: 16.5
        """
        if not GITPYTHON_AVAILABLE:
            raise ImportError(
                "GitPython not installed. Install with: pip install GitPython"
            )
        
        self.repo_path = Path(repo_path).resolve()
        
        # Validate it's a git repository
        try:
            self.repo = git.Repo(self.repo_path)
        except git.exc.InvalidGitRepositoryError:
            raise GitInspectorError(
                f"Not a git repository: {repo_path}"
            )
        except Exception as e:
            raise GitInspectorError(
                f"Failed to initialize git repository: {e}"
            )
    
    def get_commit_history(
        self,
        file_path: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recent commits affecting a file.
        
        Args:
            file_path: Path to file (relative to repo root)
            limit: Maximum number of commits to return
        
        Returns:
            List of commit dictionaries with hash, author, email, timestamp, message
        
        Requirement: 8
        """
        try:
            validated_path = self._validate_file_path(file_path)
            relative_path = validated_path.relative_to(self.repo_path)
            
            # Get commits affecting this file
            commits = list(self.repo.iter_commits(
                paths=str(relative_path),
                max_count=limit
            ))
            
            return [
                {
                    "hash": commit.hexsha,
                    "short_hash": commit.hexsha[:7],
                    "author": commit.author.name,
                    "email": commit.author.email,
                    "timestamp": datetime.fromtimestamp(commit.committed_date),
                    "message": commit.message.strip(),
                    "stats": commit.stats.files.get(str(relative_path), {})
                }
                for commit in commits
            ]
        
        except Exception as e:
            return self._handle_git_error(e, "get_commit_history", return_empty=True)
    
    def get_file_authors(self, file_path: str) -> List[Dict]:
        """
        Get unique contributors who modified a file.
        
        Args:
            file_path: Path to file
        
        Returns:
            List of author dictionaries with name, email, commit_count
        
        Requirement: 8.4
        """
        try:
            validated_path = self._validate_file_path(file_path)
            relative_path = validated_path.relative_to(self.repo_path)
            
            # Get all commits for file
            commits = list(self.repo.iter_commits(paths=str(relative_path)))
            
            # Count contributions by author
            author_stats = {}
            for commit in commits:
                author_key = (commit.author.name, commit.author.email)
                if author_key not in author_stats:
                    author_stats[author_key] = {
                        "name": commit.author.name,
                        "email": commit.author.email,
                        "commit_count": 0,
                        "first_commit": commit.committed_date,
                        "last_commit": commit.committed_date
                    }
                
                author_stats[author_key]["commit_count"] += 1
                author_stats[author_key]["last_commit"] = max(
                    author_stats[author_key]["last_commit"],
                    commit.committed_date
                )
                author_stats[author_key]["first_commit"] = min(
                    author_stats[author_key]["first_commit"],
                    commit.committed_date
                )
            
            # Convert to list and add formatted timestamps
            result = []
            for stats in author_stats.values():
                stats["first_commit"] = datetime.fromtimestamp(stats["first_commit"])
                stats["last_commit"] = datetime.fromtimestamp(stats["last_commit"])
                result.append(stats)
            
            # Sort by commit count (most contributions first)
            result.sort(key=lambda x: x["commit_count"], reverse=True)
            return result
        
        except Exception as e:
            return self._handle_git_error(e, "get_file_authors", return_empty=True)
    
    def get_file_blame(self, file_path: str) -> List[Dict]:
        """
        Get line-by-line authorship information.
        
        Args:
            file_path: Path to file
        
        Returns:
            List of blame info dicts with line_num, hash, author, timestamp
        
        Requirement: 9
        """
        try:
            validated_path = self._validate_file_path(file_path)
            relative_path = validated_path.relative_to(self.repo_path)
            
            # Check if file exists
            if not validated_path.exists():
                return []
            
            # Get blame data
            blame_data = self.repo.blame('HEAD', str(relative_path))
            
            results = []
            line_num = 1
            
            for commit, lines in blame_data:
                for line in lines:
                    results.append({
                        "line_num": line_num,
                        "hash": commit.hexsha,
                        "short_hash": commit.hexsha[:7],
                        "author": commit.author.name,
                        "email": commit.author.email,
                        "timestamp": datetime.fromtimestamp(commit.committed_date),
                        "line_content": line
                    })
                    line_num += 1
            
            return results
        
        except git.exc.GitCommandError as e:
            # Handle files not in git history
            if "no such path" in str(e).lower():
                # File is new/uncommitted
                if validated_path.exists():
                    with open(validated_path, 'r') as f:
                        lines = f.readlines()
                    return [
                        {
                            "line_num": i + 1,
                            "hash": "uncommitted",
                            "short_hash": "uncommit",
                            "author": "Uncommitted",
                            "email": "",
                            "timestamp": datetime.now(),
                            "line_content": line
                        }
                        for i, line in enumerate(lines)
                    ]
            return []
        
        except Exception as e:
            return self._handle_git_error(e, "get_file_blame", return_empty=True)
    
    def get_workspace_diff(self) -> Dict[str, List[str]]:
        """
        Get uncommitted changes in workspace.
        
        Returns:
            Dictionary with modified, added, deleted, staged, unstaged file lists
        
        Requirement: 10
        """
        try:
            result = {
                "modified": [],
                "added": [],
                "deleted": [],
                "staged": [],
                "unstaged": []
            }
            
            # Get unstaged changes (working directory vs index)
            diff_unstaged = self.repo.index.diff(None)
            for diff_item in diff_unstaged:
                file_path = diff_item.a_path or diff_item.b_path
                
                if diff_item.change_type == 'M':
                    result["modified"].append(file_path)
                    result["unstaged"].append(file_path)
                elif diff_item.change_type == 'D':
                    result["deleted"].append(file_path)
                    result["unstaged"].append(file_path)
            
            # Get staged changes (index vs HEAD)
            try:
                diff_staged = self.repo.index.diff("HEAD")
                for diff_item in diff_staged:
                    file_path = diff_item.a_path or diff_item.b_path
                    
                    if diff_item.change_type == 'A':
                        result["added"].append(file_path)
                        result["staged"].append(file_path)
                    elif diff_item.change_type == 'M':
                        if file_path not in result["modified"]:
                            result["modified"].append(file_path)
                        result["staged"].append(file_path)
                    elif diff_item.change_type == 'D':
                        if file_path not in result["deleted"]:
                            result["deleted"].append(file_path)
                        result["staged"].append(file_path)
            except git.exc.BadName:
                # No HEAD (empty repository)
                pass
            
            # Get untracked files
            untracked = self.repo.untracked_files
            for file_path in untracked:
                # Respect .gitignore
                if not self._is_ignored(file_path):
                    result["added"].append(file_path)
            
            return result
        
        except Exception as e:
            return self._handle_git_error(
                e, "get_workspace_diff",
                return_empty=True,
                default_value={"modified": [], "added": [], "deleted": [], "staged": [], "unstaged": []}
            )
    
    def _validate_file_path(self, file_path: str) -> Path:
        """
        Ensure file path is within repository.
        
        Args:
            file_path: Path to validate
        
        Returns:
            Resolved Path object
        
        Raises:
            GitInspectorError: If path is outside repository
        
        Requirement: 16.3
        """
        path = Path(file_path)
        
        # Handle relative paths
        if not path.is_absolute():
            path = (self.repo_path / path).resolve()
        
        # Check if within repository
        try:
            path.relative_to(self.repo_path)
        except ValueError:
            raise GitInspectorError(
                f"File path is outside repository: {file_path}"
            )
        
        return path
    
    def _is_ignored(self, file_path: str) -> bool:
        """Check if file matches .gitignore patterns"""
        try:
            # GitPython check if file is ignored
            return self.repo.ignored(file_path)
        except:
            return False
    
    def _handle_git_error(
        self,
        error: Exception,
        operation: str,
        return_empty: bool = False,
        default_value = None
    ):
        """
        Handle and wrap GitPython exceptions.
        
        Args:
            error: The exception that occurred
            operation: Name of operation that failed
            return_empty: If True, return empty list instead of raising
            default_value: Value to return if return_empty is True
        
        Raises:
            GitInspectorError: Wrapped exception with context
        
        Requirement: 16.4
        """
        error_message = f"Git operation '{operation}' failed: {str(error)}"
        
        if return_empty:
            # Log error but return empty result
            import logging
            logging.warning(error_message)
            return default_value if default_value is not None else []
        else:
            raise GitInspectorError(error_message) from error
    
    def get_repo_info(self) -> Dict:
        """
        Get general repository information.
        
        Returns:
            Dictionary with repo stats
        """
        try:
            return {
                "path": str(self.repo_path),
                "current_branch": self.repo.active_branch.name,
                "head_commit": self.repo.head.commit.hexsha[:7],
                "is_dirty": self.repo.is_dirty(),
                "untracked_count": len(self.repo.untracked_files),
                "remotes": [remote.name for remote in self.repo.remotes]
            }
        except Exception as e:
            return {
                "path": str(self.repo_path),
                "error": str(e)
            }
