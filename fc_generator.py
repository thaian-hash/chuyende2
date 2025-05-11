from x_plus import calculate_xplus

def find_f1(f_list):
    """Tạo tập phụ thuộc hàm F1 từ F (mỗi vế phải chỉ có 1 thuộc tính)
    
    Args:
        f_list (list): Danh sách các phụ thuộc hàm dạng (vt, vp)
        
    Returns:
        list: Danh sách F1, mỗi phụ thuộc hàm có vế phải chỉ có 1 thuộc tính
    """
    f1 = []
    
    for vt, vp in f_list:
        # Tách mỗi thuộc tính ở vế phải thành một phụ thuộc hàm riêng
        for attr in vp:
            f1.append((vt, {attr}))
            
    return f1

def find_f2(f_list, u_set):
    """Tạo tập phụ thuộc hàm F2 từ F1 (loại bỏ thuộc tính dư thừa ở vế trái)
    
    Args:
        f_list (list): Danh sách các phụ thuộc hàm dạng (vt, vp)
        u_set (set): Tập thuộc tính vũ trụ
        
    Returns:
        list: Danh sách F2, mỗi phụ thuộc hàm có vế trái tối thiểu
    """
    f1 = find_f1(f_list)
    f2 = []
    
    for vt, vp in f1:
        min_vt = set(vt)  # Bắt đầu với toàn bộ vế trái
        
        # Thử loại bỏ từng thuộc tính ở vế trái
        for attr in list(vt):
            test_vt = min_vt - {attr}
            
            # Kiểm tra xem vế trái mới có bao hàm vế phải không
            test_closure = calculate_xplus(test_vt, f1, u_set)
            
            if vp.issubset(test_closure):
                min_vt = test_vt
        
        f2.append((min_vt, vp))
            
    return f2

def find_f3(f_list, u_set):
    """Tạo tập phụ thuộc hàm F3 từ F2 (loại bỏ phụ thuộc hàm dư thừa)
    
    Args:
        f_list (list): Danh sách các phụ thuộc hàm dạng (vt, vp)
        u_set (set): Tập thuộc tính vũ trụ
        
    Returns:
        list: Danh sách F3, không có phụ thuộc hàm dư thừa
    """
    f2 = find_f2(f_list, u_set)
    f3 = []
    
    # Kiểm tra từng phụ thuộc hàm
    for i, (vt, vp) in enumerate(f2):
        # Tạo một tập F tạm thời không có phụ thuộc hàm đang xét
        temp_f = f2.copy()
        temp_f.pop(i)
        
        # Tính bao đóng của vế trái với tập F tạm thời
        temp_closure = calculate_xplus(vt, temp_f, u_set)
        
        # Nếu bao đóng không chứa vế phải, thì phụ thuộc hàm này không dư thừa
        if not vp.issubset(temp_closure):
            f3.append((vt, vp))
            
    return f3