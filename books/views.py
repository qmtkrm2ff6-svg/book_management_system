from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404
from drf_yasg import openapi
from .models import BorrowRecord
import datetime
from .models import Book
from .serializers import BookSerializer, RegisterSerializer
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    # 核心：定义全能参数描述
    id_param = openapi.Parameter(
        'id', openapi.IN_PATH, 
        description="可以是数字 ID，也可以是书名关键词", 
        type=openapi.TYPE_STRING 
    )
    
    def get_object(self):
        lookup_value = self.kwargs.get('pk')

        # 1. 精确匹配：如果是数字 ID
        if lookup_value.isdigit():
            try:
                return super().get_object()
            except Http404:
                pass
        
        # 2. 模糊查询匹配集
        queryset = Book.objects.filter(Q(title__icontains=lookup_value))
        count = queryset.count()

        if count == 1:
            # 刚好只搜到一本，直接返回
            return queryset.first()
        elif count > 1:
            # 搜到了多本，抛出错误提示用户输入更精确一点
            titles = "、".join([b.title for b in queryset[:3]]) # 列出前三个作为参考
            raise Http404(f"搜到了 {count} 本书（如：{titles}...），请提供更准确的书名或直接输入 ID。")
        
        # 3. 啥也没搜到
        raise Http404(f"找不到匹配 '{lookup_value}' 的书籍")


    def get_permissions(self):
        """管理员与普通用户权限区分"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        else:
            return [IsAuthenticated()]


    @swagger_auto_schema(manual_parameters=[id_param])
    def retrieve(self, request, *args, **kwargs): 
        lookup_value = self.kwargs.get('pk')

        # 1. 优先尝试数字 ID 精确匹配
        if lookup_value.isdigit():
            try:
                instance = super().get_object()
                serializer = self.get_serializer(instance)
                return Response(serializer.data)
            except Http404:
                # ID 没搜到，继续往下走模糊匹配
                pass

        # 2. 核心修改：关键词模糊匹配所有符合条件的书
        # 使用 filter() 而不是 get()，这样能拿到一个结果集（QuerySet）
        queryset = Book.objects.filter(Q(title__icontains=lookup_value))
        
        if queryset.exists():
            # 关键点：many=True 会让 Django 返回一个标准的 JSON 数组 []
            # Swagger 看到数组会自动渲染出带滚动条的整齐列表，包含所有字段
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        # 3. 如果 ID 和书名都对不上，才报 404
        raise Http404(f"找不到 ID 或标题匹配 '{lookup_value}' 的书籍")

    # 1. 修改后的借书接口：隐藏 data 框 + 允许字符串 ID
    @swagger_auto_schema(
        manual_parameters=[id_param], 
        request_body=None, 
    )
    @action(detail=True, methods=['post'], serializer_class=None)
    def borrow(self, request, pk=None):
        book = self.get_object()
        if book.is_borrowed:
            return Response({'status': '这本书已经被借走了'}, status=status.HTTP_400_BAD_REQUEST)
        book.is_borrowed = True
        book.save()

        BorrowRecord.objects.create(
            user=request.user,  # 当前登录的用户
            book=book
        )

        return Response({
            'status': '借书成功',
            'book': book.title,
            'user': request.user.username
        })

    
        
    # 3. 修改后的还书接口：隐藏 data 框 + 允许字符串 ID
    @swagger_auto_schema(
        manual_parameters=[id_param], 
        request_body=None, 
    )
    @action(detail=True, methods=['post'], serializer_class=None)
    def return_book(self, request, pk=None):
        book = self.get_object()
        if not book.is_borrowed:
            return Response({'status': '这本书本来就在馆内'}, status=status.HTTP_400_BAD_REQUEST)     
        book.is_borrowed = False
        book.save()
        record = BorrowRecord.objects.filter(book=book, return_date__isnull=True).last()
        if record:
            record.return_date = datetime.datetime.now()
            record.save()

        return Response({'status': '还书成功', 'user': request.user.username})

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


def book_list_page(request):
    # 1. 获取搜索关键词 (复用你之前的全能查询逻辑)
    query = request.GET.get('q', '')
    
    if query:
        # 这里可以直接套用你之前的“ID + 关键词”逻辑
        if query.isdigit():
            books = Book.objects.filter(id=query)
        else:
            books = Book.objects.filter(title__icontains=query)
    else:
        books = Book.objects.all()
    
    # 2. 返回模板，并把数据塞进去
    return render(request, 'book_list.html', {'books': books, 'query': query})



# 确保以下函数不在类里面，且顶格写
# --- 文件最底部 ---

def book_list_page(request):
    query = request.GET.get('q', '')
    if query:
        if query.isdigit():
            books = Book.objects.filter(id=query)
        else:
            books = Book.objects.filter(title__icontains=query)
    else:
        books = Book.objects.all()
    # 确保 return 后面没有其他东西，且缩进正确
    return render(request, 'book_list.html', {'books': books, 'query': query})

@login_required
def borrow_book_web(request, pk):
    # 借书逻辑
    book = Book.objects.get(pk=pk)
    if not book.is_borrowed:
        book.is_borrowed = True
        book.save()
        from .models import BorrowRecord # 确保导入了模型
        BorrowRecord.objects.create(user=request.user, book=book)
    return redirect('book-list-web')

@login_required
def return_book_web(request, pk):
    # 还书逻辑
    book = Book.objects.get(pk=pk)
    if book.is_borrowed:
        book.is_borrowed = False
        book.save()
        from .models import BorrowRecord
        record = BorrowRecord.objects.filter(book=book, return_date__isnull=True).last()
        if record:
            import datetime
            record.return_date = datetime.datetime.now()
            record.save()
    return redirect('book-list-web')

# books/views.py

def index_portal(request):
    """图书馆门户大厅视图"""
    return render(request, 'index.html')

@login_required
def my_borrow_history(request):
    """展示当前登录用户的借阅历史"""
    # 这里的 filter(user=request.user) 保证了隐私安全
    records = BorrowRecord.objects.filter(user=request.user).order_by('-borrow_date')
    return render(request, 'borrow_history.html', {'records': records})




def register_view(request):
    """用户注册视图"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'账号 {username} 创建成功，请登录！')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})