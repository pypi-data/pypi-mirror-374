class Cache:
    def __init__(self, cache_size):
        self.cache_size = cache_size
        self.arr = []   
        self.counter = 0  

    def get_time(self):
        self.counter += 1
        return self.counter

    def helper(self, key):
        for i in range(len(self.arr)):
            if key in self.arr[i]: 
                self.arr[i][key]["freq"] += 1
                self.arr[i][key]["time"] = self.get_time()
                return self.arr[i][key]["value"]  
        return None
    
    def get_data(self,key):
        return self.helper(key)
    
    def put_data(self, key, value):
        existing_value = self.helper(key)

        if existing_value is not None:
            for i in range(len(self.arr)):
                if key in self.arr[i]:
                    self.arr[i][key]["value"] = value
            print(f"Key '{key}' already present, value updated.")
        else:
            if len(self.arr) >= self.cache_size:
                self.evict()  
            self.arr.append({key: {"value": value, "freq": 1, "time": self.get_time()}})
            print(f"Key '{key}' added to cache.")

    def display(self, arr):
        print(arr)

    def evict(self):
        victim_idx = min(
            range(len(self.arr)),
            key=lambda i: (list(self.arr[i].values())[0]["freq"], 
                        list(self.arr[i].values())[0]["time"])
        )
        evicted_key = list(self.arr[victim_idx].keys())[0]
        self.arr.pop(victim_idx)
        print(f"Evicted key '{evicted_key}' due to cache full.")

