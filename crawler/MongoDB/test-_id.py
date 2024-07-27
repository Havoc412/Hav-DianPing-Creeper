from bson import ObjectId

# 定义两个 ObjectId
id1 = ObjectId("66a39ca31beaf264550f5722")
id2 = ObjectId("66a38e75b28c6b94d634ffcd")

# 获取时间戳
timestamp1 = id1.generation_time
timestamp2 = id2.generation_time

# 比较时间戳
if timestamp1 > timestamp2:
    print(f"ObjectId {id1} 的时间戳更晚，插入时间为 {timestamp1}")
    last_inserted_id = id1
else:
    print(f"ObjectId {id2} 的时间戳更晚，插入时间为 {timestamp2}")
    last_inserted_id = id2

print(f"最后插入的 ObjectId 是: {last_inserted_id}")