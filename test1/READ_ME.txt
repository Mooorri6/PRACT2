# Устанавливаем Python3 и pip
sudo apt install python3 python3-pip -y

# Создаем папку проекта
mkdir piv_analyzer
cd piv_analyzer

# Создаем виртуальное окружение
python3 -m venv venv

# Активируем его
source venv/bin/activate

# Устанавливаем необходимые библиотеки
pip3 install matplotlib

python piv_analyzer.py