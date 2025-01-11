from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


# Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255, blank=True, null=True)  # Tên hiển thị
    is_admin = models.BooleanField(default=False)  # Kiểm tra quyền admin

    def __str__(self):
        return self.display_name or self.user.username


# Post Model
class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/images/', null=True, blank=True)  # Hình ảnh
    document = models.FileField(upload_to='posts/documents/', null=True, blank=True)  # Tài liệu
    video = models.FileField(upload_to='posts/videos/', null=True, blank=True)  # Video (Thêm mới)
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(default=now)  # Thời gian bài viết được tạo
    updated_at = models.DateTimeField(auto_now=True)  # Thời gian bài viết được cập nhật
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def likes_count(self):
        """Trả về số lượt thích bài đăng."""
        return self.likes.count()

    def comments_count(self):
        """Trả về số lượng bình luận của bài đăng."""
        return self.comments.count()

    def created_at_formatted(self):
        """Trả về thời gian đăng bài viết ở định dạng dễ đọc."""
        return self.created_at.strftime('%H:%M %d/%m/%Y')

    def updated_at_formatted(self):
        """Trả về thời gian cập nhật bài viết ở định dạng dễ đọc."""
        return self.updated_at.strftime('%H:%M %d/%m/%Y')

    def has_media(self):
        """Kiểm tra xem bài đăng có phương tiện nào không."""
        return self.image or self.document or self.video

    def __str__(self):
        return self.title


# Comment Model
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(default=now)  # Thời gian bình luận được tạo
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)

    def likes_count(self):
        """Trả về số lượt thích bình luận."""
        return self.likes.count()

    def created_at_formatted(self):
        """Trả về thời gian đăng bình luận ở định dạng dễ đọc."""
        return self.created_at.strftime('%H:%M %d/%m/%Y')

    def __str__(self):
        return f"Comment by {self.author} on {self.post.title}"


# Product Model
class Product(models.Model):
    title = models.CharField(max_length=255)
    thumbnail = models.URLField()  # URL hình ảnh thumbnail
    preview_link = models.URLField()  # Link xem trước sản phẩm
    raw_price = models.IntegerField()  # Giá sản phẩm (dạng số)
    formatted_price = models.CharField(max_length=50)  # Giá sản phẩm (dạng văn bản)
    is_successful = models.BooleanField(default=False)  # Trạng thái thành công
    order_code = models.CharField(max_length=50, null=True, blank=True)  # Mã đơn hàng

    def __str__(self):
        return self.title
