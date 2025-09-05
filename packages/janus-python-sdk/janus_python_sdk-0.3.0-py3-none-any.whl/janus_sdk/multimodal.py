from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import base64

@dataclass
class FileAttachment:
    name: str
    content: bytes
    mime_type: str
    size: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "content": base64.b64encode(self.content).decode('utf-8'),
            "mime_type": self.mime_type,
            "size": self.size
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileAttachment':
        return cls(
            name=data["name"],
            content=base64.b64decode(data["content"]),
            mime_type=data["mime_type"],
            size=data["size"]
        )

@dataclass
class MultimodalOutput:
    text: Optional[str] = None
    json_data: Optional[Dict[str, Any]] = None
    files: Optional[List[FileAttachment]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_string(cls, text: str) -> 'MultimodalOutput':
        """Backward compatibility: convert string to MultimodalOutput"""
        return cls(text=text)
    
    def to_string(self) -> str:
        """Convert to string for backward compatibility"""
        if self.text:
            return self.text
        elif self.json_data:
            return str(self.json_data)
        else:
            return str(self.to_dict())
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.text is not None:
            result["text"] = self.text
        if self.json_data is not None:
            result["json_data"] = self.json_data
        if self.files is not None:
            result["files"] = [f.to_dict() for f in self.files]
        if self.metadata is not None:
            result["metadata"] = self.metadata
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MultimodalOutput':
        files = None
        if "files" in data and data["files"]:
            files = [FileAttachment.from_dict(f) for f in data["files"]]
        
        return cls(
            text=data.get("text"),
            json_data=data.get("json_data"),
            files=files,
            metadata=data.get("metadata")
        )
