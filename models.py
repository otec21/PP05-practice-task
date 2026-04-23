from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Category:
    """Модель категории"""
    id: int
    name: str
    
    def __str__(self):
        return self.name

@dataclass
class Expense:
    """Модель расхода"""
    id: Optional[int]
    amount: float
    category: str
    comment: str
    date: date
    
    def __post_init__(self):
        """Валидация данных"""
        if self.amount <= 0:
            raise ValueError("Сумма должна быть положительной")
        if not self.category:
            raise ValueError("Категория не может быть пустой")
        if len(self.comment) > 200:
            raise ValueError("Комментарий слишком длинный (макс. 200 символов)")
    
    def to_dict(self):
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'amount': self.amount,
            'category': self.category,
            'comment': self.comment,
            'date': self.date.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создание из словаря"""
        return cls(
            id=data.get('id'),
            amount=data['amount'],
            category=data['category'],
            comment=data['comment'],
            date=date.fromisoformat(data['date'])
        )
