def str_to_set(str_input):
    """Chuyển đổi chuỗi thành tập hợp ký tự
    Ví dụ: 'ABC' -> {'A', 'B', 'C'}
    """
    # Loại bỏ khoảng trắng và dấu phẩy nếu có
    cleaned = ''.join(str_input.strip().replace(',', '').split())
    
    # Chuyển đổi chuỗi thành tập hợp
    return set(cleaned) if cleaned else set()

def set_to_str(input_set):
    """Chuyển đổi tập hợp thành chuỗi
    Ví dụ: {'A', 'B', 'C'} -> 'ABC'
    """
    if not input_set:
        return "∅"  # Ký hiệu tập rỗng
    
    # Sắp xếp để đảm bảo kết quả nhất quán
    return ''.join(sorted(input_set))