"""
Parser for unified diff format.
Extracts changed files and their modifications from PR diffs.
"""
import re
from typing import List, Dict, Set
from dataclasses import dataclass


@dataclass
class FileChange:
    """Represents a changed file in a diff."""
    
    file_path: str
    old_path: str
    new_path: str
    change_type: str  # added, modified, deleted, renamed
    additions: int
    deletions: int
    changed_lines: List[int]  # Line numbers that were changed


class DiffParser:
    """Parser for unified diff format."""
    
    def __init__(self, diff_text: str):
        self.diff_text = diff_text
        self.file_changes: List[FileChange] = []
    
    def parse(self) -> List[FileChange]:
        """
        Parse the diff text and extract file changes.
        
        Returns:
            List of FileChange objects
        """
        # Split diff into file sections
        file_sections = self._split_into_files()
        
        for section in file_sections:
            file_change = self._parse_file_section(section)
            if file_change:
                self.file_changes.append(file_change)
        
        return self.file_changes
    
    def _split_into_files(self) -> List[str]:
        """Split diff text into individual file sections."""
        # Split on "diff --git" markers
        sections = re.split(r'^diff --git ', self.diff_text, flags=re.MULTILINE)
        # Remove empty first section
        return [s for s in sections if s.strip()]
    
    def _parse_file_section(self, section: str) -> FileChange:
        """Parse a single file section from the diff."""
        lines = section.split('\n')
        
        # Extract file paths from first line (e.g., "a/file.py b/file.py")
        first_line = lines[0] if lines else ""
        file_match = re.match(r'a/(.*?) b/(.*?)(?:\s|$)', first_line)
        
        if not file_match:
            return None
        
        old_path = file_match.group(1)
        new_path = file_match.group(2)
        
        # Determine change type
        change_type = self._determine_change_type(section, old_path, new_path)
        
        # Use new_path as primary, fallback to old_path for deletions
        file_path = new_path if new_path != '/dev/null' else old_path
        
        # Count additions and deletions
        additions = 0
        deletions = 0
        changed_lines = []
        current_line = 0
        
        for line in lines:
            # Track line numbers from @@ markers
            hunk_match = re.match(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
            if hunk_match:
                current_line = int(hunk_match.group(1))
                continue
            
            # Count changes
            if line.startswith('+') and not line.startswith('+++'):
                additions += 1
                changed_lines.append(current_line)
                current_line += 1
            elif line.startswith('-') and not line.startswith('---'):
                deletions += 1
            elif not line.startswith('\\'):  # Ignore "\ No newline" markers
                current_line += 1
        
        return FileChange(
            file_path=file_path,
            old_path=old_path,
            new_path=new_path,
            change_type=change_type,
            additions=additions,
            deletions=deletions,
            changed_lines=changed_lines
        )
    
    def _determine_change_type(self, section: str, old_path: str, new_path: str) -> str:
        """Determine the type of change (added, modified, deleted, renamed)."""
        if old_path == '/dev/null':
            return 'added'
        elif new_path == '/dev/null':
            return 'deleted'
        elif old_path != new_path:
            return 'renamed'
        else:
            return 'modified'
    
    def get_changed_files(self) -> List[str]:
        """Get list of changed file paths."""
        return [fc.file_path for fc in self.file_changes]
    
    def get_modified_files(self) -> List[str]:
        """Get list of modified (not added/deleted) file paths."""
        return [
            fc.file_path 
            for fc in self.file_changes 
            if fc.change_type in ['modified', 'renamed']
        ]
    
    def get_change_summary(self) -> Dict[str, int]:
        """Get summary of changes."""
        return {
            'total_files': len(self.file_changes),
            'added': sum(1 for fc in self.file_changes if fc.change_type == 'added'),
            'modified': sum(1 for fc in self.file_changes if fc.change_type == 'modified'),
            'deleted': sum(1 for fc in self.file_changes if fc.change_type == 'deleted'),
            'renamed': sum(1 for fc in self.file_changes if fc.change_type == 'renamed'),
            'total_additions': sum(fc.additions for fc in self.file_changes),
            'total_deletions': sum(fc.deletions for fc in self.file_changes)
        }

# Made with Bob
