const API_URL = "https://www.googleapis.com/books/v1/volumes?q=education+OR+learning+OR+study+materials";

// Hàm tạo giá ngẫu nhiên
function generateRandomPrice() {
  const min = 10000; // Giá tối thiểu (10,000 VND)
  const max = 200000; // Giá tối đa (200,000 VND)
  const randomPrice = Math.floor(Math.random() * (max - min + 1)) + min; // Sinh giá ngẫu nhiên trong phạm vi
  return `${randomPrice.toLocaleString()} VND`; // Định dạng giá (ví dụ: "50,000 VND")
}

// Hàm lấy danh sách tài liệu và hiển thị dạng hàng ngang
async function fetchAndRenderCards() {
  const container = document.getElementById("documentCards");

  try {
    const response = await fetch(API_URL);
    if (!response.ok) {
      throw new Error("Không thể tải tài liệu.");
    }
    const data = await response.json();

    const items = data.items;
    const totalItems = items.length;
    const rows = Math.ceil(totalItems / 4); // Số hàng cần thiết (4 tài liệu mỗi hàng)
    const totalBoxes = rows * 4; // Tổng số box cần hiển thị

    // Xử lý thêm tài liệu placeholder nếu thiếu
    const documents = [...items]; // Sao chép dữ liệu gốc
    while (documents.length < totalBoxes) {
      documents.push({
        volumeInfo: {
          title: "Placeholder Document",
          previewLink: "#",
          imageLinks: { thumbnail: "https://via.placeholder.com/150" } // Hình ảnh mặc định
        },
      });
    }

    // Hiển thị danh sách tài liệu
    container.innerHTML = documents.slice(0, totalBoxes).map((item) => `
      <div class="card" data-post-id="${item.id}">
        <img 
          src="${item.volumeInfo.imageLinks?.thumbnail || 'https://via.placeholder.com/150'}" 
          alt="Book Cover" 
          class="book-cover"
        >
        <div class="card-header">
          <span class="card-title">${item.volumeInfo.title}</span>
          <span class="card-status">${item.volumeInfo.previewLink === "#" ? "Chưa có" : "Đang hoạt động"}</span>
        </div>
        <div class="card-link">
          <a href="${item.volumeInfo.previewLink}" target="_blank">${item.volumeInfo.previewLink === "#" ? "Đang cập nhật" : "Xem tài liệu"}</a>
        </div>
        <div class="card-footer">
          <div class="price">Giá: ${generateRandomPrice()}</div>
          <button class="payment-button">Thanh toán</button>
        </div>
      </div>
    `).join('');
  } catch (error) {
    container.innerHTML = `<p style="color: red; text-align: center;">Lỗi: ${error.message}</p>`;
  }
}

// Hàm xử lý sự kiện "Thích"
function handleLikePost(postId) {
  const likeButton = document.querySelector(`[data-post-id="${postId}"]`);
  const likesCountElement = document.getElementById(`post-likes-count-${postId}`);
  
  // Gửi yêu cầu AJAX đến máy chủ
  fetch(`/forum/post/${postId}/like/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    }
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Không thể thực hiện hành động "Thích"');
      }
      return response.json();
    })
    .then(data => {
      // Cập nhật giao diện
      if (data.liked) {
        likeButton.classList.add('liked'); // Thêm class 'liked' nếu người dùng đã thích
      } else {
        likeButton.classList.remove('liked'); // Loại bỏ class 'liked' nếu người dùng bỏ thích
      }
      likesCountElement.textContent = `${data.likes_count} lượt thích`; // Cập nhật số lượt thích
    })
    .catch(error => console.error('Lỗi:', error));
}

// Sự kiện cho nút "Thích"
document.addEventListener('DOMContentLoaded', () => {
  const likeButtons = document.querySelectorAll('.like-post-btn');

  likeButtons.forEach(button => {
    button.addEventListener('click', (event) => {
      const postId = button.getAttribute('data-post-id'); // Lấy ID bài viết từ thuộc tính data-post-id
      handleLikePost(postId); // Gọi hàm xử lý sự kiện "Thích"
    });
  });
});

// Thêm sự kiện click vào liên kết "Sản phẩm" trong menu
document.getElementById("productLink").addEventListener('click', (e) => {
  e.preventDefault(); // Ngừng hành động mặc định của liên kết (không chuyển trang)

  // Thêm class 'active' vào liên kết "Sản phẩm"
  const navLinks = document.querySelectorAll('.navbar .menu a');
  navLinks.forEach(link => {
    link.classList.remove('active'); // Xóa class active khỏi tất cả các liên kết
  });
  e.target.classList.add('active'); // Thêm class active vào liên kết hiện tại

  // Hiển thị danh sách tài liệu
  const documentSection = document.querySelector('.product-list');
  documentSection.style.display = 'block'; // Hiển thị danh sách tài liệu

  // Cuộn đến phần danh sách tài liệu
  documentSection.scrollIntoView({
    behavior: 'smooth', // Cuộn mượt mà
    block: 'start', // Cuộn đến vị trí đầu của phần
  });

  // Gọi hàm để tải danh sách tài liệu
  fetchAndRenderCards();
});

// Chọn tất cả các liên kết trong menu và thêm sự kiện click cho mỗi liên kết
const navLinks = document.querySelectorAll('.navbar .menu a');

navLinks.forEach((link) => {
  link.addEventListener('click', () => {
    // Loại bỏ class 'active' từ tất cả các liên kết
    navLinks.forEach((item) => item.classList.remove('active'));

    // Thêm class 'active' vào liên kết vừa nhấn
    link.classList.add('active');
  });
});


document.addEventListener('DOMContentLoaded', function () {
  const commentForms = document.querySelectorAll('.comment-form');

  // Xử lý gửi bình luận
  commentForms.forEach(form => {
      form.addEventListener('submit', function (e) {
          e.preventDefault();

          const postId = this.getAttribute('data-post-id');
          const content = this.querySelector('textarea[name="content"]').value;
          const csrfToken = this.querySelector('[name="csrfmiddlewaretoken"]').value;

          fetch(`/forum/post/${postId}/comment/`, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
                  'X-CSRFToken': csrfToken
              },
              body: JSON.stringify({ content: content })
          })
          .then(response => response.json())
          .then(data => {
              if (data.success) {
                  const commentList = document.getElementById(`comments-list-${postId}`);
                  const newComment = document.createElement('li');
                  newComment.classList.add('comment-item');
                  newComment.innerHTML = `
                      <p><strong>${data.author}</strong>: ${data.content}</p>
                      <small>${data.created_at}</small>
                      ${data.can_delete ? `<a href="#" class="btn btn-sm btn-danger delete-comment-btn" data-comment-id="${data.comment_id}">Xóa</a>` : ''}
                  `;
                  commentList.appendChild(newComment);

                  // Reset ô nhập liệu
                  this.querySelector('textarea[name="content"]').value = '';

                  // Gắn sự kiện xóa cho nút mới
                  attachDeleteEvent();
              } else {
                  alert(data.error || 'Có lỗi xảy ra, vui lòng thử lại.');
              }
          })
          .catch(error => {
              console.error('Lỗi khi gửi bình luận:', error);
              alert('Có lỗi xảy ra, vui lòng thử lại.');
          });
      });
  });

  // Xử lý xóa bình luận
  function attachDeleteEvent() {
      const deleteButtons = document.querySelectorAll('.delete-comment-btn');

      deleteButtons.forEach(button => {
          button.addEventListener('click', function (e) {
              e.preventDefault();

              const commentId = this.getAttribute('data-comment-id');
              const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;

              fetch(`/forum/comment/${commentId}/delete/`, {
                  method: 'POST',
                  headers: {
                      'X-CSRFToken': csrfToken
                  }
              })
              .then(response => response.json())
              .then(data => {
                  if (data.success) {
                      this.closest('li').remove();
                  } else {
                      alert(data.error || 'Không thể xóa bình luận.');
                  }
              })
              .catch(error => {
                  console.error('Lỗi khi xóa bình luận:', error);
                  alert('Có lỗi xảy ra, vui lòng thử lại.');
              });
          });
      });
  }

  // Gắn sự kiện ban đầu
  attachDeleteEvent();
});
