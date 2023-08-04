# Video-Steganography
Репозиторий содержит код, реализующий функционал сокрытия в кадрах видеофайла текстовых сообщений и последующего извлечения. Сообщение записывается в младшие биты значений цветовых характеристик пикселей кадров. Распределение кадров определяется генератором псевдослучайных значений.
Отрицаемость шифрования достигнута путем записи сообщений в кадры с номерами разной четности, пиксели определяются независимо для каждого сообщения.
Уникальность генерируемых распределений реализована путем учета числа состоявшихся ранее сеансов передачи (предполагается, что проведение сеансов передачи регламентировано). Количество состоявшихся передач определяет модификацию seed-значений, определяющих распределения пикселей и четность кадров, скрывающих первое или второе сообщения соответственно.

ВАЖНО: для корректнойц работы метода сокрытия (steg_sender.py) необходимо установить набор библиотек ffmpeg и добавить путь к его рабочей директории в переменную PATH.
## Метод сокрытия сообщений:
steg_sender.py [-h] params_path

### Позиционные аргументы:
  params_path  Путь к .txt файлу с параметрами

### Опции:
  -h, --help   вывести это сообщение и выйти 

### Формат файла с параметрами:
![image](https://github.com/avvakumtheprotopope/Video-Steganography/assets/78872231/13a681bc-6421-4bf1-840b-a034a7d5b066)

- INPUT_VIDEO_FILENAME - путь к пустому стегоконтейнеру (файлу с расширением .mp4, .avi или .mkv),
- OUTPUT_VIDEO_FILENAME - путь для записи заполненного контейнера(файла с расширением .mkv),
- MESSAGE1_FILENAME - путь к текстовому файлу с первым сообщением,
- MESSAGE2_FILENAME - путь к текстовому файлу с вторым сообщением,
- RATIO_COEF - количество пикселей кадра, на которое приходится один модифицированный пиксель,
- MULTIPLY_COEF - количество повторений сообщения в кадрах


## Метод извлечения сообщений:
steg_receiver.py [-h] params_path

### Позиционные аргументы:

  params_path  Путь к .txt файлу с параметрами

### Опции:
  -h, --help   вывести это сообщение и выйти 
  
### Формат файла с параметрами:
![image](https://github.com/avvakumtheprotopope/Video-Steganography/assets/78872231/3e7e8b1e-e259-4bcb-9ccb-6c8f76c63254)

- INPUT_VIDEO_FILENAME - путь к заполненному стегоконтейнеру(файлу с расширением .mkv),
- RATIO_COEF - количество пикселей кадра, на которое приходится один модифицированный пиксель,
- MULTIPLY_COEF - количество повторений сообщения в кадрах










    
