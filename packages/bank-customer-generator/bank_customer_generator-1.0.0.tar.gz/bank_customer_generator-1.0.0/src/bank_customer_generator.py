import csv
import argparse
import random
from faker import Faker
from typing import List, Dict

"""
作业练习：
开发一个数据构造工具，用于辅助日常测试工作。

功能目标：
批量生成虚拟的客户信息。
"""

class BankCustomerGenerator:
    def __init__(self):
        self.fake = Faker()
        
    def generate_customer(self, customer_id: int) -> Dict[str, str]:
        """生成单个银行客户信息"""
        first_name = self.fake.first_name()
        last_name = self.fake.last_name()
        full_name = f"{first_name} {last_name}"
        
        return {
            "customer_id": str(customer_id),
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "email": self.fake.email(),
            "phone": self.fake.phone_number(),
            "address": self.fake.address().replace("\n", ", "),
            "city": self.fake.city(),
            "state": self.fake.state(),
            "zip_code": self.fake.zipcode(),
            "account_number": self.fake.bban(),
            "ssn": self.fake.ssn(),
            "date_of_birth": self.fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%Y-%m-%d"),
            "account_balance": f"{random.uniform(100, 50000):.2f}",
            "account_type": random.choice(["Checking", "Savings", "Money Market", "CD"]),
            "employment_status": random.choice(["Employed", "Unemployed", "Self-Employed", "Retired"]),
            "annual_income": f"{random.uniform(20000, 200000):.2f}"
        }
    
    def generate_customers(self, count: int) -> List[Dict[str, str]]:
        """生成指定数量的客户信息"""
        return [self.generate_customer(i + 1) for i in range(count)]
    
    def save_to_csv(self, customers: List[Dict[str, str]], filename: str):
        """将客户信息保存到CSV文件"""
        if not filename.endswith('.csv'):
            filename += '.csv'
            
        fieldnames = [
            "customer_id", "first_name", "last_name", "full_name", "email", 
            "phone", "address", "city", "state", "zip_code", "account_number", 
            "ssn", "date_of_birth", "account_balance", "account_type", 
            "employment_status", "annual_income"
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(customers)
            
        print(f"成功生成 {len(customers)} 条客户信息并保存到 {filename}")

def main():
    parser = argparse.ArgumentParser(description="银行客户信息生成器")
    parser.add_argument("-n", "--number", type=int, default=10, 
                        help="要生成的客户信息数量，默认为10")
    parser.add_argument("-o", "--output", type=str, default="bank_customers",
                        help="输出文件名（不需要扩展名），默认为bank_customers")
    
    args = parser.parse_args()
    
    generator = BankCustomerGenerator()
    customers = generator.generate_customers(args.number)
    generator.save_to_csv(customers, args.output)

if __name__ == "__main__":
    main()        
