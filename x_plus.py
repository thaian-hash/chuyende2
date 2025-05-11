def calculate_xplus(x_set, f_list, u_set):
    """Tính X+ (bao đóng của tập thuộc tính X)
    
    Args:
        x_set (set): Tập thuộc tính X cần tính bao đóng
        f_list (list): Danh sách các phụ thuộc hàm dạng (vt, vp)
        u_set (set): Tập thuộc tính vũ trụ
        
    Returns:
        set: Bao đóng X+ của tập X
    """
    # Đảm bảo x_set là tập con của u_set
    x_set = set(x_set) & u_set
    
    # Lặp cho đến khi X+ không thay đổi
    old_len = -1
    while len(x_set) != old_len:
        old_len = len(x_set)
        for vt, vp in f_list:
            # Nếu vế trái là tập con của X, thêm vế phải vào X
            if vt.issubset(x_set):
                x_set = x_set.union(vp)
    
    return x_set