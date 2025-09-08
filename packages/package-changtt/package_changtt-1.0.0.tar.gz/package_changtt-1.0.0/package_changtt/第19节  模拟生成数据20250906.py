import click
import csv
from faker import Faker

"""
开发一个工具，用于批量模拟生成测试数据。
"""
# Faker是一个用于生成假数据的Python库，当设置locale='zh_CN'时，会生成符合中文语境的模拟数据（如姓名、地址、电话号码等）。
fake = Faker(locale='zh_CN')


@click.command()
@click.option('--output', '-o', default='data.csv', help='Output file name')
@click.option('--count', '-c', default='100', type=int, help='Number of data records to generate')
def generate_data(output, count):
    data = []
    for i in range(count):
        username = fake.user_name()
        password = fake.password()
        phone = fake.phone_number()
        id_card = fake.ssn()
        company = fake.company()
        address = fake.address()
        position = fake.street_address()
        email = fake.email()
        amount1 = fake.random_int()
        amount2 = fake.pydecimal(left_digits=3, right_digits=2, positive=True)
        data.append([username, password, phone, id_card, company, address, position, email, amount1, amount2])
        print(data)
    # 将数据写入CSV文件
    title_list = ['姓名', '密码', '手机号', '身份证号码', '公司名称', '地址', '职位', '邮箱', '投入金额', '收益']
    with open(output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(title_list)
        writer.writerows(data)


if __name__ == '__main__':
    generate_data()
