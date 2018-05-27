
import threading
import struct
import logging
import time

# For ip_type selection

class LRUCache(object):

    class Node(object):

        def __init__(self, key, val, ttl):
            self.prev = None
            self.next = None

            if not type(key) == tuple:
                raise TypeError
            if not type(val) == bytes:
                raise TypeError
            
            self.key = key
            self.val = val
            # Expire time is the acc time
            # Support int time
            self.expire_time = int(ttl + time.time())
        
    def __init__(self, m_capacity = 10000):
        self._head = None
        self._tail = None

        # pointer_map is map for cache data pointer
        self._pointer_map = {}
        # Max length of cahce
        if m_capacity < 0:
            m_capacity = 100000
        self._capacity = m_capacity

        # threading lock
        self._lock = threading.Lock()

    def insertHead(self, a_node):
        if self._head == None:
            self._head = a_node
        self._head.prev = a_node
        a_node.next = self._head
        a_node.prev = None
        self._head = a_node
    
    def eraseTail(self):
        prev = self._tail.prev
        if prev:
            prev.next = None
            # unlink the tail
            self._tail = prev
        # it means the tail is the head
        else:
            self._head = None
        
        

    def detachNode(self, a_node):
        """
        Detach node from neighbour nodes
        Evey insert head must firstly detach
        """
        if a_node == self._head:
            self._head = a_node.next
        if a_node.prev:
            a_node.prev.next = a_node.next
        if a_node.next:
            a_node.next.prev = a_node.prev
        else:
            # Tail now
            self._tail = a_node

    def get(self, qname, type_int, class_int):
        print(qname)
        if not type(qname) == str:
            qname = str(qname, "ascii")
        print(qname)
        if len(qname) == 0 or not qname[-1] == ".":
            qname += "."
        # key: tuple(string, int, int)
        a_key = (qname, type_int, class_int)

        try:
            # threading
            self._lock.acquire()
            # Get pointer: Node
            a_pointer = self._pointer_map.get(a_key)
            if not a_pointer:
                # None
                return None
            else:
                # Expire:
                if a_pointer.expire_time <= int(time.time()):
                    del self._pointer_map[a_key]
                    # Ignore the node, it will be automatically del
                    return None

                else:
                    # put into head
                    self.detachNode(a_pointer)
                    self.insertHead(a_pointer)
                    return a_pointer.val
        finally:
            self._lock.release()

        
    def set(self, qname, type_id, class_id, val, ttl):
        if not type(qname) == str:
            qname = str(qname, "ascii")
        if qname is None or not qname[-1] == ".":
            qname += "."
        
        a_key = (qname, type_id, class_id)

        try:
            self._lock.acquire()
            # No head:
            if self._head is None:
                a_node = self.Node(a_key, val, ttl)
                self._head = a_node
                self._tail = a_node
                self._pointer_map[a_key] = a_node
                return True
            # Cache is full
            elif len(self._pointer_map) >= self._capacity:
                del self._pointer_map[self._tail.key]
                self.eraseTail()
                a_node = self.Node(a_key, val, ttl)
                self.insertHead(a_node)
                self._pointer_map[a_key] = a_node
                return True
            else:
                a_node = self.Node(a_key, val, ttl)
                self.insertHead(a_node)
                self._pointer_map[a_key] = a_node
                return True
        finally:
            self._lock.release()    


cache_ipv4 = LRUCache()       
cache_ipv6 = LRUCache()

if __name__ == "__main__":

    a_cache = LRUCache(30)
    a_cache.set("www.baidu.com", 0, 0, b"\x01\x01\x23", 123)
    a_cache.get("www.baidu.com", 0, 0)
    # for i in range(100):
        # print(i)
        # a_cache.set("www.baidu.com"+str(i), 0, 0, b"asdfafsafaf", 100)
        # print(a_cache.get("www.baidu.com"+str(i), 0, 0 ))
    print(a_cache.get("www.baidu.com", 0, 0))


