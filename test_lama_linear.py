from medtriage.stack import LinkedStack
from medtriage.queue import LinkedQueue, PriorityQueue

# 1. اختبار الحالات الفارغة (Empty cases)
empty_stack = LinkedStack()
empty_queue = LinkedQueue()
empty_pq = PriorityQueue()

assert empty_stack.is_empty() and empty_stack.pop() is None and empty_stack.undo() is None
assert empty_queue.is_empty() and empty_queue.dequeue() is None
assert empty_pq.is_empty() and empty_pq.dequeue() is None
print("Empty cases passed!")

# 2. اختبار Undo مع فرز الأعراض وطابور المختبر/الصيدلية
undo_stack = LinkedStack()
lab_queue = LinkedQueue()
pharmacy_queue = LinkedQueue()

# فرز مريض وإضافته لطابور المختبر ثم الصيدلية مع تسجيل التراجع
undo_stack.push(("triage_symptom", "Patient-101", "Fever+Cough"))
lab_queue.enqueue("Patient-101: CBC Test")
undo_stack.push(("lab_enqueue", "Patient-101: CBC Test"))
pharmacy_queue.enqueue("Patient-101: Rx-Antibiotic")
undo_stack.push(("pharmacy_enqueue", "Patient-101: Rx-Antibiotic"))

print("Undo stack top:", undo_stack.peek())
last_action = undo_stack.undo()
print("Undoing last action:", last_action)
if last_action and last_action[0] == "pharmacy_enqueue":
    # إزالة آخر عنصر أضيف لطابور الصيدلية عند التراجع
    if pharmacy_queue.to_list() and pharmacy_queue.to_list()[-1] == last_action[1]:
        # تفريغ وإعادة بناء الطابور بدون العنصر المتراجع عنه
        kept = pharmacy_queue.to_list()[:-1]
        pharmacy_queue = LinkedQueue()
        for item in kept:
            pharmacy_queue.enqueue(item)

print("Lab queue:", lab_queue.to_list())
print("Pharmacy queue after undo:", pharmacy_queue.to_list())

# 3. اختبار PriorityQueue ومنطق wait_cycles لمنع التجويع
pq = PriorityQueue(aging_threshold=2)
pq.enqueue("Low-Urgency-A", priority=5)
pq.enqueue("Low-Urgency-B", priority=5)
pq.enqueue("Critical-X", priority=1)

print("Initial PQ order:", pq.items_with_cycles())
print("First dequeue (highest urgency):", pq.dequeue())

# مرور دورات انتظار لتعزيز أولوية من ينتظر طويلاً
pq.tick_wait_cycles()
pq.tick_wait_cycles()
pq.enqueue("Moderate-Y", priority=3)
print("PQ after wait_cycles aging:", pq.items_with_cycles())
print("Next dequeue after aging:", pq.dequeue())