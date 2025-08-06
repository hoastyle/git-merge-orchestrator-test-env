#!/usr/bin/env python3
"""
Test module 4
Generated for testing purposes
"""

import os
import sys
from datetime import datetime


class TestClass004:
    """Test class 4"""
    
    def __init__(self, name="test_4"):
        self.name = name
        self.created_at = datetime.now()
        self.version = "4.2"
    
    def test_function_4(self):
        """Test function 4"""
        return f"{self.name} executed at {self.created_at}"
    
    def process_data(self, data):
        """Process test data"""
        if not data:
            return None
        
        processed = []
        for item in data:
            if isinstance(item, str):
                processed.append(item.upper())
            elif isinstance(item, (int, float)):
                processed.append(item * 2)
            else:
                processed.append(str(item))
        
        return processed


def main():
    """Main function for test module 4"""
    test_obj = TestClass004()
    print(test_obj.test_function_4())
    
    test_data = ["hello", 42, 3.14, True]
    result = test_obj.process_data(test_data)
    print(f"Processed data: {result}")


if __name__ == "__main__":
    main()
