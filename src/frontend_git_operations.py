"""
Git operations for the frontend directory.
Handles git initialization, commits, and pushes for the frontend repository.
"""
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import shutil
from src.error_logger import get_logger


class FrontendGitOperations:
    """
    Manages git operations for the frontend directory.
    Supports both incremental commits and fresh repo initialization.
    """
    
    def __init__(self, frontend_dir: str = "frontend"):
        """
        Initialize the git operations manager.
        
        Args:
            frontend_dir: Path to the frontend directory (relative or absolute)
        """
        self.frontend_dir = Path(frontend_dir).resolve()
        self.git_dir = self.frontend_dir / ".git"
        self.logger = get_logger()
    
    def has_git_repo(self) -> bool:
        """
        Check if the frontend directory has a git repository.
        
        Returns:
            True if .git directory exists, False otherwise
        """
        return self.git_dir.exists() and self.git_dir.is_dir()
    
    def remove_git_repo(self) -> bool:
        """
        Remove the .git directory from frontend.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.has_git_repo():
                shutil.rmtree(self.git_dir)
                return True
            return True  # Already removed
        except Exception as e:
            self.logger.error(f"Failed to remove .git directory: {e}")
            return False
    
    def init_repo(self, force: bool = False) -> Tuple[bool, str]:
        """
        Initialize a git repository in the frontend directory.
        
        Args:
            force: If True, removes existing .git directory first
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if force and self.has_git_repo():
                if not self.remove_git_repo():
                    return False, "Failed to remove existing .git directory"
            
            # Initialize git repo
            result = subprocess.run(
                ["git", "init"],
                cwd=self.frontend_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return True, "Git repository initialized"
        
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to initialize git repo: {e.stderr}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Failed to initialize git repo: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def add_remote(self, remote_url: str, remote_name: str = "origin") -> Tuple[bool, str]:
        """
        Add a remote to the git repository.
        
        Args:
            remote_url: URL of the remote repository
            remote_name: Name of the remote (default: origin)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Check if remote already exists
            result = subprocess.run(
                ["git", "remote", "get-url", remote_name],
                cwd=self.frontend_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Remote exists, update it
                subprocess.run(
                    ["git", "remote", "set-url", remote_name, remote_url],
                    cwd=self.frontend_dir,
                    capture_output=True,
                    text=True,
                    check=True
                )
                return True, f"Remote '{remote_name}' updated"
            else:
                # Remote doesn't exist, add it
                subprocess.run(
                    ["git", "remote", "add", remote_name, remote_url],
                    cwd=self.frontend_dir,
                    capture_output=True,
                    text=True,
                    check=True
                )
                return True, f"Remote '{remote_name}' added"
        
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to add/update remote: {e.stderr}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Failed to add/update remote: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def add_all(self) -> Tuple[bool, str]:
        """
        Stage all changes in the frontend directory.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            subprocess.run(
                ["git", "add", "."],
                cwd=self.frontend_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return True, "All changes staged"
        
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to stage changes: {e.stderr}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Failed to stage changes: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def commit(self, message: str) -> Tuple[bool, str]:
        """
        Create a commit with the given message.
        
        Args:
            message: Commit message
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.frontend_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return True, "Commit created"
        
        except subprocess.CalledProcessError as e:
            # Check if error is because nothing to commit
            if "nothing to commit" in e.stdout or "nothing to commit" in e.stderr:
                return True, "No changes to commit"
            error_msg = f"Failed to create commit: {e.stderr}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Failed to create commit: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def push(self, remote_name: str = "origin", branch: str = "main", force: bool = False) -> Tuple[bool, str]:
        """
        Push commits to the remote repository.
        
        Args:
            remote_name: Name of the remote (default: origin)
            branch: Branch name (default: main)
            force: If True, force push (default: False)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            cmd = ["git", "push"]
            if force:
                cmd.append("--force")
            cmd.extend([remote_name, branch])
            
            subprocess.run(
                cmd,
                cwd=self.frontend_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return True, f"Pushed to {remote_name}/{branch}"
        
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to push: {e.stderr}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Failed to push: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def add_commit_push_incremental(
        self,
        commit_message: str,
        remote_url: Optional[str] = None,
        remote_name: str = "origin",
        branch: str = "main"
    ) -> Tuple[bool, str]:
        """
        Incremental approach: Add, commit, and push changes to existing repo.
        
        Args:
            commit_message: Message for the commit
            remote_url: Optional remote URL to set/update
            remote_name: Name of the remote (default: origin)
            branch: Branch name (default: main)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Ensure repo exists
        if not self.has_git_repo():
            success, msg = self.init_repo()
            if not success:
                return False, msg
        
        # Set remote if provided
        if remote_url:
            success, msg = self.add_remote(remote_url, remote_name)
            if not success:
                return False, msg
        
        # Add all changes
        success, msg = self.add_all()
        if not success:
            return False, msg
        
        # Commit
        success, msg = self.commit(commit_message)
        if not success:
            return False, msg
        
        # Push
        success, msg = self.push(remote_name, branch)
        return success, msg
    
    def add_commit_push_fresh(
        self,
        commit_message: str,
        remote_url: str,
        remote_name: str = "origin",
        branch: str = "main"
    ) -> Tuple[bool, str]:
        """
        Fresh approach: Remove .git, init, add origin, add, commit, push (force).
        This keeps the repo size smaller by removing all history.
        
        Args:
            commit_message: Message for the commit
            remote_url: Remote URL
            remote_name: Name of the remote (default: origin)
            branch: Branch name (default: main)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Remove existing .git and reinitialize
        success, msg = self.init_repo(force=True)
        if not success:
            return False, msg
        
        # Add remote
        success, msg = self.add_remote(remote_url, remote_name)
        if not success:
            return False, msg
        
        # Add all changes
        success, msg = self.add_all()
        if not success:
            return False, msg
        
        # Commit
        success, msg = self.commit(commit_message)
        if not success:
            return False, msg
        
        # Force push (since we're rewriting history)
        success, msg = self.push(remote_name, branch, force=True)
        return success, msg
