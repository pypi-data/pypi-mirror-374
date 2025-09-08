from setuptools import setup,find_packages

#若为Python包发布脚本，建议改用README.md并更新setup.py配置
with open("README.rst","r",encoding='utf-8') as f:
    long_description =f.read()

setup(name='package_changtt', #包名
      version='1.0.0',
      description='全栈测试开发培训营打卡作业',
      long_description=long_description,
      author='changtt_talk',
      author_email='1113821106@qq.com',
      url='https://kjdaohang.com',
      install_requires=[],
      license='MIT License',
      packages=find_packages(),
      platforms=['all'],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Topic :: Software Development :: Libraries'
      ],
      )