from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name="书名")
    author = models.CharField(max_length=100, verbose_name="作者")
    isbn = models.CharField(max_length=20, unique=True, verbose_name="ISBN")
    publish_date = models.DateField(verbose_name="出版日期")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")
    is_borrowed = models.BooleanField(default=False, verbose_name="是否借出")
    
    
    def __str__(self):
        return self.title


class BorrowRecord(models.Model):
    # 关联用户：谁借的书
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_records')
    # 关联书籍：借的哪本书
    book = models.ForeignKey('Book', on_delete=models.CASCADE, related_name='borrow_history')
    # 时间记录
    borrow_date = models.DateTimeField(auto_now_add=True, verbose_name="借书时间")
    return_date = models.DateTimeField(null=True, blank=True, verbose_name="还书时间")

    def __str__(self):
        return f"{self.user.username} 借阅了 {self.book.title}"