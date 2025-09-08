from dataclasses import dataclass

@dataclass
class Session:
    id: str

@dataclass
class Message:
    id: str
    role: str
    content: str
