from x_plus import calculate_xplus
from utils import set_to_str

def find_k1(u_set, f_list):
    """Thuật toán tìm khóa K1 bằng cách loại bỏ thuộc tính dư thừa
    
    Args:
        u_set (set): Tập thuộc tính vũ trụ
        f_list (list): Danh sách các phụ thuộc hàm dạng (vt, vp)
        
    Returns:
        set: Khóa K1
    """
    k = set(u_set)  # Bắt đầu với tất cả thuộc tính
    
    for attr in list(u_set):  # Duyệt từng thuộc tính
        test_set = k - {attr}
        if calculate_xplus(test_set, f_list, u_set) == u_set:
            k = test_set
    
    return k

def find_k2(u_set, f_list):
    """Thuật toán tìm khóa K2 dựa trên tập không xuất hiện ở vế phải và tập vừa xuất hiện ở vế trái vừa xuất hiện ở vế phải
    
    Args:
        u_set (set): Tập thuộc tính vũ trụ
        f_list (list): Danh sách các phụ thuộc hàm dạng (vt, vp)
        
    Returns:
        set: Khóa K2
    """
    left_side = set()
    right_side = set()
    
    for vt, vp in f_list:
        left_side = left_side.union(vt)
        right_side = right_side.union(vp)
    
    k = (u_set - right_side).union(left_side.intersection(right_side))
    
    for attr in list(left_side.intersection(right_side)):
        test_set = k - {attr}
        if calculate_xplus(test_set, f_list, u_set) == u_set:
            k = test_set
    
    return k

def find_k3(u_set, f_list):
    """Thuật toán tìm khóa K3 dựa trên tập thuộc tính cần thiết
    
    Args:
        u_set (set): Tập thuộc tính vũ trụ
        f_list (list): Danh sách các phụ thuộc hàm dạng (vt, vp)
        
    Returns:
        set: Khóa K3
    """
    left_side = set()
    right_side = set()
    
    for vt, vp in f_list:
        left_side = left_side.union(vt)
        right_side = right_side.union(vp)
    
    k = (u_set - right_side).union(left_side.intersection(right_side))
    
    for attr in list(left_side.intersection(right_side).intersection(u_set)):
        test_set = k - {attr}
        if calculate_xplus(test_set, f_list, u_set) == u_set:
            k = test_set
    
    return k

def is_key(k_set, u_set, f_list):
    """Kiểm tra xem một tập thuộc tính có phải là khóa hay không
    
    Args:
        k_set (set): Tập thuộc tính cần kiểm tra
        u_set (set): Tập thuộc tính vũ trụ
        f_list (list): Danh sách các phụ thuộc hàm dạng (vt, vp)
        
    Returns:
        bool: True nếu k_set là khóa, False nếu không phải
    """
    if calculate_xplus(k_set, f_list, u_set) != u_set:
        return False
        
    for attr in k_set:
        if calculate_xplus(k_set - {attr}, f_list, u_set) == u_set:
            return False
            
    return True

def find_all_keys(u_set, f_list):
    """Thuật toán tìm tất cả các khóa bằng đệ quy backtracking với tối ưu hóa
    
    Args:
        u_set (set): Tập thuộc tính vũ trụ
        f_list (list): Danh sách các phụ thuộc hàm dạng (vt, vp)
        
    Returns:
        list: Danh sách tất cả các khóa
    """
    if not u_set or not f_list:
        return []
    
    result = []
    
    # Tìm tập thuộc tính cần thiết (essential attributes)
    right_side = set()
    for _, vp in f_list:
        right_side.update(vp)
    essential = u_set - right_side
    
    # Nếu tập cần thiết đã là khóa, chỉ trả về nó
    if essential and is_key(essential, u_set, f_list):
        return [essential]
    
    # Khởi tạo max_size
    max_size = len(u_set)
    
    def find_keys_recursive(k, remaining):
        nonlocal max_size
        if len(k) > max_size:
            return
        
        if is_key(k, u_set, f_list):
            k_set = frozenset(k)
            if k_set not in [frozenset(r) for r in result]:
                result.append(set(k))
                max_size = min(max_size, len(k))  # Cập nhật max_size
        else:
            for attr in remaining:
                new_remaining = remaining - {attr}
                find_keys_recursive(k | {attr}, new_remaining)
    
    # Bắt đầu với tập cần thiết
    remaining = u_set - essential
    find_keys_recursive(essential, remaining)
    
    return result

def find_ks1(u_set, f_list):
    """Thuật toán tìm tất cả các khóa ứng viên (KS1) và trả về dưới dạng chuỗi phân tách bằng dấu chấm phẩy
    
    Args:
        u_set (set): Tập thuộc tính vũ trụ
        f_list (list): Danh sách các phụ thuộc hàm dạng (vt, vp)
        
    Returns:
        str: Chuỗi các khóa ứng viên, phân tách bằng dấu chấm phẩy
    """
    if not u_set or not f_list:
        return ""
    
    keys = find_all_keys(u_set, f_list)
    return ';'.join(set_to_str(k) for k in keys)