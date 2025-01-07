const API_URL = "https://www.googleapis.com/books/v1/volumes?q=education+OR+learning+OR+study+materials";

// Hàm lấy danh sách tài liệu và hiển thị dạng hàng ngang
async function fetchAndRenderCards(apiURL) {
  const container = document.getElementById("documentCards");

  try {
    const response = await fetch(apiURL);
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
          imageLinks: { thumbnail: "https://via.placeholder.com/150" }, // Hình ảnh mặc định
          retailPrice: { amount: "50,000 VND" } // Giá tiền mặc định
        },
      });
    }

    // Hiển thị danh sách tài liệu
    container.innerHTML = documents.slice(0, totalBoxes).map((item) => `
      <div class="card">
        <img 
          src="${item.volumeInfo.imageLinks?.thumbnail || 'https://via.placeholder.com/150'}" 
          alt="Book Cover" 
          class="book-cover"
        >
        <div class="card-header">
          <span class="card-title">${item.volumeInfo.title}</span>
        </div>
        <div class="card-link">
          <a href="${item.volumeInfo.previewLink}" target="_blank">${item.volumeInfo.previewLink === "#" ? "Đang cập nhật" : "Xem tài liệu"}</a>
        </div>
        <div class="card-footer">
          <div class="price">
            <span>Giá: ${item.volumeInfo.retailPrice?.amount || "Chưa có giá"}</span>
          </div>
          <button class ="Payment">Thanh toán</button>
        </div>
      </div>
    `).join('');
  } catch (error) {
    container.innerHTML = `<p style="color: red; text-align: center;">Lỗi: ${error.message}</p>`;
  }
}

// Hiển thị danh sách tài liệu (cập nhật để xóa 2 sách cuối)
async function fetchAndRenderCards(apiURL) {
  const container = document.getElementById("documentCards");

  try {
    const response = await fetch(apiURL);
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
          imageLinks: { thumbnail: "https://via.placeholder.com/150" }, // Hình ảnh mặc định
          retailPrice: { amount: "50,000 VND" } // Giá tiền mặc định
        },
      });
    }

    // Xóa 2 quyển sách cuối
    documents.splice(-2, 2); // Loại bỏ 2 phần tử cuối trong mảng

    // Hiển thị danh sách tài liệu
    container.innerHTML = documents.slice(0, totalBoxes).map((item) => `
      <div class="card">
        <img 
          src="${item.volumeInfo.imageLinks?.thumbnail || 'https://via.placeholder.com/150'}" 
          alt="Book Cover" 
          class="book-cover"
        >
        <div class="card-header">
          <span class="card-title">${item.volumeInfo.title}</span>
        </div>
        <div class="card-link">
          <a href="${item.volumeInfo.previewLink}" target="_blank">${item.volumeInfo.previewLink === "#" ? "Đang cập nhật" : "Xem tài liệu"}</a>
        </div>
        <div class="card-footer">
          <div class="price">
            <span>Giá: ${item.volumeInfo.retailPrice?.amount || "Chưa có giá"}</span>
          </div>
          <button class ="Payment">Thanh toán</button>
        </div>
      </div>
    `).join('');
  } catch (error) {
    container.innerHTML = `<p style="color: red; text-align: center;">Lỗi: ${error.message}</p>`;
  }
}


// Hàm hiển thị nội dung tài liệu khi click vào sản phẩm
function displayDocumentContent(item) {
  const documentContent = document.getElementById("documentContent");

  documentContent.innerHTML = `
    <h3>${item.volumeInfo.title}</h3>
    <p>${item.volumeInfo.description || "Không có mô tả cho tài liệu này."}</p>
    <a href="${item.volumeInfo.previewLink}" target="_blank">Xem tài liệu</a>
  `;
}



// Ẩn danh sách tài liệu khi tải trang
document.getElementById("documentContent").style.display = 'none';

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
  fetchAndRenderCards(API_URL);
});

// Thêm sự kiện tìm kiếm
document.getElementById("searchButton").addEventListener("click", async () => {
  const query = document.getElementById("searchInput").value;
  if (query) {
    const searchAPI_URL = `https://www.googleapis.com/books/v1/volumes?q=${query}`;
    await fetchAndRenderCards(searchAPI_URL); // Gọi lại hàm fetchAndRenderCards với query tìm kiếm
  }
});
