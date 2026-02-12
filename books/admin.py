# books/admin.py
from django.contrib import admin
from .models import Book, BorrowRecord

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # 列表页显示的列：ID、书名、是否借出
    list_display = ('id', 'title', 'is_borrowed')
    # 搜索框：支持按 ID 或书名搜索（复用你的全能查询逻辑）
    search_fields = ('id', 'title') 
    # 右侧过滤器：按借阅状态筛选
    list_filter = ('is_borrowed',)

@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    # 显示谁借了哪本书，以及时间
    list_display = ('user', 'book', 'borrow_date', 'return_date')
    # 按照借书人搜索
    search_fields = ('user__username', 'book__title')