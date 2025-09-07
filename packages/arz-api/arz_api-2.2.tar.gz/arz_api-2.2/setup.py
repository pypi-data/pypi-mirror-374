from setuptools import setup, find_packages

setup(
  name='arz_api',
  version='2.2',
  author='TastyBread123',
  author_email='ermakovglebyt@gmail.com',
  description='Модуль для взаимодействия с форумом без Xenforo ключей',
  long_description="""# Arizona-API
API для взаимодействия с ресурсами Arizona без необходимости в получении API ключа xenforo у администраторов форума. Вы можете просто найти ваши куки (рекомендую для этого отдельные расширения) и начинать разработку!

# Описание проекта
API поддерживает около 35 методов, которые помогают в решении 90% задач. API легко масштабируется, а также имеет удобную [документацию](https://tastybread123.github.io/Arizona-API/arz_api.html).  
Также рекомендую ознакомиться с [примерами](https://github.com/TastyBread123/Arizona-API/tree/main/examples), дабы возникало меньше вопросов по использованию API.  
Удачи!""",
  long_description_content_type='text/markdown',
  url='https://github.com/TastyBread123/Arizona-API/',
  packages=find_packages(),
  install_requires=['requests>=2.28.2', 'bs4>=0.0.1', 'dukpy>=0.4.0', ' aiohttp>=3.10.5', 'aiohttp_socks>=0.9.0', 'lxml>=5.3.0'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='python xenforo arizona roleplay samp gta',
  project_urls={
    'Documentation': 'https://tastybread123.github.io/Arizona-API/arz_api.html'
  },
  python_requires='>=3.10'
)