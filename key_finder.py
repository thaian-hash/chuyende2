    from x_plus import calculate_xplus
    from utils import set_to_str
    from collections import Counter, defaultdict, deque
    import math

    # Bộ nhớ đệm để lưu trữ kết quả tính toán
    _cache = {}

    def build_dependency_graph(f_list):
        """Xây dựng đồ thị phụ thuộc có trọng số từ danh sách phụ thuộc hàm
        
        Args:
            f_list (list): Danh sách các phụ thuộc hàm dạng (vt, vp)
        
        Returns:
            tuple: (Đồ thị phụ thuộc, trọng số cạnh)
        """
        graph = defaultdict(set)
        edge_weights = defaultdict(int)
        
        for vt, vp in f_list:
            for attr in vt:
                for target in vp:
                    graph[attr].add(target)
                    edge_weights[(attr, target)] += 1  # Tăng trọng số cạnh
        
        return graph, edge_weights

    def calculate_attribute_weights(f_list):
        """Tính trọng số của các thuộc tính dựa trên tần suất xuất hiện
        
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
            # Trọng số: 2 * tần suất vế trái + tần suất vế phải
            weights[attr] = 2 * left_count.get(attr, 0) + right_count.get(attr, 0)
        
        return weights

    def dijkstra_coverage(key, graph, edge_weights, u_set):
        """Tính độ bao phủ của khóa bằng thuật toán Dijkstra
        
        Args:
            key (set): Tập khóa
            graph (dict): Đồ thị phụ thuộc
            edge_weights (dict): Trọng số cạnh
            u_set (set): Tập thuộc tính vũ trụ
        
        Returns:
            float: Điểm bao phủ (thấp hơn là tốt hơn)
        """
        cache_key = (frozenset(key), frozenset(u_set))
        if cache_key in _cache:
            return _cache[cache_key]
        
        covered = set(key)
        distances = {attr: float('inf') for attr in u_set}
        for attr in key:
            distances[attr] = 0
        
        queue = deque(key)
        while queue:
            current = queue.popleft()
            for neighbor in graph.get(current, set()):
                weight = edge_weights.get((current, neighbor), 1)
                if distances[current] + weight < distances[neighbor]:
                    distances[neighbor] = distances[current] + weight
                    covered.add(neighbor)
                    queue.append(neighbor)
        
        uncovered = len(u_set - covered)
        # Điểm bao phủ: số thuộc tính chưa bao phủ + kích thước khóa (chuẩn hóa)
        score = uncovered + len(key) / len(u_set)
        
        _cache[cache_key] = score
        return score

    def calculate_energy(key, f_list, graph):
        """Tính năng lượng của khóa dựa trên trọng số động và kết nối đồ thị
        
        Args:
            key (set): Tập khóa
            f_list (list): Danh sách các phụ thuộc hàm
            graph (dict): Đồ thị phụ thuộc
        
        Returns:
            float: Năng lượng (thấp hơn là tốt hơn)
        """
        if not key:
            return float('inf')
        
        weights = calculate_attribute_weights(f_list)
        # Tính năng lượng dựa trên logarit trọng số
        energy = sum(math.log1p(weights.get(attr, 0)) for attr in key)
        
        # Thêm điểm kết nối: số cạnh đi ra từ các thuộc tính trong khóa
        connectivity = sum(len(graph.get(attr, set())) for attr in key)
        # Chuẩn hóa năng lượng
        normalized_energy = energy / len(key) if key else float('inf')
        # Kết hợp năng lượng và kết nối (trừ để ưu tiên kết nối cao)
        return normalized_energy - (connectivity / len(f_list) if f_list else 0)

    def normalize_score(scores):
        """Chuẩn hóa điểm số bằng min-max normalization
        
        Args:
            scores (list): Danh sách các điểm số
        
        Returns:
            list: Danh sách điểm số đã chuẩn hóa
        """
        if not scores:
            return []
        
        min_score = min(scores)
        max_score = max(scores)
        if max_score == min_score:
            return [0.5] * len(scores)  # Tránh chia cho 0
        
        return [(score - min_score) / (max_score - min_score) for score in scores]

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
            balance_score = sum((weights.get(attr, 0) - sum(weights.values()) / len(weights)) ** 2 for attr in k) / len(k) if k else float('inf')
            score = (left_count * 1000) - (balance_score * 10)
            scored_keys.append((k, score))
        
        scored_keys.sort(key=lambda x: x[1], reverse=True)
        best_score = scored_keys[0][1]
        best_keys = [k for k, score in scored_keys if score == best_score]
        
        return ';'.join(set_to_str(k) for k in best_keys)

    def find_ks4(u_set, f_list):
        """Thuật toán KS4 cải tiến: Tối ưu hóa độ bao phủ với Dijkstra
        
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
        
        graph, edge_weights = build_dependency_graph(f_list)
        scored_keys = [(k, dijkstra_coverage(k, graph, edge_weights, u_set)) for k in keys]
        
        # Chuẩn hóa điểm số
        scores = [score for _, score in scored_keys]
        normalized_scores = normalize_score(scores)
        
        # Kết hợp điểm số chuẩn hóa với kích thước khóa
        final_scores = [
            (k, normalized_scores[i] + len(k) / len(u_set)) 
            for i, (k, _) in enumerate(scored_keys)
        ]
        
        final_scores.sort(key=lambda x: x[1])
        best_score = final_scores[0][1]
        best_keys = [k for k, score in final_scores if score <= best_score * 1.01]  # Chấp nhận sai số 1%
        
        return ';'.join(set_to_str(k) for k in best_keys)

    def find_ks5(u_set, f_list):
        """Thuật toán KS5 cải tiến: Tối ưu hóa năng lượng và kết nối
        
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
        
        graph, _ = build_dependency_graph(f_list)
        scored_keys = [(k, calculate_energy(k, f_list, graph)) for k in keys]
        
        # Chuẩn hóa điểm số
        scores = [score for _, score in scored_keys]
        normalized_scores = normalize_score(scores)
        
        # Kết hợp điểm số chuẩn hóa với kích thước khóa
        final_scores = [
            (k, normalized_scores[i] + len(k) / len(u_set)) 
            for i, (k, _) in enumerate(scored_keys)
        ]
        
        final_scores.sort(key=lambda x: x[1])
        best_score = final_scores[0][1]
        best_keys = [k for k, score in final_scores if score <= best_score * 1.01]
        
        return ';'.join(set_to_str(k) for k in best_keys)

    def find_ks6(u_set, f_list, coverage_weight=0.6, energy_weight=0.4):
        """Thuật toán KS6 cải tiến: Kết hợp bao phủ và năng lượng với trọng số
        
        Args:
            u_set (set): Tập thuộc tính vũ trụ
            f_list (list): Danh sách các phụ thuộc hàm dạng (vt, vp)
            coverage_weight (float): Trọng số cho độ bao phủ
            energy_weight (float): Trọng số cho năng lượng
            
        Returns:
            str: Chuỗi các khóa ứng viên, phân tách bằng dấu chấm phẩy
        """
        if not u_set or not f_list:
            return ""
        
        keys = find_all_keys(u_set, f_list)
        if not keys:
            return ""
        
        graph, edge_weights = build_dependency_graph(f_list)
        
        # Tính điểm số cho từng khóa
        coverage_scores = [dijkstra_coverage(k, graph, edge_weights, u_set) for k in keys]
        energy_scores = [calculate_energy(k, f_list, graph) for k in keys]
        
        # Chuẩn hóa điểm số
        norm_coverage = normalize_score(coverage_scores)
        norm_energy = normalize_score(energy_scores)
        
        # Kết hợp điểm số với trọng số
        final_scores = [
            (k, coverage_weight * norm_coverage[i] + energy_weight * norm_energy[i] + len(k) / len(u_set))
            for i, k in enumerate(keys)
        ]
        
        final_scores.sort(key=lambda x: x[1])
        best_score = final_scores[0][1]
        best_keys = [k for k, score in final_scores if score <= best_score * 1.01]
        
        # Loại bỏ trùng lặp
        unique_keys = []
        seen = set()
        for k in best_keys:
            k_str = set_to_str(k)
            if k_str not in seen:
                unique_keys.append(k)
                seen.add(k_str)
        
        return ';'.join(set_to_str(k) for k in unique_keys)
