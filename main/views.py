from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import localtime
from django.core.paginator import Paginator
from django.http import FileResponse
import requests
import random
import json
from .models import Profile, Post, Comment, Product
from payos import PayOS, PaymentData


# API URLs
API_URL = "https://www.googleapis.com/books/v1/volumes"
OAUTH_API_URL = "https://sinhvien1.tlu.edu.vn/education/oauth/token"

# PayOS Configuration
payOS = PayOS(
    client_id="645fef69-027b-46a3-baaf-80c5a0033913",
    api_key="7341bfe3-e34b-4442-8372-7acdd1ac343f",
    checksum_key="a835449be303b3acb626c401c5dc45b65bc1db4c1f4dc96fa40eea9b5c1c8b38"
)

# Helper functions
def generate_random_price():
    return random.randint(50000, 500000)

def format_price(price):
    return f"{price:,} VND"

def login_and_get_token(login_url, username, password):
    """
    Authenticate user with external API and return token and user details (e.g., displayName).
    """
    data = {
        'grant_type': 'password',
        'username': username,
        'password': password,
        'client_id': 'education_client',  # Ensure this is correct
        'client_secret': 'password'      # Ensure this is correct
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    try:
        response = requests.post(login_url, data=data, headers=headers, verify=False)
        response.raise_for_status()
        token = response.json().get('access_token')
        
        # Lấy thông tin chi tiết người dùng từ API trường (ví dụ: displayName)
        if token:
            user_info_url = "https://sinhvien1.tlu.edu.vn/education/api/student/getstudentbylogin"
            user_info_headers = {
                'Authorization': f'Bearer {token}'
            }
            user_info_response = requests.get(user_info_url, headers=user_info_headers, verify=False)
            user_info_response.raise_for_status()
            user_data = user_info_response.json()

            # Trả về token và tên người dùng (displayName)
            display_name = user_data.get('displayName', '')
            return token, display_name

    except requests.exceptions.RequestException as e:
        print(f"API Login Error: {e}")
        return None, None



def home(request):
    query = request.GET.get('query', '').strip()  # Lấy từ khóa tìm kiếm và loại bỏ khoảng trắng
    error_message = None

    # Gọi API để lấy dữ liệu và import vào cơ sở dữ liệu (trong mọi trường hợp)
    try:
        if query:
            # Nếu có query tìm kiếm, gọi API với query
            response = requests.get(f"{API_URL}?q={query}")
        else:
            # Nếu không có query, gọi API để lấy dữ liệu ngẫu nhiên
            response = requests.get(f"{API_URL}?q=education+OR+learning+OR+study+materials")
        
        response.raise_for_status()  # Kiểm tra nếu có lỗi trong quá trình gọi API
        data = response.json()
        items = data.get('items', [])

        # Thêm các sản phẩm tìm được từ API vào cơ sở dữ liệu
        for item in items:
            volume_info = item.get('volumeInfo', {})
            thumbnail = volume_info.get('imageLinks', {}).get('thumbnail', 'https://via.placeholder.com/150')
            title = volume_info.get('title', 'Sản phẩm không có tên')
            preview_link = volume_info.get('previewLink', '#')
            raw_price = generate_random_price()

            # Kiểm tra xem sản phẩm đã tồn tại chưa, nếu chưa thì tạo mới
            if not Product.objects.filter(preview_link=preview_link).exists():
                Product.objects.create(
                    title=title,
                    thumbnail=thumbnail,
                    preview_link=preview_link,
                    raw_price=raw_price,
                    formatted_price=format_price(raw_price),
                    is_successful=False
                )
    except requests.exceptions.RequestException as e:
        error_message = f"Không thể kết nối tới API: {str(e)}"

    # Lấy danh sách sản phẩm sau khi gọi API
    products = Product.objects.all()

    if query:
        # Nếu có query tìm kiếm, lọc sản phẩm theo từ khóa
        products = products.filter(title__icontains=query)

        # Nếu không có sản phẩm nào phù hợp với từ khóa
        if not products.exists():
            error_message = f"Không có sản phẩm nào phù hợp với từ khóa '{query}'."

    # Phân trang sản phẩm
    paginator = Paginator(products, 10)  # Giới hạn 10 sản phẩm mỗi trang
    page_number = request.GET.get('page', 1)  # Lấy số trang từ URL, mặc định là trang 1
    page_obj = paginator.get_page(page_number)  # Lấy các sản phẩm của trang hiện tại

    # Trả về kết quả cho giao diện
    return render(request, 'dashboard.html', {
        'products': page_obj,  # Truyền các sản phẩm của trang hiện tại vào template
        'query': query,  # Truyền từ khóa tìm kiếm vào template
        'error_message': error_message,  # Truyền thông báo lỗi (nếu có)
    })




def login_view(request):
    """
    Đăng nhập và chuyển hướng về URL trước đó nếu có.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Kiểm tra nếu tài khoản là admin
        if username == 'admin' and password == 'admin':
            user = User.objects.filter(username=username).first()
            if not user:
                # Tạo người dùng admin nếu chưa tồn tại
                user = User.objects.create_superuser(username=username, password=password)
            login(request, user)
            return redirect('/dashboard/')  # Chuyển hướng đến dashboard

        # Xác thực người dùng thông thường
        token, display_name = login_and_get_token(OAUTH_API_URL, username, password)
        if token:
            request.session['access_token'] = token
            request.session['username'] = username
            request.session['display_name'] = display_name

            user = User.objects.filter(username=username).first()
            if not user:
                user = User.objects.create_user(username=username, password=password)
                user.profile = Profile.objects.create(user=user, display_name=display_name)
            else:
                if not hasattr(user, 'profile'):
                    user.profile = Profile.objects.create(user=user, display_name=display_name)
                else:
                    user.profile.display_name = display_name
                    user.profile.save()

            request.session['is_admin'] = user.is_staff
            login(request, user)

            # Điều hướng đến URL "next" hoặc về trang dashboard
            next_url = request.GET.get('next', '/dashboard/')
            return redirect(next_url)

        messages.error(request, "Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.")
    return render(request, 'login.html')



def logout_view(request):
    logout(request)
    messages.success(request, "Bạn đã đăng xuất thành công.")
    return redirect('home')  # Redirect to /login/ explicitly

@login_required
def dashboard_view(request):
    query = request.GET.get('query', '').strip()  # Lấy từ khóa tìm kiếm và loại bỏ khoảng trắng
    error_message = None

    try:
        # Luôn luôn gọi API để lấy dữ liệu
        response = requests.get(f"{API_URL}?q=education+OR+learning+OR+study+materials")
        response.raise_for_status()
        data = response.json()
        items = data.get('items', [])

        # Lặp qua tất cả các sản phẩm và kiểm tra nếu chưa có trong cơ sở dữ liệu thì thêm vào
        for item in items:
            volume_info = item.get('volumeInfo', {})
            thumbnail = volume_info.get('imageLinks', {}).get('thumbnail', 'https://via.placeholder.com/150')
            title = volume_info.get('title', 'Sản phẩm không có tên')
            preview_link = volume_info.get('previewLink', '#')
            raw_price = generate_random_price()

            # Kiểm tra xem sản phẩm đã tồn tại chưa, nếu chưa thì tạo mới
            if not Product.objects.filter(preview_link=preview_link).exists():
                Product.objects.create(
                    title=title,
                    thumbnail=thumbnail,
                    preview_link=preview_link,
                    raw_price=raw_price,
                    formatted_price=format_price(raw_price),
                    is_successful=False
                )
    except requests.exceptions.RequestException as e:
        error_message = f"Không thể kết nối tới API: {str(e)}"

    # Lấy tất cả sản phẩm từ cơ sở dữ liệu
    products = Product.objects.all()

    # Nếu có query, chỉ lấy các sản phẩm có tên chứa từ khóa tìm kiếm
    if query:
        products = products.filter(title__icontains=query)

        # Nếu không có sản phẩm nào phù hợp với từ khóa
        if not products.exists():
            error_message = f"Không có sản phẩm nào phù hợp với từ khóa '{query}'."

    # Phân trang sản phẩm
    paginator = Paginator(products, 10)  # Giới hạn 10 sản phẩm mỗi trang
    page_number = request.GET.get('page', 1)  # Lấy số trang từ URL, mặc định là trang 1
    page_obj = paginator.get_page(page_number)  # Lấy các sản phẩm của trang hiện tại

    # Trả về kết quả cho giao diện
    return render(request, 'dashboard.html', {
        'products': page_obj,  # Truyền các sản phẩm của trang hiện tại vào template
        'query': query,  # Truyền từ khóa tìm kiếm vào template
        'error_message': error_message,  # Truyền thông báo lỗi (nếu có)
    })

def forum_home(request):
    posts = Post.objects.all().order_by('-created_at')  # Lấy danh sách bài đăng
    return render(request, 'forum_home.html', {'posts': posts})


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    return render(request, 'post_detail.html', {'post': post, 'comments': comments})

@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        document = request.FILES.get('document')
        video = request.FILES.get('video')
        Post.objects.create(
            title=title,
            content=content,
            image=image,
            document=document,
            video=video,
            author=request.user
        )
        return redirect('forum_home')
    return render(request, 'create_post.html')

@login_required
def add_comment(request, post_id):
    """
    Thêm bình luận vào bài đăng.
    """
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
            if not content:
                return JsonResponse({'success': False, 'error': 'Nội dung bình luận không được để trống.'})

            # Tạo bình luận
            comment = Comment.objects.create(content=content, author=request.user, post=post)

            return JsonResponse({
                'success': True,
                'author': request.user.username,
                'content': comment.content,
                'created_at': localtime(comment.created_at).strftime('%H:%M %d/%m/%Y'),
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Lỗi: {str(e)}'})
    else:
        return JsonResponse({'success': False, 'error': 'Phương thức không hợp lệ.'})



@login_required
def like_post(request, post_id):
    """
    Xử lý thích hoặc bỏ thích bài đăng.
    """
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        if request.user in post.likes.all():
            post.likes.remove(request.user)  # Hủy thích
            liked = False
        else:
            post.likes.add(request.user)  # Thích bài viết
            liked = True

        # Trả về JSON để xử lý giao diện
        return JsonResponse({'likes_count': post.likes.count(), 'liked': liked})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def like_comment(request, comment_id):
    """
    Xử lý thích hoặc bỏ thích bình luận.
    """
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == "POST":
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)  # Hủy thích
            liked = False
        else:
            comment.likes.add(request.user)  # Thích bình luận
            liked = True

        # Trả về JSON để xử lý giao diện
        return JsonResponse({'likes_count': comment.likes.count(), 'liked': liked})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Kiểm tra quyền của người dùng (chỉ tác giả hoặc admin mới có quyền xóa)
    if request.user == post.author or request.user.is_staff:
        post.delete()
        messages.success(request, "Bài đăng đã được xóa.")
        return redirect('forum_home')  # Quay lại trang forum home
    else:
        messages.error(request, "Bạn không có quyền xóa bài đăng này.")
        return redirect('post_detail', post_id=post.id)  # Quay lại trang chi tiết bài đăng nếu không có quyền



@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user == comment.author or request.user.profile.is_admin:
        comment.delete()
        messages.success(request, "Bình luận đã được xóa.")
    else:
        messages.error(request, "Bạn không có quyền xóa bình luận này.")
    return redirect('forum_home')

@login_required
def toggle_like_post(request, post_id):
    """
    Xử lý yêu cầu thích hoặc hủy thích bài viết.
    Trả về JSON chứa số lượt thích hiện tại và trạng thái 'liked'.
    """
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)

        # Kiểm tra trạng thái thích
        if request.user in post.likes.all():
            post.likes.remove(request.user)  # Hủy thích
            liked = False
        else:
            post.likes.add(request.user)  # Thêm thích
            liked = True

        return JsonResponse({'likes_count': post.likes.count(), 'liked': liked})

    return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required
def toggle_like_comment(request, comment_id):
    """
    Xử lý yêu cầu thích hoặc hủy thích bình luận.
    Trả về JSON chứa số lượt thích hiện tại và trạng thái 'liked'.
    """
    if request.method == "POST":
        comment = get_object_or_404(Comment, id=comment_id)

        # Kiểm tra trạng thái thích
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)  # Hủy thích
            liked = False
        else:
            comment.likes.add(request.user)  # Thêm thích
            liked = True

        return JsonResponse({'likes_count': comment.likes.count(), 'liked': liked})

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Kiểm tra quyền
    if request.user != post.author and not request.user.is_staff:
        messages.error(request, "Bạn không có quyền chỉnh sửa bài đăng này.")
        return redirect('post_detail', post_id=post.id)

    if request.method == 'POST':
        # Xóa media nếu có yêu cầu
        if 'delete_image' in request.POST:
            if post.image:
                post.image.delete(save=True)
                post.image = None
                post.save()
                messages.success(request, "Hình ảnh đã được xóa.")
                return redirect('edit_post', post_id=post.id)

        if 'delete_document' in request.POST:
            if post.document:
                post.document.delete(save=True)
                post.document = None
                post.save()
                messages.success(request, "Tài liệu đã được xóa.")
                return redirect('edit_post', post_id=post.id)

        if 'delete_video' in request.POST:
            if post.video:
                post.video.delete(save=True)
                post.video = None
                post.save()
                messages.success(request, "Video đã được xóa.")
                return redirect('edit_post', post_id=post.id)

        # Cập nhật bài đăng
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.image = request.FILES.get('image', post.image)
        post.document = request.FILES.get('document', post.document)
        post.video = request.FILES.get('video', post.video)
        post.save()

        messages.success(request, "Bài đăng đã được cập nhật.")
        return redirect('post_detail', post_id=post.id)

    return render(request, 'edit_post.html', {'post': post})





@login_required
def assign_admin(request, user_id):
    if hasattr(request.user, 'profile') and request.user.profile.is_admin:
        try:
            user = User.objects.get(id=user_id)
            profile, created = Profile.objects.get_or_create(user=user)
            profile.is_admin = True
            profile.save()
            return JsonResponse({'status': 'success', 'message': 'Cấp quyền quản trị thành công'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Người dùng không tồn tại'})
    return JsonResponse({'status': 'error', 'message': 'Bạn không có quyền thực hiện thao tác này'})

@login_required
def create_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            if not product_id:
                return JsonResponse({'error': 'Thiếu product_id.'}, status=400)

            product = Product.objects.get(id=product_id)

            order_code = random.randint(1000, 99999)
            product.order_code = order_code
            product.save()

            payment_data = PaymentData(
                orderCode=order_code,
                amount=product.raw_price,
                description="Thanh toán sản phẩm",
                cancelUrl="http://127.0.0.1:8000/cancel",
                returnUrl="http://127.0.0.1:8000/success"
            )

            payos_create_payment = payOS.createPaymentLink(payment_data)

            if hasattr(payos_create_payment, 'checkoutUrl'):
                return JsonResponse({'checkoutUrl': payos_create_payment.checkoutUrl})
            else:
                return JsonResponse({'error': 'Không tìm thấy liên kết thanh toán.'}, status=400)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Sản phẩm không tồn tại.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@login_required
def payment_success(request):
    order_code = request.GET.get('orderCode')
    if order_code:
        product = Product.objects.filter(order_code=order_code).first()
        if product:
            product.is_successful = True
            product.save()
    return HttpResponseRedirect('/')

@login_required
def payment_cancel(request):
    return redirect('home')


def product_list(request):
    query = request.GET.get('query', '')  # Lấy từ khóa tìm kiếm
    category = request.GET.get('category', '')  # Lấy phân loại được chọn
    filter_selected = request.GET.get('filter', '')  # Lấy bộ lọc được chọn
    page = request.GET.get('page', 1)  # Lấy số trang hiện tại từ URL

    # Danh sách gợi ý tìm kiếm
    search_suggestions = ["Toán", "Văn", "Anh", "Vật Lý", "Hóa Học", "Sinh Học", "Lịch Sử"]

    params = {
        'q': query or 'fiction',  # Mặc định tìm kiếm 'fiction' nếu không có từ khóa
        'maxResults': 40,  # Lấy tối đa 40 kết quả từ API
    }

    try:
        # Gọi API để lấy danh sách sản phẩm
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        items = data.get('items', [])
    except requests.RequestException as e:
        # Xử lý lỗi nếu không thể gọi API
        items = []
        error_message = f"Lỗi khi gọi API: {str(e)}"
        return render(request, 'product_list.html', {
            'products': [],
            'error_message': error_message,
            'search_suggestions': search_suggestions,  # Gợi ý tìm kiếm
            'selected_filter': filter_selected,
        })

    # Tạo danh sách sản phẩm
    products = [
        {
            'title': item['volumeInfo'].get('title', 'Không có tiêu đề'),
            'authors': item['volumeInfo'].get('authors', []),
            'thumbnail': item['volumeInfo'].get('imageLinks', {}).get('thumbnail', 'https://via.placeholder.com/150'),
            'category': item['volumeInfo'].get('categories', ['Chưa phân loại'])[0],
            'previewLink': item['volumeInfo'].get('previewLink', '#'),
        }
        for item in items
    ]

    # Lọc danh sách thể loại (categories)
    categories = set([product['category'] for product in products])

    # Nếu người dùng chọn bộ lọc, sắp xếp sách theo bộ lọc
    if filter_selected:
        products = [p for p in products if filter_selected.lower() in p['title'].lower()]

    # Phân trang (4 sản phẩm mỗi hàng, tối đa 5 hàng = 20 sản phẩm mỗi trang)
    paginator = Paginator(products, 20)
    paginated_products = paginator.get_page(page)

    return render(request, 'product_list.html', {
        'products': paginated_products,  # Danh sách sản phẩm của trang hiện tại
        'query': query,
        'categories': categories,  # Danh sách thể loại
        'search_suggestions': search_suggestions,  # Gợi ý tìm kiếm
        'selected_filter': filter_selected,  # Bộ lọc được chọn
    })
