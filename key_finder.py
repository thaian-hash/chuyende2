from x_plus import calculate_xplus
from utils import set_to_str
from collections import Counter, defaultdict

def find_k1(u_set, f_list):
    """Thuật toán tìm khóa K1 bằng cách loại bỏ thuộc tính dư thừa
    
    Args:
        u_set (set): Tập thuộc tính vũ trụ
        f_list (list): Danh sách các phụ thuộc hàm dạng (vt, vp)
        
    Returns:
        set: Khóa K1
    """
    k = set(u_set)  
    for attr in list(u_set):  
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
    
    right_side = set()
    for _, vp in f_list:
        right_side.update(vp)
    essential = u_set - right_side
    
    if essential and is_key(essential, u_set, f_list):
        return [essential]
    
    max_size = len(u_set)
    
    def find_keys_recursive(k, remaining):
        nonlocal max_size
        if len(k) > max_size:
            return
        
        if is_key(k, u_set, f_list):
            k_set = frozenset(k)
            if k_set not in [frozenset(r) for r in result]:
                result.append(set(k))
                max_size = min(max_size, len(k))
        else:
            for attr in remaining:
                new_remaining = remaining - {attr}
                find_keys_recursive(k | {attr}, new_remaining)
    
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

def calculate_dependency_score(key, f_list, u_set):
    """Tính điểm phụ thuộc của một khóa dựa trên số lần các thuộc tính trong khóa xuất hiện ở vế phải
    
    Args:
        key (set): Tập khóa cần tính điểm
        f_list (list): Danh sách các phụ thuộc hàm
        u_set (set): Tập thuộc tính vũ trụ
    
    Returns:
        float: Điểm phụ thuộc (thấp hơn là tốt hơn, nghĩa là ít phụ thuộc hơn)
    """
    right_side_count = Counter()
    for _, vp in f_list:
        for attr in vp:
            right_side_count[attr] += 1
    
    total_dependency = sum(right_side_count[attr] for attr in key)
    return total_dependency / len(key) if key else float('inf')

def find_ks2(u_set, f_list):
    """Thuật toán tìm tất cả các khóa ứng viên (KS2) với kiểm tra bổ sung tập con tối thiểu
    và ưu tiên các khóa có tính độc lập tối đa
    
    Args:
        u_set (set): Tập thuộc tính vũ trụ
        f_list (list): Danh sách các phụ thuộc hàm dạng (vt, vp)
        
    Returns:
        str: Chuỗi các khóa ứng viên, phân tách bằng dấu chấm phẩy
    """
    if not u_set or not f_list:
        return ""
    
    keys = find_all_keys(u_set, f_list)
    if not keys:
        return ""
    
    min_size = min(len(k) for k in keys)
    min_keys = [k for k in keys if len(k) == min_size]
    
    if not min_keys:
        return ""
    
    scored_keys = [(k, calculate_dependency_score(k, f_list, u_set)) for k in min_keys]
    scored_keys.sort(key=lambda x: x[1])
    best_score = scored_keys[0][1]
    best_keys = [k for k, score in scored_keys if score == best_score]
    
    return ';'.join(set_to_str(k) for k in best_keys)

def calculate_attribute_weights(f_list):
    """Tính trọng số của các thuộc tính dựa trên tần suất xuất hiện trong vế trái và vế phải
    
    Args:
        f_list (list): Danh sách các phụ thuộc hàm dạng (vt, vp)
    
    Returns:
        dict: Từ điển ánh xạ thuộc tính tới trọng số
    """
    left_count = Counter()
    right_count = Counter()
    
    for vt, vp in f_list:
        for attr in vt:
            left_count[attr] += 1
        for attr in vp:
            right_count[attr] += 1
    
    weights = {}
    for attr in set(left_count.keys()).union(right_count.keys()):
        weights[attr] = 2 * left_count.get(attr, 0) + right_count.get(attr, 0)
    
    return weights

def calculate_balance_score(key, weights):
    """Tính điểm cân bằng của một khóa dựa trên trọng số của các thuộc tính
    
    Args:
        key (set): Tập khóa cần tính điểm
        weights (dict): Trọng số của các thuộc tính
    
    Returns:
        float: Điểm cân bằng (thấp hơn là tốt hơn)
    """
    if not key:
        return float('inf')
    
    key_weights = [weights.get(attr, 0) for attr in key]
    if not key_weights:
        return float('inf')
    
    mean = sum(key_weights) / len(key_weights)
    variance = sum((w - mean) ** 2 for w in key_weights) / len(key_weights)
    return variance

def find_ks3(u_set, f_list):
    """Thuật toán tìm tất cả các khóa ứng viên (KS3) với ưu tiên các thuộc tính xuất hiện ở vế trái
    và thêm tiêu chí cân bằng dựa trên trọng số thuộc tính
    
    Args:
        u_set (set): Tập thuộc tính vũ trụ
        f_list (list): Danh sách các phụ thuộc hàm dạng (vt, vp)
        
    Returns:
        str: Chuỗi các khóa ứng viên, phân tách bằng dấu chấm phẩy
    """
    if not u_set or not f_list:
        return ""
    
    left_side = set()
    for vt, _ in f_list:
        left_side.update(vt)
    
    keys = find_all_keys(u_set, f_list)
    if not keys:
        return ""
    
    weights = calculate_attribute_weights(f_list)
    scored_keys = []
    for k in keys:
        left_count = len(k & left_side)
        balance_score = calculate_balance_score(k, weights)
        score = (left_count * 1000) - (balance_score * 10)
        scored_keys.append((k, score))
    
    scored_keys.sort(key=lambda x: x[1], reverse=True)
    best_score = scored_keys[0][1]
    best_keys = [k for k, score in scored_keys if score == best_score]
    
    return ';'.join(set_to_str(k) for k in best_keys)

def build_dependency_graph(f_list):
    """Xây dựng đồ thị phụ thuộc từ danh sách phụ thuộc hàm
    
    Args:
        f_list (list): Danh sách các phụ thuộc hàm dạng (vt, vp)
    
    Returns:
        dict: Đồ thị phụ thuộc (từng thuộc tính tới tập các thuộc tính phụ thuộc)
    """
    graph = defaultdict(set)
    for vt, vp in f_list:
        for attr in vt:
            graph[attr].update(vp)
    return graph

def find_shortest_path_coverage(key, graph, u_set):
    """Tính độ bao phủ và đường đi ngắn nhất trong đồ thị cho một khóa
    
    Args:
        key (set): Tập khóa
        graph (dict): Đồ thị phụ thuộc
        u_set (set): Tập thuộc tính vũ trụ
    
    Returns:
        float: Điểm bao phủ (thấp hơn là tốt hơn)
    """
    covered = set()
    queue = list(key)
    visited = set()
    
    while queue:
        attr = queue.pop(0)
        if attr not in visited:
            visited.add(attr)
            covered.update(graph.get(attr, set()))
            queue.extend(graph.get(attr, set()) - visited)
    
    uncovered = u_set - covered
    return len(uncovered) + len(key)  # Tối ưu hóa: ít thuộc tính chưa bao phủ + ít thuộc tính trong khóa

def find_ks4(u_set, f_list):
    """Thuật toán tìm khóa KS4 dựa trên tối ưu hóa độ bao phủ và tính độc lập
    
    Args:
        u_set (set): Tập thuộc tính vũ trụ
        f_list (list): Danh sách các phụ thuộc hàm dạng (vt, vp)
        
    Returns:
        str: Chuỗi các khóa ứng viên, phân tách bằng dấu chấm phẩy
    """
    if not u_set or not f_list:
        return ""
    
    keys = find_all_keys(u_set, f_list)
    if not keys:
        return ""
    
    graph = build_dependency_graph(f_list)
    scored_keys = [(k, find_shortest_path_coverage(k, graph, u_set)) for k in keys]
    scored_keys.sort(key=lambda x: x[1])
    best_score = scored_keys[0][1]
    best_keys = [k for k, score in scored_keys if score == best_score]
    
    return ';'.join(set_to_str(k) for k in best_keys)

def calculate_energy(key, f_list):
    """Tính năng lượng của một khóa dựa trên tần suất và ảnh hưởng động của thuộc tính
    
    Args:
        key (set): Tập khóa
        f_list (list): Danh sách các phụ thuộc hàm
    
    Returns:
        float: Năng lượng (thấp hơn là tốt hơn)
    """
    weights = calculate_attribute_weights(f_list)
    energy = sum(weights.get(attr, 0) ** 2 for attr in key)  # Năng lượng tỷ lệ với bình phương trọng số
    return energy / len(key) if key else float('inf')

def find_ks5(u_set, f_list):
    """Thuật toán tìm khóa KS5 dựa trên phân tích đồ thị phụ thuộc và đường đi ngắn nhất
    
    Args:
        u_set (set): Tập thuộc tính vũ trụ
        f_list (list): Danh sách các phụ thuộc hàm dạng (vt, vp)
        
    Returns:
        str: Chuỗi các khóa ứng viên, phân tách bằng dấu chấm phẩy
    """
    if not u_set or not f_list:
        return ""
    
    keys = find_all_keys(u_set, f_list)
    if not keys:
        return ""
    
    graph = build_dependency_graph(f_list)
    scored_keys = [(k, calculate_energy(k, f_list)) for k in keys]
    scored_keys.sort(key=lambda x: x[1])
    best_score = scored_keys[0][1]
    best_keys = [k for k, score in scored_keys if score == best_score]
    
    return ';'.join(set_to_str(k) for k in best_keys)

def find_ks6(u_set, f_list):
    """Thuật toán tìm khóa KS6 dựa trên phân phối năng lượng và tối ưu hóa động
    
    Args:
        u_set (set): Tập thuộc tính vũ trụ
        f_list (list): Danh sách các phụ thuộc hàm dạng (vt, vp)
        
    Returns:
        str: Chuỗi các khóa ứng viên, phân tách bằng dấu chấm phẩy
    """
    if not u_set or not f_list:
        return ""
    
    keys = find_all_keys(u_set, f_list)
    if not keys:
        return ""
    
    graph = build_dependency_graph(f_list)
    scored_keys = [(k, find_shortest_path_coverage(k, graph, u_set) + calculate_energy(k, f_list)) for k in keys]
    scored_keys.sort(key=lambda x: x[1])
    best_score = scored_keys[0][1]
    best_keys = [k for k, score in scored_keys if score == best_score]
    
    return ';'.join(set_to_str(k) for k in best_keys)
